# Validation Report — {{ACTIVITY_TITLE}}

## 1. Header

| Field | Value |
|---|---|
| Loop version | `0.0.2` |
| Date | {{DATE}} |
| Requirements | {{REQUIREMENTS_VERSION}} |
| Branch / candidate HEAD | {{BRANCH}} / {{HEAD_SHA}} |
| Base / diff | {{BASE_SHA}} / {{DIFF_RANGE}} |
| Candidate Run ID | {{RUN_ID}} |
| Configuration | {{CONFIGURATION}} |
| Environment | {{ENVIRONMENT}} |
| Independent verifier | {{INDEPENDENT_VERIFIER}} |
| Gate G verdict | {{GATE_G_VERDICT}} |
| Gate H verdict | {{GATE_H_VERDICT}} |

## 2. Task completion

| Task | Commit | Focused gate | Review | Evidence | Result |
|---|---|---|---|---|---|
| {{TASK_ID}} | {{COMMIT_SHA}} | {{GATE_RESULT}} | {{REVIEW_RESULT}} | {{EVIDENCE_PATH}} | {{RESULT}} |

## 3. Requirement evidence

Evidence uses `file:line + assertion` or an equally precise machine artifact. A requirement without evidence is uncovered.

| Requirement | Test/evidence ID | Evidence | Run ID | Result |
|---|---|---|---|---|
| {{REQ_ID}} | {{TEST_ID}} | {{FILE_LINE_AND_ASSERTION}} | {{RUN_ID}} | {{RESULT}} |

## 4. Candidate Gate G execution

Gate G validates the final activity candidate before merge. It is intentionally bounded by the accumulated `ImpactSet` and changed mandatory boundaries; it is not the default owner of repository-wide full regression when Gate H is guaranteed.

```text
Candidate SHA: {{HEAD_SHA}}
Command(s): {{GATE_G_COMMANDS}}
Scope / accumulated ImpactSet: {{GATE_G_SCOPE}}
Exit code: {{GATE_G_EXIT_CODE}}
Duration: {{GATE_G_DURATION}}
Discovered: {{GATE_G_DISCOVERED}}
Executed: {{GATE_G_EXECUTED}}
Passed: {{GATE_G_PASSED}}
Failed: {{GATE_G_FAILED}}
Skipped + justification: {{GATE_G_SKIPPED}}
Affected migrations executed: {{GATE_G_MIGRATIONS}}
Timeouts: {{GATE_G_TIMEOUTS}}
Retries: {{GATE_G_RETRIES}}
Flakes: {{GATE_G_FLAKES}}
Warnings: {{GATE_G_WARNINGS}}
```

Full repository regression in Gate G: `{{YES_NO}}`.

If `YES`, mandatory reason: {{PREMERGE_FULL_REGRESSION_REASON}}.

Allowed reasons are limited to absence of a guaranteed Gate H, mandatory repository merge policy without an equivalent post-merge gate, repository-wide runner/build/infrastructure risk that cannot be bounded, or explicit owner-authorized release exception.

## 5. Producers and artifacts

| Producer | Gate | Expected executions | Actual executions | Reused by | Artifact | Hash | Result |
|---|---|---:|---:|---|---|---|---|
| {{PRODUCER}} | {{G_OR_H}} | {{EXPECTED}} | {{ACTUAL}} | {{CONSUMERS}} | {{ARTIFACT_PATH}} | {{HASH}} | {{RESULT}} |

Duplicate producer assessment: {{DUPLICATE_PRODUCER_ASSESSMENT}}.

## 6. Coverage

| Metric / project | Covered units | Valid total units | Percentage | Threshold | Gate | Result |
|---|---:|---:|---:|---:|---|---|
| {{METRIC}} | {{COVERED}} | {{VALID_TOTAL}} | {{PERCENTAGE}} | {{THRESHOLD}} | {{GATE}} | {{RESULT}} |

Weighted totals are calculated from raw counts, never by averaging project percentages.

```text
Weighted covered units: {{WEIGHTED_COVERED}}
Weighted valid total units: {{WEIGHTED_VALID_TOTAL}}
Weighted percentage: {{WEIGHTED_PERCENTAGE}}
Excluded/invalid totals + justification: {{COVERAGE_EXCLUSIONS}}
```

Gate H must not rerun the full integrated suite solely to recreate equivalent candidate coverage. If coverage is repeated after merge, record the independent Gate H reason or invalidated fingerprint here: {{GATE_H_COVERAGE_REASON}}.

## 7. Discrimination sensors — Gate G only

Disposition: `{{PASS_NOT_REQUIRED_NOT_MEASURED_FAIL}}`

Rationale: {{SENSOR_RATIONALE}}

| Targeted risk | Controlled mutation/sensor | Expected failure | Observed failure | Real candidate result | Evidence |
|---|---|---|---|---|---|
| {{RISK}} | {{MUTATION}} | {{EXPECTED}} | {{OBSERVED}} | {{REAL_RESULT}} | {{EVIDENCE}} |

```text
Sensor worktree before: {{SENSOR_WORKTREE_BEFORE}}
Sensor worktree after: {{SENSOR_WORKTREE_AFTER}}
Restoration proof: {{RESTORATION_PROOF}}
```

Sensors are not repeated in Gate H unless the integration invalidated the detecting evidence or repository policy explicitly requires it.

## 8. Candidate code quality and scope

- [ ] Diff contains only approved activity scope.
- [ ] Main worktree and unrelated repositories remain unchanged.
- [ ] `git diff --check` passes.
- [ ] Required build/type-check/lint/static checks pass.
- [ ] Manifest, schemas, lifecycle location and `STATE.md` agree.
- [ ] No unresolved placeholders, silent skips or unapproved fallbacks remain.
- [ ] No external mutation occurred without authority.
- [ ] Final rebase/synchronization requirement is satisfied or explicitly not applicable.
- [ ] Independent verifier audited the exact candidate SHA.
- [ ] PR metadata and reviewer handoff are ready.

## 9. Candidate findings

| Severity | Finding | Owner | Disposition | Evidence |
|---|---|---|---|---|
| {{SEVERITY}} | {{FINDING}} | {{OWNER}} | {{DISPOSITION}} | {{EVIDENCE}} |

## 10. Develop Integration Gate H

Gate H runs after merge on the exact authorized integration commit and owns the complete integrated regression.

| Field | Value |
|---|---|
| Integration branch | {{INTEGRATION_BRANCH}} |
| Integrated SHA | {{INTEGRATED_SHA}} |
| Run ID | {{GATE_H_RUN_ID}} |
| Authority | {{GATE_H_AUTHORITY}} |
| Full backend/repository regression | {{RESULT}} |
| Cross-module/ecosystem regression | {{RESULT}} |
| Global migration/integration checks | {{RESULT}} |
| Merge-interaction findings | {{RESULT}} |
| Gate H verdict | {{PASS_PENDING_FAIL}} |

```text
Gate H command/wrapper: {{GATE_H_COMMAND}}
Discovered: {{GATE_H_DISCOVERED}}
Executed: {{GATE_H_EXECUTED}}
Passed: {{GATE_H_PASSED}}
Failed: {{GATE_H_FAILED}}
Skipped + justification: {{GATE_H_SKIPPED}}
Duration: {{GATE_H_DURATION}}
Retries/flakes/warnings: {{GATE_H_RETRIES_FLAKES_WARNINGS}}
```

Gate H must not be decomposed into child commands that rerun the same tests as separate fresh evidence.

## 11. Final verdicts

```text
GATE_G_CANDIDATE: {{PASS_BLOCK_FAIL}}
REQUIREMENTS_COVERED: {{RESULT}}
CANDIDATE_IMPACTSET_REGRESSION: {{RESULT}}
AFFECTED_MIGRATIONS: {{RESULT}}
COVERAGE: {{RESULT}}
DISCRIMINATION_SENSORS: {{RESULT}}
INDEPENDENT_FINAL_REVIEW: {{RESULT}}
READY_FOR_PR_OR_MERGE: {{YES_NO}}

GATE_H_DEVELOP_INTEGRATION: {{PASS_PENDING_FAIL}}
FULL_INTEGRATED_REGRESSION: {{RESULT}}
ECOSYSTEM_REGRESSION: {{RESULT}}
INTEGRATED_DEVELOP_HEALTH: {{RESULT}}
```

Gate G PASS means **merge-ready candidate**. It does not mean the complete integrated product has passed. Global/integrated success is claimed only after Gate H passes on the merged integration SHA.

Blocking rationale or residual risk: {{RATIONALE}}.
