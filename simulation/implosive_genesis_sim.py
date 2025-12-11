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
from collections.abc import Iterable


def inverted_sigmoid(r: Iterable[float], beta: float = 4.0, theta: float = 0.0) -> list[float]:
    """Evaluate the inverted sigmoid S(R) = 1 - σ(β(R-Θ))."""

    return [1.0 - 1.0 / (1.0 + math.exp(-beta * (value - theta))) for value in r]


def phase_space_trajectory(
    r_start: float,
    r_end: float,
    steps: int = 50,
    beta: float = 4.0,
    theta: float = 0.0,
    damping: float = 0.05,
    enable_safety_delay: bool = True,
    tau_star_factor: float = 0.1,
) -> tuple[list[float], list[float], list[float], list[float]]:
    """Generate phase-space data for the implosive genesis curve.

    Returns a tuple of (R values, inverted sigmoid S(R), velocity field, τ* delays)
    where the velocity is modeled as v = -ζ0·R + S(R) to capture contraction
    balanced by the inverted response.

    For Type-VI systems (ζ < 0), the safety-delay buffer τ* prevents numerical
    divergence and provides intervention window.

    Args:
        r_start: Starting R value
        r_end: Ending R value
        steps: Number of trajectory points
        beta: Logistic steepness
        theta: Threshold parameter
        damping: Damping coefficient ζ0 (negative for implosive dynamics)
        enable_safety_delay: Whether to apply τ* buffer (required for ζ < 0)
        tau_star_factor: Multiplier for τ* = tau_star_factor * |Θ - R|

    Returns:
        Tuple of (R values, S(R) values, velocity, τ* delays)
    """

    if steps <= 1:
        raise ValueError("steps must be greater than 1 to form a trajectory.")

    # SAFETY CHECK: Require τ* for negative damping (Type-VI)
    if damping < 0 and not enable_safety_delay:
        raise ValueError(
            "Safety-delay buffer (τ*) is MANDATORY for negative damping (ζ < 0). "
            "Set enable_safety_delay=True or use positive damping. "
            "See AGENTS.md §Type-VI Computational Safeguards."
        )

    r_values = [r_start + (r_end - r_start) * i / (steps - 1) for i in range(steps)]
    s_values = inverted_sigmoid(r_values, beta=beta, theta=theta)

    # Compute velocity with optional safety-delay buffer
    velocity = []
    tau_star_delays = []

    for r, s in zip(r_values, s_values):
        # Base velocity: v = -ζ0·R + S(R)
        v_base = -damping * r + s

        # Safety-delay buffer: τ* = tau_star_factor * |Θ - R|
        tau_star = tau_star_factor * abs(theta - r) if enable_safety_delay else 0.0

        # Apply delay: reduces velocity near threshold to prevent divergence
        # Delay factor: exp(-τ*) smoothly transitions from full delay (τ*→∞) to no delay (τ*→0)
        delay_factor = math.exp(-tau_star) if enable_safety_delay else 1.0
        v_delayed = v_base * delay_factor

        velocity.append(v_delayed)
        tau_star_delays.append(tau_star)

    return r_values, s_values, velocity, tau_star_delays


def compute_crep_index(
    r_values: Iterable[float],
    beta: float,
    theta: float,
    damping: float,
    alpha_c: float = 0.5,
    alpha_r: float = 0.3,
    alpha_e: float = 0.2,
) -> float:
    """
    Compute CREP (Collapse-Resonance-Expansion Potential) index.

    CREP quantifies implosive risk for Type-VI systems across three phases:
    - C: Collapse potential (negative damping strength)
    - R: Resonance window (proximity to threshold)
    - E: Expansion recovery (post-implosive rebound capacity)

    Args:
        r_values: Field coordinate values
        beta: Logistic steepness
        theta: Threshold parameter
        damping: Damping coefficient (ζ0)
        alpha_c, alpha_r, alpha_e: Component weights (should sum to 1.0)

    Returns:
        CREP index in [0, 1] range
        - 0.0-0.3: Stable expansion (low risk)
        - 0.3-0.6: Transition zone (medium risk)
        - 0.6-0.8: High implosive risk
        - 0.8-1.0: Critical collapse

    Reference:
        See METRICS.md §8.2 for full specification
    """
    r_list = list(r_values)
    if not r_list:
        return 0.0

    # Component C: Collapse potential
    # C = max(0, -ζ) · β (measures negative damping strength)
    C = max(0.0, -damping) * beta
    C_normalized = min(1.0, C / 10.0)  # Normalize: β ≈ 4.8, max(-ζ) ≈ 2

    # Component R: Resonance window
    # R = exp(-|β(R-Θ)|) peaks at threshold
    resonance_values = [math.exp(-abs(beta * (r - theta))) for r in r_list]
    R = max(resonance_values)  # Peak resonance

    # Component E: Expansion recovery
    # E = ∫[Θ, R_max] σ(β(R-Θ)) dR (post-implosive expansion capacity)
    r_max = max(r_list)
    if r_max > theta:
        # Numerical integration using trapezoidal rule
        expansion_zone = [r for r in r_list if r >= theta]
        if expansion_zone:
            sigma_values = [1.0 / (1.0 + math.exp(-beta * (r - theta))) for r in expansion_zone]
            E_raw = sum(sigma_values) * (r_max - theta) / len(sigma_values)
            E_normalized = min(1.0, E_raw)
        else:
            E_normalized = 0.0
    else:
        E_normalized = 0.0

    # Weighted CREP index
    CREP = alpha_c * C_normalized + alpha_r * R + alpha_e * E_normalized

    return min(1.0, max(0.0, CREP))  # Clamp to [0, 1]
