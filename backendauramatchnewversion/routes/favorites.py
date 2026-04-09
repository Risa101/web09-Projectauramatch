from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from models.recommendation import Favorite
from models.product import Product
from models.user import User
from routes.auth import get_current_user

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get("/")
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all favorite products for the authenticated user."""
    favs = (
        db.query(Favorite)
        .filter(Favorite.user_id == current_user.user_id)
        .order_by(Favorite.created_at.desc())
        .all()
    )
    product_ids = [f.product_id for f in favs]
    if not product_ids:
        return []

    products = (
        db.query(Product)
        .filter(Product.product_id.in_(product_ids))
        .all()
    )
    product_map = {p.product_id: p for p in products}

    return [
        {
            "favorite_id": f.favorite_id,
            "product_id": f.product_id,
            "product_name": product_map[f.product_id].name if f.product_id in product_map else None,
            "product_image": product_map[f.product_id].image_url if f.product_id in product_map else None,
            "product_price": float(product_map[f.product_id].price) if f.product_id in product_map and product_map[f.product_id].price else None,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        }
        for f in favs
    ]


@router.get("/ids")
def get_favorite_ids(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return just the product IDs the user has favorited (for heart toggle state)."""
    favs = (
        db.query(Favorite.product_id)
        .filter(Favorite.user_id == current_user.user_id)
        .all()
    )
    return [f.product_id for f in favs]


@router.post("/{product_id}")
def add_favorite(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a product to favorites."""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = (
        db.query(Favorite)
        .filter(Favorite.user_id == current_user.user_id, Favorite.product_id == product_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already favorited")

    fav = Favorite(user_id=current_user.user_id, product_id=product_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return {"message": "Added to favorites", "favorite_id": fav.favorite_id}


@router.delete("/{product_id}")
def remove_favorite(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a product from favorites."""
    fav = (
        db.query(Favorite)
        .filter(Favorite.user_id == current_user.user_id, Favorite.product_id == product_id)
        .first()
    )
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")

    db.delete(fav)
    db.commit()
    return {"message": "Removed from favorites"}
