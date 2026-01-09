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


@dataclass
class BetaEstimate:
    beta: float
    threshold: float
    r_value: float


def _logistic(z: np.ndarray, beta: float, threshold: float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-beta * (z - threshold)))


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

    x = (data - data.min()) / (np.ptp(data) + 1e-9)
    y = np.clip(x, 1e-6, 1 - 1e-6)

    # Heuristische β-Schätzung über logit-Varianz
    logit = np.log(y / (1 - y))
    beta = float(np.clip(np.std(logit) * 1.5, 0.1, 10.0))
    threshold = float(np.median(x))

    prediction = _logistic(x, beta, threshold)
    residual = y - prediction
    r_value = float(1.0 - np.var(residual) / (np.var(y) + 1e-9))

    return BetaEstimate(beta=beta, threshold=threshold, r_value=r_value)
