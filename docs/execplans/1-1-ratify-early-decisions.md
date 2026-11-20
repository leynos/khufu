# 1.1. Ratify the decisions that would otherwise force rework

This ExecPlan (execution plan) is a living document. The sections `Constraints`,
`Tolerances (exception triggers)`, `Risks`, `Progress`,
`Surprises & discoveries`, `Decision log`, `Outcomes & retrospective`,
`Conformance basis`, and `Verification plan` must be kept up to date as work
proceeds.

Status: DRAFT (expert review applied; awaiting user approval of D3-D6 and a
user decision on D7)

Branch: `1-1-ratify-early-decisions`, stacked on `regenerate-typos-config` (an
unrelated regeneration of `typos.toml` by the spelling gate, kept in its own
pull request as AGENTS.md requires).

Roadmap item: `1.1` (tasks `1.1.1` to `1.1.4`) in `docs/roadmap.md`.

## Purpose / big picture

Khufu is a planned command-line tool that will replace four separately
maintained local Kubernetes preview scripts in the df12 estate (Episodic,
Corbusier, Wildside, and Ghillie) with one shared implementation. No Khufu
runtime code exists yet. The repository holds a design
(`docs/khufu-design.md`), terms of reference (`docs/terms-of-reference.md`), a
vocabulary (`docs/context.md`), a roadmap (`docs/roadmap.md`), and a
placeholder Python package (`khufu/`).

The design leaves four foundational choices as "ADR candidates" in its §18. An
architectural decision record (ADR) is a short, stable document that records
one accepted decision, the context that forced it, the options weighed, and its
consequences. Until those four ADRs exist and are accepted, every later roadmap
step rests on choices that could still be reopened: where the code lives and
how consumers pin it, whether a second cluster provider may ever be plugged in,
who owns a running job, and where the typed data-service fixture specifications
shared with Nile Valley live. Nile Valley (`leynos/nile-valley`) is the df12
platform repository that provisions shared cloud infrastructure with OpenTofu
and delivers it through Flux GitOps.

After this work, a maintainer or agent can open `docs/adrs/` and find four
accepted ADRs:

- `docs/adrs/adr-0001-implementation-home.md` names `leynos/khufu` as the code
  home, Nile Valley as the home of `validation-estate.toml` (the estate
  manifest) and the regression matrix, and the release channel consumers pin.
- `docs/adrs/adr-0002-fixed-kind-rootless-substrate.md` fixes Linux, rootless
  Podman, kind, kubectl, and Helm as the only supported stack.
- `docs/adrs/adr-0003-systemd-user-service-supervision.md` makes transient
  systemd user services the owners of job workers, makes waiting command-line
  processes observers, defers the foreground mode to roadmap task 5.1.2, and
  lists the session-survival limits that `khufu doctor` must report.
- `docs/adrs/adr-0004-shared-fixture-specifications.md` names the owning
  repository of the shared fixture specifications, how each side consumes them,
  and how their versions stay aligned with the platform lock.

The design, terms-of-reference open-questions register, context, users' guide,
developers' guide, contents index, and roadmap then agree with those ADRs. In
particular, the design and users' guide stop describing a foreground execution
mode as available today.

Observable success: `make test` runs a decision-record suite that fails if any
ADR in `docs/adrs/` breaks the style guide's naming, heading, status, or date
rules; if ADRs 0001-0004 are missing, not `Accepted`, or lack the identifiers
their roadmap success criteria require; if design §18 or `docs/contents.md`
fails to link one of them; or if package metadata or source introduces a
cluster-provider plug-in surface that ADR 0002 forbids. Each rule is shown to
reject a deliberately broken input.

Roadmap 1.1.4's success criterion ("Khufu's renderers and Nile Valley's GitOps
rendering consume one specification source") is met at the decision level only:
no renderer exists on either side yet. ADR 0004 fixes the source and the
consumption contract, and this plan adds roadmap follow-ups that implement it.

No runtime behaviour of Khufu changes, because none exists. The visible change
is documentary: the users' guide describes execution modes and prerequisites as
ratified.

## Constraints

- No production code under `khufu/` is added or changed. Implementing
  supervision, `doctor`, the platform lock, or fixture rendering belongs to
  later roadmap tasks (2.1.1, 2.1.2, 2.2.4, 3.1.1, 5.1.1, 5.1.2, 7.1.1).
- ADR files use exactly the four paths named by roadmap 1.1. Their titles must
  slug to those filenames (`docs/documentation-style-guide.md`, "Architectural
  decision records (ADRs)", "Naming convention"). Sentence case makes ADR
  0003's title "Systemd user service supervision"; that capitalization is
  accepted.
- ADRs follow the style guide's required order (`## Status`, `## Date`,
  `## Context and problem statement`) and use these conditional headings, in
  this order, in sentence case: `## Decision drivers`, `## Options considered`
  (with `### Option A: <name>` subsections and a captioned comparison table),
  `## Decision outcome` (with a `### Consequences` subsection),
  `## Goals and non-goals` where useful, and `## Known risks and limitations`.
  See D1.
- ADR prose follows the style guide: no first-person pronouns, en-GB-oxendict
  spelling, expanded acronyms on first use, captions on every table, a
  screen-reader description before any diagram, external sources as numbered
  footnotes, and roadmap tasks cited by number and short description, because
  `mapsplice` may renumber them.
- Acceptance authority (D2): approval of this plan ratifies decisions D3-D6;
  D7 requires a separate, explicit user answer before `EP-M5` starts. Each
  ADR's Status date is the date of the corresponding user approval. Editing ADR
  text before the implementation pull request merges is normal review. After
  merge, changes follow the style guide's amendment and supersession rules.
- The terms of reference take precedence over the design and are edited only
  in the §9 open-questions register (resolution paths). Their needs statements
  (§4.2, §4.3 table, table 3) stay unchanged; see D9.
- Do not change `.github/workflows/release.yml`, repository settings (for
  example, GitHub immutable releases or tag rulesets), or any other repository.
  ADRs record those changes as consequences, and the roadmap gains follow-up
  tasks.
- Do not create `docs/repository-layout.md`. Its absence is a pre-existing gap
  outside this item.
- Test modules live under `tests/` (AGENTS.md). No code file exceeds 400
  lines. Python follows `.rules/python-*.md` and the repository's Ruff
  configuration, including the banned `from` imports in `pyproject.toml` (use
  `import dataclasses as dc`, `import enum`, `import collections.abc as cabc`,
  and similar module imports).
- Authorized configuration changes, all in `pyproject.toml`: add `pytest-bdd`
  and `hypothesis` to the `dev` dependency group with exact pins; add `"docs/"`
  to `[tool.mutmut] also_copy`; add `pythonpath = ["."]` to
  `[tool.pytest.ini_options]`; add pytest-bdd step decorators and
  `@pytest.fixture` to a Vulture `ignore_decorators` list. Refresh `uv.lock`
  with `uv lock`. No runtime dependency is added. `syrupy` is not added (D8).
- Implementation begins only after the user approves this plan.

## Tolerances (exception triggers)

Comparison base: the commit that records the user's approval of this plan
(record its SHA in `Progress` as `APPROVED_PLAN_SHA`). Counting command, from
the repository root:

```bash
git diff --numstat "$APPROVED_PLAN_SHA" -- . ':(exclude)docs/execplans/' ':(exclude)uv.lock'
```

Classification is by whole file. Markdown under `docs/` (excluding
`docs/execplans/`) is documentation. `pyproject.toml` is configuration.
Everything under `tests/`, including `.feature` files, is code. `uv.lock` is a
generated lockfile, excluded from line counts and counted as a file. This
ExecPlan is excluded from every count.

- Files: stop and escalate if more than 19 non-ExecPlan files change. Expected
  18: 4 new ADRs; 7 edited documents (`khufu-design.md`,
  `terms-of-reference.md`, `context.md`, `users-guide.md`,
  `developers-guide.md`, `contents.md`, `roadmap.md`); 4 test modules, 1
  feature file, and an optional `tests/conftest.py`; `pyproject.toml` and
  `uv.lock`.
- Code: stop above 550 net added lines under `tests/`. Estimate 420: rules
  module 150, rule tests 120, repository tests 70, BDD binding and feature 80.
- Configuration: stop above 20 net lines in `pyproject.toml`. Estimate 7.
- Documentation: stop above 1,300 net lines. Estimate 1,050: four ADRs at
  about 180-240 lines each (about 850) and about 200 lines of edits across the
  seven existing documents.
- Interface: stop if any change to `khufu/`, the Makefile, or CI workflows
  appears necessary.
- Dependencies: stop if any dependency beyond `pytest-bdd` and `hypothesis`
  appears necessary, or if `make audit` reports an advisory against either or
  their transitive dependencies (`mako`, `parse`, `parse-type`,
  `gherkin-official`).
- Architecture: stop if an ADR's direction must depart from the approved
  Decision log entries, or if the user's D7 answer requires a
  terms-of-reference scope change.
- Iterations: stop if a gate still fails after 3 fix attempts for one cause.
- Time: stop if any milestone exceeds 4 hours of active work.
- Ambiguity: stop and present options if the D7 answer leaves the consumption
  mechanism or alignment rule open.

Budget evidence: this repository has no earlier ExecPlans (`docs/execplans/` is
created by this plan), so no historical budget revisions exist. Expert review
cut the first draft's code estimate from 550 to 420 lines by removing a
filesystem-adapter module, two Hypothesis properties, and a speculative
`Superseded` rule. The documentation estimate grew because review found
contradicting passages in `docs/context.md` and `docs/developers-guide.md`.

## Risks

- Risk: the D7 decision (fixture-specification ownership) is contested between
  Khufu and Nile Valley. Severity: high. Likelihood: medium. Mitigation: D7 is
  presented neutrally with a recommendation and gates `EP-M5` only; `EP-M1` to
  `EP-M4` proceed without it.
- Risk: the foreground-mode deferral leaves CI hosts without a usable user
  manager unable to run jobs until roadmap 5.1.2. Severity: medium. Likelihood:
  high. Mitigation: ADR 0003 states this limit, `doctor` reports it, and the
  users' guide says so; early slices run on developer hosts.
- Risk: the release channel (D3) depends on GitHub immutable releases and a
  tag ruleset, both absent today, while `.github/workflows/release.yml` already
  publishes on any pushed `v*.*.*` tag and uploads assets after publication with
  `--clobber`. Severity: medium. Likelihood: high. Mitigation: ADR 0001 makes
  immutable, atomic publication a precondition of the first tag; a roadmap
  follow-up is attached to the first task that needs a pinned release; this
  work pushes no tag.
- Risk: documentation-conformance tests become brittle prose checks.
  Severity: medium. Likelihood: medium. Mitigation: tests assert structure and
  a small set of stable identifiers (repository names, file names, option
  names, digest vocabulary) within one named section, never sentences or
  roadmap numbers.
- Risk: `pytest-bdd` or `hypothesis` interacts badly with `pytest-xdist`
  (`-n auto`), the 30-second `pytest-timeout`, Vulture, or the duplication
  gate. Severity: low. Likelihood: medium. Mitigation: `EP-M1` runs every gate
  before any ADR work; steps reuse the rule functions and one shared text
  builder.
- Risk: GitHub release downloads are unavailable or blocked by egress rules
  (`release-assets.githubusercontent.com`). Severity: medium. Likelihood: low.
  Mitigation: ADR 0001 records integrity, not availability, as the guarantee
  and leaves mirroring or caching to the estate.

## Progress

- [x] (2026-11-20 10:40Z) Branch renamed to `1-1-ratify-early-decisions`;
  Lody session titled.
- [x] (2026-11-20 11:30Z) Reconnaissance: repository documents, Makefile,
  tests, style guide, Nile Valley tree, Python Package Index (PyPI) names,
  GitHub release settings, kind and systemd documentation.
- [x] (2026-11-20 12:30Z) Initial draft written and committed.
- [x] (2026-11-20 12:50Z) Spelling gate regenerated `typos.toml`; committed on
  `regenerate-typos-config` and stacked this branch on it.
- [x] (2026-11-20 13:40Z) Expert review (release engineering, systemd and
  rootless containers, Python test architecture, documentation governance)
  applied; see the revision note.
- [ ] Plan approved by the user (D3-D6); record `APPROVED_PLAN_SHA`.
- [ ] `EP-M1` decision-record suite and substrate fitness rules.
- [ ] `EP-M2` ADR 0001 accepted and cross-referenced.
- [ ] `EP-M3` ADR 0002 accepted and cross-referenced.
- [ ] `EP-M4` ADR 0003 accepted; foreground and session text reconciled.
- [ ] User answer on D7 recorded.
- [ ] `EP-M5` ADR 0004 accepted and cross-referenced.
- [ ] `EP-M6` documentation closure, roadmap 1.1 marked done, full gates.

## Surprises & discoveries

- Observation: the name `khufu` on PyPI belongs to an unrelated project
  ("Twitter Bootstrap elements via Python", versions 1.2.0-1.3.3). Evidence:
  `curl -s https://pypi.org/pypi/khufu/json`. Impact: `pip install khufu`,
  `uv tool install khufu`, and `uvx khufu` fetch the wrong package, and an exact
  `khufu==1.3.x` pin against an index would match that project once Khufu
  reaches 1.x. This drives D3.
- Observation: `femtologging` is not on PyPI; `espressoTUI` is, published by
  its upstream (`kimusan/espresso`), but its import name `espresso` collides
  with an unrelated PyPI distribution named `espresso`. Evidence: PyPI JSON
  API. Impact: Khufu's dependency set needs direct-URL, hash-pinned resolution
  (already required by roadmap 1.3.1), and PyPI rejects uploads whose metadata
  contains direct-URL dependencies, so PyPI cannot be Khufu's channel while it
  depends on femtologging that way.
- Observation: GitHub immutable releases are disabled for `leynos/khufu`, no
  tag rulesets exist, and no release has been published. Evidence:
  `gh api repos/leynos/khufu/immutable-releases` returned
  `{"enabled":false,"enforced_by_owner":false}`;
  `gh api repos/leynos/khufu/rulesets` returned `[]`; `gh release list` was
  empty. Impact: the release workflow must change before the first tag.
- Observation: Nile Valley renders the shared data services with OpenTofu
  modules (`infra/modules/cnpg/manifests.tf` emits `postgresql.cnpg.io/v1`
  `Cluster`; `infra/modules/valkey/manifests.tf` emits `hyperspike.io/v1`
  `Valkey`) inside Flux `HelmRelease` objects. It pins its own operator chart
  versions (`chart_version` default `0.26.1` in
  `infra/modules/cnpg/variables-core.tf`) and production defaults (three
  instances, block storage, 50Gi in `variables-cluster.tf`). It has no
  `validation-estate.toml` and no mention of Khufu. Evidence:
  `gh api repos/leynos/nile-valley/git/trees/HEAD?recursive=1` and file reads
  at the default branch on 2026-11-20. Impact: shared specifications must be
  language-neutral data, and ownership determines whether production platform
  upgrades depend on Khufu releases; see D7.
- Observation: rootless Podman on the planning host uses the `systemd` cgroup
  manager, so kind node containers run in `libpod-*.scope` units under
  `user@.service`, not in the worker's cgroup. Evidence: `podman info` on the
  planning host (reported by the systemd reviewer). Impact: logout without
  lingering, or a reboot, stops environment clusters as well as jobs; ADR 0003
  says so, and `doctor` must report the cgroup manager.
- Observation: `docs/repository-layout.md`, which AGENTS.md and the style
  guide treat as canonical, does not exist, and `docs/contents.md` indexes no
  ADRs although the terms of reference say ADRs are indexed there. Impact: each
  ADR milestone adds its own contents entry; the layout document is left for
  separate work.
- Observation: the "source design" cited by roadmap 1.1.1 is "Khufu local
  validation design, revision 2, 15 October 2026, supplied by the estate owner"
  (`docs/terms-of-reference.md`, references). It is not in any repository.
  Impact: ADR 0001 cites it by that description.
- Observation: `make all` and CI do not run `make nixie`. Impact: this plan
  runs it explicitly.
- Observation: running `make markdownlint` regenerated `typos.toml` from the
  shared dictionary (new tokio-attribute ignore patterns), a change unrelated
  to this work. Impact: committed on `regenerate-typos-config`, which this
  branch is stacked on.

## Decision log

- D1. Decision: write ADRs from the style guide template with sentence-case
  headings, using `## Decision outcome` (the template's "/ proposed direction"
  applies to `Proposed` ADRs) and adding `### Consequences` under it, because
  the style guide's document-type guidance requires ADRs to be "explicit about
  context, decision, consequences, and status" while the template has no
  consequences heading. Omit `## Migration plan` and `## Outstanding decisions`
  (every ADR is `Accepted`); matters delegated to later roadmap tasks go in
  `## Known risks and limitations`. Rationale: required order and roadmap
  1.1.1's explicit request for consequences are both satisfied. Date/Author:
  2026-11-20, planning agent; revised after governance review.
- D2. Decision: approval of this plan ratifies D3-D6; D7 is ratified only by
  an explicit user answer before `EP-M5`. ADRs are committed as `Accepted` with
  the date of the relevant approval; text may change in pull-request review
  before merge. Rationale: plan approval approves directions, so each direction
  needs an identifiable approval; the earlier draft bundled D7 into plan
  approval, which review rejected. Date/Author: 2026-11-20, planning agent.
- D3. Decision (ADR 0001, release channel): Khufu releases are GitHub Releases
  of `leynos/khufu`, created from immutable `vX.Y.Z` tags. Each release carries
  the pure Python wheel, a hash-pinned lock of the full runtime dependency set
  (the PEP 751 `pylock.toml` format, or a requirements file with `--hash`
  entries), and a `SHA256SUMS` file. Consumers and the estate manifest pin a
  release by version, tag, commit SHA, wheel URL and SHA-256, and
  dependency-lock URL and SHA-256; installs use hash checking
  (`--require-hashes` or the equivalent `uv` lock). Nothing resolves `khufu` by
  name from PyPI or any index; the ADR names the unsafe commands
  (`pip install khufu`, `uv tool install khufu`, `uvx khufu`) and the safe forms
  (`uvx --from 'khufu @ <wheel URL>#sha256=<digest>' khufu`, or a
  `[tool.uv.sources]` URL entry whose `uv.lock` records the hash). A release
  candidate is a PEP 440 pre-release (`X.Y.ZrcN`) published the same way, or a
  local build selected by explicit path; either identity is recorded in the
  report (design §4.3). Preconditions before the first tag: GitHub immutable
  releases enabled; a tag ruleset restricting `refs/tags/v*` to release
  maintainers; the workflow refusing tags that do not match
  `^v\d+\.\d+\.\d+(rc\d+)?$` or do not equal `project.version`; publication as
  draft, upload, then publish; `gh release verify` after publication.
  Rationale: the repository already builds a pure wheel on tag push; PyPI name
  resolution fetches an unrelated project; PyPI rejects packages with
  direct-URL dependencies, which femtologging requires; design §4.3 demands
  exact pins and forbids per-consumer resolution of unrelated dependency sets;
  immutable releases make a pinned URL's content unchangeable (integrity, not
  availability: a release can still be deleted). Rejected: PyPI under a new
  distribution name (blocked by direct-URL dependencies and adds a second
  namespace to govern); Git source pins (`git+https`) (rebuild on every install
  and pin a commit rather than a qualified artefact). Date/Author: 2026-11-20,
  planning agent; revised after release-engineering review.
- D4. Decision (ADR 0002, enforcement): add fitness rules now that fail when
  someone introduces a provider-extension surface: any `[project.entry-points]`
  group in `pyproject.toml` (console scripts belong in `[project.scripts]`,
  which is allowed, with a negative control); any import of, or attribute
  access to, `entry_points` from `importlib.metadata`, or any import of
  `pluggy`, `stevedore`, or `pkg_resources`, under `khufu/`; any function
  parameter named `provider`, `engine`, or `backend`, or any string literal
  `--provider` or `--engine`, under `khufu/`. Cyclopts derives `--provider`
  from a parameter named `provider`, so the parameter rule is the one that
  matters. Detection uses the `ast` module, so comments and prose do not trip
  it. `KIND_EXPERIMENTAL_PROVIDER=podman` is internal configuration of the
  single kind adapter, not a provider option, and the ADR says so. Once the
  command surface exists, roadmap 1.4 extends the check to walk the generated
  command descriptors and the profile schema (environment-variable and
  configuration spellings). Rationale: these rules are cheap, exact, and fail
  when the forbidden surface appears; broader scans for "docker" or "k3d" would
  flag legitimate remediation text. Rejected: deferring all enforcement to
  roadmap 1.3.2 (the import-boundary check there governs layering, not
  extension surfaces). Date/Author: 2026-11-20, planning agent; revised after
  systemd and test-architecture review.
- D5. Decision (ADR 0003, supervision invariants): each long operation runs as
  a transient service of the user's systemd manager (`systemd-run --user`,
  service type `exec`, `--collect`), never as a `--scope`, and never with
  `--pty`, `--pipe`, or `--wait`. The unit name is
  `khufu-job-<job-id>-a<attempt>.service`, with job identifiers restricted to
  `[a-z0-9-]` so no unit-name escaping is needed, which keeps names under 255
  characters. Unit identity is the unit's `InvocationID`, which the worker
  writes to the ledger at start. An `ExecStopPost=` finalizer writes
  `$SERVICE_RESULT` and `$EXIT_STATUS` to the ledger. Recovery reads
  `LoadState`, `ActiveState`, `Result`, and `InvocationID`;
  `LoadState=not-found` means "no live worker", and the outcome then comes from
  ledger records only. The worker's environment is passed explicitly
  (`--setenv`), because a transient service does not inherit the caller's
  environment. Every worker subprocess stays in the worker unit's control group
  (cgroup), except cluster containers, which deliberately live in Podman's own
  scopes; a nested `--scope` is forbidden unless bound to the worker unit. The
  exact flags are implemented and tested by roadmap 2.2.4; whether the worker
  unit needs `Delegate=yes` for kind is checked empirically by roadmap 2.1.2.
  Rationale: `--collect` unloads successful units immediately, so
  reconciliation by a fixed name cannot distinguish "never started" from
  "succeeded"; attempt suffixes avoid collisions with failed units on
  `jobs resume`; a `--scope` makes the invoking CLI the worker, so it receives
  the caller's terminal hang-up and interrupts and records no main-process
  result, breaking the observer rule. Rejected: a Khufu-owned daemon (a second
  supervisor to keep alive); `nohup` or double-fork (no supervision, no
  recorded result); foreground-only execution (couples work to the observer).
  Date/Author: 2026-11-20, planning agent; revised after systemd review.
- D6. Decision (ADR 0003, foreground mode and session limits): the foreground
  execution mode is deferred to roadmap task 5.1.2 ("Implement foreground
  execution for hosts without a usable systemd user session"), not abandoned.
  The contract 5.1.2 must honour is recorded now: record foreground execution
  in the job and report, never claim detached durability, and mark the job
  interrupted when the process is lost. Until then, mutating submissions check
  for a usable user manager before committing a job and refuse with exit code
  `3` (host prerequisite failure), leaving no queued job; read-only commands
  are never refused. A start failure after commit marks the job `failed` (exit
  `7`); a `--wait` observer whose unit is lost at logout exits `10`. Missing
  lingering is a `doctor` warning, not a refusal. `doctor` reports, and never
  repairs: whether a user manager is running, separately from whether the
  invoking environment can reach it (`XDG_RUNTIME_DIR` and the user bus are
  often absent under `sudo`, cron, non-PAM SSH sessions, containers, and CI
  agents even when a lingering manager runs); lingering, read from
  `/var/lib/systemd/linger/<user>` without D-Bus or
  `loginctl show-user --property=Linger` with it; the effective
  `UserStopDelaySec=` (without lingering, `user@.service` stops that long after
  the last session ends, default 10 seconds, stopping jobs and, through
  Podman's scopes, environment clusters; `infinity` keeps the manager after
  first login but does not start it at boot); that no transient unit or kind
  node survives a reboot, so recovery marks jobs interrupted and reconciles
  environments as stopped; the controllers delegated to `user@.service`;
  Podman's cgroup manager (must be `systemd`); and, informationally, whether
  `systemd-oomd` manages the user slice. `systemctl --user is-system-running`
  returning `degraded` (some unit failed) does not make the manager unusable.
  `KillUserProcesses=` governs session scopes, not services under the user
  manager (its compiled default is `yes` upstream and `no` on the planning
  host); it only ends a waiting observer at logout, which is harmless. The
  SQLite ledger under `$XDG_STATE_HOME/khufu` is a premise stated in ADR 0003's
  context (design §11.1 and roadmap 2.2.1 already settle it), not a separate
  decision. Rationale: roadmap 1.1.3 states the deferral and 5.1.2 schedules
  the mode; roadmap 5.1.3 (the regression matrix) already requires 5.1.2, so no
  matrix runner needs a workaround. Date/Author: 2026-11-20, planning agent;
  revised after systemd and governance review.
- D7. Decision required before `EP-M5` (ADR 0004, fixture-specification
  ownership). The question for the user: which repository owns the source of
  the typed fixture specifications for shared data services (initially
  CloudNativePG (CNPG) PostgreSQL clusters and Hyperspike Valkey)?

  Option A (Khufu owns): specifications ship in each Khufu release beside the
  platform lock; Nile Valley vendors them from the Khufu release pinned in
  `validation-estate.toml`. Strength: one release carries lock and
  specifications. Cost: Nile Valley's production GitOps rendering depends on
  releases of a local-validation tool, and Nile Valley's own operator pins
  (`chart_version` 0.26.1 for CNPG) either stay separate, which breaks
  alignment, or follow Khufu, which makes every production platform upgrade
  wait for a Khufu release.

  Option B (Nile Valley owns, recommended): Nile Valley owns the specifications
  and the production operator pins as the estate baseline, and publishes them
  as a digest-addressed, language-neutral JSON artefact (one canonical JSON
  bundle, or a sorted manifest of per-file SHA-256 digests, so the digest is
  reproducible). Khufu vendors a pinned revision into its release, records the
  upstream revision and digest in `platform.lock.toml`, and qualifies it
  locally. Nile Valley's renderers read the same artefact from its own tree,
  and the regression matrix in Nile Valley CI checks that the approved Khufu
  release's lock records the current baseline digest. Strength: one version
  axis owned by the estate owner, no dependency from production onto Khufu, and
  agreement with design §1.1, terms of reference §2 ("Nile Valley owns …
  rendered platform fixtures"), and the estate owner's stated need for "one
  platform baseline". Cost: a Khufu lock change that needs a new specification
  requires a Nile Valley change first.

  Option C (a third repository): a separate cadence, pin, and owner with no
  benefit over B.

  Either way, ADR 0004 decides the owner, the artefact identity
  (digest-addressed JSON), each side's consumption contract, and the alignment
  rule. It does not prescribe file layout (left to roadmap 3.1.1) or how Nile
  Valley's OpenTofu decodes the data (left to Nile Valley; OpenTofu's `file()`
  reads only local files and cannot validate JSON Schema, so Nile Valley CI
  validates and its tree holds the artefact). Date/Author: 2026-11-20, planning
  agent; reversed from the draft's option A after release-engineering review;
  awaiting the user's answer.
- D8. Decision (verification shape): validate this documentary change with a
  small decision-record suite: pure rule functions in
  `tests/decision_records.py`; parameterized truth-table tests and two
  Hypothesis properties; repository tests over the real `docs/` tree; one
  `pytest-bdd` feature whose positive scenario is a thin wrapper over the same
  rules; and the D4 fitness rules. Do not add `syrupy`: there is no
  multivariant output format. Do not add end-to-end tests: no command-line
  behaviour, persistence, or network boundary changes. Rationale: the user's
  instructions require pytest, `pytest-bdd`, and Hypothesis "where applicable",
  and roadmap 1.1's success criteria are structural and checkable. The
  governance reviewer recommended deferring both libraries until a task needs
  them; the user's directive and later roadmap needs (Hypothesis in 1.3.4 and
  2.2.2) outweigh that, and the suite was halved instead. Date/Author:
  2026-11-20, planning agent.
- D9. Decision (terms-of-reference edits): edit only the §9 register's
  resolution paths (implementation-home row: the accepted ADR; foreground row:
  ADR 0003 and roadmap 5.1.2). Leave §4.2 ("needs a foreground mode"), the §4.3
  CI row ("foreground execution"), and table 3 ("only foreground execution
  remains viable") unchanged. Rationale: they state needs and conditions, which
  deferral does not contradict, and the terms of reference should not carry
  delivery sequencing. Date/Author: 2026-11-20, planning agent; from governance
  review.
- D10. Decision (status and date grammar enforced by tests): the first
  non-blank line of the `## Status` body starts with one of `Proposed`,
  `Accepted`, `Superseded`, or `Deprecated`; `Accepted` must be followed by a
  space, a parenthesized ISO date such as `(2026-11-20)`, then a colon or full
  stop, a space, and a non-empty summary; a trailing period is allowed; an
  additional line starting `Amended by ADR-nnnn (YYYY-MM-DD)` is allowed. The
  first non-blank line of the `## Date` body is `YYYY-MM-DD`, optionally
  followed by a period. Rationale: the style guide requires a date and summary
  for `Accepted` but fixes no syntax; a fixed syntax makes the rule testable
  and matches the template's trailing periods. Date/Author: 2026-11-20,
  planning agent; from test-architecture review.

## Outcomes & retrospective

Not started. Complete at each milestone and at completion.

## Context and orientation

Inspected base revision: `4ab9802` ("Remove the tool list from AGENTS.md
(#34)"), the `main` commit below `regenerate-typos-config`. Line numbers refer
to that revision; relocate them with `grep -n` on the quoted heading.

The repository is a Python 3.14 project generated from a template. Its package
`khufu/` contains only `khufu/__init__.py` and `khufu/pure.py`. Tests live in
`tests/` and run under pytest 9.1.1 (from `uv.lock`) with `pytest-xdist` and
`pytest-timeout` (30 seconds per test; `pyproject.toml`
`[tool.pytest.ini_options]`, which also sets `testpaths = ["tests"]`). Existing
tests are `tests/test_stub.py`, `tests/test_action_workflow.py`, and
`tests/test_codescene_publisher_wiring.py`. The last is the closest pattern for
a repository-file conformance test: it sets
`ROOT = Path(__file__).resolve().parents[1]`, parses repository files, and
gives every assertion a message. There is no `conftest.py` and no Markdown
parsing yet. Neither `tests/` nor `scripts/` has an `__init__.py`;
`tests/test_action_workflow.py` imports `scripts.action_workflow` because
`[tool.uv] package = true` installs the project in editable mode, which puts
the repository root on `sys.path` so both directories load as namespace
packages. `ty` resolves the root the same way. `.gitignore` already lists
`.hypothesis/`.

Lint constraints that shape the test code: interrogate requires a docstring on
every function, including tests and steps; Vulture runs on `tests/` with
`ignore_names = ["test_*", "pytestmark"]` and `min_confidence = 60`, so
pytest-bdd step functions and fixtures need `ignore_decorators`, and every enum
member and dataclass field must be read somewhere; the DF12 Pylint plugin flags
three or more substring assertions against one subject in a test (R9109) and
assertions against literals with eight or more leaves (R9108), so token checks
compute a `missing` list and assert it is empty; the duplication gate
(`min-size = 24`) forbids repeated test-text builders; the mutation workflow
copies only paths in `[tool.mutmut] also_copy` plus `tests/` and
`pyproject.toml`, so `docs/` must be added.

Documents and the passages this plan changes:

- `docs/khufu-design.md` (Draft v0.1, last substantive revision 2026-10-17):
  front matter; §1.1 "Implementation home" (lines 50-59: provisional pending
  ADR 0001, and Nile Valley keeps the shared fixture specifications); §2 (lines
  61-92, fixed substrate); §3.1 Nile Valley row (line 109); §4.3 "Estate
  pinning" (lines 199-213); §5.1-5.2 (lines 215-274, single cluster adapter "is
  a module, not a registry"); §7.1 (lines 421-446, platform lock); §8.1-8.2
  (lines 527-548); §11.3 "Supervision" (lines 786-800, describes a foreground
  CI mode as present); §12.1 GitOps suite (lines 889-894); §17 tables 7 and 8
  (lines 1118-1140); §18 "Open questions and ADR candidates" (lines 1142-1158;
  its anchor `#18-open-questions-and-adr-candidates` is linked from
  `docs/developers-guide.md` line 95).
- `docs/terms-of-reference.md` (version 0.1): §2 domain bedrock (lines 58-62,
  Nile Valley owns rendered platform fixtures); §9 register (lines 304-312).
- `docs/context.md`: the "Nile Valley" row (line 23, "owns … GitOps
  fixtures") and the "Platform lock" row (line 43).
- `docs/users-guide.md`: prerequisites (lines 36-45, "Hosts without one use
  the foreground execution mode") and "Execution modes" (lines 314-323).
- `docs/developers-guide.md`: lines 95-97 ("ADR candidates … decisions
  awaiting ratification").
- `docs/roadmap.md`: 1.1 (lines 26-66); 2.1.1 (doctor checks, lines 244-252,
  no session guarantees); 2.1.2 (kind creation); 2.2.4 (supervision); 2.6.4
  (Episodic's thin delegate, the first consumer of a pinned release); 3.1.1
  (platform lock); 5.1.1 (estate manifest); 5.1.2 (foreground mode); 7.1.1
  (GitOps suite).
- `docs/contents.md`: three groups, no ADR or ExecPlan entries.
- `docs/documentation-style-guide.md`: ADR rules (lines 515-662) and the ADR's
  purpose (lines 303-320).
- `README.md`: checked; lines 26 and 31-32 are consistent with the planned
  ADRs, so no change is planned.

Gates (Makefile targets): `make fmt`, `make check-fmt`, `make typecheck` (`ty`),
`make lint` (Ruff, interrogate, Pylint with the DF12 plugin, Ambrleaks,
Skylos, Vulture, duplication, action lint), `make test`
(`uv run pytest -v -n auto`), `make audit` (`pip-audit`), `make markdownlint`
(markdownlint-cli2 plus the `typos` spelling gate), and `make nixie` (Mermaid).

External facts gathered during planning, each an axiom below:

- `systemd-run(1)`: `--user` talks to the user's service manager; a transient
  service runs detached and keeps running when the invoking process exits; a
  `--scope` runs the command synchronously in the caller's process, keeping its
  environment and terminal; `--collect` unloads units after they stop,
  successful ones immediately.
- `logind.conf(5)` and `loginctl(1)` (systemd 257 on the Rocky Linux 10
  planning host): `UserStopDelaySec=` (default 10 seconds) keeps
  `user@.service` after the last session; `enable-linger` starts the user
  manager at boot and keeps it after logout; `KillUserProcesses=` governs
  session scopes.
- kind rootless documentation[^1]: cgroup v2; `cpu` controller delegation for
  user services (default from systemd 252); Podman 3.0 or later; possibly
  `systemd-run --scope --user -p Delegate=yes`; PID, inotify, iptables-module,
  privileged-port, and log-driver hazards; no block-storage or NFS mounts.
- GitHub immutable releases[^2] (generally available 2025-10-28): once
  published, assets cannot be added, modified, or deleted and the tag cannot be
  moved; a deleted release's tag cannot be reused; the tag is unprotected until
  publication.
- uv documentation: PyPI does not accept packages with direct-URL
  dependencies.

Skills for the implementer: `execplans`, `hexagonal-architecture` (pure rules
versus the thin filesystem edge), `python-router`, `python-testing`,
`hypothesis`, `en-gb-oxendict-style`, `commit-message`, and `mapsplice` if
roadmap tasks are inserted.

## Conformance basis

Upstream artefacts, all at revision `4ab9802`:

- Terms of reference: `docs/terms-of-reference.md`, version 0.1; §2, §4.2,
  §4.3, §9 (table 4).
- Technical design: `docs/khufu-design.md`, Draft v0.1 (2026-10-17); §1.1,
  §2, §3.1, §3.2, §4.3, §5.1-5.2, §7.1, §8.1-8.2, §10.3, §11.1, §11.3, §12.1,
  §17, §18.
- Roadmap: `docs/roadmap.md`, tasks 1.1.1-1.1.4 and the tasks named above.
- Governing standard: `docs/documentation-style-guide.md`, ADR section.
- ADRs: none exist; this plan creates the first four.

Requirements:

- `REQ-HOME` (roadmap 1.1.1; terms of reference §9 row 1; design §1.1, §4.3,
  §18): one accepted ADR names the code home, the estate-manifest home, the
  regression-matrix home, the Nile Valley responsibilities, and the release
  channel consumers pin, and records the divergence from the source design and
  the release and pinning consequences.
- `REQ-SUBSTRATE` (roadmap 1.1.2; design §2, §5.1, §17 table 7): one accepted
  ADR fixes the stack, forbids `--provider`, `--engine`, k3d, Docker, rootful
  fallback, and alternate-cluster plug-ins, and states that test doubles are
  not production extension points.
- `REQ-SUPERVISION` (roadmap 1.1.3; design §11.1, §11.3, §17 table 8): one
  accepted ADR makes transient systemd user services the worker owners and
  waiting CLIs observers, defers the foreground mode, and lists the
  session-survival limits `doctor` must report.
- `REQ-FIXTURES` (roadmap 1.1.4; design §3.1, §7.1, §12.1, §18): one accepted
  ADR names the owning repository, each side's consumption mechanism, and the
  alignment rule with the platform lock.
- `REQ-FORMAT` (style guide): every ADR satisfies naming, heading-order,
  status, and date rules.
- `REQ-TRACE` (AGENTS.md documentation maintenance; terms of reference
  "indexed in `docs/contents.md`"): design §18 and `docs/contents.md` link each
  accepted ADR, and no live document contradicts them.

Gaps at the base revision:

- `GAP-NO-ADRS`: `docs/adrs/` does not exist.
- `GAP-FOREGROUND`: design §11.3 and the users' guide present the foreground
  mode as current.
- `GAP-SESSION-LIMITS`: no document enumerates session-survival limits;
  roadmap 2.1.1 omits them.
- `GAP-RELEASE-CHANNEL`: no channel is defined; the PyPI name is taken;
  immutable releases and tag rules are off.
- `GAP-FIXTURE-ALIGNMENT`: nothing states how specification versions align
  with the platform lock; design §1.1 presupposes an owner that §18 leaves open.
- `GAP-ADR-INDEX`: `docs/contents.md` indexes no ADRs.

Trace chains:

```plaintext
ToR §9 row 1 -> REQ-HOME -> design §1.1, §4.3 -> EP-M2 -> test_foundational_adr_is_accepted[0001]
roadmap 1.1.2 -> REQ-SUBSTRATE -> design §2, §17 -> EP-M1, EP-M3 -> tests/test_substrate_fitness.py
roadmap 1.1.3 -> REQ-SUPERVISION, GAP-FOREGROUND, GAP-SESSION-LIMITS -> design §11.3 -> EP-M4
  -> test_foundational_adr_is_accepted[0003]
roadmap 1.1.4 -> REQ-FIXTURES, GAP-FIXTURE-ALIGNMENT -> design §3.1, §7.1 -> EP-M5
  -> test_foundational_adr_is_accepted[0004]
style guide -> REQ-FORMAT -> EP-M1 -> tests/test_decision_record_rules.py
AGENTS.md -> REQ-TRACE, GAP-ADR-INDEX -> EP-M2 to EP-M5 -> test_adr_is_linked[0001..0004]
```

## Verification plan

### Abstract model

A decision-record set is a finite map from file names in `docs/adrs/` to
Markdown texts. A file name is valid when it equals `f"adr-{n:04d}-{slug}.md"`
for an integer `n` in 0-9999 and a slug of one or more lowercase ASCII
alphanumeric words joined by single hyphens. A text is a valid record when its
first heading is `# Architectural decision record (ADR) NNNN: TITLE`; its
level-two headings, ignoring those inside fenced code blocks, begin with
`Status`, `Date`, and `Context and problem statement` in that order; its Status
and Date bodies satisfy D10; and, when `Accepted`, it has a
`## Decision outcome` section. The record is consistent with its file name when
the heading number equals `n` and `slugify(TITLE)` equals the slug. A section's
text runs from its heading to the next level-two heading, so `### Consequences`
belongs to `## Decision outcome`.

Fenced code blocks follow CommonMark: an opening run of three or more backticks
or tildes, closed by a run of the same character at least as long.

Malformed input yields named violations (for example `bad-file-name`,
`missing-title`, `heading-order`, `unknown-status`, `accepted-without-date`,
`accepted-without-summary`, `bad-date`, `title-slug-mismatch`,
`duplicate-number`, `missing-decision-outcome`), never an exception, so one run
reports every problem.

### Invariants and lemmas

- `INV-FILENAME` (`REQ-FORMAT`): for every `n` in 0-9999 and every valid slug,
  parsing `f"adr-{n:04d}-{slug}.md"` returns `(n, slug)`.
- `INV-SLUG` (`REQ-FORMAT`): for every text `t`, `slugify(t)` is empty or a
  valid slug, `slugify(slugify(t)) == slugify(t)`, and when `slugify(t)` is
  non-empty, `f"adr-0001-{slugify(t)}.md"` parses. Accented letters are
  transliterated (style guide: "Transliterate accented letters").
- `INV-RECORD` (`REQ-FORMAT`): each malformed status, date, title, and heading
  layout in the truth table yields exactly its named violation, and each
  well-formed layout yields none.
- `INV-FOUNDATION` (`REQ-HOME`, `REQ-SUBSTRATE`, `REQ-SUPERVISION`,
  `REQ-FIXTURES`): the repository contains ADRs 0001-0004 at the roadmap paths,
  each valid, `Accepted`, and naming in its `## Decision outcome` section the
  identifiers its roadmap criterion requires.
- `INV-TRACE` (`REQ-TRACE`): each of ADRs 0001-0004 exists and is linked by
  relative path from design §18 and from `docs/contents.md`.
- `INV-NO-PLUGIN` (`REQ-SUBSTRATE`): the fitness rules report no violation for
  the repository and exactly one for each seeded forbidden surface.
- `L-SECTIONS`: heading extraction ignores fenced code, so `INV-RECORD` and
  `INV-FOUNDATION` hold for real files whose code fences contain `#` lines.

### Axioms (trusted, not verified here)

- `AXIOM-SYSTEMD-TRANSIENT`: `systemd-run(1)` semantics for `--user`,
  transient services, `--scope`, `--collect`, `Type=exec`, `ExecStopPost=`, and
  `InvocationID`. ADR 0003 depends on them; roadmap 2.2.4 tests them.
- `AXIOM-LOGIND-LINGER`: `logind.conf(5)` and `loginctl(1)` semantics for
  `UserStopDelaySec=`, lingering, and `KillUserProcesses=`; no transient unit
  survives a reboot. ADR 0003 depends on them; roadmap 2.1.1 tests the `doctor`
  findings.
- `AXIOM-KIND-ROOTLESS`: kind's documented rootless requirements and hazards.
  ADR 0002 depends on them; roadmap 2.1.1 and 2.1.2 test them.
- `AXIOM-GH-IMMUTABLE`: GitHub immutable releases guarantee integrity of a
  published tag and its assets, not availability. ADR 0001 depends on it.
- `AXIOM-PYPI-DIRECT-URL`: PyPI rejects distributions whose metadata contains
  direct-URL dependencies. ADR 0001 depends on it.
- `AXIOM-PYTEST-BDD`: `pytest-bdd` 9 binds Gherkin steps to Python functions,
  applies pytest marks to `@scenario`-bound tests, skips already-bound
  scenarios in a later `scenarios()` call, and runs under `pytest-xdist`. The
  suite depends on it; `EP-M1` exercises it.

### Methods per obligation

- Obligation: `INV-FILENAME`. Method: Hypothesis property with a construction
  oracle, plus named rejection examples. Domain: `st.integers(0, 9999)` and
  slugs from `st.from_regex(r"[a-z0-9]+(-[a-z0-9]+)*", fullmatch=True)`.
  Artefact: `tests/test_decision_record_rules.py::test_file_name_round_trip` and
  `::test_file_name_rejections` (parameterized). Evidence: before the rules
  module exists, collection fails with `ModuleNotFoundError`; afterwards both
  pass. Non-vacuity: the oracle is the f-string construction, not a second
  regular expression; rejection rows `adr-1-x.md`, `adr-0001-X.md`,
  `adr-0001-a--b.md`, `ADR-0001-a.md`, `adr-0001-.md`, and `adr-00001-a.md`
  each assert `None`; seeded fault: accept three-digit numbers, and
  `adr-001-x.md` must fail.
- Obligation: `INV-SLUG`. Method: Hypothesis property over `st.text()` plus
  named examples. Artefact: `::test_slugify_is_idempotent_and_parseable` and
  `::test_slugify_examples`. Non-vacuity: `@example` cases include an empty
  string, punctuation only, and accented text; named examples map
  `Implementation home`, `Fixed kind rootless substrate`,
  `Systemd user service supervision`, `Shared fixture specifications`, and
  `Café` to `implementation-home`, `fixed-kind-rootless-substrate`,
  `systemd-user-service-supervision`, `shared-fixture-specifications`, and
  `cafe`; seeded fault: keep uppercase letters, and the example rows fail.
- Obligation: `INV-RECORD` and `L-SECTIONS`. Method: parameterized truth
  table, one row per class, every row built by one shared helper
  (`record_text(...)`) that the BDD steps also use. Rows: each of the four
  status words (so every `Status` member is referenced); `Accepted` with and
  without date and summary; an unknown word; an amendment banner; a valid and
  an invalid date, with and without a trailing period; title and slug match and
  mismatch; headings out of order; a `## Status` line inside a three-backtick
  fence, a `~~~` fence, and a four-backtick fence containing three backticks; an
  `Accepted` record without `## Decision outcome`; two files sharing a number.
  Artefact: `::test_record_violations`. Non-vacuity: each row asserts the exact
  set of violation codes, so a rule that accepts everything fails every
  negative row, and one that rejects everything fails every positive row.
- Obligation: `INV-FOUNDATION` and `INV-TRACE`. Method: repository tests and a
  BDD scenario. Artefact: `tests/test_decision_records_repository.py`
  (`test_registry_is_valid`, `test_foundational_adr_is_accepted[0001..0004]`,
  `test_adr_is_linked[0001..0004]`) and
  `tests/features/decision_records.feature` bound by
  `tests/test_decision_records_bdd.py`. Evidence: in `EP-M1` each per-ADR case
  carries `pytest.mark.xfail(strict=True, reason="ADR nnnn lands in EP-Mk")`
  through `pytest.param(..., marks=...)`; each ADR milestone removes the two
  markers for its ADR; the BDD foundation scenario is bound with
  `@scenario(...)` plus `@pytest.mark.xfail(strict=True)` until `EP-M5`. Both
  link and acceptance cases first assert the ADR file exists, so they fail (and
  strict xfail holds) before the ADR lands. Non-vacuity: token checks compute
  `missing = [t for t in tokens if t not in section]` within
  `## Decision outcome` only and assert `not missing`; a seeded fault that
  deletes one token from an ADR's decision outcome must fail its case.
- Obligation: `INV-NO-PLUGIN`. Method: example-based fitness tests with
  seeded negative controls. Artefact: `tests/test_substrate_fitness.py`.
  Evidence: zero violations for the repository; exactly one violation code for
  each synthetic input: a pyproject mapping with an entry-point group; a
  pyproject mapping with only `[project.scripts]` (zero violations); source
  texts with `from importlib.metadata import entry_points as ep`,
  `import pluggy`, `def run(provider: str) -> None: ...`, and
  `Parameter(name="--engine")`. Non-vacuity: the repository scan asserts it
  parsed at least the two existing files under `khufu/`, so an empty glob
  cannot pass.

Required identifiers per ADR, matched in `## Decision outcome` only. They are
stable names, not prose or roadmap numbers:

```plaintext
0001: leynos/khufu, leynos/nile-valley, validation-estate.toml, SHA-256
0002: --provider, --engine, k3d, Docker, rootful
0003: systemd-run --user, InvocationID, linger, doctor
0004: platform.lock.toml, digest, plus the owning repository name from the D7 answer
```

### Formal verification decision

No model checking or formal proof is warranted. The obligations are syntactic
checks over finite documents and a filename grammar. Hypothesis covers the
open-ended grammar; truth tables cover the finite status, date, and heading
classes. The substantive claims inside the ADRs (systemd lifetimes, kind
requirements, immutable releases) are external axioms that roadmap tasks 2.1.1,
2.1.2, and 2.2.4 test against the real interfaces.

### BDD feature

Adopted, at `tests/features/decision_records.feature`, bound by
`tests/test_decision_records_bdd.py`. The foundation scenario is bound first
with `@scenario` and a strict xfail mark until `EP-M5`; `scenarios(...)` then
binds the rest. Steps call the same rule functions and the shared
`record_text(...)` builder used by the unit tests.

```gherkin
Feature: Foundational decision records
  Khufu's foundational decisions are recorded as accepted ADRs that later
  roadmap steps can rely on.

  Scenario: The four foundational ADRs are accepted and linked
    Given the decision records in the repository
    When the decision-record registry is validated
    Then ADRs 0001, 0002, 0003, and 0004 are accepted
    And each of them is linked from the design document and the contents index
    And the registry reports no violations

  Scenario: A record with an unknown status is rejected
    Given a decision record "adr-0099-example.md" whose status is "Ratified"
    When the decision-record registry is validated
    Then the registry reports the violation "unknown-status" for "adr-0099-example.md"

  Scenario: A record whose title does not match its file name is rejected
    Given a decision record "adr-0099-example.md" titled "Something else"
    When the decision-record registry is validated
    Then the registry reports the violation "title-slug-mismatch" for "adr-0099-example.md"

  Scenario: A provider plug-in surface is refused
    Given package metadata declaring the entry-point group "khufu.providers"
    When the substrate fitness rules are applied
    Then the rules report the violation "entry-point-group"
```

Scenario 1 traces to `REQ-HOME`, `REQ-SUBSTRATE`, `REQ-SUPERVISION`,
`REQ-FIXTURES`, and `REQ-TRACE`; scenarios 2 and 3 to `REQ-FORMAT`; scenario 4
to `REQ-SUBSTRATE`. Scenarios 2-4 pass from `EP-M1`.

## Plan of work

Each milestone ends with the gate sequence in `Concrete steps` and one or more
atomic commits. Every ADR milestone adds that ADR's entry to the "Decision
records" group in `docs/contents.md` and its link in design §18, and removes
its two strict-xfail markers, so the documents and tests never disagree at a
milestone boundary.

### `EP-M1` decision-record suite and substrate fitness rules

Assigned: `REQ-FORMAT`, `INV-FILENAME`, `INV-SLUG`, `INV-RECORD`,
`INV-NO-PLUGIN`, D4, D8, D10.

1. Configuration commit. In `pyproject.toml`: add `"pytest-bdd==9.0.1"` and
   `"hypothesis==6.170.17"` (or the newest patch releases at implementation
   time, pinned exactly in the style of the `ruff`, `cyclopts`, and `ty` pins)
   to `[dependency-groups] dev`; add `"docs/"` to `[tool.mutmut] also_copy`; add
   `pythonpath = ["."]` to `[tool.pytest.ini_options]`; add
   `ignore_decorators = ["@given", "@when", "@then", "@pytest.fixture"]` to
   `[tool.vulture]`. Run `uv lock`, then `make audit`. Commit ("Add pytest-bdd
   and Hypothesis for decision-record tests").
2. Red. Write `tests/test_decision_record_rules.py` importing
   `import tests.decision_records as dr`. Run
   `uv run pytest tests/test_decision_record_rules.py`; expect
   `ModuleNotFoundError: No module named 'tests.decision_records'`.
3. Green. Write `tests/decision_records.py`: pure functions over strings, no
   I/O. Proposed surface:

   ```python
   import collections.abc as cabc
   import dataclasses as dc
   import enum


   class Status(enum.StrEnum):
       PROPOSED = "Proposed"
       ACCEPTED = "Accepted"
       SUPERSEDED = "Superseded"
       DEPRECATED = "Deprecated"


   @dc.dataclass(frozen=True, slots=True)
   class Violation:
       file_name: str
       code: str  # stable kebab-case code, for example "unknown-status"


   def parse_file_name(file_name: str) -> tuple[int, str] | None: ...
   def slugify(title: str) -> str: ...
   def level_two_sections(text: str) -> dict[str, str]: ...
   def record_status(text: str) -> Status | None: ...
   def record_violations(file_name: str, text: str) -> frozenset[str]: ...
   def registry_violations(files: cabc.Mapping[str, str]) -> tuple[Violation, ...]: ...
   ```

   Rerun the focused tests until green. Put the shared `record_text(...)`
   builder in the rule test module, or in `tests/conftest.py` if the BDD module
   needs it too.
4. Repository tests. Write `tests/test_decision_records_repository.py`. A
   fixture reads `ROOT / "docs" / "adrs" / "*.md"` into a mapping (an empty
   mapping when the directory is absent); this is the only filesystem access.
   `test_registry_is_valid` passes now. The eight per-ADR cases carry strict
   xfail markers as described in `Verification plan`.
5. BDD. Write the feature and `tests/test_decision_records_bdd.py` as
   described above.
6. Fitness rules. Write `tests/test_substrate_fitness.py` with
   `entry_point_violations(pyproject: cabc.Mapping[str, object]) -> list[str]`
   and `source_violations(text: str) -> list[str]` (using `ast`), the
   repository test, and the seeded tests.
7. Negative controls. Apply each seeded fault from `Verification plan` in the
   working tree, observe the expected failure, record the transcript in
   `Artefacts and notes`, and revert with `git checkout -- <file>`.
8. Run the full gate sequence. Commit ("Add decision-record conformance
   suite").

End state: rule, property, fitness, and negative BDD tests pass; eight per-ADR
cases and the foundation scenario are strict xfails.

### `EP-M2` ADR 0001: implementation home

Assigned: `REQ-HOME`, `GAP-RELEASE-CHANNEL`, `GAP-ADR-INDEX`, D1-D3.

Create `docs/adrs/adr-0001-implementation-home.md`, titled
`# Architectural decision record (ADR) 0001: Implementation home`.

- Status: `Accepted (<approval date>)` followed by the summary "Khufu's code,
  package, and releases live in `leynos/khufu`; Nile Valley hosts the estate
  manifest and regression matrix." (D10 grammar).
- Context and problem statement: the source design placed Khufu in
  `leynos/nile-valley`; this repository exists; the terms of reference ask
  which repository hosts the implementation; design §4.3 requires exact pins
  without network discovery; Nile Valley is an OpenTofu, Flux, and Python
  platform repository whose cadence follows cloud infrastructure; the PyPI name
  `khufu` belongs to an unrelated project.
- Decision drivers: one installable package with its own release; anti-drift
  enforcement in one place; exact, hash-verified pins; no dependency-confusion
  exposure.
- Options considered: A, Khufu in `leynos/khufu` (chosen); B, Khufu inside
  `leynos/nile-valley` (the source design); C, a separately published package
  inside Nile Valley. Compare release coupling, CI scope, review ownership, and
  pin clarity in a captioned table.
- Decision outcome: code home `leynos/khufu`; estate manifest
  `validation-estate.toml` and the regression matrix in `leynos/nile-valley`;
  Nile Valley responsibilities (estate manifest, regression matrix, GitOps
  rendering); the release channel and pin shape per D3, including the unsafe
  and safe install commands. State in plain text, without a link, that
  ownership of the shared fixture specifications is decided separately (design
  §18, ADR 0004). `### Consequences`: the estate-manifest fields (version, tag,
  commit SHA, wheel URL and SHA-256, dependency-lock URL and SHA-256, platform
  lock digest, fixture-specification digest); the workspace pin shape for
  roadmap 1.5.2 (reject a `khufu` pin without URL and hash); the release
  preconditions from D3; candidates per D3; Nile Valley CI fetches the pinned
  assets, never "latest".
- Known risks and limitations: integrity is guaranteed, availability is not (a
  release can be deleted; CI runners start with empty caches; egress to
  `release-assets.githubusercontent.com` is required); a deleted release's tag
  cannot be reused; the regression-matrix runner choice (design §18 open item)
  remains with roadmap 5.1.3.

Also: rewrite only the provisional sentence of design §1.1 (lines 54-56) to
cite the accepted ADR, leaving the fixture clause (lines 57-59) unchanged until
`EP-M5`; link the ADR from design §4.3 and state the pin shape; mark design
§18's first bullet accepted with a link; set the terms-of-reference §9
implementation-home row's path to the ADR link; create the "Decision records"
group in `docs/contents.md` with this ADR; add a sub-bullet to roadmap 2.6.4
("Switch Episodic's local validation entry point to Khufu behind a thin
delegate") requiring that the pinned Khufu release be published per ADR 0001's
preconditions. Remove the two 0001 xfail markers. Gate and commit ("Accept ADR
0001: implementation home").

### `EP-M3` ADR 0002: fixed kind rootless substrate

Assigned: `REQ-SUBSTRATE`, `INV-NO-PLUGIN`, D4.

Create `docs/adrs/adr-0002-fixed-kind-rootless-substrate.md`, titled
`...0002: Fixed kind rootless substrate`. Context: four drifting
implementations across k3d, kind, Docker, and Podman; design §1-2; Episodic's
demonstrated path. Drivers: drift removal, qualification surface, rootless
safety. Options: fixed stack (chosen); provider matrix behind a plug-in
interface; kind fixed with a selectable engine; rootful fallback when rootless
fails; captioned table. Decision outcome: the stack; every forbidden surface by
name (`--provider`, `--engine`, k3d, Docker, rootful fallback,
alternate-cluster plug-in interface); `KIND_EXPERIMENTAL_PROVIDER=podman` as
internal configuration of the single kind adapter; test doubles substitute
ports in tests and are never selectable by users, configuration, environment
variables, or entry points. `### Consequences`: the fitness rules in
`tests/test_substrate_fitness.py` and their planned extension in roadmap 1.4;
`doctor` reports host prerequisites (citing kind's rootless documentation in a
footnote) and never repairs them; a new substrate requires a superseding ADR,
not a plug-in. Known risks: host variance; GitHub-hosted runners may lack
delegation.

Update design §2, §5.2 ("module, not a registry"), §17 table 7 introduction,
and §18 second bullet with links; add the `docs/contents.md` entry. Remove the
two 0002 xfail markers. Gate and commit.

### `EP-M4` ADR 0003: systemd user-service supervision

Assigned: `REQ-SUPERVISION`, `GAP-FOREGROUND`, `GAP-SESSION-LIMITS`, D5, D6.

Create `docs/adrs/adr-0003-systemd-user-service-supervision.md`, titled
`...0003: Systemd user service supervision`. Context: multi-minute cluster work
must outlive the invoking terminal or agent; the SQLite ledger under
`$XDG_STATE_HOME/khufu` is the durable record (premise; design §11.1, roadmap
2.2.1). Drivers: detached durability, crash recovery without a second worker,
observer independence, honest guarantees. Options (captioned table): transient
user services (chosen); a Khufu-owned daemon; `nohup` or double-fork;
foreground-only execution; `systemd-run --scope` (rejected for the reason in
D5). Decision outcome: the invariants in D5, the observer rule (killing a
waiting CLI never stops the worker; cancellation is the explicit `jobs cancel`
operation), the deferral and refusal sequencing in D6, and the `doctor`
session-survival findings in D6. `### Consequences`: roadmap 2.1.1 gains the
session findings; roadmap 2.1.2 checks whether the worker unit needs
`Delegate=yes`; roadmap 2.2.4 implements the invariants; recovery reconciles
environments as well as jobs. Known risks: hosts without a user manager cannot
run jobs until roadmap 5.1.2; reboot always interrupts; the compiled
`KillUserProcesses=` default differs between distributions.

In the same commit: replace the present-tense foreground paragraph in design
§11.3 with the deferral and session limits and link the ADR; mention lingering
and environment clusters in design §17 table 8's systemd row; mark design §18's
third bullet accepted; update the users' guide prerequisites (lines 36-45) and
"Execution modes" (lines 314-323) to say detached execution needs a usable user
manager, lingering is needed for jobs and environments to outlive logout,
reboot interrupts jobs and stops environments, and the foreground mode is
planned but not yet available; set the terms-of-reference §9 foreground row's
path to "ADR 0003; roadmap 5.1.2"; add "session guarantees (user manager
reachability, lingering, `UserStopDelaySec=`, delegated controllers, Podman
cgroup manager)" to roadmap 2.1.1's checklist; add the `docs/contents.md`
entry. Remove the two 0003 xfail markers. Gate and commit.

### `EP-M5` ADR 0004: shared fixture specifications

Assigned: `REQ-FIXTURES`, `GAP-FIXTURE-ALIGNMENT`, D7. Starts only after the
user's answer on D7 is recorded in `Decision log` and `Progress`.

Create `docs/adrs/adr-0004-shared-fixture-specifications.md`, titled
`...0004: Shared fixture specifications`. Context: Nile Valley's OpenTofu
modules render CNPG `Cluster` and Hyperspike `Valkey` resources for Flux with
their own operator pins; Khufu's renderers will render the same resources for
direct Helm execution; design §3.2's Valkey resource-identity hazard shows the
cost of divergence; design §7.1 makes the lock own the custom resource
definition (CRD) schemas and operator versions Khufu qualifies. Drivers: one
specification source, one version axis, language neutrality (Python and
OpenTofu), no dependency from production onto a local-validation tool unless
the user chooses it, no network discovery. Options: A, B, and C from D7 in a
captioned table comparing version axes, dependency direction, and each side's
consumption mechanism. Decision outcome: the chosen owner; the artefact
identity (digest-addressed JSON with a reproducible digest); Khufu-side
consumption (vendored or packaged files, digest recorded in
`platform.lock.toml`); Nile Valley-side consumption (artefact in its own tree,
validated in its CI); the alignment rule. Layout is left to roadmap 3.1.1 and
OpenTofu decoding to Nile Valley. `### Consequences`: design and context
wording; the GitOps suite (design §12.1, roadmap 7.1.1) renders from these
specifications; Nile Valley adoption is a Nile Valley change.

Update design §1.1's fixture clause and §3.1's Nile Valley row to match the
answer; add the specification digest to design §7.1's lock contents; link the
ADR from design §12.1 and mark §18's fourth bullet accepted; update the
`docs/context.md` "Nile Valley" and "Platform lock" rows so they agree with the
ADR; add roadmap follow-ups: a sub-bullet under 3.1.1 (the platform lock task)
recording the specification digest, and a sub-bullet under 5.1.1 ("Define
`validation-estate.toml` in Nile Valley") recording Nile Valley's adoption of
the specification artefact; add the `docs/contents.md` entry. Add the owner
token from the D7 answer to the 0004 row of the identifier table. Remove the
two 0004 xfail markers and the foundation scenario's marker. Gate and commit.

### `EP-M6` documentation closure

Assigned: `REQ-TRACE`, `GAP-ADR-INDEX`.

1. `docs/contents.md`: add a `docs/adrs/` directory entry above the four ADR
   entries and an entry for `docs/execplans/`.
2. `docs/developers-guide.md`: replace lines 95-97 ("ADR candidates …
   awaiting ratification") with a link to the "Decision records" group, and add
   a short "Decision records" subsection: where ADRs live; the filename,
   heading, status, and date rules (D10); that
   `tests/test_decision_records_repository.py` and the BDD feature enforce
   them; that every accepted ADR must be linked from design §18 and
   `docs/contents.md`; how to amend or supersede an ADR; and the substrate
   fitness rules, including that test doubles are never production extension
   points.
3. `docs/khufu-design.md` front matter: set "Last substantive revision" to the
   completion date; keep "Status: Draft v0.1" unless the user directs
   otherwise. Keep the §18 heading text so its anchor stays valid, adding the
   ADR links beneath it; if it must change, update the developers' guide link
   in the same commit.
4. Stale-claim sweep, excluding ExecPlans:

   ```bash
   rg -n -i --glob '!docs/execplans/**' docs -e provisional -e "pending acceptance" \
     -e "awaiting ratification" -e "ADR candidate" -e "foreground (execution|mode)" \
     -e "GitOps fixtures" -e "Hosts without one use"
   ```

   Every hit must agree with the ADRs or be edited. Expected surviving hits:
   the terms-of-reference needs statements kept by D9, and the design's
   description of the deferred mode.
5. Roadmap: mark 1.1.1-1.1.4 done (`- [x]`).
6. Run the full gate sequence. Update `Progress`, `Outcomes & retrospective`,
   and set the status to `COMPLETE`.

## Milestones and plateaus

- `EP-M1`: the suite exists and is green except for nine strict xfails.
  Requirements: `REQ-FORMAT`, `INV-NO-PLUGIN`. Conformance: no `khufu/` change;
  only authorized configuration. Recovery: revert the two commits. Remaining:
  all ADRs. Compatibility: none.
- `EP-M2`: ADR 0001 accepted, linked, and its xfails removed. Conformance: the
  terms-of-reference implementation-home question is closed; no release
  workflow or Nile Valley edits. Recovery: revert the ADR commit. Remaining:
  ADRs 0002-0004. Compatibility: none.
- `EP-M3`: ADR 0002 accepted and enforced. Recovery: revert. Compatibility:
  none.
- `EP-M4`: ADR 0003 accepted; no live document claims the foreground mode is
  available. Recovery: revert the single commit (ADR and reconciling edits land
  together). Compatibility: none.
- `EP-M5`: ADR 0004 accepted per the user's D7 answer; the foundation scenario
  passes. Recovery: revert. Compatibility: none.
- `EP-M6`: indexes, developers' guide, and roadmap current; all gates green.
  Compatibility: none.

At each boundary, check: the assigned requirements are satisfied; the design is
still followed or the ADR records the change; no upstream assumption was
falsified; no unapproved interface, dependency, trust boundary, or persisted
format changed; the trace links in `Conformance basis` are current.

## Concrete steps

Working directory: the repository root. Use `bash` with `set -o pipefail` so
`tee` cannot hide a failing gate. Logs follow
`/tmp/$ACTION-khufu-1-1-ratify-early-decisions.out`.

```bash
set -o pipefail
make fmt 2>&1 | tee /tmp/fmt-khufu-1-1-ratify-early-decisions.out
make check-fmt 2>&1 | tee /tmp/check-fmt-khufu-1-1-ratify-early-decisions.out
make typecheck 2>&1 | tee /tmp/typecheck-khufu-1-1-ratify-early-decisions.out
make lint 2>&1 | tee /tmp/lint-khufu-1-1-ratify-early-decisions.out
make test 2>&1 | tee /tmp/test-khufu-1-1-ratify-early-decisions.out
make markdownlint 2>&1 | tee /tmp/markdownlint-khufu-1-1-ratify-early-decisions.out
make nixie 2>&1 | tee /tmp/nixie-khufu-1-1-ratify-early-decisions.out
```

Run the gates sequentially; delegating the run to the `scrutineer` agent is
preferred. If `make markdownlint` regenerates `typos.toml` again, commit that
change on `regenerate-typos-config` (or a new base branch) rather than here.

Focused commands:

```plaintext
EP-M1 red:   uv run pytest tests/test_decision_record_rules.py
             -> ModuleNotFoundError: No module named 'tests.decision_records'
EP-M1 green: uv run pytest tests/test_decision_record_rules.py tests/test_substrate_fitness.py
             -> all pass
EP-M1 repo:  uv run pytest tests/test_decision_records_repository.py tests/test_decision_records_bdd.py
             -> 1 passed + 3 scenarios passed, 9 xfailed
EP-M2..M4:   same command -> 2 fewer xfailed per milestone (7, 5, 3)
EP-M5:       same command -> 0 xfailed
```

## Validation and acceptance

Acceptance is met when:

- `ls docs/adrs/` lists exactly the four roadmap file names.
- `make test` passes with no xfail left in the decision-record suite, and the
  scenario "The four foundational ADRs are accepted and linked" passes.
- Each negative control in `Verification plan` was observed failing for the
  intended reason in `EP-M1`, with transcripts in `Artefacts and notes`, and
  was reverted.
- `make check-fmt`, `make typecheck`, `make lint`, `make markdownlint`,
  `make nixie`, and `make audit` pass.
- The `EP-M6` sweep returns only the expected hits.
- Roadmap 1.1.1-1.1.4 are checked.

## Idempotence and recovery

All steps are file edits and test runs, so rerunning them is safe. `uv lock` is
deterministic for a fixed index state. Each milestone is one or more separate
commits, so `git revert <sha>` restores the previous plateau. Seeded faults are
made only in the working tree, observed, and reverted with
`git checkout -- <file>` before committing. `.hypothesis/` is already
git-ignored.

## Artefacts and notes

Planning-time observations (2026-11-20):

```plaintext
$ gh api repos/leynos/khufu/immutable-releases
{"enabled":false,"enforced_by_owner":false}
$ gh api repos/leynos/khufu/rulesets
[]
$ curl -s https://pypi.org/pypi/khufu/json   (info.summary)
Twitter Bootstrap elements via Python
$ man logind.conf   (UserStopDelaySec=, systemd 257, Rocky Linux 10)
... Defaults to 10s.
```

Implementation evidence (red, green, and negative controls) is appended here
during execution.

## Interfaces and dependencies

- New dev dependencies: `pytest-bdd` 9.0.x and `hypothesis` 6.170.x, exact
  pins, `dev` group only. Both declare CPython 3.14 support. `pytest-bdd` brings
  `mako`, `parse`, `parse-type`, and `gherkin-official`, which `make audit`
  checks.
- New test modules: `tests/decision_records.py` (pure rules; the single owner
  of ADR grammar, so future ADR checks extend it rather than re-parsing
  Markdown elsewhere); `tests/test_decision_record_rules.py`;
  `tests/test_decision_records_repository.py`;
  `tests/test_decision_records_bdd.py` with
  `tests/features/decision_records.feature`; `tests/test_substrate_fitness.py`.
  An optional `tests/conftest.py` holds only the shared `record_text(...)`
  builder if two modules need it. These are test infrastructure, not part of the
  `khufu` package; `docs/developers-guide.md` documents them.
- No `khufu/` interface, Makefile target, or CI workflow changes.
- Reuse: the repository has no Markdown or ADR helper
  (`rg -n "markdown|adr" tests scripts khufu` finds none), so nothing can be
  reused.

## Revision note

- 2026-11-20: initial draft from reconnaissance.
- 2026-11-20: expert review applied (release engineering, systemd and rootless
  containers, Python test architecture, documentation governance). Changes: D7
  reversed to recommend Nile Valley ownership and turned into a user decision
  gating `EP-M5` only; D3 extended to a hashed dependency lock, tag protection,
  an atomic publish sequence, candidate identity, and manifest fields, with the
  PyPI direct-URL constraint added; D5 rewritten around attempt-qualified unit
  names, `InvocationID`, a `Type=exec` start, `ExecStopPost=` result capture, a
  corrected `--scope` rejection, and cgroup containment; D6 gained
  environment-cluster loss, Podman's cgroup manager, bus reachability,
  `UserStopDelaySec=`, and refusal sequencing, and dropped SQLite as a separate
  decision; D4 now catches Cyclopts-derived options and aliased plug-in
  imports; D9 and D10 added; the test suite was halved and its xfail schedule
  fixed (per-ADR link tests, `@scenario` strict xfail, Vulture decorators,
  `pythonpath`); contradicting passages in `docs/context.md` and
  `docs/developers-guide.md` added; the release precondition moved from roadmap
  5.4.1 to 2.6.4. Remaining work and milestone order are unchanged except that
  `EP-M5` now waits for the user's D7 answer.

[^1]: <https://kind.sigs.k8s.io/docs/user/rootless/>
[^2]: <https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases>
