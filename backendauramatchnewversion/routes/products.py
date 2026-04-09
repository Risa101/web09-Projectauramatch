from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from config.database import get_db
from models.product import Product, ProductLink, Brand, ProductCategory
from models.misc import ProductConcern, SkinConcern
from services.recommendation_service import get_similar_products
from services.cache_service import cached, invalidate_pattern
from config.chromadb_config import is_chromadb_available

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/brands")
@cached("products:brands", ttl=3600)
def get_brands(db: Session = Depends(get_db)):
    """ดึง brand ทั้งหมดที่มีสินค้า active"""
    brands = (
        db.query(Brand)
        .join(Product, Product.brand_id == Brand.brand_id)
        .filter(Product.is_active == 1, Brand.is_active == 1)
        .distinct()
        .all()
    )
    return [{"brand_id": b.brand_id, "name": b.name} for b in brands]


@router.get("/categories")
@cached("products:categories", ttl=3600)
def get_categories(db: Session = Depends(get_db)):
    """ดึง category ทั้งหมด"""
    return db.query(ProductCategory).all()


@router.get("/")
@cached("products:list", ttl=3600)
def get_products(
    skip: int = 0, limit: int = 50,
    category_id: int = None,
    brand_id: int = None,
    personal_color: str = None,
    search: str = None,
    sort: str = None,
    db: Session = Depends(get_db)
):
    """ดึงสินค้า พร้อม filter, search, sort"""
    q = (
        db.query(Product)
        .options(joinedload(Product.brand), joinedload(Product.links), joinedload(Product.category))
        .filter(Product.is_active == 1)
    )
    if category_id:
        q = q.filter(Product.category_id == category_id)
    if brand_id:
        q = q.filter(Product.brand_id == brand_id)
    if personal_color:
        q = q.filter(Product.personal_color.ilike(f"%{personal_color}%"))
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%"))
    if sort == "price_asc":
        q = q.order_by(Product.price.asc())
    elif sort == "price_desc":
        q = q.order_by(Product.price.desc())
    elif sort == "newest":
        q = q.order_by(Product.created_at.desc())
    else:
        q = q.order_by(Product.created_at.desc())

    products = q.offset(skip).limit(limit).all()

    # Batch-load product concerns
    product_ids = [p.product_id for p in products]
    concern_rows = (
        db.query(ProductConcern.product_id, SkinConcern.concern_id, SkinConcern.name)
        .join(SkinConcern, SkinConcern.concern_id == ProductConcern.concern_id)
        .filter(ProductConcern.product_id.in_(product_ids))
        .all()
    ) if product_ids else []
    concern_map: dict[int, list[dict]] = {}
    for row in concern_rows:
        concern_map.setdefault(row.product_id, []).append(
            {"concern_id": row.concern_id, "name": row.name}
        )

    result = []
    for p in products:
        links = []
        try:
            for l in p.links:
                if l.is_active:
                    links.append({"link_id": l.link_id, "platform": l.platform, "url": l.url})
        except Exception:
            pass
        result.append({
            "product_id": p.product_id,
            "name": p.name,
            "description": p.description,
            "price": float(p.price) if p.price else 0,
            "image_url": p.image_url,
            "category_id": p.category_id,
            "category_name": p.category.name if p.category else None,
            "brand_name": p.brand.name if p.brand else None,
            "personal_color": p.personal_color,
            "concerns": concern_map.get(p.product_id, []),
            "links": links,
        })
    return result


@router.get("/similar/{product_id}")
def get_similar(product_id: int, limit: int = 6, db: Session = Depends(get_db)):
    """แนะนำสินค้าที่คล้ายกันด้วย TF-IDF + Cosine Similarity"""
    target = db.query(Product).options(
        joinedload(Product.brand), joinedload(Product.category), joinedload(Product.links)
    ).filter(Product.product_id == product_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Product not found")

    all_products = db.query(Product).options(
        joinedload(Product.brand), joinedload(Product.category), joinedload(Product.links)
    ).filter(Product.is_active == 1).all()

    def to_dict(p):
        links = []
        try:
            for l in p.links:
                if l.is_active:
                    links.append({"link_id": l.link_id, "platform": l.platform, "url": l.url})
        except Exception:
            pass
        return {
            "product_id": p.product_id,
            "name": p.name,
            "description": p.description,
            "price": float(p.price) if p.price else 0,
            "image_url": p.image_url,
            "category_id": p.category_id,
            "category_name": p.category.name if p.category else None,
            "brand_name": p.brand.name if p.brand else None,
            "personal_color": p.personal_color,
            "links": links,
        }

    target_dict = to_dict(target)
    all_dicts = [to_dict(p) for p in all_products]

    similar = get_similar_products(target_dict, all_dicts, top_n=limit)
    return {
        "product": target_dict,
        "similar": similar,
        "algorithm": "ChromaDB Vector Search" if is_chromadb_available() else "TF-IDF Cosine Similarity"
    }


@router.get("/by-category")
@cached("products:by_cat", ttl=3600)
def get_products_by_category(category_name: str, limit: int = 6, db: Session = Depends(get_db)):
    """ค้นหาสินค้าตามชื่อ category (ค้นแบบ LIKE)"""
    products = (
        db.query(Product)
        .join(ProductCategory)
        .options(joinedload(Product.brand), joinedload(Product.links))
        .filter(
            Product.is_active == 1,
            ProductCategory.name.ilike(f"%{category_name}%")
        )
        .limit(limit)
        .all()
    )
    return [
        {
            "product_id": p.product_id,
            "name": p.name,
            "price": float(p.price) if p.price else 0,
            "image_url": p.image_url,
            "brand_name": p.brand.name if p.brand else None,
            "links": [
                {"platform": l.platform, "url": l.url}
                for l in p.links if l.is_active
            ],
        }
        for p in products
    ]


@router.get("/makeup-recommendations")
def get_makeup_recommendations(parts: str, limit: int = 4, db: Session = Depends(get_db)):
    """แนะนำสินค้าตาม makeup parts ที่ใช้ (comma-separated: lips,eyes,eyebrows,nose,blush)"""
    part_list = [p.strip() for p in parts.split(",") if p.strip()]

    # mapping makeup part → product category keywords
    part_to_categories = {
        "lips": ["ลิปสติก", "ลิป", "lip"],
        "eyes": ["อายแชโดว์", "อาย", "eye"],
        "eyebrows": ["คิ้ว", "brow", "อายแชโดว์"],
        "nose": ["ไฮไลท์", "คอนซีลเลอร์", "highlight", "contour"],
        "blush": ["บลัชออน", "บลัช", "blush"],
    }

    results = {}
    for part in part_list:
        keywords = part_to_categories.get(part, [])
        if not keywords:
            continue

        products = []
        for kw in keywords:
            found = (
                db.query(Product)
                .join(ProductCategory)
                .options(joinedload(Product.brand), joinedload(Product.links))
                .filter(
                    Product.is_active == 1,
                    ProductCategory.name.ilike(f"%{kw}%")
                )
                .limit(limit)
                .all()
            )
            for p in found:
                if p.product_id not in [x["product_id"] for x in products]:
                    products.append({
                        "product_id": p.product_id,
                        "name": p.name,
                        "price": float(p.price) if p.price else 0,
                        "image_url": p.image_url,
                        "brand_name": p.brand.name if p.brand else None,
                        "links": [
                            {"platform": l.platform, "url": l.url}
                            for l in p.links if l.is_active
                        ],
                    })
            if len(products) >= limit:
                break

        results[part] = products[:limit]

    return results


@router.get("/{product_id}")
@cached("products:detail", ttl=3600)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/")
def create_product(
    name: str, category_id: int, brand_id: int,
    price: float, commission_rate: float = 0,
    description: str = "", image_url: str = "",
    db: Session = Depends(get_db)
):
    product = Product(
        name=name, category_id=category_id, brand_id=brand_id,
        price=price, commission_rate=commission_rate,
        description=description, image_url=image_url
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    invalidate_pattern("products:*")
    return product


@router.put("/{product_id}")
def update_product(product_id: int, name: str = None, price: float = None,
                   is_active: int = None, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if name: product.name = name
    if price: product.price = price
    if is_active is not None: product.is_active = is_active
    db.commit()
    invalidate_pattern("products:*")
    return product


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    invalidate_pattern("products:*")
    return {"message": "Deleted"}


@router.post("/{product_id}/links")
def add_product_link(product_id: int, platform: str, url: str, db: Session = Depends(get_db)):
    link = ProductLink(product_id=product_id, platform=platform, url=url)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link
