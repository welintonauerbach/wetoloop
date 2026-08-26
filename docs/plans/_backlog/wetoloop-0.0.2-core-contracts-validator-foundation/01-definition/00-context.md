# Context

WetoLoop is an open-source Workflow Engine for Task Orchestration. Version 0.0.1 established the repository layout, portable Engineering Loop templates, initial schemas and dependency-light Python validators.

The next release must strengthen the contracts before CLI or runtime automation is built. The main concern is correctness of semantic validation and the ability to iterate quickly with focused tests while safely reusing valid build and infrastructure producers.

## Engineering outcome

Make the WetoLoop contract reliable enough that a repository activity can be planned, validated, executed and audited without depending on hidden chat context or divergent validator behavior.

## Constraints

- Keep the implementation provider-neutral.
- Keep Python as validator runtime for 0.0.2.
- Do not implement the automatic impact, build-cache, Docker or database execution engine yet.
- Preserve deterministic, UTF-8, machine-readable validator output.
- Preserve the source/template licensing split.
