# 1.1. Ratify the decisions that would otherwise force rework

This ExecPlan (execution plan) is a living document. The sections `Constraints`,
`Tolerances (exception triggers)`, `Risks`, `Progress`,
`Surprises & discoveries`, `Decision log`, `Outcomes & retrospective`,
`Conformance basis`, and `Verification plan` must be kept up to date as work
proceeds.

Status: DRAFT (awaiting expert review and user approval)

Branch: `1-1-ratify-early-decisions`

Roadmap item: `1.1` (tasks `1.1.1` to `1.1.4`) in `docs/roadmap.md`.

## Purpose / big picture

Khufu is a planned command-line tool that will replace four separately
maintained local Kubernetes preview scripts in the df12 estate (Episodic,
Corbusier, Wildside, and Ghillie) with one shared implementation. No Khufu
runtime code exists yet; the repository holds a design
(`docs/khufu-design.md`), terms of reference (`docs/terms-of-reference.md`), a
vocabulary (`docs/context.md`), a roadmap (`docs/roadmap.md`), and a
placeholder Python package (`khufu/`).

The design leaves four foundational choices as "ADR candidates" in its §18. An
architectural decision record (ADR) is a short, stable document that records
one accepted decision, the context that forced it, the options weighed, and its
consequences. Until those four ADRs exist and are accepted, every later roadmap
step is built on choices that could still be reopened: where the code lives and
how consumers pin it, whether a second cluster provider may ever be plugged in,
who owns a running job, and where the typed data-service fixture specifications
shared with Nile Valley live.

After this work, a maintainer or agent can open `docs/adrs/` and find four
accepted ADRs:

- `docs/adrs/adr-0001-implementation-home.md` names `leynos/khufu` as the code
  home, `leynos/nile-valley` as the home of `validation-estate.toml` and the
  regression matrix, and the release channel consumers pin.
- `docs/adrs/adr-0002-fixed-kind-rootless-substrate.md` fixes Linux, rootless
  Podman, kind, kubectl, and Helm as the only supported stack.
- `docs/adrs/adr-0003-systemd-user-service-supervision.md` makes transient
  systemd user services the owners of job workers, makes waiting command-line
  processes observers, defers the foreground mode, and lists the
  session-survival limits that `khufu doctor` must report.
- `docs/adrs/adr-0004-shared-fixture-specifications.md` names the owning
  repository of the shared fixture specifications, how each side consumes them,
  and how their versions stay aligned with the platform lock.

The design, terms of reference, users' guide, developers' guide, contents
index, and roadmap then agree with those ADRs. In particular, the design and
users' guide stop describing a foreground execution mode as available today.

Observable success: `make test` runs a decision-record suite that fails if any
ADR in `docs/adrs/` breaks the style guide's naming, heading, or status rules,
if ADRs 0001-0004 are missing or not `Accepted`, if the design document or
contents index fails to link one of them, or if the package metadata or source
introduces a cluster-provider plug-in surface that ADR 0002 forbids. The suite
passes once the ADRs and cross-references land, and each rule is shown to
reject a deliberately broken input.

No runtime behaviour of Khufu changes, because none exists. The externally
visible change is documentary: the users' guide describes execution modes and
prerequisites as ratified.

## Constraints

- No production code under `khufu/` is added or changed. This roadmap item
  ratifies decisions; implementing supervision, `doctor`, the platform lock, or
  fixture rendering belongs to later roadmap steps (2.1.1, 2.2.4, 3.1.1, 5.1.1,
  5.1.2, and 7.1.1).
- ADR files use exactly the four paths named by roadmap 1.1. Their titles must
  slug to those filenames, as `docs/documentation-style-guide.md`
  ("Architectural decision records (ADRs)", "Naming convention") requires.
- ADRs follow the style guide's required order: `## Status`, `## Date`,
  `## Context and problem statement`, then the conditional sections used. The
  template's conditional headings are written in sentence case, as the style
  guide's heading rule requires.
- ADR acceptance authority: the user's approval of this plan ratifies the
  decision directions recorded in `Decision log` entries D3 to D7. ADRs are
  committed with `Accepted` status, the commit date, and a one-sentence
  summary. If review rejects a direction, revert the ADR commit rather than
  silently editing an accepted record.
- Requirement precedence follows `docs/khufu-design.md` front matter: the
  terms of reference settle problem and scope; accepted ADRs override the
  design. Any ADR that changes a terms-of-reference scope statement must update
  that statement in the same commit.
- Do not modify `.github/workflows/release.yml`, repository settings (such as
  GitHub immutable releases), or any repository other than `leynos/khufu`.
  Release-workflow and Nile Valley changes are recorded as consequences and
  follow-up roadmap work, not performed here.
- Do not create `docs/repository-layout.md`; its absence is a pre-existing gap
  outside this item. Record it in `Surprises & discoveries` only.
- Test helpers live under `tests/`; AGENTS.md forbids tests inside package
  modules. No code file exceeds 400 lines.
- Authorized dependency changes: add `pytest-bdd` and `hypothesis` to the
  `dev` dependency group in `pyproject.toml` and refresh `uv.lock` with
  `uv lock`. No runtime dependency is added. `syrupy` is not added (see D8).
- Comments and documentation use en-GB-oxendict spelling and follow
  `docs/documentation-style-guide.md`.
- Implementation begins only after the user approves this plan.

## Tolerances (exception triggers)

Comparison base: `4ab9802` (the `main` commit this branch was cut from).
Counting command, run from the repository root:

```bash
git diff --numstat 4ab9802 -- . ':(exclude)docs/execplans/' ':(exclude)uv.lock'
```

Classification is by whole file: Markdown under `docs/` (other than
`docs/execplans/`) is documentation; `pyproject.toml` is configuration;
`tests/**` (Python and `.feature` files) is code. `uv.lock` is a generated
lockfile and is excluded from line counts but counted as a file. This ExecPlan
is excluded from every count.

- Files: stop and escalate if more than 18 non-ExecPlan files change.
  Expected: 4 new ADRs, 6 edited docs (`khufu-design.md`,
  `terms-of-reference.md`, `users-guide.md`, `developers-guide.md`,
  `contents.md`, `roadmap.md`), about 5 test files, `pyproject.toml`, and
  `uv.lock`, totalling 17.
- Code: stop and escalate above 650 net added lines under `tests/`. Estimate:
  about 200 lines of pure rules, 60 of filesystem loading, 250 of tests, and 40
  of Gherkin, totalling 550.
- Configuration: stop and escalate above 20 net lines in `pyproject.toml`.
  Estimate: 3.
- Documentation: stop and escalate above 1,200 net lines. Estimate: four ADRs
  at roughly 170 to 230 lines each (about 800), plus about 180 lines of edits
  across the six existing documents.
- Interface: stop if any change to `khufu/`, the Makefile, or CI workflows
  appears necessary.
- Dependencies: stop if any dependency beyond `pytest-bdd` and `hypothesis`
  appears necessary, or if either cannot be installed on CPython 3.14 with the
  locked toolchain.
- Architecture: stop if an ADR's direction must depart from the recorded
  Decision log entries, or if a decision would contradict the terms of
  reference beyond the specific statements named in this plan.
- Iterations: stop if a gate still fails after 3 fix attempts for the same
  cause.
- Time: stop if any milestone exceeds 4 hours of active work.
- Ambiguity: stop and present options if Nile Valley maintainers or the user
  contradict the ownership direction in D7.

Budget evidence: this repository has no earlier ExecPlans (`docs/execplans/` is
created by this plan), so no historical budget revisions exist. The estimates
come from the survey in `Context and orientation`: the style guide's ADR
template has eleven sections, and the four decisions touch roughly 20 passages
across six documents.

## Risks

- Risk: the foreground-mode deferral contradicts the terms of reference
  (§4.2 says CI "needs a foreground mode"), the design (§11.3), and the users'
  guide ("Execution modes"). Severity: medium. Likelihood: high (the conflict
  exists today). Mitigation: ADR 0003 records the deferral to roadmap 5.1.2,
  and milestone `EP-M4` edits every conflicting passage in the same commit. CI
  needs before 5.1.2 are met by runners with a lingering user manager.
- Risk: the shared-fixture ownership direction (D7) moves specification
  ownership away from the wording in design §1.1 and §3.1, and Nile Valley's
  maintainers may disagree. Severity: high. Likelihood: medium. Mitigation: D7
  is surfaced for explicit user approval before implementation; Nile Valley
  keeps rendering, cloud-only extensions, and the estate manifest; the ADR
  states the Nile Valley-side consumption contract without editing Nile Valley.
- Risk: the release-channel decision (D3) depends on GitHub immutable
  releases, which are disabled on `leynos/khufu` today, and the current
  `release.yml` uploads assets after publication with `--clobber`, which an
  immutable release forbids. Severity: medium. Likelihood: high. Mitigation:
  ADR 0001 makes "immutable publication" a precondition of the first release
  tag and adds a follow-up task to the roadmap; no tag is pushed by this work.
- Risk: documentation-conformance tests become brittle prose checks.
  Severity: medium. Likelihood: medium. Mitigation: tests assert structure
  (filenames, headings, status grammar, links) and a small, finite set of named
  tokens tied to roadmap success criteria, never whole sentences.
- Risk: `pytest-bdd` 9 and `hypothesis` interact poorly with `pytest-xdist`
  (`-n auto`) or the 30-second `pytest-timeout`. Severity: low. Likelihood:
  low. Mitigation: `EP-M1` runs `make test` with the new suites before any ADR
  work; property tests use default example counts.
- Risk: the mutation-testing workflow copies only `scripts/`, `.github/`,
  `Makefile`, and `pyproject.toml` (`[tool.mutmut] also_copy`), so tests that
  read `docs/` would fail under mutmut. Severity: low. Likelihood: high.
  Mitigation: add `docs/` to `also_copy` in `EP-M1`.

## Progress

- [x] (2026-11-20 10:40Z) Branch renamed to `1-1-ratify-early-decisions`;
  Lody session titled.
- [x] (2026-11-20 11:30Z) Reconnaissance: repository docs, Makefile, tests,
  style guide, Nile Valley tree, PyPI name, GitHub release settings, kind and
  systemd documentation.
- [x] (2026-11-20 12:30Z) Initial draft written.
- [ ] Expert review applied.
- [ ] Plan approved by the user.
- [ ] `EP-M1` decision-record suite and substrate fitness rules, red.
- [ ] `EP-M2` ADR 0001 accepted and cross-referenced.
- [ ] `EP-M3` ADR 0002 accepted; fitness rules green.
- [ ] `EP-M4` ADR 0003 accepted; foreground and session text reconciled.
- [ ] `EP-M5` ADR 0004 accepted and cross-referenced.
- [ ] `EP-M6` documentation closure, roadmap 1.1 marked done, full gates.

## Surprises & discoveries

- Observation: the name `khufu` on the Python Package Index (PyPI) belongs to
  an unrelated project ("Twitter Bootstrap elements via Python", version
  1.3.3). Evidence: `curl -s https://pypi.org/pypi/khufu/json` during planning.
  Impact: consumers must never resolve Khufu by bare name from a package index;
  installing `khufu` without an explicit source would fetch the wrong package.
  This drives D3.
- Observation: GitHub immutable releases are disabled for `leynos/khufu`, no
  release exists, and `.github/workflows/release.yml` creates the release first
  and then uploads the wheel with `gh release upload --clobber`. Evidence:
  `gh api repos/leynos/khufu/immutable-releases` returned
  `{"enabled":false,...}`; `gh release list` was empty. Impact: an immutable
  release forbids adding assets after publication, so the workflow must change
  before the first tag (follow-up, not this item).
- Observation: Nile Valley renders the shared data services today with
  OpenTofu modules (`infra/modules/cnpg/manifests.tf` emits
  `postgresql.cnpg.io/v1` `Cluster`; `infra/modules/valkey/manifests.tf` emits
  `hyperspike.io/v1` `Valkey`) wrapped in Flux `HelmRelease` objects, driven by
  `scripts/render_platform_manifests.py`. It contains no
  `validation-estate.toml` and no mention of Khufu. Evidence:
  `gh api repos/leynos/nile-valley/git/trees/HEAD?recursive=1` and file reads
  at the default branch on 2026-11-20. Impact: shared specifications must be
  consumable from both Python and OpenTofu's HashiCorp Configuration Language
  (HCL), so they must be language-neutral data (JSON), which OpenTofu reads with
  `jsondecode(file(...))`.
- Observation: `docs/repository-layout.md`, which AGENTS.md and the style
  guide treat as canonical, does not exist, and `docs/contents.md` indexes no
  ADRs although the terms of reference say ADRs are indexed there. Impact:
  `EP-M6` adds an ADR group to `docs/contents.md`; the missing layout document
  is left for separate work.
- Observation: the "source design" referred to by roadmap 1.1.1 is "Khufu
  local validation design, revision 2, 15 October 2026, supplied by the estate
  owner" (`docs/terms-of-reference.md` references). It is not in any
  repository. Impact: ADR 0001 cites it by that description.
- Observation: `make all` and CI do not run `make nixie`. Impact: this plan
  runs `make nixie` explicitly because ADRs may carry Mermaid diagrams.

## Decision log

- D1. Decision: write the ADRs from the style guide's template, adding a
  `### Consequences` subsection under `## Decision outcome` because the style
  guide's document-type guidance requires ADRs to be "explicit about context,
  decision, consequences, and status", while its template omits a consequences
  heading. Omit `## Migration plan` where no phased change exists and
  `## Outstanding decisions` because every ADR is `Accepted`; matters delegated
  to later roadmap tasks appear in `## Known risks and limitations` with
  roadmap task numbers. Rationale: keeps the required order and satisfies
  roadmap 1.1.1's explicit request for consequences. Date/Author: 2026-11-20,
  planning agent.
- D2. Decision: the user's approval of this plan is the acceptance authority
  for the four ADRs (see `Constraints`). Rationale: the terms of reference name
  the estate owner as owner of the implementation-home question, and the user
  is that owner for this repository. Date/Author: 2026-11-20, planning agent.
- D3. Decision (ADR 0001, release channel): Khufu releases are GitHub Releases
  of `leynos/khufu`, created from immutable `vX.Y.Z` tags, carrying the pure
  Python wheel as a release asset. Consumers and the estate manifest pin an
  exact version together with the wheel's URL and SHA-256 digest; nothing
  resolves `khufu` by name from PyPI or any other index. GitHub immutable
  releases must be enabled, and the release workflow must publish assets
  atomically (draft, upload, then publish), before the first tag is pushed.
  Rationale: the repository already builds a pure wheel on tag push; the PyPI
  name is owned by an unrelated project, so name-based resolution is a
  dependency-confusion hazard; design §4.3 requires exact pins and forbids
  discovering moving versions; immutable releases guarantee a pinned URL and
  digest cannot change underneath a consumer. Rejected: PyPI under a new
  distribution name (adds an external publisher and namespace to govern for no
  estate benefit, and leaves the import-name collision); Git URL pins of source
  (`git+https`) (rebuilds on every install and pins a commit rather than a
  qualified artefact). Date/Author: 2026-11-20, planning agent.
- D4. Decision (ADR 0002): the substrate decision is enforced by fitness
  rules now, not only by review: the package metadata declares no
  `[project.entry-points]` groups, Khufu source never calls
  `importlib.metadata.entry_points`, and Khufu source never defines a
  `--provider` or `--engine` option literal.
  `KIND_EXPERIMENTAL_PROVIDER=podman` is an internal environment setting of the
  single kind adapter, not a provider option, and the ADR says so. Rationale:
  the fitness rules are cheap, precise, and fail at the moment someone
  introduces the forbidden extension surface; broader string scans for "docker"
  or "k3d" would flag legitimate remediation text and are rejected.
  Date/Author: 2026-11-20, planning agent.
- D5. Decision (ADR 0003, foreground mode): the foreground execution mode is
  deferred to roadmap task 5.1.2, not abandoned. Until 5.1.2 ships, a host
  without a usable systemd user manager cannot run mutating jobs: `doctor`
  reports the missing prerequisite, and job submission refuses with exit code
  `3` (host prerequisite failure). The contract that 5.1.2 must honour (record
  foreground execution, never claim detached durability, mark the job
  interrupted when the process is lost) is recorded now. Rationale: roadmap
  1.1.3 states the deferral and 5.1.2 schedules the mode; the earlier slices
  run on developer hosts with a user manager; deferring avoids building a
  second execution path before the detached path is proven. Date/Author:
  2026-11-20, planning agent.
- D6. Decision (ADR 0003, scope): ADR 0003 also ratifies the SQLite ledger
  under `$XDG_STATE_HOME/khufu` as the durable source of truth that supervision
  reconciles against, because design §18 bundles it into this candidate and the
  commit-before-start rule cannot be stated without it. The ledger schema
  remains roadmap task 2.2.1. Rationale: leaving the ledger unratified would
  leave §18 half-resolved. Date/Author: 2026-11-20, planning agent.
- D7. Decision (ADR 0004, recommended direction, requires explicit user
  approval): Khufu owns the source of the shared typed fixture specifications
  for the data services it provisions (initially CloudNativePG PostgreSQL
  clusters and Hyperspike Valkey), as JSON Schema documents plus versioned JSON
  specification documents under `khufu/platform/`, released in lockstep with
  the platform lock. Each Khufu release publishes the same files as a
  standalone release asset whose SHA-256 digest is recorded in
  `platform.lock.toml`. Nile Valley consumes that asset from the Khufu release
  pinned in `validation-estate.toml` and its OpenTofu modules decode it with
  `jsondecode`; Nile Valley keeps ownership of its rendering, its cloud-only
  extensions (backups, high availability, Transport Layer Security (TLS)), and
  the estate manifest. Alignment is by construction: one Khufu release carries
  one lock and one specification set, and Nile Valley CI verifies that the
  digest of the specifications it renders from equals the digest in the pinned
  release's lock. Rationale: the specifications are only valid against the
  custom resource definition (CRD) schemas and operator versions that the
  platform lock owns (design §7.1), so a second owner would create a second
  version axis, which is the drift Khufu exists to remove. Rejected
  alternatives: Nile Valley owns the specifications and Khufu vendors a pinned
  revision (two version axes that must be reconciled on every lock change); a
  third repository (a third release cadence and pin with no owner benefit).
  Consequence: design §1.1 and §3.1 wording that Nile Valley "keeps" the
  specifications changes; terms-of-reference ownership statements remain true
  because Nile Valley keeps rendering. Date/Author: 2026-11-20, planning agent;
  pending expert review and user approval.
- D8. Decision (verification shape): validate this documentary change with a
  decision-record suite under `tests/`: pure rules over in-memory ADR text in
  `tests/decision_records.py` (the domain), a thin filesystem loader (the
  adapter), unit tests and Hypothesis properties for the rules, a `pytest-bdd`
  feature for roadmap acceptance, and fitness rules for ADR 0002. Do not add
  `syrupy`: no multivariant output format exists. Do not add end-to-end tests:
  no command-line behaviour, persistence, or network boundary changes.
  Rationale: the roadmap success criteria are structural and checkable; the
  user requires pytest, pytest-bdd, and Hypothesis "where applicable", and
  later roadmap steps (1.2, 1.4, 2.2) need both libraries anyway. Date/Author:
  2026-11-20, planning agent.

## Outcomes & retrospective

Not started. Complete at each milestone and at completion.

## Context and orientation

Inspected base revision: `4ab9802` ("Remove the tool list from AGENTS.md
(#34)"). Line numbers below refer to that revision; relocate them with
`grep -n` on the quoted heading.

The repository is a Python 3.14 project generated from a template. Its package,
`khufu/`, contains only `khufu/__init__.py` and `khufu/pure.py` (placeholders).
Tests live in `tests/` and use pytest with `pytest-xdist` and `pytest-timeout`
(30 seconds per test, `pyproject.toml` `[tool.pytest.ini_options]`). Existing
tests are `tests/test_stub.py`, `tests/test_action_workflow.py` (which imports
`scripts.action_workflow`), and `tests/test_codescene_publisher_wiring.py`,
which is the closest pattern to a repository-file conformance test: it sets
`ROOT = Path(__file__).resolve().parents[1]` and asserts over parsed workflow
YAML and the Makefile, with an explanatory message on every assertion. There is
no `conftest.py`, no fixtures directory, and no Markdown parsing yet.
`pytest-bdd`, `hypothesis`, and `syrupy` are not dependencies today.

Documents that matter, with the passages this plan changes:

- `docs/khufu-design.md` (Draft v0.1, last substantive revision 2026-10-17):
  front matter (precedence: accepted ADRs override the design); §1.1
  "Implementation home" (lines 50-59, provisional pending ADR 0001; says Nile
  Valley keeps the shared fixture specifications); §2 "Constraints and
  non-goals" (lines 61-92, fixed substrate); §3.1 table row for Nile Valley
  (line 109); §4.3 "Estate pinning" (lines 199-213); §5.1-5.2 (layering and the
  single cluster adapter, lines 215-274); §7.1 "Lock and qualification" (lines
  421-446); §8.1-8.2 (doctor and kind, lines 527-548); §11.3 "Supervision"
  (lines 786-800, describes a foreground CI mode as present); §12.1 GitOps
  suite (lines 889-894); §17 tables 7 and 8 (lines 1118-1140); §18 "Open
  questions and ADR candidates" (lines 1142-1158).
- `docs/terms-of-reference.md` (version 0.1): §3 bedrock (lines 58-62, Nile
  Valley owns rendered platform fixtures); §4.2 (lines 117-121, CI needs a
  foreground mode); §9 open-questions table (lines 304-312: the
  implementation-home row targets `docs/adrs/adr-0001-implementation-home.md`;
  a foreground-mode row is a pending design decision).
- `docs/users-guide.md`: prerequisites (lines 36-45, "Hosts without one use
  the foreground execution mode") and "Execution modes" (lines 314-323).
- `docs/roadmap.md`: 1.1 (lines 26-66), 2.1.1 (doctor checks, lines 244-252,
  which omit session guarantees), 2.2.4 (supervision, requires 1.1.3), 5.1.1
  (estate manifest), 5.1.2 (foreground mode, requires 1.1.3), 5.4.1 (first
  consolidated release).
- `docs/contents.md`: three groups (product definition, project guides,
  engineering practice) and no ADR entries.
- `docs/developers-guide.md`: lines 95-97 require recording substantive
  decisions in an ADR; nothing describes ADR mechanics or doc-conformance tests.
- `docs/documentation-style-guide.md`: "Architectural decision records
  (ADRs)" (lines 515-662) defines naming, required sections, statuses
  (`Proposed`, `Accepted`, `Superseded`, `Deprecated`), the amendment banner
  (`Amended by ADR-nnnn (YYYY-MM-DD)`), conditional sections, and the template;
  lines 303-320 define the ADR's job.
- `docs/context.md`: vocabulary (estate manifest, Nile Valley, platform lock,
  regression matrix, toolchain pin). Use these terms exactly.

Gates (Makefile targets): `make fmt` (Ruff format and `mdtablefix` 0.6.1
rewrap), `make check-fmt`, `make lint` (Ruff, interrogate at 100% docstring
coverage, Pylint, DF12 lints, Ambrleaks on `tests/`, Skylos, Vulture on
`tests/`, duplication, action lint), `make typecheck` (`ty`), `make test`
(`uv run pytest -v -n auto`), `make markdownlint` (markdownlint-cli2 over
`**/*.md`, then the `typos` spelling gate), and `make nixie` (Mermaid
validation). Python test modules need docstrings on every function
(interrogate) and must satisfy Vulture, so helpers must be used.

External facts gathered during planning (each becomes an axiom below):

- systemd: `systemd-run --user` starts a transient service under the user's
  service manager; a transient service keeps running when the invoking process
  exits, unlike a `--scope` unit, which is tied to its caller.
  (`systemd-run(1)`, freedesktop.org.)
- logind: the per-user manager `user@.service` is stopped
  `UserStopDelaySec=` (default 10 s) after the user's last session ends, unless
  lingering is enabled; `loginctl enable-linger` spawns the user manager at
  boot and keeps it after logout. `KillUserProcesses=` (default "no" in the
  host's packaged documentation) governs session scopes, not services under the
  user manager. (`logind.conf(5)` and `loginctl(1)` on the Rocky Linux 10 host,
  systemd 257.)
- kind rootless: requires cgroup v2 and delegation of the `cpu` controller to
  user services (default from systemd 252); Podman 3.0 or later; may need
  `systemd-run --scope --user -p Delegate=yes`; documents PID, inotify,
  iptables-module, privileged-port, and log-driver hazards; rootless
  restrictions include no block-storage or NFS mounts.
  (<https://kind.sigs.k8s.io/docs/user/rootless/>.)
- GitHub immutable releases (generally available 2025-10-28): assets and the
  tag of a published immutable release cannot be added to, modified, moved, or
  deleted; a deleted release's tag name cannot be reused.
  (<https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases>.)

Relevant skills for the implementer: `execplans` (this format),
`hexagonal-architecture` (pure rules versus filesystem adapter),
`python-router`, `python-testing`, and `hypothesis` (test design),
`en-gb-oxendict-style` (prose), and `commit-message`.

## Conformance basis

Upstream artefacts, all at revision `4ab9802`:

- Terms of reference: `docs/terms-of-reference.md`, version 0.1; §3, §4.2,
  §4.3, §9 (open questions register, table 4).
- Technical design: `docs/khufu-design.md`, Draft v0.1 (2026-10-17); §1.1,
  §2, §3.1, §4.3, §5.1-5.2, §7.1, §8.1-8.2, §11.1, §11.3, §12.1, §17, §18.
- Roadmap: `docs/roadmap.md`, tasks 1.1.1-1.1.4 and dependants 1.2.1,
  1.2.2, 1.3.1, 2.1.1, 2.2.4, 5.1.1, 5.1.2, 5.4.1.
- Governing standard: `docs/documentation-style-guide.md`, ADR section.
- ADRs: none exist; this plan creates the first four.

Requirements derived for this plan:

- `REQ-HOME` (roadmap 1.1.1; ToR §9 row 1; design §1.1, §4.3, §18): one
  accepted ADR names the code home (`leynos/khufu`), the estate-manifest home
  (`validation-estate.toml` in `leynos/nile-valley`), the regression-matrix
  home (Nile Valley), and the release channel consumers pin; it records the
  divergence from the source design and the release and pinning consequences.
- `REQ-SUBSTRATE` (roadmap 1.1.2; design §2, §5.1, §17 table 7): one accepted
  ADR fixes the stack and forbids `--provider`, `--engine`, k3d, Docker,
  rootful fallback, and alternate-cluster plug-ins, and states that test
  doubles are not production extension points.
- `REQ-SUPERVISION` (roadmap 1.1.3; design §11.1, §11.3, §17 table 8): one
  accepted ADR makes transient systemd user services the worker owners and
  waiting CLIs observers, defers the foreground mode, and lists the
  session-survival limits `doctor` must report.
- `REQ-FIXTURES` (roadmap 1.1.4; design §3.1, §7.1, §12.1, §18): one accepted
  ADR names the owning repository, each side's consumption mechanism, and the
  version-alignment rule with the platform lock, such that both renderers
  consume one specification source.
- `REQ-FORMAT` (style guide): every ADR satisfies naming, heading-order, and
  status rules.
- `REQ-TRACE` (AGENTS.md documentation maintenance; ToR "indexed in
  `docs/contents.md`"): the design §18, the relevant design sections, the
  terms-of-reference register, and `docs/contents.md` link the accepted ADRs,
  and no live document contradicts them.

Gaps observed at the base revision:

- `GAP-NO-ADRS`: `docs/adrs/` does not exist.
- `GAP-FOREGROUND`: design §11.3, users' guide, and ToR §4.2 and §9 present
  the foreground mode as current, contradicting roadmap 1.1.3 and 5.1.2.
- `GAP-SESSION-LIMITS`: no document enumerates session-survival limits;
  roadmap 2.1.1's doctor checklist omits them.
- `GAP-RELEASE-CHANNEL`: no release channel is defined; the PyPI name is taken;
  immutable releases are off.
- `GAP-FIXTURE-ALIGNMENT`: no document states how fixture specification
  versions align with the platform lock; design §1.1 presupposes an owner that
  §18 leaves open.
- `GAP-ADR-INDEX`: `docs/contents.md` indexes no ADRs.

Trace chains:

```plaintext
ToR-§9-row1 -> REQ-HOME -> design §1.1/§4.3/§18 -> EP-M2 -> tests/test_decision_records_repository.py::test_foundational_adr_is_accepted[0001]
roadmap-1.1.2 -> REQ-SUBSTRATE -> design §2/§17 -> EP-M1, EP-M3 -> tests/test_substrate_fitness.py
roadmap-1.1.3 -> REQ-SUPERVISION, GAP-FOREGROUND, GAP-SESSION-LIMITS -> design §11.3 -> EP-M4 -> tests/features/decision_records.feature
roadmap-1.1.4 -> REQ-FIXTURES, GAP-FIXTURE-ALIGNMENT -> design §3.1/§7.1 -> EP-M5 -> test_foundational_adr_is_accepted[0004]
style guide -> REQ-FORMAT -> EP-M1 -> tests/test_decision_record_rules.py
AGENTS.md -> REQ-TRACE, GAP-ADR-INDEX -> EP-M2..EP-M6 -> test_design_and_contents_link_accepted_adrs
```

## Verification plan

### Abstract model

A decision-record set is a finite map from file names in `docs/adrs/` to
Markdown texts. A file name is valid when it matches `adr-NNNN-SLUG.md`, where
`NNNN` is four decimal digits and `SLUG` is one or more lowercase ASCII
alphanumeric words joined by single hyphens. A text is a valid record when its
first heading is `# Architectural decision record (ADR) NNNN: TITLE`, its
level-two headings begin with `Status`, `Date`, `Context and problem statement`
in that order, the `Status` body begins with one of the four permitted status
words, an `Accepted` status carries an ISO date (`YYYY-MM-DD`) and a summary
sentence, a `Superseded` status names an existing ADR, and the `Date` body is
an ISO date. The record is consistent with its file name when the heading's
number equals `NNNN` and the kebab-case rendering of `TITLE` equals `SLUG`.

Malformed input (unreadable file, missing heading) yields a named violation for
that file rather than an exception, so the suite reports every problem at once.

The substrate fitness rules operate on two inputs: the parsed `pyproject.toml`
mapping and the set of `(path, text)` pairs for Python files under `khufu/`. A
violation is any `project.entry-points` table, any call spelled `entry_points(`
or `importlib.metadata.entry_points`, or any string literal equal to
`--provider` or `--engine` (detected with the `ast` module, not regular
expressions, so comments and documentation do not trip it).

### Invariants and lemmas

- `INV-FILENAME` (`REQ-FORMAT`): a file name is accepted exactly when it
  matches the grammar, and parsing a formatted `(number, slug)` pair returns
  that pair.
- `INV-SLUG` (`REQ-FORMAT`): for every title, `slugify(title)` is a valid
  slug or empty, and is idempotent (`slugify(slugify(t)) == slugify(t)`).
- `INV-UNIQUE` (`REQ-FORMAT`): the registry reports a duplicate-number
  violation exactly when two file names share a number.
- `INV-STATUS` (`REQ-FORMAT`): a record's status is classified as exactly one
  of the four permitted values or reported as invalid; `Accepted` without a
  date or summary is invalid.
- `INV-FOUNDATION` (`REQ-HOME`, `REQ-SUBSTRATE`, `REQ-SUPERVISION`,
  `REQ-FIXTURES`): the repository registry contains ADRs 0001-0004 at the
  roadmap paths, each `Accepted`, each valid, and each naming the tokens its
  roadmap success criterion requires (table in `EP-M1`).
- `INV-TRACE` (`REQ-TRACE`): every `Accepted` ADR is linked by relative path
  from `docs/khufu-design.md` §18 and from `docs/contents.md`.
- `INV-NO-PLUGIN` (`REQ-SUBSTRATE`): the fitness rules report no violation for
  the repository, and report a violation for each seeded forbidden surface.
- `L-ORDER`: the heading-order check depends on extracting level-two headings
  in document order while ignoring headings inside fenced code blocks. This
  lemma connects `INV-STATUS` to real files whose code fences contain `#` lines.

### Axioms (trusted, not verified here)

- `AXIOM-SYSTEMD-TRANSIENT`: a transient service started by
  `systemd-run --user` is owned by the user manager and survives exit of the
  invoking process (`systemd-run(1)`). Relied on by ADR 0003.
- `AXIOM-LOGIND-LINGER`: without lingering, the user manager stops shortly
  after the last session ends (`UserStopDelaySec=`, default 10 s), stopping its
  services; with lingering it starts at boot and persists across logout
  (`logind.conf(5)`, `loginctl(1)`). No transient unit survives a reboot.
  Relied on by ADR 0003's session-survival limits.
- `AXIOM-KIND-ROOTLESS`: kind's documented rootless requirements and hazards
  (cgroup v2, `cpu` delegation, Podman 3.0 or later, PID and inotify limits,
  iptables modules, privileged ports, log driver). Relied on by ADR 0002.
- `AXIOM-GH-IMMUTABLE`: GitHub immutable releases lock tag and assets after
  publication. Relied on by ADR 0001.
- `AXIOM-OPENTOFU-JSON`: OpenTofu's `jsondecode` and `file` functions read
  JSON documents at plan time. Relied on by ADR 0004's Nile Valley consumption
  mechanism.
- `AXIOM-PYTEST-BDD`: `pytest-bdd` 9 binds Gherkin steps to Python functions
  and runs under `pytest-xdist`.

These axioms are not tested here. The ADRs cite their sources. Where later
roadmap tasks build on them (2.1.1 for doctor, 2.2.4 for supervision), those
tasks verify the repository-owned logic against the real interfaces.

### Methods per obligation

- Obligation: `INV-FILENAME`. Method: Hypothesis property plus named
  examples. Rationale: the grammar spans an open domain of names. Domain:
  integers 0-9999 with
  `st.from_regex(r"[a-z0-9]+(-[a-z0-9]+)*", fullmatch=True)` slugs; arbitrary
  text for rejection. Artefact:
  `tests/test_decision_record_rules.py::test_filename_round_trip` and
  `::test_filename_rejects_non_matching_names`. Evidence:
  `uv run pytest tests/test_decision_record_rules.py -k filename` fails with
  `ImportError` before the rules exist and passes after. Non-vacuity: named
  rejection examples `adr-1-x.md`, `adr-0001-X.md`, `adr-0001-a--b.md`,
  `ADR-0001-a.md`, `adr-0001-.md`; the rejection property uses an oracle
  regular expression written independently in the test and records
  `hypothesis.event` labels for accepted and rejected classes; a seeded fault
  (allowing three-digit numbers) must fail the `adr-001-x.md` example.
- Obligation: `INV-SLUG`. Method: Hypothesis property over `st.text()`.
  Artefact: `::test_slugify_is_idempotent_and_valid`. Non-vacuity: named
  examples map `Fixed kind rootless substrate` to
  `fixed-kind-rootless-substrate` and `Systemd user service supervision` to
  `systemd-user-service-supervision`; a seeded fault that keeps uppercase
  letters must fail.
- Obligation: `INV-UNIQUE`. Method: Hypothesis property over lists of
  `(number, slug)` pairs with an oracle computed by `collections.Counter`.
  Artefact: `::test_duplicate_numbers_are_reported_exactly`. Non-vacuity:
  `hypothesis.event` records "has duplicates" and "no duplicates"; both must
  appear in the statistics output (`--hypothesis-show-statistics`).
- Obligation: `INV-STATUS` and `L-ORDER`. Method: parameterized pytest over a
  finite truth table of status bodies and heading layouts (four valid statuses,
  unknown word, missing date, missing summary, superseded without a target,
  superseded with a target, headings out of order, a `## Status` line inside a
  fenced block). Artefact: `::test_status_classification` and
  `::test_required_heading_order`. Non-vacuity: each row asserts the specific
  violation code, so a rule that accepts everything fails every negative row.
- Obligation: `INV-FOUNDATION` and `INV-TRACE`. Method: repository tests over
  the real `docs/` tree plus a BDD feature. Artefact:
  `tests/test_decision_records_repository.py` and
  `tests/features/decision_records.feature` with
  `tests/test_decision_records_bdd.py`. Evidence: in `EP-M1` each per-ADR case
  carries `@pytest.mark.xfail(strict=True, reason="ADR nnnn lands in EP-Mk")`;
  the marker is removed in the milestone that lands the ADR, so a strict xfail
  that unexpectedly passes or a test that still fails stops the milestone.
  Non-vacuity: the BDD feature includes negative scenarios over in-memory
  records, and the repository loader is exercised against a temporary directory
  containing one broken record.
- Obligation: `INV-NO-PLUGIN`. Method: example-based fitness tests with seeded
  negative controls. Artefact: `tests/test_substrate_fitness.py`. Evidence: the
  rules report zero violations for the repository and exactly one for each
  synthetic input: a `pyproject` mapping with
  `{"project": {"entry-points": {"khufu.providers": {...}}}}`, a source text
  calling `importlib.metadata.entry_points(group="khufu.providers")`, and a
  source text defining `Parameter(name="--provider")`. Non-vacuity: the
  repository scan must visit at least the two existing files in `khufu/`
  (asserted), so an empty glob cannot pass silently.

### Formal verification decision

No model checking or formal proof is warranted. The obligations are syntactic
checks over finite documents and a filename grammar; Hypothesis covers the
open-ended grammar and parameterized tables cover the finite status and heading
partitions. The substantive claims inside the ADRs (systemd lifetimes, kind
requirements, immutable releases) are external axioms that later roadmap tasks
test against real interfaces.

### Suggested BDD features

Adopted (not merely proposed), because the user requires `pytest-bdd` where
applicable. Path: `tests/features/decision_records.feature`, bound by
`tests/test_decision_records_bdd.py` with
`scenarios("features/decision_records.feature")`.

```gherkin
Feature: Foundational decision records
  Khufu's foundational decisions are recorded as accepted ADRs that later
  roadmap steps can rely on.

  Scenario: The four foundational ADRs are accepted and linked
    Given the decision records in the repository
    When the decision-record registry is validated
    Then ADRs 0001, 0002, 0003, and 0004 are accepted
    And every accepted ADR is linked from the design document and the contents index
    And the registry reports no violations

  Scenario: A record with an unknown status is rejected
    Given a decision record "adr-0099-example.md" whose status is "Ratified"
    When the decision-record registry is validated
    Then the registry reports the violation "unknown-status" for "adr-0099-example.md"

  Scenario: An accepted record without a decision summary is rejected
    Given a decision record "adr-0099-example.md" whose status is "Accepted"
    And the status has no summary sentence
    When the decision-record registry is validated
    Then the registry reports the violation "accepted-without-summary" for "adr-0099-example.md"

  Scenario: A record whose title does not match its filename is rejected
    Given a decision record "adr-0099-example.md" titled "Something else"
    When the decision-record registry is validated
    Then the registry reports the violation "title-slug-mismatch" for "adr-0099-example.md"

  Scenario: A provider plug-in surface is refused
    Given package metadata declaring the entry-point group "khufu.providers"
    When the substrate fitness rules are applied
    Then the rules report the violation "entry-point-group"
```

Scenario 1 traces to `REQ-HOME`, `REQ-SUBSTRATE`, `REQ-SUPERVISION`,
`REQ-FIXTURES`, and `REQ-TRACE` and is strict-xfail until `EP-M5`; the others
trace to `REQ-FORMAT` and `REQ-SUBSTRATE` and pass from `EP-M1` (green half).

## Plan of work

Each milestone is one or more atomic commits, each gated. Run the gate sequence
in `Concrete steps` at the end of every milestone.

### `EP-M1` decision-record suite and substrate fitness rules

Assigned: `REQ-FORMAT`, `INV-*` rules, `INV-NO-PLUGIN`, D4, D8.

1. Configuration: in `pyproject.toml`, add `"pytest-bdd==9.0.1"` and
   `"hypothesis==6.170.17"` (or the newest patch releases available at
   implementation time, pinned exactly to match the `ruff`, `cyclopts`, and
   `ty` pin style) to `[dependency-groups] dev`, and add `"docs/"` to
   `[tool.mutmut] also_copy`. Run `uv lock`. Commit separately ("Add pytest-bdd
   and Hypothesis for decision-record tests").
2. Red: write `tests/test_decision_record_rules.py` (unit and property
   tests from `Verification plan`) importing from `tests.decision_records`
   (follow whichever import style `tests/test_action_workflow.py` uses
   successfully for `scripts.action_workflow`; if `ty` or pytest cannot resolve
   it, place the module where the existing pattern resolves and record the
   choice in `Decision log`). Run
   `uv run pytest tests/test_decision_record_rules.py`; expect collection to
   fail with `ModuleNotFoundError` for `tests.decision_records` (or the
   resolved equivalent).
3. Green: write the pure rules module `tests/decision_records.py`. It holds
   no I/O. Proposed public surface (all frozen dataclasses or enums):

   ```python
   class Status(enum.StrEnum):
       PROPOSED = "Proposed"
       ACCEPTED = "Accepted"
       SUPERSEDED = "Superseded"
       DEPRECATED = "Deprecated"

   @dataclass(frozen=True, slots=True)
   class Violation:
       file_name: str
       code: str      # stable kebab-case code, for example "unknown-status"
       detail: str

   @dataclass(frozen=True, slots=True)
   class DecisionRecord:
       file_name: str
       number: int
       slug: str
       title: str
       status: Status
       headings: tuple[str, ...]

   def parse_file_name(file_name: str) -> tuple[int, str] | None: ...
   def slugify(title: str) -> str: ...
   def level_two_headings(text: str) -> tuple[str, ...]: ...
   def parse_record(file_name: str, text: str) -> DecisionRecord | Violation: ...
   def validate_registry(files: Mapping[str, str]) -> tuple[Violation, ...]: ...
   ```

   Then write `tests/decision_record_loader.py`: one function,
   `load_registry(directory: Path) -> dict[str, str]`, that reads every `*.md`
   file in `directory` (empty mapping when the directory is absent). This is
   the only module that touches the filesystem.
4. Red for the repository: write `tests/test_decision_records_repository.py`
   with `test_registry_is_valid`, `test_foundational_adr_is_accepted`
   (parameterized over 0001-0004 with each ADR's required tokens; see the table
   below), and `test_design_and_contents_link_accepted_adrs`. Mark each
   0001-0004 case and the link test with
   `@pytest.mark.xfail(strict=True, reason="ADR nnnn lands in EP-Mk")`.
   `test_registry_is_valid` passes on an empty directory.
5. Write `tests/features/decision_records.feature` and
   `tests/test_decision_records_bdd.py`. Scenario 1 is strict-xfail until
   `EP-M5`.
6. Write `tests/test_substrate_fitness.py` with the pure rules
   (`entry_point_violations(pyproject: Mapping[str, object])` and
   `source_violations(path: str, text: str)` using `ast`) and the repository
   and seeded tests. Keep the rules in the test module unless the file nears
   400 lines; then move them to `tests/substrate_fitness.py`.
7. Run the full gate sequence. Commit ("Add decision-record conformance
   suite").

Required-token table for `test_foundational_adr_is_accepted` (tokens are
matched case-sensitively within the ADR's `## Decision outcome` section only,
so context prose cannot satisfy them):

```plaintext
0001: "leynos/khufu", "leynos/nile-valley", "validation-estate.toml", "regression matrix", "GitHub Releases", "SHA-256"
0002: "rootless Podman", "kind", "kubectl", "Helm", "--provider", "--engine", "k3d", "Docker", "rootful", "test doubles"
0003: "systemd-run --user", "observer", "5.1.2", "linger", "doctor"
0004: "leynos/khufu", "Nile Valley", "platform lock", "jsondecode", "SHA-256"
```

### `EP-M2` ADR 0001: implementation home

Assigned: `REQ-HOME`, `GAP-RELEASE-CHANNEL`, `GAP-ADR-INDEX` (first entry),
D1-D3.

Create `docs/adrs/adr-0001-implementation-home.md` titled
`# Architectural decision record (ADR) 0001: Implementation home`. Content:

- Status: `Accepted` with the acceptance date and the summary "Khufu's code,
  package, and releases live in `leynos/khufu`; Nile Valley hosts the estate
  manifest and regression matrix."
- Context: the source design ("Khufu local validation design, revision 2,
  15 October 2026, supplied by the estate owner") placed Khufu in
  `leynos/nile-valley`; this repository exists; ToR §9 open question; design
  §4.3 pinning rules; Nile Valley is an OpenTofu, Flux, and Python platform
  repository whose release cadence is tied to cloud infrastructure.
- Decision drivers: one installable package with its own release; anti-drift
  checks in one place; exact pins without network discovery; no
  dependency-confusion exposure.
- Options: A, Khufu in `leynos/khufu` (chosen); B, Khufu inside
  `leynos/nile-valley` (source design); C, Khufu as a Python package in Nile
  Valley's monorepo published separately. Compare on release coupling, CI
  scope, review ownership, and pin clarity in a captioned table.
- Decision outcome: code home, estate-manifest home, regression-matrix home,
  release channel per D3. `### Consequences`: consumers pin
  `version + URL + SHA-256`; `validation-estate.toml` records the approved
  release the same way; immutable releases must be enabled and `release.yml`
  must stop using post-publication `--clobber` uploads before the first tag;
  candidates are tested by explicit local selection (design §4.3); Nile Valley
  CI fetches the pinned asset, never "latest".
- Known risks and limitations: GitHub availability for first install (cache
  thereafter); a deleted immutable release cannot reuse its tag; the
  regression-matrix runner question (design §18 open item) stays open and
  belongs to roadmap 5.1.3.

Also in this milestone: update design §1.1 (no longer provisional; link the
ADR; keep only statements consistent with D7 for the fixture specifications,
deferring their wording to `EP-M5`), design §4.3 (link the ADR and name the pin
shape), design §18 first bullet (link, "Accepted"), the ToR §9
implementation-home row (resolution: link to the accepted ADR), add a "Decision
records" group to `docs/contents.md` with this ADR, and add a sub-bullet to
roadmap 5.4.1 requiring immutable publication per ADR 0001. Remove the
strict-xfail marker from the 0001 case. Gate and commit ("Accept ADR 0001:
implementation home").

### `EP-M3` ADR 0002: fixed kind rootless substrate

Assigned: `REQ-SUBSTRATE`, `INV-NO-PLUGIN`, D4.

Create `docs/adrs/adr-0002-fixed-kind-rootless-substrate.md` titled
`...0002: Fixed kind rootless substrate`. Content: status summary; context
(four drifting implementations across k3d, kind, Docker, and Podman; design
§1-2; Episodic's demonstrated path); drivers (drift removal, qualification
surface, rootless safety); options (fixed stack, chosen; provider matrix behind
a plug-in interface; kind fixed but engine selectable; rootful fallback when
rootless fails) in a captioned table; decision outcome naming every forbidden
surface (`--provider`, `--engine`, k3d, Docker, rootful fallback,
alternate-cluster plug-in interface) and stating that
`KIND_EXPERIMENTAL_PROVIDER=podman` is internal configuration of the single
kind adapter; test doubles substitute ports in tests and are never selectable
by users, configuration, environment variables, or entry points;
`### Consequences` naming the fitness tests in
`tests/test_substrate_fitness.py`, `doctor` reporting rather than repairing
host prerequisites (cite kind's rootless requirements), and the extension rule
(a new substrate requires a superseding ADR, not a plug-in). Known risks: host
variance; GitHub-hosted runners may lack delegation (regression-matrix runner
question).

Update design §2 (link), §5.1/§5.2 (link the "module, not a registry"
statement), §17 table 7 caption context (link), §18 second bullet. Remove the
0002 strict-xfail marker. Gate and commit.

### `EP-M4` ADR 0003: systemd user-service supervision

Assigned: `REQ-SUPERVISION`, `GAP-FOREGROUND`, `GAP-SESSION-LIMITS`, D5, D6.

Create `docs/adrs/adr-0003-systemd-user-service-supervision.md` titled
`...0003: Systemd user service supervision`. Content: status summary; context
(long multi-minute cluster work must survive the invoking terminal and agent
process; design §11); drivers (detached durability, crash recovery without a
second worker, observer independence, honest guarantees); options (transient
user services, chosen; a Khufu-owned daemon; `nohup` or double-fork background
processes; foreground-only execution; `systemd-run --scope`, rejected because a
scope dies with its caller) in a captioned table. Decision outcome:

- Each long operation runs in a named transient user service started with
  `systemd-run --user` and a deterministic unit name derived from the job
  identifier; the SQLite ledger under `$XDG_STATE_HOME/khufu` is the source of
  truth; the job is committed before the unit starts; the unit identity is
  recorded and verified; recovery reconciles by unit name and never spawns a
  second worker.
- A waiting CLI (`--wait`, a TTY, or an agent) is an observer: killing it
  never stops the worker; cancellation is the explicit `jobs cancel` operation.
- The foreground mode is deferred to roadmap 5.1.2 with the contract in D5;
  until then submission refuses with exit code `3` when no user manager is
  usable.
- Session-survival limits that `doctor` must report as findings (never
  repair): whether a user manager is reachable for the invoking user (no user
  bus means detached jobs are unavailable); whether lingering is enabled
  (without it, `user@.service` stops about `UserStopDelaySec=` after the last
  session ends, interrupting jobs at logout); that no transient unit survives
  reboot even with lingering, so recovery marks those jobs interrupted; and that
  `KillUserProcesses=` does not govern user-manager services (stated so that
  remediation text does not misdirect users).

`### Consequences`: roadmap 2.1.1 gains the session-guarantee findings; roadmap
2.2.4 implements this ADR; the regression matrix (5.1.3) needs runners with a
lingering user manager until 5.1.2 ships. Known risks: hosts without user
systemd (containers, some CI) cannot run jobs until 5.1.2; reboot always
interrupts.

Edit in the same commit: design §11.3 (replace the present-tense foreground
paragraph with the deferral and the session-limit list; link the ADR), design
§17 table 8 systemd row (mention lingering), design §18 third bullet; users'
guide prerequisites (lines 36-45) and "Execution modes" (lines 314-323) to say
detached execution needs a usable user manager, lingering is needed for jobs to
outlive logout, reboot interrupts jobs, and foreground mode is planned but not
yet available; ToR §4.2 (CI needs a foreground mode "from roadmap 5.1.2; until
then, a runner with a lingering user manager") and the ToR §9 foreground row
(resolution path: ADR 0003 and roadmap 5.1.2); roadmap 2.1.1 checklist (add
"session guarantees: user manager reachability and lingering"). Remove the 0003
strict-xfail marker. Gate and commit.

### `EP-M5` ADR 0004: shared fixture specifications

Assigned: `REQ-FIXTURES`, `GAP-FIXTURE-ALIGNMENT`, D7.

Create `docs/adrs/adr-0004-shared-fixture-specifications.md` titled
`...0004: Shared fixture specifications`. Content: status summary; context
(Nile Valley's OpenTofu modules render CNPG `Cluster` and Hyperspike `Valkey`
resources for Flux; Khufu's renderers render the same resources for direct Helm
execution; the Valkey resource-identity hazard in design §3.2 shows what
divergence costs; design §7.1 makes the lock own CRD schemas and operator
versions); drivers (one specification source, one version axis, language
neutrality for Python and HCL, no network discovery); options (Khufu owns,
chosen per D7; Nile Valley owns and Khufu vendors; a third repository) in a
captioned table comparing version axes, coupling direction, and the consumption
mechanism on each side. Decision outcome per D7, including: location
(`khufu/platform/fixtures/` holding `*.schema.json` and versioned specification
documents; exact layout settled by roadmap 3.1.1), Khufu-side consumption
(renderers load the packaged files; the lock records their digest), Nile
Valley-side consumption (download the release asset named in
`validation-estate.toml`, verify SHA-256, decode with `jsondecode`), and the
alignment rule. `### Consequences`: design §1.1 and §3.1 wording changes; the
deferred GitOps suite (design §12.1, roadmap 7.1.1) renders from these
specifications; Nile Valley adoption is a Nile Valley change outside this
repository and is listed as a known limitation until it lands.

Update design §1.1, §3.1 Nile Valley row, §7.1 (the lock records the
specification digest), §12.1 GitOps paragraph (link), and §18 fourth bullet.
Check `docs/context.md` rows for "Nile Valley" and "Platform lock" and adjust
only if they now contradict the ADR. Remove the 0004 and scenario 1 and
link-test strict-xfail markers. Gate and commit.

### `EP-M6` documentation closure

Assigned: `REQ-TRACE`, `GAP-ADR-INDEX`.

1. `docs/contents.md`: complete the "Decision records" group (directory entry
   plus four ADR entries, one line each).
2. `docs/developers-guide.md`: add a short "Decision records" subsection:
   where ADRs live, the filename and status rules, that
   `tests/test_decision_records_repository.py` and the BDD feature enforce
   them, that every accepted ADR must be linked from design §18 and
   `docs/contents.md`, and how to supersede or amend an ADR. Add a sentence on
   the substrate fitness tests and that test doubles are never production
   extension points.
3. `docs/khufu-design.md` front matter: bump "Last substantive revision" to
   the completion date and rename §18 to "Decision records and open questions"
   only if all four candidates are now accepted; keep the two remaining open
   items.
4. Stale-claim sweep, excluding `docs/execplans/`:

   ```bash
   rg -n -i "provisional|pending acceptance|ADR candidate|foreground (CI )?mode|Hosts without one use" docs --glob '!docs/execplans/**'
   ```

   Each hit must be either consistent with the ADRs or edited.
5. Roadmap: mark 1.1.1-1.1.4 as done (`- [x]`).
6. Run the full gate sequence, then update this plan's `Progress`,
   `Outcomes & retrospective`, and status to `COMPLETE`.

## Milestones and plateaus

- `EP-M1`: the suite exists; rule tests, property tests, fitness tests, and
  BDD negative scenarios pass; repository acceptance cases are strict-xfail.
  Conformance: no `khufu/` change; only the two authorized dependencies.
  Recovery: revert the two commits. Remaining: all ADRs. Compatibility: none.
- `EP-M2`: ADR 0001 accepted, linked, and its strict-xfail removed.
  Conformance: ToR implementation-home question closed; no Nile Valley or
  release-workflow edits. Recovery: revert the ADR commit. Remaining: ADRs
  0002-0004. Compatibility: none.
- `EP-M3`: ADR 0002 accepted and enforced by fitness tests. Recovery: revert.
  Compatibility: none.
- `EP-M4`: ADR 0003 accepted; no live document claims a foreground mode is
  available. Recovery: revert the single commit (ADR and reconciling edits land
  together so the documents never disagree). Compatibility: none.
- `EP-M5`: ADR 0004 accepted; BDD scenario 1 passes. Recovery: revert.
  Compatibility: none.
- `EP-M6`: indexes, developers' guide, and roadmap current; all gates green.
  Compatibility: none.

At every boundary check: assigned requirements satisfied; design still followed
(or the ADR records the change); no upstream assumption falsified; no
unapproved interface, dependency, trust boundary, or persisted-format change;
trace links in `Conformance basis` current.

## Concrete steps

Working directory: the repository root. Use `bash` with `set -o pipefail` so
`tee` cannot mask a failing gate. Log names follow
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

Run the gates sequentially, never in parallel. Delegating the run to the
`scrutineer` agent is preferred.

Focused commands:

```plaintext
EP-M1 red:   uv run pytest tests/test_decision_record_rules.py -> ModuleNotFoundError (rules module absent)
EP-M1 green: uv run pytest tests/test_decision_record_rules.py tests/test_substrate_fitness.py \
               --hypothesis-show-statistics -> all pass; both duplicate classes appear
EP-M1 repo:  uv run pytest tests/test_decision_records_repository.py \
               tests/test_decision_records_bdd.py -> 4 negative scenarios pass, 6 xfailed
EP-M2..M5:   same command -> one fewer xfailed per milestone; EP-M5 -> 0 xfailed
```

## Validation and acceptance

Acceptance is met when:

- `ls docs/adrs/` lists exactly the four roadmap filenames.
- `make test` passes with no `xfail` remaining in the decision-record suite,
  and the run shows the BDD scenario "The four foundational ADRs are accepted
  and linked" passing.
- Each negative control in `Verification plan` was observed failing for the
  intended reason during `EP-M1` (record the transcripts in
  `Artefacts and notes`), then reverted.
- `make check-fmt`, `make typecheck`, `make lint`, `make markdownlint`, and
  `make nixie` pass.
- The stale-claim sweep in `EP-M6` returns only consistent hits.
- Roadmap 1.1.1-1.1.4 are checked.

Quality criteria: tests and gates above; no performance or security scans beyond
`make audit`, which should be run once after `uv lock` in `EP-M1`.

## Idempotence and recovery

All steps are file edits and test runs; rerunning them is safe. `uv lock` is
deterministic for a fixed index state. Each milestone is a separate commit, so
`git revert <sha>` restores the previous plateau. Seeded faults for negative
controls are made in the working tree only, observed, and reverted with
`git checkout -- <file>` before committing; delete any `.hypothesis/` directory
changes produced by the seeded runs (`.hypothesis/` should be git-ignored; add
it to `.gitignore` in `EP-M1` if it is not).

## Artefacts and notes

Planning-time observations (revision `4ab9802`, 2026-11-20):

```plaintext
$ gh api repos/leynos/khufu/immutable-releases
{"enabled":false,"enforced_by_owner":false}
$ curl -s https://pypi.org/pypi/khufu/json | jq -r '.info.summary'
Twitter Bootstrap elements via Python
$ man logind.conf | grep -A3 UserStopDelaySec   (systemd 257, Rocky Linux 10)
Specifies how long to keep the user record and per-user service user@.service
around for a user after they logged out fully. ... Defaults to 10s.
```

Implementation evidence (red, green, negative controls) is appended here during
execution.

## Interfaces and dependencies

- New dev dependencies: `pytest-bdd` (9.0.x) and `hypothesis` (6.170.x),
  exact pins, `dev` group only. Both declare CPython 3.14 support.
- New test-support modules: `tests/decision_records.py` (pure rules; the
  only owner of ADR grammar and validation; future ADR checks extend it rather
  than re-parsing Markdown elsewhere) and `tests/decision_record_loader.py`
  (filesystem adapter). Both are test infrastructure, not part of the `khufu`
  package, and are documented in `docs/developers-guide.md`.
- No `khufu/` interface, Makefile target, or CI workflow changes.
- Reuse: no existing Markdown or ADR helper exists in the repository (checked
  with `rg -n "def .*markdown|adr" tests scripts khufu`), so no reuse is
  possible; the Makefile already runs everything under `tests/`.

## Revision note

- 2026-11-20: initial draft from reconnaissance; awaiting expert review.
