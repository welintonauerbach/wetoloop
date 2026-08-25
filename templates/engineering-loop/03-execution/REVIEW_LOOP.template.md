# Independent Review Loop

The reviewer must not author candidate changes.

1. Fix the candidate SHA and task scope.
2. Inspect requirements, contracts, diff, tests and evidence.
3. Classify findings by severity and affected authority.
4. Report `PASS` only when no blocking finding remains.
5. Route fixes through the corrective loop and rerun affected gates freshly.

Record reviewer identity, candidate SHA, findings and verdict in task evidence.
