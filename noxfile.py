"""Nox rituals keeping the logistic resonance reproducible."""

from __future__ import annotations

import os

import nox

DEFAULT_PYTHON = "3.11"

nox.options.sessions = ["lint", "tests"]


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

    _reuse_virtualenv(session)
    session.install(".", ".[dev]")
    session.run("pytest", "--maxfail=1", "--disable-warnings")


@nox.session(python=DEFAULT_PYTHON)
def typecheck(session: nox.Session) -> None:
    """Mypy sweep to ensure symbols echo correctly across the membrane."""

    _reuse_virtualenv(session)
    _install(session, "mypy>=1.10")
    session.install(".")
    session.run("mypy", "analysis", "models")


@nox.session(python=DEFAULT_PYTHON)
def build(session: nox.Session) -> None:
    """Assemble wheel and sdist artefacts for release bundles."""

    _reuse_virtualenv(session)
    session.install("hatchling>=1.24")
    session.run("hatch", "build")
