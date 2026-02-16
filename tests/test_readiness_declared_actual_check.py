from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

SCRIPT = Path("scripts/validation/check_readiness_declared_actual.py")


def _write_report(path: Path, declared: bool, actual: bool) -> None:
    report = {
        "domains": [
            {
                "name": "science",
                "components": [
                    {
                        "name": "coherence_formula",
                        "path": "docs/science/UTAC_v2.0_Coherence_Formula.md",
                        "declared_exists": declared,
                        "actual_exists": actual,
                    }
                ],
            }
        ]
    }
    if path.suffix == ".json":
        path.write_text(json.dumps(report), encoding="utf-8")
    else:
        path.write_text(yaml.safe_dump(report, sort_keys=False), encoding="utf-8")


def test_check_passes_without_mismatches(tmp_path: Path) -> None:
    json_path = tmp_path / "readiness.json"
    yaml_path = tmp_path / "readiness.yaml"
    _write_report(json_path, declared=True, actual=True)
    _write_report(yaml_path, declared=True, actual=True)

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--json",
            str(json_path),
            "--yaml",
            str(yaml_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0
    assert "parity is stable" in proc.stdout


def test_check_fails_on_mismatch(tmp_path: Path) -> None:
    json_path = tmp_path / "readiness.json"
    yaml_path = tmp_path / "readiness.yaml"
    _write_report(json_path, declared=False, actual=True)
    _write_report(yaml_path, declared=True, actual=True)

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--json",
            str(json_path),
            "--yaml",
            str(yaml_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 1
    assert "declared/actual mismatches" in proc.stdout
