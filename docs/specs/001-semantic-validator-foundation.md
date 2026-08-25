# SPEC-001 — Semantic Validator Foundation

- Status: Ready for review
- Target: `0.0.2`
- Depends on: WetoLoop `0.0.1` public baseline
- Owners: WetoLoop maintainers

## 1. Problem

WetoLoop `0.0.1` contains useful semantic validation rules, JSON schemas and an aggregate validator, but they are not yet one coherent contract.

Current gaps include:

1. `validate_prd.py --plan` and `validate_techspec.py --plan` execute only the weak generic `validate_document()` path, bypassing their stronger semantic rules.
2. `validate_plan.py` does not aggregate dedicated validation for `REQUIREMENTS.md`, `TEST_STRATEGY.md`, `HARNESS.json` or `VALIDATION_REPORT.md`.
3. `task.schema.json`, `state.schema.json` and `harness.schema.json` describe contracts that are not fully enforced by the aggregate path.
4. Initial `STATE.md` may legitimately use `phase: readiness` with `task: null`, while the current state validator can reject that state when tasks are applicable.
5. The public repository does not yet have a self-contained validator conformance suite proving positive and negative behavior.
6. Validator behavior differs depending on whether a file is validated directly or through a plan.

A WetoLoop plan must not pass because the aggregate path is weaker than a standalone validator.

## 2. Goals

SPEC-001 SHALL establish one canonical semantic-validation model with these properties:

- the same semantic rules execute whether validation starts from a plan or a direct artifact entrypoint;
- all applicable authoritative artifacts have an explicit validator owner;
- aggregate validation is fail-closed;
- lifecycle-aware validation distinguishes an artifact that is required to exist from evidence that is only required at finalization;
- structural contract, semantic contract and cross-artifact consistency are independently testable;
- validator fixtures are repository-contained and require no real project activity;
- diagnostics are deterministic and machine-readable;
- current Python validation remains dependency-light for `0.0.2`.

## 3. Non-goals

This specification does not implement:

- test impact resolution or `ImpactSet` behavior;
- build/cache fingerprints;
- Docker/database lifecycle reuse;
- the npm CLI;
- runtime task execution;
- a replacement of the Python validators with TypeScript.

Those concerns may consume the contracts produced here but must not be mixed into this change.

## 4. Architectural decision

Validation is split into three layers.

### 4.1 Structural validation

Structural validation proves that machine-readable metadata has the expected shape, required fields, value domains and safe paths.

For `0.0.2`, Python code remains the executable validator. JSON Schemas remain the public interoperable description of the same contract. The implementation SHALL keep the Python contract and JSON Schema behavior aligned through conformance fixtures.

No new mandatory Python package dependency is introduced in this milestone.

### 4.2 Artifact semantic validation

Artifact semantic validation proves domain-specific meaning inside one artifact, for example:

- requirement statements are precise and traceable;
- TechSpec requirements are mapped to design and test treatment;
- task front matter satisfies task lifecycle rules;
- Test Strategy defines focused and final gates coherently;
- Harness commands are safe, bounded and reference declared tokens;
- Validation Report contains reconciled final evidence when final evidence is due.

### 4.3 Cross-artifact validation

Cross-artifact validation proves relationships such as:

- approved requirements have exactly one task owner;
- tasks reference known requirements and tests;
- `STATE.md` agrees with task files;
- lifecycle directory agrees with PLAN and STATE;
- final evidence belongs to the exact candidate and Run ID;
- declared artifact paths remain contained inside the activity root.

## 5. Canonical validator entrypoints

The public validator set SHALL become:

```text
validate_manifest.py
validate_prd.py
validate_requirements.py
validate_techspec.py
validate_tasks.py
validate_test_strategy.py
validate_harness.py
validate_traceability.py
validate_execution_state.py
validate_validation_report.py
validate_lifecycle.py
validate_plan.py
```

`validate_plan.py` is the aggregate entrypoint. Individual validators remain usable for focused authoring feedback.

## 6. Single-source semantic rule behavior

Direct-file mode and `--plan` mode SHALL call the same semantic rule functions.

The implementation MUST NOT maintain two independent versions of PRD, TechSpec, task or other semantic rules.

Recommended internal organization:

```text
scripts/
├── loop_common.py          # parsing, safe paths, manifest/context loading, CLI result contract
├── loop_checks.py          # cross-artifact contracts and common plan-root resolution
├── semantic_checks.py      # artifact semantic rule functions
└── validate_*.py           # thin CLI adapters
```

Equivalent organization is acceptable if it preserves a single rule source.

The existing strong standalone PRD and TechSpec checks SHALL be extracted or called from the shared semantic layer instead of being bypassed by `--plan`.

## 7. Validation context and lifecycle maturity

`required` applicability means an artifact is part of the activity contract. It does not mean every final-only evidence field must be complete during planning.

The aggregate validator SHALL build a `ValidationContext` containing at minimum:

```text
plan_root
loop_version
plan_status
plan_lifecycle
current_phase
current_task
current_status
applicability
```

Each validator SHALL distinguish the following maturity levels:

1. **structural** — artifact must parse and satisfy safe structural rules;
2. **readiness** — fields required before implementation must be complete;
3. **execution** — active-task/state/evidence consistency must hold;
4. **final** — package-gate evidence, final report and PR-readiness fields must be complete.

The implementation MAY infer maturity from existing PLAN/STATE fields rather than add a new persisted field in this milestone.

A validator MUST NOT require final package evidence before the activity reaches final validation.

## 8. Required semantic validators

### 8.1 Requirements

`validate_requirements.py` SHALL own `REQUIREMENTS.md` semantics that are currently coupled to PRD validation.

Minimum rules:

- Requirement Catalog exists and has the canonical columns.
- Each Requirement ID is unique and canonical.
- Requirement statement contains `SHALL` and is meaningfully precise.
- Priority and Source are present.
- Pattern is one of the supported requirement patterns.
- Assumptions/Open Questions rows are complete.
- Implicit Requirement Closure contains all required dimensions or explicit `N/A because` dispositions.
- Requirement Traceability covers every approved requirement.
- unresolved placeholders are rejected when the artifact is due for readiness.

`validate_prd.py` SHALL validate product/problem semantics and SHALL NOT remain the owner of the canonical Requirement Catalog rules.

### 8.2 PRD

Minimum plan-mode behavior SHALL include the same semantic depth as direct mode, including required sections, unresolved ambiguity handling and meaningful success criteria.

### 8.3 TechSpec

Minimum plan-mode behavior SHALL include the existing strong checks for:

- architecture/design sections;
- requirement-to-design mapping;
- reuse/evolve/create/prohibited decisions;
- risk records;
- Test Treatment applicability and gate ownership;
- producer/reuse treatment where applicable;
- unresolved placeholders.

### 8.4 Tasks

Task validation SHALL enforce both structural task front matter and semantic lifecycle rules.

Minimum rules include:

- canonical ID;
- known, acyclic dependencies;
- known requirement references;
- valid status transitions represented by required fields;
- completed task requires commit SHA, evidence and independent reviewer;
- blocked task requires structured blocker;
- cancelled/superseded task requires terminal reason.

SPEC-002 extends this contract with task verification policy.

### 8.5 Test Strategy

`validate_test_strategy.py` SHALL verify that `TEST_STRATEGY.md` contains at minimum:

- canonical test scope;
- requirement/risk coverage matrix;
- focused task gate policy;
- producer/artifact reuse policy;
- coverage contract;
- final Package Gate G definition;
- evidence retention policy.

It SHALL detect contradictory policies such as simultaneously requiring fingerprint-based reuse and declaring all build/cache artifacts invalid solely because the commit changed.

### 8.6 Harness

`validate_harness.py` SHALL validate `HARNESS.json` as an executable safety contract.

Minimum rules:

- valid JSON object;
- supported schema/loop version;
- unique command IDs;
- command executable and args are structured, not shell-concatenated strings;
- declared tokens are the only tokens referenced by commands;
- path/token resolution is bounded to declared authorities;
- mutation class is recognized;
- timeouts are positive and bounded;
- `useShell` remains false for default safe profiles unless a future explicit contract authorizes otherwise;
- lifecycle mutation settings are fail-closed.

An empty `{}` Harness MUST fail when Harness is applicable.

### 8.7 Execution State

The initial readiness state SHALL be valid when:

```yaml
current:
  phase: readiness
  task: null
  status: pending
```

Before task execution begins, `current.task: null` is legal. Once state enters task execution, the referenced task and status must agree with task front matter.

The state validator SHALL also preserve completed-task reconciliation, producer uniqueness and fresh-evidence checks.

### 8.8 Validation Report

`validate_validation_report.py` SHALL be lifecycle-aware.

Before final validation it SHALL only require structural presence appropriate to the current maturity.

At final maturity it SHALL verify at minimum:

- every completed task has a final focused-gate disposition;
- requirement evidence is present and non-placeholder;
- package execution counts reconcile;
- failures, skips, retries, flakes and warnings are explicit;
- producer invocation counts reconcile;
- coverage values use raw weighted totals rather than averaged percentages;
- final verdict fields are present and internally consistent;
- `READY_FOR_PR: YES` is impossible when any mandatory final gate failed or is missing.

## 9. Aggregate validator behavior

`validate_plan.py` SHALL:

1. load PLAN and ValidationContext once;
2. resolve applicable validators deterministically;
3. run structural + semantic + cross-artifact checks appropriate to maturity;
4. never silently skip a required validator because no implementation exists;
5. emit one canonical JSON result;
6. include every skipped validator with an explicit reason;
7. preserve the current exit-code contract:
   - `0` PASS
   - `1` FAIL
   - `2` ERROR
   - `3` UNSAFE

Required aggregate ownership after this spec:

| Artifact/contract | Validator owner |
|---|---|
| PLAN/manifest | `validate_manifest.py` |
| PRD | `validate_prd.py` |
| Requirements | `validate_requirements.py` |
| TechSpec | `validate_techspec.py` |
| Tasks/task graph | `validate_tasks.py` |
| Test Strategy | `validate_test_strategy.py` |
| Harness | `validate_harness.py` |
| Requirement/task mapping | `validate_traceability.py` |
| STATE/evidence | `validate_execution_state.py` |
| Validation Report | `validate_validation_report.py` |
| lifecycle/location | `validate_lifecycle.py` |

## 10. Diagnostic contract

Plan-mode validators SHALL emit exactly one JSON object to stdout.

Each diagnostic SHALL have stable fields:

```json
{
  "code": "STABLE_MACHINE_CODE",
  "message": "Human-readable explanation",
  "path": "relative/or/absolute/path",
  "pointer": "optional logical section or field"
}
```

Diagnostic ordering SHALL be deterministic so identical invalid input produces identical output ordering.

Human-friendly direct mode MAY print additional summaries, but its pass/fail semantics MUST match plan mode.

## 11. Conformance suite

The repository SHALL contain self-contained test activities created entirely from repository fixtures or temporary directories.

No test may reference a real `_in_progress` activity or an external repository path.

Required fixture classes:

- minimum valid planning activity;
- valid readiness activity with `current.task: null`;
- valid active task activity;
- valid completed/final activity;
- malformed PRD;
- malformed requirements;
- malformed TechSpec;
- invalid task dependency cycle;
- completed task without evidence;
- invalid/empty Harness;
- contradictory Test Strategy;
- final Validation Report with unreconciled counts;
- unsafe path escape.

For every validator, at least one positive and one negative conformance case SHALL exist.

The aggregate validator SHALL also have end-to-end positive and negative tests.

## 12. Files expected to change

Expected additions:

```text
templates/engineering-loop/scripts/validate_requirements.py
templates/engineering-loop/scripts/validate_test_strategy.py
templates/engineering-loop/scripts/validate_harness.py
templates/engineering-loop/scripts/validate_validation_report.py
templates/engineering-loop/scripts/semantic_checks.py   # or equivalent shared module
tests/validator-conformance/...                         # exact location may be adapted
```

Expected modifications:

```text
templates/engineering-loop/scripts/validate_plan.py
templates/engineering-loop/scripts/validate_prd.py
templates/engineering-loop/scripts/validate_techspec.py
templates/engineering-loop/scripts/validate_tasks.py
templates/engineering-loop/scripts/validate_execution_state.py
templates/engineering-loop/scripts/loop_checks.py
templates/engineering-loop/schemas/*.schema.json
templates/engineering-loop/README.md
```

Schemas SHALL be changed only where the semantic contract requires it; this spec is not permission for unrelated schema redesign.

## 13. Compatibility

WetoLoop is pre-1.0, but this change SHOULD preserve existing direct validator entrypoints where reasonable.

The authoritative behavior after implementation is the `0.0.2` aggregate plan validation contract. Where old direct behavior conflicts with that contract, the direct entrypoint SHALL be aligned rather than preserving inconsistency.

## 14. Acceptance criteria

SPEC-001 is complete when all of the following are true:

- [ ] `validate_prd.py --plan` runs the strong PRD semantic rules.
- [ ] `validate_techspec.py --plan` runs the strong TechSpec semantic rules.
- [ ] dedicated Requirements, Test Strategy, Harness and Validation Report validators exist.
- [ ] `validate_plan.py` invokes every applicable validator at the correct maturity.
- [ ] `{}` fails Harness validation when Harness is applicable.
- [ ] initial readiness STATE with `task: null` passes.
- [ ] an active-task STATE with missing/unknown task fails.
- [ ] JSON schemas and executable structural rules have positive/negative parity fixtures.
- [ ] no conformance test depends on a real user activity.
- [ ] every validator has at least one positive and one negative test.
- [ ] aggregate validation has end-to-end PASS and FAIL cases.
- [ ] validator stdout/exit behavior is deterministic and documented.
- [ ] repository quality workflow runs the new conformance suite.

## 15. Implementation order

Recommended implementation slices:

1. shared ValidationContext and semantic rule extraction;
2. PRD/Requirements/TechSpec parity;
3. Task/STATE readiness correction;
4. Test Strategy validator;
5. Harness validator;
6. Validation Report lifecycle validator;
7. aggregate wiring;
8. self-contained conformance suite;
9. schema parity and documentation cleanup.

Each slice should run only the validator/conformance tests it affects. The full validator conformance suite and repository quality gate run once on the final candidate.
