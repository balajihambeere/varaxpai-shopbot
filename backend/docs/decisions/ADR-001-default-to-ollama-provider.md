# ADR-001: Default to the Ollama provider, not OpenAI

## Status
Accepted

## Context
Book 1's primary code path uses OpenAI (`text-embedding-3-small`, `gpt-4o-mini`). No `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is present in this environment, and none was supplied by the user. The book itself (Ch2, "The Free Alternative") explicitly documents a second, architecturally-identical path using Ollama (`nomic-embed-text` for embeddings, `llama3.2` for chat), stating "every piece of code in this book works with either option." Ollama's binary is already installed on this machine (`/opt/homebrew/bin/ollama`), though the service was not running and the models were not yet pulled at design time.

## Decision
`LLM_PROVIDER=ollama` is the default in `.env.example`. The OpenAI path is implemented behind the same provider-abstraction interface (REQ-T-002) and remains fully supported, but is opt-in and requires the user's own funded key.

## Alternatives considered
1. **Build only the OpenAI path and mark everything NOT-VERIFIED** — rejected. The book itself sanctions Ollama as an equal architecture, not a toy substitute, so this would understate what can actually be verified in this environment (framework §1.4.5 only requires the NOT-VERIFIED tag when an environment limit genuinely blocks verification — it does not here, since a real local LLM is available).
2. **Build a mock LLM provider with contract tests only** (framework §9's fallback for "no API key or model available") — rejected for the same reason: a mock is the fallback for when *no* real model is reachable; Ollama is a real, local model, so using it produces genuine (if locally-scoped) verified behavior rather than a mock.
3. **Require the user to supply an OpenAI key before proceeding** — rejected as unnecessarily blocking; the book explicitly designed around exactly this situation.

## Addendum (2026-10-14)
The user supplied a funded OpenAI API key after this ADR was written. This build's actual running configuration (`shopbot/.env`, gitignored) now sets `LLM_PROVIDER=openai`, matching the book's primary path exactly — so RAGAS scores and behavior can be compared directly against the book's own Chapter 9 baseline (Faithfulness 0.71, Context Precision 0.82) rather than only against an independently-derived Ollama-path baseline. `.env.example` (the committed template) is left defaulting to `ollama` so the repo remains runnable by anyone without a key, per the original decision below. The Ollama provider path is still implemented and tested (REQ-T-002) as a free/local fallback, not removed.

## Consequences
- Embedding dimensionality is 768 (Ollama) instead of 1536 (OpenAI) for this build's default ChromaDB collection — anyone switching providers later must re-ingest (REQ-N-006).
- RAGAS evaluation scores (REQ-F-009) will differ from the book's own reported OpenAI-path baseline (Faithfulness 0.71, Context Precision 0.82, Ch9) and must not be presented as reproducing those numbers — they are a new, independently-measured baseline for this build's provider+catalog combination.
- Marginal per-query cost is ₹0, matching REQ-N-007.
- `llama3.2` (2GB) running locally on an 8GB-RAM machine is the main resource-risk factor for this decision; if throughput/quality is inadequate, this ADR should be revisited with the user before switching defaults.
