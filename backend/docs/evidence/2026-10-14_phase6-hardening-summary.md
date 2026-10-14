# Phase 6 — Hardening, security, observability

## REQ-N-006 — Dimension-mismatch guard
Already implemented in `src/retriever.py::retrieve()` (raises `RuntimeError` naming both the actual and expected dimension when a query embedding doesn't match `config.EXPECTED_EMBEDDING_DIM`). Already covered by `tests/test_retriever.py::test_embedding_dimension_mismatch_raises_loudly` — re-confirmed passing in this phase's full test run (see coverage evidence below). No new work needed; re-verified rather than re-built.

## REQ-N-008 — Log content review
Manual read of every `logger.*` call site in `src/api.py`: all five call sites (startup, ready, rate-limit, provider-error, answered) log only `request_id`, `route`, `status_code`, `latency_ms`, `provider`, and a boolean `evidence_found` — never the raw question or answer text. REQ-N-008 satisfied by the existing design; no code change required.

## REQ-N-011 — Coverage floor (80%)
```
$ pytest --cov=src.chunker --cov=src.retriever --cov=src.prompt --cov=src.api --cov-report=term-missing tests/
Name               Stmts   Miss  Cover   Missing
------------------------------------------------
src/api.py            69      3    96%   99, 163-164
src/chunker.py        23      0   100%
src/prompt.py         26      3    88%   71, 105-106
src/retriever.py      48      2    96%   101, 113
------------------------------------------------
TOTAL                166      8    95%
26 passed in 19.21s
```
All four core modules clear the 80% floor; no shortfall to report. Full output: `2026-10-14_phase6-coverage.txt`.

## Dependency vulnerability scan (`pip-audit`)
Ran against the live venv (not a fresh resolve of `requirements.txt`, which fails — ADR-008's `--no-deps` pin for `langchain-community` is intentional and not pip-resolvable from the lockfile alone). Full output: `2026-10-14_phase6-pip-audit.txt`.

Findings and disposition, stated honestly rather than silently patched or silently ignored:

| Package | Installed | Finding | Action | Reasoning |
|---|---|---|---|---|
| `langchain-openai` | 1.1.9 | PYSEC-2026-76, fix in 1.1.14 | **Fixed** — bumped to 1.1.14 in `requirements.txt`, re-ran full test suite (26 passed) and a live backend smoke test (`/health`, `/ask` against a known grounded query) after restarting `uvicorn` to load the new version | Patch-level bump on a direct runtime dependency, verified safe |
| `chromadb` | 1.5.9 | 4 CVEs (PYSEC-2026-311/3813/3814/3815) | **Accepted risk, not fixed** | 1.5.9 is already the latest published release (`pip index versions chromadb`) — no fix version exists yet to upgrade to |
| `diskcache` | 5.6.3 | PYSEC-2026-2447 | **Accepted risk, not fixed** | 5.6.3 is already the latest published release — no fix version exists yet |
| `ragas` | 0.2.15 | PYSEC-2026-3046/3047, fix in 0.3.0rc1 | **Accepted risk, not fixed** | (a) fix is only a release candidate, not a stable release; (b) `ragas` is an evaluation-time dependency (Phase 4) only — it is never imported by the running API (`src/api.py`, `src/retriever.py`, `src/prompt.py`) and ships no attack surface in production; (c) ADR-008/009 already document that this exact pin was hard-won (`langchain-community==0.3.27 --no-deps` compatibility, dataset column-name shim) — bumping it blind risks re-breaking evaluation for a vulnerability that doesn't reach the served app |

Pre-existing, unrelated finding surfaced incidentally while installing the `langchain-openai` patch: `requirements.txt` pins `openai==1.109.1`, but the actual installed venv has drifted to `openai==2.54.0` (pip warns of an `instructor` incompatibility, `instructor==1.3.2` wants `openai<2.0.0`). This predates this session's change — not something the `langchain-openai` bump caused — and is left as a known gap for a future requirements-file audit rather than fixed opportunistically mid-scan.

## Secret scan (`gitleaks`)
Installed via Homebrew (not previously present). Two scans run:
1. **Git history** (`gitleaks detect --source .`) — 4 commits scanned, **no leaks found**. See `2026-10-14_phase6-gitleaks-history.txt`.
2. **Working tree filesystem** (`gitleaks detect --source . --no-git`) — found one real OpenAI API key in `.env` (line 10, rule `openai-api-key`). Verified `.env` is listed in `.gitignore`, is untracked (`git ls-files` confirms), and has zero presence in git history (`git log --all -- .env` returns nothing) — the key has never left the local filesystem. **This output is intentionally not saved as evidence** (it contains the live key); only the clean git-history scan is kept as a file.

## Incidental finding: fault-injection test flake rate
While re-running the suite in this phase, `tests/test_prompt.py::test_adversarial_prompt_reintroduces_drift_strict_prompt_does_not` failed twice out of six runs (full-suite and isolated, no test-order dependency — ruled out by re-running with it deselected, which left the other 25 green). The test's own in-code comment already documents this as expected: a live LLM call under temperature=0 is "only *mostly* deterministic," and 3 sampled trials is called "the deterministic-enough compromise," not a guarantee. This is not a regression from the `langchain-openai` bump above — observed failure/pass mix predates and is independent of that change. Noted here rather than silently re-run until green, per the project's evidence-honesty standard; no action taken, as Ch9/REQ-F-009's own argument (RAGAS over ad hoc keyword checks for exactly this reason) already covers the gap this test's instability points at.

## Exit criterion
Coverage and scan reports saved as evidence (this file + the two referenced `.txt` files). The one real, fixable finding (`langchain-openai`) was fixed and reverified live. The three unfixable/out-of-scope findings (`chromadb`, `diskcache`, `ragas`) are stated explicitly above, not hidden, per framework §11/§16 honesty requirement.
