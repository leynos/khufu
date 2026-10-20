# 🔺 Khufu

*One great pyramid of local validation, instead of four drifting sandcastles.*

Khufu is the shared local validation tool for the df12 Nile Valley estate. It
builds an application's image, stands up an isolated rootless kind cluster,
installs a locked operator platform, deploys the application's own chart, runs
explicit checks, and hands back a report stating exactly what was demonstrated.

> **Status:** Khufu is designed but not yet implemented. The commands below
> describe the planned interface; see the [roadmap](docs/roadmap.md) for
> progress.

______________________________________________________________________

## Why Khufu?

Episodic, Corbusier, Wildside, and Ghillie each grew their own local preview
scripts. They now disagree about cluster engines, operator versions, secret
handling, and what "it works" means. Khufu replaces them with:

- **One shared implementation**: cluster lifecycle, image transport, operator
  installation, credential binding, and evidence collection live in one place,
  not four drifting copies.
- **A fixed, rootless stack**: Linux, rootless Podman, kind, kubectl, and
  Helm. No provider matrix, no k3d branch, no rootful fallback.
- **A locked operator platform**: CloudNativePG and Hyperspike Valkey ship as
  one versioned platform bundle that applications request but never pin.
- **Agent-native durable jobs**: non-interactive commands, stable JSON
  envelopes, idempotency keys, and detached workers that survive a closed
  terminal.
- **Honest evidence**: every report records which checks passed, which were
  blocked, and which capabilities were never requested.

______________________________________________________________________

## Quick start

### Working on Khufu today

Khufu targets CPython 3.14 and uses `uv` for environment management.

```bash
git clone https://github.com/leynos/khufu.git
cd khufu
make all
```

`make all` builds the virtual environment, then runs formatting checks,
linting, type checking, and tests.

### Planned usage

An application declares its deployable surfaces in `.khufu.toml`:

```toml
schema_version = 1
application = "corbusier"

[image]
context = "."
dockerfile = "Dockerfile"

[chart]
path = "charts/corbusier"
values = ["charts/corbusier/values.local.yaml"]

[services.postgres]
database = "corbusier"
owner = "corbusier"

[environment.DATABASE_URL]
source = "postgres.application-uri"
codec = "postgresql-uri"
```

Validation is then a check, a plan, and a run (planned interface):

```bash
# Read-only host prerequisite report
khufu doctor

# Freeze inputs and effects into a plan; note the plan ID it returns
khufu plan create --app ghillie --suite smoke --json

# Submit the plan as a durable job and wait for the verdict
khufu run create --plan <plan-id> \
  --idempotency-key ghillie-pr-42-smoke --wait --json
```

______________________________________________________________________

## Features

- Read-only `doctor` diagnostics for rootless Podman, cgroup delegation, and
  user systemd.
- Declarative application contracts that reject infrastructure overrides.
- Disposable, per-worktree kind environments with private kubeconfigs.
- Shared CNPG and Valkey provisioning with typed connection bindings.
- Durable SQLite job ledger with cancellation, resumption, and crash
  reconciliation.
- Contract, smoke, and integration suites with explicit coverage exclusions.
- Redacted evidence bundles, JUnit XML, and atomic report delivery.
- `agent-context` metadata and an optional espressoTUI dashboard.

______________________________________________________________________

## Learn more

- [Documentation contents](docs/contents.md) — index of the documentation set
- [Terms of reference](docs/terms-of-reference.md) — problem, users, and scope
- [Khufu design](docs/khufu-design.md) — architecture and contracts
- [Context](docs/context.md) — shared domain vocabulary
- [Roadmap](docs/roadmap.md) — planned delivery and progress
- [Users' guide](docs/users-guide.md) — using Khufu
- [Developers' guide](docs/developers-guide.md) — contributing and development

______________________________________________________________________

## Licence

ISC — see [LICENSE](LICENSE) for details.

______________________________________________________________________

## Contributing

Contributions are welcome. Please read [AGENTS.md](AGENTS.md) for code style,
quality gates, and commit conventions before opening a pull request.
