# Technology Stack

Per framework §0, book-required technology is kept unless there is a strong production reason to change it. All choices below are BOOK-SPECIFIED unless marked otherwise; alternatives considered are cross-referenced to the book notes/ADRs where the book itself already argues the point, to avoid duplicating that reasoning here.

| Layer | Choice | Why | Alternatives (why not) | Source |
|---|---|---|---|---|
| Language | Python 3.x (3.14.5 available locally) | Book's entire codebase is Python | — | Ch2 |
| Orchestration | LangChain (`langchain`, `langchain-openai`) | Makes retriever→prompt→model structure explicit in code | Hand-rolled HTTP calls (more boilerplate, less visible architecture) | Ch2 |
| Embeddings | OpenAI `text-embedding-3-small` | Semantic retrieval requires embeddings, not keyword search | Keyword search, synonym dictionaries, structured filters — all shown to fail in Ch3; Ollama's local alternative was tried and later removed (ADR-010 — never run live, user asked to drop it) | Ch3; ADR-010 |
| Vector store | ChromaDB, local, persistent, HNSW/cosine | Local, free, zero-config, sufficient at this catalog scale | FAISS (no persistence/concurrency story), managed cloud vector DBs (premature cost/complexity before architecture is proven) | Ch4 |
| Chat model | OpenAI `gpt-4o-mini` | Smaller model + good evidence beats larger model + drift (book's own thesis) | Larger/fine-tuned models — explicitly ruled out in Ch1; Ollama's local alternative removed (ADR-010) | Ch1; Ch2; ADR-010 |
| API framework | FastAPI + Uvicorn | Async by default, Pydantic validation, auto-docs | Flask (synchronous, blocks on external calls), bare ngrok (not a framework) | Ch8 |
| Evaluation | RAGAS + HuggingFace `datasets` | Purpose-built RAG metrics, diagnostic by component | Single accuracy percentage (undebuggable per Ch9) | Ch9 |
| Local deploy | Docker Compose | Framework default hosting when no cloud access is available | Directly invoking Railway (no account access this session) | framework §0; ADR-003 |
| Cloud deploy (file only) | Railway `Procfile` | Matches book exactly, ready for the user to run themselves | — | Ch8; ADR-003 |
| Test framework | `pytest`, `pytest-cov` | Standard Python testing/coverage tooling; not specified by the book (which has no automated test suite of its own beyond the evaluation script) | — | ENGINEERING REQUIREMENT, framework §11 |

## Deliberately not adopted (named by the book as later-book work)
Qdrant Cloud, hybrid search/re-ranking libraries, conversation-memory stores, response caches — see `docs/book/unknowns.md` and `docs/book/concept-ledger.md`.
