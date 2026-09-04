# Requirements

Use stable IDs, normative language and objective acceptance criteria.

| ID | Requirement | Acceptance | Owner task |
|---|---|---|---|
| REQ-VAL-001 | The system MUST define one canonical plan-based semantic contract for each validated activity artifact. | Plan-based validators reject divergent or incomplete semantics and legacy paths cannot redefine the public contract. | T01 |
| REQ-VAL-002 | The aggregate validator MUST execute every applicable canonical validator exactly once. | A conformance fixture shows the expected validator set with no missing or duplicate execution. | T06 |
| REQ-VAL-003 | Validator output MUST remain deterministic, UTF-8 and machine-readable with stable diagnostic codes. | Repeated validation of the same fixture produces equivalent ordered JSON diagnostics and canonical exit semantics. | T01 |
| REQ-SCH-001 | PLAN, TASK, STATE and HARNESS structured data MUST be validated against canonical schemas before semantic acceptance. | Positive fixtures pass and schema-invalid fixtures fail before semantic success is possible. | T02 |
| REQ-SCH-002 | Schema and artifact path resolution MUST remain contained, local and deterministic. | Traversal, unsupported-reference and duplicate-path fixtures are rejected without escaping the activity root. | T02 |
| REQ-DEF-001 | PRD, Requirements and TechSpec MUST have semantic validation aligned to current public templates. | Current-format positive activities pass and discriminating invalid documents fail without historical document shapes. | T03 |
| REQ-EXE-001 | Every executable task MUST declare a structured ImpactSet describing affected projects, tests, consumers, boundaries and runtime configuration. | Task fixtures reject executable tasks that omit required impact fields. | T04 |
| REQ-EXE-002 | Focused verification MUST define deterministic escalation that prefers a bounded module or subsystem before repository-wide regression when impact is uncertain. | Task/Test Strategy fixtures encode and validate the approved escalation policy. | T04 |
| REQ-STA-001 | Execution state MUST allow a null current task during planning/readiness while requiring task agreement once execution is active. | Readiness null-task passes and active execution with missing/mismatched task fails. | T04 |
| REQ-STA-002 | Fresh VerificationRun evidence MUST be represented separately from reusable producer and artifact state. | State/contracts distinguish verification runs from producers and reject ambiguous records. | T04 |
| REQ-CACHE-001 | Reusable producers MUST be validated by fingerprints of relevant inputs rather than commit SHA alone. | Contract fixtures show reuse eligibility based on producer inputs while evidence remains candidate-anchored. | T04 |
| REQ-TST-001 | Task validation MUST default to the smallest focused gate and MUST NOT automatically execute the complete package suite. | Test Strategy validation rejects unconditional full-suite-per-task policy unless impact requires it. | T05 |
| REQ-TST-002 | The final package gate MUST execute the complete applicable suite and release checks once for the final candidate. | Final activity records one canonical package gate with complete applicable checks. | T08 |
| REQ-TST-003 | Slow, flaky, overlapping or redundant tests MUST be reportable as optimization candidates without automatic deletion. | Final validation/learnings capture optimization candidates independently from pass/fail evidence. | T08 |
| REQ-HAR-001 | HARNESS MUST be schema-valid and enabled commands MUST match real canonical validator interfaces. | Harness fixtures detect invalid interface definitions and the corrected harness passes. | T05 |
| REQ-LIF-001 | Lifecycle validation MUST reconcile readiness, location, state and final package evidence without relying on label-only success strings. | Positive and negative lifecycle fixtures prove Gate F and Gate G semantics. | T05 |
| REQ-FIX-001 | Validator conformance tests MUST be self-contained and MUST NOT depend on a private or pre-existing real activity. | The suite uses only repository-owned fixtures and temporary activity roots. | T07 |
| REQ-CONF-001 | Every mandatory semantic rule introduced in 0.0.2 MUST have at least one passing case and one discriminating failing case. | The conformance matrix maps each mandatory rule/diagnostic to positive and negative evidence. | T07 |
| REQ-FIN-001 | Validation Report MUST be semantically validated before READY_FOR_PR can be accepted. | Label-only PASS with missing evidence fails; a complete report passes. | T05 |
| REQ-REL-001 | This activity MUST migrate from the 0.0.1 planning contract to the final 0.0.2 contract and self-validate before Gate G. | Final activity artifacts validate under 0.0.2 and migration evidence is recorded. | T08 |

Every requirement has exactly one implementation owner. Cross-cutting conformance tests may consume a requirement but do not become additional implementation owners.
