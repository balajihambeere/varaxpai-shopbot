# ADR-009: RAGAS dataset column names changed since Book 1 was written

## Status
Accepted

## Context
Book 1 Ch9's `evaluation/evaluate.py` builds a `datasets.Dataset` with columns `{question, answer, contexts, ground_truth}`. Inspecting the installed `ragas` (0.2.15, pinned per ADR-008) metric classes directly — `ragas.metrics._faithfulness.Faithfulness._required_columns` and `ragas.metrics._context_precision.*._required_columns` — shows they require `{user_input, response, retrieved_contexts}` (Faithfulness) and `{user_input, retrieved_contexts, reference}` (Context Precision) instead. Confirmed by reading the installed package source, not assumed from memory or documentation that might itself be stale.

## Decision
`evaluation/evaluate.py` builds the dataset with the current column names (`user_input`, `response`, `retrieved_contexts`, `reference`) and passes `llm=get_chat_model()`, `embeddings=get_embeddings()` explicitly to `ragas.evaluate()` (this build's provider abstraction, ADR-001), since `ragas.evaluate()` no longer silently defaults to an OpenAI judge model the way the book's example implies.

## Alternatives considered
1. **Pin an old `ragas` matching the book's schema** — rejected for the same reason as ADR-005/007/008: these are schema/column renames in an actively maintained library area, not a security-relevant freeze candidate, and an old `ragas` is exactly the version with the broken Vertex AI import this build already had to route around (ADR-008) — going older would not even dodge that problem, since the 0.2.15 line already had it too.

## Consequences
Anyone updating `ragas` further in the future should re-check `_required_columns` on the metrics actually used, the same way this ADR did, rather than assuming the book's or this ADR's column names are permanent.
