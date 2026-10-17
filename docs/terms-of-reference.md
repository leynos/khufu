# Khufu — terms of reference

- **Status:** Draft v0.1 with acknowledged open questions
- **Audience:** The estate owner, consumer-repository maintainers, Khufu
  contributors, and reviewers of validation evidence
- **Companion documents:** `docs/context.md`, `docs/khufu-design.md`,
  `docs/roadmap.md`, and the architectural decision records (ADRs) indexed in
  `docs/contents.md`
- **Last substantive revision:** 2026-10-17
- **Version:** 0.1

## 1. Background and motivation

Four df12 application repositories — Episodic, Corbusier, Wildside, and Ghillie
— each validate their Kubernetes deployment locally before changes reach shared
infrastructure. Each repository grew its own preview tooling. The result is
four independent implementations of the same job: cluster creation, image
transport, dependency provisioning, chart deployment, health checking, and
teardown.[^1][^2][^3][^4]

Those implementations have drifted. Some target k3d with Docker, some kind with
rootless Podman, and some both. Two install operators for PostgreSQL and
Valkey; one hand-writes a PostgreSQL StatefulSet; one provisions no data
service at all. Each pins its own operator versions and renders its own custom
resources. Inspection of recorded source snapshots found concrete defects that
a shared, tested implementation would expose rather than conceal: an
inconsistent Valkey resource identity, a health endpoint that passes while
domain functionality is disabled by a misnamed environment variable, and a
Kubernetes version constraint that a modern operator bundle cannot simply
inherit.[^5][^6]

The motivation is therefore consolidation, not invention. Episodic already
demonstrates a working rootless kind execution path, and Corbusier already
demonstrates hosting data services through shared operators. The estate owner
has accepted both as the baseline.[^7] What is missing is one maintained
implementation that every consumer uses, so that a fix or upgrade lands once
and is proven against all four applications.

A second pressure is the growing share of validation performed by coding
agents. Agents run validation without a terminal, retry after failures, and
need machine-readable results and errors. None of the existing helpers was
built for that caller.[^8]

## 2. Domain

Khufu operates in local pre-merge validation of containerized applications
deployed to Kubernetes with Helm. The field's established conventions are:

- disposable local clusters (kind, k3d, minikube) standing in for a real
  cluster;
- Kubernetes operators reconciling stateful services from custom resources,
  rather than handwritten StatefulSets;
- Helm charts as the application packaging boundary, with environment-specific
  values files; and
- GitOps reconciliation (Flux in the df12 estate) as the production delivery
  path, which local validation approximates but does not replace.

The df12 estate adds its own bedrock. Nile Valley owns shared ephemeral
infrastructure, OpenTofu provisioning, rendered platform fixtures, and Flux
reconciliation, with Helm plus Kustomize as the selected packaging
direction.[^9][^10] Application repositories own their images, charts, runtime
configuration, and behavioural checks.

Rootless container execution carries known host prerequisites: cgroup v2,
delegation, subordinate ID mappings, and kernel networking limits.[^11] These
are properties of the host, not of the tool, and shape what a local validator
can promise.

Domain vocabulary is defined in `docs/context.md`.

## 3. Market context

The current default is the status quo: four per-repository preview scripts,
each invoked through Make targets, each with its own cluster-provider branches
and operator pins. Doing nothing leaves every infrastructure fix to be repeated
four times and lets validation semantics differ between applications that share
a platform.

Adjacent products address parts of the job:

| Product                  | What it covers                                           | What it leaves open for this estate                                                     |
| ------------------------ | -------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| kind used directly       | Local cluster lifecycle on a container runtime           | Operators, data services, bindings, checks, evidence, and job durability                |
| ctlptl                   | Declarative local cluster and registry set-up            | Everything above the cluster                                                            |
| Tilt, Skaffold, DevSpace | Inner-loop build, deploy, and live update for developers | A locked, shared operator platform; validation reports; non-interactive durable jobs    |
| Garden                   | Dependency-graph builds, deploys, and test runs          | Estate-wide platform pinning; agent-oriented machine protocol; fixed rootless substrate |
| Docker Compose           | Multi-container local stacks                             | Kubernetes, Helm charts, and operator behaviour                                         |
| Ephemeral cloud previews | Nile Valley's Flux-reconciled preview environments       | Validation without cloud resources, credentials, or a GitOps commit                     |

_Table 1: Adjacent products and the gaps they leave._

The gap is specific. No existing tool combines a centrally locked operator
platform, declarative application contracts that cannot override that platform,
durable non-interactive jobs designed for agents, and versioned evidence of
exactly what a run demonstrated — for a fixed, known set of applications that
must not drift apart.

## 4. Users and stakeholders

### 4.1 Primary users

**Consumer-repository maintainers.** df12 developers working on Episodic,
Corbusier, Wildside, or Ghillie on a rootless Linux workstation. They are
fluent with containers, Helm, and Kubernetes, and care about a fast,
trustworthy answer to "does this change deploy and work?" They will ignore
anything that requires editing shared infrastructure to validate their own
application, and actively dislike tools that prompt, mutate global configuration
(`~/.kube/config`, sysctls, `/etc/hosts`), or require sudo. Their current
alternative is the repository's own preview script.

**Coding agents.** Automated callers running validation on a maintainer's
behalf, without a terminal. They need non-interactive commands, structured
output and errors, safe retries, and bounded responses. They cannot recover
from prompts, ANSI-contaminated output, or a lost foreground process. Their
current alternative is driving the same preview scripts and parsing free-form
output.

### 4.2 Secondary users

**Reviewers** read reports and evidence bundles to decide whether a change was
adequately validated. They care that a report states exactly what was and was
not demonstrated. **Continuous Integration (CI)** runs the regression matrix
and consumer checks; it needs a foreground mode and deterministic exit codes.

### 4.3 Stakeholders and non-users

| Party                                     | Relationship | Cares about                                                  | Will reject                                                                |
| ----------------------------------------- | ------------ | ------------------------------------------------------------ | -------------------------------------------------------------------------- |
| Consumer-repository maintainers           | Primary user | Fast, trustworthy local validation of their own application  | Prompts, sudo, global configuration changes, per-repo infrastructure forks |
| Coding agents                             | Primary user | Machine protocol, idempotent submission, durable jobs        | Interactive flows, unbounded or unparsable output                          |
| Reviewers                                 | Secondary    | Honest coverage and evidence                                 | Reports that overstate what ran                                            |
| CI                                        | Secondary    | Deterministic exits, foreground execution, regression matrix | Hidden network discovery of moving versions                                |
| Estate owner (Nile Valley)                | Stakeholder  | One platform baseline, no drift, approved toolchain pins     | Consumers selecting their own operators or versions                        |
| Users seeking cloud-provisioning fidelity | Non-user     | Real cloud resources, DNS, production credentials            | —                                                                          |
| Docker, k3d, or rootful-host users        | Non-user     | Alternative cluster substrates                               | —                                                                          |
| Production operators                      | Non-user     | Live deployment and operations                               | —                                                                          |

_Table 2: Stakeholder mapping._

## 5. Job to be done

> When a maintainer has changed an application, its chart, or its
> configuration, the maintainer (or an agent acting for them) wants to deploy
> that exact source onto a faithful local replica of the shared platform and
> exercise real application behaviour against real data services, so they can
> merge with evidence that the change works, and know precisely what that
> evidence does not cover.

- **Functional dimension.** Build the application from its current working
  tree, provision its declared dependencies, deploy its chart, run its declared
  checks, and obtain a report.
- **Emotional dimension.** Confidence that a pass means something: no silent
  skips, no health endpoint masking missing functionality, no stale image.
- **Social dimension.** A reviewer can trust the evidence attached to a pull
  request without re-running it.
- **Competing alternatives.** The repository's own preview script; manual
  `kind`, `helm`, and `kubectl` sequences; pushing to a cloud preview and
  waiting for Flux; or merging without local validation.

A second job belongs to the estate owner:

> When the shared platform needs a fix or an upgrade, the estate owner wants
> to make the change once and prove it against every consumer, so the estate
> never again carries four divergent implementations.

## 6. Scope

### 6.1 Goals

- **One implementation.** After migration, no consumer repository contains
  its own cluster lifecycle, image transport, operator installation, custom
  resource rendering, readiness logic, credential binding, evidence collection,
  or cleanup.
- **One platform baseline.** Every consumer validates against the same
  approved toolchain and platform lock; divergent pins are detectable in CI.
- **Preserve demonstrated behaviour first.** Episodic's working execution
  path and Corbusier's data-service hosting model run through the shared
  implementation before improvements are introduced.
- **Declarative application contracts.** Each consumer describes its image,
  chart, bindings, data-service requirements, and checks without being able to
  select or override infrastructure.
- **Honest validation.** Reports distinguish passed, failed, blocked, skipped,
  and not-requested checks; required checks cannot pass by being skipped; and
  coverage exclusions are explicit.
- **Agent-native operation.** Every ordinary operation runs non-interactively
  with structured, bounded output, structured errors, idempotent submission,
  and durable jobs that survive the caller.
- **Safe locality.** Validation never mutates an environment it cannot prove
  it owns, never alters global host configuration, and never leaks secrets into
  output, logs, or evidence collected by the standard adapters.

### 6.2 Non-goals

- **Cloud-provisioning fidelity.** Khufu does not create cloud resources,
  publish GitOps changes, alter real DNS, or use production credentials. Use
  Nile Valley's ephemeral preview path for that.
- **A choice of cluster substrate.** There is no Docker, k3d, rootful, or
  pluggable alternative to rootless Podman with kind. Hosts that cannot run
  that stack receive a prerequisite report, not a fallback.
- **Wrapping legacy helpers.** Khufu does not invoke the existing preview
  scripts as permanent adapters; they are retired during migration.
- **A universal umbrella chart.** Consumers keep their own charts; Khufu does
  not absorb them.
- **A Kubernetes operator.** Existing operators reconcile resources; Khufu
  sequences work, verifies conditions, and records evidence.
- **Host remediation.** Khufu does not run sudo, change sysctls, or edit
  global container configuration; maintainers apply host fixes explicitly.
- **Proof of production properties.** High availability, failover,
  backup and restore, and multi-host resilience are out of scope unless a
  separately requested extension suite runs them; they appear as coverage
  exclusions otherwise.
- **Automatic telemetry or upstream reporting.** Feedback and evidence stay
  local unless a separately authorized delivery is configured.

## 7. Success criteria

### 7.1 User-facing success

- Episodic's demonstrated validation path completes through Khufu with
  equivalent application-level outcomes, including migrations and readiness.
- All four consumers validate through Khufu, and each consumer's legacy
  orchestration modules, copied operator manifests, and cluster-provider
  branches have been deleted.
- An agent completes a validation with two calls (plan, then run) and reads
  every result and error as schema-valid JSON without terminal escapes.
- A Ghillie run that reaches only its health endpoint cannot satisfy the full
  smoke suite.
- Secret canaries in raw, URI-escaped, and base64 forms never appear in
  normal output, plans, logs, or evidence bundles.

### 7.2 Operational success

- Killing a waiting CLI does not stop its job; killing a worker either
  reconciles safely or reports an indeterminate outcome.
- Repeating a submission with the same idempotency key returns the same job,
  and two callers cannot mutate one environment concurrently.
- A wrong ambient kube-context, a similarly named cluster, a changed
  certificate authority, or a stale environment marker cannot redirect a
  mutation.
- Four applications coexist in one environment without namespace, release,
  Secret, image-tag, or ingress collisions, and independent worktrees remain
  isolated.
- Ordinary validation contacts no remote service to discover versions.

### 7.3 Strategic success

- A shared-infrastructure change lands in one repository and passes one
  regression matrix covering all four consumers.
- CI detects any consumer whose toolchain pin, contract schema version, or
  platform fingerprint diverges from the estate manifest.
- No new per-repository preview script appears in the estate.

## 8. Constraints and assumptions

### 8.1 Hard constraints

- **Substrate.** Linux, rootless Podman, kind, kubectl, and Helm. kind is
  fixed, not a default.[^7]
- **Implementation stack.** CPython 3.14, with cuprum for external command
  execution, femtologging for diagnostics, Cyclopts for the command-line
  interface, and espressoTUI for the optional terminal dashboard.[^12][^13]
- **Naming.** The executable and Python package are both `khufu`; commands
  follow `khufu <resource> <verb>` with no `local` prefix.
- **Data-service implementations.** CloudNativePG (CNPG) for PostgreSQL and
  the Hyperspike Valkey operator for Redis-compatible caches, chosen centrally
  rather than per application.[^14][^15]
- **Ownership boundary.** Application repositories retain images, charts,
  runtime configuration, schema migrations, and behavioural checks.
- **No production effects.** No cloud resources, real DNS changes, GitOps
  publication, or production credentials.
- **Repository conventions.** This repository's package lives at `khufu/`;
  quality gates are those in `AGENTS.md`.

### 8.2 Assumptions

| Assumption                                                                                                 | Consequence if false                                                                                    |
| ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Episodic's rootless kind path works as the estate owner describes.[^7]                                     | Phase 0 baseline capture fails; the extraction must first repair the baseline before claiming parity.   |
| Corbusier's operator-hosting model runs unchanged on the Episodic substrate.                               | Integration requires substrate-specific fixes in Khufu, and the combined-stack milestone slips.         |
| Maintainer workstations provide cgroup v2 delegation, subordinate IDs, and a working systemd user session. | Detached jobs are unavailable; `doctor` reports the gap and only foreground execution remains viable.   |
| Required Python 3.14 wheels (notably femtologging) can be published for target platforms.                  | Installation compiles a Rust toolchain per host, or the femtologging constraint must be revisited.      |
| One Kubernetes version satisfies every consumer chart's constraint and the operator bundle.                | Wildside's chart range must widen, with tests, before a shared environment can host all four consumers. |
| Consumers can supply a deterministic, non-health functional check.                                         | That consumer remains blocked for the smoke suite rather than validated.                                |
| Hyperspike Valkey can satisfy each consumer's single-primary client contract.                              | Khufu returns a capability error; a central platform change and migration are required.                 |

_Table 3: Assumptions and their failure consequences._

### 8.3 Dependencies

- **Upstream libraries:** cuprum, femtologging, Cyclopts, and espressoTUI
  releases compatible with CPython 3.14. femtologging wheel availability is on
  the critical path for installation.
- **Upstream infrastructure:** kind node images, the CNPG and Hyperspike Valkey
  charts, CRD schemas, and controller images, all pinned through the platform
  lock.
- **Consumer work:** each consumer must adopt an application contract and, for
  Ghillie, correct its runtime environment variable naming and packaged
  PostgreSQL driver. Ghillie's corrections do not gate Episodic's
  extraction.[^5]
- **Nile Valley:** the estate manifest and central regression matrix.

## 9. Open questions

| Question                                                                                                                                                                                                                             | Why it matters                                                                       | Resolution criteria                                                                                                 | Owner                                      | Path                 |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ | -------------------- |
| Does Khufu's implementation live in `leynos/khufu` with Nile Valley holding only the estate manifest and regression matrix, as this repository's existence implies, rather than in `leynos/nile-valley` as the source design states? | Determines release, packaging, and where CI enforces anti-drift checks.              | An accepted ADR names the implementation home and the Nile Valley responsibilities.                                 | Estate owner                               | ADR-001              |
| What exact tool, image, and chart versions does the demonstrated Episodic path use today?                                                                                                                                            | Seeds the platform lock and golden-path tests; older inspected snapshots may differ. | A recorded baseline with command trace and versions.                                                                | Khufu maintainers                          | Phase 0 capture      |
| What is the Kubernetes version intersection of all consumer charts and the operator bundle?                                                                                                                                          | An empty intersection blocks shared environments.                                    | A resolved version, or a tested widening of Wildside's chart range.                                                 | Wildside maintainer with Khufu maintainers | Compatibility spike  |
| Which Hyperspike Valkey resource identity and topology satisfy Corbusier's and Ghillie's clients?                                                                                                                                    | The inspected helpers emit a group/version that does not match upstream.             | Integration tests pass authenticated PING, namespaced read/write/delete, and the application's multi-key behaviour. | Khufu maintainers                          | Implementation spike |
| How does a foreground CI mode advertise its weaker durability guarantee?                                                                                                                                                             | CI hosts may lack a systemd user session.                                            | A documented mode whose reports record foreground execution.                                                        | Khufu maintainers                          | Design decision      |
| What non-health functional check does each consumer expose?                                                                                                                                                                          | Without one, a consumer cannot pass the smoke suite.                                 | Each consumer contract declares a deterministic check.                                                              | Each consumer maintainer                   | Consumer migration   |
| When are the legacy Make-variable translations removed?                                                                                                                                                                              | Temporary translation risks becoming permanent drift.                                | A removal milestone recorded in the roadmap and enforced in CI.                                                     | Estate owner                               | Roadmap              |

_Table 4: Open questions register._

The terms of reference is complete enough to begin technical design and roadmap
work; the open questions above are inputs to the design's ADR candidates and
the roadmap's foundational phase.

## Appendix A: glossary

Terminology is defined in `docs/context.md`.

## Appendix B: references

The originating input is the Khufu local validation design, revision 2,
15 October 2026, supplied by the estate owner. Repository references point to
the snapshots inspected for that design, not to current branches.

[^1]: Wildside local preview design,
  <https://github.com/leynos/wildside/blob/9f4baf0b192c67f6e08eda4ced686a0fbd65a002/docs/local-k8s-preview-design.md>.
[^2]: Episodic local preview design,
  <https://github.com/leynos/episodic/blob/baa4d21a4bb4e6e09807827d39872791b40dfe84/docs/local-k3d-preview-design.md>.
[^3]: Corbusier local orchestration,
  <https://github.com/leynos/corbusier/blob/613f23b309366302c1a04e9201fc5189c05dad4e/scripts/local_k8s/orchestration.py>.
[^4]: Ghillie local deployment helper,
  <https://github.com/leynos/ghillie/blob/494d7c8ed4d36cc21a217fc42d71ba30e526c901/scripts/local_k8s/deployment.py>.
[^5]: Ghillie runtime configuration,
  <https://github.com/leynos/ghillie/blob/494d7c8ed4d36cc21a217fc42d71ba30e526c901/ghillie/runtime.py>,
  and project dependencies,
  <https://github.com/leynos/ghillie/blob/494d7c8ed4d36cc21a217fc42d71ba30e526c901/pyproject.toml>.
[^6]: Corbusier Valkey helper,
  <https://github.com/leynos/corbusier/blob/613f23b309366302c1a04e9201fc5189c05dad4e/scripts/local_k8s/valkey.py>.
[^7]: Estate owner clarification, 15 October 2026: assume kind as the
  standard, eliminate drift between the four implementations, use the working
  Episodic path and Corbusier's infrastructure-hosting model, and name the CLI
  `khufu`. This is the accepted basis, not an independently reproduced result.
[^8]: Trevin Chow, "10 Principles for Agent-Native CLIs", 1 May 2026, as
  supplied with the originating design.
[^9]: Nile Valley README,
  <https://github.com/leynos/nile-valley/blob/c87163b6976c5e53f53ed78992f3080c8e842b21/README.md>.
[^10]: Nile Valley ephemeral previews roadmap,
  <https://github.com/leynos/nile-valley/blob/c87163b6976c5e53f53ed78992f3080c8e842b21/docs/ephemeral-previews-roadmap.md>.
[^11]: kind rootless documentation,
       <https://kind.sigs.k8s.io/docs/user/rootless/>.
[^12]: cuprum README, <https://github.com/leynos/cuprum/blob/main/README.md>.
[^13]: femtologging README,
  <https://github.com/leynos/femtologging/blob/main/README.md>.
[^14]: CloudNativePG application connection documentation,
  <https://cloudnative-pg.io/documentation/1.24/applications/>.
[^15]: Hyperspike Valkey operator example,
  <https://github.com/hyperspike/valkey-operator/blob/main/valkey.yaml>.
