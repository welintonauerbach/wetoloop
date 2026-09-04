# Decisions

| ID | Decision | Status | Rationale |
|---|---|---|---|
| DEC-001 | Python remains the validator runtime for WetoLoop 0.0.2. | APPROVED | Stabilize behavior and contracts before changing implementation language. |
| DEC-002 | 0.0.2 defines ImpactSet and producer fingerprints but defers the automatic impact/cache engine. | APPROVED | Separate contract stabilization from runtime automation. |
| DEC-003 | This activity starts under 0.0.1 and migrates/dogfoods the 0.0.2 contract before Gate G. | APPROVED | Prove the new contract on the activity that creates it. |
| DEC-004 | Plan-based validators and current public templates/schemas are the canonical semantic authority; legacy positional validation must not define a divergent public contract. | DERIVED | The public activity is manifest-driven and requires one deterministic contract. |
| DEC-005 | Candidate commit identifies fresh evidence; producer fingerprints determine reusable artifact validity. | LOCKED | This is already a repository design principle and separates proof freshness from infrastructure reuse. |

`APPROVED` records explicit owner approval. `DERIVED` follows the approved scope and current repository authority. `LOCKED` changes only through an explicit corrective architectural decision.
