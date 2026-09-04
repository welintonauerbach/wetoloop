# Test Strategy — {{ACTIVITY_TITLE}}

## 1. Contract and principle

- Loop version: `0.0.2`.
- Task validation addresses the risk introduced by the current task.
- Candidate validation addresses the accumulated `ImpactSet` and activity-specific boundaries before merge.
- Develop integration validation addresses full-system regression after the candidate is merged into the authorized integration branch.
- The same broad regression must not run once on the feature branch and again on `develop` merely to be safe.
- A check is `PASS` only with fresh evidence from the exact candidate commit, worktree state, or integrated `develop` commit that owns that gate.
- Missing evidence is not success.

## 2. Provenance

| Input | Version or SHA | Owner | Purpose |
|---|---|---|---|
| Approved requirements | {{REQUIREMENTS_VERSION}} | {{OWNER}} | Acceptance contract |
| Technical specification | {{TECHSPEC_VERSION}} | {{OWNER}} | Design and risk boundaries |
| Task graph | {{TASK_GRAPH_VERSION}} | {{OWNER}} | Ordered verification units |
| Repository base | {{BASE_SHA}} | {{OWNER}} | Diff and ecosystem baseline |
| Toolchain | {{TOOLCHAIN_VERSION}} | {{OWNER}} | Reproducible execution |

## 3. Canonical test scope

Record the following before implementation. Use `N/A — because ...` only when the reason is explicit and reviewable.

| Scope field | Value |
|---|---|
| Projects affected | {{PROJECTS_AFFECTED}} |
| Production components changed | {{PRODUCTION_COMPONENTS}} |
| Test infrastructure changed | {{TEST_INFRASTRUCTURE}} |
| New or modified tests | {{NEW_OR_MODIFIED_TESTS}} |
| Existing tests directly affected | {{DIRECTLY_AFFECTED_TESTS}} |
| Direct consumers | {{DIRECT_CONSUMERS}} |
| Special boundaries | {{SPECIAL_BOUNDARIES}} |
| Runtime or configuration | {{RUNTIME_CONFIGURATION}} |
| Producer and artifact reuse plan | {{PRODUCER_REUSE_PLAN}} |
| Candidate-gate scope | {{CANDIDATE_GATE_SCOPE}} |
| Develop integration gate | {{DEVELOP_GATE_SCOPE}} |
| Explicitly not authorized | {{NOT_AUTHORIZED}} |

## 4. Requirement and coverage matrix

Every approved requirement has at least one evidence owner. Requirement IDs are traceability, not a quota of tests. Multiple requirements may be proved by one high-value scenario when they share the same defect path.

| Requirement | Risk | Test / evidence ID | Level | Applicability | Expected evidence | Owner |
|---|---|---|---|---|---|---|
| {{REQ_ID}} | {{RISK}} | {{TEST_ID}} | {{LEVEL}} | {{REQUIRED_OR_NA}} | {{EVIDENCE}} | {{OWNER}} |

Coverage levels may include unit, integration, contract, end-to-end, activation, static analysis, migration, security, performance, manual inspection, candidate gate and develop integration regression. Select the smallest level that discriminates the stated risk.

## 5. Warm focused task gate

Before every command, answer:

> **What new risk from this task does this command prove that was not already proved by an earlier task, reserved for the candidate gate, or owned by the develop integration gate?**

If the answer is `none` or `just to be safe`, the execution is redundant and must be removed or assigned to its proper owner.

The default task gate includes only applicable checks:

1. Build or type-check the affected project when the current `BuildKey` is invalid.
2. Run every new or modified valuable test.
3. Run existing tests directly related to changed behavior.
4. Validate changed test infrastructure.
5. Validate direct consumers and declared special boundaries.
6. Run the smallest applicable static, schema, manifest or lifecycle check.
7. Run `git diff --check` against the candidate when relevant.
8. Reconcile discovered, executed, passed, failed and skipped counts.
9. Record exit code, duration, warnings, timeouts, retries and flakes.

Do not automatically run broad suites, repository-wide coverage, all migrations, full frontend journeys, global topology/security scans, backup/restore exercises, benchmarks or repetitions.

Execution shapes:

- **Task:** smallest detecting test + directly affected checks + focused review + atomic commit.
- **Correction:** detecting test + directly impacted checks + finding recheck. Repeat a broad audit only when the contract, security boundary, architecture or scope changed.
- **Candidate Gate:** accumulated `ImpactSet` regression + changed mandatory boundaries + affected migrations + coverage required for changed/owned code + representative discrimination sensors + evidence reconciliation + independent verifier.
- **Develop Integration Gate:** one complete integrated regression on the merged base branch, including cross-module/ecosystem checks applicable to that repository, preceded by delta classification and fingerprint reconciliation for auxiliary producers.

Never execute a wrapper and then its child commands again as fresh evidence for the same gate. Preflight/runtime facts remain valid until environment, worktree, candidate HEAD or relevant producer inputs change.

## 6. Candidate Gate G — pre-merge

Gate G answers:

> **Is this activity candidate correct, sufficiently evidenced, and safe to merge?**

It runs on the exact final candidate after task commits and corrective cycles. By default it requires:

- all approved requirements mapped to fresh evidence;
- final build of the affected candidate graph when `BuildKey` requires it;
- regression over the accumulated `ImpactSet`, direct/transitive consumers and changed mandatory boundaries;
- only migrations/schema upgrade paths affected by the activity;
- coverage once for new/changed package code when required by the approved thresholds;
- representative discrimination sensors once, when applicable;
- producer invocation/artifact/hash reconciliation;
- code quality, scope, worktree containment and lifecycle/state validation;
- independent verification of the exact final candidate commit;
- final PR readiness assessment;
- explicit declaration that full integrated regression is owned by Gate H on `develop`.

### Gate G must not duplicate Gate H

When a mandatory Develop Integration Gate exists and will run immediately after merge, Gate G **must not** run the complete repository/backend/ecosystem suite merely to duplicate Gate H.

A pre-merge full regression is allowed only when one of these conditions is explicitly documented:

1. the repository has no guaranteed Develop Integration Gate;
2. merge policy requires full regression before merge and no equivalent post-merge gate exists;
3. the activity changes the test runner, global build graph, repository-wide infrastructure or another boundary whose risk cannot be discriminated by a bounded accumulated `ImpactSet`;
4. the owner explicitly authorizes an exceptional duplicate run for a documented release risk.

If none applies, full repository regression belongs only to Gate H.

## 7. Develop Integration Gate H — post-merge

Gate H answers:

> **After integrating this candidate with the current base branch, does the complete product/repository still pass?**

### Mandatory Gate H preflight — Delta Classification + Fingerprint Reconciliation

Before any expensive Gate H producer:

1. record the exact Gate G candidate SHA and exact integrated branch SHA;
2. compare `candidate..integrated`;
3. classify every post-candidate delta into:
   - production source;
   - backend/tests;
   - build/project/restore inputs;
   - schema/migrations;
   - OpenAPI producer inputs;
   - HTTP/topology/security inputs;
   - frontend/consumer inputs;
   - documentation/governance only;
4. reconcile applicable producer fingerprints, including `RestoreKey`, `BuildKey`, relevant `SchemaKey`s, `OpenApiKey`, `HttpSecurityKey`, `FrontendConsumerKey`, and generated-artifact keys;
5. record one action for every auxiliary producer: `REUSE`, `RERUN`, or `N/A`, including artifact hash/provenance when reused.

The full integrated repository/backend regression remains fresh mandatory Gate H evidence. Fingerprint reconciliation only governs auxiliary producer/wrapper repetition.

Gate H runs once on the exact integrated `develop` (or repository-designated integration branch) commit and owns:

- complete backend/repository non-migration regression;
- complete ecosystem/cross-module regression applicable to the repository;
- complete migration/integration verification when required by repository policy;
- verification of merge interactions and concurrent upstream changes.

Global build/OpenAPI/HTTP-security/frontend/static producers run only when their reconciled fingerprint or explicit repository Gate H policy requires fresh execution.

### Gate H anti-duplication rules

Gate H MUST NOT:

- execute a wrapper containing the full backend/repository regression and then execute the same child lane separately;
- rerun focused package/module suites already subsumed by the complete non-migration lane;
- rerun migrations module-by-module after the complete migration/integration lane;
- regenerate OpenAPI when `OpenApiKey` remains valid and accepted artifact hash/provenance remains reusable;
- rerun a complete HTTP/security/topology wrapper when `HttpSecurityKey` remains valid; when only a bounded sub-gate is invalidated and targeted execution is supported, run only that sub-gate;
- run full frontend `verify`, coverage, lint, typecheck or build solely because Gate H exists when `FrontendConsumerKey` remains valid and frontend is outside activity scope; when only a consumed API contract changed, prefer the smallest repository-required consumer-contract check;
- rerun restore/build auxiliary producers when their fingerprint is unchanged and a valid exact producer output is available;
- repeat candidate discrimination sensors, candidate mutation experiments, independent candidate verifier review or candidate-only coverage without an invalidated evidence fingerprint or explicit repository Gate H obligation.

Reused auxiliary producers must be recorded as evidence with prior PASS/artifact identity, fingerprint and hash/provenance. A skipped expensive command is valid only when reuse is explicit and reviewable.

A Gate H failure is an integration failure. It must trigger correction/rollback policy and cannot be hidden by the earlier Gate G PASS.

## 8. Producers and artifact reuse

- Restore and build once per valid input fingerprint, then reuse exact outputs while candidate and inputs remain unchanged.
- OpenAPI, coverage, generated manifests and similar outputs have one logical producer per applicable gate/RunId.
- Reused physical copies must be reconciled by hash and provenance.
- Aggregate wrappers must not execute the same producer again invisibly.
- Cache evidence never crosses material candidate changes, toolchain changes, relevant configuration changes or integrated-branch changes.
- Heavy gates execute sequentially unless isolation and resource budgets are proven.
- Resource-sensitive performance and discrimination sensors run once in a dedicated candidate lane, outside coverage instrumentation and broad suites that would distort their measurements.
- Every producer records invocation count, artifact location, hash, reuse consumers and result.
- Gate H auxiliary reuse is decided only after candidate-to-integrated delta classification and fingerprint reconciliation.

## 9. Coverage contract

For every applicable coverage metric, record covered units, valid total units, percentage and threshold. Repository/package totals are weighted from raw counts:

`weighted percentage = sum(covered units) / sum(valid total units) * 100`

Never average percentages from different projects. Exclude invalid or non-instrumented totals explicitly; do not convert missing data into zero or success.

Coverage is normally a Gate G producer for changed/owned code. Gate H must not run the complete regression a second time only to regenerate equivalent coverage. Collect Gate H coverage only when it is independently required by repository policy or the integration invalidated the Gate G coverage evidence.

## 10. Discrimination sensors

A discrimination sensor demonstrates that important evidence can actually fail for the targeted defect. Allowed dispositions:

- `PASS`: controlled mutation/equivalent sensor failed as expected and the real candidate passed afterward.
- `NOT_REQUIRED`: documented risk argument shows why a sensor adds no useful discrimination.
- `NOT_MEASURED`: evidence unavailable; cannot satisfy a mandatory sensor.
- `FAIL`: sensor did not distinguish the defect or was not restored cleanly.

Run sensors only in an isolated, recoverable candidate worktree. Record before/after status, mutation, expected failure, observed failure and restoration proof.

Sensors belong to Gate G and are **not repeated in Gate H** unless the integrated change invalidates the detecting test or the sensor itself is explicitly part of repository integration policy.

## 11. Gate sequence

1. Warm task-focused gates and task reviews.
2. Corrective loops for task/finding failures.
3. Final candidate synchronization/rebase when required.
4. Gate G: accumulated ImpactSet, affected migrations/boundaries, required coverage, sensors and evidence reconciliation.
5. Independent verifier review of the exact candidate SHA.
6. PR readiness decision.
7. Merge under repository authority.
8. Gate H preflight: candidate-to-integrated delta classification and fingerprint reconciliation.
9. Gate H on the exact integrated `develop` commit: full regression once + only invalidated auxiliary producers.
10. Integration verdict and correction/rollback when necessary.

## 12. Evidence retention

Store concise evidence under `04-validation/evidence/`. Evidence identifies gate (`Task`, `G`, or `H`), `RunId`, command/action, exact scope, candidate or integrated SHA, exit code, duration, counts, producer hashes, verifier when applicable, and timestamp.

Gate H evidence additionally records candidate SHA, integrated SHA, delta categories, reconciled fingerprints, and explicit `REUSE/RERUN/N/A` decisions for auxiliary producers.

Package/candidate success must never be relabeled integrated ecosystem success. Gate G may be `PASS` while Gate H remains `PENDING`; the activity is merge-ready, not globally integrated, until Gate H passes.
