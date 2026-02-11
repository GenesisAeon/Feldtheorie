"""Tests for experiments.week2.multimodal_stress_test."""

from __future__ import annotations

import json

import numpy as np
import pytest

from experiments.week2.multimodal_stress_test import (
    StressProbe,
    StressTestReport,
    run_stress_test,
    run_stress_test_experiment,
    sigma_phi_from_logits,
)


# ---------------------------------------------------------------------------
# Basic execution
# ---------------------------------------------------------------------------


def test_stress_test_runs() -> None:
    probes, report = run_stress_test(probes_per_scenario=10, force_numpy=True)
    assert len(probes) == 50  # 5 scenarios * 10 probes each
    assert report.total_probes == 50


def test_stress_test_deterministic() -> None:
    p1, r1 = run_stress_test(probes_per_scenario=10, force_numpy=True, seed=42)
    p2, r2 = run_stress_test(probes_per_scenario=10, force_numpy=True, seed=42)
    for a, b in zip(p1, p2):
        assert a.sigma_phi_local == b.sigma_phi_local


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------


def test_all_scenarios_present() -> None:
    probes, report = run_stress_test(probes_per_scenario=5, force_numpy=True)
    scenario_names = {p.scenario for p in probes}
    expected = {
        "contradiction_pairs",
        "adversarial_attacks",
        "semantic_shifts",
        "cross_lingual",
        "noise_resilience",
    }
    assert scenario_names == expected


def test_adversarial_flag_set_correctly() -> None:
    probes, _ = run_stress_test(probes_per_scenario=5, force_numpy=True)
    for p in probes:
        if p.scenario in ("contradiction_pairs", "adversarial_attacks", "noise_resilience"):
            assert p.is_adversarial is True
        else:
            assert p.is_adversarial is False


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def test_detection_accuracy_in_range() -> None:
    _, report = run_stress_test(probes_per_scenario=50, force_numpy=True)
    assert 0.0 <= report.detection_accuracy <= 1.0


def test_false_positive_rate_in_range() -> None:
    _, report = run_stress_test(probes_per_scenario=50, force_numpy=True)
    assert 0.0 <= report.false_positive_rate <= 1.0


def test_sigma_phi_cross_positive() -> None:
    _, report = run_stress_test(probes_per_scenario=20, force_numpy=True)
    assert report.sigma_phi_cross > 0.0


def test_response_time_recorded() -> None:
    probes, report = run_stress_test(probes_per_scenario=10, force_numpy=True)
    assert report.mean_response_time_ms >= 0.0
    for p in probes:
        assert p.response_time_ms >= 0.0


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


def test_probes_are_stress_probe_type() -> None:
    probes, _ = run_stress_test(probes_per_scenario=5, force_numpy=True)
    assert all(isinstance(p, StressProbe) for p in probes)


def test_safety_states_valid() -> None:
    probes, _ = run_stress_test(probes_per_scenario=10, force_numpy=True)
    valid = {"stable", "warning", "critical"}
    for p in probes:
        assert p.safety_state in valid


# ---------------------------------------------------------------------------
# Integration
# ---------------------------------------------------------------------------


def test_experiment_writes_json(tmp_path) -> None:
    payload = run_stress_test_experiment(
        output_dir=tmp_path,
        probes_per_scenario=5,
        force_numpy=True,
    )
    json_path = tmp_path / "stress_test.json"
    assert json_path.exists()
    data = json.loads(json_path.read_text())
    assert data["report"]["total_probes"] == 25


def test_experiment_payload_has_report() -> None:
    payload = run_stress_test_experiment(probes_per_scenario=5, force_numpy=True)
    assert "report" in payload
    assert "elapsed_seconds" in payload
