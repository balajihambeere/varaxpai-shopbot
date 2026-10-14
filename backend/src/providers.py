# src/providers.py
# Provider abstraction (REQ-T-002, ADR-001). Everything downstream calls
# get_embeddings() / get_chat_model() and never imports langchain_openai
# or langchain_ollama directly — swapping LLM_PROVIDER in .env is the only
# change needed to switch providers (Ch2's two paths, unified behind one
# interface, per Ch6's "retriever as an abstraction" principle applied to
# the provider layer too).
from functools import lru_cache

from src import config


@lru_cache(maxsize=1)
def get_embeddings():
    if config.LLM_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model=config.OPENAI_EMBEDDING_MODEL,
            api_key=config.OPENAI_API_KEY,
        )
    else:
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(
            model=config.OLLAMA_EMBEDDING_MODEL,
            base_url=config.OLLAMA_BASE_URL,
        )


@lru_cache(maxsize=1)
def get_chat_model():
    # temperature=0 always (Ch7, REQ-N-002) — not a parameter callers can override.
    # Cached (REQ-N-005 / Ch8's lifespan principle, "build once, serve
    # many") so the API layer doesn't construct a new client per request.
    if config.LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=config.OPENAI_CHAT_MODEL,
            temperature=0,
            api_key=config.OPENAI_API_KEY,
        )
    else:
        from langchain_ollama import OllamaLLM
        return OllamaLLM(
            model=config.OLLAMA_CHAT_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=0,
        )
