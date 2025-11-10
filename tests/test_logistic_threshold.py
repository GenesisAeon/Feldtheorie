"""Comprehensive tests for logistic threshold membrane module.

Ensures ThresholdMembrane class correctly implements logistic resonance,
null model comparisons, and summary export functionality.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from models.logistic_threshold import ThresholdMembrane, _default_impedance


class TestDefaultImpedance:
    """Test the default unity impedance field."""

    def test_returns_ones_for_scalar_like_input(self) -> None:
        """Unity impedance should return array of ones."""
        r = np.array([0.0, 0.5, 1.0])
        result = _default_impedance(r)
        np.testing.assert_array_equal(result, np.ones(3))

    def test_preserves_input_shape(self) -> None:
        """Output shape should match input shape."""
        r = np.linspace(-1.0, 1.0, 50)
        result = _default_impedance(r)
        assert result.shape == r.shape


class TestThresholdMembraneResponse:
    """Test the core logistic response method."""

    def test_response_at_theta_is_half_max(self) -> None:
        """Logistic function should equal 0.5 at R = theta."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.2)
        r = np.array([0.5])
        result = membrane.response(r)
        assert math.isclose(result[0], 0.5, rel_tol=1e-6)

    def test_response_increases_monotonically(self) -> None:
        """Response should increase as R increases."""
        membrane = ThresholdMembrane(theta=0.0, beta=5.0)
        r = np.linspace(-2.0, 2.0, 50)
        result = membrane.response(r)
        # Check monotonicity: each element should be >= previous
        assert np.all(np.diff(result) >= 0)

    def test_response_approaches_zero_below_threshold(self) -> None:
        """Far below theta, response should approach 0."""
        membrane = ThresholdMembrane(theta=0.0, beta=4.0)
        r = np.array([-10.0])
        result = membrane.response(r)
        assert result[0] < 1e-6

    def test_response_approaches_one_above_threshold(self) -> None:
        """Far above theta, response should approach 1."""
        membrane = ThresholdMembrane(theta=0.0, beta=4.0)
        r = np.array([10.0])
        result = membrane.response(r)
        assert result[0] > 0.999

    def test_higher_beta_gives_steeper_transition(self) -> None:
        """Higher beta should result in sharper sigmoid."""
        r = np.linspace(-1.0, 1.0, 100)
        membrane_low = ThresholdMembrane(theta=0.0, beta=2.0)
        membrane_high = ThresholdMembrane(theta=0.0, beta=10.0)

        response_low = membrane_low.response(r)
        response_high = membrane_high.response(r)

        # High beta should have steeper gradient at theta
        # Measure width at half-max: narrower = steeper
        half_max_low = np.sum((response_low > 0.25) & (response_low < 0.75))
        half_max_high = np.sum((response_high > 0.25) & (response_high < 0.75))
        assert half_max_high < half_max_low

    def test_custom_impedance_modulates_response(self) -> None:
        """Custom impedance function should scale the response."""
        def half_impedance(r: np.ndarray) -> np.ndarray:
            return 0.5 * np.ones_like(r)

        membrane = ThresholdMembrane(theta=0.0, beta=4.0, zeta=half_impedance)
        r = np.array([10.0])  # Far above threshold
        result = membrane.response(r)
        # Response should be ~0.5 instead of ~1.0 due to impedance
        assert math.isclose(result[0], 0.5, rel_tol=1e-2)

    def test_accepts_list_input(self) -> None:
        """Method should accept lists, not just numpy arrays."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.0)
        r_list = [0.0, 0.5, 1.0]
        result = membrane.response(r_list)
        assert isinstance(result, np.ndarray)
        assert len(result) == 3

    def test_empty_input_returns_empty_array(self) -> None:
        """Empty input should return empty output."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.0)
        result = membrane.response([])
        assert len(result) == 0


class TestNullBaseline:
    """Test the static null baseline method."""

    def test_null_baseline_is_smooth(self) -> None:
        """Null baseline should be monotonically increasing."""
        r = np.linspace(-1.0, 1.0, 100)
        null = ThresholdMembrane.null_baseline(r)
        # Check smoothness via monotonicity
        assert np.all(np.diff(null) >= 0)

    def test_null_baseline_normalized(self) -> None:
        """Null baseline should be normalized to [0, 1] range."""
        r = np.linspace(-2.0, 2.0, 100)
        null = ThresholdMembrane.null_baseline(r)
        assert np.min(null) >= 0.0
        assert np.max(null) <= 1.0

    def test_null_baseline_accepts_list(self) -> None:
        """Should accept list input."""
        r_list = [0.0, 0.5, 1.0]
        result = ThresholdMembrane.null_baseline(r_list)
        assert isinstance(result, np.ndarray)
        assert len(result) == 3

    def test_null_baseline_single_point(self) -> None:
        """Should handle single point gracefully."""
        r = [0.5]
        result = ThresholdMembrane.null_baseline(r)
        assert len(result) == 1
        # With single point, centered=0, so result should be 0.5
        assert 0.0 <= result[0] <= 1.0


class TestCompareAgainstNull:
    """Test the compare_against_null method."""

    def test_returns_all_expected_keys(self) -> None:
        """Output should contain all required keys."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.2)
        r = np.linspace(0.0, 1.0, 50)
        result = membrane.compare_against_null(r)

        expected_keys = {"R", "logistic", "null", "resonance_gain", "half_max_index"}
        assert set(result.keys()) == expected_keys

    def test_R_matches_input(self) -> None:
        """Returned R should match input."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.2)
        r = np.linspace(0.0, 1.0, 20)
        result = membrane.compare_against_null(r)
        np.testing.assert_array_almost_equal(result["R"], r)

    def test_resonance_gain_is_positive(self) -> None:
        """Resonance gain should be positive."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.2)
        r = np.linspace(0.0, 1.0, 50)
        result = membrane.compare_against_null(r)
        assert result["resonance_gain"] > 0

    def test_resonance_gain_is_finite(self) -> None:
        """Resonance gain should be finite."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.2)
        r = np.linspace(0.0, 1.0, 50)
        result = membrane.compare_against_null(r)
        assert math.isfinite(result["resonance_gain"])

    def test_half_max_index_within_bounds(self) -> None:
        """Half-max index should be valid array index."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.2)
        r = np.linspace(0.0, 1.0, 50)
        result = membrane.compare_against_null(r)
        idx = result["half_max_index"]
        assert 0 <= idx < len(r)

    def test_half_max_index_near_theta(self) -> None:
        """Half-max crossing should occur near theta."""
        membrane = ThresholdMembrane(theta=0.5, beta=6.0)
        r = np.linspace(0.0, 1.0, 100)
        result = membrane.compare_against_null(r)
        idx = result["half_max_index"]
        crossing_R = r[idx]
        # Should be close to theta (within 0.1 for beta=6)
        assert abs(crossing_R - 0.5) < 0.1

    def test_logistic_and_null_arrays_same_length(self) -> None:
        """Logistic and null arrays should match input length."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.2)
        r = np.linspace(0.0, 1.0, 75)
        result = membrane.compare_against_null(r)
        assert len(result["logistic"]) == len(r)
        assert len(result["null"]) == len(r)


class TestExportSummary:
    """Test the export_summary method."""

    def test_returns_dict_with_expected_keys(self) -> None:
        """Summary should contain all required fields."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.2)
        r = np.linspace(0.0, 1.0, 50)
        summary = membrane.export_summary(r)

        expected = {
            "R_min", "R_max", "theta", "beta",
            "zeta_mean", "resonance_gain", "half_max_index"
        }
        assert set(summary.keys()) == expected

    def test_R_min_max_correct(self) -> None:
        """R_min and R_max should match input range."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.2)
        r = np.linspace(-1.0, 2.0, 50)
        summary = membrane.export_summary(r)

        assert math.isclose(summary["R_min"], -1.0, rel_tol=1e-6)
        assert math.isclose(summary["R_max"], 2.0, rel_tol=1e-6)

    def test_theta_beta_match_membrane_params(self) -> None:
        """Exported theta and beta should match membrane config."""
        membrane = ThresholdMembrane(theta=0.7, beta=3.5)
        r = np.linspace(0.0, 1.0, 50)
        summary = membrane.export_summary(r)

        assert summary["theta"] == 0.7
        assert summary["beta"] == 3.5

    def test_zeta_mean_is_one_for_default_impedance(self) -> None:
        """Default impedance mean should be 1.0."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.2)
        r = np.linspace(0.0, 1.0, 50)
        summary = membrane.export_summary(r)

        assert math.isclose(summary["zeta_mean"], 1.0, rel_tol=1e-6)

    def test_can_write_to_existing_dict(self) -> None:
        """Should be able to pass existing dict to populate."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.2)
        r = np.linspace(0.0, 1.0, 50)

        existing = {"custom_field": 42.0}
        result = membrane.export_summary(r, store=existing)

        # Should return same dict
        assert result is existing
        # Should contain both original and new fields
        assert result["custom_field"] == 42.0
        assert "theta" in result

    def test_all_values_are_finite(self) -> None:
        """All exported values should be finite numbers."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.2)
        r = np.linspace(0.0, 1.0, 50)
        summary = membrane.export_summary(r)

        for key, value in summary.items():
            assert math.isfinite(value), f"{key} is not finite: {value}"

    def test_all_values_are_floats(self) -> None:
        """All exported values should be Python floats."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.2)
        r = np.linspace(0.0, 1.0, 50)
        summary = membrane.export_summary(r)

        for key, value in summary.items():
            assert isinstance(value, float), f"{key} is not float: {type(value)}"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_point_response(self) -> None:
        """Should handle single-point input."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.2)
        r = [0.5]
        result = membrane.response(r)
        assert len(result) == 1
        assert math.isclose(result[0], 0.5, rel_tol=1e-6)

    def test_two_point_response(self) -> None:
        """Should handle two-point input."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.2)
        r = [0.0, 1.0]
        result = membrane.response(r)
        assert len(result) == 2
        assert result[0] < result[1]  # Monotonic

    def test_extreme_beta_values(self) -> None:
        """Should handle very small and very large beta."""
        r = np.linspace(0.0, 1.0, 50)

        # Very small beta: gradual transition
        membrane_small = ThresholdMembrane(theta=0.5, beta=0.1)
        result_small = membrane_small.response(r)
        assert np.all(np.isfinite(result_small))

        # Very large beta: sharp transition
        membrane_large = ThresholdMembrane(theta=0.5, beta=100.0)
        result_large = membrane_large.response(r)
        assert np.all(np.isfinite(result_large))

    def test_theta_outside_R_range(self) -> None:
        """Should handle theta outside R range."""
        # Theta above R range
        membrane_above = ThresholdMembrane(theta=10.0, beta=4.0)
        r = np.linspace(0.0, 1.0, 50)
        result_above = membrane_above.response(r)
        # All values should be near 0
        assert np.all(result_above < 0.1)

        # Theta below R range
        membrane_below = ThresholdMembrane(theta=-10.0, beta=4.0)
        result_below = membrane_below.response(r)
        # All values should be near 1
        assert np.all(result_below > 0.9)

    def test_negative_R_values(self) -> None:
        """Should handle negative R values correctly."""
        membrane = ThresholdMembrane(theta=0.0, beta=4.0)
        r = np.linspace(-2.0, -0.1, 20)
        result = membrane.response(r)
        # All should be below 0.5 (below theta=0)
        assert np.all(result < 0.5)

    def test_compare_against_null_with_minimal_input(self) -> None:
        """compare_against_null should handle small arrays."""
        membrane = ThresholdMembrane(theta=0.5, beta=4.2)
        r = np.linspace(0.0, 1.0, 5)  # Just 5 points
        result = membrane.compare_against_null(r)

        # Should still produce valid output
        assert math.isfinite(result["resonance_gain"])
        assert 0 <= result["half_max_index"] < len(r)
