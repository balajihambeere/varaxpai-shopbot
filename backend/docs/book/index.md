# Book Index — "Book 1" (untitled series, Pramana Framework)

Source files: `/Applications/zuxpert/Book-1/book1_preface.md`, `book1_chapter_1..10_*.md`.
All chapters read in full on 2026-10-14. No unread parts.

| # | File | Title | Builds |
|---|---|---|---|
| — | book1_preface.md | Preface | Names "Confident Drift," "Grounding Layer," "Pramana Framework"; states the book builds ShopBot for zUdyog Fashion |
| 1 | book1_chapter_1_problem_with_brilliant_liars.md | The Problem With Brilliant Liars | Diagnoses Confident Drift; rules out prompt-only, full-catalog-in-context, and fine-tuning fixes; introduces the Grounding Layer concept |
| 2 | book1_chapter_2_before_the_first_line.md | Before the First Line of Code | Project structure, venv, .gitignore, dependencies (langchain, langchain-openai, chromadb, fastapi, uvicorn, python-dotenv), API key hygiene, `test_setup.py`, Ollama local alternative |
| 3 | book1_chapter_3_what_1536_numbers_actually_mean.md | What 1536 Numbers Actually Mean | Why keyword search fails; embeddings as semantic coordinates; cosine similarity; `text-embedding-3-small` (1536-dim) vs `nomic-embed-text` (768-dim) |
| 4 | book1_chapter_4_the_memory_that_thinks.md | The Memory That Thinks | Why a loop/regular DB doesn't scale; ANN search; ChromaDB (HNSW, cosine); ingestion; metadata for pre-filtering |
| 5 | book1_chapter_5_cut_it_right.md | Cut It Right | The "blob problem" and "too-small" failure; chunking by concern (identity/variants/policy/care/faq); `product_to_chunks()`; "One chunk. One question. One clear answer." |
| 6 | book1_chapter_6_the_right_answer_is_already_there.md | The Right Answer Is Already There | Similarity threshold calibration (0.75); retriever as abstraction (`retrieve(query)`); metadata filtering to avoid competing chunks; k=3 default |
| 7 | book1_chapter_7_the_prompt_is_the_product.md | The Prompt Is the Product | Three prompt drafts (unconstrained → over-constrained → final); temperature=0 justification; `format_docs` chunk labeling; prompt as policy document |
| 8 | book1_chapter_8_give_it_a_door.md | Give It a Door | FastAPI vs Flask/ngrok; input validation (empty/long/injection); lifespan pattern (build chain once); `/health`, `/ask`; ngrok for demo, Railway for deploy |
| 9 | book1_chapter_9_four_questions_is_not_a_test.md | Four Questions Is Not a Test | Selection bias in manual testing; RAGAS framework; Faithfulness + Context Precision (Book 1 scope); 20-case labeled test set; baseline scores 0.71 / 0.82 |
| 10 | book1_chapter_10_ship_it.md | Ship It | Real beta-user failures (vocabulary gap "function", multi-intent query, threshold-adjacent type-mismatch) and their fixes; final architecture recap; cost recap (₹7.60) |

## Reading status
All 10 chapters + preface: READ in full. `BOOK READ (all chapters)` = complete, no unread parts.
