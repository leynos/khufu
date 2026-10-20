# Khufu roadmap

This roadmap translates the [Khufu design](khufu-design.md) and the
[terms of reference](terms-of-reference.md) into an outcome-oriented delivery
sequence. It does not promise dates. Each phase carries one testable idea at
the GIST level: the steps beneath a phase work toward validating or falsifying
that idea, and each task is a review-sized execution unit with its
dependencies, design citations, and success criteria.

The sequence follows the extraction order in khufu-design.md §16: capture the
demonstrated baseline, extract Episodic's execution path, integrate Corbusier's
hosting model, migrate Wildside and Ghillie, then remove the legacy sources of
drift. Follow the [documentation style guide](documentation-style-guide.md) for
four-digit filenames: ADRs use `docs/adrs/adr-nnnn-title-slug.md`, and Requests
for Comments (RFCs) use `docs/rfcs/rfc-nnnn-title-slug.md`. Terminology follows
[context](context.md).

## 1. Foundational contracts and demonstrated baseline

Idea: if Khufu ratifies its implementation home, fixed substrate, and
supervision model, records the demonstrated Episodic and Corbusier baselines as
executable fixtures, and settles its machine-facing contracts before any
cluster code exists, then the first live slice can extract working behaviour
without reopening substrate choices or reworking the command surface.

### 1.1. Ratify the decisions that would otherwise force rework

This step answers which choices Khufu treats as settled and which remain open.
Its outcome fixes the repository boundary, the absence of a provider plug-in
interface, and the worker ownership model that every later step assumes. See
khufu-design.md §§1-2 and §18.

- [ ] 1.1.1. Record the implementation-home decision as
  `docs/adrs/adr-0001-implementation-home.md`.
  - Decide that `leynos/khufu` hosts the implementation and that Nile Valley
    hosts `validation-estate.toml` and the regression matrix.
  - Record the divergence from the source design's Nile Valley home and the
    consequences for release and pinning.
  - See khufu-design.md §4.3 and §18.
  - Success: one accepted ADR names the code home, the estate-manifest home,
    and the release channel consumers pin.
- [ ] 1.1.2. Record the fixed substrate decision as
  `docs/adrs/adr-0002-fixed-kind-rootless-substrate.md`.
  - Requires 1.1.1.
  - State that Linux, rootless Podman, kind, kubectl, and Helm are the only
    supported stack, with no `--provider`, `--engine`, k3d, Docker, rootful
    fallback, or alternate-cluster plug-in interface.
  - Record that test doubles isolate effects without becoming production
    extension points.
  - See khufu-design.md §2 and §17.
- [ ] 1.1.3. Record the job supervision decision as
  `docs/adrs/adr-0003-systemd-user-service-supervision.md`.
  - Requires 1.1.1.
  - Decide that transient systemd user services own workers, that waiting
    CLIs are observers, and that a foreground-only mode is deferred.
  - Record session-survival limits that `doctor` must report.
  - See khufu-design.md §11.3.
- [ ] 1.1.4. Record where the typed fixture specifications shared with Nile
  Valley's GitOps path live as
  `docs/adrs/adr-0004-shared-fixture-specifications.md`.
  - Requires 1.1.1.
  - Decide the owning repository, the consumption mechanism on each side, and
    how versions stay aligned with the platform lock.
  - See khufu-design.md §3.1 and §18.
  - Success: Khufu's renderers and Nile Valley's GitOps rendering consume one
    specification source.

### 1.2. Capture the demonstrated baseline as regression fixtures

This step answers exactly what "working" means for the paths Khufu extracts.
Its outcome seeds the platform lock and the golden-path assertions, so later
extraction can be judged by parity rather than memory. See khufu-design.md §3,
§7.1, and §16.

- [ ] 1.2.1. Capture Episodic's working local validation path as a baseline
  record under `tests/fixtures/baseline/episodic/`.
  - Requires 1.1.2.
  - Record host prerequisites, tool, image, and chart versions, the kind
    configuration and node image digest, command order, and success
    criteria from the known working run.
  - Reconcile differences against the inspected Episodic snapshot explicitly
    rather than copying older configuration.
  - Success: the record lists every command and version needed to reproduce
    the demonstrated run, and each divergence from the inspected source is
    annotated.
- [ ] 1.2.2. Capture Corbusier's operator-hosting model as a baseline record
  under `tests/fixtures/baseline/corbusier/`.
  - Requires 1.1.2.
  - Record CloudNativePG (CNPG) and Hyperspike Valkey installation, namespace
    ownership, custom resources, credential flow, and the application Secret
    binding model.
  - Record the Valkey group, version, and kind actually emitted against the
    upstream definition, flagging the inconsistency in khufu-design.md §3.2.
  - Success: the record identifies every resource Corbusier creates and which
    fields Khufu must preserve.
- [ ] 1.2.3. Write the source-hazard register as regression cases.
  - Requires 1.2.1 and 1.2.2.
  - Encode each hazard in khufu-design.md §3.2 (Valkey resource identity,
    Ghillie environment naming and driver packaging, Kubernetes version
    constraints, credential URI schemes, image short-name resolution, empty
    ingress hosts) as a named, initially failing or pending case.
  - Success: every hazard has a case ID that a later task closes.

### 1.3. Qualify the Python 3.14 runtime and library boundary

This step answers whether the required libraries install, import, and shut down
cleanly on CPython 3.14 from locked wheels. Its outcome removes packaging risk
from the first live slice. See khufu-design.md §§5.3-5.4.

- [ ] 1.3.1. Add locked runtime dependencies on Cyclopts, cuprum,
  femtologging, and espressoTUI with exact versions and distribution hashes.
  - Requires 1.1.1.
  - Use a published femtologging wheel; reject any resolution that compiles
    a Rust toolchain at install time.
  - Success: `uv sync` on a clean CPython 3.14 host installs from wheels only,
    and the lock records hashes for every distribution.
- [ ] 1.3.2. Lay out the `khufu/` package boundaries with enforced import
  direction.
  - Requires 1.3.1.
  - Create `domain`, `application`, `ports`, `adapters`, `cli`, `tui`,
    `schemas`, `platform`, and `skills` packages under `khufu/`.
  - Add an import-boundary check that fails when `domain` imports adapters,
    subprocess, logging, or terminal code, and when machine-mode code
    imports `espresso`.
  - See khufu-design.md §§5.1-5.2.
  - Success: the boundary check runs in `make lint` and fails on a seeded
    violation.
- [ ] 1.3.3. Implement the femtologging adapter with pre-handler redaction and
  explicit shutdown.
  - Requires 1.3.2.
  - Serialize application-owned event objects before handing them to
    handlers; logging failure must never produce a success result.
  - See khufu-design.md §5.3 and §13.3.
  - Success: a failing handler leaves command outcomes unchanged, and
    shutdown flushes without hanging under pytest's timeout.
- [ ] 1.3.4. Implement the cuprum command catalogue and typed builders for
  `podman`, `kind`, `kubectl`, and `helm`.
  - Requires 1.3.2.
  - Expose no arbitrary `exec` entry point; restrict permitted subcommands
    through typed builders and target validation.
  - Success: a builder cannot emit an unlisted subcommand, and Hypothesis
    property tests show no builder output contains shell metacharacter
    interpretation or an implicit kube-context.

### 1.4. Settle the machine-facing command contract

This step answers whether one descriptor registry can generate the CLI, help,
and agent context while keeping machine output and errors stable. Its outcome
is the headless contract every later command inherits. See khufu-design.md
§§9-10.

- [ ] 1.4.1. Implement the command descriptor registry and Cyclopts
  registration generated from it.
  - Requires 1.3.2.
  - Record effect class, parameters, enums, schemas, asynchronous behaviour,
    and examples per descriptor.
  - Reject banned aliases and inconsistent flag vocabulary at registry load.
  - See khufu-design.md §5.3 and §10.1.
  - Success: CI fails when a descriptor introduces a banned alias or an
    inconsistent flag name.
- [ ] 1.4.2. Implement the success and error envelopes, exit taxonomy, and
  output-channel rules.
  - Requires 1.4.1.
  - Emit exactly one JSON document on stdout in machine mode, one structured
    error on stderr, and no ANSI or prompts; make JSON the non-TTY default.
  - Adapt Cyclopts parse errors before Cyclopts prints or exits.
  - See khufu-design.md §§10.2-10.4.
  - Success: Hypothesis-generated malformed argv always yields a
    schema-valid error envelope with an exit code from the taxonomy.
- [ ] 1.4.3. Implement bounded responses: list pagination, log line and byte
  limits, and the 64 KiB structural summary cap with cursors.
  - Requires 1.4.2.
  - Success: no response exceeds its bound, and no truncation produces
    invalid JSON.
- [ ] 1.4.4. Implement `khufu agent-context` and `khufu skill-path`.
  - Requires 1.4.1.
  - Default to a bounded index; expand with `--command`, `--application`,
    and `--detail`.
  - Validate packaged `SKILL.md` examples against the generated surface.
  - See khufu-design.md §10.5.
  - Success: a skill example that names an unknown flag fails CI.
- [ ] 1.4.5. Implement profiles with documented precedence and value
  provenance.
  - Requires 1.4.2.
  - Support `khufu profile create`, `update`, `get`, `list`, and `delete`;
    reject plaintext credential values.
  - See khufu-design.md §6.1 and §9.
  - Success: `profile get --json` reports the source layer of each effective
    value, and a credential-shaped value is refused.

### 1.5. Define the versioned schemas for contracts, plans, and reports

This step answers whether application contracts can express each consumer's
needs while rejecting infrastructure selection. Its outcome is the schema set
that discovery and planning consume. See khufu-design.md §6 and §13.1.

- [ ] 1.5.1. Implement the `.khufu.toml` application contract schema and
  read-only discovery.
  - Requires 1.4.2.
  - Reject unknown fields and versions with JSON Pointer locations and the
    allowed set; reject cluster-engine, operator, chart-version, raw
    manifest, and lifecycle-hook fields.
  - Resolve relative paths from the application root; forbid escape.
  - See khufu-design.md §§6.1-6.2 and §4.2.
  - Success: Hypothesis-generated contracts with injected forbidden fields
    are always rejected with the offending pointer.
- [ ] 1.5.2. Implement the `khufu.workspace.toml` schema and exact toolchain
  pin validation.
  - Requires 1.5.1.
  - Success: a floating or non-matching toolchain pin fails with a stable
    error code.
- [ ] 1.5.3. Implement the check declaration and trust model.
  - Requires 1.5.1.
  - Require ID, category, dependencies, executor, finite deadline, required
    status, result schema, and expected artefacts; require explicit trust
    authorization for host entrypoints.
  - See khufu-design.md §6.3.
  - Success: a host entrypoint without trust authorization is a policy
    refusal before any side effect.
- [ ] 1.5.4. Implement `khufu app list` and `khufu app get`.
  - Requires 1.5.1 and 1.4.3.
  - Success: discovery never imports application Python modules or runs
    hooks, verified by a fixture contract whose repository contains a
    trapped module.

## 2. Vertical slice 1: Episodic golden path through Khufu

Idea: if Episodic's demonstrated rootless kind validation runs end to end
through Khufu's durable, agent-native job model with parity to the baseline,
then one shared implementation can carry the estate's execution path, and
Episodic can retire its independent cluster code.

This slice delivers a usable `plan create` and `run create` loop for one
consumer. Episodic's existing raw PostgreSQL bootstrap is characterized by a
short-lived extraction fixture only; it is not a public Khufu capability and is
replaced in phase 3. See khufu-design.md §16.

### 2.1. Prove the host and cluster target can be trusted

This step answers whether Khufu can diagnose a rootless host and create a kind
environment whose identity it can prove before every mutation. Its outcome
guards every later effect. See khufu-design.md §§8.1-8.3.

- [ ] 2.1.1. Implement `khufu doctor` as a read-only prerequisite report.
  - Requires steps 1.3-1.4.
  - Check executables and versions, rootless UID, Podman connection locality,
    cgroup v2 and delegation, user systemd, subordinate IDs, writable XDG
    directories, disk headroom, and networking prerequisites.
  - Never run sudo, change sysctls, or edit global container configuration.
  - Success: each finding carries a stable code, the supported value, and
    remediation text; a cmd-mox suite proves doctor issues no mutating
    command.
- [ ] 2.1.2. Implement kind environment creation on rootless Podman with an
  environment marker and platform fingerprint.
  - Requires 2.1.1 and 1.2.1.
  - Set `KIND_EXPERIMENTAL_PROVIDER=podman`, use a delegated user scope when
    required, and record the effective cluster configuration and node image
    digest.
  - See khufu-design.md §8.2.
- [ ] 2.1.3. Implement private kubeconfig handling and pre-mutation target
  verification.
  - Requires 2.1.2.
  - Write a mode `0600` kubeconfig per environment; pass its path and context
    explicitly; never touch `~/.kube/config`.
  - Verify node container identity, API server CA fingerprint, and the
    environment marker UID before every mutation.
  - Success: an E2E test shows that a wrong ambient context, a similarly
    named cluster, a stale marker, a changed CA, or a wrong Podman
    connection each refuses the mutation with exit code `6`.

### 2.2. Prove the durable job model before long effects depend on it

This step answers whether submission, supervision, and reconciliation are safe
enough to own multi-minute cluster work. Its outcome lets every later mutation
run as a job. See khufu-design.md §11.

- [ ] 2.2.1. Implement the SQLite ledger under `$XDG_STATE_HOME/khufu`.
  - Requires 1.5.1.
  - Use transactions, foreign keys, and WAL; store environments, plans, jobs,
    steps, inventories, idempotency keys, events, and artefact references.
  - Refuse network filesystems and repository paths.
  - See khufu-design.md §11.1.
  - Success: a schema check proves no column can hold secret values.
- [ ] 2.2.2. Implement the job and step state machines in the pure domain.
  - Requires 2.2.1.
  - Record intent before effect and observed outcome afterwards for every
    step, with a retry and recovery classification.
  - See khufu-design.md §11.4.
  - Success: a Hypothesis `RuleBasedStateMachine` shows no sequence of
    events reaches an illegal transition or loses a recorded intent.
- [ ] 2.2.3. Implement submission with scope-qualified idempotency keys.
  - Requires 2.2.2.
  - Success: resubmitting a key with the same plan hash returns the same
    job, and a different plan hash returns a conflict with exit code `5`.
- [ ] 2.2.4. Implement transient systemd user-service supervision of workers.
  - Requires 2.2.3 and 1.1.3.
  - Commit the job before starting the unit; record and verify the unit
    identity; reconcile the commit-to-start crash window by unit name.
  - See khufu-design.md §11.3.
- [ ] 2.2.5. Implement per-environment mutation locks and the
  `jobs get`, `list`, `cancel`, `resume`, and `prune` commands.
  - Requires 2.2.4.
  - Support `--wait` and `--wait-timeout` without coupling observer expiry to
    execution; cancellation stops supervised process groups and then
    reconciles; pruning never deletes clusters.
  - See khufu-design.md §§11.5-11.6 and §9.
  - Success: two concurrent submissions against one environment serialize,
    and a wait timeout exits `9` while the job continues.

### 2.3. Deploy Episodic's image and chart through the shared path

This step answers whether frozen builds, image transport, and direct Helm
execution reproduce the baseline deployment. Its outcome is the first real
application running under Khufu. See khufu-design.md §8.4, §7.4, and §6.2.

- [ ] 2.3.1. Implement frozen build contexts and qualified, uniquely tagged
  image builds.
  - Requires 2.2.2.
  - Fingerprint staged content including uncommitted and untracked inputs,
    Dockerfile, build parameters, and platform; record the image ID or OCI
    digest separately.
  - Success: modifying a working-tree file after plan creation is detected
    before the build, and two parallel builds never share an archive path.
- [ ] 2.3.2. Implement image archive export and kind import with cleanup on
  success, failure, and cancellation.
  - Requires 2.3.1 and 2.1.3.
  - Use pull policy `Never` where the chart allows it; never fall back to
    pulling after a failed import.
  - Success: the deployed Pod's image ID matches the imported image ID.
- [ ] 2.3.3. Implement lock-aware direct Helm deployment driven by chart
  bindings.
  - Requires 2.3.2 and 1.5.1.
  - Record the executor for every release; refuse a release already owned
    by another executor.
  - See khufu-design.md §4.1.
- [ ] 2.3.4. Add the temporary Episodic PostgreSQL extraction fixture.
  - Requires 2.3.3 and 1.2.1.
  - Characterize the existing bootstrap, `DATABASE_URL`, and database-aware
    readiness behind a test-only adapter that the public contract schema
    cannot select.
  - Success: the fixture is unreachable from `.khufu.toml` and is listed for
    removal in 3.3.2.

### 2.4. Deliver the agent-native plan and run loop

This step answers whether an agent can validate Episodic in two calls and
recover from any interruption. Its outcome is the headless product surface. See
khufu-design.md §§9-10 and §12.

- [ ] 2.4.1. Implement `khufu plan create` and `khufu plan get`.
  - Requires 2.3.3 and 1.5.3.
  - Freeze sources, artefacts, compatibility, and effects into a redacted,
    hashed plan; support `--dry-run` without installing anything.
  - Success: the same inputs produce the same plan hash, and a stale input
    changes it.
- [ ] 2.4.2. Implement `khufu run create` with readiness predicates and
  explicit checks.
  - Requires 2.4.1 and step 2.2.
  - Reject stale or incompatible plans; require non-empty expected resource
    sets and endpoints; never pass on a selector that matches nothing.
  - See khufu-design.md §7.4 and §12.1.
  - Success: a required check without its executable reports `blocked`, not
    `skipped`, and the run fails with exit code `8`.
- [ ] 2.4.3. Implement `khufu environment create`, `update`, `get`, `list`,
  and `delete` as job-submitting commands.
  - Requires 2.4.2.
  - Support `--wait`, `--timeout`, `--idempotency-key`, `--dry-run`, and
    `--json` on every mutation.
- [ ] 2.4.4. Implement `khufu endpoint create`, `get`, `list`, and `delete`.
  - Requires 2.4.3.
  - Bind loopback-only, allocated high ports and record the port only after
    the listener starts.
  - See khufu-design.md §8.5.

### 2.5. Prove evidence, secrets, and cleanup are trustworthy

This step answers whether a run leaves honest evidence and nothing dangerous
behind. Its outcome is a report that states exactly what was demonstrated. See
khufu-design.md §§13-14.

- [ ] 2.5.1. Implement the report model and `khufu report get` with stdout
  and atomic file delivery.
  - Requires 2.4.2.
  - Record Khufu release, platform lock digest, contract schema, source
    fingerprint, image identities, check outcomes, coverage, and
    exclusions; emit canonical JSON and JUnit XML.
  - Success: unknown delivery schemes return the supported set, and file
    delivery never follows an attacker-controlled symlink.
- [ ] 2.5.2. Implement bounded, redacted evidence collection and
  `khufu logs get`.
  - Requires 2.5.1.
  - Collect events, Pod status, current and previous logs, Job results, and
    rendered manifests before any cleanup removes them.
  - Parse manifests to omit `data`, `stringData`, tokens, kubeconfig
    credentials, and credential-bearing URLs.
- [ ] 2.5.3. Implement inventory-driven cleanup with retain-on-failure
  defaults and orphan reporting.
  - Requires 2.5.2.
  - Keep cleanup failures separate from the primary failure; require
    `--allow-data-loss` where the delete plan says so; report orphaned
    candidates when the ledger lacks them.
  - See khufu-design.md §14.
  - Success: `--force` never deletes an unrecognized cluster.
- [ ] 2.5.4. Implement `khufu feedback create`, `get`, and `list`.
  - Requires 2.5.1.
  - Store local records only; no upstream transmission.
  - See khufu-design.md §13.4.

### 2.6. Prove the Episodic slice end to end

This step answers whether the extracted path matches the baseline under real
failure conditions. Its outcome gates Episodic's migration. See khufu-design.md
§15.

- [ ] 2.6.1. Build the Episodic golden-path E2E suite on a real rootless kind
  host.
  - Requires steps 2.1-2.5.
  - Success: `plan create` then `run create --wait` passes the smoke suite
    with parity to the baseline in 1.2.1, and both cold creation and
    existing-environment reconciliation pass.
- [ ] 2.6.2. Build the interruption E2E suite.
  - Requires 2.6.1.
  - Kill the waiting CLI, then kill the worker at intent, effect, and record
    boundaries; restart and reconcile.
  - Success: killing the CLI never kills the worker, and every worker kill
    either reconciles the existing effect or reports `indeterminate`.
- [ ] 2.6.3. Build the secret-canary E2E suite.
  - Requires 2.6.1.
  - Seed canaries in raw, URI-escaped, and base64 forms.
  - Success: no canary appears in stdout, stderr, plans, the ledger, logs,
    or evidence bundles from the standard collectors.
- [ ] 2.6.4. Switch Episodic's local validation entry point to Khufu behind a
  thin delegate.
  - Requires 2.6.1 to 2.6.3.
  - Success: Episodic's golden-path validation passes through Khufu before
    its independent cluster implementation is removed in 5.3.1.

## 3. Vertical slice 2: Shared data services on one platform lock

Idea: if CNPG and Hyperspike Valkey can be provisioned, qualified, and bound
through one centrally owned implementation that serves both Episodic and
Corbusier with equivalent application outcomes, then data services need no
per-repository infrastructure code, and the consolidated data-service release
can ship.

### 3.1. Qualify the shared operators in the platform lock

This step answers which exact operator, CRD, and image tuple the estate
supports, and whether it reconciles from cold and from existing state. See
khufu-design.md §7.1 and §7.4.

- [ ] 3.1.1. Implement `platform.lock.toml` packaging, fingerprinting, and
  qualification-evidence references.
  - Requires 1.2.2 and 2.1.2.
  - Fail on missing CRD schema coverage for any required resource.
  - Success: the compatibility intersection of chart ranges, the node image,
    and operator requirements is computed, and an empty intersection fails
    before deployment.
- [ ] 3.1.2. Implement operator installation with CRD establishment and
  controller and webhook availability gates.
  - Requires 3.1.1.
  - Never deploy custom resources before their CRDs are established; route
    CRD upgrades only through a platform-upgrade plan or recreation.
  - See khufu-design.md §7.4.

### 3.2. Bind data services to applications safely

This step answers whether typed renderers and bindings can satisfy each
consumer's client contract without exposing secrets. See khufu-design.md
§§7.2-7.3 and §6.2.

- [ ] 3.2.1. Implement the CNPG renderer and per-application cluster and
  user provisioning.
  - Requires 3.1.2.
  - Use one instance in the small profile; mark HA, failover, backups, and
    restore as coverage exclusions; read only the application Secret and
    use the managed service endpoint.
- [ ] 3.2.2. Implement the Hyperspike Valkey renderer with qualified resource
  identity and topology.
  - Requires 3.1.2 and 1.2.3.
  - Emit the group, version, and kind verified against the locked CRD;
    translate `single-primary` from the locked resource shape, not a raw
    `replicas` field.
  - Success: an invalid group, version, or kind, or a mismatched topology,
    fails before application deployment, and an unsupported topology
    returns `UNSUPPORTED_SERVICE_TOPOLOGY`.
- [ ] 3.2.3. Implement typed bindings and codecs for `postgresql-uri` and
  `redis-uri`.
  - Requires 3.2.1 and 3.2.2.
  - Record source Secret identity and resource version without contents;
    refresh bindings deliberately when a source changes.
  - Success: Hypothesis round-trip properties prove codecs percent-encode
    every credential byte correctly.
- [ ] 3.2.4. Implement in-cluster data-service checks.
  - Requires 3.2.3.
  - Prove PostgreSQL authentication and Valkey authenticated `PING`, a
    namespaced write, read, and delete, and declared transaction behaviour.

### 3.3. Move Episodic and onboard Corbusier on the shared services

This step answers whether both baseline consumers reach equivalent application
outcomes on one implementation. See khufu-design.md §12.2 and §16.

- [ ] 3.3.1. Migrate Episodic's database to the CNPG path.
  - Requires step 3.2 and 2.6.4.
  - Preserve bootstrap semantics, writable mounts, migrations, and
    readiness; keep object-store persistence an explicit capability.
  - Success: Episodic's smoke suite passes with migrations and a declared
    application operation on CNPG.
- [ ] 3.3.2. Remove the Episodic PostgreSQL extraction fixture.
  - Requires 3.3.1.
  - Success: no raw PostgreSQL code path remains in Khufu.
- [ ] 3.3.3. Write Corbusier's `.khufu.toml` and run it on the shared kind
  path.
  - Requires step 3.2.
  - Preserve its chart contract and client URI requirements.
  - Success: Corbusier's smoke suite passes PostgreSQL and Valkey
    authentication, migrations, and a declared operation using both services.
- [ ] 3.3.4. Build the combined-stack E2E suite for Episodic and Corbusier.
  - Requires 3.3.2 and 3.3.3.
  - Run both consumers in one environment and in separate environments.
  - Success: deleting one application leaves the other's data and the
    shared operators intact, and the consolidated data-service release is
    tagged only after this suite passes.

## 4. Vertical slice 3: Wildside and Ghillie on the shared contract

Idea: if Wildside and Ghillie can express their differing chart bindings,
session keys, and dependencies declaratively, and any application defects
surface as failed checks rather than infrastructure forks, then the contract is
general enough for the whole estate.

### 4.1. Onboard Wildside without unnecessary dependencies

This step answers whether a consumer with no data services and a narrow
Kubernetes range fits the contract. See khufu-design.md §3.2 and §12.2.

- [ ] 4.1.1. Implement create-once generated Secrets for session keys.
  - Requires phase 3.
  - Preserve existing keys unless a separate operation authorizes rotation;
    transport payloads through stdin or protected storage.
  - See khufu-design.md §13.2.
- [ ] 4.1.2. Write Wildside's `.khufu.toml` and resolve its Kubernetes
  compatibility intersection.
  - Requires 4.1.1 and 3.1.1.
  - Do not add PostgreSQL or Valkey; honour the chart's declared range.
  - Success: Wildside passes its health contract, session-key mount check,
    and a declared non-health operation, or the plan fails with an explicit
    empty-intersection error.
- [ ] 4.1.3. Widen Wildside's chart Kubernetes range in the Wildside
  repository when 4.1.2 reports an empty intersection.
  - Requires 4.1.2.
  - Justify the widened range with tests against the locked node image; skip
    this task, recording the resolved version, when the intersection is
    non-empty.
  - See khufu-design.md §3.2 and §7.1.
  - Success: Wildside's plan resolves a Kubernetes version shared with the
    other consumers and the operator bundle.

### 4.2. Onboard Ghillie with its application corrections

This step answers whether a health endpoint can be prevented from masking
missing domain functionality. See khufu-design.md §3.2, §6.3, and §12.2.

- [ ] 4.2.1. Write Ghillie's `.khufu.toml` with its nested Secret binding and
  `GHILLIE_DATABASE_URL`.
  - Requires phase 3.
  - Choose a codec compatible with the asynchronous driver packaged in its
    image.
- [ ] 4.2.2. Land Ghillie's runtime-driver packaging correction in the Ghillie
  repository.
  - Requires 4.2.1.
  - Promote `asyncpg` to runtime dependencies and verify it in the built
    image.
  - Success: the packaged-image test fails before the change and passes
    after it.
- [ ] 4.2.3. Add Ghillie's deterministic report-domain smoke scenario.
  - Requires 4.2.2.
  - Success: a health-only profile cannot satisfy full smoke validation, and
    the scenario passes against the built runtime image.

### 4.3. Prove routing and coexistence across all four consumers

This step answers whether four applications can share one environment without
collisions. See khufu-design.md §8.5 and §15.2.

- [ ] 4.3.1. Implement the optional `ingress` capability with pinned Traefik
  and planner-generated hosts.
  - Requires 3.1.2.
  - Reject ambiguous or empty hosts; validate through a loopback forward
    with the correct Host header; report `not_requested` when disabled.
- [ ] 4.3.2. Build the four-application coexistence E2E suite.
  - Requires 4.1.3, 4.2.3, and 4.3.1.
  - Success: all four consumers coexist without conflicting namespaces,
    release names, Secrets, image tags, or ingress routes, and two
    worktrees remain isolated.
- [ ] 4.3.3. Build the combinatorial suite over consumers, suites, and
  capabilities.
  - Requires 4.3.2.
  - Cover each consumer against contract and smoke suites with ingress on
    and off, existing versus disposable environments, and each cleanup
    policy, using pairwise selection for the live portion.
  - See khufu-design.md §15.2.
  - Success: every pair of options appears in at least one live run, and
    the full product passes the contract suite offline.

## 5. Vertical slice 4: Drift elimination and estate governance

Idea: if the estate's pins, contract versions, and platform fingerprints are
checked centrally and the legacy helpers are deleted once parity holds, then
drift cannot silently re-enter, and the first consolidated release can
truthfully claim that all four consumers share one implementation.

### 5.1. Stand up the central regression matrix

This step answers whether shared infrastructure changes are tested against
every consumer before release. See khufu-design.md §4.3 and §15.

- [ ] 5.1.1. Define `validation-estate.toml` in Nile Valley.
  - Requires 1.1.1 and phase 4.
  - Record the approved Khufu release and each consumer revision.
- [ ] 5.1.2. Implement foreground execution for hosts without a usable
  systemd user session.
  - Requires 1.1.3 and 2.2.4.
  - Record foreground execution in the job and report; losing the process
    marks the job interrupted rather than claiming detached durability.
  - See khufu-design.md §11.3.
  - Success: a job on a host without user systemd completes in the
    foreground, and its report states the weaker durability guarantee.
- [ ] 5.1.3. Implement the resource-bounded rootless kind regression matrix
  in Nile Valley CI.
  - Requires 5.1.1 and 5.1.2.
  - Success: a Khufu candidate is marked supported only when all four
    consumers pass their contract and smoke suites.

### 5.2. Detect drift in pins and copied machinery

This step answers whether CI can tell legacy orchestration apart from
legitimate application tests. See khufu-design.md §4.2.

- [ ] 5.2.1. Implement pin, contract schema, and platform fingerprint drift
  checks.
  - Requires 5.1.1.
  - Success: a consumer with a divergent bootstrap pin or contract version
    fails CI with the expected baseline in the message.
- [ ] 5.2.2. Implement scoped repository checks for copied infrastructure
  machinery.
  - Requires 5.2.1.
  - Detect operator manifests, kind or Helm invocations, and copied shared
    modules outside thin delegates, while allowing application tests and
    explanatory documentation.

### 5.3. Retire the legacy helpers

This step answers whether every consumer can run without its independent
orchestration. See khufu-design.md §16.

- [ ] 5.3.1. Replace each consumer's Make targets with thin delegates and
  explicit legacy-variable translation.
  - Requires 5.2.2.
  - Record a removal milestone for the translation layer; reject
    unsupported old and new configuration combinations.
- [ ] 5.3.2. Delete the four legacy orchestration modules, copied operator
  manifests, and k3d and Docker branches.
  - Requires 5.3.1.
  - Success: 5.2.2 passes on every consumer, and Khufu never invokes a
    legacy script.

### 5.4. Ship the first consolidated release

This step answers whether every release acceptance behaviour holds at once. See
khufu-design.md §15.3.

- [ ] 5.4.1. Run the release acceptance suite and record qualification
  evidence alongside the platform lock.
  - Requires steps 5.1-5.3.
  - Success: every behaviour in khufu-design.md §15.3 passes, except TUI
    terminal restoration, which 6.1.2 verifies when the TUI ships; the
    estate manifest and consumer pins update together.

## 6. Vertical slice 5: Interactive inspection without a second engine

Idea: if an espressoTUI dashboard can be built purely over the versioned
observations and application services that machine clients already use, then
interactive inspection adds no TUI-only behaviour and no second execution path.

### 6.1. Deliver the read-mostly inspector

This step answers whether the observation model is rich enough for humans. See
khufu-design.md §5.3 and §9.

- [ ] 6.1.1. Implement `khufu tui` with run list, step progress, bounded log
  viewport, check details, and artefact browser.
  - Requires phase 2.
  - Lazy-import `espresso`; route `Cmd` effects through application
    services; closing detaches without cancelling.
  - Success: the import-boundary check proves machine commands never load
    `espresso`.
- [ ] 6.1.2. Build the terminal restoration E2E suite.
  - Requires 6.1.1.
  - Success: the terminal state is restored after exceptions, SIGINT, and
    worker failure under a pseudo-terminal harness.

## 7. Deferred extensions after the core promise

Idea: if the consolidated release is already trustworthy and boring to operate,
Khufu can evaluate broader validation suites on their product value instead of
letting them delay elimination of the four legacy implementations.

### 7.1. Evaluate the local GitOps suite

- [ ] 7.1.1. Decide whether a Flux suite backed by a local Git or OCI source
  graduates into scope.
  - Requires phase 5.
  - See khufu-design.md §12.1.

### 7.2. Evaluate platform extension suites

- [ ] 7.2.1. Decide whether TLS and External Secrets Operator (ESO) suites
  graduate into scope.
  - Requires phase 5.
  - See khufu-design.md §8.5 and §12.1.
- [ ] 7.2.2. Decide whether storage persistence, database recovery, and
  multi-node failover suites graduate into scope.
  - Requires phase 5.
  - See khufu-design.md §7.2 and §12.1.

### 7.3. Evaluate execution and delivery extensions

- [ ] 7.3.1. Decide whether an allowlisted webhook delivery adapter is
  needed.
  - Requires phase 5.
  - See khufu-design.md §13.4.
- [ ] 7.3.2. Decide whether an orphan adoption workflow is needed beyond
  orphan reporting.
  - Requires 2.5.3.
  - See khufu-design.md §14.
