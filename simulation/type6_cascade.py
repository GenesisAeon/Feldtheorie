"""
Type-VI Implosive Cascade Simulator

Implements cubic-root jump dynamics for systems with negative damping (ζ < 0).

Based on:
- simulation/notes/type6_cubic_jump_outline.md
- METRICS.md Section 8 (Type-VI Classification)
- pipelines/fit_tau_star/ (τ* safety mechanism)

Version: v6.0.0-alpha
Author: Johann Benjamin Römer, MOR Framework
Date: 2025-11-26
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipelines.fit_tau_star import (
    apply_safety_delay,
    compute_tau_star,
    compute_zeta_risk,
)


@dataclass
class Type6Parameters:
    """Parameters for Type-VI implosive cascade simulation.

    Attributes:
        domain: System domain (climate, finance, neuro, etc.)
        R_init: Initial field coordinate (e.g., temperature anomaly in °C)
        Theta: Activation threshold
        beta: Logistic steepness
        zeta_0: Negative damping coefficient (must be < 0 for Type-VI)
        gamma: Cubic-jump strength
        dt: Time step
        T_max: Maximum simulation time
        crep_threshold: Auto-halt threshold (default 0.95)
    """

    domain: str
    R_init: float
    Theta: float
    beta: float
    zeta_0: float
    gamma: float
    dt: float = 0.01
    T_max: float = 100.0
    crep_threshold: float = 0.95

    def __post_init__(self):
        """Validate parameters."""
        if self.zeta_0 >= 0:
            raise ValueError(
                f"Type-VI requires negative damping: zeta_0={self.zeta_0} >= 0"
            )
        if self.beta <= 0:
            raise ValueError(f"beta must be positive: beta={self.beta}")
        if self.gamma < 0:
            raise ValueError(f"gamma must be non-negative: gamma={self.gamma}")


@dataclass
class SimulationState:
    """Snapshot of simulation state at time t.

    Attributes:
        t: Time
        R: Field coordinate
        zeta: ζ-risk factor
        tau_star: τ* safety delay
        crep_index: CREP index (0-1 scale)
        dR_dt: Field velocity
    """

    t: float
    R: float
    zeta: float
    tau_star: float
    crep_index: float
    dR_dt: float


def sigmoid_inverted(beta: float, R: float, Theta: float) -> float:
    """Inverted sigmoid for Type-VI dynamics.

    Standard sigmoid: σ(β(R-Θ)) = 1 / (1 + exp(-β(R-Θ)))
    Type-VI inverted: 1 - σ(β(R-Θ))

    Args:
        beta: Logistic steepness
        R: Current field value
        Theta: Threshold

    Returns:
        Inverted sigmoid value (0-1)
    """
    sigmoid = 1.0 / (1.0 + np.exp(-beta * (R - Theta)))
    return 1.0 - sigmoid


def compute_crep_index(
    R: float, Theta: float, beta: float, zeta: float
) -> float:
    """Compute CREP (Collapse-Resonance-Expansion Potential) index.

    CREP = α_C·C + α_R·R_resonance + α_E·E_rebound

    Where:
    - C (Collapse potential): max(0, -ζ) · β
    - R_resonance (Resonance window): exp(-|β(R-Θ)|)
    - E_rebound (Expansion recovery): Simplified to 0.2

    Standard weights: α_C=0.5, α_R=0.3, α_E=0.2

    Args:
        R: Current field value
        Theta: Threshold
        beta: Logistic steepness
        zeta: ζ-risk factor

    Returns:
        CREP index in [0, 1] range
    """
    # Components (see METRICS.md Section 8.2)
    # Normalized collapse potential (divide by β to keep in reasonable range)
    C_raw = max(0, -zeta) * beta
    C = min(C_raw / (beta + 1.0), 1.0)  # Normalize to [0, 1]

    R_resonance = np.exp(-abs(beta * (R - Theta)))  # Resonance window
    E_rebound = 0.2  # Simplified (should integrate sigmoid for full version)

    # Weighted sum
    alpha_C, alpha_R, alpha_E = 0.5, 0.3, 0.2
    crep = alpha_C * C + alpha_R * R_resonance + alpha_E * E_rebound

    return min(crep, 1.0)  # Clip to [0, 1]


def cubic_jump_term(R: float, Theta: float, gamma: float) -> float:
    """Compute cubic-root jump term.

    For Type-VI: ΔR ∝ (R - Θ)^(1/3)

    Args:
        R: Current field value
        Theta: Threshold
        gamma: Jump strength coefficient

    Returns:
        Cubic-jump contribution
    """
    if R > Theta:
        # Cubic-root scaling for supercritical regime
        delta = R - Theta
        return gamma * (delta ** (1.0 / 3.0))
    else:
        # No jump below threshold
        return 0.0


def field_velocity(
    R: float,
    Theta: float,
    beta: float,
    zeta_0: float,
    gamma: float,
) -> float:
    """Compute dR/dt for Type-VI field dynamics.

    dR/dt = -ζ₀·R + S_inv(R) + cubic_jump

    Where:
    - ζ₀ < 0: Negative damping (implosive)
    - S_inv(R): Inverted sigmoid (collapse modulation)
    - cubic_jump: ΔR ∝ (R-Θ)^(1/3)

    Args:
        R: Current field value
        Theta: Threshold
        beta: Logistic steepness
        zeta_0: Negative damping coefficient
        gamma: Cubic-jump strength

    Returns:
        Field velocity dR/dt
    """
    # Negative damping term
    damping = -zeta_0 * R

    # Inverted sigmoid modulation
    sigmoid_inv = sigmoid_inverted(beta, R, Theta)

    # Cubic-root jump
    jump = cubic_jump_term(R, Theta, gamma)

    return damping + sigmoid_inv + jump


def rk4_step(
    R: float,
    dt: float,
    params: Type6Parameters,
) -> float:
    """Standard RK4 integration step (without τ* delay).

    Args:
        R: Current field value
        dt: Time step
        params: Simulation parameters

    Returns:
        Updated field value R_next
    """
    # Define velocity function
    def f(r):
        return field_velocity(r, params.Theta, params.beta, params.zeta_0, params.gamma)

    # RK4 coefficients
    k1 = f(R)
    k2 = f(R + 0.5 * dt * k1)
    k3 = f(R + 0.5 * dt * k2)
    k4 = f(R + dt * k3)

    # RK4 update
    R_next = R + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

    return R_next


def simulate_type6_cascade(
    params: Type6Parameters,
    verbose: bool = True,
) -> list[SimulationState]:
    """Simulate Type-VI implosive cascade with τ* safety delay.

    Args:
        params: Simulation parameters
        verbose: Print progress messages

    Returns:
        List of SimulationState snapshots

    Example:
        >>> params = Type6Parameters(
        ...     domain="climate",
        ...     R_init=1.8,
        ...     Theta=2.1,
        ...     beta=4.2,
        ...     zeta_0=-0.15,
        ...     gamma=0.5,
        ...     dt=0.01,
        ...     T_max=100.0,
        ... )
        >>> history = simulate_type6_cascade(params)
        >>> print(f"Final CREP: {history[-1].crep_index:.3f}")
    """
    if verbose:
        print(f"🌀 Type-VI Cascade Simulation: {params.domain}")
        print(f"   R_init={params.R_init:.2f}, Θ={params.Theta:.2f}, β={params.beta:.2f}")
        print(f"   ζ₀={params.zeta_0:.3f} (negative damping)")
        print(f"   γ={params.gamma:.2f} (cubic-jump)")

    R = params.R_init
    R_prev = params.R_init
    t = 0.0
    history: list[SimulationState] = []

    # Initial state
    zeta = compute_zeta_risk(R, params.Theta, params.beta)
    tau_star = compute_tau_star(R, params.Theta, params.beta)
    crep = compute_crep_index(R, params.Theta, params.beta, zeta)
    dR_dt = field_velocity(R, params.Theta, params.beta, params.zeta_0, params.gamma)

    history.append(
        SimulationState(
            t=t,
            R=R,
            zeta=zeta,
            tau_star=tau_star,
            crep_index=crep,
            dR_dt=dR_dt,
        )
    )

    # Main integration loop
    n_steps = int(params.T_max / params.dt)
    for step in range(1, n_steps + 1):
        t = step * params.dt

        # Standard RK4 step
        R_next = rk4_step(R, params.dt, params)

        # Compute diagnostics
        zeta = compute_zeta_risk(R, params.Theta, params.beta)
        tau_star = compute_tau_star(R, params.Theta, params.beta)
        crep = compute_crep_index(R, params.Theta, params.beta, zeta)

        # Apply τ* safety delay for ζ < 0
        if zeta < 0:
            R_next = apply_safety_delay(
                R_next, R_prev, tau_star, params.dt, mode="exponential"
            )

        # Compute velocity
        dR_dt = field_velocity(R_next, params.Theta, params.beta, params.zeta_0, params.gamma)

        # Store state
        history.append(
            SimulationState(
                t=t,
                R=R_next,
                zeta=zeta,
                tau_star=tau_star,
                crep_index=crep,
                dR_dt=dR_dt,
            )
        )

        # Safety check: halt if CREP exceeds threshold
        if crep > params.crep_threshold:
            if verbose:
                print(
                    f"⚠️  CRITICAL: CREP > {params.crep_threshold} at t={t:.2f}, halting simulation"
                )
                print(f"   Final R={R_next:.3f}, CREP={crep:.3f}")
            break

        # Update
        R_prev = R
        R = R_next

        # Progress report (every 10% of T_max)
        if verbose and step % (n_steps // 10) == 0:
            progress = 100 * step / n_steps
            print(
                f"   [{progress:5.1f}%] t={t:6.2f}, R={R:6.3f}, ζ={zeta:+.3f}, CREP={crep:.3f}, τ*={tau_star:.4f}"
            )

    if verbose:
        final = history[-1]
        print("\n✅ Simulation complete")
        print(f"   Final time: t={final.t:.2f}")
        print(f"   Final R: {final.R:.3f}")
        print(f"   Final CREP: {final.crep_index:.3f}")
        print(f"   Total steps: {len(history)}")

    return history


# ============================================================================
# ARCTIC METHANE RELEASE CASE STUDY
# ============================================================================

ARCTIC_METHANE_PARAMS = Type6Parameters(
    domain="climate",
    R_init=1.8,  # Current global warming (°C above pre-industrial)
    Theta=2.1,  # Permafrost threshold (°C)
    beta=4.2,  # Logistic steepness
    zeta_0=-0.15,  # Negative damping (methane feedback)
    gamma=0.5,  # Cubic-jump strength
    dt=0.01,  # Time step (years)
    T_max=50.0,  # Simulate 50 years
    crep_threshold=0.95,  # Halt at extreme collapse
)


def run_arctic_methane_simulation(verbose: bool = True) -> list[SimulationState]:
    """Run Arctic methane release cascade simulation.

    This is the canonical Type-VI example from METRICS.md Section 8.3.

    Returns:
        Simulation history

    Example:
        >>> history = run_arctic_methane_simulation()
        >>> # Analyze cubic-root scaling
        >>> validate_cubic_root_scaling(history)
    """
    return simulate_type6_cascade(ARCTIC_METHANE_PARAMS, verbose=verbose)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Type-VI Implosive Cascade Simulator"
    )
    parser.add_argument(
        "--domain",
        type=str,
        default="climate",
        help="System domain (climate, finance, neuro, etc.)",
    )
    parser.add_argument(
        "--R-init", type=float, default=1.8, help="Initial field coordinate"
    )
    parser.add_argument("--Theta", type=float, default=2.1, help="Activation threshold")
    parser.add_argument("--beta", type=float, default=4.2, help="Logistic steepness")
    parser.add_argument(
        "--zeta-0", type=float, default=-0.15, help="Negative damping coefficient"
    )
    parser.add_argument("--gamma", type=float, default=0.5, help="Cubic-jump strength")
    parser.add_argument("--dt", type=float, default=0.01, help="Time step")
    parser.add_argument("--T-max", type=float, default=50.0, help="Maximum time")
    parser.add_argument(
        "--preset",
        type=str,
        default=None,
        choices=["arctic-methane"],
        help="Use preset parameters",
    )

    args = parser.parse_args()

    if args.preset == "arctic-methane":
        print("📊 Running Arctic Methane Release simulation (preset)\n")
        params = ARCTIC_METHANE_PARAMS
        history = run_arctic_methane_simulation()
    else:
        params = Type6Parameters(
            domain=args.domain,
            R_init=args.R_init,
            Theta=args.Theta,
            beta=args.beta,
            zeta_0=args.zeta_0,
            gamma=args.gamma,
            dt=args.dt,
            T_max=args.T_max,
        )
        history = simulate_type6_cascade(params)

    # Write summary to metrics/beta_evolution.csv
    from datetime import datetime, timezone

    final = history[-1]
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    logfile = Path(__file__).parent.parent / "metrics" / "beta_evolution.csv"
    with open(logfile, "a") as f:
        # Check if we need to write data (not just comments)
        f.write(
            f'{timestamp},{params.domain},{final.R:.4f},{params.Theta:.4f},'
            f'{params.beta:.4f},{final.zeta:.4f},{final.tau_star:.6f},'
            f'{final.crep_index:.4f},"Type-VI cascade simulation"\n'
        )

    print(f"\n📝 Logged to {logfile}")
    print("\n🎯 Next: Run visualization with:")
    print("   python scripts/plot_type6_cascade.py")
