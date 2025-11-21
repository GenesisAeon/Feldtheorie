"""
Implosive Genesis Engine

Formal:
    Provides an inverted sigmoid S(R) = 1 - 1 / (1 + exp(-β(R-Θ))) to model
    implosive genesis where σ(β(R-Θ)) flips into contraction. Phase-space
    trajectories combine S(R) with a damping term ζ(R)=ζ0·R to trace the
    compressed→expanded transition without rendering figures.

Empirical:
    Returns numeric arrays so analysis notebooks can benchmark null baselines
    (ζ0≈0, β small) against implosive regimes (ζ0>0, β large) and compute ΔAIC,
    R², or time-to-threshold metrics.

Poetic:
    The field inhales — the inverted sigmoid bends resonance inward before the
    membrane exhales back toward balance.
"""
from __future__ import annotations

import math
from typing import Iterable, List, Tuple


def inverted_sigmoid(r: Iterable[float], beta: float = 4.0, theta: float = 0.0) -> List[float]:
    """Evaluate the inverted sigmoid S(R) = 1 - σ(β(R-Θ))."""

    return [1.0 - 1.0 / (1.0 + math.exp(-beta * (value - theta))) for value in r]


def phase_space_trajectory(
    r_start: float,
    r_end: float,
    steps: int = 50,
    beta: float = 4.0,
    theta: float = 0.0,
    damping: float = 0.05,
) -> Tuple[List[float], List[float], List[float]]:
    """Generate phase-space data for the implosive genesis curve.

    Returns a tuple of (R values, inverted sigmoid S(R), velocity field) where
    the velocity is modeled as v = -ζ0·R + S(R) to capture contraction balanced
    by the inverted response.
    """

    if steps <= 1:
        raise ValueError("steps must be greater than 1 to form a trajectory.")

    r_values = [r_start + (r_end - r_start) * i / (steps - 1) for i in range(steps)]
    s_values = inverted_sigmoid(r_values, beta=beta, theta=theta)
    velocity = [-damping * r + s for r, s in zip(r_values, s_values)]
    return r_values, s_values, velocity
