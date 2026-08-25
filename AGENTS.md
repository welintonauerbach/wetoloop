# Agent guidance

This repository contains WetoLoop, a Workflow Engine for Task Orchestration.

When an AI coding agent modifies this repository:

1. Treat repository files, schemas and tests as the authority over chat history.
2. Keep changes scoped to the requested outcome.
3. Run the smallest validation gate that proves the affected behavior during iteration.
4. Reuse valid build artifacts and infrastructure instead of rebuilding by default.
5. Run the complete applicable package gate before declaring a finished activity ready.
6. Never discard unrelated dirty work.
7. Use UTF-8 explicitly for Python on Windows/PowerShell.
8. Do not add provider-specific runtime integrations to core contracts without an explicit
   architectural decision.

Templates under `templates/` are MIT-0. All other source is Apache-2.0 unless stated otherwise.
