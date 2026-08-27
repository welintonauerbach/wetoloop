# WetoLoop Engineering Loop template

This directory contains the repository-portable Engineering Loop contract for WetoLoop `0.0.2` project adoption.

An activity is manifest-driven and keeps only `PLAN.yaml` and `README.md` at its root.

## Generated layout

```text
<activity>/
├── PLAN.yaml
├── README.md
├── 01-definition/
├── 02-design/
├── 03-execution/
├── 04-validation/
└── 05-governance/
```

The five groups are mandatory, unique and ordered. `PLAN.yaml` owns their IDs, labels, directories and artifact paths. Paths are activity-relative, use `/`, and may not be absolute, contain `..`, or escape the activity directory.

## Applicability

| Tier | Minimum contract |
|---|---|
| S | definition, requirements, bounded task, focused evidence and handoff |
| M | S plus design contracts, TechSpec and independent task review |
| L | M plus ADRs, corrective loop, candidate validation and learnings |
| X | every artifact, independent final validation, sensors, Candidate Gate G and Develop Integration Gate H |

An artifact marked required by `PLAN.yaml.applicability` must exist even when a lower tier would otherwise omit it. Applicability is explicit and is never inferred from empty files.

## Validation ownership

WetoLoop `0.0.2` separates two final assurance questions:

### Candidate Gate G — before merge

> Is the activity candidate correct and safe to merge?

Gate G owns the accumulated `ImpactSet`, affected consumers, changed mandatory boundaries, affected migrations, required activity/package coverage, representative discrimination sensors, evidence reconciliation and independent candidate verification.

Gate G does **not** run the complete repository/ecosystem regression merely to duplicate the post-merge integration gate.

### Develop Integration Gate H — after merge

> After integration with the current base branch, does the complete repository/product still pass?

Gate H owns the complete integrated regression on the exact `develop` (or configured integration branch) SHA. It verifies cross-module/ecosystem behavior and merge interactions once.

Candidate sensors, mutation experiments, candidate-only coverage and independent candidate review are not repeated in Gate H unless their evidence was invalidated by integration or repository policy explicitly requires it.

A pre-merge full repository regression is an exception and must be justified by one of the contract-approved reasons: no guaranteed Gate H, mandatory merge policy without equivalent post-merge regression, unbounded repository-wide runner/build/infrastructure risk, or explicit owner-authorized release exception.

## Use

1. Copy `PLAN.template.yaml` to a new activity as `PLAN.yaml`.
2. Copy the numbered group templates without flattening the directories.
3. Replace placeholders; do not remove required contract sections.
4. Validate the plan, traceability and execution state.
5. Keep the activity in backlog until the readiness contract is satisfied.
6. Run warm focused task gates during implementation.
7. Run Candidate Gate G once on the final candidate.
8. After authorized merge, run Develop Integration Gate H once on the integrated branch.

The `schemas/` directory defines the machine-readable contracts. Semantic constraints that JSON Schema cannot express alone are enforced by validator scripts.

## Safety invariants

- Repository scanning is read-only.
- Commands are structured as executable plus argv and never raw shell text.
- Existing dirty files are never discarded or silently absorbed.
- Each requirement and evidence item has one canonical producer.
- Intermediate task gates validate the affected surface only.
- Build and test infrastructure may be reused when their inputs remain valid.
- Broad regression has one canonical owner: Gate H when that gate is guaranteed.
- Gate G and Gate H must not duplicate the same complete regression without an explicit approved exception.
- Sensors run once on the candidate and are fully restored before handoff.
- Gate G completion requires fresh candidate evidence, independent review and an atomic handoff.
- Global/integrated success requires Gate H PASS after merge.

Templates are licensed under MIT-0 so generated or copied project artifacts do not carry an attribution requirement. WetoLoop source code is licensed separately under Apache-2.0.
