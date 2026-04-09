import logging
import os

import redis
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

_redis_client: redis.Redis | None = None
_redis_available: bool = False


def _init_redis() -> redis.Redis | None:
    """Create a Redis connection. Returns None if Redis is unreachable."""
    global _redis_client, _redis_available
    try:
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=3,
        )
        client.ping()
        _redis_client = client
        _redis_available = True
        logger.info("Redis connected at %s:%s", REDIS_HOST, REDIS_PORT)
        return client
    except (redis.ConnectionError, redis.TimeoutError, OSError) as exc:
        _redis_client = None
        _redis_available = False
        logger.warning("Redis unavailable (%s), running without cache", exc)
        return None


def get_redis() -> redis.Redis | None:
    """Return the cached Redis client, lazily initializing on first call."""
    global _redis_client, _redis_available
    if _redis_client is not None:
        return _redis_client
    if not _redis_available and _redis_client is None:
        return _init_redis()
    return None


def is_redis_available() -> bool:
    """Check current Redis availability."""
    return _redis_available


def check_redis_health() -> dict:
    """Startup health check. Returns status dict for logging."""
    client = get_redis()
    if client is None:
        return {"status": "unavailable", "message": "Redis not connected, running without cache"}
    try:
        client.ping()
        return {"status": "connected", "host": REDIS_HOST, "port": REDIS_PORT}
    except (redis.ConnectionError, redis.TimeoutError, OSError):
        return {"status": "unavailable", "message": "Redis ping failed, running without cache"}
