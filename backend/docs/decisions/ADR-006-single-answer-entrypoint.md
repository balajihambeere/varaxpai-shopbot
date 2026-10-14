# ADR-006: One `answer()` entry point, not the book's two parallel implementations

## Status
Accepted

## Context
Book 1 Ch7 shows two separate implementations of essentially the same operation: `src/prompt.py:answer(query)` (manual retrieve → format → invoke) and `src/chain.py:build_chain()` (an LCEL `RunnableSequence` using a `get_retriever()` function that chapter never actually defines — it presumes a LangChain `Retriever` object wrapping the Ch6 `retrieve()` function). Both are presented as valid; the book doesn't reconcile them into one call path, and `evaluation/evaluate.py` (Ch9) calls `src.prompt.answer()`, not the chain.

## Decision
Implement only `src/prompt.py:answer(query)` as the single callable both the API (Phase 3) and the evaluation harness (Phase 4) use. Do not also build a parallel LCEL chain object.

## Alternatives considered
1. **Build both, as the book literally shows** — rejected. Two independent code paths that are supposed to produce the same behavior is exactly the kind of redundant abstraction framework §1.5 warns against ("three similar lines is better than a premature abstraction") — a bug fix applied to one path and not the other would silently reintroduce drift in whichever path the fix missed.
2. **Build only the LCEL chain, drop `prompt.answer()`** — rejected because Ch9's evaluation code (which this build also implements, REQ-F-009) calls `answer()` directly, and the book never defines the missing `get_retriever()` LangChain-retriever wrapper the chain version needs — building it would be inventing an interface the book doesn't specify (framework §1.4.1).

## Consequences
`src/chain.py` is not created as a separate file. The "chain" concept from Ch7/Ch8 — retriever → prompt → model → output — exists as the body of `src/prompt.py:answer()` instead of as a standalone LangChain `Runnable` object. Traceability for REQ-F-003 and REQ-F-004 points to `src/prompt.py`, not a `src/chain.py` that doesn't exist.
