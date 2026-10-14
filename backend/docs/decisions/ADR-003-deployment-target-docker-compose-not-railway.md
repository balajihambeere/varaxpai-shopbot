# ADR-003: Target Docker Compose (L2) for this session; Railway files written but not executed

## Status
Accepted

## Context
Book 1 Ch8 deploys ShopBot to Railway via `railway login && railway up`. This session has no Railway account, no CLI session, and no instruction from the user to create cloud infrastructure or spend money on their behalf. The framework's own default hosting (§0) is "Docker Compose locally; cloud files written but marked NOT VERIFIED" when no cloud target is specified — which matches this exact situation.

## Decision
Build and verify a Docker Compose setup locally (L2 per framework §12). Write the Railway `Procfile` (REQ-T-005) exactly as the book specifies, so it is ready to use, but do not attempt to run `railway up` or create any account/billing relationship. Tag Railway deployment `NOT-VERIFIED`, L0.

## Alternatives considered
1. **Ask the user for Railway credentials and deploy for real** — rejected as a default; deploying to a real cloud service, potentially incurring cost and creating a publicly-reachable endpoint, is exactly the class of action the operating guidelines say requires asking first rather than assuming. If the user wants L3 verification, that is a specific follow-up ask, not a default action.
2. **Skip containerization entirely and only verify a bare venv run** — rejected; Docker Compose is a reversible, local, zero-cost action that gets closer to production-shape without the irreversibility of a real cloud deploy, and it's explicitly the framework's stated default.

## Consequences
Final report will state deployment level reached as L1/L2 (whichever is actually verified by the time implementation finishes), not L3, and will not describe the system as having been deployed to Railway.
