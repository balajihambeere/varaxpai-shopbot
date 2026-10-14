# ADR-008: Pin `langchain-community==0.3.27` (no-deps) so RAGAS can import

## Status
Accepted

## Context
`ragas` (tested at both the latest 0.4.3 and an older 0.2.15) unconditionally imports `from langchain_community.chat_models.vertexai import ChatVertexAI` inside `ragas/llms/base.py`, regardless of which LLM provider is actually configured. The currently-released `langchain-community` (0.4.2) has removed that submodule as part of its stated sunset/deprecation (the package prints its own deprecation warning on import, pointing to standalone integration packages as the replacement). The result is a hard `ModuleNotFoundError` on `import ragas`, confirmed directly (not assumed) with both ragas versions. Installing the standalone `langchain-google-vertexai` package does not fix it — the broken import path is a submodule *inside* `langchain_community` itself, which that package doesn't restore.

This build never uses Vertex AI (only OpenAI/Ollama, per ADR-001) — the failure is purely an unused import path breaking package load.

## Decision
Pin `ragas==0.2.15` (not the latest 0.4.3 — both have the identical broken import, but installing `ragas` always re-resolves `langchain-community` to its latest, so the pin order matters) and `pip install --no-deps langchain-community==0.3.27` afterward — the last `0.3.x` release that still ships `langchain_community.chat_models.vertexai`. `--no-deps` avoids pip trying to downgrade `langchain-core`/`langchain` to satisfy `langchain-community==0.3.27`'s original (much older) constraints, since those older constraints predate the `langchain` 1.x line this build otherwise uses. Install order matters: `ragas` first (it pulls `langchain-community` latest as a transitive dependency), then re-pin `langchain-community==0.3.27 --no-deps` last, overwriting that resolution. Verified by running the full existing test suite (26 tests, Phases 0-3) after the pin — all still pass, confirming no regression in the retriever/prompt/API code that uses `langchain_core`/`langchain_openai`/`langchain_ollama` directly.

## Alternatives considered
1. **Pin an older `langchain` (<1.0) matching `langchain-community==0.3.x`'s native constraints** — rejected; would undo ADR-005's fix and revert the whole project to a years-old LangChain major version, for a dependency (`langchain-community`) this project doesn't otherwise need at all — ShopBot never imports it directly.
2. **Vendor/monkeypatch a stub `langchain_community.chat_models.vertexai` module** — rejected; editing third-party package internals is not reproducible for someone else running `pip install -r requirements.txt` on a clean checkout (framework §12 "prove clean-environment setup").
3. **Drop RAGAS, build a custom Faithfulness/Context-Precision scorer** — rejected; RAGAS is the book's own named evaluation framework (Ch9, C-022) and reinventing it would be exactly the kind of invented-requirement framework §1.4.1 warns against.

## Consequences
`requirements.txt` must pin `langchain-community==0.3.27` explicitly (a plain `pip freeze` after this fix captures it correctly). If a future `ragas` release removes the unconditional Vertex AI import, this pin can be dropped — recorded here so the next person knows why it's there and when it's safe to remove.
