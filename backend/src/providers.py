# src/providers.py
# OpenAI client factory (REQ-T-002). Cached, built-once client access —
# everything downstream calls get_embeddings() / get_chat_model() rather
# than constructing langchain_openai clients itself.
from functools import lru_cache

from src import config


@lru_cache(maxsize=1)
def get_embeddings():
    from langchain_openai import OpenAIEmbeddings
    return OpenAIEmbeddings(
        model=config.OPENAI_EMBEDDING_MODEL,
        api_key=config.OPENAI_API_KEY,
    )


@lru_cache(maxsize=1)
def get_chat_model():
    # temperature=0 always (REQ-N-002) — not a parameter callers can override.
    # Cached (REQ-N-005, "build once, serve many") so the API layer doesn't
    # construct a new client per request.
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=config.OPENAI_CHAT_MODEL,
        temperature=0,
        api_key=config.OPENAI_API_KEY,
    )
