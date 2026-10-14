# ADR-010: Drop Ollama provider support; OpenAI only

## Status
Accepted. Supersedes ADR-001.

## Context
ADR-001 defaulted this build to a free Ollama alternative (`nomic-embed-text` + `llama3.2`), with OpenAI as an opt-in path once the user supplied a funded key. In practice, every live run in this build's entire history — ingestion, calibration, RAGAS evaluation, the FastAPI layer, the Docker Compose deployment — used the OpenAI path exclusively (`.env`'s actual `LLM_PROVIDER=openai` since early in the build). A GATE 2 review additionally found that the Ollama path was never run live end-to-end at all, only import-checked (`import langchain_ollama` succeeding) — closing that gap would have required pulling `llama3.2` (~2GB), and the user explicitly asked to drop Ollama entirely instead of verifying it.

## Decision
Remove Ollama support from the codebase rather than carry an unused, never-verified code path:
- `src/providers.py`: removed the `OllamaEmbeddings`/`OllamaLLM` branches; `get_embeddings()`/`get_chat_model()` now build OpenAI clients only.
- `src/config.py`: `LLM_PROVIDER` now only accepts `"openai"` (raises if anything else); removed `OLLAMA_*` settings; `EXPECTED_EMBEDDING_DIM` is now a fixed `1536`.
- `src/prompt.py`: removed the Ollama plain-string-prompt branch (`OllamaLLM` isn't a chat model, needed different message handling) — always builds chat messages now.
- `requirements.txt`, `.env.example`, `.env`: removed `langchain-ollama`/`ollama` packages and all `OLLAMA_*` variables.
- `docs/requirements.md`, `docs/traceability.md`, `docs/architecture.md`, `docs/stack.md`, `docs/security/threat-model.md`, `README.md`, `docs/operations.md`, `docs/api.md`, `docs/known-limitations.md`: updated to describe an OpenAI-only system, not a dual-provider one.

**Not changed:** the dimension-mismatch guard itself (REQ-N-006's loud-failure behavior) — it's still correct, defensive engineering even with a single provider, in case the catalog is ever re-ingested with a different embedding model later. The provider-abstraction *module* (`src/providers.py`) is also kept, now as a plain cached-client factory, not a multi-provider switch — removing it entirely would mean the lifespan/retriever code importing `langchain_openai` directly, a smaller change but not obviously better than keeping one clearly-named module as the single place that builds model clients.

## Alternatives considered
1. **Verify Ollama live, then drop it anyway** — rejected by the user directly; not worth a 2GB download for a path about to be deleted.
2. **Keep Ollama as dead/untested code, just stop recommending it** — rejected; the user asked for all references removed, and carrying untested provider-branching code is worse than not having it (a future contributor could "fix" the Ollama branch, believe it's verified, and ship something that was never actually run).
3. **Delete/rewrite ADR-001 in place** — rejected; ADRs are a historical decision record (framework convention already established in this project, ADR-005 through ADR-009). ADR-001 is marked `Superseded by ADR-010` instead, preserving why Ollama was chosen in the first place.

## Consequences
- `REQ-N-007` ("zero marginal cost via a local model") and the provider-swapping framing of `REQ-N-006`/`REQ-T-002` no longer apply as originally written — updated in `docs/requirements.md` with a note pointing here, not silently deleted.
- This build now has a hard dependency on a funded OpenAI account; there is no free/local fallback.
- A separate, later cleanup pass removed all source-material chapter/book references from this codebase entirely (code comments, requirements, traceability, every ADR, and a notes directory that existed purely to track chapter-by-chapter reading) — this ADR's own original wording has been updated accordingly rather than left as the only place still citing a source that the rest of the project no longer references.
