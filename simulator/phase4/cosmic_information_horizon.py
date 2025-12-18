"""Cosmic Information Horizon with Hex-Resonance Phase Transition.

This module simulates information accessibility near an event horizon,
using the σ(β(R-Θ)) sigmoid model from the V6 framework. The transition
steepness is locked to HEX_RESONANCE_BETA ≈ 4.779.

Physical Model:
    The information density R(r) decays as matter approaches the horizon.
    Accessibility is governed by:

        P_access(r) = σ(β(R(r) - Θ))
                    = 1 / (1 + exp(-β(R(r) - Θ)))

    Where:
    - R(r): Information readiness/density at radius r
    - Θ = 0.66: Critical threshold (consciousness integration barrier)
    - β = HEX_RESONANCE_BETA: Transition steepness (digital-physics baseline)

Interpretation:
    In the OIPK framework, the event horizon represents the boundary where
    orthogonal time-flows become causally disconnected. The sigmoid transition
    models the "soft horizon" experienced by consciousness - not a sharp cutoff,
    but a gradual phase transition governed by hex-resonance.

    This mirrors Hawking radiation: information is not lost instantly, but
    decays through a β-controlled gradient.

Usage:
    from simulator.phase4.cosmic_information_horizon import run_simulation
    results = run_simulation(horizon_radius=10.0, duration=100.0)
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

# Add models path for importing unified_constants
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "models"))

try:
    from unified_constants import HEX_RESONANCE_BETA, verify_hex_alignment
except ImportError:
    HEX_RESONANCE_BETA = 16 ** (1 / math.sqrt(math.pi))

    def verify_hex_alignment(empirical_beta, tolerance=0.1):
        deviation = abs(empirical_beta - HEX_RESONANCE_BETA)
        score = max(0.0, 1.0 - (deviation / tolerance))
        return {
            "target_beta": HEX_RESONANCE_BETA,
            "empirical_beta": empirical_beta,
            "deviation": deviation,
            "resonance_score": round(score, 4),
            "status": "RESONANT" if deviation <= tolerance else "DISSONANT"
        }


def sigmoid(x: float, beta: float, theta: float) -> float:
    """Compute logistic sigmoid σ(β(x - θ)).

    Parameters
    ----------
    x : float
        Input variable (readiness, information density, etc.)
    beta : float
        Steepness parameter (HEX_RESONANCE_BETA)
    theta : float
        Threshold position

    Returns
    -------
    float
        Sigmoid activation ∈ [0, 1]
    """
    return 1.0 / (1.0 + math.exp(-beta * (x - theta)))


def information_density_profile(
    r: np.ndarray,
    r_horizon: float,
    scale_length: float = 2.0,
    far_field_density: float = 1.0
) -> np.ndarray:
    """Compute information density R(r) as function of radius.

    The density follows an exponential decay near the horizon:
        R(r) = R_∞ · exp(-(r_h - r) / λ)  for r < r_h
        R(r) = R_∞                         for r > r_h

    Parameters
    ----------
    r : np.ndarray
        Radial coordinates
    r_horizon : float
        Event horizon radius
    scale_length : float
        Decay scale length λ
    far_field_density : float
        Asymptotic information density far from horizon

    Returns
    -------
    np.ndarray
        Information density R(r) at each radius
    """
    R = np.ones_like(r) * far_field_density

    # Exponential decay inside horizon
    inside = r < r_horizon
    R[inside] = far_field_density * np.exp((r[inside] - r_horizon) / scale_length)

    return R


def compute_accessibility(
    R: np.ndarray,
    beta: float,
    theta: float
) -> np.ndarray:
    """Compute information accessibility P(R) = σ(β(R - Θ)).

    Parameters
    ----------
    R : np.ndarray
        Information density values
    beta : float
        Hex-resonance steepness
    theta : float
        Critical threshold

    Returns
    -------
    np.ndarray
        Accessibility probability ∈ [0, 1]
    """
    return 1.0 / (1.0 + np.exp(-beta * (R - theta)))


def hawking_evaporation(
    M0: float,
    t: float,
    evaporation_constant: float = 0.01
) -> float:
    """Model black hole mass loss via Hawking radiation.

    Simplified model:
        M(t) = M_0 · exp(-t/τ_evap)

    Parameters
    ----------
    M0 : float
        Initial black hole mass
    t : float
        Time elapsed
    evaporation_constant : float
        Evaporation timescale parameter

    Returns
    -------
    float
        Remaining mass M(t)
    """
    tau_evap = M0 / evaporation_constant
    return M0 * math.exp(-t / tau_evap)


def schwarzschild_radius(mass: float, gravitational_constant: float = 1.0) -> float:
    """Compute Schwarzschild radius r_s = 2GM/c².

    In geometric units (G=c=1):
        r_s = 2M

    Parameters
    ----------
    mass : float
        Black hole mass
    gravitational_constant : float
        Gravitational constant (normalized)

    Returns
    -------
    float
        Event horizon radius
    """
    return 2.0 * gravitational_constant * mass


def run_simulation(
    horizon_radius: float = 10.0,
    duration: float = 100.0,
    dt: float = 0.5,
    n_radial_points: int = 200,
    theta: float = 0.66,
    evaporation_enabled: bool = True,
    snapshot_interval: int = 20,
    verbose: bool = True
) -> dict:
    """Run cosmic information horizon simulation with hex-resonance.

    Parameters
    ----------
    horizon_radius : float
        Initial event horizon radius (Schwarzschild)
    duration : float
        Total simulation time
    dt : float
        Time step size
    n_radial_points : int
        Number of spatial sample points
    theta : float
        Critical information threshold (0.66 from Neuro-Kosmos Bridge)
    evaporation_enabled : bool
        Include Hawking evaporation dynamics
    snapshot_interval : int
        Steps between snapshots
    verbose : bool
        Print progress information

    Returns
    -------
    dict
        Simulation results with telemetry:
        - 'config': Simulation parameters
        - 'beta_hex': Used steepness
        - 'resonance_check': Alignment verification
        - 'snapshots': Time evolution of horizon properties
        - 'final_state': Final accessibility profile
    """
    # Setup radial grid (from center to 3× horizon radius)
    r_max = 3.0 * horizon_radius
    r = np.linspace(0.0, r_max, n_radial_points)

    # Use HEX_RESONANCE_BETA as phase transition steepness
    beta = HEX_RESONANCE_BETA

    # Initial black hole mass (from horizon radius)
    M0 = horizon_radius / 2.0  # r_s = 2M

    # Time evolution
    n_steps = int(duration / dt)
    snapshots = []

    if verbose:
        print(f"🌌 Starting Cosmic Information Horizon Simulation")
        print(f"   β_hex = {beta:.5f}")
        print(f"   Θ (threshold) = {theta:.2f}")
        print(f"   Initial Horizon: r_s = {horizon_radius:.2f}")
        print(f"   Duration: {duration:.1f} time units ({n_steps} steps)")
        print(f"   Hawking Evaporation: {'ENABLED' if evaporation_enabled else 'DISABLED'}")

    for step in range(n_steps):
        t = step * dt

        # Compute current mass (with Hawking evaporation)
        if evaporation_enabled:
            M_current = hawking_evaporation(M0, t, evaporation_constant=0.01)
        else:
            M_current = M0

        # Update horizon radius
        r_horizon = schwarzschild_radius(M_current)

        # Compute information density profile
        R_profile = information_density_profile(r, r_horizon, scale_length=2.0)

        # Compute accessibility
        P_access = compute_accessibility(R_profile, beta, theta)

        # Compute information flux across horizon
        # (Information that remains accessible despite being near horizon)
        horizon_idx = np.argmin(np.abs(r - r_horizon))
        info_retention = P_access[horizon_idx] if horizon_idx < len(P_access) else 0.0

        # Total accessible information (integral)
        total_accessible_info = np.trapz(P_access * R_profile, r)

        # Take snapshots
        if step % snapshot_interval == 0:
            # Find transition zone (where P_access ≈ 0.5)
            transition_indices = np.where((P_access > 0.4) & (P_access < 0.6))[0]
            transition_width = len(transition_indices) * (r[1] - r[0]) if len(transition_indices) > 0 else 0.0

            snapshots.append({
                "time": t,
                "mass": M_current,
                "horizon_radius": r_horizon,
                "info_retention_at_horizon": float(info_retention),
                "total_accessible_info": float(total_accessible_info),
                "transition_width": float(transition_width)
            })

            if verbose and step % (snapshot_interval * 5) == 0:
                print(f"   t={t:6.1f} | M={M_current:.3f} | r_s={r_horizon:.3f} | "
                      f"Info@Horizon: {info_retention:.3f} | "
                      f"Total Accessible: {total_accessible_info:.2f}")

    # Final state analysis
    final_R = information_density_profile(r, r_horizon, scale_length=2.0)
    final_P = compute_accessibility(final_R, beta, theta)

    resonance_check = verify_hex_alignment(beta, tolerance=0.01)

    # Check if horizon has evaporated
    horizon_evaporated = M_current < 0.1 * M0

    # Compute transition sharpness
    transition_sharpness = beta / (1.0 + math.exp(-beta * (theta - theta)))  # Maximum gradient

    results = {
        "meta": {
            "module": "cosmic_information_horizon",
            "version": "1.0.0",
            "description": "Information accessibility near event horizon with hex-resonance"
        },
        "config": {
            "initial_horizon_radius": horizon_radius,
            "duration": duration,
            "dt": dt,
            "n_radial_points": n_radial_points,
            "theta": theta,
            "beta_hex": beta,
            "evaporation_enabled": evaporation_enabled
        },
        "resonance_check": resonance_check,
        "snapshots": snapshots,
        "final_state": {
            "mass": M_current,
            "horizon_radius": r_horizon,
            "horizon_evaporated": horizon_evaporated,
            "radial_grid": r.tolist(),
            "information_density": final_R.tolist(),
            "accessibility_profile": final_P.tolist(),
            "total_accessible_info": float(np.trapz(final_P * final_R, r))
        },
        "emergence_analysis": {
            "information_preserved": not horizon_evaporated,
            "hex_resonance_active": resonance_check["status"] == "RESONANT",
            "transition_sharpness": float(transition_sharpness),
            "soft_horizon_confirmed": 0.1 < final_P[horizon_idx] < 0.9 if horizon_idx < len(final_P) else False
        }
    }

    if verbose:
        print(f"\n✨ Simulation Complete!")
        print(f"   Final Mass: {M_current:.3f} (evaporated: {horizon_evaporated})")
        print(f"   Final Horizon: r_s = {r_horizon:.3f}")
        print(f"   Total Accessible Info: {results['final_state']['total_accessible_info']:.2f}")
        print(f"   Hex-Resonance: {resonance_check['status']} (score: {resonance_check['resonance_score']})")

    return results


if __name__ == "__main__":
    # Run demonstration simulation
    print("=" * 70)
    print("COSMIC INFORMATION HORIZON SIMULATION")
    print("Hex-Resonance Phase Transition: β = 16^(1/√π) ≈ 4.779")
    print("=" * 70)
    print()

    results = run_simulation(
        horizon_radius=10.0,
        duration=100.0,
        dt=0.5,
        n_radial_points=200,
        theta=0.66,
        evaporation_enabled=True,
        snapshot_interval=20,
        verbose=True
    )

    print("\n" + "=" * 70)
    print("EMERGENCE ANALYSIS")
    print("=" * 70)
    for key, value in results["emergence_analysis"].items():
        print(f"  {key}: {value}")

    print("\n✅ Horizon simulation completed. Check results['snapshots'] for time evolution.")
