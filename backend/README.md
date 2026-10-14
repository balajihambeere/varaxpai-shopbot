# ShopBot

An AI-powered product assistant for **zUdyog Fashion**, a fictional Indian clothing retailer. ShopBot answers customer questions about a 50-product catalog using retrieval-augmented generation (RAG), and — critically — says "I don't know, contact support" rather than guessing when it has no evidence for an answer.

This is a real, working implementation of a retrieve-then-constrain RAG architecture ("Grounding Layer"): retrieve relevant product evidence first, then constrain the language model to answer only from that evidence. No retrieved evidence → no answer, by construction, not by prompt-writing discipline alone.

## Architecture

```
Customer question
      │
      ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Retriever   │────▶│  Similarity   │────▶│   Prompt/    │────▶ Grounded answer
│ (ChromaDB)   │     │  threshold    │     │   Chain      │      (or exact fallback)
└─────────────┘     │  gate (0.62)  │     └─────────────┘
                     └──────────────┘
```

- **Ingestion** (`src/ingest.py`, `src/chunker.py`): the 50-product catalog is split into per-concern chunks (identity, variants, policy, care, FAQ) and embedded into a persistent ChromaDB collection.
- **Retrieval** (`src/retriever.py`): a customer question is embedded and matched against the collection. Only chunks clearing a calibrated similarity threshold (0.62 for this catalog — see `docs/evidence/2026-10-14_threshold-calibration.txt`) are returned; otherwise `None`.
- **Grounding** (`src/prompt.py`): the language model is given only the retrieved evidence and instructed never to answer beyond it. When retrieval returns `None`, the model is never even called — the exact fallback string is returned directly.
- **API** (`src/api.py`): `POST /ask` and `GET /health`, matching the contract the existing `zudyog-fashion` Next.js frontend already expects.

Full component breakdown: `docs/architecture.md`. Design decisions and the reasoning behind them: `docs/decisions/ADR-*.md`. Every requirement mapped to the code and test that implements it: `docs/traceability.md`.

## Features

- Grounded Q&A over the product catalog (care instructions, sizing/variants, return policy, FAQs)
- Exact, consistent fallback when no evidence supports an answer — never a fabricated guess
- Loud failure (not a silent wrong answer) on an embedding-dimension mismatch if the catalog is ever re-ingested with a different embedding model
- Input validation (empty, overlong, prompt-injection-shaped), rate limiting, structured request-ID logging
- RAGAS evaluation harness (Faithfulness, Context Precision) against a 20-case labeled test set

## Stack

Python 3.12, FastAPI, ChromaDB, LangChain (`langchain-core` 1.x + `langchain-openai`), OpenAI (`text-embedding-3-small` + `gpt-4o-mini`), pytest + pytest-cov, RAGAS. Full pinned list: `requirements.txt`. Rationale: `docs/stack.md`.

## Local setup

```bash
python3 -m venv venv
source venv/bin/activate
```

**Install dependencies.** A single `pip install -r requirements.txt` will fail with `ResolutionImpossible` — `ragas` pulls the latest `langchain-community`, which conflicts with this project's `langchain-core` 1.x line (see ADR-008). Install in two steps instead:

```bash
grep -v '^langchain-community==' requirements.txt > /tmp/requirements-no-lc.txt
pip install -r /tmp/requirements-no-lc.txt
pip install --no-deps $(grep '^langchain-community==' requirements.txt)
```

**Configure.** Copy `.env.example` to `.env` and fill in `OPENAI_API_KEY`. OpenAI is the only supported provider (ADR-010) — a funded OpenAI account is required. See the "Environment variables" section below.

**Ingest the catalog:**
```bash
python -m src.ingest
```
This builds the ChromaDB collection at `./chroma_db`. Re-run it whenever `data/products.py` changes, or whenever you switch `LLM_PROVIDER` (the embedding dimension changes — see REQ-N-006 in `docs/traceability.md`).

**Run the API:**
```bash
uvicorn src.api:app --reload
```
Then: `curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"question":"Does the Printed Silk Saree need dry cleaning?"}'`

## Environment variables

See `.env.example` for the full, commented list. The ones you'll actually touch:

| Variable | Default | Purpose |
|---|---|---|
| `LLM_PROVIDER` | `openai` | OpenAI only (ADR-010) |
| `OPENAI_API_KEY` | — | required — a funded OpenAI account |
| `SIMILARITY_THRESHOLD` | `0.75` | a provisional default — this build re-calibrated to `0.62` for its real 50-product catalog (see evidence); re-run `scripts/calibrate_threshold.py` if you change the catalog |
| `CHROMA_DB_PATH` | `./chroma_db` | where the vector store lives |
| `RATE_LIMIT_PER_MINUTE` | `20` | per-client `/ask` rate limit |

## Running tests

```bash
pytest tests/                                    # full suite (26 tests)
pytest --cov=src.chunker --cov=src.retriever --cov=src.prompt --cov=src.api --cov-report=term-missing tests/   # with coverage
```
Coverage floor is 80% on core logic; current: 95% overall. See `docs/evidence/2026-10-14_phase6-coverage.txt`.

Run the RAGAS evaluation harness (costs real API calls on the `openai` provider):
```bash
python -m evaluation.evaluate
```

## Deployment

**Docker Compose (local, L2):**
```bash
docker compose up --build -d
docker compose run --rm shopbot-api python -m src.ingest   # first run only — the named volume starts empty
docker compose restart shopbot-api                          # clear the restart backoff from the pre-ingest crash loop
curl http://localhost:8000/health
```
Do **not** use `docker compose exec` for the first ingest — the container can't stay running long enough to `exec` into before the collection exists; `run --rm` starts a fresh one-off container against the same volume instead.

**Railway (cloud, L3):** `Procfile` is written with the standard start command, but has not been deployed or verified in this build (no Railway account access during development). Treat it as untested.

Full operational detail (monitoring, logs, troubleshooting, recovery): `docs/operations.md`.

## Frontend

The existing `zudyog-fashion` Next.js app (`../zudyog-fashion/`) is the customer-facing chat widget. Its `app/api/chat/route.ts` already forwards `{question, session_id}` to `${SHOPBOT_API_URL:-http://localhost:8000}/ask` — no frontend changes were needed to integrate this backend. Run it with `npm run dev` alongside the backend above.

## Known limitations

See `docs/known-limitations.md` for the full, honest list — including an occasion-vocabulary gap that doesn't fully resolve at this catalog's scale, and an accepted multi-intent-query limitation.

## Documentation map

| Doc | Contents |
|---|---|
| `docs/architecture.md` | components and how they interact |
| `docs/api.md` | every public endpoint |
| `docs/operations.md` | deploy, monitor, logs, troubleshooting, recovery |
| `docs/traceability.md` | every requirement mapped to its code and test |
| `docs/requirements.md` | full requirement list with priorities and acceptance criteria |
| `docs/known-limitations.md` | honest list of gaps and unknowns |
| `docs/sources.md` | external references used, with access dates |
| `docs/decisions/ADR-*.md` | why each non-obvious engineering choice was made |
| `docs/security/threat-model.md` | STRIDE-oriented threat model and mitigations |
| `docs/evidence/*` | dated command transcripts backing every `VERIFIED` claim above |
