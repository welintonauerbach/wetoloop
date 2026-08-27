# Execution Prompt

Execute exactly one eligible task unless the activity explicitly authorizes sequential task execution.

## Preflight

1. Verify absolute repository, branch, upstream, HEAD and worktree state.
2. Confirm the activity is in `_in_progress` and Gate F is ready.
3. Reconcile `PLAN.yaml`, task, `STATE.md`, Git and fresh evidence.
4. Confirm dependencies, one writer, independent reviewer/verifier and harness command.
5. Stop on any governance mismatch; do not repair authority implicitly.

## Per-task loop

Implement only the bounded capability, add focused tests, run the smallest declared warm gate, obtain review, reconcile evidence/state, check the commit and create one atomic commit. Do not silently retry, skip or widen a filter to obtain PASS.

Before running a command, state the unique new task risk it proves. Skip repetition owned by an earlier task, Candidate Gate G or Develop Integration Gate H.

Corrections rerun the detecting test, directly impacted checks and the finding recheck. Broad reaudit is reserved for contract, security, architecture or scope changes.

Never run a wrapper and its child commands twice for the same evidence.

## Candidate Gate G — pre-merge

The final activity task must validate the exact candidate using:

- accumulated `ImpactSet` regression;
- direct/transitive consumers affected by the activity;
- changed mandatory architecture/security/configuration boundaries;
- only affected migrations/schema upgrade paths;
- required changed-code/package coverage once;
- representative discrimination sensors once;
- producer/evidence/count reconciliation;
- independent verifier of the exact candidate SHA;
- PR/merge readiness decision.

**Do not run the complete repository/backend/ecosystem regression in Gate G when a mandatory Gate H will run after merge.**

A pre-merge full regression requires an explicit documented exception: no guaranteed Gate H, repository merge policy requiring it without equivalent post-merge validation, repository-wide runner/build/infrastructure risk that cannot be bounded, or owner-authorized release exception.

## Develop Integration Gate H — post-merge

After authorized merge, Gate H owns the complete integrated regression on the exact `develop` (or configured integration-branch) SHA.

Gate H runs the repository/ecosystem full regression once and validates merge interactions. It must not separately repeat task suites already contained in the full wrapper.

By default Gate H does not repeat candidate sensors, mutation experiments, independent candidate review or candidate-only coverage. Repeat them only when integration changed the relevant evidence fingerprint or repository policy explicitly requires it.

A Gate G PASS means merge-ready. Global/integrated success may be claimed only after Gate H passes.
