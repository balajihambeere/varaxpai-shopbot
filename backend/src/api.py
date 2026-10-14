# src/api.py
# FastAPI app: POST /ask, GET /health. Pydantic validation
# (empty/length/injection), lifespan pattern (build once, serve many —
# REQ-N-005), structured logging with a request ID (REQ-N-009), basic
# rate limiting (REQ-N-010).
#
# REQ-T-006: request/response shape must match the existing
# zudyog-fashion frontend's app/api/chat/route.ts contract exactly:
# {question, session_id} -> {answer, session_id}. Do not change this
# shape without updating the frontend (see ADR-004).
import re
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from src import config
from src.logging_setup import logger
from src.ratelimit import rate_limiter
from src.retriever import warmup


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ShopBot API", extra={"provider": config.LLM_PROVIDER})
    status = warmup()
    app.state.collection_status = status
    logger.info(
        f"ShopBot ready: {status['document_count']} chunks in "
        f"'{status['collection_name']}'",
        extra={"provider": config.LLM_PROVIDER},
    )
    yield


app = FastAPI(
    title="ShopBot API",
    description="AI-powered product assistant for zUdyog Fashion",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Request/response models ──────────────────────────────────────────
_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"you\s+are\s+now\s+",
    r"act\s+as\s+",
    r"system\s+prompt",
    r"forget\s+(everything|all)",
]


class QuestionRequest(BaseModel):
    question: str
    session_id: str = "default"

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        v = v.strip()
        v = v.replace("‘", "'").replace("’", "'")  # smart single quotes
        v = v.replace("“", '"').replace("”", '"')  # smart double quotes
        v = v.replace("—", " - ")  # em dash
        v = v.replace("​", "")  # zero-width space

        if not v:
            raise ValueError("Question cannot be empty.")
        if len(v) > 500:
            raise ValueError(f"Question too long ({len(v)} characters). Maximum is 500.")

        for pattern in _INJECTION_PATTERNS:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Invalid question format.")

        return v


class AnswerResponse(BaseModel):
    answer: str
    session_id: str


# ── Endpoints ────────────────────────────────────────────────────────
@app.get("/health")
def health_check(request: Request):
    """
    ADR-002: beyond a plain static health check, also reports whether
    the ChromaDB collection is actually populated — a service
    that is "up" but has nothing to retrieve from would otherwise
    silently produce fallback answers for every query, which is itself
    the class of failure this whole project exists to prevent.
    """
    status = getattr(request.app.state, "collection_status", None)
    if status is None or status["document_count"] == 0:
        return JSONResponse(
            status_code=200,
            content={
                "status": "degraded",
                "degraded": True,
                "service": "ShopBot",
                "version": "1.0.0",
                "reason": "collection is empty — run `python -m src.ingest`",
            },
        )
    return {
        "status": "ok",
        "degraded": False,
        "service": "ShopBot",
        "version": "1.0.0",
        "provider": config.LLM_PROVIDER,
        "document_count": status["document_count"],
    }


@app.post("/ask", response_model=AnswerResponse)
def ask_shopbot(payload: QuestionRequest, request: Request):
    """
    Ask ShopBot a product question. Returns a grounded answer sourced
    from zUdyog Fashion's product catalog, or the exact fallback string
    when no evidence clears the similarity threshold (REQ-N-001).
    """
    request_id = str(uuid.uuid4())
    client_key = request.client.host if request.client else "unknown"

    if not rate_limiter.allow(client_key):
        logger.warning(
            "Rate limit exceeded",
            extra={"request_id": request_id, "route": "/ask", "status_code": 429},
        )
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please slow down.")

    start = time.monotonic()
    try:
        from src.prompt import answer, NO_EVIDENCE_FALLBACK  # local import: lets tests patch src.prompt freely
        result = answer(payload.question)
    except Exception as e:
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        logger.error(
            f"Provider error: {type(e).__name__}",
            extra={"request_id": request_id, "route": "/ask", "status_code": 503,
                   "latency_ms": latency_ms, "provider": config.LLM_PROVIDER},
        )
        raise HTTPException(
            status_code=503,
            detail="ShopBot's language model provider is temporarily unavailable. Please try again shortly.",
        )

    latency_ms = round((time.monotonic() - start) * 1000, 1)
    logger.info(
        "Answered /ask",
        extra={"request_id": request_id, "route": "/ask", "status_code": 200,
               "latency_ms": latency_ms, "provider": config.LLM_PROVIDER,
               "evidence_found": result != NO_EVIDENCE_FALLBACK},
    )
    return AnswerResponse(answer=result, session_id=payload.session_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host=config.API_HOST, port=config.API_PORT, reload=True)
