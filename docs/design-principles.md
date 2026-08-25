# Design principles

## Evidence is fresh; infrastructure may be reused

A previous test result does not prove the current affected risk. Tests that are required
for the current change must produce fresh evidence. Build artifacts, dependency caches,
containers and database baselines may be reused when their inputs remain valid.

## Focused task gates

Intermediate task completion should run the smallest gate that proves the affected surface.
Unknown impact should escalate to a module or bounded subsystem before escalating to the
entire repository.

## Final package gate

The completed activity must run the full applicable package suite, coverage and clean
integration/migration checks required by the project.

## Input fingerprints

Reuse decisions should be based on relevant inputs, not merely the current commit SHA.
A commit identifies evidence; fingerprints determine whether a producer artifact remains
valid.

## Persistent test infrastructure

Docker images, healthy containers, schema state and deterministic seed baselines should be
reused whenever possible. Clean-from-zero database construction belongs in the final gate
or when migration inputs change.

## Test debt is explicit

Slow, overlapping, redundant or flaky tests should be recorded as optimization candidates.
Unrelated tasks should not silently remove tests merely because they appear redundant.
