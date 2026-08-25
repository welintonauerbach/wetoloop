# Roadmap

WetoLoop begins at `0.0.1`. The `0.x` line is intentionally iterative while contracts
stabilize.

## 0.0.1 — public baseline

- Open-source repository structure and community files.
- Engineering Loop templates and schemas.
- Initial validator baseline.
- Explicit source/template licensing split.
- Basic repository quality workflow.

## 0.0.2 — contract foundation

Active specifications:

- [SPEC-001 — Semantic Validator Foundation](specs/001-semantic-validator-foundation.md)
- [SPEC-002 — ImpactSet & Task Verification Contract](specs/002-impactset-task-verification-contract.md)

These specifications establish the validation and impact-analysis contracts required before build reuse, test infrastructure reuse and Harness execution are automated.

## Next 0.0.x milestones

- Implement and stabilize SPEC-001 semantic validation across PRD, requirements, TechSpec,
  tasks, test strategy, state, harness and final validation report.
- Add self-contained validator fixtures and conformance tests.
- Implement SPEC-002 `ImpactSet` and task-level verification contracts.
- Define producer fingerprints for restore, build, generated artifacts and infrastructure.
- Implement warm focused task gates and a cold final package gate.
- Define reusable Docker/database lifecycle strategies.
- Add metrics for cache hits, producer executions, slow tests, flakes and redundant tests.
- Introduce reusable skills for init, definition, design, planning, execution and finalization.
- Implement the npm CLI and package boundaries.

## Before 1.0

- Stable activity and harness contracts.
- Backward-compatibility and migration policy.
- Harness conformance suite.
- Documented extension model.
- Reproducible release and package publishing process.
