"""Tests for experiments.week1.adversarial — beta-spike adversarial detection."""

from __future__ import annotations

import json

import numpy as np
import pytest
from experiments.week1.adversarial import (
    REFERENCE_DIMENSION,
    SPIKE_THRESHOLD,
    AdversarialProbe,
    beta_spike_score,
    estimate_beta_from_outputs,
    run_adversarial_experiment,
    run_adversarial_probes,
)
from theory.afet import AFETFramework

# ---------------------------------------------------------------------------
# estimate_beta_from_outputs
# ---------------------------------------------------------------------------


def test_nominal_logits_yield_near_expected_beta() -> None:
    """Tight logits near sigma_Phi=0.0625 -> beta near predict_beta(1.0)."""
    framework = AFETFramework()
    expected = framework.predict_beta(REFERENCE_DIMENSION)
    # Construct logits with CV ~ 0.0625
    logits = np.array([10.0, 10.1, 9.9, 10.05])
    beta = estimate_beta_from_outputs(logits, framework)
    # Should be in the same ballpark (within 50%)
    assert abs(beta - expected) / expected < 0.5


def test_high_variance_logits_yield_higher_beta() -> None:
    framework = AFETFramework()
    tight = estimate_beta_from_outputs(np.array([10.0, 10.1, 9.9, 10.0]), framework)
    wide = estimate_beta_from_outputs(np.array([1.0, 20.0, 3.0, 18.0]), framework)
    assert wide > tight


def test_beta_always_positive() -> None:
    beta = estimate_beta_from_outputs(np.array([0.0, 0.0, 0.0, 0.0]))
    assert beta >= 0.0


# ---------------------------------------------------------------------------
# beta_spike_score
# ---------------------------------------------------------------------------


def test_spike_score_one_when_equal() -> None:
    assert beta_spike_score(7.0, 7.0) == pytest.approx(1.0)


def test_spike_score_above_one_when_observed_exceeds() -> None:
    assert beta_spike_score(10.0, 7.0) > 1.0


def test_spike_score_below_one_when_observed_lower() -> None:
    assert beta_spike_score(5.0, 7.0) < 1.0


# ---------------------------------------------------------------------------
# run_adversarial_probes (numpy fallback)
# ---------------------------------------------------------------------------


def test_probes_return_five_results() -> None:
    """3 FGSM epsilons + 1 semantic + 1 nonsense = 5."""
    probes = run_adversarial_probes(force_numpy=True)
    assert len(probes) == 5


def test_all_probes_are_adversarial_probe() -> None:
    probes = run_adversarial_probes(force_numpy=True)
    assert all(isinstance(p, AdversarialProbe) for p in probes)


def test_semantic_shift_is_not_spike() -> None:
    probes = run_adversarial_probes(force_numpy=True)
    semantic = [p for p in probes if p.name == "semantic_shift"]
    assert len(semantic) == 1
    assert not semantic[0].is_spike


def test_probes_deterministic() -> None:
    p1 = run_adversarial_probes(force_numpy=True, seed=99)
    p2 = run_adversarial_probes(force_numpy=True, seed=99)
    for a, b in zip(p1, p2, strict=True):
        assert a.beta_observed == b.beta_observed


# ---------------------------------------------------------------------------
# run_adversarial_experiment (integration)
# ---------------------------------------------------------------------------


def test_experiment_writes_json(tmp_path) -> None:
    run_adversarial_experiment(output_dir=tmp_path, force_numpy=True)
    path = tmp_path / "week1_adversarial.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["backend"] == "numpy"
    assert len(data["probes"]) == 5


def test_experiment_payload_structure() -> None:
    payload = run_adversarial_experiment(force_numpy=True)
    assert "spike_threshold" in payload
    assert payload["spike_threshold"] == SPIKE_THRESHOLD
    for p in payload["probes"]:
        assert "spike_score" in p
        assert "is_spike" in p
        assert "safety_state" in p
