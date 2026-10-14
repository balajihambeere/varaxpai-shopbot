# Sources

## External documentation
No live web fetch of external documentation was performed with a URL and access date logged during this build. Library behavior (LangChain's `langchain_core`/`langchain_openai`/`langchain_ollama` import paths, ChromaDB's `where`-clause syntax, RAGAS's dataset column names, package version compatibility) was determined empirically — by running the actual installed code, reading its error messages and source files directly (`pip show`, tracebacks, `site-packages` inspection), and recording the result as evidence — rather than by citing external docs. This is noted explicitly here rather than fabricating URLs/dates that weren't actually used; see each decision's reasoning and the exact commands run in:
- `docs/decisions/ADR-005-modern-langchain-import-paths.md`
- `docs/decisions/ADR-007-chromadb-multi-field-where-syntax.md`
- `docs/decisions/ADR-008-ragas-requires-pinned-langchain-community.md`
- `docs/decisions/ADR-009-ragas-column-names-changed.md`
- `docs/evidence/2026-10-14_langchain-import-check.md`

## Tooling
- `gitleaks` (secret scanning) and `pip-audit` (dependency vulnerability scanning) — run locally against this repository and its installed environment; see `docs/evidence/2026-10-14_phase6-*`. Findings used were the tools' own direct output, not external advisories looked up separately.
- Docker, Docker Compose — standard local tooling, version numbers recorded in `docs/evidence/2026-10-14_phase7-docker-compose.md`.

## Pre-existing project assets (not sourced during this build, inherited)
- `data/products.py` — the 50-product catalog, copied verbatim from a pre-existing `products.py` in the companion frontend project.
- The Next.js frontend — built separately before this backend build started; its `/api/chat` contract was read directly from its own source (`app/api/chat/route.ts`), not from external documentation.
