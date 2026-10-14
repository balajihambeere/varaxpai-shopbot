# Traceability Table

An empty Code or Test column means the concept is not done. This table is updated at the end of every implementation phase (framework §7.4) — not retroactively batch-filled at the end.

| Concept ID | Requirement ID | Component | Code location | Test ID | Status | Evidence |
|---|---|---|---|---|---|---|
| C-008,C-009,C-010,C-011 | REQ-F-001 | Ingestion | `src/chunker.py`, `src/ingest.py` | smoke_test | VERIFIED | 50 products → 255 chunks, OpenAI embed, `docs/evidence/2026-10-14_phase0-smoke-test.txt` |
| C-005,C-006,C-012,C-013,C-014 | REQ-F-002 | Retriever | `src/retriever.py` | tests/test_retriever.py (5 tests) | VERIFIED | recalibrated threshold 0.62; `docs/evidence/2026-10-14_phase1-pytest.txt` |
| C-002,C-015,C-016,C-017 | REQ-F-003 | Prompt/Chain | `src/prompt.py` | tests/test_prompt.py (5 tests) | VERIFIED | fault-injection proves grounding constraint does real work; `docs/evidence/2026-10-14_fault-injection-prompt.md`, `2026-10-14_phase2-pytest.txt` |
| C-018,C-019,C-020 | REQ-F-004 | API | | | NOT-STARTED | |
| C-009 | REQ-F-005 | Retriever (metadata filter) | `src/retriever.py` (`$and` where, ADR-007) | tests/test_retriever.py::test_product_id_filter_isolates_one_products_policy_chunk | VERIFIED | 6 products share identical return-policy text; filter isolates correctly |
| C-024 | REQ-F-006 | Data (products.py, already applied) | `data/products.py` (copied verbatim) | — | VERIFIED-BY-INSPECTION | "function" present in occasion field for festive products (manual grep); no dedicated regression test yet — add in Phase 4 evaluation set |
| C-026 | REQ-F-007 | Prompt | `src/prompt.py` (SHOPBOT_SYSTEM) | tests/test_prompt.py::test_type_mismatch_deflects_to_support_real_llm | VERIFIED | works; general constraint found to be independently sufficient for current gpt-4o-mini, see evidence Finding 1 |
| C-025 | REQ-F-008 | Prompt (documented limitation) | n/a — intentionally not built | n/a | DOCUMENTED-LIMITATION | COULD priority, matches book's own Ch10 scope decision |
| C-022,C-023 | REQ-F-009 | Evaluation | | | NOT-STARTED | |
| C-013 (U-01) | REQ-F-010 | Evaluation / calibration | `scripts/calibrate_threshold.py` | 24-query manual run (12 correct / 12 no-answer) | VERIFIED | threshold 0.62, clean gap [0.6107,0.6205]; `docs/evidence/2026-10-14_threshold-calibration.txt` |
| C-002,C-004 | REQ-N-001 | Retriever+Prompt | `src/prompt.py`, `src/retriever.py` | tests/test_prompt.py::test_no_evidence_returns_exact_fallback_string | VERIFIED | LLM provably never called when evidence is None (monkeypatch asserts) |
| C-016 | REQ-N-002 | Chain config | `src/providers.py` | tests/test_prompt.py::test_chat_model_is_deterministic | VERIFIED | temperature hardcoded to 0, not request-configurable |
| — | REQ-N-003 | Repo hygiene | `.gitignore`, `.env.example` | | DONE | this file's own existence + absence of `.env` in repo |
| C-019 | REQ-N-004 | API validators | | | NOT-STARTED | |
| C-020 | REQ-N-005 | API lifespan | | | NOT-STARTED | |
| C-012 | REQ-N-006 | Provider abstraction | | | NOT-STARTED | |
| — | REQ-N-007 | Config defaults | `.env.example` (`LLM_PROVIDER=ollama`) | | DONE | file content |
| — | REQ-N-008 | Logging | | | NOT-STARTED | |
| — | REQ-N-009 | Observability | | | NOT-STARTED | |
| — | REQ-N-010 | API rate limit | | | NOT-STARTED | |
| — | REQ-N-011 | Test coverage | | | NOT-STARTED | |
| — | REQ-T-001 | Dependencies | | | NOT-STARTED | |
| — | REQ-T-002 | Provider abstraction | | | NOT-STARTED | |
| C-008 | REQ-T-003 | Vector store setup | `src/ingest.py` | smoke_test (collection metadata check) | VERIFIED | `hnsw:space=cosine`; 255 chunks from 50 products |
| — | REQ-T-004 | Docker Compose | | | NOT-STARTED | |
| C-021 | REQ-T-005 | Railway Procfile | | | NOT-STARTED | |
| — | REQ-T-006 | Frontend integration | `zudyog-fashion/app/api/chat/route.ts` (pre-existing, confirmed compatible) | | VERIFIED-BY-INSPECTION — not yet run end-to-end | see `docs/book/unknowns.md` U-07 |
| — | REQ-T-007 | Test suite | | | NOT-STARTED | |

Status vocabulary matches framework §1.3: `NOT-STARTED`, `PARTIAL`, `VERIFIED-BY-INSPECTION` (code read, not executed), `VERIFIED`, `PARTIALLY-VERIFIED`, `NOT-VERIFIED`, `DONE` (used here only for pure-documentation/config items with no runtime behavior to verify).
