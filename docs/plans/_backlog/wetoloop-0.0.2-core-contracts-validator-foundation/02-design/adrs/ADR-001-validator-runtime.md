# ADR-001 — Keep Python as validator runtime for 0.0.2

Status: Accepted

## Context

Validator semantics and public contracts need stabilization. Migrating implementation language at the same time would mix behavioral changes with porting risk.

## Decision

Keep dependency-light Python validators as the executable reference implementation for WetoLoop 0.0.2. A future TypeScript core must pass the same conformance suite before replacing them.

## Consequences

The release focuses on contract correctness. Python remains an implementation choice, not a provider-specific architectural dependency.
