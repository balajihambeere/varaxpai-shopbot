# scripts/smoke_test.py
# Vertical-slice check: a handful of queries exercising the grounded-
# answer path, the no-evidence fallback path, and known failure shapes
# (type-mismatch deflection, weak-evidence rejection).
from src.prompt import answer, NO_EVIDENCE_FALLBACK
from src.retriever import retrieve

QUERIES = [
    ("Does the Printed Silk Saree need dry cleaning?", "grounded (care)"),
    ("What colours does the Breathable Cotton Kurta come in?", "grounded (variants)"),
    ("What is the return policy for the Banarasi Silk Saree?", "grounded (policy)"),
    ("Do you sell men's sherwanis?", "fallback — not in catalog"),
    ("Does the Printed Silk Saree have a cotton lining?", "fallback — attribute not in catalog"),
    ("Do you have anything for a winter wedding?", "fallback or weak-evidence — 0.51 similarity case"),
]

for query, expected_shape in QUERIES:
    print(f"\n{'='*70}\nQuery: {query}\nExpected shape: {expected_shape}")
    evidence = retrieve(query)
    if evidence is None:
        print("Retriever: None (no evidence cleared threshold)")
    else:
        for e in evidence:
            print(f"  [{e['similarity']}] ({e['metadata']['chunk_type']}) "
                  f"{e['metadata'].get('product_name','?')}: {e['text'][:70]}...")
    response = answer(query)
    print(f"ShopBot: {response}")
    if evidence is None:
        assert response == NO_EVIDENCE_FALLBACK, "No-evidence path must return the exact fallback string"

print("\nSmoke test complete.")
