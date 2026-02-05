"""
Neuro β-Extractor
=================

Minimaler β-Schätzer für neuronale Zeitreihen.

σ(β(R-Θ)) bleibt hier bewusst konservativ: wir nutzen eine einfache
logistische Fit-Approximation als Platzhalter, damit R stabil wächst,
Θ über Nullmodelle und ΔAIC-Grenzen geschützt bleibt und ζ(R) nicht driftet.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.optimize import curve_fit


@dataclass
class BetaEstimate:
    beta: float
    threshold: float
    r_value: float


def _logistic(z: np.ndarray, beta: float, threshold: float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-beta * (z - threshold)))


def _heuristic_beta_fit(x: np.ndarray, y: np.ndarray) -> BetaEstimate:
    logit = np.log(y / (1 - y))
    beta = float(np.clip(np.std(logit) * 1.5, 0.1, 10.0))
    threshold = float(np.median(x))

    prediction = _logistic(x, beta, threshold)
    residual = y - prediction
    r_value = float(1.0 - np.var(residual) / (np.var(y) + 1e-9))
    return BetaEstimate(beta=beta, threshold=threshold, r_value=r_value)


def estimate_beta_from_series(series: Sequence[float]) -> BetaEstimate:
    """
    Schätzt β aus einer Zeitreihe, indem eine logistische Kurve an
    normierte Amplituden angepasst wird.

    Nullmodelle (linear/power-law/constant) und ΔAIC-Vergleiche werden
    in der Analyse-Schicht durchgeführt.
    """
    data = np.asarray(series, dtype=float)
    if data.size < 10:
        return BetaEstimate(beta=0.0, threshold=0.0, r_value=0.0)

    y = (data - data.min()) / (np.ptp(data) + 1e-9)
    y = np.clip(y, 1e-6, 1 - 1e-6)
    x = np.linspace(0.0, 1.0, num=y.size)

    try:
        params, _ = curve_fit(
            _logistic,
            x,
            y,
            p0=(4.8, 0.5),
            bounds=([0.1, 0.0], [20.0, 1.0]),
            maxfev=10000,
        )
        beta, threshold = (float(params[0]), float(params[1]))
        prediction = _logistic(x, beta, threshold)
        residual = y - prediction
        r_value = float(1.0 - np.var(residual) / (np.var(y) + 1e-9))
        if not np.isfinite(r_value):
            return _heuristic_beta_fit(x, y)
        return BetaEstimate(beta=beta, threshold=threshold, r_value=r_value)
    except (RuntimeError, ValueError):
        return _heuristic_beta_fit(x, y)
