"""Comprehensive tests for ResonantImpedance motif.

Tests initialization, impedance breathing dynamics, trace generation,
summarization, and edge cases.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from models import ResonantImpedance


class TestResonantImpedanceInit:
    """Test initialization and basic properties."""

    def test_initialization_with_defaults(self) -> None:
        """Should initialize with default parameters."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)
        assert motif.theta == 0.5
        assert motif.beta == 8.0
        assert motif.relief_gain == 0.65
        assert motif.recovery_rate == 0.18
        assert motif.hysteresis == 0.3
        assert motif.baseline == 0.84
        assert motif.floor == 0.12
        assert motif.ceiling == 1.08

    def test_initialization_with_custom_params(self) -> None:
        """Should accept custom parameters."""
        motif = ResonantImpedance(
            theta=0.4,
            beta=9.0,
            relief_gain=0.7,
            recovery_rate=0.2,
            hysteresis=0.4,
            baseline=0.9,
            floor=0.15,
            ceiling=1.2,
        )
        assert motif.theta == 0.4
        assert motif.beta == 9.0
        assert motif.relief_gain == 0.7
        assert motif.recovery_rate == 0.2
        assert motif.hysteresis == 0.4
        assert motif.baseline == 0.9
        assert motif.floor == 0.15
        assert motif.ceiling == 1.2

    def test_post_init_clips_baseline(self) -> None:
        """Post-init should clip baseline to [floor, ceiling]."""
        # Baseline above ceiling
        motif1 = ResonantImpedance(theta=0.5, beta=8.0, baseline=2.0, ceiling=1.0)
        assert motif1.baseline == 1.0

        # Baseline below floor
        motif2 = ResonantImpedance(theta=0.5, beta=8.0, baseline=0.0, floor=0.2)
        assert motif2.baseline == 0.2

    def test_post_init_sets_state_to_baseline(self) -> None:
        """Initial state should equal baseline."""
        motif = ResonantImpedance(theta=0.5, beta=8.0, baseline=0.75)
        assert motif.current_impedance == 0.75


class TestCurrentImpedance:
    """Test the current_impedance property."""

    def test_current_impedance_returns_state(self) -> None:
        """Should return internal state."""
        motif = ResonantImpedance(theta=0.5, beta=8.0, baseline=0.8)
        assert motif.current_impedance == 0.8

    def test_current_impedance_updates_after_trace(self) -> None:
        """Should reflect updated state after trace."""
        motif = ResonantImpedance(theta=0.5, beta=8.0, baseline=0.8)
        initial = motif.current_impedance
        motif.trace([0.0, 1.0])
        after = motif.current_impedance
        assert initial != after  # State should change


class TestReset:
    """Test the reset method."""

    def test_reset_restores_baseline(self) -> None:
        """Reset should restore impedance to baseline."""
        motif = ResonantImpedance(theta=0.5, beta=8.0, baseline=0.8)
        motif.trace([0.0, 1.0])  # Change state
        motif.reset()
        assert motif.current_impedance == 0.8

    def test_reset_clears_gate_memory(self) -> None:
        """Reset should clear gate history."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)
        motif.trace([1.0])  # Open gate
        motif.reset()
        assert motif._last_gate == 0.0


class TestTrace:
    """Test the trace method."""

    def test_trace_returns_expected_keys(self) -> None:
        """Trace should return all expected arrays."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)
        control = [0.0, 0.5, 1.0]
        history = motif.trace(control)

        expected_keys = {"R", "zeta", "gate", "relief", "recovery", "hysteresis"}
        assert set(history.keys()) == expected_keys

    def test_trace_arrays_same_length(self) -> None:
        """All arrays should have same length as input."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)
        control = np.linspace(0.0, 1.0, 50)
        history = motif.trace(control)

        assert len(history["R"]) == 50
        assert len(history["zeta"]) == 50
        assert len(history["gate"]) == 50
        assert len(history["relief"]) == 50
        assert len(history["recovery"]) == 50
        assert len(history["hysteresis"]) == 50

    def test_trace_gate_opens_above_theta(self) -> None:
        """Gate should open when R crosses theta."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)
        control = np.linspace(0.0, 1.0, 100)
        history = motif.trace(control)

        # Gate should be near 0 at R=0 and near 1 at R=1
        assert history["gate"][0] < 0.1
        assert history["gate"][-1] > 0.9

    def test_trace_impedance_drops_above_theta(self) -> None:
        """Impedance should decrease when gate opens."""
        motif = ResonantImpedance(theta=0.5, beta=8.0, baseline=0.8, floor=0.2)
        control = np.linspace(0.0, 1.0, 100)
        history = motif.trace(control)

        # Impedance should drop from baseline toward floor
        assert history["zeta"][-1] < motif.baseline

    def test_trace_relief_activates_when_gate_opens(self) -> None:
        """Relief force should activate above theta."""
        motif = ResonantImpedance(theta=0.4, beta=9.0)
        control = np.linspace(0.0, 1.0, 64)
        history = motif.trace(control)

        assert history["gate"].max() > 0.5
        assert np.max(history["relief"]) > 0.0

    def test_trace_recovery_activates_when_gate_closes(self) -> None:
        """Recovery force should activate when returning."""
        motif = ResonantImpedance(theta=0.45, beta=8.5)
        # Ramp up then down
        control = list(np.linspace(0.3, 0.95, 32)) + list(np.linspace(0.95, 0.2, 48))
        history = motif.trace(control)

        # Recovery should be active in second half
        recovery_second_half = history["recovery"][40:]
        assert np.mean(recovery_second_half) > 0.0

    def test_trace_respects_dt_parameter(self) -> None:
        """Different dt should produce different dynamics."""
        motif1 = ResonantImpedance(theta=0.5, beta=8.0)
        motif2 = ResonantImpedance(theta=0.5, beta=8.0)
        control = [0.0, 1.0]

        history1 = motif1.trace(control, dt=0.1)
        history2 = motif2.trace(control, dt=1.0)

        # Different dt should produce different trajectories
        assert not np.allclose(history1["zeta"], history2["zeta"])

    def test_trace_clips_to_floor_and_ceiling(self) -> None:
        """Impedance should stay within [floor, ceiling]."""
        motif = ResonantImpedance(theta=0.5, beta=8.0, floor=0.1, ceiling=1.0)
        control = np.linspace(0.0, 1.0, 100)
        history = motif.trace(control)

        assert np.all(history["zeta"] >= motif.floor)
        assert np.all(history["zeta"] <= motif.ceiling)

    def test_trace_updates_internal_state(self) -> None:
        """Trace should update internal impedance state."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)
        control = [0.5, 1.0]
        history = motif.trace(control)

        assert math.isclose(motif.current_impedance, history["zeta"][-1])

    def test_trace_with_numpy_array(self) -> None:
        """Should accept numpy array as input."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)
        control = np.array([0.0, 0.5, 1.0])
        history = motif.trace(control)

        assert len(history["zeta"]) == 3

    def test_trace_with_list(self) -> None:
        """Should accept list as input."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)
        control = [0.0, 0.5, 1.0]
        history = motif.trace(control)

        assert len(history["zeta"]) == 3


class TestCallable:
    """Test the __call__ method."""

    def test_call_returns_zeta_array(self) -> None:
        """Calling motif should return impedance array."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)
        control = [0.0, 0.5, 1.0]
        zeta = motif(control)

        assert isinstance(zeta, np.ndarray)
        assert len(zeta) == 3

    def test_call_matches_trace_zeta(self) -> None:
        """Call result should match trace zeta."""
        motif = ResonantImpedance(theta=0.5, beta=7.5)
        control = [0.2, 0.4, 0.8, 0.6]

        trace_history = motif.trace(control)
        motif.reset()
        direct = motif(control)

        np.testing.assert_allclose(direct, trace_history["zeta"])


class TestSummarise:
    """Test the summarise method."""

    def test_summarise_returns_expected_keys(self) -> None:
        """Summarise should return all expected metrics."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)
        control = np.linspace(0.0, 1.0, 50)
        history = motif.trace(control)
        summary = motif.summarise(history)

        expected_keys = {
            "theta",
            "beta",
            "zeta_mean",
            "zeta_min",
            "zeta_max",
            "gate_mean",
            "gate_area",
            "impedance_area",
            "relief_area",
            "recovery_area",
            "hysteresis_area",
            "relief_recovery_balance",
            "relief_recovery_ratio",
            "relief_recovery_symmetry",
            "hysteresis_bias",
            "relief_peak",
            "recovery_peak",
            "hysteresis_peak",
            "final_impedance",
            "baseline_impedance",
        }
        assert set(summary.keys()) == expected_keys

    def test_summarise_values_finite(self) -> None:
        """All summary values should be finite or None."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)
        control = np.linspace(0.0, 1.0, 50)
        history = motif.trace(control)
        summary = motif.summarise(history)

        for key, value in summary.items():
            if value is not None:
                assert math.isfinite(value), f"{key} is not finite"

    def test_summarise_theta_beta_match(self) -> None:
        """Summarised theta and beta should match motif."""
        motif = ResonantImpedance(theta=0.7, beta=9.0)
        control = [0.5, 1.0]
        history = motif.trace(control)
        summary = motif.summarise(history)

        assert summary["theta"] == 0.7
        assert summary["beta"] == 9.0

    def test_summarise_zeta_min_max_valid(self) -> None:
        """zeta_min should be <= zeta_max."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)
        control = np.linspace(0.0, 1.0, 50)
        history = motif.trace(control)
        summary = motif.summarise(history)

        assert summary["zeta_min"] <= summary["zeta_max"]

    def test_summarise_can_update_existing_dict(self) -> None:
        """Should update existing dictionary if provided."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)
        control = [0.5, 1.0]
        history = motif.trace(control)

        existing = {"custom_key": 42}
        summary = motif.summarise(history, store=existing)

        assert summary["custom_key"] == 42
        assert "theta" in summary
        assert summary is existing  # Should be same object

    def test_summarise_with_single_point(self) -> None:
        """Should handle single-point trace."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)
        control = [0.5]
        history = motif.trace(control)
        summary = motif.summarise(history)

        # Should not crash
        assert math.isfinite(summary["zeta_mean"])

    def test_summarise_relief_recovery_ratio_none_when_zero_recovery(self) -> None:
        """Ratio should be None when recovery is zero."""
        motif = ResonantImpedance(theta=0.5, beta=8.0, recovery_rate=0.0)
        control = [1.0, 1.0, 1.0]  # All above theta
        history = motif.trace(control)
        summary = motif.summarise(history)

        # If recovery is truly zero, ratio should be None
        if abs(summary["recovery_area"]) < 1e-12:
            assert summary["relief_recovery_ratio"] is None


class TestLogisticHelper:
    """Test the internal _logistic helper."""

    def test_logistic_at_theta_is_half(self) -> None:
        """Logistic should be 0.5 at theta."""
        from models.resonant_impedance import _logistic

        result = _logistic(0.5, theta=0.5, beta=8.0)
        assert math.isclose(result, 0.5, abs_tol=1e-6)

    def test_logistic_below_theta_is_small(self) -> None:
        """Logistic should be near 0 below theta."""
        from models.resonant_impedance import _logistic

        result = _logistic(0.0, theta=0.5, beta=8.0)
        assert result < 0.1

    def test_logistic_above_theta_is_large(self) -> None:
        """Logistic should be near 1 above theta."""
        from models.resonant_impedance import _logistic

        result = _logistic(1.0, theta=0.5, beta=8.0)
        assert result > 0.9


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_motif_with_zero_relief_gain(self) -> None:
        """Should handle zero relief gain."""
        motif = ResonantImpedance(theta=0.5, beta=8.0, relief_gain=0.0)
        control = [0.0, 1.0]
        history = motif.trace(control)
        # Impedance shouldn't drop much with zero relief
        assert all(math.isfinite(v) for v in history["zeta"])

    def test_motif_with_zero_recovery_rate(self) -> None:
        """Should handle zero recovery rate."""
        motif = ResonantImpedance(theta=0.5, beta=8.0, recovery_rate=0.0)
        control = [0.0, 0.5, 1.0]
        history = motif.trace(control)
        assert all(math.isfinite(v) for v in history["zeta"])

    def test_motif_with_zero_hysteresis(self) -> None:
        """Should handle zero hysteresis."""
        motif = ResonantImpedance(theta=0.5, beta=8.0, hysteresis=0.0)
        control = [0.0, 1.0]
        history = motif.trace(control)
        # All hysteresis forces should be zero
        assert all(abs(v) < 1e-10 for v in history["hysteresis"])

    def test_motif_with_very_large_beta(self) -> None:
        """Should handle very steep logistic."""
        motif = ResonantImpedance(theta=0.5, beta=50.0)
        control = np.linspace(0.0, 1.0, 50)
        history = motif.trace(control)
        assert all(math.isfinite(v) for v in history["zeta"])

    def test_motif_with_baseline_equals_floor(self) -> None:
        """Should handle baseline == floor."""
        motif = ResonantImpedance(theta=0.5, beta=8.0, baseline=0.2, floor=0.2)
        control = [0.5, 1.0]
        history = motif.trace(control)
        assert all(v >= motif.floor for v in history["zeta"])

    def test_trace_with_empty_input(self) -> None:
        """Should handle empty input."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)
        history = motif.trace([])

        assert len(history["zeta"]) == 0

    def test_trace_with_single_value(self) -> None:
        """Should handle single value input."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)
        history = motif.trace([0.5])

        assert len(history["zeta"]) == 1
        assert math.isfinite(history["zeta"][0])

    def test_trace_with_constant_control(self) -> None:
        """Should handle constant control parameter."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)
        control = [0.5] * 20
        history = motif.trace(control)

        # Should converge to some steady state
        assert all(math.isfinite(v) for v in history["zeta"])


class TestRealWorldScenarios:
    """Test realistic usage scenarios."""

    def test_impedance_relief_activates_when_threshold_crossed(self) -> None:
        """Relief should activate when crossing threshold."""
        motif = ResonantImpedance(theta=0.4, beta=9.0, baseline=0.82, floor=0.18)
        control = np.linspace(0.0, 1.0, 64)
        history = motif.trace(control)

        assert history["gate"].max() > 0.5
        assert history["zeta"][-1] < motif.baseline
        assert np.max(history["relief"]) > 0.0

    def test_impedance_recovers_after_relief(self) -> None:
        """Impedance should recover when returning below theta."""
        motif = ResonantImpedance(theta=0.45, beta=8.5, baseline=0.86, floor=0.2)

        # First sweep: activate relief
        motif.trace(np.linspace(0.3, 0.95, 32))

        # Second sweep: recovery phase
        recovery_history = motif.trace(np.full(48, 0.2))

        end = recovery_history["zeta"][-1]
        target_band = motif.floor + 0.6 * (motif.baseline - motif.floor)
        assert end > target_band
        assert np.isclose(end, motif.current_impedance)
        assert np.mean(recovery_history["recovery"]) > 0.0

    def test_successive_traces_accumulate_state(self) -> None:
        """Multiple traces should accumulate state changes."""
        motif = ResonantImpedance(theta=0.5, beta=8.0)

        motif.trace([0.0])
        state1 = motif.current_impedance

        motif.trace([1.0])
        state2 = motif.current_impedance

        motif.trace([0.5])
        state3 = motif.current_impedance

        # States should progressively differ
        assert state1 != state2
        assert state2 != state3
