# ADR-002: `/health` verifies the ChromaDB collection is non-empty, beyond the book's literal check

## Status
Accepted

## Context
Book 1's `/health` endpoint (Ch8) returns a static `{"status": "ok", "service": "ShopBot", "version": "1.0.0"}` — it does not check any dependency. This is sufficient for Railway's deployment probe in the book's narrow sense (process is up), but it cannot distinguish "the service is up and the Grounding Layer has evidence to serve" from "the service is up but the vector store was never ingested or was wiped," which would silently produce empty-retrieval fallbacks for every query — itself a (correctly-handled, but avoidable) Grounding Failure mode.

## Decision
Extend `/health` to also check that the configured ChromaDB collection exists and has a non-zero document count, returning a degraded (but still HTTP 200, with a `"degraded": true` field) status if not, rather than crashing or lying.

## Alternatives considered
1. **Match the book exactly** — rejected because it would hide an entire class of operational failure the book's own Chapter 1 thesis argues against (a system that looks fine and silently isn't).
2. **Fail the health check hard (HTTP 503) if the collection is empty** — considered, but rejected as the primary behavior because a fresh deployment legitimately has an empty collection before the first ingest run; a hard failure would block the normal "deploy, then ingest" sequence. A degraded-but-200 status with a clear field is more operationally correct.

## Consequences
This is a deviation from the book's literal code (documented, not silent, per framework §1.2 precedence rules — engineering best practice outranks blind literalism when the book's own stated principles support the deviation). Traceability entry for REQ-N-009 should reference this ADR.
