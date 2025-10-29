"""Tests for the ResonantImpedance motif's logistic breathing."""

import numpy as np
import pytest

from models import ResonantImpedance


def test_impedance_relief_activates_when_threshold_crossed() -> None:
    motif = ResonantImpedance(theta=0.4, beta=9.0, baseline=0.82, floor=0.18)
    control = np.linspace(0.0, 1.0, 64)

    history = motif.trace(control)

    assert history["gate"].max() > 0.5
    assert history["zeta"][-1] < motif.baseline
    assert np.max(history["relief"]) > 0.0


def test_impedance_recovers_after_relief() -> None:
    motif = ResonantImpedance(theta=0.45, beta=8.5, baseline=0.86, floor=0.2)

    motif.trace(np.linspace(0.3, 0.95, 32))
    recovery_history = motif.trace(np.full(48, 0.2))

    end = recovery_history["zeta"][-1]
    target_band = motif.floor + 0.6 * (motif.baseline - motif.floor)
    assert end > target_band
    assert np.isclose(end, motif.current_impedance)
    assert np.mean(recovery_history["recovery"]) > 0.0


def test_call_matches_trace_output() -> None:
    motif = ResonantImpedance(theta=0.5, beta=7.5, baseline=0.78, floor=0.16)
    samples = [0.2, 0.4, 0.8, 0.6]

    trace_history = motif.trace(samples)
    motif.reset()
    direct = motif(samples)

    np.testing.assert_allclose(direct, trace_history["zeta"])
