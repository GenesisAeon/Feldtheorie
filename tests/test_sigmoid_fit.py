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
