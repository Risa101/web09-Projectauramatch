"""
Multi-signal scoring engine for product recommendations.

Combines 6 signals into a composite score (0–999.99):
  S1: Rule match priority (0–300)
  S2: Color shade proximity via CIEDE2000 (0–300)
  S3: Personal color season match (0–150)
  S4: Avoid-color penalty (-100–0)
  S5: Demographic feedback ratio (0–100)
  S6: Popularity via favorites (0–50)
"""

import numpy as np
import colour
from sqlalchemy import func as sa_func, case
from sqlalchemy.orm import Session

# ── Module-level cache for hex → L*a*b* conversions ────────────────────────
_hex_lab_cache: dict[str, tuple[float, float, float]] = {}


def hex_to_lab(hex_color: str) -> tuple[float, float, float]:
    """Convert a hex color string like '#FF6B6B' to CIELAB (L*, a*, b*).

    Uses sRGB → XYZ (D65) → L*a*b* via colour-science.
    Results are cached at module level.
    """
    if hex_color in _hex_lab_cache:
        return _hex_lab_cache[hex_color]

    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    rgb_norm = np.array([r, g, b], dtype=np.float64) / 255.0
    xyz = colour.sRGB_to_XYZ(rgb_norm)
    lab = colour.XYZ_to_Lab(xyz)
    result = (float(lab[0]), float(lab[1]), float(lab[2]))
    _hex_lab_cache[hex_color] = result
    return result


def compute_color_proximity(shades_lab: list[tuple], palette_lab: list[tuple]) -> float:
    """S2: Score how well product shades match palette best_colors.

    Computes min CIEDE2000 distance across all (shade, palette_color) pairs.
    Returns 0–300. Perfect match ≈ 300, delta E >= 50 → 0.
    """
    if not shades_lab or not palette_lab:
        return 150.0  # neutral when no shade data

    shades_arr = np.array(shades_lab)
    palette_arr = np.array(palette_lab)

    min_de = float("inf")
    for shade in shades_arr:
        for pcolor in palette_arr:
            de = colour.difference.delta_E_CIE2000(shade, pcolor)
            if de < min_de:
                min_de = de

    return max(0.0, 300.0 * (1.0 - min_de / 50.0))


def compute_avoid_penalty(shades_lab: list[tuple], avoid_lab: list[tuple]) -> float:
    """S4: Penalty for product shades close to avoid-colors.

    Returns -100 to 0. Only penalizes when min delta E < 15.
    """
    if not shades_lab or not avoid_lab:
        return 0.0

    shades_arr = np.array(shades_lab)
    avoid_arr = np.array(avoid_lab)

    min_de = float("inf")
    for shade in shades_arr:
        for avoid in avoid_arr:
            de = colour.difference.delta_E_CIE2000(shade, avoid)
            if de < min_de:
                min_de = de

    if min_de >= 15.0:
        return 0.0

    return -100.0 * (1.0 - min_de / 15.0)


def compute_personal_color_score(product_pc: str | None, analysis_pc: str) -> float:
    """S3: Score for personal color season match.

    Returns 150 if match, 0 if mismatch, 75 if product has no data.
    """
    if not product_pc:
        return 75.0
    seasons = [s.strip().lower() for s in product_pc.split(",")]
    if analysis_pc.lower() in seasons:
        return 150.0
    return 0.0


def compute_final_score(s1: float, s2: float, s3: float,
                        s4: float, s5: float, s6: float) -> float:
    """Combine all signals and clamp to 0–999.99."""
    raw = s1 + s2 + s3 + s4 + s5 + s6
    return round(max(0.0, min(999.99, raw)), 2)


# ── Batch DB queries ───────────────────────────────────────────────────────

def compute_concern_bonus(product_concern_ids: set[int],
                          user_concern_ids: set[int]) -> float:
    """S1 bonus for skin concern overlap.

    Returns 0–60.  Each matching concern adds 20 points (capped at 60).
    This bonus is added to S1 (Rule Match Priority) during scoring.
    """
    if not product_concern_ids or not user_concern_ids:
        return 0.0
    overlap = len(product_concern_ids & user_concern_ids)
    return min(overlap * 20.0, 60.0)


def batch_concern_match_scores(product_ids: list[int], user_id: int,
                               db: Session) -> dict[int, float]:
    """Batch-compute S1 concern bonuses for a list of products.

    Returns {product_id: bonus 0–60}.
    """
    if not product_ids or not user_id:
        return {pid: 0.0 for pid in product_ids}

    from models.misc import UserSkinConcern, ProductConcern

    # User's concern IDs
    user_rows = (
        db.query(UserSkinConcern.concern_id)
        .filter(UserSkinConcern.user_id == user_id)
        .all()
    )
    user_concern_ids = {r.concern_id for r in user_rows}
    if not user_concern_ids:
        return {pid: 0.0 for pid in product_ids}

    # Product concern mappings
    pc_rows = (
        db.query(ProductConcern.product_id, ProductConcern.concern_id)
        .filter(ProductConcern.product_id.in_(product_ids))
        .all()
    )
    product_concerns: dict[int, set[int]] = {}
    for row in pc_rows:
        product_concerns.setdefault(row.product_id, set()).add(row.concern_id)

    scores = {}
    for pid in product_ids:
        scores[pid] = compute_concern_bonus(
            product_concerns.get(pid, set()), user_concern_ids
        )
    return scores


def rating_to_s5(avg_rating: float | None) -> float:
    """Convert average 1-5 star rating to S5 score (0-100). None -> 50."""
    if avg_rating is None:
        return 50.0
    return (avg_rating / 5.0) * 100.0


def batch_feedback_scores(product_ids: list[int], personal_color: str,
                          db: Session) -> dict[int, float]:
    """S5: Aggregate product review ratings from users with same personal_color.

    Returns {product_id: score 0–100}. Default 50 for products with no reviews.
    """
    if not product_ids:
        return {}

    from models.misc import ProductReview
    from models.analysis import AnalysisResult

    # Users whose analysis matches the target personal_color
    matching_users = (
        db.query(AnalysisResult.user_id)
        .filter(AnalysisResult.personal_color == personal_color)
        .distinct()
        .subquery()
    )

    rows = (
        db.query(
            ProductReview.product_id,
            sa_func.avg(ProductReview.rating).label("avg_rating"),
        )
        .filter(
            ProductReview.product_id.in_(product_ids),
            ProductReview.user_id.in_(db.query(matching_users.c.user_id)),
        )
        .group_by(ProductReview.product_id)
        .all()
    )

    scores = {}
    for product_id, avg_rating in rows:
        scores[product_id] = rating_to_s5(float(avg_rating) if avg_rating else None)

    for pid in product_ids:
        if pid not in scores:
            scores[pid] = 50.0

    return scores


def batch_popularity_scores(product_ids: list[int], db: Session) -> dict[int, float]:
    """S6: Popularity score from favorite counts.

    Returns {product_id: score 0–50}. Caps at 10 favorites.
    """
    if not product_ids:
        return {}

    from models.recommendation import Favorite

    rows = (
        db.query(
            Favorite.product_id,
            sa_func.count(Favorite.favorite_id).label("fav_count"),
        )
        .filter(Favorite.product_id.in_(product_ids))
        .group_by(Favorite.product_id)
        .all()
    )

    scores = {}
    for product_id, fav_count in rows:
        scores[product_id] = min((fav_count or 0) / 10.0, 1.0) * 50.0

    for pid in product_ids:
        if pid not in scores:
            scores[pid] = 0.0

    return scores
