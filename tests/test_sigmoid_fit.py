"""Ensure sigmoid fitting fallbacks keep the resonance channel open."""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np
import pytest

from models.sigmoid_fit import (
    SigmoidFitResult,
    fit_sigmoid_with_fallbacks,
    linear_fit_aic,
    power_law_fit_aic,
)


def _generate_sigmoid_samples(
    *,
    theta: float,
    beta: float,
    L: float = 1.0,
    baseline: float = 0.0,
    noise: float = 0.0,
    size: int = 40,
) -> tuple[np.ndarray, np.ndarray]:
    r = np.linspace(theta - 1.0, theta + 1.0, num=size)
    sigma = L / (1.0 + np.exp(-beta * (r - theta))) + baseline
    if noise > 0:
        rng = np.random.default_rng(42)
        sigma = sigma + rng.normal(scale=noise, size=size)
    return r, sigma


def test_fit_sigmoid_with_fallbacks_prefers_scipy_when_available() -> None:
    sigmoid_fit = pytest.importorskip("models.sigmoid_fit")
    if sigmoid_fit._SCIPY_OPTIMIZE is None:
        pytest.skip("SciPy optimiser not available")

    r, sigma = _generate_sigmoid_samples(theta=0.5, beta=4.2, noise=0.01)
    result = fit_sigmoid_with_fallbacks(r, sigma)
    assert isinstance(result, SigmoidFitResult)
    assert result.ok
    assert result.method == "nonlinear_curve_fit"
    assert result.beta is not None and math.isfinite(result.beta)
    assert result.ci_width is None or result.ci_width >= 0.0


def test_fit_sigmoid_with_fallbacks_recovers_when_scipy_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    import models.sigmoid_fit as sigmoid_fit

    monkeypatch.setattr(sigmoid_fit, "_SCIPY_OPTIMIZE", None)
    r, sigma = _generate_sigmoid_samples(theta=0.5, beta=4.0, noise=0.05)
    result = sigmoid_fit.fit_sigmoid_with_fallbacks(r, sigma)
    assert result.ok
    assert result.method == "logit_linear_fallback"
    assert result.beta is not None and result.beta > 0.0


def test_null_model_aic_functions_handle_degenerate_inputs() -> None:
    empty: Sequence[float] = []
    assert math.isinf(linear_fit_aic(empty, empty))
    assert math.isinf(power_law_fit_aic(empty, empty))

    x = np.linspace(1.0, 2.0, num=10)
    y_linear = 2.0 * x + 1.0
    y_power = x ** 2

    assert math.isfinite(linear_fit_aic(x, y_linear))
    assert math.isfinite(power_law_fit_aic(x, y_power))


def test_fit_sigmoid_empty_inputs_returns_invalid() -> None:
    """Empty inputs should return invalid result."""
    result = fit_sigmoid_with_fallbacks([], [])
    assert not result.ok
    assert result.method == "invalid"
    assert result.beta is None


def test_fit_sigmoid_mismatched_lengths_returns_invalid() -> None:
    """Mismatched input lengths should return invalid result."""
    result = fit_sigmoid_with_fallbacks([0.1, 0.2], [0.5])
    assert not result.ok
    assert result.method == "invalid"


def test_fit_sigmoid_constant_response_handles_gracefully() -> None:
    """Constant response (no variation) should be handled gracefully."""
    x = np.linspace(0.0, 1.0, 20)
    y = np.ones(20) * 0.5  # Constant response

    result = fit_sigmoid_with_fallbacks(x, y)
    # scipy may "succeed" with constant data but produce degenerate params
    # or fallback may handle it - either is acceptable
    if result.ok:
        # If it succeeded, params should reflect the constant (degenerate case)
        assert result.beta is not None
    else:
        # If it failed, should have appropriate error
        assert result.method == "indeterminate"


def test_fit_sigmoid_insufficient_data_for_power_law() -> None:
    """power_law_fit_aic should return inf for insufficient data."""
    x = [0.1, -0.2]  # Not enough positive values
    y = [0.5, 0.3]
    aic = power_law_fit_aic(x, y)
    assert math.isinf(aic)


def test_linear_fit_aic_with_single_point() -> None:
    """linear_fit_aic should return inf for single point."""
    aic = linear_fit_aic([1.0], [2.0])
    assert math.isinf(aic)


def test_logistic_function() -> None:
    """Test the logistic function directly."""
    from models.sigmoid_fit import logistic

    r = np.array([0.0, 0.5, 1.0])
    L = 1.0
    beta = 4.0
    theta = 0.5
    baseline = 0.0

    result = logistic(r, L, beta, theta, baseline)

    # At theta, should be approximately L/2 + baseline
    assert result[1] > 0.4 and result[1] < 0.6
    # Below theta, should be close to baseline
    assert result[0] < 0.3
    # Above theta, should be close to L + baseline
    assert result[2] > 0.7
