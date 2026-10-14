# tests/test_chunker.py
# Unit tests for src.chunker. No network, no DB — pure function tests.
# Includes negative cases encoding common chunking mistakes (missing
# sections, un-anchored text) as regression tests (framework §8:
# "add at least one test that fails if the concept is removed or faked").
from src.chunker import product_to_chunks, all_chunks

SAMPLE_PRODUCT = {
    "id": "p999",
    "name": "Test Kurta",
    "description": "A test kurta for unit testing.",
    "category": "kurta",
    "fabric": "cotton",
    "occasion": "casual",
    "colors": ["red", "blue"],
    "sizes": ["S", "M"],
    "price": 1000,
    "stock_status": "in stock",
    "return_policy": "Returns within 7 days.",
    "exchange_policy": "Size exchange within 10 days.",
    "care_instructions": "Hand wash only.",
    "faqs": [
        {"question": "Does it shrink?", "answer": "No."},
        {"question": "Is it office-appropriate?", "answer": "Yes."},
    ],
}


def test_chunk_count_matches_sections_plus_faqs():
    chunks = product_to_chunks(SAMPLE_PRODUCT)
    # identity + variants + policy + care + 2 faqs = 6
    assert len(chunks) == 6


def test_every_chunk_has_a_type_and_product_id_in_metadata():
    chunks = product_to_chunks(SAMPLE_PRODUCT)
    for c in chunks:
        assert c["metadata"]["chunk_type"] in {"identity", "variants", "policy", "care", "faq"}
        assert c["metadata"]["product_id"] == "p999"


def test_every_chunk_is_anchored_with_the_product_name():
    """Anchoring rule: a chunk retrieved in isolation must still be
    meaningful. 'Dry clean only' with no product name is nearly
    unsearchable — this test fails if that rule is silently dropped, per
    framework §8's fault-injection requirement."""
    chunks = product_to_chunks(SAMPLE_PRODUCT)
    for c in chunks:
        assert SAMPLE_PRODUCT["name"] in c["text"], (
            f"chunk {c['id']} does not contain the product name — "
            "violates the anchoring rule"
        )


def test_missing_optional_sections_do_not_produce_empty_chunks():
    product = dict(SAMPLE_PRODUCT)
    product["return_policy"] = ""
    product["care_instructions"] = ""
    product["faqs"] = []
    chunks = product_to_chunks(product)
    # Only identity + variants remain
    assert len(chunks) == 2
    assert {c["metadata"]["chunk_type"] for c in chunks} == {"identity", "variants"}


def test_all_chunks_flattens_the_whole_catalog():
    catalog = [SAMPLE_PRODUCT, dict(SAMPLE_PRODUCT, id="p998", name="Another Kurta")]
    chunks = all_chunks(catalog)
    assert len(chunks) == 12
    ids = [c["id"] for c in chunks]
    assert len(ids) == len(set(ids)), "chunk ids must be unique across the catalog"
