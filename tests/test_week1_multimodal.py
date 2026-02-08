"""Tests for experiments.week1.multimodal — multi-modal sigma_Phi monitoring."""

from __future__ import annotations

import json

import numpy as np
import pytest

from experiments.week1.multimodal import (
    MultiModalResult,
    run_multimodal_experiment,
    run_scenarios,
    sigma_phi_from_logits,
)


# ---------------------------------------------------------------------------
# sigma_phi_from_logits
# ---------------------------------------------------------------------------


def test_sigma_phi_positive_for_nontrivial_input() -> None:
    logits = np.array([1.0, 2.0, 3.0, 4.0])
    assert sigma_phi_from_logits(logits) > 0.0


def test_sigma_phi_zero_for_constant_input() -> None:
    logits = np.array([5.0, 5.0, 5.0, 5.0])
    assert sigma_phi_from_logits(logits) == pytest.approx(0.0)


def test_sigma_phi_increases_with_spread() -> None:
    tight = sigma_phi_from_logits(np.array([10.0, 10.1, 9.9, 10.0]))
    wide = sigma_phi_from_logits(np.array([1.0, 20.0, 3.0, 18.0]))
    assert wide > tight


def test_sigma_phi_handles_near_zero_mean() -> None:
    """When mean is near zero, sigma_Phi should still be finite."""
    logits = np.array([-1.0, 1.0, -1.0, 1.0])
    result = sigma_phi_from_logits(logits)
    assert np.isfinite(result)


# ---------------------------------------------------------------------------
# run_scenarios (numpy fallback)
# ---------------------------------------------------------------------------


def test_scenarios_return_three_results() -> None:
    results = run_scenarios(force_numpy=True)
    assert len(results) == 3


def test_scenarios_cover_expected_names() -> None:
    results = run_scenarios(force_numpy=True)
    names = {r.scenario for r in results}
    assert names == {"aligned", "contradictory", "adversarial"}


def test_all_results_are_multimodal_result() -> None:
    results = run_scenarios(force_numpy=True)
    assert all(isinstance(r, MultiModalResult) for r in results)


def test_scenarios_deterministic_with_same_seed() -> None:
    r1 = run_scenarios(force_numpy=True, seed=123)
    r2 = run_scenarios(force_numpy=True, seed=123)
    for a, b in zip(r1, r2):
        assert a.sigma_phi == b.sigma_phi


def test_aligned_is_stable_adversarial_is_not() -> None:
    """In AFET, lower sigma_Phi = less stable. Aligned should be stable."""
    results = run_scenarios(force_numpy=True)
    by_name = {r.scenario: r for r in results}
    assert by_name["aligned"].safety_state == "stable"
    assert by_name["adversarial"].safety_state in ("warning", "critical")


# ---------------------------------------------------------------------------
# run_multimodal_experiment (integration)
# ---------------------------------------------------------------------------


def test_experiment_writes_json(tmp_path) -> None:
    payload = run_multimodal_experiment(output_dir=tmp_path, force_numpy=True)
    json_path = tmp_path / "week1_multimodal.json"
    assert json_path.exists()
    data = json.loads(json_path.read_text())
    assert data["backend"] == "numpy"
    assert len(data["scenarios"]) == 3


def test_experiment_payload_structure() -> None:
    payload = run_multimodal_experiment(force_numpy=True)
    assert "backend" in payload
    assert "scenarios" in payload
    for s in payload["scenarios"]:
        assert "scenario" in s
        assert "sigma_phi" in s
        assert "safety_state" in s
