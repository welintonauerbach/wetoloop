---
schema_version: 1
loop_version: "0.0.1"
plan_id: replace-plan-id
current:
  phase: readiness
  task: null
  status: pending
completed_tasks: []
repository:
  absolute_path: C:/absolute/path/to/repository
  branch: replace-working-branch
  base_branch: main
  approved_base_sha: null
run:
  id: null
  started_at: null
  writer: null
last_verified_commit: null
last_gate:
  id: gate-f
  result: not_run
  run_id: null
  finished_at: null
location:
  lifecycle: backlog
  directory: docs/plans/_backlog/replace-plan-id
next_step:
  command_id: owner-approval
  summary: Complete Gate F readiness
blockers: []
working_tree:
  expected_dirty_files: []
  unexpected_dirty_files: []
measurement:
  package_gate: not_run
  independent_validation: not_run
  ecosystem_regression: pending_on_main
producers: []
updated_at: 2026-01-01T00:00:00Z
---

# Execution State

## Human Context

Explain why the structured state has its current values.

## Resume Checklist

- [ ] Reconcile Git, PLAN, task, state and evidence.
- [ ] Confirm no previous Run producer remains active.
- [ ] Execute only the recorded next step.

Git remains authoritative for repository facts. Gate results require fresh
evidence and authority conflicts must remain visible.
