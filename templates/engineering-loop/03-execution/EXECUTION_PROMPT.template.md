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
