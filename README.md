# WetoLoop

**Workflow Engine for Task Orchestration**

WetoLoop is an open-source foundation for deterministic engineering loops used by AI
coding agents and engineering teams. It turns product intent into explicit contracts,
bounded tasks, focused verification, evidence and final package validation.

> Status: `0.0.1` — early public development. Interfaces and file contracts may change.

## Why WetoLoop

AI coding workflows become unreliable when the process exists only in a prompt or chat
history. WetoLoop moves the workflow into repository-owned artifacts and machine-readable
contracts.

Core principles:

- explicit requirements, design decisions and task ownership;
- deterministic lifecycle and state transitions;
- focused task gates instead of full-suite execution after every task;
- reuse of valid build artifacts and test infrastructure;
- fresh evidence for risks affected by the current change;
- complete package validation only at the final activity gate;
- structured commands, path containment and fail-closed validation;
- learnings captured so future loops can become faster and safer.

## Repository layout

```text
wetoloop/
├── packages/                  # future npm packages: core, CLI and harness
├── templates/                 # reusable Engineering Loop templates
├── skills/                    # reusable agent procedures
├── docs/                      # architecture, principles and roadmap
├── examples/                  # future reference activities and integrations
├── scripts/                   # repository-level quality tooling
└── .github/                   # contribution and CI configuration
```

The current executable baseline lives under `templates/engineering-loop/` and includes
manifest templates, schemas and dependency-light Python validators.

## Versioning

WetoLoop starts at `0.0.1` and follows Semantic Versioning. During `0.x`, breaking
changes are expected while the public contracts stabilize.

The historical private Engineering Loop versions that preceded WetoLoop are not public
WetoLoop release numbers.

## Installation

The npm CLI is not published yet. The repository is intentionally marked private in the
root `package.json` to prevent accidental publication while the CLI contract is being
built.

The intended usage model is:

```bash
npx @wetoloop/cli init
```

with local and global npm installation supported once the CLI package is ready.

## Development

Requirements:

- Node.js 20+
- npm 10+
- Python 3.10+

Run repository checks:

```bash
npm test
npm run check:python
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution workflow.

## Roadmap

The first public milestones focus on:

1. stabilizing the WetoLoop activity contract and semantic validators;
2. impact-aware focused test selection;
3. build, dependency, Docker and database reuse based on input fingerprints;
4. warm task gates and a cold final package gate;
5. reusable Engineering Loop skills;
6. a distributable npm CLI and harness interface.

See [docs/roadmap.md](docs/roadmap.md).

## Licensing

WetoLoop source code is licensed under the [Apache License 2.0](LICENSE).

Files under `templates/` are licensed under [MIT-0](templates/LICENSE), allowing copied
or generated project artifacts to be used without an attribution requirement.
