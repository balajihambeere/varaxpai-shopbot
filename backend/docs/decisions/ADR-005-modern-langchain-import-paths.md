# ADR-005: Use `langchain_core` import paths instead of `langchain.schema` / `langchain.prompts`

## Status
Accepted

## Context
Importing `SystemMessage, HumanMessage` from `langchain.schema` and `ChatPromptTemplate` from `langchain.prompts` fails against the current `langchain` (1.4.5, 2026): `No module named 'langchain.schema'` and `No module named 'langchain.prompts'` (verified directly, not assumed — see `docs/evidence/`). LangChain reorganized these into `langchain_core.messages` and `langchain_core.prompts` in an earlier major version; both import cleanly in 1.4.5 and are drop-in replacements for the same classes (confirmed by direct import test).

## Decision
Use `from langchain_core.messages import SystemMessage, HumanMessage` and `from langchain_core.prompts import ChatPromptTemplate` everywhere this build needs them. `RunnablePassthrough` (`langchain_core.runnables`) and `StrOutputParser` (`langchain_core.output_parsers`) already used the current import paths and needed no change.

## Alternatives considered
1. **Pin an old `langchain` version matching older import paths** — rejected; pulling a years-old, likely-unpatched dependency version solely to preserve a stale import path is a worse security/maintenance trade than updating two import lines, and framework §9 asks for current, scanned dependencies, not nostalgically pinned ones.

## Consequences
None beyond the two corrected import lines — the classes, their constructors, and the chain-composition (`|`) syntax are otherwise unchanged in behavior. Logged here, not silently patched, per framework §1.4.1 ("do not guess... do not invent").
