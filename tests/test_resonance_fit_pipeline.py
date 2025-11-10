"""Comprehensive tests for resonance fitting pipeline.

Tests logit transforms, threshold fitting, null model comparisons,
and statistical diagnostics.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from analysis.resonance_fit_pipeline import (
    _mean,
    _variance,
    evaluate_null_model,
    fit_threshold_parameters,
    logit,
)


class TestLogit:
    """Test the logit transform function."""

    def test_logit_at_half_is_zero(self) -> None:
        """logit(0.5) should be 0."""
        result = logit([0.5])
        assert len(result) == 1
        assert math.isclose(result[0], 0.0, abs_tol=1e-10)

    def test_logit_below_half_is_negative(self) -> None:
        """logit(p) for p < 0.5 should be negative."""
        result = logit([0.1, 0.2, 0.3])
        for value in result:
            assert value < 0

    def test_logit_above_half_is_positive(self) -> None:
        """logit(p) for p > 0.5 should be positive."""
        result = logit([0.6, 0.7, 0.9])
        for value in result:
            assert value > 0

    def test_logit_clips_at_zero(self) -> None:
        """logit(0) should be clipped to avoid -inf."""
        result = logit([0.0])
        assert math.isfinite(result[0])
        assert result[0] < -10  # Very negative but finite

    def test_logit_clips_at_one(self) -> None:
        """logit(1) should be clipped to avoid +inf."""
        result = logit([1.0])
        assert math.isfinite(result[0])
        assert result[0] > 10  # Very positive but finite

    def test_logit_handles_multiple_values(self) -> None:
        """Should handle lists of values."""
        probs = [0.1, 0.5, 0.9]
        result = logit(probs)
        assert len(result) == 3
        assert all(math.isfinite(v) for v in result)

    def test_logit_monotonic(self) -> None:
        """logit should be monotonically increasing."""
        probs = [0.1, 0.3, 0.5, 0.7, 0.9]
        result = logit(probs)
        for i in range(len(result) - 1):
            assert result[i] < result[i + 1]

    def test_logit_empty_list(self) -> None:
        """Should handle empty input."""
        result = logit([])
        assert result == []


class TestMean:
    """Test the _mean helper function."""

    def test_mean_of_simple_list(self) -> None:
        """Should compute correct mean."""
        assert math.isclose(_mean([1.0, 2.0, 3.0]), 2.0)

    def test_mean_of_single_value(self) -> None:
        """Mean of single value is that value."""
        assert _mean([5.0]) == 5.0

    def test_mean_of_empty_list(self) -> None:
        """Mean of empty list should be 0."""
        assert _mean([]) == 0.0

    def test_mean_with_negatives(self) -> None:
        """Should handle negative numbers."""
        assert math.isclose(_mean([-1.0, 0.0, 1.0]), 0.0)

    def test_mean_with_floats(self) -> None:
        """Should handle floating point values."""
        values = [0.1, 0.2, 0.3]
        assert math.isclose(_mean(values), 0.2, abs_tol=1e-10)


class TestVariance:
    """Test the _variance helper function."""

    def test_variance_of_constant(self) -> None:
        """Variance of constant values is zero."""
        mean_val = 5.0
        variance = _variance([5.0, 5.0, 5.0], mean_val)
        assert variance == 0.0

    def test_variance_calculation(self) -> None:
        """Should compute correct variance."""
        values = [1.0, 2.0, 3.0]
        mean_val = 2.0
        # Variance = (1 + 0 + 1) = 2
        variance = _variance(values, mean_val)
        assert math.isclose(variance, 2.0)

    def test_variance_single_value(self) -> None:
        """Variance of single value is zero."""
        variance = _variance([3.0], 3.0)
        assert variance == 0.0

    def test_variance_empty_list(self) -> None:
        """Variance of empty list is zero."""
        variance = _variance([], 0.0)
        assert variance == 0.0


class TestFitThresholdParameters:
    """Test the threshold parameter fitting function."""

    def test_fit_perfect_sigmoid(self) -> None:
        """Should fit perfect sigmoid data accurately."""
        theta_true = 0.5
        beta_true = 4.0

        R = np.linspace(-1.0, 2.0, 50)
        sigma = 1.0 / (1.0 + np.exp(-beta_true * (R - theta_true)))

        result = fit_threshold_parameters(R, sigma)

        # Should recover parameters with high accuracy
        assert math.isclose(result["theta"], theta_true, abs_tol=0.1)
        assert math.isclose(result["beta"], beta_true, abs_tol=0.5)
        assert result["r2"] > 0.99

    def test_fit_returns_expected_keys(self) -> None:
        """Should return all expected diagnostic keys."""
        R = [0.0, 0.5, 1.0]
        sigma = [0.2, 0.5, 0.8]

        result = fit_threshold_parameters(R, sigma)

        expected_keys = {
            "beta", "theta", "beta_ci_lower", "beta_ci_upper",
            "theta_ci_lower", "theta_ci_upper", "r2", "aic", "ss_res"
        }
        assert set(result.keys()) == expected_keys

    def test_fit_confidence_intervals_valid(self) -> None:
        """Confidence intervals should be valid."""
        R = np.linspace(0.0, 1.0, 20)
        sigma = 1.0 / (1.0 + np.exp(-5.0 * (R - 0.5)))

        result = fit_threshold_parameters(R, sigma)

        # CI bounds should straddle the estimate
        assert result["beta_ci_lower"] <= result["beta"] <= result["beta_ci_upper"]

        if not math.isnan(result["theta"]):
            assert result["theta_ci_lower"] <= result["theta"] <= result["theta_ci_upper"]

    def test_fit_r2_bounded(self) -> None:
        """R² should be between 0 and 1."""
        R = [0.0, 0.5, 1.0]
        sigma = [0.1, 0.5, 0.9]

        result = fit_threshold_parameters(R, sigma)
        assert 0.0 <= result["r2"] <= 1.0

    def test_fit_empty_raises_error(self) -> None:
        """Should raise ValueError for empty input."""
        with pytest.raises(ValueError, match="At least one sample"):
            fit_threshold_parameters([], [])

    def test_fit_single_point_handles_gracefully(self) -> None:
        """Should handle single point (minimal data)."""
        # Single point doesn't raise error, but has limited statistics
        result = fit_threshold_parameters([0.5], [0.5])
        assert isinstance(result, dict)
        # With one point, we can't really estimate parameters well
        assert "beta" in result
        assert "theta" in result

    def test_fit_with_noise(self) -> None:
        """Should handle noisy data gracefully."""
        np.random.seed(42)
        theta_true = 0.5
        beta_true = 4.0

        R = np.linspace(-1.0, 2.0, 30)
        sigma_clean = 1.0 / (1.0 + np.exp(-beta_true * (R - theta_true)))
        noise = np.random.normal(0, 0.05, size=len(R))
        sigma = np.clip(sigma_clean + noise, 0.01, 0.99)

        result = fit_threshold_parameters(R, sigma)

        # Should still recover parameters reasonably
        assert math.isclose(result["theta"], theta_true, abs_tol=0.3)
        assert result["r2"] > 0.8

    def test_fit_flat_data_handles_degenerate(self) -> None:
        """Should handle flat/degenerate data without crash."""
        # All same R values -> Sxx = 0
        R = [0.5, 0.5, 0.5]
        sigma = [0.3, 0.5, 0.7]

        result = fit_threshold_parameters(R, sigma)

        # Should not crash, beta should be 0
        assert result["beta"] == 0.0
        assert math.isnan(result["theta"])

    def test_fit_negative_R_values(self) -> None:
        """Should handle negative R values."""
        R = [-2.0, -1.0, 0.0, 1.0, 2.0]
        sigma = [0.01, 0.1, 0.5, 0.9, 0.99]

        result = fit_threshold_parameters(R, sigma)

        assert math.isfinite(result["beta"])
        assert math.isfinite(result["theta"])

    def test_fit_aic_finite(self) -> None:
        """AIC should be finite for reasonable data."""
        R = np.linspace(0.0, 1.0, 20)
        sigma = 1.0 / (1.0 + np.exp(-4.0 * (R - 0.5)))

        result = fit_threshold_parameters(R, sigma)

        assert math.isfinite(result["aic"])

    def test_fit_ss_res_non_negative(self) -> None:
        """Sum of squared residuals should be non-negative."""
        R = [0.0, 0.5, 1.0]
        sigma = [0.2, 0.5, 0.8]

        result = fit_threshold_parameters(R, sigma)

        assert result["ss_res"] >= 0.0


class TestEvaluateNullModel:
    """Test the null model evaluation function."""

    def test_null_model_linear_fit(self) -> None:
        """Should fit linear data perfectly."""
        R = np.linspace(0.0, 1.0, 20)
        sigma = 2.0 * R + 0.1  # Perfect linear

        result = evaluate_null_model(R, sigma)

        assert result["r2"] > 0.99
        assert result["ss_res"] < 1e-6

    def test_null_model_returns_expected_keys(self) -> None:
        """Should return all expected keys."""
        R = [0.0, 0.5, 1.0]
        sigma = [0.1, 0.5, 0.9]

        result = evaluate_null_model(R, sigma)

        # Should contain at least the key diagnostic metrics
        required_keys = {"aic", "r2", "ss_res"}
        assert required_keys.issubset(result.keys())
        # May also include slope, intercept which is fine

    def test_null_model_r2_bounded(self) -> None:
        """R² should be between 0 and 1."""
        R = [0.0, 0.5, 1.0]
        sigma = [0.2, 0.5, 0.8]

        result = evaluate_null_model(R, sigma)

        assert 0.0 <= result["r2"] <= 1.0

    def test_null_model_aic_finite(self) -> None:
        """AIC should be finite."""
        R = np.linspace(0.0, 1.0, 20)
        sigma = 0.5 + 0.3 * R

        result = evaluate_null_model(R, sigma)

        assert math.isfinite(result["aic"])

    def test_null_model_with_noise(self) -> None:
        """Should handle noisy data."""
        np.random.seed(42)
        R = np.linspace(0.0, 1.0, 30)
        sigma_clean = 0.3 + 0.4 * R
        noise = np.random.normal(0, 0.05, size=len(R))
        sigma = np.clip(sigma_clean + noise, 0.0, 1.0)

        result = evaluate_null_model(R, sigma)

        assert result["r2"] > 0.5
        assert math.isfinite(result["aic"])

    def test_null_model_constant_sigma(self) -> None:
        """Should handle constant sigma values."""
        R = [0.0, 0.5, 1.0]
        sigma = [0.5, 0.5, 0.5]

        result = evaluate_null_model(R, sigma)

        # R² should be 1.0 for constant (perfect fit with zero slope)
        assert result["r2"] == 1.0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_fit_with_extreme_beta(self) -> None:
        """Should handle very steep sigmoid (large beta)."""
        R = np.linspace(-1.0, 1.0, 50)
        sigma = 1.0 / (1.0 + np.exp(-20.0 * (R - 0.0)))  # Very steep

        result = fit_threshold_parameters(R, sigma)

        # Should still fit, though beta estimate may differ
        assert math.isfinite(result["beta"])
        assert result["beta"] > 0

    def test_fit_with_small_beta(self) -> None:
        """Should handle gradual sigmoid (small beta)."""
        R = np.linspace(-5.0, 5.0, 50)
        sigma = 1.0 / (1.0 + np.exp(-0.5 * (R - 0.0)))  # Gradual

        result = fit_threshold_parameters(R, sigma)

        assert math.isfinite(result["beta"])
        assert result["beta"] > 0

    def test_fit_with_theta_outside_range(self) -> None:
        """Should handle theta outside R range."""
        R = np.linspace(0.0, 1.0, 20)
        # Theta = 5.0, far outside R range
        sigma = 1.0 / (1.0 + np.exp(-4.0 * (R - 5.0)))

        result = fit_threshold_parameters(R, sigma)

        # All sigma values will be near 0 - may result in degenerate fit
        # theta might be NaN if fit fails, which is acceptable
        assert "theta" in result  # Key should exist
        # Either finite or NaN is acceptable for this edge case
