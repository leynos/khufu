"""Behavioural checks for the CodeScene coverage arrangement (CV-005).

Main owns CodeScene: pull requests measure coverage and never reach CodeScene,
and one push-to-main publisher uploads from the ``codescene`` environment. The
shared ``cv005-contracts`` checker (``make test-workflow-contracts``) holds the
whole shape. These tests state the same invariants in this repository's own
terms, so a reader of the test suite sees them and a regression in one wiring
fails here with a message that names it.
"""

import re
import typing as typ
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
UPLOAD_ACTION = "leynos/shared-actions/.github/actions/upload-codescene-coverage@"
AVAILABILITY_COMMAND = (
    'echo "available=${{ secrets.CS_ACCESS_TOKEN != \'\' }}" >> "$GITHUB_OUTPUT"'
)


def _workflow(name: str) -> dict[typ.Any, typ.Any]:
    """Return the parsed workflow file.

    Returns
    -------
    dict[typing.Any, typing.Any]
        The workflow document.
    """
    return yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))


def _steps(name: str, job: str) -> list[dict[str, typ.Any]]:
    """Return the steps of the named job, in order.

    Returns
    -------
    list[dict[str, typing.Any]]
        The job's steps.
    """
    return _workflow(name)["jobs"][job]["steps"]


def _step(name: str, job: str, step_name: str) -> dict[str, typ.Any]:
    """Return the one step called *step_name*.

    Returns
    -------
    dict[str, typing.Any]
        That step.
    """
    matches = [s for s in _steps(name, job) if s.get("name") == step_name]
    assert len(matches) == 1, f"{name} must have exactly one step {step_name!r}"
    return matches[0]


def test_the_pull_request_workflow_never_reaches_codescene() -> None:
    """Scenario: a pull request runs CI. Invariant: nothing names CodeScene."""
    text = (WORKFLOWS / "ci.yml").read_text(encoding="utf-8").lower()
    code = "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )
    for forbidden in ("cs_access_token", "codescene.io", "upload-codescene-coverage"):
        assert forbidden not in code, f"ci.yml must not mention {forbidden}"


def test_the_pull_request_coverage_lane_is_pull_request_only() -> None:
    """The ratchet lane measures on pull requests and publishes no artefact."""
    lane = _step("ci.yml", "lint-test", "Test and Measure Coverage")
    assert lane["if"] == "github.event_name == 'pull_request'", (
        "the coverage lane must run on pull requests, and only there"
    )
    assert lane["with"]["with-ratchet"] == "true", "the lane must ratchet coverage"
    assert lane["with"]["publish-artefact"] == "false", "the lane publishes nothing"


def test_the_publisher_runs_only_for_main() -> None:
    """Scenario: a push or a dispatch. Invariant: main, in the environment."""
    workflow = _workflow("coverage-main.yml")
    triggers = workflow.get("on", workflow.get(True))
    assert triggers["push"]["branches"] == ["main"], "the publisher is a main push"
    assert "pull_request" not in triggers, "a pull request must never publish"
    job = workflow["jobs"]["coverage-upload"]
    assert job["environment"] == "codescene", "the token lives in the environment"
    assert job["permissions"] == {"contents": "read"}, "the publisher only reads"


def test_the_upload_needs_the_token_and_the_main_ref() -> None:
    """Scenario: a dispatch from a branch. Invariant: nothing is uploaded."""
    upload = _step(
        "coverage-main.yml", "coverage-upload", "Upload coverage data to CodeScene"
    )
    assert UPLOAD_ACTION in upload["uses"], "the shared uploader publishes"
    guard = " ".join(str(upload["if"]).split())
    assert "steps.codescene-token.outputs.available == 'true'" in guard, (
        "the upload must wait for the token check"
    )
    assert "github.ref == 'refs/heads/main'" in guard, (
        "a dispatch from another branch must not upload"
    )
    assert upload["with"]["mode"] == "upload", "the publisher uploads, never checks"


def test_the_token_reaches_the_uploader_as_an_input_not_an_environment() -> None:
    """The composite uploader would hand a step's env to its nested steps."""
    upload = _step(
        "coverage-main.yml", "coverage-upload", "Upload coverage data to CodeScene"
    )
    assert upload["with"]["access-token"] == "${{ secrets.CS_ACCESS_TOKEN }}", (
        "the token goes straight to the input"
    )
    assert "env" not in upload, "the upload step must bind no environment"
    check = _step(
        "coverage-main.yml", "coverage-upload", "Check for the CodeScene token"
    )
    assert check["run"].strip() == AVAILABILITY_COMMAND, (
        "the check runs the exact command"
    )
    assert "env" not in check, "the check binds no environment"


def test_a_missing_token_is_a_warning_and_the_run_still_succeeds() -> None:
    """Scenario: no token in the environment. Invariant: warn, do not fail."""
    warn = _step(
        "coverage-main.yml", "coverage-upload", "Report skipped CodeScene upload"
    )
    assert warn["if"] == "steps.codescene-token.outputs.available != 'true'", (
        "the warning must run exactly when the token is unavailable"
    )
    assert "::warning::" in warn["run"], "a skipped upload is recorded as a warning"
    assert "continue-on-error" not in warn, "the warning step must not mask failures"


def test_the_contract_checker_is_pinned_to_a_full_commit() -> None:
    """The shared checker is fetched from one full shared-actions commit."""
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    match = re.search(r"^CV005_CONTRACTS_REF \?= (\S+)$", makefile, re.MULTILINE)
    assert match is not None, "the Makefile must pin CV005_CONTRACTS_REF"
    assert re.fullmatch(r"[0-9a-f]{40}", match.group(1)), "pin a full commit"
    assert "test-workflow-contracts" in makefile, "the Makefile runs the checker"


@pytest.mark.parametrize("name", ["ci.yml", "coverage-main.yml"])
def test_both_workflows_declare_least_privilege_permissions(name: str) -> None:
    """The token and the lane read the repository and nothing more."""
    workflow = _workflow(name)
    permissions = workflow.get("permissions") or workflow["jobs"][
        "coverage-upload" if name == "coverage-main.yml" else "lint-test"
    ].get("permissions")
    assert permissions in ({"contents": "read"}, {}), f"{name} must not write"


# Messages for the actionlint test are module constants so that a passing run
# still executes every line (slipcover counts unexecuted continuation lines of
# a multi-line assertion message against the coverage ratchet).
ACTIONLINT_MESSAGES: typ.Final = {
    "unpinned": "both workflows must install a pinned actionlint",
    "mismatch": "the publisher and ci.yml must agree on the actionlint version",
    "path": "the tool must reach the PATH of later steps",
    "late": "actionlint must be installed before coverage is measured",
}


def test_the_publisher_installs_actionlint_at_the_version_ci_uses() -> None:
    """The publisher measures the same suite as the pull-request lane.

    Tests that need ``actionlint`` skip without it, and a skipped test is
    uncovered code, so a publisher without the tool measured less coverage than
    the lane and failed the ratchet against the stored baseline.
    """
    install = _step("coverage-main.yml", "coverage-upload", "Install actionlint")
    ci_run = _step("ci.yml", "lint-test", "Install CLI tools")["run"]
    pattern = r"actionlint@(v[0-9.]+)"
    versions = [re.findall(pattern, install["run"]), re.findall(pattern, ci_run)]
    steps = _steps("coverage-main.yml", "coverage-upload")
    names = [step.get("name") for step in steps]
    ordered = names.index("Install actionlint") < names.index("Generate coverage")
    assert all(len(found) == 1 for found in versions), ACTIONLINT_MESSAGES["unpinned"]
    assert versions[0] == versions[1], ACTIONLINT_MESSAGES["mismatch"]
    assert "$GITHUB_PATH" in install["run"], ACTIONLINT_MESSAGES["path"]
    assert ordered, ACTIONLINT_MESSAGES["late"]
