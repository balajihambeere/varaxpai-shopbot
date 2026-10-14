# ADR-004: Build the backend at `zuxpai/shopbot/`, alongside the existing `zudyog-fashion` frontend

## Status
Accepted

## Context
Before this design pass, `/Applications/zuxpert/Book-1/zuxpai/` already contained a Next.js frontend (`zudyog-fashion`) with a working chat UI (`ChatBotContext`, `ChatBot.tsx`, `AskAIButton.tsx`) and an `/api/chat` route that forwards `{question, session_id}` JSON to `${SHOPBOT_API_URL}/ask`, defaulting to `http://localhost:8000`. It also contained `products.py`, a verbatim Python conversion of the frontend's product data matching the book's exact Ch5 schema, with the Ch10 "function" vocabulary fix already applied. No Python backend existed yet anywhere in the tree.

## Decision
Create the backend at `zuxpai/shopbot/`, sibling to `zudyog-fashion`, and copy `products.py` into `shopbot/data/products.py` verbatim (no edits). Treat the frontend's existing contract as fixed and build the backend to match it, rather than redesigning the API shape.

## Alternatives considered
1. **Build an isolated repo elsewhere (e.g. directly under `Book-1/`)** — rejected; it would duplicate or orphan the already-working frontend integration and the already-correctly-converted catalog data, violating framework §1.5 ("do not over-engineer" / don't redo work that already fits).
2. **Modify the frontend's API contract to something different** — rejected; nothing about the existing contract is wrong, and changing it would be unjustified churn with no stated requirement behind it.

## Consequences
- `shopbot/` gets its own git repository (the book's Ch2 instructs `git init` in the project root; `zudyog-fashion` has no `.git` of its own either, so this does not conflict with any existing VCS state).
- REQ-T-006 ("no frontend changes required") is a direct consequence of this decision, not an independent requirement — it only holds because this ADR chose to match the existing contract rather than invent a new one.
