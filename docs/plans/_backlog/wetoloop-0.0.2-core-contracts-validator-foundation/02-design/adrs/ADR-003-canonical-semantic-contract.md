# ADR-003 — Use one canonical plan-based semantic contract

Status: Accepted

## Context

Some 0.0.1 validator entrypoints contain a shallow `--plan` path and a stronger legacy positional path targeting an older document shape.

## Decision

The manifest-driven plan-based path is the sole public semantic authority. Current templates, schemas, decisions and conformance fixtures define expected behavior. Legacy entrypoints may be retained only as compatibility adapters and may not define divergent semantics.

## Consequences

Aggregate validation becomes deterministic and future CLI/harness consumers have one stable contract to invoke.
