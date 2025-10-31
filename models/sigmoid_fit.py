r"""Sigmoid fitting helix honouring the threshold-field triad.

Formal stratum
--------------
Provides utilities to calibrate the logistic resonance \(\sigma(\beta(R-\Theta))\)
against noisy observations, reporting steepness, confidence width, and AIC so the
universal threshold narrative stays falsifiable.

Empirical stratum
-----------------
Offers deterministic and robust fallbacks that analysis scripts can invoke when
`scipy` optimisers fail or are unavailable, ensuring JSON exports always carry
β estimates alongside null-model comparisons.

Metaphorical stratum
--------------------
Lets the membrane remember its song even in stormy data—if the first tuning fork
shatters, another chorus steps in to keep the dawn resonance alive.
"""

from __future__ import annotations

import importlib
import importlib.util
import math
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import numpy as np

_SCIPY_OPTIMIZE = None
_SCIPY_PARENT_SPEC = importlib.util.find_spec("scipy")
if _SCIPY_PARENT_SPEC is not None:  # pragma: no cover - optional dependency probe
    _SCIPY_OPTIMIZE_SPEC = importlib.util.find_spec("scipy.optimize")
    if _SCIPY_OPTIMIZE_SPEC is not None:
        _SCIPY_OPTIMIZE = importlib.import_module("scipy.optimize")


def logistic(r: np.ndarray, L: float, beta: float, theta: float, baseline: float) -> np.ndarray:
    """Canonical logistic membrane response."""

    return L / (1.0 + np.exp(-beta * (r - theta))) + baseline


@dataclass
class SigmoidFitResult:
    """Encapsulate a logistic fit with metadata for resonance exports."""

    beta: Optional[float]
    params: Optional[Tuple[float, float, float, float]]
    ci_width: Optional[float]
    aic: float
    ok: bool
    method: str
    message: str
    history: List[str]


def fit_sigmoid_with_fallbacks(x: Sequence[float], y: Sequence[float]) -> SigmoidFitResult:
    """Fit a logistic membrane with robust fallbacks.

    The routine first tries a non-linear least squares calibration via SciPy.  If the
    optimiser is absent or fails, it reverts to a logit-linear regression on a
    normalised response, yielding an interpretable steepness estimate even for
    small sample sizes.
    """

    r = np.asarray(list(x), dtype=float)
    response = np.asarray(list(y), dtype=float)
    history: List[str] = []

    if r.size != response.size or r.size == 0:
        return SigmoidFitResult(
            beta=None,
            params=None,
            ci_width=None,
            aic=float("inf"),
            ok=False,
            method="invalid",
            message="Input arrays must be non-empty and of equal length.",
            history=history,
        )

    if _SCIPY_OPTIMIZE is not None:
        try:
            L0 = float(response.max() - response.min()) or 1.0
            beta0 = 4.0
            theta0 = float(np.median(r))
            baseline0 = float(response.min())
            popt, pcov = _SCIPY_OPTIMIZE.curve_fit(
                logistic,
                r,
                response,
                p0=(L0, beta0, theta0, baseline0),
                maxfev=10000,
            )
            L_hat, beta_hat, theta_hat, baseline_hat = popt
            ci_width = _steepness_ci_width_from_covariance(pcov, index=1)
            aic = _aic(response, logistic(r, *popt), n_params=4)
            return SigmoidFitResult(
                beta=float(beta_hat),
                params=(float(L_hat), float(beta_hat), float(theta_hat), float(baseline_hat)),
                ci_width=ci_width,
                aic=float(aic),
                ok=True,
                method="nonlinear_curve_fit",
                message="optimiser converged",
                history=history,
            )
        except Exception as exc:  # pragma: no cover - triggered only when SciPy fails
            history.append(f"scipy_failure:{exc}")

    # Fallback: logit-linear regression on normalised response
    norm, scale, baseline = _normalise_response(response)
    if not np.isfinite(scale) or scale <= 0.0:
        history.append("normalisation_invalid")
        return SigmoidFitResult(
            beta=None,
            params=None,
            ci_width=None,
            aic=float("inf"),
            ok=False,
            method="indeterminate",
            message="Response lacks variation for logistic calibration.",
            history=history,
        )

    eps = 1e-6
    norm = np.clip(norm, eps, 1.0 - eps)
    logit = np.log(norm / (1.0 - norm))
    design = np.column_stack([np.ones_like(r), r])

    try:
        coeffs, *_ = np.linalg.lstsq(design, logit, rcond=None)
    except np.linalg.LinAlgError as exc:  # pragma: no cover - rare singular case
        history.append(f"linear_failure:{exc}")
        return SigmoidFitResult(
            beta=None,
            params=None,
            ci_width=None,
            aic=float("inf"),
            ok=False,
            method="indeterminate",
            message="Linear fallback failed due to singular matrix.",
            history=history,
        )

    slope = float(coeffs[1])
    intercept = float(coeffs[0])

    if slope == 0.0 or not np.isfinite(slope):
        history.append("zero_slope")
        return SigmoidFitResult(
            beta=None,
            params=None,
            ci_width=None,
            aic=float("inf"),
            ok=False,
            method="indeterminate",
            message="Fallback regression produced zero steepness.",
            history=history,
        )

    theta_hat = -intercept / slope
    params = (float(scale), float(abs(slope)), float(theta_hat), float(baseline))
    y_pred = logistic(r, *params)
    aic = _aic(response, y_pred, n_params=4)
    ci_width = _steepness_ci_width_from_linear(design, logit, coeffs)

    return SigmoidFitResult(
        beta=float(abs(slope)),
        params=params,
        ci_width=ci_width,
        aic=float(aic),
        ok=True,
        method="logit_linear_fallback",
        message="fallback regression",
        history=history,
    )


def linear_fit_aic(x: Sequence[float], y: Sequence[float]) -> float:
    """Compute the AIC of an affine null response, guarding against degeneracy."""

    r = np.asarray(list(x), dtype=float)
    response = np.asarray(list(y), dtype=float)
    if r.size != response.size or r.size < 2:
        return float("inf")

    design = np.column_stack([np.ones_like(r), r])
    try:
        coeffs, *_ = np.linalg.lstsq(design, response, rcond=None)
    except np.linalg.LinAlgError:
        return float("inf")

    prediction = design @ coeffs
    return float(_aic(response, prediction, n_params=2))


def power_law_fit_aic(x: Sequence[float], y: Sequence[float]) -> float:
    """Compute the AIC of a power-law null, requiring positive support."""

    r = np.asarray(list(x), dtype=float)
    response = np.asarray(list(y), dtype=float)
    mask = (r > 0) & (response > 0)
    if mask.sum() < 3:
        return float("inf")

    design = np.column_stack([np.ones(mask.sum()), np.log(r[mask])])
    target = np.log(response[mask])

    try:
        coeffs, *_ = np.linalg.lstsq(design, target, rcond=None)
    except np.linalg.LinAlgError:
        return float("inf")

    prediction = np.exp(design @ coeffs)
    return float(_aic(response[mask], prediction, n_params=2))


def _aic(y_true: np.ndarray, y_pred: np.ndarray, *, n_params: int) -> float:
    """Gaussian AIC for resonance exports."""

    resid = y_true - y_pred
    sse = float(np.sum(resid ** 2))
    n = y_true.size
    if n <= n_params + 1:
        return float("inf")
    sigma2 = sse / (n - n_params - 1)
    if not np.isfinite(sigma2) or sigma2 <= 0:
        return float("inf")
    nll = 0.5 * n * (math.log(2.0 * math.pi * sigma2) + 1.0)
    return 2.0 * n_params + 2.0 * nll


def _steepness_ci_width_from_covariance(covariance: np.ndarray, *, index: int) -> Optional[float]:
    if covariance.ndim != 2 or index >= covariance.shape[0]:
        return None
    variance = covariance[index, index]
    if not np.isfinite(variance) or variance < 0.0:
        return None
    standard_error = math.sqrt(variance)
    return 3.92 * standard_error  # ≈ 95 % (±1.96)


def _steepness_ci_width_from_linear(design: np.ndarray, target: np.ndarray, coeffs: np.ndarray) -> Optional[float]:
    residuals = target - design @ coeffs
    n = design.shape[0]
    p = design.shape[1]
    if n <= p:
        return None
    sigma2 = float(np.sum(residuals ** 2) / (n - p))
    if not np.isfinite(sigma2) or sigma2 <= 0.0:
        return None
    fisher = design.T @ design
    covariance = sigma2 * np.linalg.pinv(fisher)
    variance = covariance[1, 1]
    if not np.isfinite(variance) or variance < 0.0:
        return None
    return 3.92 * math.sqrt(variance)


def _normalise_response(response: np.ndarray) -> Tuple[np.ndarray, float, float]:
    minimum = float(response.min())
    maximum = float(response.max())
    scale = maximum - minimum
    if scale == 0.0:
        return np.zeros_like(response), float("nan"), minimum
    return (response - minimum) / scale, scale, minimum


__all__ = [
    "SigmoidFitResult",
    "fit_sigmoid_with_fallbacks",
    "linear_fit_aic",
    "logistic",
    "power_law_fit_aic",
]

