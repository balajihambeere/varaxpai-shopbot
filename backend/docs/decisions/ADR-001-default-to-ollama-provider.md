# ADR-001: Default to the Ollama provider, not OpenAI

## Status
Superseded by ADR-010 (2026-10-14) — Ollama support has been removed from the codebase entirely; this record is kept for why it was chosen in the first place.

## Context
No `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` was present in this environment at design time, and none had been supplied by the user yet. Ollama offers an architecturally-identical local path (`nomic-embed-text` for embeddings, `llama3.2` for chat), with the same abstraction working for either option. Ollama's binary was already installed on this machine (`/opt/homebrew/bin/ollama`), though the service was not running and the models were not yet pulled at design time.

## Decision
`LLM_PROVIDER=ollama` is the default in `.env.example`. The OpenAI path is implemented behind the same provider-abstraction interface (REQ-T-002) and remains fully supported, but is opt-in and requires the user's own funded key.

## Alternatives considered
1. **Build only the OpenAI path and mark everything NOT-VERIFIED** — rejected. A real local LLM is available, so this would understate what can actually be verified in this environment (framework §1.4.5 only requires the NOT-VERIFIED tag when an environment limit genuinely blocks verification — it does not here).
2. **Build a mock LLM provider with contract tests only** (framework §9's fallback for "no API key or model available") — rejected for the same reason: a mock is the fallback for when *no* real model is reachable; Ollama is a real, local model, so using it produces genuine (if locally-scoped) verified behavior rather than a mock.
3. **Require the user to supply an OpenAI key before proceeding** — rejected as unnecessarily blocking when a working free alternative exists.

## Addendum (2026-10-14)
The user supplied a funded OpenAI API key after this ADR was written. This build's actual running configuration (`.env`, gitignored) now sets `LLM_PROVIDER=openai`. `.env.example` (the committed template) is left defaulting to `ollama` so the repo remains runnable by anyone without a key, per the original decision below. The Ollama provider path is still implemented and tested (REQ-T-002) as a free/local fallback, not removed. (This addendum itself is now historical — see ADR-010, which removes Ollama support entirely.)

## Consequences
- Embedding dimensionality is 768 (Ollama) instead of 1536 (OpenAI) for this build's default ChromaDB collection — anyone switching providers later must re-ingest (REQ-N-006).
- RAGAS evaluation scores (REQ-F-009) are this build's own independently-measured baseline for its provider+catalog combination, not compared against any other baseline.
- Marginal per-query cost is ₹0, matching REQ-N-007.
- `llama3.2` (2GB) running locally on an 8GB-RAM machine is the main resource-risk factor for this decision; if throughput/quality is inadequate, this ADR should be revisited with the user before switching defaults.
