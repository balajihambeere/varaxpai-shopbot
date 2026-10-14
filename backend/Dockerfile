# Dockerfile — REQ-T-004 (Docker Compose, local L2 target per ADR-003)
FROM python:3.12-slim

WORKDIR /app

# System deps for chromadb's native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# ADR-008: a single-pass `pip install -r requirements.txt` is
# ResolutionImpossible — ragas pulls langchain-community latest (0.4.2,
# incompatible with this project's langchain-core 1.x line), so the fix
# installs everything else first, then overwrites langchain-community
# with the pinned 0.3.x release via --no-deps. Verified against a clean
# venv (not just this build image) before landing here.
RUN grep -v '^langchain-community==' requirements.txt > /tmp/requirements-no-lc.txt \
    && pip install --no-cache-dir -r /tmp/requirements-no-lc.txt \
    && pip install --no-cache-dir --no-deps $(grep '^langchain-community==' requirements.txt)

COPY data/ ./data/
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY evaluation/ ./evaluation/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Image ships without a baked-in ChromaDB collection — ingestion runs
# once against the mounted chroma_db/ volume (see docker-compose.yml),
# matching Ch4/Ch5's "ingest, then serve" sequence, not baked at build
# time (so re-ingesting after a catalog/threshold change doesn't require
# a rebuild).
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
