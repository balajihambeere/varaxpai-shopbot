# Technology Stack

Established technology is kept unless there is a strong production reason to change it. Alternatives considered are cross-referenced to ADRs where one exists, to avoid duplicating that reasoning here.

| Layer | Choice | Why | Alternatives (why not) |
|---|---|---|---|
| Language | Python 3.x (3.14.5 available locally) | Mature ecosystem for this stack (LangChain, ChromaDB, FastAPI, RAGAS) | — |
| Orchestration | LangChain (`langchain`, `langchain-openai`) | Makes retriever→prompt→model structure explicit in code | Hand-rolled HTTP calls (more boilerplate, less visible architecture) |
| Embeddings | OpenAI `text-embedding-3-small` | Semantic retrieval requires embeddings, not keyword search | Keyword search, synonym dictionaries, structured filters — all fail on paraphrase/synonym queries; a local alternative (Ollama) was tried and later removed (ADR-010 — never run live, user asked to drop it) |
| Vector store | ChromaDB, local, persistent, HNSW/cosine | Local, free, zero-config, sufficient at this catalog scale | FAISS (no persistence/concurrency story), managed cloud vector DBs (premature cost/complexity before architecture is proven) |
| Chat model | OpenAI `gpt-4o-mini` | Smaller model + good evidence beats larger model + drift | Larger/fine-tuned models — more expensive and no more reliable without grounding; a local alternative (Ollama) was removed (ADR-010) |
| API framework | FastAPI + Uvicorn | Async by default, Pydantic validation, auto-docs | Flask (synchronous, blocks on external calls) |
| Evaluation | RAGAS + HuggingFace `datasets` | Purpose-built RAG metrics, diagnostic by component | A single accuracy percentage (undebuggable — doesn't separate retrieval quality from generation faithfulness) |
| Local deploy | Docker Compose | Reversible, local, zero-cost, closer to production shape than a bare venv | Directly invoking Railway (no account access this session) |
| Cloud deploy (file only) | Railway `Procfile` | Standard start command, ready for the user to run themselves | — |
| Test framework | `pytest`, `pytest-cov` | Standard Python testing/coverage tooling | — |

## Deliberately not adopted
Qdrant Cloud, hybrid search/re-ranking libraries, conversation-memory stores, response caches — out of scope for this build, see `docs/known-limitations.md`.
