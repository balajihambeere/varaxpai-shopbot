# ShopBot

An AI-powered product assistant for **zUdyog Fashion**, a fictional Indian clothing retailer. ShopBot answers customer questions about a 50-product catalog using retrieval-augmented generation (RAG), and says "I don't know, contact support" rather than guessing when it has no evidence for an answer.

This directory holds two independent projects, each with its own git history:

| Project | What | Start here |
|---|---|---|
| `backend/` | Python/FastAPI RAG service — ingestion, retrieval, grounded prompting, `/ask` + `/health` | `backend/README.md` |
| `frontend/` | Next.js chat widget — the customer-facing UI, already wired to the backend's `/ask` endpoint | `frontend/README.md` |

## Running both together

```bash
# terminal 1 — backend
cd backend
source venv/bin/activate
uvicorn src.api:app --reload

# terminal 2 — frontend
cd frontend
npm run dev
```

Then open the frontend at `http://localhost:3000` — it talks to the backend at `http://localhost:8000` by default (`SHOPBOT_API_URL` in the frontend's env if you need to point it elsewhere).

Full architecture, API reference, deployment, and known limitations are documented in `backend/docs/` — see `backend/README.md`'s documentation map.
