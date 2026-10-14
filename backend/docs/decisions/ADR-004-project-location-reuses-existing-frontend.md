# ADR-004: Build the backend alongside the existing frontend, in the same companion-code directory

## Status
Accepted (project renamed since: directory originally `zuxpai/shopbot`, now `varaxpai/backend` — the decision itself is unaffected by the rename)

## Context
Before this design pass, the companion-code directory already contained a Next.js frontend (originally `zudyog-fashion`, now `frontend`) with a working chat UI (`ChatBotContext`, `ChatBot.tsx`, `AskAIButton.tsx`) and an `/api/chat` route that forwards `{question, session_id}` JSON to `${SHOPBOT_API_URL}/ask`, defaulting to `http://localhost:8000`. It also contained `products.py`, a verbatim Python conversion of the frontend's product data, with the "function" vocabulary fix already applied. No Python backend existed yet anywhere in the tree.

## Decision
Create the backend as a sibling directory to the frontend, and copy `products.py` into the backend's `data/products.py` verbatim (no edits). Treat the frontend's existing contract as fixed and build the backend to match it, rather than redesigning the API shape.

## Alternatives considered
1. **Build an isolated repo elsewhere** — rejected; it would duplicate or orphan the already-working frontend integration and the already-correctly-converted catalog data, violating framework §1.5 ("do not over-engineer" / don't redo work that already fits).
2. **Modify the frontend's API contract to something different** — rejected; nothing about the existing contract is wrong, and changing it would be unjustified churn with no stated requirement behind it.

## Consequences
- The backend gets its own git repository; the frontend has no `.git` of its own either, so this does not conflict with any existing VCS state.
- REQ-T-006 ("no frontend changes required") is a direct consequence of this decision, not an independent requirement — it only holds because this ADR chose to match the existing contract rather than invent a new one.
