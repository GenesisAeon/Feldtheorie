#!/usr/bin/env python3
"""Unified doctor output in machine-readable JSON.

Aggregates the same health checks as ``make doctor`` into a single JSON
envelope suitable for dashboards, CI gates, and status boards.

Usage::

    python scripts/doctor_json.py
    python scripts/doctor_json.py --output analysis/doctor_latest.json
"""

from __future__ import annotations

import importlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=BASE_DIR, **kwargs)


def python_version() -> dict[str, object]:
    return {"python": sys.version, "ok": True}


def core_deps() -> dict[str, object]:
    deps: dict[str, str | None] = {}
    for mod in ("numpy", "scipy", "pandas", "yaml"):
        try:
            m = importlib.import_module(mod)
            deps[mod] = getattr(m, "__version__", "unknown")
        except ImportError:
            deps[mod] = None
    ok = all(v is not None for v in deps.values())
    return {"dependencies": deps, "ok": ok}


def test_collection() -> dict[str, object]:
    result = _run([sys.executable, "-m", "pytest", "--collect-only", "-q"])
    count = 0
    for line in reversed(result.stdout.strip().splitlines()):
        match = re.search(r"(\d+)\s+tests?\s+collected", line)
        if match:
            count = int(match.group(1))
            break
    return {"test_count": count, "ok": count > 0}


def trilayer_sync() -> dict[str, object]:
    result = _run([sys.executable, "scripts/sigillin_sync.py", "report"])
    try:
        data = json.loads(result.stdout)
        counts = data.get("meta", {}).get("counts", {})
        total = counts.get("total", 0)
        gaps = counts.get("with_gaps", 0)
        return {"total": total, "with_gaps": gaps, "ok": gaps == 0}
    except (json.JSONDecodeError, KeyError):
        return {"total": 0, "with_gaps": -1, "ok": False, "error": result.stderr.strip()}


def version_sync() -> dict[str, object]:
    result = _run([sys.executable, "scripts/update_version.py", "--check"])
    ok = result.returncode == 0
    return {"ok": ok, "details": result.stdout.strip()}


def docs_index_parity() -> dict[str, object]:
    result = _run(
        [sys.executable, "scripts/archive_sigillin.py", "--recount", "--recount-targets", "docs", "--dry-run", "--fail-on-delta"]
    )
    # returncode 2 signals parity drift (delta != 0 or missing/orphan entries)
    ok = result.returncode == 0

    # Extract concrete delta numbers from output for diagnostics
    details = result.stdout.strip()[:500]
    missing: list[str] = []
    orphans: list[str] = []
    for line in result.stdout.splitlines():
        if "Missing in index:" in line:
            missing = [s.strip() for s in line.split(":", 1)[1].split(",") if s.strip()]
        elif "Orphan entries:" in line:
            orphans = [s.strip() for s in line.split(":", 1)[1].split(",") if s.strip()]

    return {
        "ok": ok,
        "details": details,
        "missing_count": len(missing),
        "orphan_count": len(orphans),
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Machine-readable health check (JSON)")
    parser.add_argument("--output", type=Path, help="Write JSON to file")
    args = parser.parse_args()

    envelope: dict[str, object] = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tool": "scripts/doctor_json.py",
        },
        "checks": {
            "python": python_version(),
            "core_deps": core_deps(),
            "test_collection": test_collection(),
            "trilayer_sync": trilayer_sync(),
            "version_sync": version_sync(),
            "docs_index_parity": docs_index_parity(),
        },
    }

    all_ok = all(
        check.get("ok", False)
        for check in envelope["checks"].values()
        if isinstance(check, dict)
    )
    envelope["healthy"] = all_ok

    output_json = json.dumps(envelope, ensure_ascii=False, indent=2)
    print(output_json)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_json, encoding="utf-8")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
