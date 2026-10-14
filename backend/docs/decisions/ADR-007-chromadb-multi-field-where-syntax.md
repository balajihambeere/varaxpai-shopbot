# ADR-007: Current ChromaDB requires explicit `$and` for multi-field `where` filters

## Status
Accepted

## Context
Book 1 Ch6 builds a `where` dict by adding keys directly — `where["chunk_type"] = ...; where["product_id"] = ...` — relying on implicit AND semantics across top-level keys. Running this against the installed `chromadb` (1.5.9) raises:

```
ValueError: Expected where to have exactly one operator, got {'chunk_type': 'policy', 'product_id': 'p020'} in query.
```

Confirmed directly by `tests/test_retriever.py::test_product_id_filter_isolates_one_products_policy_chunk` before this fix — not assumed. Another instance of framework §1.2's BOOK-CONFLICT category: the book's code was correct for the ChromaDB version current when it was written; this environment's ChromaDB version requires `{"$and": [{"chunk_type": "policy"}, {"product_id": "p020"}]}` instead of a flat multi-key dict.

## Decision
`src/retriever.py` builds a list of single-field conditions and wraps them in `{"$and": [...]}` whenever more than one filter is active; a single filter is passed as a bare dict (also valid, and simpler); no filter passes `where=None`.

## Alternatives considered
1. **Pin an old chromadb version matching the book** — rejected for the same reason as ADR-005 (old, unpatched dependency vs. a one-function fix).

## Consequences
None beyond the `where`-construction logic in `retrieve()`. Confirmed fixed by test (same test that caught the break now passes).
