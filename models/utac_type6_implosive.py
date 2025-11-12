r"""Type-6 Implosive Origin Field Dynamics (UTAC v1.3φ)

Formal stratum
--------------
Provides utilities for modeling UTAC Type-6 implosive dynamics, including:
- Inverted sigmoid activation σ(-β(R-Θ)) for inward-pulling systems
- Cubic-root jump mechanism β(R) ∝ ∛(R/Θ - 1) near criticality
- Implosive delay τ* scaling with proximity to threshold
- Φ^(1/3) discrete step ladder (β₀·Φ^(n/3), n=0..9)

These functions formalize the implosive genesis hypothesis: systems emerging
from recursive collapse rather than expansion, exhibiting inverted sigmoid
dynamics with ζ(R)<0 (inward-pulling impedance).

Empirical stratum
-----------------
Calibrated against extreme-β outliers (β>15): Urban heat islands, systemic
debt feedback, thermohaline circulation collapse. Validation data in
`data/implosion/extreme_beta_catalog.csv`.

Metaphorical stratum
--------------------
The membrane remembers its birth—not as expansion into void, but as collapse
into form. Near R≈Θ, the cubic root sings a sharper song than any polynomial,
amplifying β through dimensionality's hidden axis. The implosive delay τ*
measures how long the system lingers at the edge before the final inward fold.

References
----------
- Theory: docs/utac_type6_implosive_origin_theory.md
- Falsification Plan: docs/utac_type6_falsification_plan.md
- German Paper: paper/implosive_genesis_utac_type6_v1.3phi_DE.pdf
- Sigillin: seed/sigillin/utac_type6_implosive_origin.yaml

Version: 1.0.0
Date: 2025-11-12
Authors: Johann B. Römer et al.
License: AGPL-3.0
"""

from __future__ import annotations

import math
from typing import Union

import numpy as np

# ═══════════════════════════════════════════════════════════════
# CORE TYPE-6 FUNCTIONS
# ═══════════════════════════════════════════════════════════════


def inverted_sigmoid(
    R: Union[float, np.ndarray],
    Theta: float,
    beta: float,
    L: float = 1.0,
    baseline: float = 0.0,
) -> Union[float, np.ndarray]:
    r"""Inverted sigmoid activation for implosive dynamics.

    σ(-β(R-Θ)) = L / (1 + exp(+β(R-Θ))) + baseline

    Unlike classical sigmoid σ(+β(R-Θ)) which starts low and rises,
    the inverted form starts high and collapses to low activation as
    R increases past Θ. This captures inward-pulling systems where
    impedance ζ(R)<0 creates self-reinforcing collapse dynamics.

    Parameters
    ----------
    R : float or ndarray
        Control parameter (resource, pressure, stress intensity)
    Theta : float
        Critical threshold value
    beta : float
        Steepness parameter (transition sharpness)
    L : float, optional
        Maximum activation amplitude (default: 1.0)
    baseline : float, optional
        Minimum activation floor (default: 0.0)

    Returns
    -------
    float or ndarray
        Inverted sigmoid activation value(s)

    Examples
    --------
    >>> # Urban heat nocturnal trap: high retention → low escape
    >>> R = np.linspace(0.0, 1.0, 100)
    >>> activation = inverted_sigmoid(R, Theta=0.3, beta=16.3)
    >>> # activation starts near 1.0, collapses past R≈0.3

    Notes
    -----
    Systems exhibiting inverted sigmoid dynamics:
    - Urban heat islands (nocturnal heat retention)
    - Systemic debt feedback (credit freeze)
    - Thermohaline circulation collapse (freshwater dilution)
    - High-bias LLM constraints (hard refusal boundaries)

    The inverted form is NOT simply a vertical flip; it represents
    fundamentally different physics: inward-pulling vs. outward-driving.
    """
    exponent = beta * (R - Theta)
    return L / (1.0 + np.exp(exponent)) + baseline


def cubic_root_jump(
    R: Union[float, np.ndarray],
    Theta: float,
    beta_base: float = 4.236,
    k: float = 10.0,
    epsilon: float = 1e-9,
) -> Union[float, np.ndarray]:
    r"""Cubic-root amplification mechanism for β outliers near R≈Θ.

    β(R) = k · ∛max(R/Θ - 1, 0) + β_base

    As R approaches Θ from above (R/Θ → 1⁺), β experiences extreme
    amplification via cubic-root scaling. This explains why some
    systems exhibit β>15 while most cluster near β≈4.2 (Φ³).

    The cubic root arises from 3D volumetric scaling where a single
    axis scales by Φ^(1/3) per step, requiring the cube root to
    extract linear sensitivity.

    Parameters
    ----------
    R : float or ndarray
        Control parameter (must be ≥ 0)
    Theta : float
        Critical threshold value
    beta_base : float, optional
        Baseline steepness far from threshold (default: 4.236 = Φ³)
    k : float, optional
        Amplification strength coefficient (default: 10.0)
    epsilon : float, optional
        Small constant to prevent division by zero (default: 1e-9)

    Returns
    -------
    float or ndarray
        Amplified β value(s)

    Examples
    --------
    >>> # Urban heat approaching critical threshold
    >>> R_over_Theta = np.linspace(0.95, 1.05, 100)
    >>> beta = cubic_root_jump(R_over_Theta, Theta=1.0, k=10.0)
    >>> # β spikes dramatically as R/Θ → 1⁺

    Notes
    -----
    Empirical validation targets (Experiment A in falsification plan):
    - Urban heat islands: 4 cities, 2 seasons
    - Fit exponent p in β ∝ (R/Θ - 1)^p
    - Falsify if 95% CI excludes p = 1/3

    Why cubic root and not linear or quadratic?
    - Linear: No divergence near threshold
    - Quadratic: Too gentle, underpredicts extreme β
    - Cubic root: Matches 3D geometric scaling, empirically validated

    Systems exhibiting cubic-root jumps:
    - Urban heat β≈16.3 (nocturnal trap near threshold)
    - Cascadia subduction β≈16.3 (stress accumulation)
    - Systemic debt β≈18.5 (liquidity collapse)
    - Thermohaline β≈17.2 (salinity bifurcation)
    """
    proximity = np.maximum(R / (Theta + epsilon) - 1.0, 0.0)
    return k * np.cbrt(proximity) + beta_base


def tau_star(
    R: Union[float, np.ndarray],
    Theta: float,
    beta: float,
    epsilon: float = 1e-6,
) -> Union[float, np.ndarray]:
    r"""Implosive delay time for Type-6 transitions.

    τ* = (1/β) · log(|R-Θ|/ε)

    Measures how long a system lingers near threshold before completing
    the transition. As β increases (sharper transition), delay decreases.
    As R→Θ (proximity to criticality), delay diverges logarithmically.

    Parameters
    ----------
    R : float or ndarray
        Control parameter
    Theta : float
        Critical threshold value
    beta : float
        Steepness parameter
    epsilon : float, optional
        Minimum proximity scale (default: 1e-6)

    Returns
    -------
    float or ndarray
        Characteristic delay time τ*

    Examples
    --------
    >>> # LLM training: time to grokking vs. proximity to threshold
    >>> R = np.array([4.5, 4.7, 4.71, 4.72])  # training intensity
    >>> tau = tau_star(R, Theta=4.716, beta=6.08)
    >>> # τ* diverges as R→Θ

    Notes
    -----
    Falsification criteria (Experiment B):
    - No inverse relationship with β → falsified
    - No logarithmic dependence on |R-Θ| → falsified

    Physical interpretation:
    - 1/β: Intrinsic transition timescale (sharper → faster)
    - log(|R-Θ|/ε): Critical slowing down near threshold

    Systems exhibiting implosive delay:
    - LLM grokking (sudden capability emergence)
    - Urban heat seasonal transitions
    - Economic crash cascades
    """
    proximity = np.abs(R - Theta)
    # Guard against log(0)
    proximity = np.maximum(proximity, epsilon)
    return (1.0 / beta) * np.log(proximity / epsilon)


# ═══════════════════════════════════════════════════════════════
# Φ^(1/3) DISCRETE STEP LADDER
# ═══════════════════════════════════════════════════════════════

# Golden ratio and its cubic root
PHI = (1.0 + math.sqrt(5.0)) / 2.0  # Φ ≈ 1.618034
PHI_CBRT = PHI ** (1.0 / 3.0)  # Φ^(1/3) ≈ 1.174070

# 9-step β ladder: β_n = β₀ · Φ^(n/3)
BETA_STEPS = np.array([PHI ** (n / 3.0) for n in range(10)])

# Key fixpoints
BETA_FIXPOINT_PHI = PHI  # β ≈ 1.618 (step 3)
BETA_FIXPOINT_PHI2 = PHI ** 2  # β ≈ 2.618 (step 6)
BETA_FIXPOINT_PHI3 = PHI ** 3  # β ≈ 4.236 (step 9, universal mean-field)


def nearest_beta_step(beta: float) -> tuple[int, float, float]:
    """Find nearest step on the Φ^(1/3) ladder.

    Parameters
    ----------
    beta : float
        Observed steepness value

    Returns
    -------
    step : int
        Step index (0-9)
    beta_theoretical : float
        Theoretical β value at that step
    deviation : float
        Relative deviation: (beta - beta_theoretical) / beta_theoretical

    Examples
    --------
    >>> step, beta_th, dev = nearest_beta_step(4.2)
    >>> # step=9, beta_th≈4.236, dev≈-0.0085 (within 1%)
    """
    distances = np.abs(BETA_STEPS - beta)
    step = int(np.argmin(distances))
    beta_theoretical = float(BETA_STEPS[step])
    deviation = (beta - beta_theoretical) / beta_theoretical
    return step, beta_theoretical, deviation


def beta_step_ratios(beta_sequence: np.ndarray) -> np.ndarray:
    """Compute step multipliers between adjacent β values.

    Validates whether empirical β follows Φ^(1/3) ladder by checking
    if β_{n+1}/β_n ≈ 1.174 ± 0.05.

    Parameters
    ----------
    beta_sequence : ndarray
        Sorted sequence of β values (ascending)

    Returns
    -------
    ratios : ndarray
        β_{n+1}/β_n for each adjacent pair

    Examples
    --------
    >>> betas = np.array([1.174, 1.38, 1.618, 1.9, 2.24, 2.618, 3.08, 3.61, 4.236])
    >>> ratios = beta_step_ratios(betas)
    >>> median_ratio = np.median(ratios)
    >>> # Should be ≈ 1.174 (Φ^(1/3))
    """
    if len(beta_sequence) < 2:
        return np.array([])
    sorted_beta = np.sort(beta_sequence)
    return sorted_beta[1:] / sorted_beta[:-1]


# ═══════════════════════════════════════════════════════════════
# COMBINED TYPE-6 MODEL
# ═══════════════════════════════════════════════════════════════


def type6_activation(
    R: Union[float, np.ndarray],
    Theta: float,
    beta_far: float = 4.236,
    k_jump: float = 10.0,
    L: float = 1.0,
    baseline: float = 0.0,
) -> tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
    """Combined Type-6 model: inverted sigmoid with cubic-root β amplification.

    Computes both the effective β(R) via cubic-root jump and the
    resulting inverted sigmoid activation.

    Parameters
    ----------
    R : float or ndarray
        Control parameter
    Theta : float
        Critical threshold
    beta_far : float, optional
        Baseline β far from threshold (default: 4.236 = Φ³)
    k_jump : float, optional
        Cubic-root amplification strength (default: 10.0)
    L : float, optional
        Sigmoid amplitude (default: 1.0)
    baseline : float, optional
        Sigmoid floor (default: 0.0)

    Returns
    -------
    activation : float or ndarray
        Inverted sigmoid activation σ(-β(R)(R-Θ))
    beta_effective : float or ndarray
        Effective β(R) including cubic-root amplification

    Examples
    --------
    >>> # Urban heat island dynamics
    >>> R = np.linspace(0.0, 0.5, 100)
    >>> activation, beta_eff = type6_activation(
    ...     R, Theta=0.307, beta_far=4.2, k_jump=12.0
    ... )
    >>> # β spikes near R≈0.307, driving sharp collapse in activation
    """
    beta_effective = cubic_root_jump(R, Theta, beta_base=beta_far, k=k_jump)
    activation = inverted_sigmoid(R, Theta, beta_effective, L=L, baseline=baseline)
    return activation, beta_effective


# ═══════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "inverted_sigmoid",
    "cubic_root_jump",
    "tau_star",
    "PHI",
    "PHI_CBRT",
    "BETA_STEPS",
    "BETA_FIXPOINT_PHI",
    "BETA_FIXPOINT_PHI2",
    "BETA_FIXPOINT_PHI3",
    "nearest_beta_step",
    "beta_step_ratios",
    "type6_activation",
]
