# API Reference

Base URL: `http://localhost:8000` (local/Docker) — no authentication. Not intended to be exposed directly to the public internet without a reverse proxy (see `docs/security/threat-model.md`).

## `GET /health`

Liveness + dependency check. Confirms the ChromaDB collection is reachable and non-empty, not just that the process is running (ADR-002) — a service that's "up" with an empty collection would otherwise silently fall back on every query, which is the exact failure class this project exists to prevent.

**Request:** no parameters.

**Response — healthy (200):**
```json
{
  "status": "ok",
  "degraded": false,
  "service": "ShopBot",
  "version": "1.0.0",
  "provider": "openai",
  "document_count": 255
}
```

**Response — degraded, collection empty (200, not an error status):**
```json
{
  "status": "degraded",
  "degraded": true,
  "service": "ShopBot",
  "version": "1.0.0",
  "reason": "collection is empty — run `python -m src.ingest`"
}
```
A degraded response is still HTTP 200 (the process itself is alive and able to answer about its own state) — check the `degraded` field, not the status code, to detect this case. See `docs/operations.md` for recovery.

## `POST /ask`

Ask ShopBot a product question. Returns a grounded answer sourced from retrieved catalog evidence, or the exact fallback string when no evidence clears the similarity threshold (REQ-N-001) — this endpoint never calls the language model at all in the fallback case, so a "no answer" response is architecturally guaranteed to not be a guess.

**Request body:**
```json
{
  "question": "Does the Printed Silk Saree need dry cleaning?",
  "session_id": "default"
}
```
| Field | Type | Required | Notes |
|---|---|---|---|
| `question` | string | yes | 1–500 characters after whitespace trim and smart-quote/em-dash normalization. Rejected if empty, over 500 chars, or shaped like a prompt-injection attempt (see below). |
| `session_id` | string | no | defaults to `"default"`. Echoed back unchanged; not currently used for conversation memory (no session state is kept — each request is independent). |

**Response — 200 (success or grounded fallback — both are 200):**
```json
{
  "answer": "Yes, the Printed Silk Saree requires dry cleaning only. ...",
  "session_id": "default"
}
```
The fallback answer, returned verbatim and byte-for-byte identical whenever no evidence clears the retrieval threshold:
```json
{
  "answer": "I don't have a product that matches that specifically. Could you describe what you're looking for differently, or contact our team at support@zudyog.in?",
  "session_id": "default"
}
```

**Response — 422 Unprocessable Entity:** returned by FastAPI/Pydantic validation, before the retriever or model are ever invoked, for any of:
- Empty or whitespace-only `question`
- `question` longer than 500 characters
- `question` matching a prompt-injection-shaped pattern (case-insensitive): "ignore (all) previous instructions", "you are now ...", "act as ...", mentions of "system prompt", "forget everything/all"

**Response — 429 Too Many Requests:** returned when a client exceeds `RATE_LIMIT_PER_MINUTE` (default 20) requests per minute, keyed by client host.
```json
{"detail": "Rate limit exceeded. Please slow down."}
```

**Response — 503 Service Unavailable:** returned when OpenAI raises an error — network failure, invalid/expired key, provider outage.
```json
{"detail": "ShopBot's language model provider is temporarily unavailable. Please try again shortly."}
```

### Example
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What colours does the Breathable Cotton Kurta come in?"}'
```

## Frontend contract

The existing `zudyog-fashion` Next.js app's `app/api/chat/route.ts` proxies directly to this API: it forwards the raw request body to `POST ${SHOPBOT_API_URL:-http://localhost:8000}/ask` and returns the JSON response unchanged. No separate contract to maintain — the shapes above are exactly what the frontend sends and expects. Verified end-to-end in `docs/evidence/2026-10-14_phase5-frontend-integration.md`.
