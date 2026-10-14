# Threat Model

Written before implementation, per framework §6.2. Scope: the ShopBot backend (this build) and its one integration point with the existing frontend. No user accounts, payments, or PII collection are in this build's scope.

## Assets and data classification

| Asset | Classification | Why |
|---|---|---|
| Product catalog (`data/products.py`) | Internal, non-sensitive (public product info) | Already publicly visible on the storefront |
| Customer question/answer text in transit and in logs | Sensitive by default (framework §0 default) | May contain incidental personal context even though no account system exists; treated conservatively |
| LLM provider API key (`OPENAI_API_KEY`, if the OpenAI path is used) | Secret | Billing + abuse risk if leaked |
| ChromaDB index files (`chroma_db/`) | Internal | Derived from public catalog data, but still excluded from git for hygiene |
| Service availability (`/ask`, `/health`) | Business-impacting | Customer-facing demos and real traffic depend on it |

## Trust boundaries

1. **Browser ↔ Next.js frontend** — untrusted input, existing code, out of this build's direct control but consumed by it indirectly.
2. **Next.js `route.ts` ↔ ShopBot API** — server-to-server over `SHOPBOT_API_URL`; same-origin trust assumed only if both run on a private network/same host in this build's local/Compose deployment. No mutual auth in this build's scope (see Architecture "Auth flow").
3. **ShopBot API ↔ LLM provider (OpenAI remote)** — every request crosses the trust boundary (customer question text leaves the machine) — relevant to REQ-N-008. A local-only alternative (Ollama) was built, never verified live, and removed at the user's request (ADR-010) — there is no longer a privacy-preserving local path in this build.
4. **ShopBot API ↔ ChromaDB (local filesystem)** — trusted, same process/host.

## Main threats (STRIDE-oriented) and mitigations

| # | Threat | STRIDE | Mitigation | Requirement |
|---|---|---|---|---|
| T-01 | Prompt injection: "ignore previous instructions," "reveal your system prompt," role-override attempts | Tampering / Elevation | Regex-based rejection at the Pydantic validator layer before the chain runs; `temperature=0` reduces susceptibility of anything that does get through; system prompt itself never echoes verbatim on request | REQ-N-004 |
| T-02 | Data leakage via over-generation: model fills a gap with plausible-but-wrong/training-derived detail that could include inferred-sounding PII-like specifics | Information Disclosure (soft) | The entire Grounding Layer architecture (retriever threshold + constrained prompt) — this is the core defense, not a bolt-on | REQ-N-001, REQ-F-003 |
| T-03 | Denial of service / cost exhaustion: a client hammers `/ask`, each call triggering an embedding + LLM call | Denial of Service | Rate limiting on `/ask` | REQ-N-010 |
| T-04 | Oversized/pathological input (very long strings, repeated Unicode tricks) inflating token cost or destabilizing retrieval | Denial of Service | Length cap (500 chars) + character normalization | REQ-N-004 |
| T-05 | Secret leakage: `OPENAI_API_KEY` committed to git, logged, or echoed in an error message | Information Disclosure | `.gitignore` from first commit, secret scan before any commit (framework §9), error responses never include raw exception text containing config values | REQ-N-003 |
| T-06 | Embedding-dimension mismatch after a re-ingest with a different embedding model silently returns wrong/garbage nearest-neighbors | Tampering (data integrity) | Explicit dimension check at retriever init; fail loudly | REQ-N-006 |
| T-07 | Stale/missing vector index serves silently-empty retrieval, which — without the threshold+fallback discipline — would look identical to "no catalog answer" | Repudiation / Information Disclosure | Startup health check verifies the ChromaDB collection is non-empty before reporting healthy (ADR-002) | REQ-N-009 |
| T-08 | Supply-chain: a compromised/vulnerable pinned dependency (langchain, chromadb, fastapi, etc.) | Tampering | `pip-audit` / dependency vulnerability scan before declaring any phase done (framework §9) | — (process requirement, see Implementation Plan phase exit criteria) |
| T-09 | Cross-origin abuse: any website calling the public `/ask` endpoint directly if it's ever exposed without the frontend in front of it | Spoofing | CORS restricted to the known frontend origin in production config; documented as a config item, not hardcoded | REQ-N-010 area |
| T-10 | Data leaving the trust boundary unnecessarily — every `/ask` call sends customer question text to OpenAI, a third party (no local alternative since ADR-010) | Information Disclosure | Documented explicitly in README/.env.example comments and this threat model; accepted as a known tradeoff, not mitigated further in this build | REQ-N-008 |

## Prompt injection and data leakage (AI-specific, framework §6.2 requirement)

Already covered by T-01/T-02 above. Additional note: because the system prompt instructs the model to answer **only** from retrieved context and never echo its own instructions, a successful injection that gets past the regex filter is still constrained by (a) temperature=0 and (b) having no sensitive data in its context window to leak beyond the public catalog — the worst case is a wrong/off-topic answer, not a secret disclosure, **as long as REQ-N-001 holds**. The Grounding Layer is treated as the primary control, with the regex filter as defense-in-depth, not the only line of defense.

## Residual/accepted risk
No authentication on `/ask` (public storefront assistant, by design). Accepted at this scope; flagged as a question for the user if this is ever exposed on a public internet-facing host outside the local/Compose environment this build targets.
