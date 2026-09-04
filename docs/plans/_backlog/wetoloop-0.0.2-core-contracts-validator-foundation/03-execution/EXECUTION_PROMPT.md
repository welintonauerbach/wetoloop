# Execution Prompt

Execute activity `wetoloop-0.0.2-core-contracts-validator-foundation` on branch `feat/0.0.2-core-contracts-validator-foundation` only after Gate F records `READY_FOR_EXECUTION: YES`.

## Authority order

1. PLAN.yaml
2. REQUIREMENTS.md
3. approved Decisions and ADRs
4. Contract Register and TECHSPEC.md
5. TASKS.md and current task
6. TEST_STRATEGY.md
7. STATE.md

Repository files and Git facts override chat memory.

## Execution algorithm

1. Reconcile branch, approved base, worktree and STATE.
2. Select the next dependency-eligible task.
3. Implement only that task's scope.
4. Resolve declared impact and producer fingerprints.
5. Reuse valid dependency/build/generated/infrastructure producers.
6. Produce fresh verification for affected risk using the smallest focused gate.
7. Record counts, duration, retries/flakes, producer reuse and evidence.
8. Obtain independent task review.
9. Commit atomically and reconcile STATE.
10. Continue until the DAG is complete.

STOP only on a real BLOCKER, authority conflict, unsafe state or a failed gate that cannot be resolved within the approved corrective loop.

## Test policy

Do not run the complete suite after every task. Do not rerun restore/build/producers whose relevant inputs and artifacts remain valid. Escalate unknown impact to a bounded module/subsystem before repository-wide regression.

T08 owns the single cold final package gate: complete applicable suite, coverage, conformance, self-validation, final activity migration to 0.0.2 and independent final review.

## Prohibited

- implementation before Gate F approval;
- raw shell interpolation in harness contracts;
- provider-specific core contracts;
- automatic deletion of redundant/flaky tests;
- claiming PASS without fresh evidence for affected risk.
