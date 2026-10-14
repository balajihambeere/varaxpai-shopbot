# Implementation Plan

Vertical slice first (framework §7.1), then remaining MUST items, then SHOULD, then COULD. Tests and security are built inside each phase, not deferred.

## Phase 0 — Vertical slice: prove the Grounding Layer works end-to-end on a small subset
**Scope:** venv + dependencies (REQ-T-001), provider abstraction for Ollama only (REQ-T-002 partial), chunker (REQ-F-001 partial, 5 representative products), ingest, retriever with a provisional threshold, minimal prompt/chain, one script that asks 3 known questions and prints grounded answers — no API layer yet.
**Exit criterion:** running one script end-to-end produces a correct, evidence-grounded answer for at least one query and the exact fallback string for one deliberately unanswerable query, both confirmed by reading the printed output against the catalog (manual at this phase only — automated tests arrive Phase 1).

## Phase 1 — Full catalog, chunking, and retrieval (REQ-F-001, REQ-F-002, REQ-F-005, REQ-F-006, REQ-F-010, REQ-T-003)
Ingest all 50 products. Add metadata filtering. Empirically calibrate the similarity threshold against the real catalog (REQ-F-010) — do not reuse 0.75 unexamined. Unit + integration tests for chunker and retriever (real ChromaDB, not mocked).
**Exit criterion:** calibration evidence saved; retriever test suite passes; traceability updated for REQ-F-001/002/005/006/010.

## Phase 2 — Prompt, chain, and grounding guarantees (REQ-F-003, REQ-F-007, REQ-N-001, REQ-N-002)
Final system prompt (three-instruction structure: positive voice, exact fallback, no knowledge-gap-filling), temperature=0 enforced, `format_docs` labeling, threshold-adjacent type-mismatch deflection line. Fault-injection test: stub retriever to return `None`, assert fallback is byte-exact.
**Exit criterion:** fault-injection test passes; a weakened-prompt regression test demonstrates drift reappears without the constraint, proving the test actually detects the failure it claims to.

## Phase 3 — API layer (REQ-F-004, REQ-N-003, REQ-N-004, REQ-N-005, REQ-N-009, REQ-N-010)
FastAPI app, lifespan-built chain, Pydantic validation (empty/length/injection), `/health` with collection check (ADR-002), structured logging with request IDs, rate limiting. API tests (valid request, each malformed-input class, concurrent-request lifespan-singleton check).
**Exit criterion:** `pytest` API suite passes; manual `curl` smoke test against a running `uvicorn` process succeeds and is logged as evidence.

## Phase 4 — Evaluation (REQ-F-009)
Build the 20+-case labeled test set against the real catalog, plus three real-world failure cases as explicit regression tests. Run RAGAS (Faithfulness, Context Precision). Record baseline.
**Exit criterion:** evaluation run completes, scores and raw command output saved to `docs/evidence/`, interpreted honestly as this build's own baseline, not compared against any other numbers as if they were a pass/fail bar.

## Phase 5 — Frontend integration verification (REQ-T-006)
Run `zudyog-fashion` locally with `SHOPBOT_API_URL=http://localhost:8000`, exercise the chat widget end-to-end for a handful of real questions, confirm no contract changes were needed.
**Exit criterion:** screenshot/log evidence of at least one real round-trip through the actual UI.

## Phase 6 — Hardening, security, observability (REQ-N-006, REQ-N-008, REQ-N-011, threat model mitigations, security scan, dependency scan)
Dimension-mismatch guard, log-content review, coverage report against the 80% floor, `pip-audit` (or equivalent) dependency scan, secret scan.
**Exit criterion:** coverage and scan reports saved as evidence; any shortfall against the 80% floor stated explicitly, not hidden.

## Phase 7 — Containerization and deployment files (REQ-T-004, REQ-T-005)
Dockerfile + docker-compose.yml for local L2 run; Railway `Procfile` written (not executed, ADR-003).
**Exit criterion:** `docker compose up` serves `/health` as 200, evidence saved. Deployment level reached is reported honestly (L1/L2), not claimed as L3.

## Phase 8 — Documentation and final (GATE 2) review
README, architecture doc finalization, operations doc, API doc, traceability.md, known limitations. Independent skeptical re-read of traceability + evidence. Final report per framework §16.
**Exit criterion:** every MUST requirement in `docs/requirements.md` has a non-empty Code and Test column in `docs/traceability.md`, or is explicitly listed as a known gap in the final report — nothing silently missing.

## Commit discipline
One git commit per phase (framework §7.4), each with a message naming the phase and its exit criterion result.
