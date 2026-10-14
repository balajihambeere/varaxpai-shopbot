# ADR-006: One `answer()` entry point, not two parallel implementations

## Status
Accepted

## Context
Two separate implementations of essentially the same operation were on the table: `src/prompt.py:answer(query)` (manual retrieve → format → invoke) and a hypothetical `src/chain.py:build_chain()` (an LCEL `RunnableSequence` using a `get_retriever()` wrapper around the retriever). Reconciling these into one call path matters: the evaluation harness needs exactly one function to call.

## Decision
Implement only `src/prompt.py:answer(query)` as the single callable both the API (Phase 3) and the evaluation harness (Phase 4) use. Do not also build a parallel LCEL chain object.

## Alternatives considered
1. **Build both call paths** — rejected. Two independent code paths that are supposed to produce the same behavior is exactly the kind of redundant abstraction framework §1.5 warns against ("three similar lines is better than a premature abstraction") — a bug fix applied to one path and not the other would silently reintroduce drift in whichever path the fix missed.
2. **Build only an LCEL chain, no `prompt.answer()`** — rejected because the evaluation code (REQ-F-009) calls `answer()` directly, and the chain version would need a `get_retriever()` LangChain-retriever wrapper with no concrete interface to build against — that would mean inventing an interface rather than implementing a specified one (framework §1.4.1).

## Consequences
`src/chain.py` is not created as a separate file. The "chain" concept — retriever → prompt → model → output — exists as the body of `src/prompt.py:answer()` instead of as a standalone LangChain `Runnable` object. Traceability for REQ-F-003 and REQ-F-004 points to `src/prompt.py`, not a `src/chain.py` that doesn't exist.
