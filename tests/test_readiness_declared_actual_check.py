from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

SCRIPT = Path("scripts/validation/check_readiness_declared_actual.py")


def _write_domains_report(path: Path, declared: bool, actual: bool) -> None:
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


def _write_datasets_report(path: Path, declared: bool, actual: bool) -> None:
    report = {
        "datasets": [
            {
                "id": "utac-v1_3-ds-001",
                "domain": "climate",
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


def _run_check(json_path: Path, yaml_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
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
        encoding="utf-8",
        check=False,
    )


def test_check_passes_without_mismatches_domains_schema(tmp_path: Path) -> None:
    json_path = tmp_path / "readiness.json"
    yaml_path = tmp_path / "readiness.yaml"
    _write_domains_report(json_path, declared=True, actual=True)
    _write_domains_report(yaml_path, declared=True, actual=True)

    proc = _run_check(json_path, yaml_path)

    assert proc.returncode == 0
    assert "parity is stable" in proc.stdout


def test_check_fails_on_mismatch_domains_schema(tmp_path: Path) -> None:
    json_path = tmp_path / "readiness.json"
    yaml_path = tmp_path / "readiness.yaml"
    _write_domains_report(json_path, declared=False, actual=True)
    _write_domains_report(yaml_path, declared=True, actual=True)

    proc = _run_check(json_path, yaml_path)

    assert proc.returncode == 1
    assert "declared/actual mismatches" in proc.stdout


def test_check_fails_on_mismatch_datasets_schema(tmp_path: Path) -> None:
    json_path = tmp_path / "readiness.json"
    yaml_path = tmp_path / "readiness.yaml"
    _write_datasets_report(json_path, declared=False, actual=True)
    _write_datasets_report(yaml_path, declared=True, actual=True)

    proc = _run_check(json_path, yaml_path)

    assert proc.returncode == 1
    assert "declared/actual mismatches" in proc.stdout
    assert "utac-v1_3-ds-001 (climate)" in proc.stdout
