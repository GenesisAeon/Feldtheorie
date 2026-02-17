#!/usr/bin/env python3
"""Field Health Contract validator.

Checks the live repository state against the contract defined in
``field_health_contract.yaml`` and reports pass/fail for each clause.

Usage
-----
Check (CI-safe, exit 1 on failure)::

    python scripts/check_field_health.py

JSON output::

    python scripts/check_field_health.py --json

Override contract path::

    python scripts/check_field_health.py --contract path/to/contract.yaml
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
DEFAULT_CONTRACT = BASE_DIR / "field_health_contract.yaml"


def load_contract(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def check_tests(clause: dict) -> dict:
    """Collect tests and verify count meets the contract minimum."""
    min_count = clause.get("min_count", 1)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True,
        cwd=BASE_DIR,
    )
    count = 0
    for line in reversed(result.stdout.strip().splitlines()):
        m = re.search(r"(\d+)\s+tests?\s+collected", line)
        if m:
            count = int(m.group(1))
            break
    ok = count >= min_count
    return {
        "name": "tests",
        "ok": ok,
        "collected": count,
        "min_required": min_count,
        "detail": f"{count} tests collected (min {min_count})",
    }


def check_trilayer_sync(clause: dict) -> dict:
    """Run sigillin_sync.py and verify gap count is within contract limit."""
    max_gaps = clause.get("max_gaps", 0)
    result = subprocess.run(
        [sys.executable, "scripts/sigillin_sync.py", "report"],
        capture_output=True,
        text=True,
        cwd=BASE_DIR,
    )
    gaps = -1
    try:
        data = json.loads(result.stdout)
        gaps = data["meta"]["counts"]["with_gaps"]
    except (json.JSONDecodeError, KeyError):
        pass
    ok = 0 <= gaps <= max_gaps
    return {
        "name": "trilayer_sync",
        "ok": ok,
        "gaps": gaps,
        "max_allowed": max_gaps,
        "detail": f"{gaps} gaps (max {max_gaps})",
    }


def check_version_sync(clause: dict) -> dict:
    """Run update_version.py --check and verify consistency."""
    result = subprocess.run(
        [sys.executable, "scripts/update_version.py", "--check"],
        capture_output=True,
        text=True,
        cwd=BASE_DIR,
    )
    ok = result.returncode == 0
    return {
        "name": "version_sync",
        "ok": ok,
        "detail": result.stdout.strip() if ok else result.stdout.strip() + " " + result.stderr.strip(),
    }


def check_docs_freshness(clause: dict) -> dict:
    """Check that tracked files were modified within max_age_days."""
    max_age = clause.get("max_age_days", 90)
    tracked = clause.get("tracked_files", [])
    now = datetime.now(timezone.utc)
    stale: list[str] = []
    details: list[str] = []

    for filepath in tracked:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", filepath],
            capture_output=True,
            text=True,
            cwd=BASE_DIR,
        )
        date_str = result.stdout.strip()
        if not date_str:
            stale.append(filepath)
            details.append(f"{filepath}: no git history")
            continue
        last_modified = datetime.fromisoformat(date_str)
        age_days = (now - last_modified).days
        if age_days > max_age:
            stale.append(filepath)
            details.append(f"{filepath}: {age_days} days old (max {max_age})")
        else:
            details.append(f"{filepath}: {age_days} days old (OK)")

    ok = len(stale) == 0
    return {
        "name": "docs_freshness",
        "ok": ok,
        "stale_files": stale,
        "max_age_days": max_age,
        "detail": "; ".join(details),
    }


def check_claim_evidence(clause: dict) -> dict:
    """Run claim evidence checker if registry exists."""
    max_missing = clause.get("max_missing_artifacts", 0)
    registry_path = BASE_DIR / "docs" / "science" / "claim_evidence_registry.yaml"
    if not registry_path.exists():
        return {
            "name": "claim_evidence",
            "ok": False,
            "missing": -1,
            "detail": "claim_evidence_registry.yaml not found",
        }
    result = subprocess.run(
        [sys.executable, "scripts/check_claim_evidence.py", "--json"],
        capture_output=True,
        text=True,
        cwd=BASE_DIR,
    )
    try:
        data = json.loads(result.stdout)
        missing = data.get("missing_count", -1)
    except (json.JSONDecodeError, KeyError):
        missing = -1
    ok = 0 <= missing <= max_missing
    return {
        "name": "claim_evidence",
        "ok": ok,
        "missing_artifacts": missing,
        "max_allowed": max_missing,
        "detail": f"{missing} missing artifacts (max {max_missing})",
    }


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

CHECKS = {
    "tests": check_tests,
    "trilayer_sync": check_trilayer_sync,
    "version_sync": check_version_sync,
    "docs_freshness": check_docs_freshness,
    "claim_evidence": check_claim_evidence,
}


def run_contract(contract: dict) -> dict:
    results: list[dict] = []
    for key, check_fn in CHECKS.items():
        clause = contract.get(key)
        if clause is None:
            continue
        results.append(check_fn(clause))

    all_ok = all(r["ok"] for r in results)
    return {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "contract": "field_health_contract.yaml",
        },
        "healthy": all_ok,
        "checks": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Field Health Contract")
    parser.add_argument(
        "--contract",
        type=Path,
        default=DEFAULT_CONTRACT,
        help="Path to contract YAML",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON instead of human-readable")
    args = parser.parse_args()

    contract = load_contract(args.contract)
    envelope = run_contract(contract)

    if args.json:
        print(json.dumps(envelope, ensure_ascii=False, indent=2))
    else:
        status = "HEALTHY" if envelope["healthy"] else "UNHEALTHY"
        print(f"Field Health Contract: {status}")
        print("=" * 50)
        for check in envelope["checks"]:
            icon = "PASS" if check["ok"] else "FAIL"
            print(f"  [{icon}] {check['name']}: {check['detail']}")
        print()

    return 0 if envelope["healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
