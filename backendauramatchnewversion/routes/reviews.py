from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import func as sa_func, case
from sqlalchemy.orm import Session
from config.database import get_db
from routes.auth import get_current_user
from models.user import User
from models.product import Product
from models.misc import ProductReview

router = APIRouter(prefix="/reviews", tags=["Reviews"])


class ReviewCreate(BaseModel):
    rating: int
    comment: str | None = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


@router.post("/{product_id}")
def upsert_review(
    product_id: int,
    body: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update the current user's review for a product."""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = (
        db.query(ProductReview)
        .filter(ProductReview.user_id == current_user.user_id,
                ProductReview.product_id == product_id)
        .first()
    )

    if existing:
        existing.rating = body.rating
        existing.comment = body.comment
        db.commit()
        db.refresh(existing)
        review = existing
    else:
        review = ProductReview(
            product_id=product_id,
            user_id=current_user.user_id,
            rating=body.rating,
            comment=body.comment,
        )
        db.add(review)
        db.commit()
        db.refresh(review)

    return {
        "review_id": review.review_id,
        "product_id": review.product_id,
        "user_id": review.user_id,
        "rating": review.rating,
        "comment": review.comment,
        "is_verified": review.is_verified,
        "created_at": str(review.created_at) if review.created_at else None,
    }


@router.get("/{product_id}")
def get_reviews(product_id: int, db: Session = Depends(get_db)):
    """Get all reviews for a product, with usernames."""
    rows = (
        db.query(ProductReview, User.username)
        .join(User, User.user_id == ProductReview.user_id)
        .filter(ProductReview.product_id == product_id)
        .order_by(ProductReview.created_at.desc())
        .all()
    )
    return [
        {
            "review_id": r.review_id,
            "product_id": r.product_id,
            "user_id": r.user_id,
            "username": username,
            "rating": r.rating,
            "comment": r.comment,
            "is_verified": r.is_verified,
            "created_at": str(r.created_at) if r.created_at else None,
        }
        for r, username in rows
    ]


@router.get("/{product_id}/summary")
def get_review_summary(product_id: int, db: Session = Depends(get_db)):
    """Get average rating, total count, and star distribution."""
    rows = (
        db.query(
            sa_func.count(ProductReview.review_id).label("total"),
            sa_func.avg(ProductReview.rating).label("avg"),
            sa_func.sum(case((ProductReview.rating == 1, 1), else_=0)).label("s1"),
            sa_func.sum(case((ProductReview.rating == 2, 1), else_=0)).label("s2"),
            sa_func.sum(case((ProductReview.rating == 3, 1), else_=0)).label("s3"),
            sa_func.sum(case((ProductReview.rating == 4, 1), else_=0)).label("s4"),
            sa_func.sum(case((ProductReview.rating == 5, 1), else_=0)).label("s5"),
        )
        .filter(ProductReview.product_id == product_id)
        .first()
    )

    total = rows.total or 0
    return {
        "average_rating": round(float(rows.avg), 2) if rows.avg else 0,
        "total_count": total,
        "distribution": {
            1: rows.s1 or 0,
            2: rows.s2 or 0,
            3: rows.s3 or 0,
            4: rows.s4 or 0,
            5: rows.s5 or 0,
        },
    }


@router.delete("/{product_id}")
def delete_review(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete the current user's review for a product."""
    review = (
        db.query(ProductReview)
        .filter(ProductReview.user_id == current_user.user_id,
                ProductReview.product_id == product_id)
        .first()
    )
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    db.delete(review)
    db.commit()
    return {"message": "Review deleted"}
