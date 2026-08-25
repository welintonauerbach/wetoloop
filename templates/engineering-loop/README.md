# WetoLoop Engineering Loop template

This directory contains the repository-portable Engineering Loop contract shipped with
WetoLoop `0.0.1`.

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

The five groups are mandatory, unique and ordered. `PLAN.yaml` owns their IDs, labels,
directories and artifact paths. Paths are activity-relative, use `/`, and may not be
absolute, contain `..`, or escape the activity directory.

## Applicability

| Tier | Minimum contract |
|---|---|
| S | definition, requirements, bounded task, focused evidence and handoff |
| M | S plus design contracts, TechSpec and independent task review |
| L | M plus ADRs, corrective loop, package validation and learnings |
| X | every artifact, independent final validation, sensors and final package gate |

An artifact marked required by `PLAN.yaml.applicability` must exist even when a lower
tier would otherwise omit it. Applicability is explicit and is never inferred from empty
files.

## Use

1. Copy `PLAN.template.yaml` to a new activity as `PLAN.yaml`.
2. Copy the numbered group templates without flattening the directories.
3. Replace placeholders; do not remove required contract sections.
4. Validate the plan, traceability and execution state.
5. Keep the activity in backlog until the readiness contract is satisfied.

The `schemas/` directory defines the machine-readable contracts. Semantic constraints
that JSON Schema cannot express alone are enforced by the validator scripts.

## Safety invariants

- Repository scanning is read-only.
- Commands are structured as executable plus argv and never raw shell text.
- Existing dirty files are never discarded or silently absorbed.
- Each requirement and evidence item has one canonical producer.
- Intermediate task gates should validate the affected surface only.
- Build and test infrastructure may be reused when their inputs remain valid.
- Completion requires fresh final package evidence, independent review and an atomic handoff.

Templates are licensed under MIT-0 so generated or copied project artifacts do not carry
an attribution requirement. WetoLoop source code is licensed separately under Apache-2.0.
