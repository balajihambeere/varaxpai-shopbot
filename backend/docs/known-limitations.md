# Known Limitations and Unknowns

Honest list, per framework §13. Full unknowns table with reasoning: `docs/book/unknowns.md`. Full defect list from the Phase 8 skeptical review: `docs/evidence/2026-10-14_phase8-gate2-review.md`.

## Open gaps (things that should work but aren't fully verified)

- **`pip install -r requirements.txt` does not succeed as a single command.** `ragas` transitively pulls a `langchain-community` version incompatible with this project's `langchain-core` line (ADR-008). The real, working install path is the two-step sequence documented in `README.md` and encoded in the `Dockerfile`. Anyone following only the README's single `pip install -r requirements.txt` line without reading further would hit `ResolutionImpossible`.
- **Railway deployment unexecuted.** `Procfile` content matches the book's exact start command, but no Railway account was available during this build. Deployment level actually reached and verified is **L2** (local Docker Compose), not L3.
- **Visual browser click-through of the chat widget not captured.** The round-trip through the frontend's `/api/chat` → backend `/ask` is verified via curl and backend request logs (fallback and grounded response shapes both confirmed), but no screenshot of the actual rendered chat widget exists — the Claude-in-Chrome browser extension wasn't connected during that session. The user explicitly accepted log-based evidence over blocking to connect it.

## Accepted, documented limitations (not defects — named by the book or accepted as out of scope)

- **No free/local provider alternative.** The book offers Ollama as a zero-cost local path (Ch2 "Free Alternative"); this build removed it entirely (ADR-010) after finding it had never been run live end-to-end, only import-checked. This build now has a hard dependency on a funded OpenAI account, with no fallback.
- **Multi-intent queries** ("festive AND warm clothing") are answered from the single best-matching chunk with no explicit multi-query retrieval — this is the book's own named Book 2 scope (C-025), not something this build attempts to fix.
- **Occasion-vocabulary fix doesn't fully reproduce at this catalog's scale.** The book's Ch10 "function" vocabulary fix is present in the data, but a bare query like "What's good for a function?" doesn't clear this build's calibrated threshold against the real 50-product catalog — a genuine, measured gap versus the book's narrative at a smaller catalog size, documented rather than silently patched (`docs/evidence/2026-10-14_phase4-function-query-finding.md`).
- **Dependency vulnerabilities accepted, not patched:** `chromadb` and `diskcache` have no fixed version published yet (both already on the latest release); `ragas`'s fix is only a release candidate for a dependency that's eval-only and never imported by the served API. See `docs/evidence/2026-10-14_phase6-hardening-summary.md`.
- **One test is intermittently flaky by design.** `tests/test_prompt.py::test_adversarial_prompt_reintroduces_drift_strict_prompt_does_not` samples a live LLM 3 times per prompt variant; the test's own comment documents that even 3 samples isn't a determinism guarantee. Observed failing in roughly 1/3 of runs during Phase 6 — not a regression, a known property of testing stochastic model output.
- **RAGAS scores are not directly comparable to the book's own numbers.** This build's Faithfulness (0.645) and Context Precision (0.933) baselines are measured against a different (larger, real) catalog than the book's demo set — presented as this build's own baseline, not as reproducing or falling short of the book's reported 0.71/0.82.
- **No conversation memory.** `session_id` is accepted and echoed back but not used to retain any state between requests — each `/ask` call is independent, matching the book's own scope (conversation memory is named future work).
- **Test-set authorship is solely the implementer's**, which the book itself (Ch9) flags as a form of selection bias ("a test set written by the developer is a demonstration, not a test set"). This is a process limitation of a solo-session build, not something automatable away.

## Assumptions made explicit
- Chat question/answer content is treated as sensitive by default and not logged in full (no stated zUdyog privacy/retention policy exists beyond what's in `data/products.py`, since the book is a RAG architecture book, not a privacy-engineering one).
- No real customer PII, accounts, or payment data are collected by any MUST-scope endpoint in this build.
