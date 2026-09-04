# Test Strategy — WetoLoop 0.0.2 Core Contracts & Validator Foundation

## 1. Contract

The activity starts on WetoLoop 0.0.1 and migrates to 0.0.2 in T08.

Core rule: **evidence is fresh; valid physical producers may be reused**.

A prior PASS never substitutes for verification of risk affected by the current task. Dependency state, build artifacts, generated artifacts and infrastructure may be reused when declared fingerprints remain valid.

## 2. Canonical affected surfaces

- Python validator scripts under `templates/engineering-loop/scripts/`;
- templates and JSON schemas under `templates/engineering-loop/`;
- repository-owned validator/conformance tests;
- final release metadata only in T08.

There is no Docker/database test infrastructure in this activity. Docker/database reuse is a contract concern only; no container is introduced merely to test the feature.

## 3. Warm focused task gate

For T01-T06, run only:

1. new/modified tests owned by the task;
2. existing tests directly affected by changed validator/shared parser behavior;
3. changed schema fixtures;
4. the smallest aggregate check necessary when orchestration changes;
5. `git diff --check`.

Do not run repository-wide conformance, coverage or complete package suite after each task.

T07 may run the complete conformance suite because that task owns the suite, but it does not run final code-coverage instrumentation.

## 4. Producer reuse

- `npm ci` runs only in a fresh environment or when dependency/lock inputs change.
- Python validator runtime has no project dependency restore.
- Python compile checks run when Python source changes and again in final package validation.
- Generated fixtures are reused when their declared inputs are unchanged.
- No Docker image, container or database producer is applicable to this activity.

Producer fingerprints include relevant toolchain, dependency, source/configuration or infrastructure inputs. Commit SHA anchors evidence but is not the sole producer-cache key.

## 5. Gate escalation

- known local validator change -> validator-focused tests;
- shared parser/schema change -> affected schemas plus direct validator consumers;
- aggregate orchestration change -> aggregate fixture suite;
- unknown impact -> bounded validator/conformance module;
- cross-cutting public contract change -> declared consumer suite;
- final candidate -> complete package gate.

## 6. Conformance and discrimination

Every mandatory 0.0.2 semantic rule requires at least one positive case and one negative case that fails for the intended diagnostic/risk. Required examples include readiness null-task semantics, stale evidence, invalid producer reuse, missing ImpactSet, invalid Harness interface and label-only Validation Report PASS.

## 7. Coverage

Code coverage instrumentation runs only in T08. Initial target: at least 90% for canonical Python validator modules using raw covered/valid totals. Semantic rule coverage is stricter: 100% of mandatory 0.0.2 semantic rules must map to positive and negative conformance evidence.

## 8. Cold final package gate — T08 only

Run once on the final candidate:

- clean dependency materialization when applicable;
- repository quality checks;
- all schema fixtures;
- all canonical validator tests;
- complete self-contained conformance suite;
- code coverage;
- aggregate validation of the migrated 0.0.2 activity;
- `git diff --check`;
- producer/count/retry/flake reconciliation;
- independent final review.

## 9. Test optimization candidates

Slow, flaky, overlapping or duplicate-risk tests are recorded in VALIDATION_REPORT/LEARNINGS with cost and proposed follow-up. They are not deleted as incidental cleanup.
