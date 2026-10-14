# src/retriever.py
# The retriever is the gatekeeper of the Grounding Layer: it decides what
# evidence is worth passing to the model, not what the answer is. Returns
# None when nothing clears the similarity threshold — callers MUST treat
# None as "route to the fallback," never as "ask the model anyway" (REQ-N-001).
from typing import Optional

import chromadb

from src import config
from src.providers import get_embeddings

_client = None
_collection = None
_embeddings_model = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
        _collection = _client.get_collection(config.CHROMA_COLLECTION_NAME)
    return _collection


def _get_embeddings():
    global _embeddings_model
    if _embeddings_model is None:
        _embeddings_model = get_embeddings()
    return _embeddings_model


def warmup() -> dict:
    """
    Build the ChromaDB client/collection and embeddings client once, at
    process startup (REQ-N-005), rather than lazily on the first request.
    Returns a small status dict the API's health check can use (ADR-002).
    """
    collection = _get_collection()
    _get_embeddings()
    return {"collection_name": collection.name, "document_count": collection.count()}


def retrieve(
    query: str,
    chunk_type: Optional[str] = None,
    product_id: Optional[str] = None,
    threshold: Optional[float] = None,
    k: Optional[int] = None,
) -> Optional[list[dict]]:
    """
    Retrieve relevant product chunks for a query.

    Args:
        query: customer's question.
        chunk_type: optional filter — restrict to one chunk type
                    (e.g. "care", "policy", "variants", "identity", "faq").
        product_id: optional filter — restrict to a specific product.
        threshold: override config.SIMILARITY_THRESHOLD (used by the
                   calibration script; production call sites should omit
                   this and use the configured value).
        k: override config.MAX_RETRIEVED_CHUNKS.

    Returns:
        A list of chunks above the similarity threshold, or None if nothing
        qualifies. Each chunk: {"text", "similarity", "metadata"}.
    """
    collection = _get_collection()
    embeddings_model = _get_embeddings()

    threshold = config.SIMILARITY_THRESHOLD if threshold is None else threshold
    k = config.MAX_RETRIEVED_CHUNKS if k is None else k

    query_vector = embeddings_model.embed_query(query)

    if len(query_vector) != config.EXPECTED_EMBEDDING_DIM:
        raise RuntimeError(
            f"Query embedding has {len(query_vector)} dimensions, expected "
            f"{config.EXPECTED_EMBEDDING_DIM} for provider {config.LLM_PROVIDER}. "
            "This usually means the collection was built with a different "
            "provider — re-ingest after switching LLM_PROVIDER (REQ-N-006)."
        )

    # NOTE: current ChromaDB (1.5.x) requires an explicit $and when combining
    # more than one top-level field in `where` — a plain
    # {"chunk_type": ..., "product_id": ...} dict (implicit AND) raises
    # "Expected where to have exactly one operator" on this version.
    # See docs/decisions/ADR-007-chromadb-multi-field-where-syntax.md and
    # docs/evidence/ for the exact error. Confirmed by test.
    conditions = []
    if chunk_type:
        conditions.append({"chunk_type": chunk_type})
    if product_id:
        conditions.append({"product_id": product_id})

    if len(conditions) == 0:
        where = None
    elif len(conditions) == 1:
        where = conditions[0]
    else:
        where = {"$and": conditions}

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=k,
        where=where,
        include=["documents", "distances", "metadatas"],
    )

    if not results["documents"] or not results["documents"][0]:
        return None

    retrieved = []
    for i, doc in enumerate(results["documents"][0]):
        distance = results["distances"][0][i]
        similarity = 1 - distance  # ChromaDB returns distance; convert to similarity
        if similarity >= threshold:
            retrieved.append({
                "text": doc,
                "similarity": round(similarity, 4),
                "metadata": results["metadatas"][0][i],
            })

    return retrieved if retrieved else None
