"""Tests for the Redis Cache-Aside service.

Uses ``unittest.mock`` to patch Redis so tests run without a live server.
"""

import json
from decimal import Decimal
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from services.cache_service import (
    _default_serializer,
    _serialize,
    _deserialize,
    _build_cache_key,
    cache_get,
    cache_set,
    invalidate_key,
    invalidate_pattern,
    cached,
)


# ── Serialization tests ────────────────────────────────────────────────────

class TestSerialization:
    def test_decimal_serialized_to_float(self):
        result = _serialize({"price": Decimal("299.00")})
        assert json.loads(result)["price"] == 299.0

    def test_datetime_serialized_to_iso(self):
        dt = datetime(2026, 4, 9, 12, 0, 0)
        result = _serialize({"created_at": dt})
        assert json.loads(result)["created_at"] == "2026-04-09T12:00:00"

    def test_nested_structure(self):
        data = {
            "products": [
                {"name": "ลิปสติก", "price": Decimal("350.50")},
                {"name": "บลัชออน", "price": Decimal("499.00")},
            ]
        }
        result = _serialize(data)
        parsed = json.loads(result)
        assert parsed["products"][0]["name"] == "ลิปสติก"
        assert parsed["products"][1]["price"] == 499.0

    def test_thai_characters_preserved(self):
        data = {"name": "คอนซีลเลอร์ เนื้อแมตต์"}
        result = _serialize(data)
        assert "คอนซีลเลอร์" in result

    def test_roundtrip(self):
        original = {"id": 1, "price": Decimal("100.50"), "name": "test"}
        raw = _serialize(original)
        restored = _deserialize(raw)
        assert restored["id"] == 1
        assert restored["price"] == 100.5

    def test_unsupported_type_raises(self):
        with pytest.raises(TypeError):
            _serialize({"bad": object()})


# ── Cache key builder tests ─────────────────────────────────────────────────

class TestBuildCacheKey:
    def test_simple_key(self):
        key = _build_cache_key("products:list", {"skip": 0, "limit": 50}, {"db"})
        assert key == "products:list:limit=50:skip=0"

    def test_db_excluded(self):
        key = _build_cache_key("test", {"db": "session_obj", "id": 5}, {"db"})
        assert "db=" not in key
        assert "id=5" in key

    def test_none_values(self):
        key = _build_cache_key("p", {"category_id": None, "brand_id": 3}, {"db"})
        assert "category_id=None" in key
        assert "brand_id=3" in key

    def test_sorted_deterministic(self):
        key1 = _build_cache_key("p", {"a": 1, "b": 2}, set())
        key2 = _build_cache_key("p", {"b": 2, "a": 1}, set())
        assert key1 == key2


# ── cache_get / cache_set with mocked Redis ─────────────────────────────────

class TestCacheOperations:
    @patch("services.cache_service.get_redis")
    def test_cache_set_and_get_hit(self, mock_get_redis):
        mock_client = MagicMock()
        mock_get_redis.return_value = mock_client

        data = {"product_id": 1, "name": "Lipstick"}
        cache_set("test:key", data, ttl=60)

        mock_client.setex.assert_called_once()
        call_args = mock_client.setex.call_args
        assert call_args[0][0] == "test:key"
        assert call_args[0][1] == 60
        stored_json = call_args[0][2]

        mock_client.get.return_value = stored_json
        result = cache_get("test:key")
        assert result["product_id"] == 1
        assert result["name"] == "Lipstick"

    @patch("services.cache_service.get_redis")
    def test_cache_get_miss(self, mock_get_redis):
        mock_client = MagicMock()
        mock_get_redis.return_value = mock_client
        mock_client.get.return_value = None

        result = cache_get("nonexistent:key")
        assert result is None

    @patch("services.cache_service.get_redis")
    def test_invalidate_key(self, mock_get_redis):
        mock_client = MagicMock()
        mock_get_redis.return_value = mock_client

        invalidate_key("products:detail:5")
        mock_client.delete.assert_called_once_with("products:detail:5")

    @patch("services.cache_service.get_redis")
    def test_invalidate_pattern(self, mock_get_redis):
        mock_client = MagicMock()
        mock_get_redis.return_value = mock_client
        mock_client.scan.return_value = (0, ["products:list:1", "products:list:2"])

        invalidate_pattern("products:*")
        mock_client.delete.assert_called_once_with("products:list:1", "products:list:2")


# ── Graceful fallback tests (Redis unavailable) ─────────────────────────────

class TestGracefulFallback:
    @patch("services.cache_service.get_redis", return_value=None)
    def test_cache_get_returns_none_when_redis_down(self, _):
        result = cache_get("any:key")
        assert result is None

    @patch("services.cache_service.get_redis", return_value=None)
    def test_cache_set_does_not_crash_when_redis_down(self, _):
        cache_set("any:key", {"data": True}, ttl=60)

    @patch("services.cache_service.get_redis", return_value=None)
    def test_invalidate_does_not_crash_when_redis_down(self, _):
        invalidate_key("any:key")
        invalidate_pattern("any:*")

    @patch("services.cache_service.get_redis")
    def test_cache_get_handles_redis_exception(self, mock_get_redis):
        mock_client = MagicMock()
        mock_get_redis.return_value = mock_client
        mock_client.get.side_effect = ConnectionError("Redis gone")

        result = cache_get("test:key")
        assert result is None

    @patch("services.cache_service.get_redis")
    def test_cache_set_handles_redis_exception(self, mock_get_redis):
        mock_client = MagicMock()
        mock_get_redis.return_value = mock_client
        mock_client.setex.side_effect = ConnectionError("Redis gone")

        cache_set("test:key", {"data": True})


# ── @cached decorator tests ─────────────────────────────────────────────────

class TestCachedDecorator:
    @patch("services.cache_service.get_redis")
    def test_decorator_caches_on_miss(self, mock_get_redis):
        mock_client = MagicMock()
        mock_get_redis.return_value = mock_client
        mock_client.get.return_value = None

        call_count = 0

        @cached("test:func", ttl=300)
        def my_func(x=1, db=None):
            nonlocal call_count
            call_count += 1
            return {"result": x}

        result = my_func(x=42, db="fake_session")
        assert result == {"result": 42}
        assert call_count == 1
        mock_client.setex.assert_called_once()

    @patch("services.cache_service.get_redis")
    def test_decorator_returns_cached_on_hit(self, mock_get_redis):
        mock_client = MagicMock()
        mock_get_redis.return_value = mock_client
        mock_client.get.return_value = json.dumps({"result": 99})

        call_count = 0

        @cached("test:func", ttl=300)
        def my_func(x=1, db=None):
            nonlocal call_count
            call_count += 1
            return {"result": x}

        result = my_func(x=1, db="fake_session")
        assert result == {"result": 99}
        assert call_count == 0

    @patch("services.cache_service.get_redis", return_value=None)
    def test_decorator_falls_through_when_redis_down(self, _):
        call_count = 0

        @cached("test:func", ttl=300)
        def my_func(x=1, db=None):
            nonlocal call_count
            call_count += 1
            return {"result": x}

        result = my_func(x=7, db="fake")
        assert result == {"result": 7}
        assert call_count == 1
