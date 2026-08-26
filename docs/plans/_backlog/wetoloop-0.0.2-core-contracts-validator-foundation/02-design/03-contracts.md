# Contract Register

| ID | Contract | Authority | Consumer | Change rule |
|---|---|---|---|---|
| CTR-001 | Activity manifest and applicability | PLAN.yaml + plan schema | Aggregate validator, lifecycle | Schema/version change plus conformance evidence |
| CTR-002 | Canonical validator result | TECHSPEC + validator tests | CLI/harness/future integrations | Stable JSON/exit semantics; breaking change explicit |
| CTR-003 | ImpactSet | TECHSPEC + task schema | Task planner, future impact engine | Provider-neutral fields; extension by versioned contract |
| CTR-004 | VerificationRun | TECHSPEC + state schema | Gates, evidence, final report | Fresh per affected verification; never satisfied by stale result |
| CTR-005 | ProducerFingerprint | TECHSPEC + state schema | Restore/build/generated/infra producers | Hash only declared relevant inputs and tool/config identity |
| CTR-006 | ProducerRecord | TECHSPEC + state schema | Gate executor and report | Reuse requires matching fingerprint and healthy artifact state |
| CTR-007 | Task execution contract | TASK schema + semantic validator | Planner, executor, reviewer | Task owns requirements, impact, verification and evidence |
| CTR-008 | Harness command contract | HARNESS schema + semantic validator | Runtime adapters | Structured executable+argv; no raw shell interpolation |
| CTR-009 | Test Strategy contract | TEST_STRATEGY + semantic validator | Task/package gates | Focused by default; escalation and package ownership explicit |
| CTR-010 | Validation Report contract | VALIDATION_REPORT + semantic validator | Gate G, reviewer, release | Label-only success is insufficient; evidence/counts/producers reconcile |

Conflicting authorities are blockers. A lower-level validator implementation cannot silently override the public template/schema/decision contract.
