# ADR-005: Use `langchain_core` import paths instead of the book's `langchain.schema` / `langchain.prompts`

## Status
Accepted

## Context
Book 1 (Ch7) imports `SystemMessage, HumanMessage` from `langchain.schema` and `ChatPromptTemplate` from `langchain.prompts`. Installing the current `langchain` (1.4.5, 2026) and testing those exact import statements fails: `No module named 'langchain.schema'` and `No module named 'langchain.prompts'` (verified directly, not assumed — see `docs/evidence/`). LangChain reorganized these into `langchain_core.messages` and `langchain_core.prompts` in an earlier major version; both import cleanly in 1.4.5 and are drop-in replacements for the classes the book uses (confirmed by direct import test).

This is an instance of framework §1.2 "book says something **outdated**... do not copy it silently. Mark it BOOK-CONFLICT, explain, and propose a fix" — the book's code is correct for the LangChain version current when it was written; it is stale against the version available in this environment today.

## Decision
Use `from langchain_core.messages import SystemMessage, HumanMessage` and `from langchain_core.prompts import ChatPromptTemplate` everywhere this build needs them. `RunnablePassthrough` (`langchain_core.runnables`) and `StrOutputParser` (`langchain_core.output_parsers`) already match the book's own import paths and needed no change.

## Alternatives considered
1. **Pin an old `langchain` version matching the book's era** — rejected; pulling a years-old, likely-unpatched dependency version solely to match a book's import paths is a worse security/maintenance trade than updating two import lines, and framework §9 asks for current, scanned dependencies, not nostalgically pinned ones.

## Consequences
None beyond the two corrected import lines — the classes, their constructors, and the chain-composition (`|`) syntax the book relies on are otherwise unchanged in behavior. Logged here, not silently patched, per framework §1.4.1 ("do not guess... do not invent") and §1.2 (BOOK-CONFLICT must be explained, not hidden).
