# src/config.py
# Central place for every environment-driven setting. Nothing in this
# project reads os.getenv() directly outside this module, so there is
# exactly one place to look when a value needs to change.
import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").strip().lower()
if LLM_PROVIDER != "openai":
    raise ValueError(f"LLM_PROVIDER must be 'openai', got: {LLM_PROVIDER!r}")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

# REQ-F-010: this is a provisional default — scripts/calibrate_threshold.py
# records an empirically-derived value for the actual catalog, which may
# not match this default at a different catalog size/composition.
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.75"))
MAX_RETRIEVED_CHUNKS = int(os.getenv("MAX_RETRIEVED_CHUNKS", "3"))

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "zudyog_products")

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# REQ-N-010: basic abuse/cost guard on /ask.
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "20"))

# REQ-N-006: expected embedding dimensionality for the configured provider
# — used by the retriever/ingest to detect a provider/collection mismatch
# loudly instead of returning silently-wrong nearest neighbours.
EXPECTED_EMBEDDING_DIM = 1536

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Set it in .env.")
