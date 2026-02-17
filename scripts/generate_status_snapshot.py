#!/usr/bin/env python3
"""Generate a single-source-of-truth status snapshot for the Feldtheorie repo.

Collects live telemetry (test counts, version strings, trilayer sync, drift
score) and writes ``status_snapshot.json``.  All top-level documentation
(README, QUICKSTART, TEST_REPORT) should derive their numbers from this file
via ``scripts/sync_docs_from_snapshot.py``.

Usage
-----
Generate snapshot::

    python scripts/generate_status_snapshot.py

Write to custom path::

    python scripts/generate_status_snapshot.py --output /tmp/snapshot.json

Skip slow checks (e.g. for quick iteration)::

    python scripts/generate_status_snapshot.py --skip-tests
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parents[1]
VERSION_FILE = BASE_DIR / "VERSION.yaml"
DEFAULT_OUTPUT = BASE_DIR / "status_snapshot.json"


# ---------------------------------------------------------------------------
# Collectors
# ---------------------------------------------------------------------------


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=BASE_DIR, **kwargs)


def collect_versions() -> dict[str, str]:
    """Read version channels from VERSION.yaml."""
    with VERSION_FILE.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return {
        "package_version": data.get("package_version", "unknown"),
        "release_stream": data.get("release_stream", "unknown"),
        "stable_version": data.get("stable_version", "unknown"),
        "alpha_version": data.get("alpha_version", "unknown"),
    }


def _parse_test_count(stdout: str) -> int:
    """Extract 'N tests collected' from pytest --collect-only output."""
    for line in reversed(stdout.strip().splitlines()):
        m = re.search(r"(\d+)\s+tests?\s+collected", line)
        if m:
            return int(m.group(1))
    return 0


def collect_test_count() -> int:
    """Collect main test count via pytest."""
    result = _run([sys.executable, "-m", "pytest", "--collect-only", "-q"])
    return _parse_test_count(result.stdout)


def collect_v9_test_count() -> int:
    """Collect v9_alpha test count."""
    v9_dir = BASE_DIR / "v9_alpha"
    if not v9_dir.is_dir():
        return 0
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True,
        cwd=v9_dir,
    )
    return _parse_test_count(result.stdout)


def collect_trilayer_sync() -> dict[str, int]:
    """Get trilayer total and gap count from sigillin_sync.py."""
    result = _run([sys.executable, "scripts/sigillin_sync.py", "report"])
    try:
        data = json.loads(result.stdout)
        counts = data.get("meta", {}).get("counts", {})
        return {
            "total": counts.get("total", 0),
            "with_gaps": counts.get("with_gaps", 0),
        }
    except (json.JSONDecodeError, KeyError):
        return {"total": 0, "with_gaps": -1}


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def generate_snapshot(*, skip_tests: bool = False) -> dict:
    versions = collect_versions()

    if skip_tests:
        test_count = 0
        v9_test_count = 0
    else:
        test_count = collect_test_count()
        v9_test_count = collect_v9_test_count()

    trilayer = collect_trilayer_sync()

    return {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator": "scripts/generate_status_snapshot.py",
        },
        "versions": versions,
        "tests": {
            "main_collected": test_count,
            "v9_alpha_collected": v9_test_count,
            "total_collected": test_count + v9_test_count,
        },
        "trilayer": trilayer,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate status_snapshot.json (Single Source of Truth)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output path (default: status_snapshot.json)",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip pytest collection (fast mode, test counts = 0)",
    )
    args = parser.parse_args()

    snapshot = generate_snapshot(skip_tests=args.skip_tests)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"status_snapshot.json written ({snapshot['tests']['main_collected']} tests collected)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
