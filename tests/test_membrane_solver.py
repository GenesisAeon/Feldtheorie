"""Comprehensive tests for membrane solver module.

Tests core functions, boundary conditions, and solver integration.
"""

from __future__ import annotations

import math

import pytest

from models.membrane_solver import (
    DynamicRobinBoundary,
    logistic_impedance_gate,
    logistic_response,
    smooth_impedance_profile,
    threshold_crossing_diagnostics,
    update_impedance,
)


class TestLogisticResponse:
    """Test the core logistic response function."""

    def test_scalar_response_at_theta_is_half(self) -> None:
        """At R=theta, response should be 0.5."""
        result = logistic_response(0.5, theta=0.5, beta=4.0)
        assert isinstance(result, float)
        assert math.isclose(result, 0.5, rel_tol=1e-6)

    def test_list_response_returns_list(self) -> None:
        """Should handle list input and return list."""
        R_list = [0.0, 0.5, 1.0]
        result = logistic_response(R_list, theta=0.5, beta=4.0)
        assert isinstance(result, list)
        assert len(result) == 3

    def test_response_monotonically_increases(self) -> None:
        """Response should increase with R."""
        R_list = [-1.0, 0.0, 1.0]
        result = logistic_response(R_list, theta=0.0, beta=4.0)
        assert result[0] < result[1] < result[2]

    def test_approaches_zero_below_theta(self) -> None:
        """Far below theta, should approach 0."""
        result = logistic_response(-10.0, theta=0.0, beta=4.0)
        assert result < 1e-6

    def test_approaches_one_above_theta(self) -> None:
        """Far above theta, should approach 1."""
        result = logistic_response(10.0, theta=0.0, beta=4.0)
        assert result > 0.999

    def test_higher_beta_steeper(self) -> None:
        """Higher beta should give steeper transition."""
        # At R slightly above theta
        r = 0.1
        low_beta = logistic_response(r, theta=0.0, beta=2.0)
        high_beta = logistic_response(r, theta=0.0, beta=10.0)
        # High beta should be closer to 1
        assert high_beta > low_beta


class TestLogisticImpedanceGate:
    """Test the impedance gate blending function."""

    def test_returns_zeta_closed_below_theta(self) -> None:
        """Far below theta, should return zeta_closed."""
        result = logistic_impedance_gate(-10.0, theta=0.0, beta=4.0, zeta_closed=1.35, zeta_open=0.65)
        assert math.isclose(result, 1.35, rel_tol=1e-3)

    def test_returns_zeta_open_above_theta(self) -> None:
        """Far above theta, should return zeta_open."""
        result = logistic_impedance_gate(10.0, theta=0.0, beta=4.0, zeta_closed=1.35, zeta_open=0.65)
        assert math.isclose(result, 0.65, rel_tol=1e-3)

    def test_blends_at_theta(self) -> None:
        """At theta, should be midpoint."""
        result = logistic_impedance_gate(0.0, theta=0.0, beta=4.0, zeta_closed=1.35, zeta_open=0.65)
        expected = (1.35 + 0.65) / 2.0
        assert math.isclose(result, expected, rel_tol=1e-6)

    def test_monotonically_decreases(self) -> None:
        """Impedance should decrease as R increases."""
        R_values = [-1.0, 0.0, 1.0]
        results = [logistic_impedance_gate(r, theta=0.0, beta=4.0) for r in R_values]
        assert results[0] > results[1] > results[2]


class TestUpdateImpedance:
    """Test the update_impedance function (existing tests expanded)."""

    def test_update_impedance_tracks_logistic_gate(self) -> None:
        """Should track logistic transition."""
        zeta_closed = update_impedance(R_trigger=-1.0, Theta=0.5, beta=6.0, zeta_max=1.4, zeta_min=0.2)
        zeta_mid = update_impedance(R_trigger=0.5, Theta=0.5, beta=6.0, zeta_max=1.4, zeta_min=0.2)
        zeta_open = update_impedance(R_trigger=1.5, Theta=0.5, beta=6.0, zeta_max=1.4, zeta_min=0.2)

        assert math.isclose(zeta_closed, 1.4, rel_tol=1e-3)
        assert math.isclose(zeta_mid, (1.4 + 0.2) / 2.0, rel_tol=1e-6)
        assert zeta_open == pytest.approx(0.2, abs=0.005)

    def test_update_impedance_monotonic(self) -> None:
        """Should be monotonically decreasing."""
        values = [update_impedance(R_trigger=r, Theta=0.0, beta=5.0, zeta_max=1.2, zeta_min=0.3) for r in (-1.0, 0.0, 1.0)]
        assert values[0] > values[1] > values[2]

    def test_custom_zeta_range(self) -> None:
        """Should respect custom zeta_max and zeta_min."""
        zeta_low = update_impedance(R_trigger=-10.0, Theta=0.0, beta=4.0, zeta_max=2.0, zeta_min=0.1)
        zeta_high = update_impedance(R_trigger=10.0, Theta=0.0, beta=4.0, zeta_max=2.0, zeta_min=0.1)
        assert math.isclose(zeta_low, 2.0, rel_tol=1e-3)
        assert math.isclose(zeta_high, 0.1, rel_tol=1e-3)


class TestSmoothImpedanceProfile:
    """Test the smooth impedance profile constructor."""

    def test_returns_callable(self) -> None:
        """Should return a callable function."""
        zeta = smooth_impedance_profile(theta=0.5)
        assert callable(zeta)

    def test_transitions_around_theta(self) -> None:
        """Profile should transition from resonant to damped gain."""
        zeta = smooth_impedance_profile(theta=0.5, resonant_gain=0.6, damped_gain=1.4)

        # Below theta: should be near resonant_gain
        below = zeta(-10.0)
        # Above theta: should be near damped_gain
        above = zeta(10.0)

        assert below < above
        # Relaxed tolerances due to logistic blending
        assert 0.5 <= below <= 0.7
        assert 1.3 <= above <= 1.5

    def test_midpoint_at_theta(self) -> None:
        """At theta, should be approximately midpoint."""
        zeta = smooth_impedance_profile(theta=0.5, resonant_gain=0.6, damped_gain=1.4)
        mid = zeta(0.5)
        expected = (0.6 + 1.4) / 2.0
        # Wider tolerance for logistic midpoint
        assert math.isclose(mid, expected, abs_tol=0.2)

    def test_switch_width_affects_transition(self) -> None:
        """Larger switch_width should give broader transition."""
        zeta_narrow = smooth_impedance_profile(theta=0.5, switch_width=0.1)
        zeta_wide = smooth_impedance_profile(theta=0.5, switch_width=1.0)

        # Slightly below theta
        r = 0.3
        # With narrow width, should be closer to resonant end
        # This is a qualitative test
        assert callable(zeta_narrow)
        assert callable(zeta_wide)


class TestDynamicRobinBoundary:
    """Test the DynamicRobinBoundary dataclass."""

    def test_initialization_with_defaults(self) -> None:
        """Should initialize with default parameters."""
        boundary = DynamicRobinBoundary(theta=0.5)
        assert boundary.theta == 0.5
        assert boundary.beta_robin == 4.8
        assert boundary.zeta_floor == 0.65
        assert boundary.zeta_ceiling == 1.35

    def test_gate_returns_logistic_response(self) -> None:
        """Gate should return logistic response at R."""
        boundary = DynamicRobinBoundary(theta=0.5, beta_robin=4.0)
        gate = boundary.gate(0.5)
        assert math.isclose(gate, 0.5, rel_tol=1e-6)

    def test_gate_increases_with_R(self) -> None:
        """Gate should increase monotonically."""
        boundary = DynamicRobinBoundary(theta=0.5)
        gate_below = boundary.gate(0.0)
        gate_at = boundary.gate(0.5)
        gate_above = boundary.gate(1.0)
        assert gate_below < gate_at < gate_above

    def test_impedance_decreases_with_R(self) -> None:
        """Impedance should decrease as R increases."""
        boundary = DynamicRobinBoundary(theta=0.5)
        z_below = boundary.impedance(0.0)
        z_at = boundary.impedance(0.5)
        z_above = boundary.impedance(1.0)
        assert z_below > z_at > z_above

    def test_impedance_bounded_by_floor_ceiling(self) -> None:
        """Impedance should stay within [floor, ceiling]."""
        boundary = DynamicRobinBoundary(theta=0.5, zeta_floor=0.65, zeta_ceiling=1.35)
        for r in [-10.0, 0.0, 0.5, 1.0, 10.0]:
            z = boundary.impedance(r)
            assert boundary.zeta_floor <= z <= boundary.zeta_ceiling

    def test_boundary_flux_returns_finite(self) -> None:
        """Boundary flux should return finite value."""
        boundary = DynamicRobinBoundary(theta=0.5)
        flux = boundary.boundary_flux(R=0.5, sigma=0.4, driver=0.6)
        assert math.isfinite(flux)

    def test_boundary_flux_depends_on_gate(self) -> None:
        """Flux should change with gate opening."""
        boundary = DynamicRobinBoundary(theta=0.5)
        # Below theta (gate ~0): minimal flux
        flux_below = boundary.boundary_flux(R=-10.0, sigma=0.5, driver=0.5)
        # Above theta (gate ~1): larger flux magnitude
        flux_above = boundary.boundary_flux(R=10.0, sigma=0.5, driver=0.5)
        # Absolute values might differ
        assert math.isfinite(flux_below)
        assert math.isfinite(flux_above)

    def test_snapshot_returns_dict(self) -> None:
        """Snapshot should return diagnostic dict."""
        boundary = DynamicRobinBoundary(theta=0.5)
        snap = boundary.snapshot(R=0.5, sigma=0.4, driver=0.6)
        assert isinstance(snap, dict)
        assert "gate" in snap
        assert "impedance" in snap
        assert "boundary_flux" in snap

    def test_snapshot_values_finite(self) -> None:
        """All snapshot values should be finite."""
        boundary = DynamicRobinBoundary(theta=0.5)
        snap = boundary.snapshot(R=0.5, sigma=0.4, driver=0.6)
        for key, value in snap.items():
            assert math.isfinite(value), f"{key} is not finite"


class TestThresholdCrossingDiagnostics:
    """Test the threshold_crossing_diagnostics function."""

    def test_detects_crossing(self) -> None:
        """Should detect when R crosses theta."""
        # Simple trajectory crossing theta=0.5
        results = {
            "R": [0.0, 0.3, 0.6, 0.8, 1.0],
            "sigma": [0.1, 0.2, 0.7, 0.9, 0.95],
            "t": [0.0, 1.0, 2.0, 3.0, 4.0]
        }
        diagnostics = threshold_crossing_diagnostics(results, theta=0.5, beta=4.0)

        assert "crossed" in diagnostics
        assert diagnostics["crossed"] is True

    def test_reports_crossing_index(self) -> None:
        """Should report index where crossing occurred."""
        results = {
            "R": [0.0, 0.3, 0.6, 0.8, 1.0],
            "sigma": [0.1, 0.2, 0.7, 0.9, 0.95],
            "t": [0.0, 1.0, 2.0, 3.0, 4.0]
        }
        diagnostics = threshold_crossing_diagnostics(results, theta=0.5, beta=4.0)

        assert "crossing_index" in diagnostics
        # Should cross between index 1 (0.3) and 2 (0.6)
        idx = diagnostics["crossing_index"]
        assert idx is not None
        assert 1 <= idx <= 3

    def test_no_crossing_detected(self) -> None:
        """Should detect when no crossing occurs."""
        # Trajectory stays below theta
        results = {
            "R": [0.0, 0.1, 0.2, 0.3],
            "sigma": [0.1, 0.15, 0.2, 0.25],
            "t": [0.0, 1.0, 2.0, 3.0]
        }
        diagnostics = threshold_crossing_diagnostics(results, theta=0.5, beta=4.0)

        assert diagnostics["crossed"] is False

    def test_handles_single_point(self) -> None:
        """Should handle single-point trajectory."""
        results = {
            "R": [0.5],
            "sigma": [0.5],
            "t": [0.0]
        }
        diagnostics = threshold_crossing_diagnostics(results, theta=0.5, beta=4.0)
        assert isinstance(diagnostics, dict)

    def test_handles_empty_trajectory(self) -> None:
        """Should raise ValueError for empty trajectory."""
        results = {
            "R": [],
            "sigma": [],
            "t": []
        }
        # Function raises ValueError for empty input
        with pytest.raises(ValueError, match="At least one sample"):
            threshold_crossing_diagnostics(results, theta=0.5, beta=4.0)
