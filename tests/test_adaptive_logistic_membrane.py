"""Tests for the adaptive logistic membrane plasticity helper."""

from __future__ import annotations

import numpy as np
import pytest

from models import AdaptiveLogisticMembrane


def test_propagate_adapts_threshold_and_beta() -> None:
    """Adaptive runs should nudge Theta upward and keep sigma within [0, 1]."""

    membrane = AdaptiveLogisticMembrane(theta=0.3, beta=4.5, meta_beta=5.0)
    control = np.linspace(0.1, 0.95, 80)

    history = membrane.propagate(control, dt=0.12)

    assert history["theta"].shape == control.shape
    assert history["beta"].shape == control.shape
    assert np.all(history["sigma"] >= 0.0)
    assert np.all(history["sigma"] <= 1.0)

    summary = membrane.summarise(history)
    assert summary["theta_shift"] > 0.0
    assert summary["gate_mean"] > 0.0
    assert summary["resonance_gain"] >= 0.0


def test_reset_restores_baselines_after_adaptation() -> None:
    """Reset should return the membrane to its remembered dawn state."""

    membrane = AdaptiveLogisticMembrane(theta=0.4, beta=6.0, meta_beta=4.4)
    control = np.linspace(0.2, 1.1, 60)
    membrane.propagate(control, dt=0.15)

    assert membrane.theta != pytest.approx(membrane.theta_baseline)
    assert membrane.beta != pytest.approx(membrane.beta_baseline)

    membrane.reset()

    assert membrane.theta == pytest.approx(membrane.theta_baseline)
    assert membrane.beta == pytest.approx(membrane.beta_baseline)
