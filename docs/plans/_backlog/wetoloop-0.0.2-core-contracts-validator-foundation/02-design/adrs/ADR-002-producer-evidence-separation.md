# ADR-002 — Separate fresh verification from reusable producers

Status: Accepted

## Context

WetoLoop requires fresh evidence for affected risk but also wants fast iteration through reuse of builds, dependency state, generated artifacts, containers and database baselines.

## Decision

Represent VerificationRun separately from ProducerFingerprint and ProducerRecord. Verification is fresh; a producer/artifact may be reused when declared inputs still match and its state remains valid.

## Consequences

Commit SHA anchors evidence but no longer invalidates every physical producer by default. Future cache and infrastructure engines can implement this contract without changing evidence semantics.
