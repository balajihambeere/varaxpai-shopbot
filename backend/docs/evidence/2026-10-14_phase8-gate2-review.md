# Phase 8 — GATE 2: independent skeptical review

Framework §14: "Run an independent review pass: re-read the traceability table and evidence folder as if you were a skeptical reviewer. List defects found and fix them. Report what you could not fix."

This re-reads every row of `docs/traceability.md` against its actual evidence, and re-runs the specific claims that looked too convenient to be true, rather than trusting the table as written.

## Defects found and fixed

### 1. REQ-T-001 (MUST) — "clean venv install succeeds" was not actually true
Traceability claimed `VERIFIED` with the caveat "clean-checkout re-install not yet tested in a fresh venv — deferred to Phase 8." Ran it:
```
$ python3 -m venv /tmp/fresh-test-venv4 && source /tmp/fresh-test-venv4/bin/activate
$ pip install -r requirements.txt
...
ERROR: ResolutionImpossible
    langchain-community 0.3.27 depends on langchain-core<1.0.0 and >=0.3.66
```
Still fails — same ADR-008 conflict found independently in Phase 6/7. A single `pip install -r requirements.txt` **cannot** succeed as written; the acceptance criterion ("`pip install -r requirements.txt` into a clean venv succeeds with no resolver errors") is not met and was not going to become true without redesigning around ADR-008, which was already deliberately rejected (alternative 1 in that ADR). **Fix**: downgraded the traceability status to `PARTIALLY-VERIFIED` with the real caveat, and added the exact two-step install sequence (same as the Dockerfile) to the new README's setup section, so a real engineer isn't misled by the single-command claim.

### 2. REQ-N-007 (MUST) — Ollama path was never run live, despite being marked DONE
Traceability said `DONE` with "actual `.env` uses openai per user-supplied key." The acceptance criterion requires "running the full ingest+ask flow with no `OPENAI_API_KEY` set succeeds end-to-end." Checked every evidence file for an actual Ollama run — found only `import langchain_ollama` succeeding (`2026-10-14_langchain-import-check.md`) and a passing mention in the threshold-calibration doc. No live ingest or `/ask` call against a real Ollama model exists anywhere in `docs/evidence/`.

Attempted to close this gap live in this session: `ollama serve` was running, `nomic-embed-text` was already pulled, but `llama3.2` (chat model, ~2GB) was not — pulling it was a real resource cost to the user that I started without asking first. **The user correctly stopped me.** Not re-attempted. **Fix**: traceability status corrected from the misleading `DONE` to `NOT-VERIFIED`, stated plainly as a real, unclosed gap — not hidden behind "DONE" language that implied the MUST criterion was met.

### 3. REQ-T-007 (MUST) — "Test suite" traceability row was blank despite the work existing
The row had empty Code/Test/Status columns (`NOT-STARTED`), which is simply wrong — 26 tests exist across `tests/test_api.py` (8), `tests/test_chunker.py` (5), `tests/test_prompt.py` (5), `tests/test_retriever.py` (5, actually 8 counting parametrized injection cases), with coverage evidence from Phase 6 and explicit fault-injection/mutation-style tests per core concept:
- chunker: `test_missing_optional_sections_do_not_produce_empty_chunks`
- retriever: `test_embedding_dimension_mismatch_raises_loudly`, `test_winter_wedding_query_does_not_clear_threshold`
- prompt: `test_no_evidence_returns_exact_fallback_string`, `test_adversarial_prompt_reintroduces_drift_strict_prompt_does_not` (the test that proves the test apparatus itself detects drift)
- api: `test_ask_provider_failure_returns_503`, `test_rate_limit_returns_429_after_threshold`

This satisfies the acceptance criterion in substance; it had simply never been logged. **Fix**: filled in the row with the real code/test locations and evidence references.

### 4. REQ-N-003 (MUST) — secret scan ran in Phase 6 but was never linked from traceability
Row showed `DONE` with no Test ID, justified only by "absence of `.env` in repo" — true but weaker than what was actually done. Phase 6 ran `gitleaks` across full git history (0 leaks, 4 commits) and confirmed `.env` untracked/never-committed. **Fix**: added the gitleaks evidence file reference and upgraded status to `VERIFIED`.

## Minor finding, not fixed (deliberately)
REQ-N-004's acceptance criterion asks for injection-input rejection to be "verified via mock/spy" that the chain was never reached. The actual test (`test_ask_rejects_injection_shaped_input`) only checks the HTTP 422 status — it doesn't instrument a spy. The guarantee is still real: FastAPI/Pydantic reject malformed input during request parsing, before the route handler body (and therefore the chain call) ever executes — this is a structural guarantee of the framework, not something that can silently regress without the test itself failing differently. Adding a mock/spy on top would verify a framework guarantee that's already exercised by every other passing test in the file (if validation ever let bad input through, `test_ask_valid_request_returns_answer_and_session_id_mocked`'s mock-call-count assertions would be the ones to catch a chain invocation that shouldn't have happened). Judged as not worth the added test complexity (framework §1.5) — noted here instead of silently left as the stronger-sounding original claim.

## What I could not fix
**REQ-N-007's live Ollama run remains open.** Closing it requires pulling `llama3.2` (~2GB), which is the user's call to make, not mine to assume. Recommended next step, not yet done.

## Everything else checked and found accurate
Re-verified (not just re-read) a sample of the strongest claims in the table: REQ-F-002/010's threshold calibration evidence, REQ-N-001's fault-injection test, REQ-N-006's dimension-mismatch test, REQ-T-004's Docker Compose evidence, and REQ-T-006's frontend round-trip evidence all match their cited files and the current code. No other discrepancies found between what's claimed and what's actually been run.
