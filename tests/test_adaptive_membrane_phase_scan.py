from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from analysis import adaptive_membrane_phase_scan as phase_scan


def test_run_scan_payload_consistency() -> None:
    payload = phase_scan.run_scan(seed=19, max_points=32)

    metadata = payload["metadata"]
    assert metadata["script"] == "analysis/adaptive_membrane_phase_scan.py"

    scenarios = payload["scenarios"]
    assert isinstance(scenarios, list)
    assert len(scenarios) == 3

    theta_shifts = []
    beta_shifts = []
    for entry in scenarios:
        summary = entry["summary"]
        samples = entry["samples"]

        assert 0.0 <= summary["gate_mean"] <= 1.0
        assert math.isfinite(summary["resonance_gain"])
        assert math.isfinite(summary["baseline_resonance_gain"])
        assert math.isfinite(summary["resonance_gain_delta"])
        assert 0.0 <= summary["sigma_fraction_above_half"] <= 1.0
        assert summary["steps"] >= len(samples["R"])
        assert len(samples["R"]) <= 32

        theta_shifts.append(summary["theta_shift"])
        beta_shifts.append(summary["beta_shift"])

    assert any(shift > 0 for shift in theta_shifts)
    assert any(shift >= 0 for shift in beta_shifts)

    aggregates = payload["aggregates"]
    assert aggregates["scenarios"] == len(scenarios)
    assert math.isfinite(aggregates["resonance_gain_mean"])
    assert math.isfinite(aggregates["resonance_gain_delta_mean"])


def test_cli_writes_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    output = tmp_path / "phase.json"
    phase_scan.main(["--output", str(output), "--max-points", "24", "--seed", "7"])

    captured = capsys.readouterr()
    assert "Adaptive membrane phase scan complete" in captured.out
    assert output.exists()

    with output.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    assert payload["aggregates"]["scenarios"] == 3
