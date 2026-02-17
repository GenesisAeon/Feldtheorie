#!/usr/bin/env python3
"""Validate hard-coded claims in top-level documentation against live data.

Checks README.md, QUICKSTART.md, and TEST_REPORT.md for claims about test
counts, version strings, etc. and compares them to the actual state from
pytest / VERSION.yaml.  This catches drift even when status_snapshot.json
has not been regenerated.

Usage
-----
Run validation (CI-safe, exit 1 on any mismatch)::

    python scripts/validate_doc_claims.py

JSON output::

    python scripts/validate_doc_claims.py --json

Skip pytest (use snapshot instead)::

    python scripts/validate_doc_claims.py --from-snapshot status_snapshot.json
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
README = BASE_DIR / "README.md"
QUICKSTART = BASE_DIR / "QUICKSTART.md"
TEST_REPORT = BASE_DIR / "TEST_REPORT.md"
VERSION_FILE = BASE_DIR / "VERSION.yaml"


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------


def _parse_test_count(stdout: str) -> int:
    for line in reversed(stdout.strip().splitlines()):
        m = re.search(r"(\d+)\s+tests?\s+collected", line)
        if m:
            return int(m.group(1))
    return 0


def collect_live_data() -> dict:
    """Collect real test count and version info."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True,
        cwd=BASE_DIR,
    )
    test_count = _parse_test_count(result.stdout)

    with VERSION_FILE.open("r", encoding="utf-8") as fh:
        versions = yaml.safe_load(fh)

    return {
        "test_count": test_count,
        "package_version": versions.get("package_version", "unknown"),
    }


def load_from_snapshot(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        snap = json.load(fh)
    return {
        "test_count": snap["tests"]["main_collected"],
        "package_version": snap["versions"]["package_version"],
    }


# ---------------------------------------------------------------------------
# Claim extractors
# ---------------------------------------------------------------------------


def _extract_readme_claims(text: str) -> list[dict]:
    """Find test-count claims in README.md."""
    claims: list[dict] = []

    # Badge: tests-1224%2F1224%20passing
    badge = re.search(r"tests-(\d+)%2F(\d+)%20passing", text)
    if badge:
        claims.append({
            "file": "README.md",
            "claim_type": "test_badge",
            "claimed_value": int(badge.group(1)),
            "pattern": f"badge shows {badge.group(1)}/{badge.group(2)}",
        })

    # Prose: "1224 passing tests" or "1224/1224 tests passing"
    for m in re.finditer(r"\b(\d+) passing tests\b", text):
        claims.append({
            "file": "README.md",
            "claim_type": "test_prose",
            "claimed_value": int(m.group(1)),
            "pattern": m.group(0),
        })
    for m in re.finditer(r"\b(\d+)/\d+ tests passing\b", text):
        claims.append({
            "file": "README.md",
            "claim_type": "test_prose",
            "claimed_value": int(m.group(1)),
            "pattern": m.group(0),
        })

    return claims


def _extract_quickstart_claims(text: str) -> list[dict]:
    claims: list[dict] = []
    m = re.search(r"tests/\s+.*?(\d+)/\d+ tests", text)
    if m:
        claims.append({
            "file": "QUICKSTART.md",
            "claim_type": "test_count",
            "claimed_value": int(m.group(1)),
            "pattern": m.group(0),
        })
    return claims


def _extract_test_report_claims(text: str) -> list[dict]:
    claims: list[dict] = []
    m = re.search(r"\*\*(\d+) Tests eingesammelt\*\*", text)
    if m:
        claims.append({
            "file": "TEST_REPORT.md",
            "claim_type": "test_collected",
            "claimed_value": int(m.group(1)),
            "pattern": m.group(0),
        })
    return claims


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate(live: dict) -> list[dict]:
    """Return list of claim check results."""
    results: list[dict] = []

    for path, extractor in [
        (README, _extract_readme_claims),
        (QUICKSTART, _extract_quickstart_claims),
        (TEST_REPORT, _extract_test_report_claims),
    ]:
        if not path.exists():
            results.append({
                "file": path.name,
                "ok": False,
                "detail": f"{path.name} not found",
            })
            continue

        text = path.read_text(encoding="utf-8")
        claims = extractor(text)

        for claim in claims:
            expected = live["test_count"]
            ok = claim["claimed_value"] == expected
            results.append({
                "file": claim["file"],
                "claim_type": claim["claim_type"],
                "claimed": claim["claimed_value"],
                "actual": expected,
                "pattern": claim["pattern"],
                "ok": ok,
            })

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate doc claims against live data")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument(
        "--from-snapshot",
        type=Path,
        default=None,
        help="Use snapshot instead of running pytest",
    )
    args = parser.parse_args()

    if args.from_snapshot:
        live = load_from_snapshot(args.from_snapshot)
    else:
        live = collect_live_data()

    results = validate(live)
    all_ok = all(r["ok"] for r in results)

    envelope = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": str(args.from_snapshot) if args.from_snapshot else "live",
            "actual_test_count": live["test_count"],
        },
        "ok": all_ok,
        "claims": results,
    }

    if args.json:
        print(json.dumps(envelope, ensure_ascii=False, indent=2))
    else:
        status = "ALL CLAIMS VALID" if all_ok else "CLAIM DRIFT DETECTED"
        print(f"Doc Claim Validation: {status}")
        print(f"  Actual test count: {live['test_count']}")
        print()
        for r in results:
            icon = "OK" if r["ok"] else "DRIFT"
            detail = f"claimed={r.get('claimed')}, actual={r.get('actual')}"
            print(f"  [{icon}] {r['file']}: {r.get('claim_type', 'check')} ({detail})")
            if not r["ok"]:
                print(f"         pattern: {r.get('pattern', '')}")
        print()
        if not all_ok:
            print("Fix: python scripts/generate_status_snapshot.py && "
                  "python scripts/sync_docs_from_snapshot.py --apply")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
