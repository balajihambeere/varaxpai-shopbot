# Operations

## Deploying

**Local (bare metal):**
```bash
source venv/bin/activate
python -m src.ingest            # once, or whenever data/products.py or LLM_PROVIDER changes
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

**Docker Compose (L2 — the furthest level actually run and verified in this build):**
```bash
docker compose up --build -d
docker compose run --rm shopbot-api python -m src.ingest   # first run only — named volume starts empty
docker compose restart shopbot-api                          # the service container crash-loops until ingest completes; this clears its restart backoff
```
See `docs/evidence/2026-10-14_phase7-docker-compose.md` for why the ingest step must use `run --rm`, not `exec` (the container can't stay up long enough to `exec` into before the collection exists).

**Railway (L3 — written, never deployed):** `Procfile` content uses the standard start command (`web: uvicorn src.api:app --host 0.0.0.0 --port $PORT`), but no Railway account was available during this build. Treat as untested until someone actually deploys and checks `/health`.

## Monitoring

- **Liveness/readiness:** `GET /health`. A 200 with `"degraded": false` means the collection is populated and queryable. A 200 with `"degraded": true` means the process is up but has nothing to retrieve from — see Troubleshooting below.
- **Docker health check:** the image's `HEALTHCHECK` curls `/health` every 30s; `docker compose ps` shows `(healthy)`/`(unhealthy)` directly.
- **Structured logs:** every `/ask` call emits a JSON log line with `request_id`, `route`, `status_code`, `latency_ms`, `provider`, and `evidence_found` (boolean — whether retrieval found anything above threshold). Raw question/answer text is **not** logged (REQ-N-008) — if you need to debug a specific bad answer, reproduce it interactively with `curl`, don't look for it in the logs.

## Logs

- **Bare metal:** stdout of the `uvicorn` process (redirect to a file if backgrounding, e.g. `> shopbot.log 2>&1`).
- **Docker:** `docker compose logs shopbot-api` (add `-f` to follow, `--tail=N` to limit).

Example log line:
```json
{"ts": "2026-10-14T13:06:45", "level": "INFO", "logger": "shopbot", "message": "Answered /ask", "request_id": "ccf8a6c2-...", "route": "/ask", "latency_ms": 4798.7, "status_code": 200, "provider": "openai", "evidence_found": true}
```

## Common failures and recovery

| Symptom | Cause | Fix |
|---|---|---|
| `/health` returns `"degraded": true, "reason": "collection is empty"` | Ingest never ran, or ran against a different `CHROMA_DB_PATH`/volume | Bare metal: `python -m src.ingest`. Docker: `docker compose run --rm shopbot-api python -m src.ingest`, then `docker compose restart shopbot-api`. |
| Docker container stuck "Restarting" in `docker compose ps`, never reaches healthy | Lifespan's `warmup()` crashes hard on a missing collection (`get_collection()`, not `get_or_create_collection()`) — this is before the collection has ever been created | Same fix as above. Don't try `docker compose exec` — there's never a running container to exec into before ingest completes. |
| `/ask` returns 503 "language model provider is temporarily unavailable" | OpenAI API error — expired/invalid key, network issue, or provider outage | Check `OPENAI_API_KEY` validity and account status. |
| `pip install -r requirements.txt` fails with `ResolutionImpossible` mentioning `langchain-community` | `ragas` transitively pulls the latest `langchain-community`, incompatible with this project's `langchain-core` 1.x line (ADR-008) | Use the two-step install in `README.md` — install everything except the `langchain-community==` line, then reinstall just that line with `--no-deps`. |
| `RuntimeError: ... dimensions, expected 1536 ...` on any query | Collection was built with a different embedding model than the one currently configured (e.g. after manually changing `OPENAI_EMBEDDING_MODEL`) | Re-ingest: delete `chroma_db/` (or the Docker volume) and run `python -m src.ingest` again. This is REQ-N-006's loud-failure guarantee working as intended — never silently serve wrong-dimension results. |
| `/ask` answers seem to be guessing rather than grounded | Should not happen by design — `src/prompt.py` never calls the model when retrieval returns `None` | If you see this, it's a real bug, not a tuning issue. Check `evidence_found` in the log for that request; file it against `tests/test_prompt.py::test_no_evidence_returns_exact_fallback_string`, which exists specifically to catch this class of regression. |
| 429 "Rate limit exceeded" | More than `RATE_LIMIT_PER_MINUTE` (default 20) requests from the same client host in a minute | Expected behavior under load/abuse. Raise `RATE_LIMIT_PER_MINUTE` in `.env` if the limit is genuinely too low for real traffic. |

## Recovery from a corrupted/stale vector store

```bash
# bare metal
rm -rf chroma_db/
python -m src.ingest

# docker
docker compose down -v        # WARNING: deletes the named volume — confirm before running
docker compose up --build -d
docker compose run --rm shopbot-api python -m src.ingest
docker compose restart shopbot-api
```

## Rotating secrets

`.env` is gitignored and has never been committed (confirmed via `gitleaks`, `docs/evidence/2026-10-14_phase6-gitleaks-history.txt`). To rotate the OpenAI key: update `.env`, then restart the process/container — there's no separate secrets store to update in this build.
