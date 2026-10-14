# src/ingest.py
# Book 1, Ch4 + Ch5: embed every chunk once, store in a persistent
# ChromaDB collection. Run as a script: `python -m src.ingest`.
import chromadb

from src import config
from src.providers import get_embeddings
from src.chunker import all_chunks
from data.products import PRODUCTS


def ingest() -> int:
    embeddings_model = get_embeddings()
    client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)

    # REQ-N-006: never silently reuse a collection built with a different
    # embedding dimensionality than the active provider produces.
    try:
        existing = client.get_collection(config.CHROMA_COLLECTION_NAME)
        if existing.count() > 0:
            peek = existing.peek(limit=1)
            if peek["embeddings"] is not None and len(peek["embeddings"]) > 0:
                existing_dim = len(peek["embeddings"][0])
                if existing_dim != config.EXPECTED_EMBEDDING_DIM:
                    raise RuntimeError(
                        f"Collection '{config.CHROMA_COLLECTION_NAME}' was built with "
                        f"{existing_dim}-dim embeddings but LLM_PROVIDER="
                        f"{config.LLM_PROVIDER} produces {config.EXPECTED_EMBEDDING_DIM}-dim "
                        f"embeddings. Delete {config.CHROMA_DB_PATH} and re-ingest, or "
                        f"switch LLM_PROVIDER back to match the existing collection."
                    )
    except Exception as e:
        if "does not exist" not in str(e) and "RuntimeError" not in type(e).__name__:
            pass  # collection simply doesn't exist yet — fine, created below

    collection = client.get_or_create_collection(
        name=config.CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    chunks = all_chunks(PRODUCTS)
    print(f"Products: {len(PRODUCTS)}  ->  Chunks: {len(chunks)}")

    texts = [c["text"] for c in chunks]
    vectors = embeddings_model.embed_documents(texts)

    actual_dim = len(vectors[0])
    if actual_dim != config.EXPECTED_EMBEDDING_DIM:
        raise RuntimeError(
            f"Provider {config.LLM_PROVIDER} returned {actual_dim}-dim embeddings, "
            f"expected {config.EXPECTED_EMBEDDING_DIM}. Check config.EXPECTED_EMBEDDING_DIM."
        )

    # Replace wholesale rather than upsert — simplest correct behavior for
    # a catalog that is re-ingested as a unit (Ch5's "rebuild the index"
    # instruction after any chunking-strategy change).
    if collection.count() > 0:
        all_ids = collection.get()["ids"]
        if all_ids:
            collection.delete(ids=all_ids)

    collection.add(
        ids=[c["id"] for c in chunks],
        embeddings=vectors,
        documents=texts,
        metadatas=[c["metadata"] for c in chunks],
    )

    print(f"Ingested {collection.count()} chunks into ChromaDB "
          f"(provider={config.LLM_PROVIDER}, dim={actual_dim}).")
    return collection.count()


if __name__ == "__main__":
    ingest()
