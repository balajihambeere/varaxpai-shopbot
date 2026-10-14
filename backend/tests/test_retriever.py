# tests/test_retriever.py
# Integration tests against the real, already-ingested ChromaDB collection
# (framework §11: "use real dependencies where possible, such as a real
# test database" — not mocked). Requires `python -m src.ingest` to have
# been run first against the current .env (OpenAI, this build) — these
# tests make real embedding API calls.
import pytest

from src import config
from src.retriever import retrieve, _get_collection


@pytest.fixture(autouse=True, scope="module")
def _require_ingested_collection():
    collection = _get_collection()
    if collection.count() == 0:
        pytest.skip("ChromaDB collection is empty — run `python -m src.ingest` first")


def test_known_query_returns_correct_grounded_evidence():
    """REQ-F-002: a query with a real catalog answer must return it above
    the configured threshold, as the top result."""
    results = retrieve("What is the price of the Heavyweight Woolen Shawl?")
    assert results is not None
    top = results[0]
    assert top["metadata"]["product_id"] == "p002"
    assert top["metadata"]["chunk_type"] == "variants"
    assert top["similarity"] >= config.SIMILARITY_THRESHOLD


def test_unanswerable_query_returns_none():
    """REQ-N-001: absent evidence must be None, never a guessed chunk."""
    results = retrieve("Do you have a loyalty rewards program?")
    assert results is None


def test_winter_wedding_query_does_not_clear_threshold():
    """Adversarial case: the retriever must not hand the model an
    adjacent-but-wrong chunk — an unrelated anarkali suit chunk scores
    0.51 similarity for this exact query, below this catalog's threshold."""
    results = retrieve("Do you have anything for a winter wedding?")
    assert results is None


def test_product_id_filter_isolates_one_products_policy_chunk():
    """REQ-F-005: six products share the identical return-policy text
    'Returns within 7 days, unused.' (p017, p019, p020, p023, p046, p047).
    A product-scoped query must return only that product's policy chunk,
    not a near-duplicate from a different product."""
    results = retrieve(
        "What is the return policy?",
        chunk_type="policy",
        product_id="p020",
        threshold=0.0,
    )
    assert results is not None
    assert all(r["metadata"]["product_id"] == "p020" for r in results)


def test_embedding_dimension_mismatch_raises_loudly(monkeypatch):
    """REQ-N-006: a provider/collection dimension mismatch must raise an
    explicit error, never silently return wrong nearest-neighbours."""
    import src.retriever as retriever_module

    class _WrongDimEmbeddings:
        def embed_query(self, text):
            return [0.0] * (config.EXPECTED_EMBEDDING_DIM + 1)

    monkeypatch.setattr(retriever_module, "_embeddings_model", _WrongDimEmbeddings())
    with pytest.raises(RuntimeError, match="dimensions"):
        retrieve("any query")
