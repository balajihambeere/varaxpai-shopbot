# Phase 5 — Frontend integration verification

**Resumed after a tool-level Bash outage** (recorded mid-Phase-5 in the prior session; confirmed not an app defect via the user's own `!`-prefixed shell at the time). Backend and frontend dev servers had stopped by this session; both were restarted clean and the round-trip re-verified from scratch.

## Setup
- Backend: `uvicorn src.api:app --host 0.0.0.0 --port 8000` (venv, provider=openai), log at `/tmp/shopbot-uvicorn.log`.
- Frontend: `npm run dev` in `zudyog-fashion/` (Next.js 16.2.10, Turbopack), log at `/tmp/zudyog-frontend.log`. No `SHOPBOT_API_URL` override needed — `app/api/chat/route.ts` defaults to `http://localhost:8000`, matching the backend.

## Backend health
```
$ curl -s http://localhost:8000/health
{"status":"ok","degraded":false,"service":"ShopBot","version":"1.0.0","provider":"openai","document_count":255}
```

## Round-trip through the frontend's own `/api/chat` route (not a direct call to the backend)

**Query 1 — out-of-catalog (fallback expected):**
```
$ curl -s -X POST http://localhost:3000/api/chat -H "Content-Type: application/json" -d '{"question":"What do you have for a wedding?"}'
{"answer":"I don't have a product that matches that specifically. Could you describe what you're looking for differently, or contact our team at support@zudyog.in?","session_id":"default"}
```
Correct fallback — no wedding-specific product exists in the 50-item catalog; this is the grounding guarantee working as designed, not a defect.

**Query 2 — known grounded query (matches Phase 1 calibration evidence exactly):**
```
$ curl -s -X POST http://localhost:3000/api/chat -H "Content-Type: application/json" -d '{"question":"Does the Printed Silk Saree need dry cleaning?"}'
{"answer":"Yes, the Printed Silk Saree requires dry cleaning only. Machine washing will damage the zari border and cause the silk to lose its sheen. It's also best to store it in a muslin cloth bag away from direct sunlight. If you have any more questions, feel free to ask!","session_id":"default"}
```
Byte-for-byte consistent with the answer recorded in `2026-10-14_phase1-smoke-test-recalibrated.txt` for the same question.

## Backend-side confirmation the calls came from the frontend proxy, not direct
```
{"ts": "2026-10-14T13:06:25", ..., "route": "/ask", "status_code": 200, "evidence_found": false}
INFO:     127.0.0.1:49340 - "POST /ask HTTP/1.1" 200 OK
{"ts": "2026-10-14T13:06:45", ..., "route": "/ask", "status_code": 200, "evidence_found": true}
INFO:     127.0.0.1:49345 - "POST /ask HTTP/1.1" 200 OK
```
`evidence_found: false/true` matches the fallback/grounded shape of each query above.

## Known gap, stated honestly
The exit criterion in `docs/implementation-plan.md` calls for "screenshot/log evidence of at least one real round-trip through the actual UI." The Claude-in-Chrome browser extension was not connected in this session, so a visual click-through of the chat widget in an actual browser window was not captured. What **is** verified: the exact HTTP contract the chat widget calls (`POST /api/chat` on the running Next.js dev server, which internally calls `POST /ask` on the running FastAPI backend) end-to-end, with both fallback and grounded response shapes confirmed and cross-checked against backend request logs. The user was asked and chose to accept this log-based evidence rather than block on connecting the browser extension. Residual risk is low: the widget's own client-side code (`components/`) was not line-audited in this pass, but the `route.ts` proxy — the only code that talks to the backend — is confirmed correct.
