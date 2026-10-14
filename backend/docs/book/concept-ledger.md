# Concept Ledger

Status values: `TO-BUILD` (MUST implement), `TO-BUILD-SHOULD`, `ENCODE-AS-LIMITATION` (book itself treats as unresolved/deferred to a later book), `TERMINOLOGY-ONLY` (no standalone code artifact).

| ID | One-line definition | Source | Status |
|---|---|---|---|
| C-001 | Confident Drift — fluent, confident, wrong output from a model lacking grounded facts | Preface; Ch1 | TERMINOLOGY-ONLY (diagnostic concept; prevented by C-002/C-012/C-015) |
| C-002 | Grounding Layer — mandatory retrieval step between question and answer | Preface; Ch1 | TO-BUILD (the whole system) |
| C-003 | Pramana Framework — philosophical name for the architecture | Preface; Ch1 | TERMINOLOGY-ONLY |
| C-004 | Grounding Failure — retrieval returns nothing/wrong, drift resumes | Preface; Ch4; Ch6 | TO-BUILD (prevented by threshold + fallback) |
| C-005 | Embedding — text → 1536/768-dim semantic coordinate | Ch3 | TO-BUILD |
| C-006 | Cosine similarity scoring | Ch3 | TO-BUILD |
| C-007 | ANN (Approximate Nearest Neighbour) search | Ch4 | TO-BUILD (via ChromaDB/HNSW, not hand-rolled) |
| C-008 | ChromaDB persistent vector collection | Ch4 | TO-BUILD |
| C-009 | Metadata storage for pre-filter + display | Ch4; Ch6 | TO-BUILD |
| C-010 | Chunking-by-concern / "blob problem" avoidance | Ch5 | TO-BUILD |
| C-011 | Chunk types: identity, variants, policy, care, faq | Ch5 | TO-BUILD |
| C-012 | Retriever abstraction `retrieve(query, chunk_type, product_id)` | Ch6 | TO-BUILD |
| C-013 | Similarity threshold calibration methodology | Ch6 | TO-BUILD (value re-derived empirically for this build's 50-product catalog, not copied from book) |
| C-014 | k (max retrieved chunks) tuning, default 3 | Ch6 | TO-BUILD |
| C-015 | System prompt as grounding/policy enforcement | Ch7 | TO-BUILD |
| C-016 | Temperature = 0 determinism requirement | Ch7 | TO-BUILD |
| C-017 | `format_docs` chunk-type labeling in context | Ch7 | TO-BUILD |
| C-018 | FastAPI async API layer | Ch8 | TO-BUILD |
| C-019 | Input validation (empty/long/injection/normalize) | Ch8 | TO-BUILD |
| C-020 | Lifespan pattern — build chain once at startup | Ch8 | TO-BUILD |
| C-021 | Deployment ladder: local → ngrok(dev) → Railway(prod) | Ch8 | TO-BUILD-SHOULD (Railway deploy itself NOT-VERIFIED this session, see ADR-003) |
| C-022 | RAGAS evaluation — Faithfulness + Context Precision | Ch9 | TO-BUILD |
| C-023 | Labeled test-set discipline (write before scoring; include deliberate fallback cases) | Ch9 | TO-BUILD |
| C-024 | Vocabulary-gap fix via occasion-metadata synonyms ("function") | Ch10 | TO-BUILD (already present in `data/products.py`) |
| C-025 | Multi-intent query limitation (single-vector query can't represent "AND" of two concepts) | Ch10 | ENCODE-AS-LIMITATION (book defers systematic fix to Book 2; this build matches book's own caveat-in-answer approach, COULD not MUST) |
| C-026 | Threshold-adjacent type-mismatch fix via one prompt line | Ch10 | TO-BUILD |

## Explicitly out of scope (named by the book as later-book work)
Hybrid search, re-ranking, Qdrant Cloud migration, Answer Relevance / Context Recall RAGAS dimensions, multi-query retrieval, corrective retrieval, conversation memory, response caching. Tagged `UNKNOWN / NOT SPECIFIED IN BOOK` for Book 1 and excluded from this build's MUST/SHOULD requirements.
