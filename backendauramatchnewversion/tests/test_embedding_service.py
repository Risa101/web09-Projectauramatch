"""Tests for the embedding service.

Tests document building and embedding functions.
Uses ``unittest.mock`` to patch the sentence-transformer model.
"""

from unittest.mock import patch, MagicMock

import pytest

from services.embedding_service import (
    build_product_document,
    embed_texts,
    embed_single,
)


# ── Document building tests ───────────────────────────────────────────────

class TestBuildProductDocument:
    def test_all_fields_populated(self):
        product = {
            "name": "Maybelline Super Stay Vinyl Ink",
            "category_name": "ลิปสติก",
            "brand_name": "Maybelline",
            "description": "ลิปจิ้มจุ่มเนื้อไวนิล ติดทน 16 ชม.",
            "personal_color": "spring,summer",
            "concern_names": ["ผิวแห้ง", "ผิวแพ้ง่าย"],
        }
        doc = build_product_document(product)
        assert "Maybelline Super Stay Vinyl Ink" in doc
        assert "ลิปสติก" in doc
        assert "Maybelline" in doc
        assert "ลิปจิ้มจุ่มเนื้อไวนิล" in doc
        assert "personal_color: spring,summer" in doc
        assert "concerns: ผิวแห้ง, ผิวแพ้ง่าย" in doc

    def test_missing_optional_fields(self):
        product = {
            "name": "Test Product",
            "category_name": None,
            "brand_name": None,
            "description": None,
            "personal_color": None,
        }
        doc = build_product_document(product)
        assert doc == "Test Product"
        assert "personal_color" not in doc
        assert "concerns" not in doc

    def test_thai_text_preserved(self):
        product = {
            "name": "คอนซีลเลอร์ เนื้อแมตต์",
            "category_name": "คอนซีลเลอร์",
            "brand_name": "Canmake",
            "description": "คอนซีลเลอร์เนื้อครีม ปกปิดดี",
        }
        doc = build_product_document(product)
        assert "คอนซีลเลอร์ เนื้อแมตต์" in doc
        assert "Canmake" in doc

    def test_empty_dict(self):
        doc = build_product_document({})
        assert doc == ""

    def test_pipe_delimited_format(self):
        product = {
            "name": "Product A",
            "category_name": "Blush",
            "brand_name": "Brand X",
            "description": "Great product",
        }
        doc = build_product_document(product)
        assert " | " in doc
        parts = doc.split(" | ")
        assert len(parts) == 4

    def test_concerns_without_personal_color(self):
        product = {
            "name": "Test",
            "concern_names": ["สิว"],
        }
        doc = build_product_document(product)
        assert "concerns: สิว" in doc
        assert "personal_color" not in doc

    def test_empty_concern_names_list(self):
        product = {
            "name": "Test",
            "concern_names": [],
        }
        doc = build_product_document(product)
        assert "concerns" not in doc


# ── Embedding tests ───────────────────────────────────────────────────────

class TestEmbedTexts:
    @patch("services.embedding_service._get_model")
    def test_returns_embeddings_list(self, mock_get_model):
        mock_model = MagicMock()
        fake_embeddings = MagicMock()
        fake_embeddings.tolist.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_model.encode.return_value = fake_embeddings
        mock_get_model.return_value = mock_model

        result = embed_texts(["text1", "text2"])
        assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_model.encode.assert_called_once_with(["text1", "text2"], show_progress_bar=False)

    @patch("services.embedding_service._get_model")
    def test_returns_none_when_model_unavailable(self, mock_get_model):
        mock_get_model.return_value = None
        result = embed_texts(["text1"])
        assert result is None

    @patch("services.embedding_service._get_model")
    def test_returns_none_on_encode_exception(self, mock_get_model):
        mock_model = MagicMock()
        mock_model.encode.side_effect = RuntimeError("CUDA error")
        mock_get_model.return_value = mock_model

        result = embed_texts(["text1"])
        assert result is None


class TestEmbedSingle:
    @patch("services.embedding_service.embed_texts")
    def test_returns_single_embedding(self, mock_embed_texts):
        mock_embed_texts.return_value = [[0.1, 0.2, 0.3]]
        result = embed_single("test text")
        assert result == [0.1, 0.2, 0.3]
        mock_embed_texts.assert_called_once_with(["test text"])

    @patch("services.embedding_service.embed_texts")
    def test_returns_none_on_failure(self, mock_embed_texts):
        mock_embed_texts.return_value = None
        result = embed_single("test text")
        assert result is None
