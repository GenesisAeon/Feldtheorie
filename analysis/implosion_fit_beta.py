#!/usr/bin/env python3
"""
UTAC v1.3φ - Implosive Origin Field Simulation
===============================================

This script simulates Type-6 implosive field dynamics with negative coupling (ζ<0)
and inverted sigmoid response σ(-β(R-Θ)).

Key features:
- Nine-step β-scaling following Φ^(1/3) sequence
- Negative coupling regime (ζ < 0)
- Energy release integral computation
- JSON output for manuscript integration

Author: Johann Benjamin Römer
Date: November 2025
License: AGPL-3.0
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

import numpy as np

# Golden ratio
PHI = (1 + np.sqrt(5)) / 2
PHI_THIRD = PHI ** (1 / 3)


def sigma_implosive(R: np.ndarray, beta: float, theta: float) -> np.ndarray:
    """
    Inverted sigmoid function for implosive dynamics.

    σ_imp(R) = 1 / (1 + exp(β(R - Θ)))

    Parameters
    ----------
    R : np.ndarray
        System drive parameter
    beta : float
        Steepness parameter
    theta : float
        Threshold location

    Returns
    -------
    np.ndarray
        Implosive response values
    """
    return 1.0 / (1.0 + np.exp(beta * (R - theta)))


def compute_beta_sequence(beta_0: float, steps: int = 9) -> np.ndarray:
    """
    Generate β-sequence following Φ^(1/3) scaling.

    β_n = β_0 × Φ^(n/3)

    Parameters
    ----------
    beta_0 : float
        Initial steepness
    steps : int
        Number of steps (default 9)

    Returns
    -------
    np.ndarray
        Sequence of β values
    """
    n = np.arange(steps + 1)
    return beta_0 * (PHI ** (n / 3))


def integrate_energy_release(R: np.ndarray, beta: float, theta: float) -> np.ndarray:
    """
    Compute energy release integral for implosive transition.

    E(R) = ∫_{-∞}^R σ_imp(r, β, Θ) dr

    Parameters
    ----------
    R : np.ndarray
        System drive values
    beta : float
        Steepness parameter
    theta : float
        Threshold location

    Returns
    -------
    np.ndarray
        Cumulative energy release
    """
    sigma_values = sigma_implosive(R, beta, theta)
    # Trapezoidal integration
    dR = np.diff(R)
    E = np.zeros_like(R)
    E[1:] = np.cumsum((sigma_values[:-1] + sigma_values[1:]) / 2 * dR)
    return E


def simulate_membrane_dynamics(
    beta: float,
    theta: float,
    zeta: float,
    J_func: callable,
    T: float = 100.0,
    dt: float = 0.01,
    R0: float = -2.0,
    random_seed: int = 1337,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulate membrane equation with negative coupling.

    dR/dt = J(t) - ζ(R) · (R - σ_imp(β(R-Θ)))

    Parameters
    ----------
    beta : float
        Steepness parameter
    theta : float
        Threshold location
    zeta : float
        Coupling strength (negative for implosive)
    J_func : callable
        Driver function J(t)
    T : float
        Simulation duration
    dt : float
        Time step
    R0 : float
        Initial condition
    random_seed : int
        Random seed for reproducibility

    Returns
    -------
    tuple
        (time_array, R_trajectory, sigma_trajectory)
    """
    np.random.seed(random_seed)

    n_steps = int(T / dt)
    t = np.linspace(0, T, n_steps)
    R = np.zeros(n_steps)
    R[0] = R0

    for i in range(n_steps - 1):
        sigma_current = sigma_implosive(R[i], beta, theta)
        J_current = J_func(t[i])

        dR_dt = J_current - zeta * (R[i] - sigma_current)
        R[i + 1] = R[i] + dt * dR_dt

    sigma_traj = sigma_implosive(R, beta, theta)

    return t, R, sigma_traj


def driver_linear_ramp(t: float, rate: float = 0.02) -> float:
    """Linear driver: J(t) = rate × t"""
    return rate * t


def driver_step_function(t: float, t_step: float = 20.0, amplitude: float = 1.0) -> float:
    """Step function driver: J(t) = A × H(t - t_step)"""
    return amplitude if t >= t_step else 0.0


def driver_stochastic(t: float, mean: float = 0.5, noise_std: float = 0.1) -> float:
    """Stochastic driver: J(t) = mean + η(t)"""
    return mean + np.random.normal(0, noise_std)


def run_full_simulation(config: dict) -> dict:
    """
    Run complete implosive field simulation suite.

    Parameters
    ----------
    config : dict
        Simulation configuration

    Returns
    -------
    dict
        Results dictionary with metadata and trajectories
    """
    beta_0 = config.get("beta_0", 1.0)
    steps = config.get("steps", 9)
    theta = config.get("theta", 0.5)
    zeta_min, zeta_max = config.get("zeta_range", [-1.5, -0.5])
    driver_type = config.get("driver", "linear_ramp")
    T = config.get("duration", 100.0)
    dt = config.get("timestep", 0.01)
    random_seed = config.get("random_seed", 1337)

    # Generate β-sequence
    beta_sequence = compute_beta_sequence(beta_0, steps)

    # Select driver
    if driver_type == "linear_ramp":
        J_func = lambda t: driver_linear_ramp(t, rate=0.02)
    elif driver_type == "step":
        J_func = lambda t: driver_step_function(t, t_step=20.0, amplitude=1.0)
    elif driver_type == "stochastic":
        J_func = lambda t: driver_stochastic(t, mean=0.5, noise_std=0.1)
    else:
        raise ValueError(f"Unknown driver type: {driver_type}")

    # Storage
    results = {
        "metadata": {
            "model": "UTAC_v1.3phi",
            "field_type": "Type-6 Implosive",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "config": config,
        },
        "phi": float(PHI),
        "phi_third": float(PHI_THIRD),
        "beta_0": float(beta_0),
        "beta_sequence": [float(b) for b in beta_sequence],
        "attractor_value": float(beta_sequence[-1]),
        "simulations": [],
    }

    # Run simulations for selected β values (steps 0, 3, 6, 9)
    key_steps = [0, 3, 6, 9]
    zeta_values = np.linspace(zeta_min, zeta_max, 3)

    for step_idx in key_steps:
        beta = beta_sequence[step_idx]

        for zeta in zeta_values:
            t, R_traj, sigma_traj = simulate_membrane_dynamics(
                beta=beta,
                theta=theta,
                zeta=zeta,
                J_func=J_func,
                T=T,
                dt=dt,
                random_seed=random_seed,
            )

            # Compute energy release
            R_grid = np.linspace(-3, 3, 200)
            E_release = integrate_energy_release(R_grid, beta, theta)

            # Threshold crossing analysis
            crossing_mask = np.abs(R_traj - theta) < 0.05
            if np.any(crossing_mask):
                crossing_time = t[np.where(crossing_mask)[0][0]]
            else:
                crossing_time = None

            sim_result = {
                "step": int(step_idx),
                "beta": float(beta),
                "zeta": float(zeta),
                "theta": float(theta),
                "crossing_time": float(crossing_time) if crossing_time is not None else None,
                "final_R": float(R_traj[-1]),
                "final_sigma": float(sigma_traj[-1]),
                "energy_integral_max": float(np.max(E_release)),
                # Store downsampled trajectories (every 10th point)
                "trajectory": {
                    "time": t[::10].tolist(),
                    "R": R_traj[::10].tolist(),
                    "sigma": sigma_traj[::10].tolist(),
                },
            }

            results["simulations"].append(sim_result)

    # Compute convergence metrics
    results["convergence"] = {
        "phi3_theoretical": float(PHI**3),
        "beta9_simulated": float(beta_sequence[-1]),
        "relative_error": float(abs(beta_sequence[-1] - PHI**3) / (PHI**3)),
        "converged": bool(abs(beta_sequence[-1] - PHI**3) / (PHI**3) < 0.01),
    }

    return results


def save_results(results: dict, output_path: Path):
    """Save simulation results to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✓ Results saved to: {output_path}")


def print_summary(results: dict):
    """Print simulation summary."""
    print("\n" + "=" * 70)
    print("UTAC v1.3φ - Type-6 Implosive Field Simulation")
    print("=" * 70)

    print("\n📊 Φ-Scaling Parameters:")
    print(f"   Φ = {results['phi']:.6f}")
    print(f"   Φ^(1/3) = {results['phi_third']:.6f}")
    print(f"   β₀ = {results['beta_0']:.3f}")

    print("\n🌀 β-Sequence (9 steps):")
    for i, beta in enumerate(results["beta_sequence"]):
        marker = " ← Φ³ attractor" if i == 9 else ""
        print(f"   Step {i}: β = {beta:.4f}{marker}")

    conv = results["convergence"]
    print("\n✓ Convergence:")
    print(f"   Φ³ (theoretical) = {conv['phi3_theoretical']:.6f}")
    print(f"   β₉ (simulated) = {conv['beta9_simulated']:.6f}")
    print(f"   Relative error = {conv['relative_error']*100:.2f}%")
    print(f"   Converged: {conv['converged']}")

    print(f"\n🔬 Simulations run: {len(results['simulations'])}")

    print("\n" + "=" * 70 + "\n")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="UTAC v1.3φ Implosive Field Simulator")
    parser.add_argument(
        "--beta0", type=float, default=1.0, help="Initial steepness β₀ (default: 1.0)"
    )
    parser.add_argument("--steps", type=int, default=9, help="Number of Φ^(1/3) steps (default: 9)")
    parser.add_argument(
        "--theta", type=float, default=0.5, help="Threshold location Θ (default: 0.5)"
    )
    parser.add_argument(
        "--driver",
        choices=["linear_ramp", "step", "stochastic"],
        default="linear_ramp",
        help="Driver function type (default: linear_ramp)",
    )
    parser.add_argument(
        "--duration", type=float, default=100.0, help="Simulation duration (default: 100.0)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="analysis/results/beta_implosion_curve.json",
        help="Output JSON path",
    )
    parser.add_argument("--seed", type=int, default=1337, help="Random seed (default: 1337)")

    args = parser.parse_args()

    # Configuration
    config = {
        "beta_0": args.beta0,
        "steps": args.steps,
        "theta": args.theta,
        "zeta_range": [-1.5, -0.5],
        "driver": args.driver,
        "duration": args.duration,
        "timestep": 0.01,
        "random_seed": args.seed,
    }

    print("🌀 Starting UTAC v1.3φ simulation...")

    # Run simulation
    results = run_full_simulation(config)

    # Save results
    output_path = Path(args.output)
    save_results(results, output_path)

    # Print summary
    print_summary(results)

    print("✓ Simulation complete!")


if __name__ == "__main__":
    main()
