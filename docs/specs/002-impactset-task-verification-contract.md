# SPEC-002 — ImpactSet & Task Verification Contract

- Status: Ready for review
- Target: `0.0.2`
- Depends on: SPEC-001 Semantic Validator Foundation
- Owners: WetoLoop maintainers

## 1. Problem

WetoLoop `0.0.1` correctly states that task completion should run the smallest gate that proves the risk introduced by the task, but the task contract currently contains only a generic `gate: focused` marker.

That is not enough to answer deterministically:

- which production units changed;
- which tests are directly affected;
- which consumers may break;
- which boundaries require special treatment;
- when a focused test is sufficient;
- when verification must escalate to a module, subsystem or package suite;
- why a broad suite was executed;
- why a build or test was safely skipped.

Without a machine-readable impact contract, agents can interpret “focused” differently and may either under-test changes or run the full suite “just to be safe.”

## 2. Goals

SPEC-002 SHALL define a portable contract for resolving and recording the verification surface of a task.

The contract SHALL:

- make task-owned verification intent explicit;
- derive actual impact from repository evidence instead of trusting manual declarations alone;
- represent direct and transitive impact;
- support conservative escalation when impact confidence is low;
- stop escalation at the smallest safe bounded scope before falling back to a package-wide suite;
- distinguish production impact, test impact and boundary/risk triggers;
- provide deterministic inputs to later build reuse, test selection and Harness execution;
- produce an auditable `ImpactSet` that can be attached to evidence;
- keep the final package gate independent from task-level impact optimization.

## 3. Non-goals

This specification does not implement:

- language-specific dependency graph adapters for every ecosystem;
- build artifact fingerprints;
- Docker/database reuse;
- physical command execution by the Harness;
- coverage collection;
- final package-gate implementation.

Those features consume the `ImpactSet` contract in later specifications.

## 4. Core principle

A task SHALL declare verification policy and known boundaries, but the final `ImpactSet` SHALL be resolved from actual repository state.

The resolver MUST treat the Git diff and repository dependency evidence as authoritative over optimistic task metadata.

In short:

```text
Task verification policy
        +
Actual changed files
        +
Repository dependency graph / mappings
        +
Risk triggers and special boundaries
        =
Resolved ImpactSet
```

Manual task declarations may expand the resolved impact. They MUST NOT silently remove impact discovered from the repository.

## 5. Terminology

### 5.1 Verification Policy

Persistent task metadata describing how impact should be interpreted and how uncertainty should escalate.

### 5.2 Impact Hint

A declared project, path, consumer or boundary known during planning. Hints help resolution but are not proof of the complete impact set.

### 5.3 ImpactSet

A runtime result describing the exact verification surface selected for a specific candidate state.

### 5.4 Direct impact

A unit directly changed or explicitly coupled to a changed unit.

### 5.5 Transitive impact

A consumer reachable through the dependency graph from a changed shared contract/library/unit.

### 5.6 Boundary trigger

A change category that requires special verification independently of normal source dependency mapping, such as migration, authentication, serialization, DI composition or test infrastructure.

### 5.7 Escalation

Conservative widening of the verification scope when exact selection cannot safely discriminate the risk.

## 6. Task contract

`TASK.md` front matter SHALL evolve from a generic focused gate to an explicit verification contract.

Recommended shape:

```yaml
verification:
  mode: focused
  impact_policy: direct_and_transitive
  confidence_required: high

  hints:
    projects: []
    test_projects: []
    direct_consumers: []
    boundaries: []

  escalation:
    unknown_impact: module_suite
    shared_contract_change: consumer_suite
    persistence_change: persistence_suite
    migration_change: persistence_suite
    auth_or_security_boundary: subsystem_suite
    composition_or_config_change: subsystem_suite
    test_infrastructure_change: dependent_integration_suite
```

Names may be refined during implementation, but the semantics above are normative.

The existing `tests:` list remains the task-owned list of planned/new/modified test IDs. It does not replace impact resolution.

The existing `gate:` field SHOULD be deprecated in favor of `verification.mode` once compatibility migration is documented.

## 7. Verification mode

Initial supported modes:

- `focused` — resolve the smallest safe affected surface;
- `package` — explicitly task-owned broad package verification, allowed only with a documented reason;
- `none` — allowed only for changes where executable verification is genuinely not applicable and a static/manual evidence rule is declared.

`focused` is the default and expected mode for implementation tasks.

A task MUST NOT use `package` merely to avoid impact analysis.

## 8. Resolved ImpactSet model

The resolver SHALL produce a structured result equivalent to:

```yaml
impact_set:
  schema_version: 1
  task: T04
  candidate: <commit-or-dirty-state-identifier>

  changed_files: []

  production:
    direct_units: []
    transitive_consumers: []

  tests:
    planned_or_modified: []
    directly_affected: []
    consumer_tests: []

  boundaries: []
  risk_triggers: []

  selected_scopes: []

  confidence: high
  escalation:
    level: exact
    reason: null

  exclusions: []
```

The persisted representation MAY be JSON, YAML front matter or a canonical evidence section. The semantic fields are required regardless of serialization.

## 9. Impact resolution inputs

The resolver SHALL consider, in order:

1. actual Git diff for the candidate task;
2. task source/test/documentation scope;
3. new or modified tests declared by the task;
4. project/module dependency graph where available;
5. repository-maintained source-to-test mappings where available;
6. TechSpec Test Treatment and declared special boundaries;
7. task impact hints;
8. known risk-trigger rules.

A missing optional dependency graph is not automatically a blocker. It reduces confidence and invokes escalation rules.

## 10. Resolution algorithm

The default resolver SHALL follow this sequence.

### Step 1 — classify changed files

Each changed file is classified into one or more categories:

- production source;
- test source;
- shared contract/schema/API;
- persistence/data access;
- migration;
- authentication/authorization/security boundary;
- serialization/protocol;
- DI/composition/global configuration;
- test infrastructure;
- build/dependency metadata;
- documentation only;
- unknown.

Repository adapters may add classifications but may not weaken the core safety categories.

### Step 2 — resolve direct production units

Map changed production files to the smallest known executable or logical units: project, package, module, library or component.

### Step 3 — resolve planned/modified tests

Every new or modified task-owned test SHALL be included in the task gate unless the test is proven non-executable in the current environment and explicitly deferred by authority.

### Step 4 — resolve directly affected existing tests

Use repository mappings, naming conventions, project ownership and dependency evidence to select tests directly coupled to changed behavior.

### Step 5 — resolve consumers

If a changed unit exposes shared behavior or contracts, resolve direct and then transitive consumers as required by policy.

### Step 6 — apply boundary triggers

Boundary rules can widen the gate independent of dependency topology.

### Step 7 — calculate confidence

Confidence is `high`, `medium` or `low` based on completeness of impact evidence.

### Step 8 — escalate if necessary

If confidence does not meet task policy or a mandatory trigger requires a broader gate, widen to the smallest configured safe scope.

### Step 9 — produce exclusions

Anything intentionally not executed SHALL have a structured reason and gate owner, such as `final_package`, `ecosystem`, `not_applicable` or `external_authority`.

## 11. Escalation ladder

The standard escalation ladder SHALL be:

```text
exact tests/components
    ↓
project/module suite
    ↓
bounded subsystem / consumer suite
    ↓
package suite
```

The resolver SHOULD stop at the first level that safely covers the uncertainty.

Unknown impact MUST NOT jump directly to full repository/package regression when a bounded module or subsystem can safely contain the uncertainty.

The final activity gate still runs the complete applicable package suite regardless of previous focused decisions.

## 12. Mandatory risk-trigger behavior

Minimum default trigger rules:

| Change | Minimum task verification consequence |
|---|---|
| New/modified test | run that test |
| Local production implementation | direct tests for that behavior |
| Shared library/contract/API/schema | direct tests + affected consumer tests |
| Persistence/repository behavior | direct tests + persistence/integration scope |
| Migration | migration/persistence integration scope |
| Auth/security boundary | bounded security/subsystem regression |
| Serialization/protocol contract | contract tests + consumers |
| DI/composition/global configuration | startup/composition tests + bounded subsystem suite |
| Test infrastructure | tests that depend on that infrastructure |
| Dependency/build metadata | affected build/type-check + relevant tests |
| Documentation only | static/document validation unless generated/runtime contract changed |
| Unknown | escalate to module or bounded subsystem |

Repository-specific policies may widen these defaults.

## 13. Build interaction

SPEC-002 determines *what must be verified*, not whether compilation artifacts can be reused.

Later fingerprint logic SHALL consume the ImpactSet and answer whether the selected verification requires a new producer execution.

Therefore:

```text
ImpactSet says: project A and tests X/Y are affected.
Fingerprint policy says: project A build output is still valid or must be rebuilt.
```

These decisions MUST remain separate.

## 14. Evidence contract

Every focused task gate SHALL record the resolved ImpactSet or an immutable reference to it.

Minimum evidence:

- task ID;
- candidate identity;
- changed files considered;
- direct production units;
- selected tests/scopes;
- consumer impact;
- boundary/risk triggers;
- confidence;
- escalation level and reason;
- explicit exclusions/deferred scopes;
- resolver version/policy identifier.

This allows an independent reviewer to answer: “Why were these tests sufficient for this task?”

## 15. Validation rules

SPEC-001 validators SHALL be extended so task verification metadata is machine checked.

Minimum rules:

- `verification.mode` is recognized;
- `focused` tasks contain an impact policy and escalation policy;
- hint arrays contain safe, non-empty identifiers/paths;
- unknown escalation is never `none`;
- boundary trigger configuration cannot narrow a WetoLoop mandatory default;
- a package-mode task contains an explicit justification;
- task verification metadata cannot declare exclusion of new/modified task-owned tests;
- legacy `gate: focused` is accepted only during the documented migration window.

Resolved ImpactSet validation SHALL reject:

- candidate mismatch;
- missing changed-file accounting;
- selected scope with no risk/impact rationale;
- high confidence when required dependency evidence is known to be unavailable and no equivalent mapping exists;
- exclusion without reason/owner;
- unknown impact with no escalation;
- manually declared impact that is narrower than discovered Git/dependency impact.

## 16. Repository adapter boundary

The generic WetoLoop contract SHALL not hard-code `.NET`, Node.js, Go or other ecosystem rules into the core specification.

Adapters may provide:

```text
changed file → project/module
project/module → tests
project/module → consumers
contract → consumers
boundary classification
```

The generic resolver SHALL consume these mappings through a stable adapter interface.

A fallback adapter SHALL still support path/project-level escalation when rich dependency data is unavailable.

## 17. Expected file changes

Expected modifications:

```text
templates/engineering-loop/03-execution/TASK.template.md
templates/engineering-loop/04-validation/TEST_STRATEGY.template.md
templates/engineering-loop/schemas/task.schema.json
templates/engineering-loop/scripts/validate_tasks.py
templates/engineering-loop/scripts/semantic_checks.py   # from SPEC-001, or equivalent
```

Expected additions may include:

```text
templates/engineering-loop/schemas/impact-set.schema.json
templates/engineering-loop/scripts/impact_contract.py
```

Runtime resolution code may initially live under `packages/core` or remain deferred until the Harness/Core implementation spec. If resolution execution is deferred, the schema, task contract, validation rules and conformance cases in this spec must still be completed.

## 18. Required conformance scenarios

At minimum, conformance tests SHALL cover:

1. local source change selects direct tests only;
2. new test is always included;
3. shared contract change adds consumer tests;
4. migration change selects persistence/migration scope;
5. test infrastructure change selects dependent integration tests;
6. documentation-only change does not trigger broad runtime suite;
7. unknown source mapping escalates to module suite;
8. missing module boundary escalates to bounded subsystem/package according to policy;
9. manual hints can widen but cannot narrow discovered impact;
10. package mode without justification fails validation;
11. unknown impact configured with `none` fails validation;
12. resolved ImpactSet candidate mismatch fails validation.

## 19. Acceptance criteria

SPEC-002 is complete when:

- [ ] task template contains a machine-readable verification policy.
- [ ] task schema validates the verification policy.
- [ ] `gate: focused` has a documented migration/deprecation path.
- [ ] an `ImpactSet` schema/contract exists.
- [ ] direct, transitive, boundary and escalation semantics are documented and testable.
- [ ] mandatory default risk triggers are implemented in validation/resolution rules.
- [ ] task validation rejects unsafe/narrowing policies.
- [ ] ImpactSet validation rejects unresolved unknown impact.
- [ ] positive and negative conformance cases cover the required scenarios.
- [ ] Test Strategy references ImpactSet as the source of task-focused scope.
- [ ] focused task evidence can explain why the selected scope is sufficient.
- [ ] no implementation requires running the entire package suite simply because exact impact is unavailable when a bounded fallback exists.

## 20. Implementation order

Recommended implementation slices:

1. task verification metadata and schema;
2. ImpactSet public schema/semantic model;
3. risk classifications and mandatory triggers;
4. escalation policy and confidence model;
5. validation of policies and resolved sets;
6. Test Strategy integration;
7. self-contained conformance scenarios;
8. handoff contract for later Core/Harness runtime resolution.

Task-level tests should remain focused on changed resolver/schema behavior. The complete SPEC-001/SPEC-002 conformance suites and repository quality gate run once on the final candidate.
