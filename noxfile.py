"""Nox rituals keeping the logistic resonance reproducible."""

from __future__ import annotations

import os
import sys

import nox

DEFAULT_PYTHON = os.environ.get("NOX_PYTHON", f"{sys.version_info.major}.{sys.version_info.minor}")

nox.options.sessions = ["lint", "tests", "crep_guard"]
nox.options.error_on_missing_interpreters = False


def _install(session: nox.Session, *packages: str) -> None:
    """Install *packages* while echoing the membrane cadence."""

    if packages:
        session.install(*packages)


def _reuse_virtualenv(session: nox.Session) -> None:
    """Reuse the virtualenv when running inside CI or GitHub Codespaces."""

    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        session.env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
        session.env.setdefault("NOX_SESSION_REUSE", "1")


@nox.session(python=DEFAULT_PYTHON)
def lint(session: nox.Session) -> None:
    """Check formatting and static diagnostics so ΔAIC guards stay awake."""

    _reuse_virtualenv(session)
    _install(session, "ruff>=0.5.0", "black>=24.4")
    session.run("ruff", "check", "analysis", "models", "tests", "noxfile.py", "pyproject.toml")
    session.run("black", "--check", "analysis", "models", "tests")


@nox.session(python=DEFAULT_PYTHON)
def format(session: nox.Session) -> None:
    """Apply formatting when the membrane requests a gentle tuning."""

    _reuse_virtualenv(session)
    _install(session, "black>=24.4")
    session.run("black", "analysis", "models", "tests")


@nox.session(python=DEFAULT_PYTHON)
def tests(session: nox.Session) -> None:
    """Run the pytest suite so the resonance ledger stays trustworthy."""

    # Known-risk register — tests explicitly excluded from the default run:
    #
    #   tests/test_aeon_api_bridge.py
    #   science/tests/test_aeon_api_bridge.py
    #     Risk: requires live AEON API endpoint; fails in offline CI.
    #     Owner: api-bridge subsystem.  Review trigger: API contract change.
    #
    #   tests/test_neuro_profile_model.py
    #     Risk: depends on optional LLM/model weights not bundled in the repo.
    #     Owner: NeuroProfile track.  Review trigger: model artefacts added.
    #
    # Any new ignore MUST be added here with a matching rationale entry.
    _reuse_virtualenv(session)
    session.install(".", ".[dev,api]", "pytest-asyncio>=0.23,<1")
    session.run(
        "pytest",
        "tests",
        "--ignore=tests/test_aeon_api_bridge.py",
        "--ignore=science/tests/test_aeon_api_bridge.py",
        "--ignore=tests/test_neuro_profile_model.py",
        "--maxfail=1",
        "--disable-warnings",
    )


@nox.session(python=DEFAULT_PYTHON)
def typecheck(session: nox.Session) -> None:
    """Mypy sweep to ensure symbols echo correctly across the membrane."""

    _reuse_virtualenv(session)
    _install(session, "mypy>=1.10")
    session.install(".")
    session.run("mypy", "analysis", "models")


@nox.session(python=DEFAULT_PYTHON)
def crep_guard(session: nox.Session) -> None:
    """Run CREP/τ* Safety Guard for Type-VI governance artifacts."""

    _reuse_virtualenv(session)
    session.install("pyyaml>=6.0")
    session.run(
        "python",
        "-m",
        "tools.crep_guard",
        "--check-type6-trilayer",
        "--threshold",
        "0.7",
        "--tau-default",
        "0.1",
    )


@nox.session(python=DEFAULT_PYTHON)
def drift_gate(session: nox.Session) -> None:
    """Block release when declared readiness diverges from observed filesystem truth.

    Runs scripts/validation/check_status_drift_score.py against the latest
    utac_v2_readiness.json.  Exits non-zero (and therefore fails CI) when the
    status_drift_score is non-zero, i.e. when any of the following is true:

      - declared vs. actual component existence mismatches > 0
      - doc-target artifacts listed in the readiness report are missing
      - readiness report is older than 14 days (stale declared truth)
      - TEST_REPORT.md is older than 30 days (stale observed truth)

    This implements the "CI Truth Gate" from the P1 backlog:
    statusboard.json (observed) must be reconcilable with utac_v2_readiness.json
    (declared) before any release-gate passes.
    """
    _reuse_virtualenv(session)
    session.run(
        "python",
        "scripts/validation/check_status_drift_score.py",
        "--max-age-days",
        "14",
        "--max-test-report-age-days",
        "30",
        external=True,
    )


@nox.session(python=DEFAULT_PYTHON)
def build(session: nox.Session) -> None:
    """Assemble wheel and sdist artefacts for release bundles."""

    _reuse_virtualenv(session)
    session.install("hatchling>=1.24")
    session.run("hatch", "build")
