# ADR-002: `/health` verifies the ChromaDB collection is non-empty, beyond a static check

## Status
Accepted

## Context
A static `/health` endpoint returning `{"status": "ok", "service": "ShopBot", "version": "1.0.0"}` with no dependency check is sufficient for a deployment probe in the narrow sense (process is up), but it cannot distinguish "the service is up and the Grounding Layer has evidence to serve" from "the service is up but the vector store was never ingested or was wiped," which would silently produce empty-retrieval fallbacks for every query — itself a (correctly-handled, but avoidable) Grounding Failure mode.

## Decision
Extend `/health` to also check that the configured ChromaDB collection exists and has a non-zero document count, returning a degraded (but still HTTP 200, with a `"degraded": true` field) status if not, rather than crashing or lying.

## Alternatives considered
1. **A static health check with no dependency verification** — rejected because it would hide an entire class of operational failure: a system that looks fine and silently isn't.
2. **Fail the health check hard (HTTP 503) if the collection is empty** — considered, but rejected as the primary behavior because a fresh deployment legitimately has an empty collection before the first ingest run; a hard failure would block the normal "deploy, then ingest" sequence. A degraded-but-200 status with a clear field is more operationally correct.

## Consequences
Traceability entry for REQ-N-009 references this ADR.
