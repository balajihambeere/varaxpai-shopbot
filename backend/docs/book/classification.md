# Book Classification

**Classification: Implementable system book.**

## Justification
The book has a clear, consistent, incrementally-built architecture with concrete code for every component:
- Explicit algorithms (cosine similarity formula, HNSW-backed ANN retrieval, threshold-gated retrieval)
- Explicit APIs (`retrieve()`, `answer()`, FastAPI `/ask` and `/health` with Pydantic schemas)
- Explicit data model (`product_to_chunks()` → identity/variants/policy/care/faq chunks, with metadata schema)
- A working, runnable reference implementation for every chapter, with actual output transcripts
- A named evaluation method (RAGAS, two dimensions) with a reported baseline
- A named deployment path (ngrok → Railway) with the actual commands

This is not a framework/principles book dressed up with anecdotes — the Arjun/Krishna/Meera narrative frames *why* each engineering decision was made, but every decision resolves to runnable code the book itself shows executing with real output.

## Scope boundary (what "the book" means for this build)
Only Book 1 (preface + 10 chapters) is in scope. The book repeatedly references "Book 2" (Qdrant Cloud migration, hybrid search, re-ranking, Answer Relevance/Context Recall RAGAS dimensions, conversation memory, caching) and "Book 3" (corrective retrieval) as explicitly future work. Those are out of scope for this build and are not to be invented — see `unknowns.md` and the concept ledger's "out of scope" section.

## Consequence for the rest of this design
Because this is an implementable system book, framework §3's fallback ("too little technical detail — stop and tell me") does not apply. Proceeding to full requirements/design/implementation is appropriate.
