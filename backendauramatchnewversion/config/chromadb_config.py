"""ChromaDB persistent vector store configuration.

Provides a singleton ChromaDB client with local persistent storage.
Mirrors the redis_config.py pattern: lazy init, graceful fallback.
"""
import logging
import os

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

CHROMA_PERSIST_DIR = os.getenv(
    "CHROMA_PERSIST_DIR",
    os.path.join(os.path.dirname(__file__), "..", "data", "chroma"),
)
CHROMA_COLLECTION_NAME = "products"

_chroma_client = None
_chroma_available: bool = False


def _init_chromadb():
    """Create a ChromaDB persistent client. Returns None on failure."""
    global _chroma_client, _chroma_available
    try:
        import chromadb

        os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        _chroma_client = client
        _chroma_available = True
        logger.info("ChromaDB initialized at %s", CHROMA_PERSIST_DIR)
        return client
    except Exception as exc:
        _chroma_client = None
        _chroma_available = False
        logger.warning("ChromaDB unavailable (%s), falling back to TF-IDF", exc)
        return None


def get_chromadb_client():
    """Return the cached ChromaDB client, lazily initializing on first call."""
    global _chroma_client, _chroma_available
    if _chroma_client is not None:
        return _chroma_client
    if not _chroma_available and _chroma_client is None:
        return _init_chromadb()
    return None


def get_collection():
    """Return the products collection, or None if unavailable."""
    client = get_chromadb_client()
    if client is None:
        return None
    try:
        return client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    except Exception as exc:
        logger.warning("ChromaDB collection error: %s", exc)
        return None


def is_chromadb_available() -> bool:
    """Check current ChromaDB availability."""
    return _chroma_available


def check_chromadb_health() -> dict:
    """Startup health check. Returns status dict for logging."""
    client = get_chromadb_client()
    if client is None:
        return {"status": "unavailable", "message": "ChromaDB not initialized"}
    try:
        collection = get_collection()
        count = collection.count() if collection else 0
        return {
            "status": "connected",
            "path": CHROMA_PERSIST_DIR,
            "product_count": count,
        }
    except Exception:
        return {"status": "unavailable", "message": "ChromaDB health check failed"}
