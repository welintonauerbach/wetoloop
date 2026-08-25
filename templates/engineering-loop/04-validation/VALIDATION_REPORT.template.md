# Validation Report — {{ACTIVITY_TITLE}}

## 1. Header

| Field | Value |
|---|---|
| Loop version | `0.0.1` |
| Date | {{DATE}} |
| Requirements | {{REQUIREMENTS_VERSION}} |
| Branch / HEAD | {{BRANCH}} / {{HEAD_SHA}} |
| Base / diff | {{BASE_SHA}} / {{DIFF_RANGE}} |
| Run ID | {{RUN_ID}} |
| Configuration | {{CONFIGURATION}} |
| Environment | {{ENVIRONMENT}} |
| Verifier | {{INDEPENDENT_VERIFIER}} |
| Verdict | {{VERDICT}} |

## 2. Task completion

| Task | Commit | Focused gate | Independent review | Evidence | Result |
|---|---|---|---|---|---|
| {{TASK_ID}} | {{COMMIT_SHA}} | {{GATE_RESULT}} | {{REVIEW_RESULT}} | {{EVIDENCE_PATH}} | {{RESULT}} |

## 3. Requirement evidence

Evidence uses `file:line + assertion` or an equally precise machine artifact. A requirement without evidence is uncovered.

| Requirement | Test ID | Evidence | Run ID | Result |
|---|---|---|---|---|
| {{REQ_ID}} | {{TEST_ID}} | {{FILE_LINE_AND_ASSERTION}} | {{RUN_ID}} | {{RESULT}} |

## 4. Package gate execution

```text
Command(s): {{COMMANDS}}
Filter/scope: {{FILTER_SCOPE}}
Exit code: {{EXIT_CODE}}
Duration: {{DURATION}}
Unique test methods planned: {{PLANNED_TESTS}}
Discovered: {{DISCOVERED}}
Executed: {{EXECUTED}}
Passed: {{PASSED}}
Failed: {{FAILED}}
Skipped + justification: {{SKIPPED_AND_JUSTIFICATION}}
Timeouts: {{TIMEOUTS}}
Retries: {{RETRIES}}
Flakes: {{FLAKES}}
Warnings: {{WARNINGS}}
Test count before: {{TEST_COUNT_BEFORE}}
Test count after: {{TEST_COUNT_AFTER}}
```

Reconciliation assertion: `discovered = executed + justified_not_executed`; `executed = passed + failed + skipped_as_reported_by_runner`. Explain any runner-specific counting difference here: {{COUNT_RECONCILIATION}}.

## 5. Producers and artifacts

| Producer | Expected executions | Actual executions | Reused by | Artifact | Hash | Justification | Result |
|---|---:|---:|---|---|---|---|---|
| {{PRODUCER}} | {{EXPECTED}} | {{ACTUAL}} | {{CONSUMERS}} | {{ARTIFACT_PATH}} | {{HASH}} | {{JUSTIFICATION}} | {{RESULT}} |

Duplicate producer assessment: {{DUPLICATE_PRODUCER_ASSESSMENT}}.

## 6. Coverage

| Metric / project | Covered units | Valid total units | Percentage | Threshold | Result |
|---|---:|---:|---:|---:|---|
| {{METRIC}} | {{COVERED}} | {{VALID_TOTAL}} | {{PERCENTAGE}} | {{THRESHOLD}} | {{RESULT}} |

Weighted totals are calculated from raw counts, never by averaging project percentages:

```text
Weighted covered units: {{WEIGHTED_COVERED}}
Weighted valid total units: {{WEIGHTED_VALID_TOTAL}}
Weighted percentage: {{WEIGHTED_PERCENTAGE}}
Excluded or invalid totals + justification: {{COVERAGE_EXCLUSIONS}}
```

## 7. Discrimination sensor

Disposition: `{{PASS_NOT_REQUIRED_NOT_MEASURED_FAIL}}`

Rationale: {{SENSOR_RATIONALE}}

| Targeted risk | Controlled mutation or sensor | Expected failure | Observed failure | Real candidate result | Evidence |
|---|---|---|---|---|---|
| {{RISK}} | {{MUTATION}} | {{EXPECTED}} | {{OBSERVED}} | {{REAL_RESULT}} | {{EVIDENCE}} |

```text
Sensor worktree before: {{SENSOR_WORKTREE_BEFORE}}
Sensor worktree after: {{SENSOR_WORKTREE_AFTER}}
Restoration proof: {{RESTORATION_PROOF}}
```

`NOT_MEASURED` cannot satisfy a mandatory discrimination sensor.

## 8. Code quality and scope

- [ ] Diff contains only approved activity scope.
- [ ] Main worktree and unrelated repositories remain unchanged.
- [ ] `git diff --check` passes.
- [ ] Build/type-check/lint/static checks required by the matrix pass.
- [ ] Manifest, schemas, lifecycle location and `STATE.md` agree.
- [ ] No unresolved placeholders, silent skips or unapproved fallbacks remain.
- [ ] No external mutation occurred without authority.
- [ ] Final rebase or synchronization requirement is satisfied or explicitly not applicable.
- [ ] PR metadata and reviewer handoff are ready.

## 9. Findings

| Severity | Finding | Owner | Disposition | Evidence |
|---|---|---|---|---|
| {{SEVERITY}} | {{FINDING}} | {{OWNER}} | {{DISPOSITION}} | {{EVIDENCE}} |

## 10. Ecosystem status

| Ecosystem gate | Integration base | Authority | Run ID | Result | Notes |
|---|---|---|---|---|---|
| {{ECOSYSTEM_GATE}} | {{INTEGRATION_BASE}} | {{AUTHORITY}} | {{RUN_ID}} | {{RESULT}} | {{NOTES}} |

Package readiness and ecosystem regression are separate verdicts. A pending or unauthorized ecosystem gate must remain explicit.

## 11. Final verdict

```text
VERDICT: {{PASS_BLOCK_FAIL}}
REQUIREMENTS COVERED: {{RESULT}}
DISCOVERY/EXECUTION RECONCILED: {{RESULT}}
DUPLICATE PRODUCERS: {{RESULT}}
TIMEOUTS/RETRIES/FLAKES: {{RESULT}}
COVERAGE: {{RESULT}}
DISCRIMINATION SENSOR: {{RESULT}}
PACKAGE GATE: {{RESULT}}
FINAL REBASE/SYNC: {{RESULT}}
INDEPENDENT FINAL REVIEW: {{RESULT}}
READY_FOR_PR: {{YES_NO}}
ECOSYSTEM REGRESSION: {{RESULT}}
```

Blocking rationale or residual risk: {{RATIONALE}}.
