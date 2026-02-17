#!/usr/bin/env python3
"""Generate a statusboard JSON aggregating all operational telemetry.

Reads existing artifacts (no expensive subprocess calls) to build a single
operational dashboard with R/Θ/β/ζ parameters, test counts, trilayer sync,
manifest gaps, and the latest codex ID.

Usage
-----
Generate statusboard (reads existing artifacts)::

    python scripts/generate_statusboard.py

Write to custom path::

    python scripts/generate_statusboard.py --output /tmp/statusboard.json

The output complements ``status_snapshot.json`` (which collects live pytest
counts) by adding the UTAC membrane parameters and manifest gap data that
the snapshot does not track.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = BASE_DIR / "statusboard.json"

# Data sources (all pre-computed JSON artifacts — no subprocess calls)
VERSION_FILE = BASE_DIR / "VERSION.yaml"
SNAPSHOT_FILE = BASE_DIR / "status_snapshot.json"
READINESS_FILE = BASE_DIR / "analysis" / "reports" / "utac_v2_readiness.json"
MANIFEST_GLOB = "analysis/results/utac_v2_manifest_gap_scan_*.json"
CODEX_JSON = BASE_DIR / "seed" / "codexfeedback.json"


# ---------------------------------------------------------------------------
# Collectors (artifact readers — no pytest, no subprocesses)
# ---------------------------------------------------------------------------


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None


def collect_versions() -> dict[str, str]:
    if not VERSION_FILE.exists():
        return {}
    with VERSION_FILE.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return {
        "package_version": data.get("package_version", "unknown"),
        "release_stream": data.get("release_stream", "unknown"),
        "stable_version": data.get("stable_version", "unknown"),
        "alpha_version": data.get("alpha_version", "unknown"),
    }


def collect_snapshot_tests() -> dict[str, int]:
    data = _read_json(SNAPSHOT_FILE)
    if data is None:
        return {"main_collected": 0, "v9_alpha_collected": 0, "total_collected": 0}
    return data.get("tests", {})


def collect_snapshot_trilayer() -> dict[str, int]:
    data = _read_json(SNAPSHOT_FILE)
    if data is None:
        return {"total": 0, "with_gaps": -1}
    return data.get("trilayer", {})


def collect_readiness() -> dict[str, object]:
    data = _read_json(READINESS_FILE)
    if data is None:
        return {"available": False}
    logistic = data.get("meta", {}).get("logistic", {})
    summary = data.get("data_summary", {})
    return {
        "available": True,
        "R": logistic.get("mean_readiness"),
        "theta": logistic.get("theta"),
        "beta": logistic.get("beta"),
        "sigma": logistic.get("sigma"),
        "datasets_total": summary.get("total"),
        "datasets_fully_ready": summary.get("fully_ready"),
    }


def _latest_manifest_scan() -> Path | None:
    """Find the most recent manifest gap scan by filename timestamp."""
    pattern = str(BASE_DIR / MANIFEST_GLOB)
    candidates = sorted(glob.glob(pattern))
    return Path(candidates[-1]) if candidates else None


def collect_manifest_gaps() -> dict[str, object]:
    path = _latest_manifest_scan()
    if path is None:
        return {"available": False}
    data = _read_json(path)
    if data is None:
        return {"available": False, "path": str(path)}
    logistic = data.get("logistic", {})
    summary = data.get("summary", {})
    return {
        "available": True,
        "scan_file": path.name,
        "scan_date": data.get("generated_at"),
        "R_manifest": logistic.get("mean_readiness"),
        "theta": logistic.get("theta"),
        "beta": logistic.get("beta"),
        "sigma_manifest": logistic.get("sigma"),
        "datasets_pending": summary.get("datasets_pending", 0),
        "components_missing": summary.get("missing_components_total", 0),
        "analysis_gaps": summary.get("analysis_gaps", 0),
    }


def collect_latest_codex_id() -> dict[str, str | None]:
    """Extract the most recent codex entry ID from codexfeedback.json."""
    data = _read_json(CODEX_JSON)
    if data is None or not isinstance(data, dict):
        return {"latest_id": None}
    entries = data.get("entries", [])
    if not entries:
        return {"latest_id": None}
    last = entries[-1]
    return {
        "latest_id": last.get("id"),
        "latest_title": last.get("title"),
        "latest_created": last.get("created_at"),
        "total_entries": len(entries),
    }


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def generate_statusboard() -> dict:
    versions = collect_versions()
    tests = collect_snapshot_tests()
    trilayer = collect_snapshot_trilayer()
    readiness = collect_readiness()
    manifest = collect_manifest_gaps()
    codex = collect_latest_codex_id()

    # Determine overall membrane state
    sigma_readiness = readiness.get("sigma")
    sigma_manifest = manifest.get("sigma_manifest")
    datasets_pending = manifest.get("datasets_pending", 0)
    components_missing = manifest.get("components_missing", 0)
    trilayer_gaps = trilayer.get("with_gaps", -1)

    # Health verdict: green/yellow/red
    if trilayer_gaps == 0 and components_missing == 0 and datasets_pending == 0:
        health = "green"
    elif trilayer_gaps == 0 and (components_missing > 0 or datasets_pending > 0):
        health = "yellow"
    else:
        health = "red"

    return {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator": "scripts/generate_statusboard.py",
        },
        "health": health,
        "versions": versions,
        "membrane": {
            "readiness": {
                "R": readiness.get("R"),
                "theta": readiness.get("theta"),
                "beta": readiness.get("beta"),
                "sigma": sigma_readiness,
            },
            "manifest": {
                "R": manifest.get("R_manifest"),
                "theta": manifest.get("theta"),
                "beta": manifest.get("beta"),
                "sigma": sigma_manifest,
                "datasets_pending": datasets_pending,
                "components_missing": components_missing,
                "scan_date": manifest.get("scan_date"),
            },
        },
        "tests": tests,
        "trilayer": {
            "total": trilayer.get("total", 0),
            "with_gaps": trilayer_gaps,
        },
        "codex": codex,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate statusboard.json (operational telemetry dashboard)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output path (default: statusboard.json)",
    )
    args = parser.parse_args()

    board = generate_statusboard()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(board, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Print summary to stdout
    h = board["health"]
    m = board["membrane"]
    t = board["tests"]
    print(f"Health: {h}")
    print(f"  Readiness: σ={m['readiness']['sigma']}, R={m['readiness']['R']}")
    print(
        f"  Manifest:  σ={m['manifest']['sigma']}, R={m['manifest']['R']}, "
        f"pending={m['manifest']['datasets_pending']}, missing={m['manifest']['components_missing']}"
    )
    print(f"  Tests:     {t.get('total_collected', 0)} collected")
    print(f"  Trilayer:  {board['trilayer']['total']} total, {board['trilayer']['with_gaps']} gaps")
    print(f"  Codex:     {board['codex'].get('latest_id', 'n/a')}")
    print(f"Written: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
