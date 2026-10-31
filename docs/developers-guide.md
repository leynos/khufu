# Developer guide

This guide explains the contributor workflow for the generated project and the
architecture conventions for Khufu itself.

## Local workflow

The public entrypoint for formatting, linting, typechecking, tests, and
spelling is `make all`. Narrower Make targets may be invoked when investigating
a specific failure, and changes should be reconciled with the aggregate gate
before being considered complete.

`make lint` checks tracked and untracked Python sources discovered by Git,
including sources under hidden action directories. It runs Ruff 0.16.8,
Interrogate for 100% docstring coverage, Pylint, the DF12 Python lint plugin,
Ambrleaks on `tests/`, the strict Skylos gate and Vulture on test helpers, the
shared Nose duplication gate, and workflow/action validation. Pylint's base
sweep runs on PyPy 3.12 when the selected Python baseline is exactly 3.12; for
a newer baseline it runs on CPython at that baseline. The baseline is the
selected `python_version`, with 3.12 as the minimum supported version. The DF12
Python Lints v0.4.0, Ambrleaks, Skylos, Vulture, and duplication tools run as
isolated tools on Python 3.14.

With default Git source discovery, `fmt`, `check-fmt`, `lint-python`, and
`typecheck` stop with a diagnostic before running tools if Git or repository
metadata is unavailable. GNU Make 4.2 or newer captures one Git result and
checks its `.SHELLSTATUS` immediately; the tools share that captured source
list. `help` and `build` do not depend on source discovery; initialize the
generated project with `git init` before its first quality-gate run.

Rust-enabled projects declare only the PyO3 module initializer as a runtime
entrypoint. The native import tests exercise that boundary, and unused sibling
functions remain blocking.

`make typecheck` runs `ty`, pinned at `0.0.56`: unpinned installations broke
repositories when ty 0.0.56 landed. Bump the pin deliberately — update the
version and fix any new diagnostics in the same pull request.

Ruff and `ty` run from isolated tools on Python 3.14; their versions are pinned
to Ruff 0.16.8 and `ty` 0.0.56. `make check-fmt` and `make fmt` also check or
apply Markdown table formatting with mdtablefix 0.6.1.

`make lint-actions` validates YAML under `.github/` with yamllint 1.38.0,
workflow syntax with actionlint, composite actions with action-validator, and
shell scripts with shellcheck. `make markdownlint` runs markdownlint-cli2 and
the spelling gate. Spelling uses `typos-config-builder` with scope `all`.

Run `make audit` as the dependency vulnerability gate. It runs `pip-audit` for
Python dependencies, and Rust-enabled projects also run `cargo audit` from the
`rust_extension` crate directory.

## Khufu architecture and toolchain

Khufu is designed but not yet implemented. Its developer-facing architecture
lives in the [Khufu design](khufu-design.md); this section records the
conventions a contributor must know before implementation begins.

### Runtime and dependencies

Khufu targets ordinary CPython 3.14 and uses `uv` for environment and lockfile
management. The planned dependency stack is Cyclopts for command parsing,
cuprum as the sole external-command execution boundary, femtologging behind a
narrow logging adapter, and espressoTUI (imported as `espresso`) for the
optional inspector (design §5.3). The lockfile pins exact versions and
distribution hashes; minimum-version metadata does not establish compatibility
(design §5.4). Do not introduce an alternative cluster engine, command runner,
or logging facade; drift between those seams is the problem Khufu exists to
remove.

### Package boundaries

The package lives at `khufu/` and follows the hexagonal layout in design §5.1:
dependencies point inward through `domain`, `application`, `ports`, and
`adapters`, with `cli`, `tui`, `schemas`, `platform`, and `skills` as
supporting packages (design §5.2). Domain code must not import terminal,
subprocess, Kubernetes-client, or logging code; adapters implement ports and
never decide application policy. The roadmap requires an import-boundary check
that enforces this rule.

All external commands go through cuprum's approved-program catalogue and typed
builders. There is no arbitrary `exec` escape hatch, and a catalogue entry for
`kubectl` is not blanket approval for every subcommand (design §5.3). Command
descriptors, CLI registration, `agent-context`, and skill examples are
generated from the same Khufu-owned descriptors, so a new command is added in
one place.

### Sources of truth

- [Khufu design](khufu-design.md) for architecture, contracts, protocol, jobs,
  suites, evidence, and verification.
- [Roadmap](roadmap.md) for delivery order and the acceptance criteria of each
  numbered task.
- [Terms of reference](terms-of-reference.md) and [context](context.md) for
  product scope and vocabulary.
- [ADR candidates](khufu-design.md#18-open-questions-and-adr-candidates) for
  decisions awaiting ratification; record a decision in the design and, when
  substantive, in an ADR before implementing it.

Keep this section current as implementation lands: when a package appears, a
dependency is added or removed, or a decision is ratified, update the design
and this guide together.

## Automation scripts

The [Scripting standards](scripting-standards.md) document provides guidance
for adding or updating helper scripts. New and updated scripts are expected to
use `Cyclopts` for command-line interfaces, `cuprum` for typed and
catalogue-bound external command execution, `pathlib` for filesystem paths, and
`cmd-mox` for tests that mock external executables.

Script changes should update the scripting guide when they introduce a new
convention, command catalogue, testing pattern, or operational expectation that
future contributors need to follow.

## GitHub Actions

The generated repository includes GitHub Actions workflows and local composite
actions under `.github/`.

- `.github/workflows/ci.yml` runs on pushes to `main` and on pull requests. It
  sets up the selected `python_version` baseline (at least 3.12), installs
  `uv`, validates the generated `Makefile` with `mbake`, installs CLI tools,
  then runs `make build`, `make check-fmt`, `make lint`, `make typecheck`,
  `make markdownlint`, and `make audit` except for Dependabot pull requests via
  `if: github.actor != 'dependabot[bot]'`. The Markdown target includes
  repository-wide spelling. CI provisions Go and Rust/Cargo toolchains for
  installing CLI tools, then delegates coverage generation to the shared
  coverage action. Rust lint and test tools are installed and
  `rust_extension/Cargo.toml` is passed to coverage only when the Rust
  extension is enabled.
- `.github/workflows/audit.yml` runs `make audit` against the default branch
  weekly as the compensating control for the Dependabot CI bypass.
- `.github/workflows/act-validation.yml` runs rendered workflow validation in a
  separate workflow. It installs `act`, checks Docker availability, and runs
  `make test WITH_ACT=1` outside the coverage path.
- `.github/workflows/release.yml` publishes wheels when a `v*.*.*` tag is
  pushed. It builds a pure Python wheel, creates a GitHub release with
  generated release notes, downloads wheel artefacts, and uploads them to the
  tag release.
- `.github/workflows/build-wheels.yml` is a reusable workflow for extension
  builds. It accepts a Python version and builds wheels across Linux, Windows,
  and macOS architectures via `.github/actions/build-wheels`.
- `.github/workflows/coverage-main.yml` is the one CodeScene publisher; see
  "CodeScene coverage publication" below.

- `.github/workflows/mutation-testing.yml` runs daily at 09:30 UTC and supports
  manual dispatch. It delegates to reusable workflows from
  `leynos/shared-actions`; stagger the generated cron schedule before adopting
  it alongside other repositories.

  The mutmut job is generated only when the minimum Python version is 3.13 or
  newer because the shared workflow helpers require Python 3.13 or newer.

- `.github/actions/build-wheels` wraps `cibuildwheel` with `uvx` and uploads
  architecture-specific wheel artefacts.
- `.github/actions/pure-python-wheel` builds a pure Python wheel with
  `uv build --wheel` and uploads the resulting artefact.
- `.github/dependabot.yml` enables dependency update pull requests for GitHub
  Actions and Python packages. Rust-enabled projects also receive Cargo updates.

CI provisions Go 1.27 before installing Actionlint 1.7.12, whose minimum is Go
1.25; module caching is disabled because the project has no Go module. It also
provisions stable Rust/Cargo for the `mdtablefix` `cargo-binstall` installer in
both pure-Python and Rust-enabled projects. These prerequisites do not change
the selected `python_version` application baseline. In Rust-enabled projects,
the Rust lint and test cache uses the `rust_extension -> target` workspace
while retaining the tool-cache directories; Rust-specific cache configuration
and tools remain conditional on the extension.

The `CS_ACCESS_TOKEN` secret belongs in the `codescene` environment, whose
deployment policy admits `main` alone. Without it the publisher skips the
upload, writes a warning and still succeeds. If a repository- or
organization-level `CS_ACCESS_TOKEN` also exists, move it into the environment
and delete the broader copy: GitHub makes broader secrets available to
workflows outside the environment, and the publisher falls back to them when
the environment has none.

## Shared spelling configuration

Run `make spelling` to enforce en-GB-oxendict spelling. The shared
`typos-config-builder` gate regenerates `typos.toml` from the live estate
dictionary in `leynos/agent-helper-scripts` and the `typos.local.toml` overlay
on every run, then checks tracked Markdown. A word added to the shared
dictionary therefore needs no change here, and `typos.toml` must never be drift
checked in continuous integration. `typos.toml` is generated output, but it is
tracked: commit the regenerated file after a `make spelling` run changes it.
The local cache that keeps the gate usable when the authority is temporarily
unreachable is ignored by Git. Add only narrow project-specific terms and
exclusions to `typos.local.toml`; never edit generated `typos.toml` by hand.

## CodeScene coverage publication

Main owns CodeScene (CV-005). Nothing a pull request can start talks to
CodeScene or holds its credential.

- **Pull requests** (`.github/workflows/ci.yml`) run the tests, then measure
  coverage and ratchet it with the shared `generate-coverage` action over the
  whole tree, as it measured before the move. The report is not uploaded
  anywhere.
- **Main** (`.github/workflows/coverage-main.yml`) is the one publisher. It
  runs on each push to `main` and on manual dispatch (which must target `main`:
  the `codescene` environment, whose deployment policy admits `main` alone,
  refuses a dispatch from any other branch before the job runs). It generates
  the same coverage, writes the ratchet baseline that pull requests compare
  against, and uploads through the shared `upload-codescene-coverage` action.
  With no `CS_ACCESS_TOKEN` in the environment, the upload step is skipped and
  a separate step writes a warning, so the run still succeeds and the publisher
  works before a CodeScene project exists.
- **Known exception.** Merges made with `GITHUB_TOKEN`, such as Dependabot
  automerge, fire no push event, so they reach the publisher only through a
  later push or a manual dispatch. A manual dispatch uploads coverage but does
  not save the ratchet baseline, which the shared action writes only on a push
  to `main`; pull requests keep comparing against the older baseline until a
  later push advances it.

The `generate-coverage` selection in both workflows must match field for field
(format and interpreter), and `.github/cv005.toml` names the interpreter.

`tests/test_codescene_publisher_wiring.py` states the same invariants as
behavioural checks in this repository's own terms: the pull-request workflow
never names CodeScene, the coverage lane runs on pull requests only and
publishes no artefact, the publisher runs for `main` alone in the `codescene`
environment, the upload needs both the token check and the main ref, the token
reaches the uploader as an input rather than an environment, a missing token is
a warning and not a failure, and the contract checker is pinned to a full
commit. Each fails when its wiring is removed.

### The CV-005 contract check

`make test-workflow-contracts` runs the shared `cv005-contracts` checker
against this repository's workflows. `make all` includes it, and CI runs it.
The checker is fetched from the `leynos/shared-actions` commit named by
`CV005_CONTRACTS_REF` in the `Makefile`, so the first run needs network access.
Always pin a full 40-character commit: a fix to the contract arrives as a pin
bump, never as a local copy of the rules. The command exits 0 when every clause
holds, 1 with one `clause: message` line per violation, and 2 when the tree or
the configuration cannot be read.
