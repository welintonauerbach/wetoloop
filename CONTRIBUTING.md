# Contributing to WetoLoop

Thanks for helping improve WetoLoop.

## Before opening a change

- Search existing issues before creating a new one.
- Keep changes narrowly scoped and explain the engineering outcome.
- Prefer an issue for behavioral or contract changes before a large implementation.
- Do not mix unrelated cleanup with functional changes.

## Development setup

Requirements:

- Node.js 20+
- npm 10+
- Python 3.10+

Clone the repository and run:

```bash
npm install
npm test
npm run check:python
```

Python processes that read repository content must run in UTF-8. On Windows/PowerShell,
prefer:

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
```

## Pull requests

A pull request should:

- describe the problem and intended outcome;
- include focused tests or validation for the affected behavior;
- avoid unnecessary full-suite work during iteration;
- update documentation when a public contract changes;
- keep generated artifacts and unrelated files out of the diff;
- pass the repository quality workflow.

## Contracts and compatibility

WetoLoop is currently pre-1.0. Changes to templates, schemas, validator output or harness
contracts may be breaking. Call them out explicitly in the pull request and changelog.

## Licensing contributions

By submitting a contribution, you agree that source contributions are provided under
Apache-2.0 unless the file is under `templates/`, where contributions are provided under
MIT-0.
