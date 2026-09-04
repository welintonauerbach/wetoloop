# WetoLoop 0.0.2 — Core Contracts & Validator Foundation

This activity stabilizes the first public WetoLoop contracts before the CLI and automatic execution engine are introduced.

- Activity: `wetoloop-0.0.2-core-contracts-validator-foundation`
- Baseline contract: WetoLoop `0.0.1`
- Target release: WetoLoop `0.0.2`
- Base branch: `main`
- Approved base SHA: `fe6f1ede6c3bae80b84ada73fdbe28c71f822dea`
- Working branch: `feat/0.0.2-core-contracts-validator-foundation`
- Tier: `X`
- Lifecycle: `backlog`

## Outcome

WetoLoop 0.0.2 will have one canonical semantic validation path, self-contained conformance fixtures, explicit impact and producer-reuse contracts, and deterministic aggregate validation.

## Approved architectural decisions

1. Python remains the validator runtime for 0.0.2.
2. ImpactSet and fingerprints are defined in 0.0.2; the automatic impact/cache engine is deferred.
3. This activity starts under the 0.0.1 contract and must migrate/dogfood the 0.0.2 contract before Gate G.

## Execution boundary

This branch currently materializes planning artifacts only. Product code, schemas, validators and repository version metadata must not be changed until Gate F is explicitly approved.
