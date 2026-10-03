"""Environment guard for the Mandala memory lab tests.

The lab runs in its own environment: Windows, results and temp on D:/mandala,
scoped-correspondence >= 0.42.0 (venv D:/mandala/.venvs/mandala-memory). Repo-wide
runs such as Feldtheorie's CI (`pytest --cov=src` from the root, Linux, no SCF)
would otherwise collect these files and fail on missing prerequisites -- or
write into a relative "D:" directory. Outside the lab environment the whole
folder is therefore NOT collected and the reason is reported once.
"""
import importlib.metadata
import os
import sys


def _lab_environment_problem():
    if sys.platform != "win32":
        return "not Windows (the runner measures peak memory via the Windows API)"
    if not os.path.isdir("D:/mandala"):
        return "local lab layout D:/mandala not present"
    try:
        version = importlib.metadata.version("scoped-correspondence")
    except importlib.metadata.PackageNotFoundError:
        return "scoped-correspondence not installed"
    parts = tuple(int(p) for p in version.split(".")[:2] if p.isdigit())
    if parts < (0, 42):
        return f"scoped-correspondence {version} < 0.42.0 (use D:/mandala/.venvs/mandala-memory)"
    return None


_PROBLEM = _lab_environment_problem()
collect_ignore_glob = ["test_*.py"] if _PROBLEM else []


def pytest_report_header(config):
    if _PROBLEM:
        return f"mandala_memory lab tests NOT collected: {_PROBLEM}"


def pytest_sessionfinish(session, exitstatus):
    if _PROBLEM:
        tr = session.config.pluginmanager.get_plugin("terminalreporter")
        if tr is not None:
            tr.write_line(f"[mandala_memory] lab tests not collected: {_PROBLEM}")
