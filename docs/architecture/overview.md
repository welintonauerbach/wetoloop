# Architecture overview

WetoLoop separates declarative engineering contracts from deterministic execution.

```text
Product intent
     │
     ▼
Templates + schemas
     │
     ▼
Activity manifest + state + task graph
     │
     ▼
Core policies
     │
     ├── validation
     ├── impact analysis
     ├── build/test reuse
     ├── evidence
     └── lifecycle
     │
     ▼
Harness interface
     │
     ▼
Repository tools and execution environment
```

## Planned package boundaries

### `packages/core`

Owns domain contracts, activity parsing, lifecycle rules, impact sets, fingerprints and
provider-neutral policy.

### `packages/cli`

Owns installation, initialization, validation, diagnostics and command-line UX.

### `packages/harness`

Owns deterministic task execution, build/test orchestration, evidence capture and final
package gates.

## Design rule

The core must remain independent from any specific agent runtime or model provider.
Runtime integrations should depend on WetoLoop contracts, never the reverse.
