# Test Strategy — {{ACTIVITY_TITLE}}

## 1. Contract and principle

- Loop version: `0.0.1`.
- Task validation addresses the risk of the task.
- Branch/package validation addresses the complete activity package.
- Base-branch/ecosystem validation addresses integration with the surrounding product.
- The final package gate keeps every applicable assurance and adds lifecycle, manifest, containment, state and harness checks.
- A check is `PASS` only with fresh evidence from the exact candidate commit or worktree state. Missing evidence is not success.

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
| Deferred package gates | {{DEFERRED_PACKAGE_GATES}} |
| Deferred ecosystem gates | {{DEFERRED_ECOSYSTEM_GATES}} |
| Explicitly not authorized | {{NOT_AUTHORIZED}} |

## 4. Requirement and coverage matrix

Every approved requirement has at least one test ID and one evidence owner. Every matrix row declares `REQUIRED` or `N/A — because ...`; blank applicability is a failure.

| Requirement | Risk | Test ID | Level | Applicability | Expected evidence | Owner |
|---|---|---|---|---|---|---|
| {{REQ_ID}} | {{RISK}} | {{TEST_ID}} | {{LEVEL}} | {{REQUIRED_OR_NA}} | {{EVIDENCE}} | {{OWNER}} |

Coverage levels may include unit, integration, contract, end-to-end, activation, static analysis, migration, security, performance, manual inspection and ecosystem regression. The selected level must discriminate the stated risk.

## 5. Focused task gate

Before every test or gate, answer:

> **What new risk from this task does this command prove that was not already
> proved by an earlier task or reserved for the final package gate?**

If the answer is `none` or `just to be safe`, the execution is redundant and
must be removed or assigned to its proper package/ecosystem owner. Do not reduce
coverage: prove each risk once, at the smallest level that discriminates it.

The default task gate includes only applicable checks from this list:

1. Build or type-check the affected project.
2. Run every new or modified test.
3. Run existing tests directly related to changed behavior.
4. Validate changed test infrastructure.
5. Validate direct consumers and declared special boundaries.
6. Run the smallest applicable static, schema, manifest or lifecycle check.
7. Run `git diff --check` against the candidate.
8. Reconcile discovered, executed, passed, failed and skipped counts.
9. Record exit code, duration, warnings, timeouts, retries and flakes.

Do not automatically run broad or complete suites, global coverage, migrations, full frontend journeys, global topology or security scans, backup/restore exercises, benchmarks or repetitions. Run them when the risk matrix, package gate or ecosystem gate makes them applicable, and record why.

Use these execution shapes:

- **Task:** smallest test for the new risk, directly affected checks, focused
  review, atomic commit.
- **Correction:** detecting test, directly impacted checks, finding recheck.
  Repeat a broad audit only when contract, security boundary, architecture or
  scope changed.
- **Final package:** coverage once, complete suite or wrapper once, deep
  verifier and representative discrimination sensor.
- **Develop/ecosystem:** complete regression after integration on the
  authorized base.

Never execute a wrapper and then its child commands again as fresh evidence for
the same gate. Preflight/runtime facts remain valid for the session until the
environment, worktree or relevant HEAD changes. Requirement IDs provide
traceability; they are not a quota of tests.

## 6. Producers and artifact reuse

- Restore and build once per `RunId`, then reuse the exact output while the candidate commit and inputs remain unchanged.
- OpenAPI, coverage, generated manifests and similar outputs have one logical producer per `RunId`.
- Reused physical copies must be reconciled by hash and provenance.
- Aggregate wrappers must not execute the same producer again invisibly.
- Cache evidence never crosses commits, material worktree changes, toolchain changes or configuration changes.
- Heavy gates execute sequentially unless their isolation and resource budgets are proven.
- Resource-sensitive performance and discrimination sensors run once in a dedicated
  package lane, outside coverage instrumentation and broad suites that would distort
  their measurements. The aggregate package wrapper owns that lane and must not
  execute it again through a child suite.
- Every producer records invocation count, artifact location, hash, reuse consumers and result.

## 7. Coverage contract

For every applicable coverage metric, record covered units, valid total units, percentage and threshold. Repository-wide or package totals are weighted from raw counts:

`weighted percentage = sum(covered units) / sum(valid total units) * 100`

Never average percentages from different projects. Exclude invalid or non-instrumented totals explicitly; do not convert missing data into zero or success. Thresholds and exclusions must be approved before Gate G.

## 8. Discrimination sensor

Risk-applicable tests require a discrimination sensor that demonstrates the evidence can fail for the targeted defect. Allowed dispositions are:

- `PASS`: controlled mutation or equivalent sensor failed as expected and the real candidate passed afterward.
- `NOT_REQUIRED`: a documented risk argument shows why a sensor adds no useful discrimination.
- `NOT_MEASURED`: evidence was unavailable; this cannot satisfy a mandatory sensor.
- `FAIL`: the sensor did not distinguish the defect or was not restored cleanly.

Run mutations only in an isolated, recoverable worktree. Record before/after status, mutation, expected failure, observed failure and restoration proof.

## 9. Package Gate G

Gate G runs on the final candidate after task commits and corrective cycles. It requires:

- all approved requirements mapped to fresh evidence;
- final build and complete applicable package regression;
- final rebase or base synchronization when required by repository policy, followed by revalidation;
- discovered/executed/passed/failed/skipped reconciliation, with skip justifications;
- explicit timeouts, retries, flakes and warnings;
- weighted coverage and discrimination-sensor dispositions where applicable;
- producer invocation and artifact/hash reconciliation;
- code quality, scope, worktree containment and lifecycle/state validation;
- independent verification of the exact final commit;
- final PR readiness assessment;
- ecosystem regression status recorded separately from package status.

Package success must never be relabeled ecosystem success. When ecosystem execution requires external authority or a different base branch, record `PENDING_EXTERNAL_AUTHORITY` or `NOT_RUN — because ...`; do not declare global completion.

## 10. Gate sequence

1. Task-focused gate and independent task review.
2. Corrective loop, up to the approved cycle limit, for any failure.
3. Final candidate synchronization/rebase when required.
4. Final package regression and evidence-or-zero matrix.
5. Producer, artifact, count, coverage and sensor reconciliation.
6. Independent verifier review of the exact final SHA.
7. PR readiness decision.
8. Ecosystem regression on the authorized integration base.

## 11. Evidence retention

Store concise evidence under `04-validation/evidence/`. Evidence identifies `RunId`, command or structured action, exact scope, candidate SHA or dirty set, exit code, duration, counts, producer hashes, verifier and timestamp. External push, PR creation, deployment, production mutation and ecosystem writes require their own explicit authority.
