# Khufu context

- **Status:** Draft v0.1
- **Last substantive revision:** 2026-10-17
- **Audience:** Khufu contributors, consumer-repository maintainers, and
  reviewers

This document defines Khufu's ubiquitous language. The
[terms of reference](terms-of-reference.md) and the
[Khufu design](khufu-design.md) use these definitions normatively. Terms in
backticks name files, commands, or source-level identifiers.

## Estate and actors

| Term                  | Definition                                                                                                                                                                                |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Consumer              | An application repository that validates itself through Khufu. The initial consumers are Episodic, Corbusier, Wildside, and Ghillie.                                                      |
| Demonstrated baseline | The working local validation behaviour that Khufu extracts: Episodic's rootless kind execution path and Corbusier's operator-hosting model. It is accepted as working, not re-evaluated.  |
| Drift                 | Divergence between consumers in infrastructure behaviour, tool versions, operator bundles, or validation semantics. Khufu exists to remove drift.                                         |
| Estate                | The set of consumers, the approved Khufu release, and the application revisions exercised together by the regression matrix.                                                              |
| Estate manifest       | `validation-estate.toml` in Nile Valley. It records the approved Khufu toolchain and the consumer revisions used by the regression matrix.                                                |
| Legacy helper         | A consumer's pre-Khufu preview script or module, including its k3d and Docker branches. Legacy helpers appear only in the extraction inventory and are retired as each consumer migrates. |
| Nile Valley           | The df12 platform repository that owns shared ephemeral infrastructure, GitOps fixtures, and the estate manifest.                                                                         |
| Regression matrix     | The central, resource-bounded run of every consumer's contract and smoke suites against one Khufu candidate. A shared-infrastructure change is not supported until the matrix passes.     |
| Thin delegate         | A Make target in a consumer that selects an application and operation and invokes `khufu`. It never runs kind, Podman, Helm, or kubectl directly.                                         |
| Toolchain pin         | The exact Khufu release a workspace or consumer CI uses. Pins are checked against the estate manifest; floating versions such as `latest` are rejected.                                   |

_Table 1: Estate and actor vocabulary._

## Inputs and configuration

| Term                 | Definition                                                                                                                                                                                                 |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Application          | One consumer's deployable surfaces and checks, as declared by its application contract.                                                                                                                    |
| Application contract | `.khufu.toml` in a consumer repository. It declares the image, chart, chart bindings, data-service requirements, environment bindings, and checks. It cannot select infrastructure implementations.        |
| Binding              | A typed mapping from a data-service output, such as a database application URI, to an application input, such as an environment variable or chart value.                                                   |
| Capability           | A named, centrally tested platform feature that a plan can request, such as `ingress`. Unrequested capabilities appear as `not_requested` coverage.                                                        |
| Chart binding        | A mapping from a Khufu-supplied value (image repository, tag, pull policy, Secret name) to a path in the consumer's chart values.                                                                          |
| Codec                | The encoding rule a binding uses to render a credential into a client-specific form, such as `postgresql-uri` or `redis-uri`.                                                                              |
| Data service         | A dependency Khufu provisions through a shared operator: `postgres` (CloudNativePG) or `cache` (Hyperspike Valkey).                                                                                        |
| Platform bundle      | The operator charts, manifests, CRD schemas, and images packaged with a Khufu release, described by its platform lock.                                                                                     |
| Platform fingerprint | A digest identifying the platform lock and effective cluster configuration of an environment. Reuse of an environment requires a compatible fingerprint.                                                   |
| Platform lock        | `platform.lock.toml`, packaged in each Khufu release. It pins kind, the node image digest, Helm, operator charts and controller images, CRD schemas, and data-service images. It is not an override layer. |
| Profile              | A named user-level configuration for host preferences, resource budgets, and delivery policy. Profiles never hold plaintext credentials.                                                                   |
| Workspace            | `khufu.workspace.toml`. It maps application IDs to local checkouts and selects an exact Khufu toolchain.                                                                                                   |

_Table 2: Input and configuration vocabulary._

## Execution

| Term                   | Definition                                                                                                                                                                                      |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Disposable environment | An environment a run creates for itself. Its cleanup policy defaults to retain-on-failure and delete-on-success.                                                                                |
| Environment            | A dedicated kind cluster owned by Khufu, with its platform bundle installed and one or more application namespaces. Each environment has an environment ID.                                     |
| Environment marker     | A Kubernetes object, recorded by UID in the ledger, that proves a cluster is the environment Khufu created. Names and labels alone never prove ownership.                                       |
| Executor               | The party that owns a resource's lifecycle: direct Helm execution by Khufu, Flux, or an operator. One release never has two executors.                                                          |
| Frozen build context   | The staged, content-fingerprinted copy of an image build context used by an asynchronous job. It includes uncommitted and untracked inputs.                                                     |
| Idempotency key        | A caller-supplied, scope-qualified key. Resubmitting the same key and plan hash returns the same job; the same key with another plan hash is a conflict.                                        |
| Indeterminate          | A terminal job or step state meaning Khufu cannot prove whether an external effect happened, for example after a crash during a non-replayable migration.                                       |
| Job                    | A durable, asynchronous execution of a plan or another operation, recorded in the ledger and run by a worker.                                                                                   |
| Ledger                 | The SQLite database under `$XDG_STATE_HOME/khufu` that records environments, plans, jobs, steps, inventories, idempotency keys, events, and artefact references. It never stores secret values. |
| Mutation lock          | An operating-system-backed, per-environment lock held by a worker for the whole of a state-sensitive operation.                                                                                 |
| Plan                   | A typed, redacted, hashed description of the intended inputs and effects of an operation. A run executes a frozen plan; a stale plan is rejected, not silently replanned.                       |
| Reconciliation         | Re-observing kind, Kubernetes, and Helm state after an interruption to decide whether recorded intents took effect, and continuing or failing accordingly.                                      |
| Step                   | One node in a job's directed acyclic graph of effects. Each step records intent before acting and the observed outcome afterwards.                                                              |
| Supervisor             | The transient systemd user service that owns a worker's execution. A waiting CLI process is an observer, not the owner.                                                                         |
| Worker                 | The process that executes a job's steps under a supervisor.                                                                                                                                     |

_Table 3: Execution vocabulary._

## Validation and evidence

| Term               | Definition                                                                                                                                                                            |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Check              | An application- or platform-declared assertion with an ID, category, dependencies, executor, finite deadline, required or optional status, and result schema.                         |
| Check outcome      | One of `passed`, `failed`, `blocked`, `skipped`, or `not_requested`. A required check can never become a successful skip.                                                             |
| Coverage           | The list of validation areas a report actually demonstrated, such as `render`, `deployment`, `dependencies`, and `application-smoke`.                                                 |
| Coverage exclusion | An explicitly reported area that the run did not demonstrate, such as ingress, Flux reconciliation, backups, or high availability.                                                    |
| Doctor             | `khufu doctor`, the read-only host prerequisite report. It diagnoses; it never remediates.                                                                                            |
| Endpoint           | A supervised, loopback-only port forward to a resource in a known environment.                                                                                                        |
| Evidence bundle    | The collected, redacted artefacts of a run: summary, canonical report JSON, JUnit XML, redacted plan, rendered manifests, events, Pod status, logs, Job results, and cleanup results. |
| Feedback record    | A local friction report with optional command or job references. Feedback is never sent anywhere automatically.                                                                       |
| Report             | The structured record of checks, coverage, and identities for a run. It outlives the environment.                                                                                     |
| Suite              | A named validation level: contract, smoke, integration, GitOps, or a platform extension suite.                                                                                        |

_Table 4: Validation and evidence vocabulary._

## Agent-native interface

| Term               | Definition                                                                                                                                                                                      |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Agent context      | `khufu agent-context`, the versioned, filterable, machine-readable description of commands, effects, enums, profiles, and applications.                                                         |
| Command descriptor | The single registry entry for a command: name, parameters, effect class, schemas, enums, asynchronous behaviour, and examples. CLI registration, help, and agent context are generated from it. |
| Effect class       | The classification of a command's side effects: read-only, local-state write, cluster write, or destructive.                                                                                    |
| Envelope           | The stable outer JSON shape of every machine-mode result or error.                                                                                                                              |
| Machine mode       | Output mode selected by `--json` or a non-TTY stdout: exactly one JSON document on success, one structured error document on failure, and no prompts or ANSI sequences.                         |

_Table 5: Agent-native interface vocabulary._
