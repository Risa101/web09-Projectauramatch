"""Tests for the RAG service.

Tests retrieval, context formatting, system prompt construction,
chat history formatting, and the full RAG orchestrator.
Uses ``unittest.mock`` to patch ChromaDB, embedding model, and Gemini API.
"""

import asyncio
from unittest.mock import patch, MagicMock

import pytest

# Register all ORM models so SQLAlchemy can resolve relationships
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

from services.rag_service import (
    retrieve_product_context,
    fetch_products_by_ids,
    format_product_context,
    build_analysis_context,
    build_system_prompt,
    format_chat_history,
    generate_rag_response,
    BEAUTY_CONSULTANT_PERSONA,
    MAX_HISTORY_MESSAGES,
)


# ── Test data ────────────────────────────────────────────────────────────

SAMPLE_PRODUCTS = [
    {
        "product_id": 1,
        "name": "Maybelline Super Stay Vinyl Ink",
        "brand_name": "Maybelline",
        "category_name": "ลิปสติก",
        "price": 350.0,
        "description": "ลิปจิ้มจุ่มเนื้อไวนิล ติดทน 16 ชม.",
        "personal_color": "spring,summer",
    },
    {
        "product_id": 2,
        "name": "Romand Juicy Lasting Tint",
        "brand_name": "Romand",
        "category_name": "ลิปสติก",
        "price": 290.0,
        "description": "ทินท์เนื้อฉ่ำ สีสดใส",
        "personal_color": "spring",
    },
]


def _mock_chroma_results(ids, metadatas):
    """Build a ChromaDB query result dict."""
    return {
        "ids": [ids],
        "distances": [[0.1] * len(ids)],
        "metadatas": [metadatas],
        "documents": [["doc"] * len(ids)],
    }


def _mock_analysis(**kwargs):
    """Create a mock AnalysisResult object."""
    analysis = MagicMock()
    analysis.face_shape = kwargs.get("face_shape", "oval")
    analysis.skin_tone = kwargs.get("skin_tone", "light")
    analysis.skin_undertone = kwargs.get("skin_undertone", "warm")
    analysis.personal_color = kwargs.get("personal_color", "spring")
    return analysis


def _mock_message(prompt=None, response=None):
    """Create a mock GeminiMessage object."""
    msg = MagicMock()
    msg.prompt = prompt
    msg.response = response
    return msg


# ── Retrieve product context tests ──────────────────────────────────────

class TestRetrieveProductContext:
    @patch("services.rag_service.embed_single")
    @patch("services.rag_service.get_collection")
    def test_returns_product_ids_on_success(self, mock_coll, mock_embed):
        mock_embed.return_value = [0.1, 0.2, 0.3]

        collection = MagicMock()
        collection.count.return_value = 10
        collection.query.return_value = _mock_chroma_results(
            ids=["product_1", "product_2", "product_3"],
            metadatas=[
                {"product_id": 1, "is_active": 1},
                {"product_id": 2, "is_active": 1},
                {"product_id": 3, "is_active": 1},
            ],
        )
        mock_coll.return_value = collection

        result = retrieve_product_context("แนะนำลิปสติก", top_k=3)
        assert result == [1, 2, 3]

    @patch("services.rag_service.get_collection", return_value=None)
    def test_returns_none_when_chromadb_unavailable(self, mock_coll):
        result = retrieve_product_context("test query")
        assert result is None

    @patch("services.rag_service.embed_single", return_value=None)
    @patch("services.rag_service.get_collection")
    def test_returns_none_when_embedding_fails(self, mock_coll, mock_embed):
        collection = MagicMock()
        collection.count.return_value = 10
        mock_coll.return_value = collection

        result = retrieve_product_context("test query")
        assert result is None

    @patch("services.rag_service.embed_single", return_value=[0.1])
    @patch("services.rag_service.get_collection")
    def test_returns_none_on_query_exception(self, mock_coll, mock_embed):
        collection = MagicMock()
        collection.count.return_value = 10
        collection.query.side_effect = RuntimeError("ChromaDB error")
        mock_coll.return_value = collection

        result = retrieve_product_context("test query")
        assert result is None

    @patch("services.rag_service.get_collection")
    def test_returns_none_on_empty_collection(self, mock_coll):
        collection = MagicMock()
        collection.count.return_value = 0
        mock_coll.return_value = collection

        result = retrieve_product_context("test query")
        assert result is None

    @patch("services.rag_service.embed_single", return_value=[0.1])
    @patch("services.rag_service.get_collection")
    def test_respects_top_k(self, mock_coll, mock_embed):
        collection = MagicMock()
        collection.count.return_value = 10
        collection.query.return_value = _mock_chroma_results(
            ids=["product_1"],
            metadatas=[{"product_id": 1, "is_active": 1}],
        )
        mock_coll.return_value = collection

        retrieve_product_context("test", top_k=7)
        _, kwargs = collection.query.call_args
        assert kwargs["n_results"] == 7


# ── Fetch products by IDs tests ─────────────────────────────────────────

class TestFetchProductsByIds:
    def test_returns_product_dicts(self):
        mock_product = MagicMock()
        mock_product.product_id = 1
        mock_product.name = "Test Lipstick"
        mock_product.brand.name = "TestBrand"
        mock_product.category.name = "ลิปสติก"
        mock_product.price = 350.0
        mock_product.description = "A test product"
        mock_product.personal_color = "spring"

        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_product]

        result = fetch_products_by_ids([1], mock_db)
        assert len(result) == 1
        assert result[0]["name"] == "Test Lipstick"
        assert result[0]["brand_name"] == "TestBrand"
        assert result[0]["price"] == 350.0

    def test_returns_empty_for_no_ids(self):
        mock_db = MagicMock()
        result = fetch_products_by_ids([], mock_db)
        assert result == []

    def test_handles_missing_brand_and_category(self):
        mock_product = MagicMock()
        mock_product.product_id = 1
        mock_product.name = "No Brand Product"
        mock_product.brand = None
        mock_product.category = None
        mock_product.price = None
        mock_product.description = None
        mock_product.personal_color = None

        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_product]

        result = fetch_products_by_ids([1], mock_db)
        assert result[0]["brand_name"] is None
        assert result[0]["category_name"] is None
        assert result[0]["price"] is None


# ── Format product context tests ────────────────────────────────────────

class TestFormatProductContext:
    def test_formats_multiple_products(self):
        ctx = format_product_context(SAMPLE_PRODUCTS)
        assert "1." in ctx
        assert "2." in ctx
        assert "สินค้าที่เกี่ยวข้องจากระบบ" in ctx

    def test_includes_all_fields(self):
        ctx = format_product_context(SAMPLE_PRODUCTS[:1])
        assert "Maybelline Super Stay Vinyl Ink" in ctx
        assert "Maybelline" in ctx
        assert "ลิปสติก" in ctx
        assert "฿350" in ctx
        assert "ลิปจิ้มจุ่มเนื้อไวนิล" in ctx

    def test_returns_empty_for_none(self):
        assert format_product_context(None) == ""

    def test_returns_empty_for_empty_list(self):
        assert format_product_context([]) == ""

    def test_thai_content_preserved(self):
        thai_product = [{
            "product_id": 1,
            "name": "คอนซีลเลอร์ เนื้อแมตต์",
            "brand_name": "Canmake",
            "category_name": "คอนซีลเลอร์",
            "price": 420.0,
            "description": "คอนซีลเลอร์เนื้อครีม ปกปิดดี",
        }]
        ctx = format_product_context(thai_product)
        assert "คอนซีลเลอร์ เนื้อแมตต์" in ctx
        assert "คอนซีลเลอร์เนื้อครีม ปกปิดดี" in ctx

    def test_handles_missing_optional_fields(self):
        product = [{
            "product_id": 1,
            "name": "Test",
            "brand_name": None,
            "category_name": None,
            "price": None,
            "description": None,
        }]
        ctx = format_product_context(product)
        assert "Test" in ctx
        assert "ไม่ระบุ" in ctx


# ── Build analysis context tests ────────────────────────────────────────

class TestBuildAnalysisContext:
    def test_formats_complete_analysis(self):
        analysis = _mock_analysis()
        ctx = build_analysis_context(analysis)
        assert "ข้อมูลผู้ใช้" in ctx
        assert "oval" in ctx
        assert "light" in ctx
        assert "warm" in ctx
        assert "spring" in ctx

    def test_returns_empty_for_none(self):
        assert build_analysis_context(None) == ""

    def test_handles_partial_analysis(self):
        analysis = _mock_analysis(
            face_shape="round",
            skin_tone=None,
            skin_undertone=None,
            personal_color=None,
        )
        ctx = build_analysis_context(analysis)
        assert "round" in ctx
        assert "สีผิว" not in ctx


# ── Build system prompt tests ───────────────────────────────────────────

class TestBuildSystemPrompt:
    def test_includes_persona(self):
        prompt = build_system_prompt("", "")
        assert "AuraMatch Beauty Consultant" in prompt

    def test_includes_product_context(self):
        product_ctx = "--- สินค้า ---\n1. Test Product"
        prompt = build_system_prompt(product_ctx, "")
        assert "Test Product" in prompt

    def test_includes_analysis_context(self):
        analysis_ctx = "--- ข้อมูลผู้ใช้ ---\nรูปทรงใบหน้า: oval"
        prompt = build_system_prompt("", analysis_ctx)
        assert "oval" in prompt

    def test_works_without_any_context(self):
        prompt = build_system_prompt("", "")
        assert BEAUTY_CONSULTANT_PERSONA in prompt
        # No dynamic sections appended beyond persona
        assert "สินค้าที่เกี่ยวข้องจากระบบ" not in prompt
        assert "--- ข้อมูลผู้ใช้ ---" not in prompt


# ── Format chat history tests ───────────────────────────────────────────

class TestFormatChatHistory:
    def test_formats_user_and_model_messages(self):
        messages = [
            _mock_message(prompt="สวัสดี", response="สวัสดีค่ะ"),
            _mock_message(prompt="แนะนำลิป", response="ขอแนะนำ..."),
        ]
        history = format_chat_history(messages)
        assert len(history) == 4
        assert history[0] == {"role": "user", "parts": ["สวัสดี"]}
        assert history[1] == {"role": "model", "parts": ["สวัสดีค่ะ"]}

    def test_limits_to_last_n_messages(self):
        messages = [
            _mock_message(prompt=f"msg{i}", response=f"resp{i}")
            for i in range(20)
        ]
        history = format_chat_history(messages)
        # Last 10 messages, each produces 2 entries (user + model)
        assert len(history) == MAX_HISTORY_MESSAGES * 2

    def test_returns_empty_for_no_messages(self):
        assert format_chat_history([]) == []

    def test_handles_none_fields(self):
        messages = [_mock_message(prompt="hello", response=None)]
        history = format_chat_history(messages)
        assert len(history) == 1
        assert history[0]["role"] == "user"


# ── Generate RAG response tests ─────────────────────────────────────────

class TestGenerateRagResponse:
    @patch("services.rag_service.create_gemini_model")
    @patch("services.rag_service.retrieve_product_context", return_value=[1, 2])
    @patch("services.rag_service.fetch_products_by_ids", return_value=SAMPLE_PRODUCTS)
    def test_successful_rag_response(self, mock_fetch, mock_retrieve, mock_model):
        mock_genai = MagicMock()
        mock_genai.generate_content.return_value = MagicMock(text="แนะนำลิปสติก Maybelline ค่ะ")
        mock_model.return_value = mock_genai

        text, img = asyncio.run(generate_rag_response(
            prompt="แนะนำลิปสติก",
            session_messages=[],
            db=MagicMock(),
        ))
        assert text == "แนะนำลิปสติก Maybelline ค่ะ"
        assert img is None
        mock_model.assert_called_once()
        call_kwargs = mock_model.call_args[1]
        assert "system_instruction" in call_kwargs
        assert "AuraMatch" in call_kwargs["system_instruction"]

    @patch("services.rag_service.create_gemini_model")
    @patch("services.rag_service.retrieve_product_context", return_value=None)
    def test_fallback_without_chromadb(self, mock_retrieve, mock_model):
        mock_genai = MagicMock()
        mock_genai.generate_content.return_value = MagicMock(text="คำแนะนำทั่วไป")
        mock_model.return_value = mock_genai

        text, _ = asyncio.run(generate_rag_response(
            prompt="แนะนำลิปสติก",
            session_messages=[],
        ))
        assert text == "คำแนะนำทั่วไป"
        mock_genai.generate_content.assert_called_once()

    @patch("services.rag_service.create_gemini_model")
    @patch("services.rag_service.retrieve_product_context", return_value=None)
    def test_fallback_without_analysis(self, mock_retrieve, mock_model):
        mock_genai = MagicMock()
        mock_genai.generate_content.return_value = MagicMock(text="ตอบได้ค่ะ")
        mock_model.return_value = mock_genai

        text, _ = asyncio.run(generate_rag_response(
            prompt="test",
            session_messages=[],
            analysis=None,
        ))
        assert text == "ตอบได้ค่ะ"
        call_kwargs = mock_model.call_args[1]
        assert "--- ข้อมูลผู้ใช้ ---" not in call_kwargs["system_instruction"]

    @patch("services.rag_service.create_gemini_model")
    @patch("services.rag_service.retrieve_product_context", return_value=None)
    def test_includes_image(self, mock_retrieve, mock_model):
        mock_genai = MagicMock()
        mock_genai.generate_content.return_value = MagicMock(text="เห็นรูปแล้วค่ะ")
        mock_model.return_value = mock_genai

        import tempfile
        from PIL import Image

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img = Image.new("RGB", (10, 10), color="red")
            img.save(f, format="PNG")
            temp_path = f.name

        try:
            text, _ = asyncio.run(generate_rag_response(
                prompt="วิเคราะห์รูปนี้",
                session_messages=[],
                image_path=temp_path,
            ))
            assert text == "เห็นรูปแล้วค่ะ"

            call_args = mock_genai.generate_content.call_args[0][0]
            user_msg = call_args[-1]
            assert len(user_msg["parts"]) == 2
        finally:
            import os
            os.unlink(temp_path)

    @patch("services.rag_service.create_gemini_model")
    @patch("services.rag_service.retrieve_product_context", return_value=None)
    def test_error_on_gemini_failure(self, mock_retrieve, mock_model):
        mock_genai = MagicMock()
        mock_genai.generate_content.side_effect = RuntimeError("API quota exceeded")
        mock_model.return_value = mock_genai

        text, img = asyncio.run(generate_rag_response(
            prompt="test",
            session_messages=[],
        ))
        assert "Error:" in text
        assert "API quota exceeded" in text
        assert img is None

    @patch("services.rag_service.create_gemini_model")
    @patch("services.rag_service.retrieve_product_context", return_value=[1])
    @patch("services.rag_service.fetch_products_by_ids", return_value=SAMPLE_PRODUCTS[:1])
    def test_chat_history_included(self, mock_fetch, mock_retrieve, mock_model):
        mock_genai = MagicMock()
        mock_genai.generate_content.return_value = MagicMock(text="ตอบต่อค่ะ")
        mock_model.return_value = mock_genai

        prev_messages = [_mock_message(prompt="สวัสดี", response="สวัสดีค่ะ")]

        asyncio.run(generate_rag_response(
            prompt="แนะนำต่อ",
            session_messages=prev_messages,
            db=MagicMock(),
        ))

        call_args = mock_genai.generate_content.call_args[0][0]
        assert len(call_args) == 3  # 2 history entries + 1 new user message
        assert call_args[0]["role"] == "user"
        assert call_args[0]["parts"] == ["สวัสดี"]
        assert call_args[1]["role"] == "model"
        assert call_args[2]["role"] == "user"
        assert call_args[2]["parts"] == ["แนะนำต่อ"]
