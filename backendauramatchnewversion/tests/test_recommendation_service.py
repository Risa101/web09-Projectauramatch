"""Tests for the ChromaDB-based recommendation service.

Uses ``unittest.mock`` to patch ChromaDB and embedding model so tests
run without any external dependencies.
"""

from unittest.mock import patch, MagicMock

import pytest

from services.recommendation_service import get_similar_products


# ── Test data ─────────────────────────────────────────────────────────────

TARGET_PRODUCT = {
    "product_id": 1,
    "name": "Maybelline Vinyl Ink",
    "category_name": "ลิปสติก",
    "brand_name": "Maybelline",
    "description": "ลิปจิ้มจุ่ม",
    "personal_color": "spring",
}

ALL_PRODUCTS = [
    TARGET_PRODUCT,
    {"product_id": 2, "name": "MAC Lipstick", "category_name": "ลิปสติก",
     "brand_name": "MAC", "description": "ลิปสติกเนื้อแมตต์"},
    {"product_id": 3, "name": "Romand Juicy", "category_name": "ลิปสติก",
     "brand_name": "Romand", "description": "ทินท์เนื้อฉ่ำ"},
    {"product_id": 4, "name": "Canmake Blush", "category_name": "บลัชออน",
     "brand_name": "Canmake", "description": "บลัชออนเนื้อฝุ่น"},
]


def _mock_chroma_results(ids, distances, metadatas):
    """Build a ChromaDB query result dict."""
    return {
        "ids": [ids],
        "distances": [distances],
        "metadatas": [metadatas],
        "documents": [["doc"] * len(ids)],
    }


# ── ChromaDB path tests ──────────────────────────────────────────────────

class TestChromaDBSimilar:
    @patch("services.recommendation_service.embed_single")
    @patch("services.recommendation_service.get_collection")
    @patch("services.recommendation_service.is_chromadb_available", return_value=True)
    def test_returns_similar_products(self, mock_avail, mock_coll, mock_embed):
        mock_embed.return_value = [0.1, 0.2, 0.3]

        collection = MagicMock()
        collection.count.return_value = 4
        collection.query.return_value = _mock_chroma_results(
            ids=["product_1", "product_2", "product_3"],
            distances=[0.0, 0.15, 0.35],
            metadatas=[
                {"product_id": 1, "is_active": 1},
                {"product_id": 2, "is_active": 1},
                {"product_id": 3, "is_active": 1},
            ],
        )
        mock_coll.return_value = collection

        results = get_similar_products(TARGET_PRODUCT, ALL_PRODUCTS, top_n=2)

        assert len(results) == 2
        assert results[0]["product_id"] == 2
        assert results[0]["name"] == "MAC Lipstick"
        assert results[0]["similarity_score"] == 0.85

    @patch("services.recommendation_service.embed_single")
    @patch("services.recommendation_service.get_collection")
    @patch("services.recommendation_service.is_chromadb_available", return_value=True)
    def test_excludes_target_product(self, mock_avail, mock_coll, mock_embed):
        mock_embed.return_value = [0.1, 0.2, 0.3]

        collection = MagicMock()
        collection.count.return_value = 4
        collection.query.return_value = _mock_chroma_results(
            ids=["product_1", "product_2"],
            distances=[0.0, 0.2],
            metadatas=[
                {"product_id": 1, "is_active": 1},
                {"product_id": 2, "is_active": 1},
            ],
        )
        mock_coll.return_value = collection

        results = get_similar_products(TARGET_PRODUCT, ALL_PRODUCTS, top_n=3)

        product_ids = [r["product_id"] for r in results]
        assert 1 not in product_ids

    @patch("services.recommendation_service.embed_single")
    @patch("services.recommendation_service.get_collection")
    @patch("services.recommendation_service.is_chromadb_available", return_value=True)
    def test_similarity_score_computation(self, mock_avail, mock_coll, mock_embed):
        """ChromaDB cosine distance 0.3 should yield similarity 0.7."""
        mock_embed.return_value = [0.1]

        collection = MagicMock()
        collection.count.return_value = 2
        collection.query.return_value = _mock_chroma_results(
            ids=["product_2"],
            distances=[0.3],
            metadatas=[{"product_id": 2, "is_active": 1}],
        )
        mock_coll.return_value = collection

        results = get_similar_products(TARGET_PRODUCT, ALL_PRODUCTS, top_n=1)
        assert results[0]["similarity_score"] == 0.7

    @patch("services.recommendation_service.embed_single")
    @patch("services.recommendation_service.get_collection")
    @patch("services.recommendation_service.is_chromadb_available", return_value=True)
    def test_similarity_clamped_at_zero(self, mock_avail, mock_coll, mock_embed):
        """Distance > 1 should not yield negative similarity."""
        mock_embed.return_value = [0.1]

        collection = MagicMock()
        collection.count.return_value = 2
        collection.query.return_value = _mock_chroma_results(
            ids=["product_2"],
            distances=[1.5],
            metadatas=[{"product_id": 2, "is_active": 1}],
        )
        mock_coll.return_value = collection

        results = get_similar_products(TARGET_PRODUCT, ALL_PRODUCTS, top_n=1)
        assert results[0]["similarity_score"] == 0.0

    @patch("services.recommendation_service.embed_single")
    @patch("services.recommendation_service.get_collection")
    @patch("services.recommendation_service.is_chromadb_available", return_value=True)
    def test_enriches_with_full_product_data(self, mock_avail, mock_coll, mock_embed):
        mock_embed.return_value = [0.1]

        collection = MagicMock()
        collection.count.return_value = 2
        collection.query.return_value = _mock_chroma_results(
            ids=["product_4"],
            distances=[0.1],
            metadatas=[{"product_id": 4, "is_active": 1}],
        )
        mock_coll.return_value = collection

        results = get_similar_products(TARGET_PRODUCT, ALL_PRODUCTS, top_n=1)
        assert results[0]["name"] == "Canmake Blush"
        assert results[0]["brand_name"] == "Canmake"
        assert "similarity_score" in results[0]

    @patch("services.recommendation_service.embed_single")
    @patch("services.recommendation_service.get_collection")
    @patch("services.recommendation_service.is_chromadb_available", return_value=True)
    def test_respects_top_n(self, mock_avail, mock_coll, mock_embed):
        mock_embed.return_value = [0.1]

        collection = MagicMock()
        collection.count.return_value = 4
        collection.query.return_value = _mock_chroma_results(
            ids=["product_2", "product_3", "product_4"],
            distances=[0.1, 0.2, 0.3],
            metadatas=[
                {"product_id": 2, "is_active": 1},
                {"product_id": 3, "is_active": 1},
                {"product_id": 4, "is_active": 1},
            ],
        )
        mock_coll.return_value = collection

        results = get_similar_products(TARGET_PRODUCT, ALL_PRODUCTS, top_n=2)
        assert len(results) == 2


# ── TF-IDF fallback tests ────────────────────────────────────────────────

class TestTFIDFFallback:
    @patch("services.recommendation_service.is_chromadb_available", return_value=False)
    @patch("services.tfidf_fallback.get_similar_products")
    def test_falls_back_when_chromadb_unavailable(self, mock_tfidf, mock_avail):
        mock_tfidf.return_value = [{"product_id": 2, "similarity_score": 0.5}]

        results = get_similar_products(TARGET_PRODUCT, ALL_PRODUCTS, top_n=2)

        mock_tfidf.assert_called_once_with(TARGET_PRODUCT, ALL_PRODUCTS, 2)
        assert results == [{"product_id": 2, "similarity_score": 0.5}]


# ── Graceful degradation tests ───────────────────────────────────────────

class TestGracefulDegradation:
    @patch("services.recommendation_service.is_chromadb_available", return_value=True)
    @patch("services.recommendation_service.get_collection")
    @patch("services.tfidf_fallback.get_similar_products")
    def test_fallback_on_empty_collection(self, mock_tfidf, mock_coll, mock_avail):
        collection = MagicMock()
        collection.count.return_value = 0
        mock_coll.return_value = collection
        mock_tfidf.return_value = []

        get_similar_products(TARGET_PRODUCT, ALL_PRODUCTS)
        mock_tfidf.assert_called_once()

    @patch("services.recommendation_service.is_chromadb_available", return_value=True)
    @patch("services.recommendation_service.embed_single", return_value=None)
    @patch("services.recommendation_service.get_collection")
    @patch("services.tfidf_fallback.get_similar_products")
    def test_fallback_on_embed_failure(self, mock_tfidf, mock_coll, mock_embed, mock_avail):
        collection = MagicMock()
        collection.count.return_value = 10
        mock_coll.return_value = collection
        mock_tfidf.return_value = []

        get_similar_products(TARGET_PRODUCT, ALL_PRODUCTS)
        mock_tfidf.assert_called_once()

    @patch("services.recommendation_service.is_chromadb_available", return_value=True)
    @patch("services.recommendation_service.embed_single", return_value=[0.1])
    @patch("services.recommendation_service.get_collection")
    @patch("services.tfidf_fallback.get_similar_products")
    def test_fallback_on_query_exception(self, mock_tfidf, mock_coll, mock_embed, mock_avail):
        collection = MagicMock()
        collection.count.return_value = 10
        collection.query.side_effect = RuntimeError("ChromaDB error")
        mock_coll.return_value = collection
        mock_tfidf.return_value = []

        get_similar_products(TARGET_PRODUCT, ALL_PRODUCTS)
        mock_tfidf.assert_called_once()

    @patch("services.recommendation_service.is_chromadb_available", return_value=True)
    @patch("services.recommendation_service.get_collection", return_value=None)
    @patch("services.tfidf_fallback.get_similar_products")
    def test_fallback_on_collection_none(self, mock_tfidf, mock_coll, mock_avail):
        mock_tfidf.return_value = []

        get_similar_products(TARGET_PRODUCT, ALL_PRODUCTS)
        mock_tfidf.assert_called_once()
