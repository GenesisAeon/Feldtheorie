"""Three v0 role-vector estimators: tau, V, I^macro.

Definitions frozen in RIG_v0_SCOPING.md section 1. Implemented here
exactly as specified -- no additional smoothing, clipping, or tuning
beyond what the spec states, so a reviewer can check code against spec
line by line.
"""

from __future__ import annotations

import numpy as np


def autocorrelation(x: np.ndarray, max_lag: int) -> np.ndarray:
    """Normalized autocorrelation function, lags 0..max_lag."""
    x = x - x.mean()
    n = len(x)
    denom = np.dot(x, x)
    if denom == 0:
        return np.zeros(max_lag + 1)
    acf = np.empty(max_lag + 1)
    for lag in range(max_lag + 1):
        acf[lag] = np.dot(x[: n - lag], x[lag:]) / denom
    return acf


def e_folding_tau(x: np.ndarray, max_lag: int | None = None) -> float:
    """tau = smallest lag k such that ACF(k) <= 1/e. Falls back to max_lag
    if the ACF never decays that far within the window (documented, not
    silently clipped).

    max_lag defaults to len(x)//4 (standard rule of thumb: reliable ACF
    estimates need lag << N) rather than a fixed constant -- an earlier
    version of this function used a fixed max_lag=200, which silently hit
    its own ceiling for both Train A (critical slowing down near T_c
    genuinely pushes tau past 200) and Train B, giving a meaningless
    tau=200.0 for both domains. Found via direct ACF inspection during the
    first H1 run, 2026-08-29 -- see RIG_v0_SCOPING.md run log / commit
    history for the before/after result, not silently corrected."""
    if max_lag is None:
        max_lag = len(x) // 4
    acf = autocorrelation(x, min(max_lag, len(x) - 2))
    threshold = 1.0 / np.e
    below = np.where(acf <= threshold)[0]
    if len(below) == 0:
        return float(len(acf) - 1)  # did not decay within window
    return float(below[0])


def rolling_variability(x: np.ndarray, window: int) -> np.ndarray:
    """V = rolling-window standard deviation."""
    n = len(x)
    v = np.full(n, np.nan)
    for i in range(window, n):
        v[i] = x[i - window : i].std()
    return v


def _ar1_fit(y: np.ndarray) -> tuple[float, float]:
    """Fit y[t] = a + b*y[t-1] via least squares. Returns (a, b)."""
    y_prev, y_next = y[:-1], y[1:]
    if len(y_prev) < 2 or y_prev.std() == 0:
        return float(y.mean()), 0.0
    b, a = np.polyfit(y_prev, y_next, 1)
    return float(a), float(b)


def macro_informativeness(x: np.ndarray, block_size: int) -> float:
    """I^macro = 1 - MSE(x[t+1] | coarse AR(1) forecast) / MSE(x[t+1] | naive mean).

    Coarse series y = block-average of x at `block_size`. An AR(1) is fit
    on y and used to forecast the coarse-scale next value, then compared
    (same units, no rescaling trick) against the fine series' actual next
    value at the end of each block. The naive baseline predicts the
    running mean of x up to t. This is the "single-layer coarse-vs-fine
    cut" specified in RIG_v0_SCOPING.md section 1 -- not full PID/EI.
    """
    n = len(x)
    n_blocks = n // block_size
    if n_blocks < 4:
        return float("nan")

    coarse = np.array([x[i * block_size : (i + 1) * block_size].mean() for i in range(n_blocks)])
    a, b = _ar1_fit(coarse)

    coarse_forecast_errors = []
    naive_errors = []
    for i in range(1, n_blocks):
        forecast = a + b * coarse[i - 1]
        actual_fine_next = x[i * block_size] if i * block_size < n else x[-1]
        coarse_forecast_errors.append((actual_fine_next - forecast) ** 2)

        naive_pred = x[: i * block_size].mean()
        naive_errors.append((actual_fine_next - naive_pred) ** 2)

    mse_coarse = float(np.mean(coarse_forecast_errors))
    mse_naive = float(np.mean(naive_errors))
    if mse_naive == 0:
        return float("nan")
    return 1.0 - (mse_coarse / mse_naive)


def detrend_linear(x: np.ndarray) -> np.ndarray:
    """Remove a linear trend. Applied uniformly to every domain's x_t
    before tau/V/I^macro estimation -- RIG_v0_SCOPING.md section 1 already
    specifies "the (detrended, per domain) series" for V; an earlier run
    only detrended Train B explicitly (via its d* trend term) and left
    Train A's raw |magnetization| un-detrended, whose deterministic
    ramp-induced drift (ordered -> disordered phase) dominated the ACF and
    produced a tau estimate that scaled with simulation length rather than
    converging to a physical correlation time. Fixed 2026-08-29, same
    domain-agnostic operation for both series, not an Ising-specific
    correction."""
    t = np.arange(len(x))
    coef = np.polyfit(t, x, 1)
    return x - np.polyval(coef, t)


def role_vector(x: np.ndarray, window_multiplier: int = 10) -> dict[str, float]:
    """Compute (tau, I_macro, V) for a series x, per RIG_v0_SCOPING.md."""
    x = detrend_linear(x)
    tau = e_folding_tau(x)
    tau_int = max(2, int(round(tau)))
    window = max(4, window_multiplier * tau_int)
    window = min(window, len(x) // 2)

    v_series = rolling_variability(x, window)
    v = float(np.nanmean(v_series))

    block_size = max(2, 2 * tau_int)
    i_macro = macro_informativeness(x, block_size)

    return {"tau": tau, "V": v, "I_macro": i_macro, "window": window, "block_size": block_size}
