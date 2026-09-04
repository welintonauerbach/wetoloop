# Product Requirements Document

## Problem and outcome

WetoLoop 0.0.1 expresses stronger engineering rules than its current aggregate validators can deterministically enforce. Some plan-based validators perform only shallow checks, while legacy modes enforce a different historical document shape. Impact-aware testing and producer reuse are design principles but not yet explicit machine-readable contracts.

WetoLoop 0.0.2 must make the public contract internally consistent and testable before runtime automation is introduced.

## Scope

### In scope

- one canonical plan-based semantic validation contract;
- structural validation for PLAN, TASK, STATE and HARNESS;
- semantic validation for Requirements, PRD, TechSpec, tasks, traceability, Test Strategy, Harness, State, lifecycle and Validation Report;
- explicit ImpactSet and gate-escalation contracts;
- explicit VerificationRun, ProducerFingerprint and ProducerRecord concepts;
- self-contained conformance fixtures and discrimination tests;
- warm focused task gates and a cold final package gate policy;
- dogfooding migration of this activity from 0.0.1 to 0.0.2 before Gate G.

### Out of scope

- npm CLI implementation;
- TypeScript core migration;
- automatic impact discovery or test selection;
- build cache engine;
- Docker/database lifecycle executor;
- skills;
- provider/runtime integrations.

## Users and journeys

1. An activity author creates a manifest-driven activity and receives deterministic validation.
2. An executing agent evaluates declared impact, reuses valid producers and runs only fresh verification for affected risk.
3. A reviewer traces requirements to one implementation owner, task evidence and final package evidence.
4. A maintainer changes semantic rules using positive and discriminating negative conformance fixtures.

## Requirements and release acceptance

Release acceptance requires every approved requirement in REQUIREMENTS.md to have one implementation owner, discriminating evidence and successful final package validation. The final activity must self-validate using the 0.0.2 contract before the release is ready.
