from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _write_report(path: Path, *, mismatches: int, doc_exists: bool, generated_at: str) -> None:
    payload = {
        "meta": {"generated_at": generated_at},
        "declared_actual_drift": {"mismatch_count": mismatches, "has_drift": mismatches > 0},
        "doc_targets": [
            {
                "path": "docs/science/example.md",
                "exists": doc_exists,
                "expected_outputs": [],
            }
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_test_report(path: Path, date_str: str) -> None:
    path.write_text(
        "\n".join(
            [
                "# Test Suite Report - V6",
                "",
                f"**Datum:** {date_str}",
                "**Branch:** main",
            ]
        ),
        encoding="utf-8",
    )


def test_status_drift_gate_passes_for_clean_report(tmp_path: Path) -> None:
    report = tmp_path / "readiness.json"
    test_report = tmp_path / "TEST_REPORT.md"
    _write_report(
        report,
        mismatches=0,
        doc_exists=True,
        generated_at="2099-01-01T00:00:00+00:00",
    )
    _write_test_report(test_report, "2099-01-01")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/validation/check_status_drift_score.py",
            "--json",
            str(report),
            "--max-age-days",
            "14",
            "--test-report",
            str(test_report),
            "--max-test-report-age-days",
            "30",
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 0
    assert "status_drift_score=0" in result.stdout


def test_status_drift_gate_fails_for_mismatch(tmp_path: Path) -> None:
    report = tmp_path / "readiness.json"
    test_report = tmp_path / "TEST_REPORT.md"
    _write_report(
        report,
        mismatches=1,
        doc_exists=True,
        generated_at="2099-01-01T00:00:00+00:00",
    )
    _write_test_report(test_report, "2099-01-01")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/validation/check_status_drift_score.py",
            "--json",
            str(report),
            "--test-report",
            str(test_report),
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 1
    assert "status_drift_score=1" in result.stdout


def test_status_drift_gate_fails_for_stale_report(tmp_path: Path) -> None:
    report = tmp_path / "readiness.json"
    test_report = tmp_path / "TEST_REPORT.md"
    _write_report(
        report,
        mismatches=0,
        doc_exists=True,
        generated_at="2000-01-01T00:00:00+00:00",
    )
    _write_test_report(test_report, "2099-01-01")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/validation/check_status_drift_score.py",
            "--json",
            str(report),
            "--max-age-days",
            "1",
            "--test-report",
            str(test_report),
            "--max-test-report-age-days",
            "30",
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 1
    assert "stale_penalty=" in result.stdout


def test_status_drift_gate_fails_for_stale_test_report(tmp_path: Path) -> None:
    report = tmp_path / "readiness.json"
    test_report = tmp_path / "TEST_REPORT.md"
    _write_report(
        report,
        mismatches=0,
        doc_exists=True,
        generated_at="2099-01-01T00:00:00+00:00",
    )
    _write_test_report(test_report, "2000-01-01")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/validation/check_status_drift_score.py",
            "--json",
            str(report),
            "--test-report",
            str(test_report),
            "--max-test-report-age-days",
            "1",
            "--max-age-days",
            "-1",
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 1
    assert "test_report_stale_penalty=" in result.stdout
