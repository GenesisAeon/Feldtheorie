"""
τ* (Tau-Star) Safety-Delay Mechanism

RK4-compatible temporal buffer for Type-VI implosive field dynamics.

Usage:
    from pipelines.fit_tau_star import compute_tau_star, apply_safety_delay

    # Compute delay for current field state
    tau_star = compute_tau_star(R, Theta, beta)

    # Apply delay in RK4 integration
    R_delayed = apply_safety_delay(R, R_prev, tau_star, dt)
"""
from __future__ import annotations

import math
from typing import Union

import numpy as np


def compute_tau_star(
    R: Union[float, np.ndarray],
    Theta: float,
    beta: float = 4.8,
    k: float = 0.1,
) -> Union[float, np.ndarray]:
    """
    Compute τ* safety delay for implosive field dynamics.

    τ* = k · |Θ - R|

    Where:
    - R: Current field coordinate (Resource/Reality)
    - Θ: Activation threshold
    - k: Delay coefficient (default 0.1)
    - β: Field steepness (for future coupling, not used in basic formula)

    Args:
        R: Field coordinate (scalar or array)
        Theta: Threshold value
        beta: Logistic steepness (reserved for advanced coupling)
        k: Delay coefficient

    Returns:
        τ* delay value(s)

    Example:
        >>> tau = compute_tau_star(R=0.3, Theta=0.5, beta=4.8)
        >>> print(f"τ* = {tau:.4f}")
        τ* = 0.0200
    """
    return k * np.abs(Theta - R)


def apply_safety_delay(
    R_current: Union[float, np.ndarray],
    R_previous: Union[float, np.ndarray],
    tau_star: Union[float, np.ndarray],
    dt: float,
    mode: str = "exponential",
) -> Union[float, np.ndarray]:
    """
    Apply τ* safety delay to field evolution in RK4 integration.

    Delays field response to prevent instantaneous collapse in ζ<0 scenarios.

    Modes:
    - "exponential": R_delayed = R_prev + (R - R_prev) · (1 - exp(-dt/τ*))
    - "linear": R_delayed = R_prev + (R - R_prev) · min(dt/τ*, 1.0)

    Args:
        R_current: Current field value from RK4 step
        R_previous: Previous field value
        tau_star: Computed τ* delay
        dt: Time step
        mode: Delay mode ("exponential" or "linear")

    Returns:
        Delayed field value R_delayed

    Example:
        >>> R_delayed = apply_safety_delay(
        ...     R_current=0.3,
        ...     R_previous=0.5,
        ...     tau_star=0.02,
        ...     dt=0.001,
        ...     mode="exponential"
        ... )
    """
    # Avoid division by zero
    epsilon = 1e-10
    tau_star_safe = np.maximum(tau_star, epsilon)

    if mode == "exponential":
        # Exponential smoothing: prevents discontinuities
        damping = 1.0 - np.exp(-dt / tau_star_safe)
        R_delayed = R_previous + (R_current - R_previous) * damping

    elif mode == "linear":
        # Linear interpolation: simpler but may cause discontinuities
        alpha = np.minimum(dt / tau_star_safe, 1.0)
        R_delayed = R_previous + (R_current - R_previous) * alpha

    else:
        raise ValueError(f"Unknown delay mode: {mode}. Use 'exponential' or 'linear'")

    return R_delayed


def compute_zeta_risk(
    R: Union[float, np.ndarray],
    Theta: float,
    beta: float,
) -> Union[float, np.ndarray]:
    """
    Compute ζ-risk factor for implosive scenarios.

    ζ(R) = σ(β(R - Θ)) - 1.0

    When ζ < 0: Implosive regime (needs τ* protection)
    When ζ ≥ 0: Safe regime

    Args:
        R: Field coordinate
        Theta: Threshold
        beta: Steepness

    Returns:
        ζ-risk value(s)
    """
    # Logistic function σ(β(R-Θ))
    sigma = 1.0 / (1.0 + np.exp(-beta * (R - Theta)))

    # ζ = σ - 1.0 (negative when R < Θ)
    zeta = sigma - 1.0

    return zeta


def rk4_step_with_tau_star(
    R: float,
    dR_dt_func,
    dt: float,
    Theta: float,
    beta: float,
    R_history: list[float] | None = None,
) -> tuple[float, float]:
    """
    RK4 integration step with τ* safety delay.

    Combines standard RK4 with τ*-delayed response for implosive fields.

    Args:
        R: Current field value
        dR_dt_func: Function(R, t) -> dR/dt
        dt: Time step
        Theta: Activation threshold
        beta: Field steepness
        R_history: Previous R values for delay calculation

    Returns:
        (R_next, tau_star) tuple
    """
    # Standard RK4 coefficients
    k1 = dR_dt_func(R)
    k2 = dR_dt_func(R + 0.5 * dt * k1)
    k3 = dR_dt_func(R + 0.5 * dt * k2)
    k4 = dR_dt_func(R + dt * k3)

    # RK4 update (undelayed)
    R_rk4 = R + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

    # Compute τ* for current state
    tau_star = compute_tau_star(R, Theta, beta)

    # Apply safety delay
    R_prev = R_history[-1] if R_history else R
    R_next = apply_safety_delay(R_rk4, R_prev, tau_star, dt, mode="exponential")

    return R_next, tau_star


__all__ = [
    "compute_tau_star",
    "apply_safety_delay",
    "compute_zeta_risk",
    "rk4_step_with_tau_star",
]
