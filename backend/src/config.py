# src/config.py
# Central place for every environment-driven setting. Nothing in this
# project reads os.getenv() directly outside this module, so there is
# exactly one place to look when a value needs to change (Ch2's
# "structure decided once" rule, applied to configuration).
import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
if LLM_PROVIDER not in ("openai", "ollama"):
    raise ValueError(f"LLM_PROVIDER must be 'openai' or 'ollama', got: {LLM_PROVIDER!r}")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "llama3.2")

# REQ-F-010: this is a provisional value until scripts/calibrate_threshold.py
# records an empirically-derived one for the real 50-product catalog (Ch6
# calibrates against the book's own 5-product demo catalog only).
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.75"))
MAX_RETRIEVED_CHUNKS = int(os.getenv("MAX_RETRIEVED_CHUNKS", "3"))

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "zudyog_products")

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# REQ-N-010: basic abuse/cost guard on /ask. Book is silent on this —
# ENGINEERING REQUIREMENT, not BOOK-SPECIFIED.
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "20"))

# REQ-N-006: embedding dimensionality differs by provider (Ch2) — used by
# the retriever/ingest to detect a provider/collection mismatch loudly
# instead of returning silently-wrong nearest neighbours.
EXPECTED_EMBEDDING_DIM = {"openai": 1536, "ollama": 768}[LLM_PROVIDER]

if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
    raise ValueError(
        "LLM_PROVIDER=openai but OPENAI_API_KEY is not set. "
        "Set it in .env or switch LLM_PROVIDER=ollama."
    )
