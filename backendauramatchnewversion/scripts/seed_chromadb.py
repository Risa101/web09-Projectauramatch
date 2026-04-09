"""Seed ChromaDB with product embeddings.

Reads all active products from MySQL, builds document strings,
computes embeddings, and upserts into the ChromaDB products collection.

Usage:
  cd backendauramatchnewversion
  python scripts/seed_chromadb.py

Idempotent — upsert replaces existing entries.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import all models to register relationships (same as main.py)
import models.user
import models.misc
import models.product
import models.analysis
import models.recommendation
import models.commission
import models.gemini
import models.photo_editor
import models.blog
import models.behavior
import models.saved_look

from sqlalchemy.orm import joinedload
from config.database import SessionLocal
from config.chromadb_config import get_collection
from models.product import Product, Brand, ProductCategory
from models.misc import ProductConcern, SkinConcern
from services.embedding_service import build_product_document, embed_texts


def load_products(db):
    """Load all active products with related data."""
    products = (
        db.query(Product)
        .options(
            joinedload(Product.brand),
            joinedload(Product.category),
        )
        .filter(Product.is_active == 1)
        .all()
    )

    result = []
    for p in products:
        # Load concerns for this product
        concern_names = (
            db.query(SkinConcern.name)
            .join(ProductConcern, ProductConcern.concern_id == SkinConcern.concern_id)
            .filter(ProductConcern.product_id == p.product_id)
            .all()
        )

        result.append({
            "product_id": p.product_id,
            "name": p.name,
            "description": p.description,
            "category_id": p.category_id,
            "category_name": p.category.name if p.category else None,
            "brand_id": p.brand_id,
            "brand_name": p.brand.name if p.brand else None,
            "personal_color": p.personal_color,
            "price": float(p.price) if p.price else 0.0,
            "concern_names": [c[0] for c in concern_names],
        })

    return result


def seed():
    """Main seeding function."""
    collection = get_collection()
    if collection is None:
        print("ERROR: ChromaDB is not available. Check installation.")
        sys.exit(1)

    db = SessionLocal()
    try:
        products = load_products(db)
        if not products:
            print("No active products found in database.")
            sys.exit(1)

        print(f"Loaded {len(products)} products from MySQL")

        # Build document strings
        documents = []
        ids = []
        metadatas = []

        for p in products:
            doc = build_product_document(p)
            documents.append(doc)
            ids.append(f"product_{p['product_id']}")
            metadatas.append({
                "product_id": p["product_id"],
                "category_id": p["category_id"] or 0,
                "brand_id": p["brand_id"] or 0,
                "personal_color": p["personal_color"] or "",
                "price": p["price"],
                "is_active": 1,
            })

        print("Generating embeddings...")
        embeddings = embed_texts(documents)
        if embeddings is None:
            print("ERROR: Failed to generate embeddings. Check sentence-transformers installation.")
            sys.exit(1)

        print(f"Generated {len(embeddings)} embeddings (dim={len(embeddings[0])})")

        # Upsert into ChromaDB
        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        print(f"Upserted {len(ids)} products into ChromaDB collection '{collection.name}'")
        print(f"Collection count: {collection.count()}")
        print("Done!")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
