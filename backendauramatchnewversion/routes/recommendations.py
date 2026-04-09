from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session, joinedload
from config.database import get_db
from models.recommendation import Recommendation, RecommendationRule, RecommendationFeedback
from models.analysis import AnalysisResult, ColorPalette
from models.product import Product, Brand, ProductLink, ProductColorShade
from models.user import User
from routes.auth import get_current_user
from services.cache_service import cache_get, cache_set
from services.scoring_service import (
    hex_to_lab,
    compute_color_proximity,
    compute_avoid_penalty,
    compute_personal_color_score,
    compute_final_score,
    batch_feedback_scores,
    batch_popularity_scores,
    batch_concern_match_scores,
)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


def _load_palette_colors(palette_id, db: Session):
    """Load best_colors and avoid_colors Lab arrays from a ColorPalette.

    Results are cached in Redis for 2 hours since palette data rarely changes.
    """
    if not palette_id:
        return [], []

    cache_key = f"palettes:{palette_id}"
    hit = cache_get(cache_key)
    if hit is not None:
        return [tuple(c) for c in hit["best"]], [tuple(c) for c in hit["avoid"]]

    palette = db.query(ColorPalette).filter(ColorPalette.palette_id == palette_id).first()
    if not palette:
        return [], []

    best_lab = []
    if palette.best_colors and "colors" in palette.best_colors:
        for c in palette.best_colors["colors"]:
            if "L" in c and "a" in c and "b" in c:
                best_lab.append((c["L"], c["a"], c["b"]))
            elif "hex" in c:
                best_lab.append(hex_to_lab(c["hex"]))

    avoid_lab = []
    if palette.avoid_colors and "colors" in palette.avoid_colors:
        for c in palette.avoid_colors["colors"]:
            if "L" in c and "a" in c and "b" in c:
                avoid_lab.append((c["L"], c["a"], c["b"]))
            elif "hex" in c:
                avoid_lab.append(hex_to_lab(c["hex"]))

    cache_set(cache_key, {"best": best_lab, "avoid": avoid_lab}, ttl=7200)

    return best_lab, avoid_lab


def _get_product_shades_lab(product_ids: list[int], db: Session) -> dict[int, list[tuple]]:
    """Batch-load product color shades as Lab tuples. Returns {product_id: [(L,a,b), ...]}."""
    if not product_ids:
        return {}
    shades = (
        db.query(ProductColorShade)
        .filter(
            ProductColorShade.product_id.in_(product_ids),
            ProductColorShade.hex_color.isnot(None),
            ProductColorShade.is_active == 1,
        )
        .all()
    )
    result: dict[int, list[tuple]] = {}
    for s in shades:
        if s.hex_color and len(s.hex_color) >= 4:
            lab = hex_to_lab(s.hex_color)
            result.setdefault(s.product_id, []).append(lab)
    return result


def generate_recs_for_analysis(analysis, db: Session) -> list:
    """Generate recommendations using multi-signal weighted scoring.

    Signals: rule match (S1), color proximity (S2), personal color (S3),
    avoid penalty (S4), demographic feedback (S5), popularity (S6).
    """
    db.query(Recommendation).filter(Recommendation.analysis_id == analysis.analysis_id).delete()

    # ── Phase 1: Rule-based candidates ──────────────────────────────────────
    rules = db.query(RecommendationRule).filter(
        (RecommendationRule.face_shape == analysis.face_shape) | (RecommendationRule.face_shape == "any"),
        (RecommendationRule.skin_tone == analysis.skin_tone) | (RecommendationRule.skin_tone == "any"),
        (RecommendationRule.skin_undertone == analysis.skin_undertone) | (RecommendationRule.skin_undertone == "any"),
        (RecommendationRule.personal_color == analysis.personal_color) | (RecommendationRule.personal_color == "any"),
        (RecommendationRule.gender == analysis.gender) | (RecommendationRule.gender == "any"),
    ).order_by(RecommendationRule.priority.desc()).all()

    # Deduplicate rules per product, keep highest priority
    rule_map: dict[int, float] = {}
    for rule in rules:
        if rule.product_id not in rule_map:
            rule_map[rule.product_id] = float(rule.priority)

    # ── Phase 2: Candidate expansion (products without rules) ───────────────
    rule_product_ids = set(rule_map.keys())
    extra_products = []
    if analysis.personal_color:
        extra_products = (
            db.query(Product)
            .filter(
                Product.is_active == 1,
                Product.personal_color.ilike(f"%{analysis.personal_color}%"),
                ~Product.product_id.in_(rule_product_ids) if rule_product_ids else True,
            )
            .all()
        )
    for p in extra_products:
        rule_map.setdefault(p.product_id, 0.0)

    all_product_ids = list(rule_map.keys())
    if not all_product_ids:
        db.commit()
        return []

    # ── Batch-load scoring data ─────────────────────────────────────────────
    best_lab, avoid_lab = _load_palette_colors(analysis.palette_id, db)
    shades_map = _get_product_shades_lab(all_product_ids, db)
    feedback_map = batch_feedback_scores(all_product_ids, analysis.personal_color or "", db)
    popularity_map = batch_popularity_scores(all_product_ids, db)
    concern_map = batch_concern_match_scores(all_product_ids, analysis.user_id, db)

    # Load product personal_color field
    products = (
        db.query(Product.product_id, Product.personal_color)
        .filter(Product.product_id.in_(all_product_ids))
        .all()
    )
    pc_map = {p.product_id: p.personal_color for p in products}

    # ── Normalize S1 ────────────────────────────────────────────────────────
    max_priority = max(rule_map.values()) if rule_map else 1.0
    if max_priority == 0:
        max_priority = 1.0

    # ── Score each candidate ────────────────────────────────────────────────
    scored: list[tuple[int, float]] = []
    for pid in all_product_ids:
        s1_base = (rule_map.get(pid, 0.0) / max_priority) * 300.0
        s1 = min(s1_base + concern_map.get(pid, 0.0), 300.0)
        s2 = compute_color_proximity(shades_map.get(pid, []), best_lab)
        s3 = compute_personal_color_score(pc_map.get(pid), analysis.personal_color or "")
        s4 = compute_avoid_penalty(shades_map.get(pid, []), avoid_lab)
        s5 = feedback_map.get(pid, 50.0)
        s6 = popularity_map.get(pid, 0.0)
        final = compute_final_score(s1, s2, s3, s4, s5, s6)
        scored.append((pid, final))

    scored.sort(key=lambda x: x[1], reverse=True)

    # ── Create Recommendation records ───────────────────────────────────────
    recs = []
    for pid, final_score in scored:
        rec = Recommendation(
            analysis_id=analysis.analysis_id,
            product_id=pid,
            score=final_score,
        )
        db.add(rec)
        recs.append(rec)

    db.commit()
    return recs


@router.post("/generate/{analysis_id}")
def generate_recommendations(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(AnalysisResult).filter(AnalysisResult.analysis_id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    recs = generate_recs_for_analysis(analysis, db)
    return {"message": f"Generated {len(recs)} recommendations", "count": len(recs)}


@router.get("/{analysis_id}")
def get_recommendations(analysis_id: int, limit: int = 20, db: Session = Depends(get_db)):
    from models.product import ProductCategory

    recs = (
        db.query(Recommendation)
        .filter(Recommendation.analysis_id == analysis_id)
        .options(
            joinedload(Recommendation.product).joinedload(Product.brand),
            joinedload(Recommendation.product).joinedload(Product.links),
            joinedload(Recommendation.product).joinedload(Product.category),
            joinedload(Recommendation.product).joinedload(Product.color_shades),
        )
        .order_by(Recommendation.score.desc())
        .limit(limit)
        .all()
    )

    flat = []
    by_category: dict[str, list] = {}
    for rec in recs:
        p = rec.product
        category_name = p.category.name if p.category else "Other"
        item = {
            "recommendation_id": rec.recommendation_id,
            "score": float(rec.score) if rec.score else 0,
            "product": {
                "product_id": p.product_id,
                "name": p.name,
                "price": float(p.price) if p.price else None,
                "image_url": p.image_url,
                "brand": p.brand.name if p.brand else None,
                "category": category_name,
                "links": [
                    {"link_id": l.link_id, "platform": l.platform, "url": l.url}
                    for l in p.links if l.is_active
                ],
            },
        }
        flat.append(item)
        by_category.setdefault(category_name, []).append(item)

    return {
        "recommendations": flat,
        "by_category": by_category,
        "total": len(flat),
    }


@router.post("/feedback/{recommendation_id}")
def add_feedback(
    recommendation_id: int,
    rating: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    feedback = RecommendationFeedback(
        recommendation_id=recommendation_id,
        user_id=current_user.user_id,
        rating=rating
    )
    db.add(feedback)
    db.commit()
    return {"message": "Feedback saved"}


class CompareRequest(BaseModel):
    analysis_id: int
    product_ids: list[int]

    @field_validator("product_ids")
    @classmethod
    def limit_product_ids(cls, v):
        if len(v) < 1 or len(v) > 3:
            raise ValueError("product_ids must contain 1-3 items")
        return v


@router.post("/compare")
def compare_products(
    body: CompareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return S2 (color proximity) and S4 (avoid penalty) scores for products
    against the user's analysis palette, plus the user's face_shape."""
    analysis = db.query(AnalysisResult).filter(
        AnalysisResult.analysis_id == body.analysis_id
    ).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if analysis.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not your analysis")

    best_lab, avoid_lab = _load_palette_colors(analysis.palette_id, db)
    shades_map = _get_product_shades_lab(body.product_ids, db)

    products = {}
    for pid in body.product_ids:
        s2 = compute_color_proximity(shades_map.get(pid, []), best_lab)
        s4 = compute_avoid_penalty(shades_map.get(pid, []), avoid_lab)
        match_pct = max(0.0, min(100.0, (s2 + s4) / 300.0 * 100.0))
        products[pid] = {
            "s2": round(s2, 2),
            "s4": round(s4, 2),
            "match_pct": round(match_pct, 1),
        }

    return {"face_shape": analysis.face_shape, "products": products}
