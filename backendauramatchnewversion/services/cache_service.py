"""Cache-Aside pattern implementation with Redis.

Provides a ``@cached`` decorator for FastAPI route functions and manual
cache helpers (``cache_get``, ``cache_set``, ``invalidate_pattern``).

All operations are wrapped in try/except so that a Redis outage never
crashes the application — it simply falls through to the database.
"""

import functools
import json
import logging
from decimal import Decimal
from datetime import datetime

from config.redis_config import get_redis

logger = logging.getLogger(__name__)

# ── JSON serializer that handles SQLAlchemy / Decimal / datetime ────────────

def _default_serializer(obj):
    """Convert non-standard types so ``json.dumps`` doesn't raise."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, "__dict__"):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _serialize(data) -> str:
    return json.dumps(data, default=_default_serializer, ensure_ascii=False)


def _deserialize(raw: str):
    return json.loads(raw)


# ── Low-level helpers ───────────────────────────────────────────────────────

def cache_get(key: str):
    """Read from Redis. Returns deserialized data or None on miss/error."""
    client = get_redis()
    if client is None:
        return None
    try:
        raw = client.get(key)
        if raw is not None:
            logger.debug("Cache HIT: %s", key)
            return _deserialize(raw)
        logger.debug("Cache MISS: %s", key)
        return None
    except Exception as exc:
        logger.warning("Redis GET failed for %s: %s", key, exc)
        return None


def cache_set(key: str, data, ttl: int = 3600):
    """Write to Redis with TTL. Silently fails on error."""
    client = get_redis()
    if client is None:
        return
    try:
        client.setex(key, ttl, _serialize(data))
        logger.debug("Cache SET: %s (TTL=%ds)", key, ttl)
    except Exception as exc:
        logger.warning("Redis SET failed for %s: %s", key, exc)


def invalidate_key(key: str):
    """Delete a single cache key."""
    client = get_redis()
    if client is None:
        return
    try:
        client.delete(key)
        logger.debug("Cache INVALIDATE: %s", key)
    except Exception as exc:
        logger.warning("Redis DELETE failed for %s: %s", key, exc)


def invalidate_pattern(pattern: str):
    """Delete all keys matching a glob pattern (e.g. ``products:*``).

    Uses SCAN to avoid blocking Redis with a KEYS command on large datasets.
    """
    client = get_redis()
    if client is None:
        return
    try:
        cursor = 0
        deleted = 0
        while True:
            cursor, keys = client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                client.delete(*keys)
                deleted += len(keys)
            if cursor == 0:
                break
        if deleted:
            logger.debug("Cache INVALIDATE pattern '%s': %d keys deleted", pattern, deleted)
    except Exception as exc:
        logger.warning("Redis SCAN/DELETE failed for pattern '%s': %s", pattern, exc)


# ── Decorator ───────────────────────────────────────────────────────────────

def _build_cache_key(prefix: str, kwargs: dict, exclude: set[str]) -> str:
    """Build a deterministic cache key from function kwargs.

    Parameters in *exclude* (e.g. ``{"db"}``) are omitted from the key.
    None values become the literal string ``"None"``.
    """
    parts = [prefix]
    for k, v in sorted(kwargs.items()):
        if k in exclude:
            continue
        parts.append(f"{k}={v}")
    return ":".join(parts)


def cached(prefix: str, ttl: int = 3600, exclude_params: set[str] | None = None):
    """Cache-Aside decorator for FastAPI endpoint functions.

    Parameters
    ----------
    prefix : str
        Cache key namespace, e.g. ``"products:list"``.
    ttl : int
        Time-to-live in seconds (default 3600 = 1 hour).
    exclude_params : set[str] | None
        Parameter names to exclude from the cache key.
        ``"db"`` is always excluded automatically.
    """
    _exclude = {"db"}
    if exclude_params:
        _exclude |= exclude_params

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = _build_cache_key(prefix, kwargs, _exclude)

            # Try cache first
            hit = cache_get(key)
            if hit is not None:
                return hit

            # Cache miss — call the real function
            result = func(*args, **kwargs)

            # Store result in cache
            cache_set(key, result, ttl)

            return result
        return wrapper
    return decorator
