# Execution Prompt

Execute exactly one eligible task unless the activity explicitly authorizes sequential task execution.

## Preflight

1. Verify absolute repository, branch, upstream, HEAD and worktree state.
2. Confirm the activity is in `_in_progress` and Gate F is ready.
3. Reconcile `PLAN.yaml`, task, `STATE.md`, Git and fresh evidence.
4. Confirm dependencies, one writer, independent reviewer/verifier and harness command.
5. Stop on any governance mismatch; do not repair authority implicitly.

## Executive progress checkpoints

Keep the owner informed with short execution checkpoints. These updates are operational orientation, not technical reports.

Required visible states:

- `INICIADA` — once when a task starts, with one line describing the objective;
- `EM EXECUÇÃO` — only after a meaningful milestone when the task spans multiple implementation/test/corrective phases;
- `CORRECTIVE LOOP` — when a deterministic failure enters correction, with the bounded cause and next action;
- `CONCLUÍDA` — once after the task gate/review passes, with one-line outcome, gate result and next task;
- `BLOCKED` — immediately for a real STOP condition, with the blocker in one line.

Preferred shape:

```text
▶ T02 INICIADA — <one-line objective>.
… T02 EM EXECUÇÃO — <one-line status>. Progresso: <criteria closed/total or phase>. Próximo: <one action>.
✓ T02 CONCLUÍDA — <one-line result>. Gate: PASS. Próxima: <task>.
```

Rules:

- keep each checkpoint to 1–3 short lines;
- use objective progress such as criteria counts, current phase, gate state and next action;
- do not provide wall-clock ETA, delivery promises or speculative duration estimates;
- do not paste raw logs, command dumps, stack traces, secrets or sensitive configuration;
- do not interrupt an active command merely to report status; checkpoint between meaningful phases;
- a fast task may emit only `INICIADA` and `CONCLUÍDA`;
- do not create repository commits/files solely for intermediate checkpoints;
- at task completion, fold the final one-line executive summary into the normal `STATE.md` handoff using existing state fields/human context rather than creating a separate reporting artifact.

Progress reporting must remain lightweight and must never trigger duplicate tests, producers or validation runs.

## Per-task loop

Emit `INICIADA`, implement only the bounded capability, add focused tests, emit `EM EXECUÇÃO` only after meaningful milestones when useful, run the smallest declared warm gate, obtain review, reconcile evidence/state, check the commit, create one atomic commit, fold the one-line executive summary into `STATE.md`, emit `CONCLUÍDA`, then continue when sequential execution is authorized. Do not silently retry, skip or widen a filter to obtain PASS.

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

After authorized merge, Gate H runs on the exact integrated `develop` (or configured integration-branch) SHA.

### Mandatory preflight — Delta Classification + Fingerprint Reconciliation

Before any expensive Gate H producer:

1. record the exact Gate G candidate SHA and exact integrated SHA;
2. compare `candidate..integrated`;
3. classify post-candidate changes into production source, backend tests,
   build/project/restore inputs, schema/migrations, OpenAPI producer inputs,
   HTTP/topology/security inputs, frontend/consumer inputs and
   documentation/governance-only changes;
4. reconcile the relevant producer fingerprints, including `RestoreKey`,
   `BuildKey`, relevant `SchemaKey`s, `OpenApiKey`, `HttpSecurityKey`,
   `FrontendConsumerKey` and generated-artifact keys;
5. record `REUSE`, `RERUN` or `N/A` for every auxiliary producer, including
   hash/provenance when reused.

The complete integrated repository/backend regression remains mandatory fresh
Gate H evidence. Fingerprint reuse prevents only unnecessary auxiliary producer
and wrapper repetition.

Gate H runs the complete integrated non-migration/backend regression once and
the complete migration/integration lane once according to repository policy,
plus merge-interaction verification.

Run global build, OpenAPI, HTTP/security, frontend/consumer and static producers
only when their fingerprint or explicit repository Gate H policy requires fresh
execution.

Gate H MUST NOT:

- execute a wrapper containing the full backend regression and then rerun the
  same child lane separately;
- rerun package/module suites already subsumed by the complete non-migration
  lane;
- rerun migrations module-by-module after the complete migration lane;
- regenerate OpenAPI when `OpenApiKey` remains valid and artifact
  hash/provenance remains reusable;
- rerun the complete HTTP/security wrapper when `HttpSecurityKey` remains
  valid; if only a bounded sub-gate changed and targeted execution is
  available, run only that sub-gate;
- run full frontend verify/coverage/build merely because Gate H exists when
  `FrontendConsumerKey` remains valid and frontend is outside activity scope;
  when only an API consumer contract changed, prefer the smallest repository-
  required consumer-contract check;
- rerun restore/build auxiliary producers when their fingerprint is unchanged
  and a valid producer output is available;
- repeat candidate sensors, mutation experiments, independent candidate review
  or candidate-only coverage unless integration invalidated the relevant
  evidence fingerprint or repository policy explicitly requires it.

Record reused producers explicitly so skipped expensive commands are justified
by fingerprint and provenance rather than silently omitted.

A Gate G PASS means merge-ready. Global/integrated success may be claimed only after Gate H passes.
