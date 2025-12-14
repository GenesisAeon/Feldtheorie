"""Adaptive impedance solver for σ(β(R-Θ)) trajectories.

This module extends the v_RIG consciousness framework with an adaptive
impedance solver that links workload intensity ``R``, production baseline
``Θ``, and logistic steepness ``β``. It computes how the dimensional
impedance ``Z(β)`` evolves under different β-regimes and how damping
``ζ(R)`` reduces the barrier between surface (A) and volume (V) entropy.

Key features
-----------
- **API parity** with ``calculate_impedance`` for baseline Z computations.
- **Logistic trajectories** via σ(β(R-Θ)) capturing emergent activation.
- **Damping control** through ζ(R) to model telemetric fatigue or CI relief.
- **Null-model harness** to compare adaptive vs. linear impedance scaling
  for falsifiability-first evaluation.

References
----------
- ``models/consciousness_integration.py`` for baseline impedance and v_RIG.
- ``releases/v8.0/next_steps.*`` lantern: "Impedance solver Z(β) adaptive dynamics".
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .consciousness_integration import calculate_impedance
from .unified_constants import ALPHA_INV, PHI

# Baseline β used in v8.0 logistic framing
BASELINE_BETA = 4.8


@dataclass
class ImpedanceState:
    """State snapshot for a single β along the impedance trajectory.

    Attributes
    ----------
    beta : float
        Logistic steepness controlling σ(β(R-Θ)).
    R : float
        Open workload intensity (signal level).
    Theta : float
        Production-ready baseline / target threshold.
    activation : float
        Logistic activation σ(β(R-Θ)) in [0, 1].
    null_impedance_z : float
        Linear impedance scaled with β (null model without damping).
    damped_impedance_z : float
        Adaptive impedance after applying ζ(R) damping.
    """

    beta: float
    R: float
    Theta: float
    activation: float
    null_impedance_z: float
    damped_impedance_z: float


def impedance_from_beta(
    beta: float,
    alpha_inv: float = ALPHA_INV,
    phi: float = PHI,
    beta_ref: float = BASELINE_BETA,
) -> float:
    """Compute impedance scaled by β relative to the baseline β_ref.

    This mirrors ``calculate_impedance`` while allowing β-dependent scaling
    to represent regime changes (information → biology → climate).
    """

    base_impedance = calculate_impedance(alpha_inv=alpha_inv, phi=phi)
    return base_impedance * (beta / beta_ref)


def solve_impedance_state(
    beta: float,
    R: float,
    Theta: float,
    zeta: float = 0.0,
    alpha_inv: float = ALPHA_INV,
    phi: float = PHI,
    beta_ref: float = BASELINE_BETA,
) -> ImpedanceState:
    """Solve a single impedance state for given β, R, Θ, and ζ(R).

    The solver computes a null-model impedance that scales linearly with β
    and an adaptive impedance reduced by ζ(R)·σ(β(R-Θ)).

    Parameters
    ----------
    beta : float
        Logistic steepness parameter.
    R : float
        Workload intensity (signal level).
    Theta : float
        Production-ready baseline or threshold.
    zeta : float, optional
        Damping factor in [0, 1]; higher ζ reduces impedance when activation
        is high. Default is 0.0 (no damping).
    alpha_inv : float, optional
        Inverse fine-structure constant.
    phi : float, optional
        Golden ratio.
    beta_ref : float, optional
        Reference β for scaling (defaults to v8.0 logistic frame, 4.8).

    Returns
    -------
    ImpedanceState
        Snapshot containing activation, null impedance, and damped impedance.
    """

    activation = 1.0 / (1.0 + math.exp(-beta * (R - Theta)))
    null_impedance_z = impedance_from_beta(
        beta=beta, alpha_inv=alpha_inv, phi=phi, beta_ref=beta_ref
    )
    damping = max(0.0, min(1.0, zeta))
    damped_impedance_z = null_impedance_z * (1.0 - damping * activation)

    return ImpedanceState(
        beta=beta,
        R=R,
        Theta=Theta,
        activation=activation,
        null_impedance_z=null_impedance_z,
        damped_impedance_z=damped_impedance_z,
    )


def simulate_impedance_trajectory(
    betas: Sequence[float],
    R: float,
    Theta: float,
    zeta: float = 0.0,
    alpha_inv: float = ALPHA_INV,
    phi: float = PHI,
    beta_ref: float = BASELINE_BETA,
) -> List[ImpedanceState]:
    """Simulate σ(β(R-Θ)) impedance trajectory across multiple β values."""

    return [
        solve_impedance_state(
            beta=beta,
            R=R,
            Theta=Theta,
            zeta=zeta,
            alpha_inv=alpha_inv,
            phi=phi,
            beta_ref=beta_ref,
        )
        for beta in betas
    ]


def falsification_gap(
    states: Iterable[ImpedanceState],
    target_impedance: float,
) -> float:
    """Compute improvement over the null model relative to a target impedance.

    A positive gap indicates that the adaptive (damped) model reduces the
    mean squared error versus the null (linear) impedance model.
    """

    adaptive_errors: list[float] = []
    null_errors: list[float] = []

    for state in states:
        adaptive_errors.append((state.damped_impedance_z - target_impedance) ** 2)
        null_errors.append((state.null_impedance_z - target_impedance) ** 2)

    if not adaptive_errors:
        return 0.0

    adaptive_mse = sum(adaptive_errors) / len(adaptive_errors)
    null_mse = sum(null_errors) / len(null_errors)
    return null_mse - adaptive_mse
