# Execution Prompt

Execute exactly one eligible task.

## Preflight

1. Verify absolute repository, branch, upstream, HEAD and worktree state.
2. Confirm the activity is in `_in_progress` and Gate F is ready.
3. Reconcile `PLAN.yaml`, task, `STATE.md`, Git and fresh evidence.
4. Confirm dependencies, one writer, independent reviewer and harness command.
5. Stop on any mismatch; do not repair governance implicitly.

## Per-task loop

Implement only the bounded capability, add focused tests, run the smallest
declared gate, obtain independent review, reconcile evidence/state, check the
commit and create one atomic commit. Do not silently retry, skip or widen a
filter to obtain PASS.

Before running a command, state the unique new task risk it proves. Skip
repetition owned by an earlier task or the final package gate. Corrections rerun
the detecting test, directly impacted checks and the finding recheck; broad
reaudit is reserved for contract, security, architecture or scope changes.
Never run a wrapper and its child commands twice for the same evidence.

## Final verification

Completion requires the final candidate, package regression, sensors,
independent validation, evidence reconciliation and Gate G.
