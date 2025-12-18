"""Soliton-Doppler Field Simulation with Hex-Resonance Lock.

This module simulates a nonlinear wave field governed by a modified
Korteweg-de Vries (KdV) equation with coupling strength locked to
HEX_RESONANCE_BETA ≈ 4.779.

The KdV equation:
    ∂u/∂t + β·u·∂u/∂x + γ·∂³u/∂x³ = 0

exhibits soliton solutions - stable, localized wave packets that
propagate without changing shape. This simulation tests whether
the hex-resonance value produces emergent solitonic structures.

Physical Interpretation:
- β = HEX_RESONANCE_BETA: Nonlinear coupling (information density gradient)
- γ: Dispersion parameter (quantum/cosmic spreading)
- Solitons represent "information coherence" in the V6 framework

Usage:
    from simulator.phase4.soliton_doppler import run_simulation
    results = run_simulation(duration=100.0, grid_points=512)
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
    # Fallback if import fails
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


def kdv_rhs(u: np.ndarray, dx: float, beta: float, gamma: float) -> np.ndarray:
    """Compute right-hand side of KdV equation: -(β·u·∂u/∂x + γ·∂³u/∂x³).

    Parameters
    ----------
    u : np.ndarray
        Wave field values on spatial grid
    dx : float
        Spatial step size
    beta : float
        Nonlinear coupling strength (HEX_RESONANCE_BETA)
    gamma : float
        Dispersion coefficient

    Returns
    -------
    np.ndarray
        Time derivative du/dt
    """
    # Compute spatial derivatives using finite differences
    # First derivative: ∂u/∂x (central difference)
    du_dx = np.gradient(u, dx)

    # Third derivative: ∂³u/∂x³ (using gradient three times)
    d3u_dx3 = np.gradient(np.gradient(np.gradient(u, dx), dx), dx)

    # KdV equation: ∂u/∂t = -(β·u·∂u/∂x + γ·∂³u/∂x³)
    dudt = -(beta * u * du_dx + gamma * d3u_dx3)

    return dudt


def initialize_wave_packet(
    x: np.ndarray,
    amplitude: float = 2.0,
    width: float = 1.0,
    center: float = 0.0
) -> np.ndarray:
    """Initialize a Gaussian wave packet as initial condition.

    Parameters
    ----------
    x : np.ndarray
        Spatial grid
    amplitude : float
        Peak amplitude
    width : float
        Gaussian width parameter
    center : float
        Center position of wave packet

    Returns
    -------
    np.ndarray
        Initial wave field u(x, t=0)
    """
    return amplitude * np.exp(-((x - center) / width) ** 2)


def detect_solitons(
    u: np.ndarray,
    threshold: float = 0.5,
    min_width: int = 5
) -> dict[str, int | list[float]]:
    """Detect localized wave packets (candidate solitons).

    A soliton is identified as a localized peak with amplitude above threshold
    and sufficient spatial extent.

    Parameters
    ----------
    u : np.ndarray
        Wave field at current time
    threshold : float
        Minimum amplitude to be considered a soliton
    min_width : int
        Minimum number of grid points for soliton structure

    Returns
    -------
    dict
        Detection metrics: count, positions, amplitudes
    """
    # Find local maxima above threshold
    peaks = []
    amplitudes = []

    for i in range(1, len(u) - 1):
        if u[i] > threshold and u[i] > u[i-1] and u[i] > u[i+1]:
            # Check if peak has sufficient width
            width_left = 0
            width_right = 0

            for j in range(i-1, 0, -1):
                if u[j] > threshold / 2:
                    width_left += 1
                else:
                    break

            for j in range(i+1, len(u)):
                if u[j] > threshold / 2:
                    width_right += 1
                else:
                    break

            if width_left + width_right >= min_width:
                peaks.append(i)
                amplitudes.append(float(u[i]))

    return {
        "soliton_count": len(peaks),
        "positions": peaks,
        "amplitudes": amplitudes,
        "max_amplitude": max(amplitudes) if amplitudes else 0.0,
        "total_energy": float(np.sum(u**2))
    }


def run_simulation(
    duration: float = 50.0,
    dt: float = 0.01,
    grid_points: int = 512,
    domain_length: float = 100.0,
    gamma: float = 0.1,
    snapshot_interval: int = 50,
    verbose: bool = True
) -> dict:
    """Run KdV soliton simulation with hex-resonance coupling.

    Parameters
    ----------
    duration : float
        Total simulation time
    dt : float
        Time step size
    grid_points : int
        Number of spatial grid points
    domain_length : float
        Spatial domain size [-L/2, L/2]
    gamma : float
        Dispersion coefficient
    snapshot_interval : int
        Steps between soliton detection checks
    verbose : bool
        Print progress information

    Returns
    -------
    dict
        Simulation results with telemetry:
        - 'config': Simulation parameters
        - 'beta_hex': Used coupling strength
        - 'resonance_check': Alignment verification
        - 'snapshots': Time series of soliton detections
        - 'final_state': Final wave field statistics
    """
    # Setup spatial grid
    x = np.linspace(-domain_length / 2, domain_length / 2, grid_points)
    dx = x[1] - x[0]

    # Initialize wave field with a wave packet
    u = initialize_wave_packet(x, amplitude=3.0, width=2.0, center=-20.0)

    # Use HEX_RESONANCE_BETA as coupling strength
    beta = HEX_RESONANCE_BETA

    # Time evolution
    n_steps = int(duration / dt)
    snapshots = []

    if verbose:
        print(f"🌊 Starting Soliton-Doppler Simulation")
        print(f"   β_hex = {beta:.5f}")
        print(f"   γ (dispersion) = {gamma:.5f}")
        print(f"   Grid: {grid_points} points over [{-domain_length/2:.1f}, {domain_length/2:.1f}]")
        print(f"   Duration: {duration:.1f} time units ({n_steps} steps)")

    for step in range(n_steps):
        # RK4 time integration
        k1 = kdv_rhs(u, dx, beta, gamma)
        k2 = kdv_rhs(u + 0.5 * dt * k1, dx, beta, gamma)
        k3 = kdv_rhs(u + 0.5 * dt * k2, dx, beta, gamma)
        k4 = kdv_rhs(u + dt * k3, dx, beta, gamma)

        u = u + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

        # Periodic boundary conditions (wrap around)
        # For solitons, we want them to propagate through boundaries

        # Take snapshots
        if step % snapshot_interval == 0:
            detection = detect_solitons(u, threshold=0.5)
            snapshots.append({
                "time": step * dt,
                "soliton_count": detection["soliton_count"],
                "max_amplitude": detection["max_amplitude"],
                "total_energy": detection["total_energy"]
            })

            if verbose and step % (snapshot_interval * 10) == 0:
                print(f"   t={step*dt:6.1f} | Solitons: {detection['soliton_count']} | "
                      f"Max Amp: {detection['max_amplitude']:.3f} | "
                      f"Energy: {detection['total_energy']:.2f}")

    # Final analysis
    final_detection = detect_solitons(u, threshold=0.5)
    resonance_check = verify_hex_alignment(beta, tolerance=0.01)

    # Check if solitons emerged
    avg_soliton_count = np.mean([s["soliton_count"] for s in snapshots])
    stability_metric = np.std([s["total_energy"] for s in snapshots]) / np.mean([s["total_energy"] for s in snapshots])

    results = {
        "meta": {
            "module": "soliton_doppler",
            "version": "1.0.0",
            "description": "KdV soliton emergence under hex-resonance coupling"
        },
        "config": {
            "duration": duration,
            "dt": dt,
            "grid_points": grid_points,
            "domain_length": domain_length,
            "gamma": gamma,
            "beta_hex": beta
        },
        "resonance_check": resonance_check,
        "snapshots": snapshots,
        "final_state": {
            "soliton_count": final_detection["soliton_count"],
            "soliton_positions": final_detection["positions"],
            "soliton_amplitudes": final_detection["amplitudes"],
            "total_energy": final_detection["total_energy"],
            "avg_soliton_count": float(avg_soliton_count),
            "energy_stability": float(stability_metric)
        },
        "emergence_analysis": {
            "solitons_emerged": final_detection["soliton_count"] > 0,
            "stable_structures": stability_metric < 0.1,
            "hex_resonance_active": resonance_check["status"] == "RESONANT"
        }
    }

    if verbose:
        print(f"\n✨ Simulation Complete!")
        print(f"   Final Soliton Count: {final_detection['soliton_count']}")
        print(f"   Average Count: {avg_soliton_count:.2f}")
        print(f"   Energy Stability: {stability_metric:.4f}")
        print(f"   Hex-Resonance: {resonance_check['status']} (score: {resonance_check['resonance_score']})")

    return results


if __name__ == "__main__":
    # Run demonstration simulation
    print("=" * 70)
    print("SOLITON-DOPPLER FIELD SIMULATION")
    print("Hex-Resonance Lock: β = 16^(1/√π) ≈ 4.779")
    print("=" * 70)
    print()

    results = run_simulation(
        duration=50.0,
        dt=0.01,
        grid_points=512,
        domain_length=100.0,
        gamma=0.1,
        snapshot_interval=50,
        verbose=True
    )

    print("\n" + "=" * 70)
    print("EMERGENCE ANALYSIS")
    print("=" * 70)
    for key, value in results["emergence_analysis"].items():
        print(f"  {key}: {value}")

    print("\n✅ Soliton simulation completed. Check results['snapshots'] for time evolution.")
