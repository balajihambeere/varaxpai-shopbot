# Architecture

## System diagram

```
Browser (customer)
    │
    ▼
zudyog-fashion (Next.js, existing)         ← no changes required (REQ-T-006)
  app/api/chat/route.ts  ──POST {question,session_id}──┐
                                                        ▼
                                        ShopBot API (FastAPI, this build)
                                        ┌─────────────────────────────┐
                                        │ POST /ask   GET /health      │
                                        │   │                          │
                                        │   ▼                          │
                                        │ validate (empty/len/inject)  │
                                        │   │                          │
                                        │   ▼                          │
                                        │ retriever.retrieve(query)    │──► ChromaDB (persistent, ./chroma_db)
                                        │   │ (embed via provider)     │      cosine HNSW index, 23×N chunks
                                        │   ▼                          │
                                        │ threshold gate (≥ calibrated)│
                                        │   │                          │
                                        │   ├─ None ──► fallback text  │
                                        │   │                          │
                                        │   ▼                          │
                                        │ prompt.answer(query, chunks) │──► LLM provider (Ollama default / OpenAI optional)
                                        │   │ temperature = 0          │
                                        │   ▼                          │
                                        │ {answer, session_id}         │
                                        └─────────────────────────────┘
```

## Component responsibilities

| Component | File (planned) | Responsibility | Book chapter |
|---|---|---|---|
| Catalog data | `data/products.py` | Source of truth for 50 zUdyog products (already copied verbatim from existing `zuxpai/products.py`) | Ch5 Appendix-A schema |
| Chunker | `src/chunker.py` | `product_to_chunks()` — one product → identity/variants/policy/care/faq chunks | Ch5 |
| Provider abstraction | `src/providers.py` | Returns an embeddings client + chat client for `LLM_PROVIDER=openai|ollama` | Ch2; ADR-001 |
| Ingestion | `src/ingest.py` | Embeds all chunks, writes to ChromaDB | Ch4, Ch5 |
| Retriever | `src/retriever.py` | `retrieve(query, chunk_type=None, product_id=None)`, threshold gate, k=3 default | Ch6 |
| Prompt/chain | `src/prompt.py` | System prompt (grounding contract), `format_docs`, `answer(query)` — single entry point, see ADR-006 | Ch7 |
| API | `src/api.py` | FastAPI app, lifespan-built chain, Pydantic validation, `/ask`, `/health` | Ch8 |
| Evaluation | `evaluation/test_cases.py`, `evaluation/evaluate.py` | Labeled test set, RAGAS (Faithfulness, Context Precision) | Ch9 |
| Calibration | `scripts/calibrate_threshold.py` | Empirically derive the similarity threshold for the real 50-product catalog | Ch6; REQ-F-010 |
| Tests | `tests/` | Unit, integration, API, negative, security, mutation/fault-check | framework §11 |

## Request flow (happy path)

1. Customer submits a question in the existing chat widget.
2. Next.js `route.ts` forwards the raw JSON body to `SHOPBOT_API_URL/ask`.
3. FastAPI's Pydantic validator strips/normalizes the string, rejects empty/>500-char/injection-shaped input (HTTP 422 on reject).
4. `retrieve()` embeds the query with the configured provider, queries ChromaDB (optionally pre-filtered by `chunk_type`/`product_id`), keeps only results ≥ threshold, returns up to `k=3` chunks or `None`.
5. If `None`: the chain returns the book's fallback string immediately (LLM is not called — cheaper and guarantees the fallback text is exact, not paraphrased).
6. If chunks exist: `format_docs` labels them by `chunk_type`, the system prompt + labeled context + question go to the chat LLM at `temperature=0`.
7. The model's text becomes `AnswerResponse.answer`; `session_id` is echoed back unchanged (Book 1 scope has no multi-turn memory — see below).
8. FastAPI returns JSON; Next.js renders it in the chat widget.

## Error flow

| Failure point | Behavior | Requirement |
|---|---|---|
| Malformed/empty/too-long/injection-shaped input | HTTP 422 with Pydantic's field error, chain never invoked | REQ-N-004 |
| Retriever finds nothing ≥ threshold | HTTP 200, exact fallback sentence (not an error — framework note: this is "the Grounding Layer operating correctly," Ch6) | REQ-N-001 |
| Embedding/chat provider unreachable (Ollama not running / OpenAI network error) | HTTP 503 with a clear message, no stack trace leaked to the client; logged with request ID | REQ-N-009 (new — book doesn't cover provider-outage handling explicitly; ENGINEERING REQUIREMENT) |
| ChromaDB collection missing/empty (not yet ingested) | Startup check fails loudly at lifespan time, service refuses to report healthy, rather than serving empty-context answers silently | REQ-N-001 extension (ENGINEERING REQUIREMENT — book doesn't test this case, but it is the same class of silent-Grounding-Failure the whole book warns against) |
| Embedding-dimension mismatch (provider switched without re-ingest) | Must raise an explicit, caught exception, not a silently-wrong similarity score | REQ-N-006 |

## AI/LLM flow

Two swappable providers behind one interface (`src/providers.py`):

- **Ollama (default, free, local)**: `OllamaEmbeddings(model=nomic-embed-text)` (768-dim) + `OllamaLLM(model=llama3.2)`.
- **OpenAI (optional, paid, requires user's key)**: `OpenAIEmbeddings(model=text-embedding-3-small)` (1536-dim) + `ChatOpenAI(model=gpt-4o-mini, temperature=0)`.

The two are **not interchangeable on an existing collection** — dimensionality differs (768 vs 1536). Switching `LLM_PROVIDER` requires `rm -rf chroma_db/ && python src/ingest.py` (operational runbook item, documented in README/operations doc, not just in this architecture doc).

Prompt versioning: the system prompt text is a constant in `src/prompt.py` with a version comment and changelog, per Ch7's own discipline — any edit to the prompt is a reviewed change, not a casual tweak.

## Database / storage

ChromaDB `PersistentClient` at `./chroma_db`. Collection `zudyog_products`, `hnsw:space=cosine`. No relational database in Book 1 scope — no user accounts, no orders, no persisted conversation history (`session_id` is accepted and echoed for forward-compatibility with Book 2's memory work, but is not used to look up or store anything in Book 1 scope). This is intentional minimalism, not an oversight — framework §1.5 "do not over-engineer": a conversation-memory store is Book 2 scope per the book itself (C-025 area) and would be built without a stated requirement.

## Auth flow

**None in Book 1 scope.** The book never introduces authentication for the `/ask` endpoint — ShopBot is a public product-Q&A assistant, equivalent to a storefront search box. `UNKNOWN / NOT SPECIFIED IN BOOK` whether a production deployment would want API-key-gated access from the frontend; flagged in the threat model as an accepted risk at this scope (mitigated partially by rate limiting, REQ-N-010) rather than invented as a requirement the book doesn't support.

## Deployment

| Level | What | Status for this build |
|---|---|---|
| L0 | Files written, not run | Railway `Procfile` (REQ-T-005) |
| L1 | Runs locally from clean checkout per README | Target for this session — `VERIFIED` once achieved, with evidence |
| L2 | Runs in containers (Docker Compose) | Target for this session (REQ-T-004), framework's default hosting since no cloud access |
| L3 | Deployed to real cloud (Railway) | Not reachable this session — no Railway account/CLI access (U-04); stays `NOT-VERIFIED` |

## Observability

Structured JSON logs with a request ID per `/ask` call, logging: timestamp, request ID, query length (not full query text at default level, REQ-N-008), whether retrieval returned evidence, similarity score of top result, provider used, response latency. `/health` returns `{"status": "ok", "service": "ShopBot", "version": ...}` plus a dependency check (ChromaDB collection reachable and non-empty) — an upgrade over the book's literal health check, justified because the book's own Ch10 failures (vocabulary gaps, threshold-adjacent slips) are only debuggable with this data (ENGINEERING-DECISION, see ADR-002).

## Repository structure

```
shopbot/
├── data/products.py            (copied verbatim from existing catalog)
├── src/                        (chunker, providers, ingest, retriever, prompt, chain, api)
├── evaluation/                 (test_cases.py, evaluate.py)
├── scripts/                    (calibrate_threshold.py, and other one-off ops scripts)
├── tests/                      (unit, integration, api, security, mutation)
├── docs/
│   ├── book/                   (index, notes/ch01-10, concept-ledger, unknowns, classification)
│   ├── decisions/               (ADRs)
│   ├── evidence/                (command transcripts, dated)
│   ├── security/threat-model.md
│   ├── architecture.md (this file)
│   ├── requirements.md
│   └── traceability.md
├── .env.example
├── .gitignore
├── requirements.txt
├── Procfile                     (Railway, L0 only)
├── docker-compose.yml           (L2 target)
└── README.md
```

Every folder has a stated purpose above; none added speculatively (framework §1.5).
