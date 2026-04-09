"""Product similarity service using ChromaDB vector search.

Replaces the previous TF-IDF implementation with semantic vector search
via sentence-transformers + ChromaDB. Falls back to TF-IDF if ChromaDB
is unavailable.
"""
import logging

from config.chromadb_config import get_collection, is_chromadb_available
from services.embedding_service import build_product_document, embed_single

logger = logging.getLogger(__name__)


def get_similar_products(target_product, all_products, top_n=6):
    """Find products similar to target_product.

    Uses ChromaDB vector search when available, falls back to TF-IDF.

    Args:
        target_product: dict with product fields (product_id, name, etc.)
        all_products: list of product dicts (used by enrichment and TF-IDF fallback)
        top_n: number of similar products to return

    Returns:
        list of product dicts with 'similarity_score' added
    """
    if is_chromadb_available():
        try:
            results = _chromadb_similar(target_product, top_n)
            if results is not None:
                return _enrich_results(results, all_products)
        except Exception as exc:
            logger.warning("ChromaDB search failed, falling back to TF-IDF: %s", exc)

    from services.tfidf_fallback import get_similar_products as tfidf_similar

    return tfidf_similar(target_product, all_products, top_n)


def _chromadb_similar(target_product, top_n):
    """Query ChromaDB for similar products."""
    collection = get_collection()
    if collection is None or collection.count() == 0:
        return None

    doc = build_product_document(target_product)
    query_embedding = embed_single(doc)
    if query_embedding is None:
        return None

    target_id = str(target_product.get("product_id"))

    # Request top_n + 1 because the target product itself may be in results
    n_results = min(top_n + 1, collection.count())
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={"is_active": 1},
    )

    if not results or not results["ids"] or not results["ids"][0]:
        return None

    similar = []
    for i, doc_id in enumerate(results["ids"][0]):
        pid = results["metadatas"][0][i].get("product_id")
        if str(pid) == target_id:
            continue

        # ChromaDB cosine distance = 1 - cosine_similarity
        distance = results["distances"][0][i] if results["distances"] else 0
        similarity = round(max(0.0, 1.0 - distance), 4)

        similar.append({
            "product_id": pid,
            "similarity_score": similarity,
        })

    return similar[:top_n]


def _enrich_results(chroma_results, all_products):
    """Merge ChromaDB results with full product data from all_products."""
    product_lookup = {p["product_id"]: p for p in all_products}
    enriched = []
    for r in chroma_results:
        pid = r["product_id"]
        if pid in product_lookup:
            enriched.append({
                **product_lookup[pid],
                "similarity_score": r["similarity_score"],
            })
    return enriched
