# Review Loop

Every implementation task requires independent review after its focused gate.

The reviewer checks requirement/task scope, public contract compatibility, impact declaration, gate adequacy, producer reuse, test discrimination, affected consumers, path/command safety, evidence freshness and atomic commit readiness.

Verdicts are `PASS`, `CORRECTIVE_REQUIRED` or `BLOCK`. The reviewer must not be the same execution identity recorded as task builder.
