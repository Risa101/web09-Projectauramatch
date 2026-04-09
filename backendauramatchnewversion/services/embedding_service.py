"""Embedding service for product vector search.

Loads the multilingual sentence-transformer model once and provides
functions to build document strings and compute embeddings.
"""
import logging

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    """Lazy-load the sentence-transformer model."""
    global _model
    if _model is not None:
        return _model
    try:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        logger.info("Loaded embedding model: paraphrase-multilingual-MiniLM-L12-v2")
        return _model
    except Exception as exc:
        logger.warning("Failed to load embedding model: %s", exc)
        return None


def build_product_document(product_dict: dict) -> str:
    """Build a single text document from product fields for embedding.

    Args:
        product_dict: must contain keys: name, category_name, brand_name,
                      description, personal_color. Optional: concern_names (list[str]).
    """
    parts = []
    parts.append(product_dict.get("name") or "")
    parts.append(product_dict.get("category_name") or "")
    parts.append(product_dict.get("brand_name") or "")
    parts.append(product_dict.get("description") or "")

    pc = product_dict.get("personal_color")
    if pc:
        parts.append(f"personal_color: {pc}")

    concerns = product_dict.get("concern_names")
    if concerns:
        parts.append(f"concerns: {', '.join(concerns)}")

    return " | ".join(p for p in parts if p)


def embed_texts(texts: list[str]) -> list[list[float]] | None:
    """Encode a list of texts into embeddings. Returns None on failure."""
    model = _get_model()
    if model is None:
        return None
    try:
        embeddings = model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
    except Exception as exc:
        logger.warning("Embedding failed: %s", exc)
        return None


def embed_single(text: str) -> list[float] | None:
    """Encode a single text. Returns None on failure."""
    result = embed_texts([text])
    return result[0] if result else None
