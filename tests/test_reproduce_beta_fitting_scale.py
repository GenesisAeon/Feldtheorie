"""Regression tests for the 2026-09-08 fitting-scale fix in reproduce_beta.py.

Before the fix, _exp_fit/_power_fit minimized SSE in LOG-scale (a
log-normal/multiplicative error model) while _poly_fit and the logistic
fit minimized SSE in original scale (a Gaussian error model) -- but
_aic_bic always computed RSS on the original scale for every model, so
the exponential/power AIC values did not reflect each model's actual
best fit under the error model AIC implicitly assumes. This made the
logistic look better relative to the null models than a fair, same-
likelihood comparison would show.
"""

from __future__ import annotations

import numpy as np
import pytest
from scripts.reproduce_beta import _exp_fit, _power_fit, _rss


def test_exp_fit_minimizes_original_scale_rss_better_than_log_linear() -> None:
    """The new fit must not do worse, on original-scale RSS, than the
    old closed-form log-linear regression it now only uses as a seed."""
    rng = np.random.default_rng(7)
    x = np.linspace(0.1, 10, 30)
    y = 2.0 * np.exp(0.3 * x) + rng.normal(0, 5.0, size=x.size)
    y = np.clip(y, 0.01, None)

    old_log_coeffs = np.polyfit(x, np.log(y), deg=1)
    old_yhat = np.exp(old_log_coeffs[1]) * np.exp(old_log_coeffs[0] * x)
    old_rss = _rss(y, old_yhat)

    _, new_yhat = _exp_fit(x, y)
    new_rss = _rss(y, new_yhat)

    assert new_rss <= old_rss + 1e-6


def test_power_fit_minimizes_original_scale_rss_better_than_log_log() -> None:
    rng = np.random.default_rng(11)
    x = np.linspace(0.5, 10, 30)
    y = 3.0 * np.power(x, 1.5) + rng.normal(0, 4.0, size=x.size)
    y = np.clip(y, 0.01, None)

    old_log_coeffs = np.polyfit(np.log(x), np.log(y), deg=1)
    old_log_pred = old_log_coeffs[1] + old_log_coeffs[0] * np.log(np.clip(x, 1e-12, None))
    old_yhat = np.exp(old_log_pred)
    old_rss = _rss(y, old_yhat)

    _, new_yhat = _power_fit(x, y)
    new_rss = _rss(y, new_yhat)

    assert new_rss <= old_rss + 1e-6


def test_exp_fit_recovers_known_parameters_on_clean_data() -> None:
    x = np.linspace(0, 5, 25)
    y = 1.5 * np.exp(0.4 * x)  # noise-free
    coeffs, yhat = _exp_fit(x, y)
    a, b = coeffs
    assert a == pytest.approx(1.5, rel=1e-3)
    assert b == pytest.approx(0.4, rel=1e-3)
    assert yhat == pytest.approx(y, rel=1e-3)


def test_power_fit_recovers_known_parameters_on_clean_data() -> None:
    x = np.linspace(0.1, 5, 25)
    y = 2.0 * np.power(x, 1.2)  # noise-free
    coeffs, yhat = _power_fit(x, y)
    a, b = coeffs
    assert a == pytest.approx(2.0, rel=1e-3)
    assert b == pytest.approx(1.2, rel=1e-3)
    assert yhat == pytest.approx(y, rel=1e-3)


def test_exp_fit_rejects_all_nonpositive_response() -> None:
    x = np.linspace(0, 5, 10)
    y = -np.ones_like(x)
    with pytest.raises(ValueError, match="positive response"):
        _exp_fit(x, y)


def test_power_fit_rejects_all_nonpositive_inputs() -> None:
    x = -np.ones(10)
    y = np.ones(10)
    with pytest.raises(ValueError, match="positive control and response"):
        _power_fit(x, y)
