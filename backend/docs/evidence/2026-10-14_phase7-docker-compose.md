# Phase 7 — Containerization and deployment files (REQ-T-004, REQ-T-005)

`Dockerfile`/`docker-compose.yml`/`Procfile`/`.dockerignore` existed in the working tree uncommitted from an earlier session (written during a tool outage, never built or run — flagged `NOT-VERIFIED` in `docs/traceability.md`). This phase actually builds and runs the stack rather than trusting that earlier draft, and two real bugs surfaced in the process.

## Tooling
```
$ docker --version
Docker version 28.5.1, build e180ab8
$ docker compose version
Docker Compose version v2.40.2-desktop.1
```
Docker Desktop was not running at the start of this phase; started via `open -a Docker` and polled until `docker info` succeeded (~2s).

## Bug 1 — Dockerfile's single-pass `pip install -r requirements.txt` is ResolutionImpossible
Verified independently in a clean host venv before touching the Dockerfile (not assumed from the Docker build logs alone):
```
$ python3 -m venv /tmp/fresh-test-venv && source /tmp/fresh-test-venv/bin/activate
$ pip install -r requirements.txt
...
ERROR: Cannot install ... langchain-core==1.6.10 because these package versions have
conflicting dependencies.
The conflict is caused by:
    langchain-community 0.3.27 depends on langchain-core<1.0.0 and >=0.3.66
ERROR: ResolutionImpossible
```
This is exactly the conflict `pip-audit -r requirements.txt` hit in Phase 6 — ADR-008's fix (`pip install --no-deps langchain-community==0.3.27` as a second pass, after everything else) was applied by hand to the existing dev venv at the time, but was never encoded into the Dockerfile, so a genuinely clean build (anyone else's `docker compose up`, or this image rebuilt from scratch) would have failed the same way.

**Fix** (`Dockerfile`): replaced the single `pip install -r requirements.txt` with the two-step sequence ADR-008 describes — install everything except the `langchain-community==` line, then reinstall just that line with `--no-deps`. Re-verified in a second clean venv (`/tmp/fresh-test-venv3`) before editing the Dockerfile:
```
$ grep -v '^langchain-community==' requirements.txt > /tmp/requirements-no-lc.txt
$ pip install -r /tmp/requirements-no-lc.txt   # succeeds, pulls langchain-community 0.4.2 transitively
$ pip install --no-deps langchain-community==0.3.27   # overwrites with the pinned 0.3.x
$ python -c "import ragas; from src import api"   # both succeed
```

## Bug 2 — pre-existing `requirements.txt`/venv drift, surfaced by this exact fix
While testing Bug 1's fix, the *same* clean-venv install additionally failed on:
```
ERROR: Cannot install ... openai==1.109.1 and langchain-openai==1.1.14 because...
instructor 1.3.2 depends on openai<2.0.0
langchain-openai 1.1.14 depends on openai>=2.26.0
```
This is the drift Phase 6 flagged as "pre-existing, left as a known gap" — but it turned out to be load-bearing: `requirements.txt` still pinned `openai==1.109.1`, inconsistent with the `langchain-openai==1.1.14` bump Phase 6 made (which needs `openai>=2.26.0`). The local dev venv didn't surface this because it already had `openai==2.54.0` installed from before the bump (never reconciled against the lockfile) — the Docker build, starting from a truly clean image, would have hit it immediately.

**Fix**: confirmed `instructor` is never imported anywhere in this codebase (`grep -rn "import instructor" src/ tests/ scripts/ evaluation/` — no matches) and has no reverse dependency (`pip show instructor` → `Required-by:` empty) — a genuine orphan, not something ragas or anything else needs. Removed `instructor==1.3.2` from `requirements.txt` and uninstalled it from the dev venv; updated the `openai` pin from `1.109.1` to `2.54.0` to match what `langchain-openai==1.1.14` actually requires and what was already running. Re-ran the full test suite after both changes: `26 passed`.

## Bug 3 — ingestion chicken-and-egg with `docker compose exec`
Phase 6's traceability note (carried over from the earlier uncommitted draft) said to run `docker compose exec shopbot-api python -m src.ingest` once the volume is mounted. This does not work: the named volume starts empty, `src/retriever.py`'s `warmup()` calls `get_collection()` (not `get_or_create_collection()`) and raises `chromadb.errors.NotFoundError` when the collection doesn't exist yet, which crashes the FastAPI lifespan hook and the container immediately exits/restart-loops — there is never a running container to `exec` into.

**Fix (operational, no code change)**: use `docker compose run --rm shopbot-api python -m src.ingest` instead — this starts a fresh one-off container against the same named volume without depending on the long-running service already being up. Confirmed:
```
$ docker compose run --rm shopbot-api python -m src.ingest
Products: 50  ->  Chunks: 255
Ingested 255 chunks into ChromaDB (provider=openai, dim=1536).
```
followed by `docker compose restart shopbot-api` to clear the original container's restart-loop backoff. `docs/traceability.md`'s REQ-T-004 row corrected to say `run --rm`, not `exec`.

## Final verification
```
$ docker compose ps
NAME                    STATUS                   PORTS
shopbot-shopbot-api-1   Up 5 seconds (healthy)   0.0.0.0:8000->8000/tcp

$ curl -s http://localhost:8000/health
{"status":"ok","degraded":false,"service":"ShopBot","version":"1.0.0","provider":"openai","document_count":255}

$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/health
200

$ curl -s -X POST http://localhost:8000/ask -H "Content-Type: application/json" \
    -d '{"question":"Does the Printed Silk Saree need dry cleaning?"}'
{"answer":"Yes, the Printed Silk Saree requires dry cleaning only. ... zari border ...",
 "session_id":"default"}
```
Answer text is byte-identical to the venv-based runs in Phase 1/5 evidence — the container serves the same grounded answer as the bare-metal process.

## REQ-T-005 — Railway Procfile
`Procfile` content (`web: uvicorn src.api:app --host 0.0.0.0 --port $PORT`) re-confirmed matching the book exactly. Not executed — no Railway account access this session (ADR-003, unchanged). Deployment level reached: **L2 (local Docker Compose)**, not L3 (actual cloud deploy) — reported honestly, not claimed as more than it is.

## Exit criterion
`docker compose up` serves `/health` as 200 — **met**, after fixing the two real build-time bugs above (not assumed from the pre-written, never-run files). Evidence: this file + `2026-10-14_phase7-container-logs.txt`.
