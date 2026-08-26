# Technical Specification

## Architecture and boundaries

WetoLoop 0.0.2 keeps Python validators as the executable reference implementation while making the public contract implementation-neutral.

```text
Templates + PLAN
      |
      v
Structured parser
      |
      v
Shared schema validation
      |
      v
Canonical semantic validators
      |
      v
Aggregate validate_plan
      |
      v
Self-contained conformance suite
```

`packages/core` remains reserved in this release. Runtime-specific behavior is not introduced.

## Detailed design

### Canonical semantic path

Every canonical validator accepts the activity root through `--plan`. Public semantics are defined only by the current manifest, templates, schemas, decisions and semantic rule tests. Historical positional entrypoints may remain temporarily for compatibility, but they cannot enforce a different public document shape or participate as a second authority.

### Shared schema validation

A dependency-light shared schema layer validates structured PLAN, TASK, STATE and HARNESS data before semantic success. Unsupported references fail closed. Artifact and relative path containment remains mandatory.

### ImpactSet

Every executable task declares:

- policy: `direct_and_transitive`;
- affected projects/modules;
- production components;
- test infrastructure;
- new or modified tests;
- existing directly affected tests;
- direct consumers;
- special boundaries;
- runtime/configuration inputs;
- uncertainty: `known` or `unknown`.

Unknown impact escalates first to a declared bounded module/subsystem. Repository-wide regression is reserved for explicit cross-cutting impact or the final package gate.

### VerificationRun

A VerificationRun is fresh proof for the current candidate or dirty state and affected risk. It records run ID, task/gate, candidate anchor, commands/actions, scope, timing, results and evidence. A prior PASS never substitutes for a new VerificationRun when the same risk is affected again.

### ProducerFingerprint

A ProducerFingerprint identifies whether a physical producer can be reused. It covers relevant inputs such as toolchain/runtime identity, dependency manifests and lockfiles, source/build inputs, generator inputs, Dockerfile/base image/build context, migration set/database engine and deterministic seed inputs. Candidate commit SHA is not by itself the producer-cache key.

### ProducerRecord

A reusable producer record contains producer kind, fingerprint, artifact identity/hash/location, health/validity, execution count, producing run and reuse consumers. Reuse is allowed only while fingerprint and artifact validity remain true.

### State phases

During `planning` or `readiness`, `current.task` may be null. Once execution is active, current task must exist and status must agree with task front matter.

### Gate model

**Warm focused task gate:** reuse valid producers; create fresh verification only for affected risk.

**Cold final package gate:** execute complete applicable package regression, coverage, schema/semantic conformance, clean lifecycle checks, exact final-candidate review and self-validation.

## Security and safety

- Validators remain read-only and strict UTF-8.
- Raw shell command templates remain forbidden.
- Relative paths stay inside activity/workspace authority.
- Unknown structured input fails closed.
- No provider-specific runtime dependency enters core contracts.
- External writes and lifecycle moves require explicit authority.

## Testability and rollout

Each mandatory semantic rule gets a positive and discriminating negative fixture. T01-T07 run only affected focused gates; complete conformance, code coverage and self-hosted migration run once in T08. The activity remains on 0.0.1 during planning/implementation and migrates to 0.0.2 in T08 before Gate G.
