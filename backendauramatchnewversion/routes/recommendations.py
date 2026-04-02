from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from config.database import get_db
from models.recommendation import Recommendation, RecommendationRule, RecommendationFeedback
from models.analysis import AnalysisResult
from models.product import Product, Brand, ProductLink
from models.user import User
from routes.auth import get_current_user

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/generate/{analysis_id}")
def generate_recommendations(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(AnalysisResult).filter(AnalysisResult.analysis_id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # ลบ recommendations เก่าของ analysis นี้ก่อน (กันซ้ำ)
    db.query(Recommendation).filter(Recommendation.analysis_id == analysis_id).delete()

    rules = db.query(RecommendationRule).filter(
        (RecommendationRule.face_shape == analysis.face_shape) | (RecommendationRule.face_shape == "any"),
        (RecommendationRule.skin_tone == analysis.skin_tone) | (RecommendationRule.skin_tone == "any"),
        (RecommendationRule.skin_undertone == analysis.skin_undertone) | (RecommendationRule.skin_undertone == "any"),
        (RecommendationRule.personal_color == analysis.personal_color) | (RecommendationRule.personal_color == "any"),
        (RecommendationRule.gender == analysis.gender) | (RecommendationRule.gender == "any"),
    ).order_by(RecommendationRule.priority.desc()).all()

    recommendations = []
    seen = set()
    for rule in rules:
        if rule.product_id not in seen:
            rec = Recommendation(
                analysis_id=analysis_id,
                product_id=rule.product_id,
                score=float(rule.priority)
            )
            db.add(rec)
            recommendations.append(rec)
            seen.add(rule.product_id)

    db.commit()
    return {"message": f"Generated {len(recommendations)} recommendations", "count": len(recommendations)}


@router.get("/{analysis_id}")
def get_recommendations(analysis_id: int, limit: int = 20, db: Session = Depends(get_db)):
    recs = (
        db.query(Recommendation)
        .filter(Recommendation.analysis_id == analysis_id)
        .options(
            joinedload(Recommendation.product).joinedload(Product.brand),
            joinedload(Recommendation.product).joinedload(Product.links),
        )
        .order_by(Recommendation.score.desc())
        .limit(limit)
        .all()
    )

    results = []
    for rec in recs:
        p = rec.product
        results.append({
            "recommendation_id": rec.recommendation_id,
            "score": float(rec.score) if rec.score else 0,
            "product": {
                "product_id": p.product_id,
                "name": p.name,
                "price": float(p.price) if p.price else None,
                "image_url": p.image_url,
                "brand": p.brand.name if p.brand else None,
                "links": [
                    {"link_id": l.link_id, "platform": l.platform, "url": l.url}
                    for l in p.links if l.is_active
                ],
            },
        })
    return results


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
