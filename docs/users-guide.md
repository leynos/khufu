# khufu Users' Guide

This guide is for consumer-repository maintainers, coding agents, and reviewers
who validate Kubernetes applications through Khufu. It documents the planned
user-facing contract and the repository's current quality gates. Khufu is
designed but not yet implemented, so treat every command, configuration key,
and report field here as a specification that later roadmap tasks implement and
this guide then tracks.

## Khufu status

Khufu is designed but not yet implemented. No `khufu` command, `.khufu.toml`
contract, or validation report is available yet, so the workflow and reference
sections below describe the planned interface and cannot be run today. The
[Khufu design](khufu-design.md) is the source of truth: the application
contract in §6.2, the command surface in §9, the agent-native protocol and exit
codes in §10, durable jobs in §11, and reports in §13. The
[roadmap](roadmap.md) sequences delivery; this guide will document each command
as it ships, starting with the Episodic golden path in phase 2.

## Prerequisites

The planned toolchain targets Linux with rootless container execution. Run
`khufu doctor` before the first validation to classify the host rather than
infer readiness from a distribution version. The design (§8.1) specifies these
host checks:

- Linux with rootless Podman, kind, kubectl, and Helm on `PATH`, at supported
  versions.
- A non-root user ID with subordinate ID mappings and cgroup v2 delegation.
- A working Podman connection that resolves to the local user.
- A usable systemd user session for detached jobs. Hosts without one use the
  foreground execution mode (see [Execution modes](#execution-modes)).
- Writable runtime, state, and cache directories with sufficient disk
  headroom.

Khufu never runs `sudo`, edits sysctls, changes global container configuration,
or switches to rootful containers. When a prerequisite fails, `doctor` reports
the supported value and a specific remediation that the maintainer applies
explicitly.

The Python baseline for working on Khufu itself is `3.14` (minimum: `3.12`).

## Application contract

Each consumer declares its deployable surfaces in a `.khufu.toml` file at the
repository root. The contract names the image, chart, chart bindings, data
services, environment bindings, and checks. It cannot select a cluster engine,
pin an operator version, or supply platform manifests; the schema rejects every
field listed as consumer-forbidden in the design (§4.2).

The following illustrative Corbusier contract shows the proposed schema version
1 and is reproduced from the design (§6.2):

```toml
schema_version = 1
application = "corbusier"

[image]
context = "."
dockerfile = "Dockerfile"

[chart]
path = "charts/corbusier"
values = ["charts/corbusier/values.local.yaml"]

[chart.bindings]
image_repository = "image.repository"
image_tag = "image.tag"
image_pull_policy = "image.pullPolicy"
application_secret = "existingSecretName"

[services.postgres]
database = "corbusier"
owner = "corbusier"
instances = 1
storage = "1Gi"

[services.cache]
client_protocol = "redis"
topology = "single-primary"

[environment.DATABASE_URL]
source = "postgres.application-uri"
codec = "postgresql-uri"

[environment.VALKEY_URL]
source = "cache.application-uri"
codec = "redis-uri"
```

A `postgres` declaration always uses the bundled CloudNativePG implementation,
and a `cache` declaration always uses the bundled Hyperspike Valkey
implementation. The application neither chooses nor versions them. A
`single-primary` topology expresses a client requirement, not a custom-resource
field.

Relative application paths resolve from the consumer repository root, not the
caller's working directory. An application contract cannot escape its own root.
Discovery is read-only and never imports application Python modules or runs
hooks. Unknown fields and unknown schema versions fail with JSON Pointer field
locations and the valid alternatives.

### Check execution and trust

Checks normally run as Kubernetes Jobs using the application image or a
separately pinned test image, with credentials supplied through Secret
references. An application-owned host test entrypoint instead requires explicit
trust authorization in the reviewed plan and runs through `cuprum` without a
shell. Host entrypoints may perform migrations, fixtures, or assertions, but
never provision or tear down infrastructure.

Host execution is trusted code, not a sandbox, so the reviewed plan is where
that trust is granted and the design (§6.3) defines the boundary. No template
expression evaluates arbitrary Python.

## Workspace and profiles

Two further inputs select how a contract runs:

- `khufu.workspace.toml` maps application IDs to local checkouts and selects
  an exact Khufu toolchain.
- A named user profile records host preferences, execution budgets, and
  delivery policy. Profiles never hold plaintext credentials.

When values conflict, precedence from highest to lowest is: explicit flags,
`KHUFU_*` environment variables, the selected profile, the workspace, the
application contract, and packaged defaults. The platform lock is a hard
compatibility constraint, not a layer in that order.

## Validation workflow

The planned workflow is a check, a plan, and a run. `doctor` is read-only.
`plan create` freezes sources and effects into a typed, redacted plan and
prints its plan ID. `run create` submits that frozen plan as a durable job and
can wait for its verdict.

```bash
# Read-only host prerequisite report
khufu doctor

# Freeze inputs and effects into a plan; note the plan ID it returns
khufu plan create --app ghillie --suite smoke --json

# Submit the plan as a durable job and wait for the verdict
khufu run create --plan <plan-id> \
  --idempotency-key ghillie-pr-42-smoke --wait --json
```

`run create` rejects a stale or incompatible plan rather than replanning under
an approved ID. A run creates a disposable environment unless the plan selects
an existing one. The design (§9) documents the full command surface; the
principal commands are:

| Command                                              | Contract                                                  |
| ---------------------------------------------------- | --------------------------------------------------------- |
| `khufu doctor`                                       | Read-only prerequisite report.                            |
| `khufu app list` / `get`                             | Discover contracts and capabilities without running them. |
| `khufu plan create` / `get`                          | Compute and optionally persist a typed, redacted plan.    |
| `khufu environment create` / `get` / `delete`        | Explicit environment lifecycle; mutations submit jobs.    |
| `khufu run create`                                   | Submit a validation job from a frozen plan.               |
| `khufu jobs get` / `list` / `cancel` / `resume`      | Inspect, reattach, cancel, or recover jobs.               |
| `khufu logs get`                                     | Bounded, redacted logs for a job, step, or resource.      |
| `khufu report get`                                   | Structured check report and artefact references.          |
| `khufu endpoint create` / `get` / `list` / `delete`  | Supervised loopback forwarding for an environment.        |
| `khufu profile create` / `update` / `get` / `delete` | Persistent host configuration, never credentials.         |
| `khufu agent-context`                                | Versioned, filterable machine-readable metadata.          |
| `khufu tui`                                          | Optional espressoTUI observer and command client.         |

_Table 1: Principal planned commands._

Every submitting mutation supports `--wait`, a finite execution `--timeout`,
`--idempotency-key`, `--dry-run`, and `--json`. `--wait-timeout` bounds the
observer only and never cancels an in-flight job. `jobs get` succeeds when it
retrieves a job, even a failed one; `jobs get --wait` and `run create --wait`
propagate the job's terminal outcome.

### Validation suites

A plan selects one or more suites. The design (§12) defines their coverage; the
essentials are:

- **Contract.** Parses the schemas, resolves required files, verifies lock and
  chart dependency hashes, runs Helm lint and deterministic rendering, and
  validates against the exact Kubernetes and CRD schemas, including namespace
  scope, Secret bindings, probes, volumes, and requested capabilities. Contract
  validation needs no running cluster.
- **Smoke.** Creates or verifies the rootless kind environment, installs the
  selected operators, proves service connectivity and authentication from
  inside the cluster, runs declared migrations, deploys the built image, checks
  liveness and readiness, and runs at least one non-health application
  operation. A database `SELECT 1` is not evidence that schema and business
  operations work.
- **Integration.** Executes application-owned, deterministic acceptance
  scenarios using local dependency fakes and synthetic credentials. Contacting
  a live external service, such as an AI provider, requires an explicit profile
  capability recorded as a distinct coverage mode; the default never spends API
  credits or contacts production systems.

Each consumer also has a minimum smoke contract in the design (§12.2), and the
generic bullets above do not lower it. Ghillie, for example, requires full
runtime configuration, the packaged PostgreSQL driver, domain endpoint
availability, and a deterministic report-domain scenario with the required
fixtures or fakes; a health-only profile cannot satisfy full smoke validation.
The other consumers have equivalent minimums recorded there.

A missing declared functional test blocks the corresponding validation level,
so a suite cannot report success by skipping the behaviour it exists to prove.
The GitOps and platform extension suites are deferred and appear in reports as
coverage exclusions until roadmap tasks deliver them.

## Machine-readable output

Non-interactive use is the default: ordinary commands do not prompt, and
missing inputs fail before side effects. JSON is the non-TTY default and is
always available through `--json`. Successful stdout contains exactly one JSON
document; failures emit one structured error document on stderr. Incidental
stderr chatter is suppressed in machine mode.

Every machine-mode success shares a stable outer envelope. Values below are
illustrative.

```json
{
  "schema_version": "1.0",
  "command": "run.create",
  "request_id": "req_671d",
  "status": "succeeded",
  "job_id": "job_93bd",
  "environment_id": "env_5c9a",
  "result": {
    "plan_id": "plan_7e4c",
    "report_id": "report_93bd",
    "checks": {"passed": 12, "failed": 0, "skipped": 0},
    "coverage": ["render", "deployment", "dependencies", "application-smoke"]
  },
  "artifacts": [],
  "warnings": [],
  "truncated": false,
  "next_cursor": null
}
```

Submission without waiting returns `status: accepted`, not `succeeded`. Errors
use the same versioned envelope and add a stable `error.code`, the offending
`field`, the `received` value, the `allowed` set, and whether the request is
`retryable`.

The exit code is a coarse classification for shells; the JSON error code
carries the precise category. The planned taxonomy is:

| Code  | Meaning                                             |
| ----- | --------------------------------------------------- |
| `0`   | Successful request or submission.                   |
| `2`   | Invalid input.                                      |
| `3`   | Host prerequisite failure.                          |
| `4`   | Missing resource.                                   |
| `5`   | Conflict or stale plan.                             |
| `6`   | Policy refusal.                                     |
| `7`   | Execution or infrastructure failure.                |
| `8`   | Failed validation checks.                           |
| `9`   | Deadline or observer wait expiry.                   |
| `10`  | Interrupted or indeterminate work.                  |
| `70`  | Internal defect.                                    |
| `130` | Client interrupted by SIGINT; the worker continues. |

_Table 2: Planned exit codes._

## Durable jobs

`run create` and environment mutations submit durable jobs. The ledger lives
under `$XDG_STATE_HOME/khufu`, falling back to `~/.local/state/khufu`, and
stores environments, plans, jobs, steps, idempotency keys, events, and artefact
references. It never stores secret values or credential-bearing command input.

Submission is idempotent. Resubmitting the same scope-qualified idempotency key
with the same plan returns the same job; reusing the key with a different plan
hash is a conflict (exit `5`). Two agents cannot concurrently mutate one
environment, because a worker holds a per-environment mutation lock for the
whole of a state-sensitive run.

A job moves from `queued` to `running` and then to `succeeded`, `failed`,
`cancelled`, `timed_out`, or `interrupted`. A queued job can be cancelled or
become interrupted before it starts. After a crash, recovery reconciles the
recorded worker identity and re-queries Kubernetes and Helm rather than
assuming an operation failed because a client lost its response. An operation
that cannot be safely replayed may end `indeterminate`. The design (§11)
defines the state machine.

Cancellation is explicit and is not rollback. For a queued job whose worker has
not started, `jobs cancel` moves it directly to `cancelled`; if the worker
start is unconfirmed, recovery reconciles the recorded unit name first and
stops any worker it finds. For a running job, Khufu records the request
durably, stops supervised subprocess groups with a bounded grace period, and
reconciles work Kubernetes has already accepted, stopping owned test Jobs where
necessary. Whether the environment is retained or deleted afterwards follows
the job's cleanup policy (§14), not the cancellation itself.

Cancelling a job is distinct from an observer timeout. `--wait-timeout` and an
expired deadline end only the local wait; the durable worker continues unless a
`jobs cancel` request stops it. The design (§11.5) defines the full sequence.

### Execution modes

On rootless Linux, each long operation runs in a named transient systemd user
service. A waiting terminal only observes; killing the waiting `khufu` process
does not kill its worker. User services are not assumed to survive logout or
reboot: after a reboot the ledger remains durable while execution has stopped,
and recovery marks the job interrupted.

Hosts without a usable systemd user session, including some CI runners, use a
foreground mode. It records foreground execution in the job and report and
states that losing the process interrupts execution; it never claims detached
durability.

## Reports and evidence

`khufu report get` returns the structured check report and artefact references.
`--deliver=stdout` returns a bounded structured report payload;
`--deliver=file:<path>` atomically writes the report or evidence bundle and
returns metadata. Binary archives never share stdout with a JSON envelope, and
unknown schemes return the supported set.

Each report records the source revision and frozen content fingerprint, image
identities, CLI and dependency versions, platform lock hash, chart artefact and
values hashes, environment identity, executed check IDs, execution mode,
timestamps, durations, outcomes, and coverage exclusions. It records the Khufu
release, platform lock digest, contract schema version, and application source
fingerprint, so different toolchains cannot masquerade as equivalent validation.

Reports distinguish `passed`, `failed`, `blocked`, `skipped`, and
`not_requested`. A required check cannot skip its way to success. A capability
that was not requested, such as ingress, appears as `not_requested` coverage
rather than implying that it works.

An evidence bundle contains the summary, canonical report JSON, JUnit XML, the
redacted plan, relevant rendered manifests, bounded Kubernetes events, Pod
status and termination data, available container logs, migration and test Job
results, Helm and Flux observations, and cleanup results. Failed Helm installs
and test Jobs keep their diagnostics before TTL cleanup, namespace deletion, or
any configured rollback removes them.

The primary validation failure and any cleanup failure are both preserved; a
cleanup problem never overwrites the original error. A failed required
leak-cleanup check prevents a disposable run from succeeding. The design
(§13.1) defines the bundle contents.

## Secrets and safety

Secrets are typed sensitive values. They never appear in CLI flags, profiles,
Helm values files, the ledger, artefact names, or URLs. Khufu prefers Secret
references and redacts stdout, stderr, logs, and persisted artefacts before
writing. Structured manifests have `data`, `stringData`, token fields,
kubeconfig credentials, and credential-bearing URLs removed.

Khufu does not promise perfect redaction of arbitrary application output. A
raw, unredacted bundle requires a separate, explicit, local-only action.
Private directories are user-only, sensitive files use mode `0600`, and output
paths are validated to refuse attacker-controlled symlinks.

## Environments and cleanup

An environment is a dedicated kind cluster owned by Khufu, identified by an ID
and proven by an environment marker recorded in the ledger. Names and labels
alone never prove ownership. Each environment has a private kubeconfig with mode
`0600`; Khufu never merges into or changes `~/.kube/config`.

A disposable environment defaults to retain-on-failure and delete-on-success,
after evidence collection. CI may select retain-never. A pre-existing
environment is retained unless a separate deletion operation authorizes its
destruction.

```bash
khufu environment delete env_5c9a --dry-run --json
khufu environment delete env_5c9a --force --allow-data-loss --wait --json
```

The delete plan determines whether `--allow-data-loss` is required. `--force`
authorizes deletion without prompting but never bypasses ownership, credential
policy, compatibility, or target checks. Deleting a kind environment removes
its node-local volumes; a stuck finalizer produces diagnostics, never an
automatic force-removal. The design (§14) defines the full cleanup sequence.

## Hosts and connectivity

Default connectivity is supervised, loopback-only port forwarding on allocated
high ports, via `khufu endpoint create`. Khufu records the target resource and
bound port only after the listener starts, avoiding fixed host-port collisions,
and never edits `/etc/hosts`.

The optional `ingress` capability installs the locked Traefik release with
explicit per-application hosts and ingress classes. Ingress checks run through
a loopback forward to Traefik with the appropriate `Host` header, separately
from direct service checks.

## Feedback

`khufu feedback create` records local friction reports that reference a command
or job ID with redacted free text. Khufu performs no automatic telemetry, issue
creation, upstream POST, or artefact upload unless a separately configured and
authorized delivery adapter is in use.

## Constraints and non-goals

The following are deliberate limits, not missing features:

- **Fixed substrate.** Linux, rootless Podman, kind, kubectl, and Helm only.
  There is no provider matrix, k3d or Docker path, rootful fallback, or plug-in
  cluster backend.
- **Local only.** Khufu does not create cloud resources, publish GitOps
  changes, alter real DNS, or require production credentials.
- **No host remediation.** Khufu does not run `sudo`, change sysctls, or edit
  global container configuration.
- **No umbrella chart or operator.** Consumers keep their own charts. Existing
  operators reconcile resources; Khufu sequences work, verifies conditions, and
  records evidence.
- **No production-property proof.** High availability, failover, backup and
  restore, and multi-host resilience are out of scope unless a separately
  requested extension suite runs them; otherwise they appear as coverage
  exclusions.
- **No legacy wrappers.** Khufu does not invoke the four existing preview
  scripts as permanent adapters.

## Interpreting a validation result

A successful run means the frozen plan's requested checks passed against the
recorded inputs. It does not mean every possible production property was
tested. When reading a report, confirm:

- The application source fingerprint and image identity match the change under
  review, including uncommitted inputs.
- The Khufu release and platform lock digest are the approved baseline.
- Every required check is `passed`; `blocked`, `skipped`, and `not_requested`
  entries are understood coverage exclusions.
- No check passed only because a health endpoint masked missing domain
  functionality; declared checks exercise real application behaviour.
- Cleanup results are present and separate from the validation outcome.

The design's release-acceptance list (§15.3) states the behaviours a
consolidated release must demonstrate; the [roadmap](roadmap.md) tracks which
are implemented.

## Repository quality gates

Before the first quality-gate run, initialize Git at the generated project root
with `git init`. Python source discovery and Markdown table formatting use Git
repository metadata.

Generated projects use `make all` as the standard local quality gate. It runs
these targets in order:

- `build`: create the local virtual environment and install development
  dependencies with `uv sync --group dev`.
- `check-fmt`: check Ruff formatting for Python sources and, when Rust is
  enabled, `cargo fmt` for the Rust extension.
- `lint`: run `lint-python` and, when Rust is enabled, `lint-rust`.
- `typecheck`: run `ty check`.
- `test`: run pytest and, when Rust is enabled, Rust tests.
- `spelling`: regenerate `typos.toml` and check repository-wide spelling.

Run `make markdownlint` separately to lint Markdown and run the same spelling
gate. Run `make audit` separately to check dependencies with `pip-audit` and,
when Rust is enabled, `cargo audit`.

The Python baseline is `3.14` (minimum: 3.12).

Git discovers Python sources from tracked and untracked files, including hidden
action directories. `lint-python` runs Ruff 0.16.8 and Interrogate for 100%
docstring coverage, followed by the pinned base Pylint (`PYLINT_VERSION`). It
uses the interpreter selected for the baseline:

uv-managed CPython 3.14 (`PYLINT_PYTHON`)

The base sweep keeps `syntax-error` enabled, so a module that the interpreter
cannot parse fails linting rather than being skipped.

The DF12 Python Lints v0.4.0 Pylint plugin adds its configured project rules.
DF12 Pylint, Ambrleaks, Skylos, Vulture, and the duplication detector run as
isolated tools on Python 3.14. Ambrleaks checks `tests/`; Skylos checks the
repository, and Vulture checks test helpers. The duplication gate installs its
pinned Nose detector with the shared verified installer before checking
duplication families. `make lint-actions` validates GitHub Actions sources with
actionlint, action-validator, yamllint, and shellcheck.

Ruff and `ty` run as isolated tools on Python 3.14; `ty` is pinned to 0.0.56.
The Makefile pins mdtablefix to 0.6.1 for Markdown table formatting. CI
installs these CLI tools and runs `make markdownlint`.

The spelling target regenerates `typos.toml` from the live shared dictionary
and the `typos.local.toml` overlay on every run, so `typos.toml` is never drift
checked in continuous integration. Run `make spelling` directly when updating
documentation; commit the regenerated `typos.toml`. An ignored local cache
remains usable when the shared source is temporarily offline.

Pytest discovery is limited to the top-level `tests/` tree. Keep generated
project unit tests there rather than in package module directories or
`unittests/` subdirectories, because CI coverage runs through xdist-backed
SlipCover support.

When the Rust extension is enabled, `lint-rust` runs:

- `cargo doc` with warnings denied;
- `cargo clippy` with the generated Clippy configuration; and
- Whitaker with `whitaker --all`.

The generated Makefile never installs Whitaker; it fails with a clear error
when the wrapper is missing. Install it yourself with `whitaker-installer` (see
<https://github.com/leynos/whitaker>) before running local Rust linting.

## Dependency auditing

Run `make audit` to check generated project dependencies for known
vulnerabilities. All generated projects run `pip-audit` against the Python
environment created by `uv sync --group dev`. CI skips `make audit` for
Dependabot pull requests; a weekly scheduled audit on the default branch is the
compensating control. Rust-enabled projects also run `cargo audit` from the
`rust_extension` crate directory.

## Scheduled mutation testing

The `.github/workflows/mutation-testing.yml` workflow runs mutation testing
daily at 09:30 UTC and can also be started manually from GitHub Actions. Adjust
the generated cron schedule to stagger it against other repositories.

For projects whose minimum Python version is 3.13 or newer, the workflow runs
mutmut against `khufu/`. The Python mutation job is omitted for older baselines
because the shared workflow helpers require Python 3.13 or newer.

## Rust test behaviour

Rust-enabled projects use `cargo nextest run` when `cargo-nextest` is
available. If `cargo-nextest` is not installed, the generated `test` target
falls back to `cargo test`. Rust documentation tests still run through
`cargo test --doc`.

If cargo is missing from the local environment, generated Rust test targets
fail early with a clear error instead of falling through to an unusable `cargo`
invocation.

## Local GitHub Actions validation

The generated Makefile supports optional local workflow validation using
[`act`](https://github.com/nektos/act). When `act` is installed and Docker is
available, pass `WITH_ACT=1` to the `test` target:

```bash
make test WITH_ACT=1
```

This sets `RUN_ACT_VALIDATION=1` for the pytest invocation, enabling the
act-based integration tests that run the generated CI workflow locally. Omitting
`WITH_ACT` (or setting it to `0`) skips act validation; the rest of the test
suite runs unchanged.

## Cleaning local state

Run `make clean` to remove local build and cache outputs, including `.venv`,
`.uv-cache`, `.uv-tools`, Python cache directories, coverage outputs, and Rust
`target` output when the Rust extension is enabled.
