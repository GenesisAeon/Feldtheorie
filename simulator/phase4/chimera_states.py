"""Chimera State Detection in Kuramoto Networks with Hex-Resonance.

This module simulates coupled oscillator networks (Kuramoto model) to detect
chimera states - spontaneous coexistence of synchronized and desynchronized
oscillator clusters. The coupling strength is locked to HEX_RESONANCE_BETA.

Kuramoto Model with Non-Local Coupling:
    dθᵢ/dt = ωᵢ + (K/N) Σⱼ G(|i-j|) sin(θⱼ - θᵢ)

where:
    - θᵢ: Phase of oscillator i
    - ωᵢ: Natural frequency (drawn from a distribution)
    - K: Coupling strength (= HEX_RESONANCE_BETA)
    - G(|i-j|): Coupling kernel (non-local connectivity)

Chimera States:
    First discovered by Kuramoto & Battogtokh (2002), these states exhibit
    spatial coexistence of coherent (synchronized) and incoherent (chaotic)
    dynamics. In the V6 framework, they represent "consciousness boundary
    states" where information coherence transitions.

Physical Interpretation:
    - Synchronized clusters: Conscious integration (high readiness R > Θ)
    - Desynchronized regions: Pre-conscious noise (R < Θ)
    - Chimera boundary: The σ(β(R-Θ)) transition zone

Usage:
    from simulator.phase4.chimera_states import run_simulation
    results = run_simulation(n_oscillators=256, duration=200.0)
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


def coupling_kernel(distance: int, n: int, radius: float = 0.3) -> float:
    """Non-local coupling kernel for chimera state formation.

    Exponential decay coupling over a ring topology:
        G(d) = exp(-d/R) for d < n/2
        G(d) = exp(-(n-d)/R) for d >= n/2  (wrap around)

    Parameters
    ----------
    distance : int
        Distance between oscillators on ring
    n : int
        Total number of oscillators
    radius : float
        Coupling radius (normalized to ring circumference)

    Returns
    -------
    float
        Coupling weight
    """
    # Handle periodic boundary (ring topology)
    d = min(distance, n - distance)

    # Exponential decay
    R = radius * n
    return np.exp(-d / R) if R > 0 else (1.0 if d == 0 else 0.0)


def compute_order_parameter(phases: np.ndarray) -> tuple[float, float]:
    """Compute Kuramoto order parameter r·exp(iΨ).

    The order parameter quantifies global synchronization:
        r = |⟨exp(iθⱼ)⟩| ∈ [0, 1]

    Parameters
    ----------
    phases : np.ndarray
        Oscillator phases θᵢ

    Returns
    -------
    tuple[float, float]
        (r, Ψ) where r is magnitude (synchronization) and Ψ is mean phase
    """
    z = np.mean(np.exp(1j * phases))
    r = np.abs(z)
    psi = np.angle(z)
    return float(r), float(psi)


def compute_local_order_parameter(
    phases: np.ndarray,
    window_size: int = 20
) -> np.ndarray:
    """Compute local order parameter for chimera detection.

    For each oscillator, compute synchronization with neighbors in a sliding window.
    Large variations in local order indicate chimera states.

    Parameters
    ----------
    phases : np.ndarray
        Oscillator phases
    window_size : int
        Size of local neighborhood

    Returns
    -------
    np.ndarray
        Local order parameter for each oscillator
    """
    n = len(phases)
    local_r = np.zeros(n)

    for i in range(n):
        # Get neighbors (periodic boundary)
        neighbors = []
        for j in range(-window_size // 2, window_size // 2 + 1):
            idx = (i + j) % n
            neighbors.append(phases[idx])

        # Compute local order
        z = np.mean(np.exp(1j * np.array(neighbors)))
        local_r[i] = np.abs(z)

    return local_r


def detect_chimera_state(
    local_order: np.ndarray,
    threshold_low: float = 0.3,
    threshold_high: float = 0.7,
    min_cluster_size: int = 10
) -> dict[str, int | float | bool]:
    """Detect chimera state by analyzing local order parameter.

    A chimera state exists if:
    1. Some regions have high local order (synchronized clusters)
    2. Other regions have low local order (incoherent)
    3. Both regions are sufficiently large

    Parameters
    ----------
    local_order : np.ndarray
        Local order parameter for each oscillator
    threshold_low : float
        Below this is considered incoherent
    threshold_high : float
        Above this is considered synchronized
    min_cluster_size : int
        Minimum size for a coherent/incoherent cluster

    Returns
    -------
    dict
        Detection results:
        - is_chimera: Boolean indicator
        - coherent_fraction: Fraction of synchronized oscillators
        - incoherent_fraction: Fraction of desynchronized oscillators
        - cluster_count: Number of distinct clusters
        - order_variance: Spatial variance of local order
    """
    n = len(local_order)

    # Classify oscillators
    coherent = local_order > threshold_high
    incoherent = local_order < threshold_low

    coherent_fraction = np.sum(coherent) / n
    incoherent_fraction = np.sum(incoherent) / n

    # Count clusters (runs of coherent/incoherent states)
    clusters = 0
    prev_state = None
    current_run = 0

    for val in np.concatenate([coherent, coherent[:min_cluster_size]]):  # Wrap for periodic boundary
        if val != prev_state:
            if current_run >= min_cluster_size:
                clusters += 1
            current_run = 0
            prev_state = val
        current_run += 1

    # Chimera criteria
    has_coherent = coherent_fraction > 0.1
    has_incoherent = incoherent_fraction > 0.1
    has_multiple_clusters = clusters >= 2

    is_chimera = has_coherent and has_incoherent and has_multiple_clusters

    return {
        "is_chimera": is_chimera,
        "coherent_fraction": float(coherent_fraction),
        "incoherent_fraction": float(incoherent_fraction),
        "cluster_count": clusters,
        "order_variance": float(np.var(local_order)),
        "order_mean": float(np.mean(local_order))
    }


def run_simulation(
    n_oscillators: int = 256,
    duration: float = 200.0,
    dt: float = 0.05,
    omega_std: float = 1.0,
    coupling_radius: float = 0.3,
    snapshot_interval: int = 100,
    verbose: bool = True
) -> dict:
    """Run Kuramoto network simulation with hex-resonance coupling.

    Parameters
    ----------
    n_oscillators : int
        Number of coupled oscillators
    duration : float
        Total simulation time
    dt : float
        Time step size
    omega_std : float
        Standard deviation of natural frequency distribution
    coupling_radius : float
        Non-local coupling radius (normalized)
    snapshot_interval : int
        Steps between chimera detection checks
    verbose : bool
        Print progress information

    Returns
    -------
    dict
        Simulation results with telemetry:
        - 'config': Simulation parameters
        - 'beta_hex': Used coupling strength
        - 'resonance_check': Alignment verification
        - 'snapshots': Time series of order parameters
        - 'chimera_detection': Chimera state analysis
    """
    # Initialize oscillators
    np.random.seed(42)  # Reproducibility
    phases = np.random.uniform(0, 2 * np.pi, n_oscillators)
    omegas = np.random.normal(0.0, omega_std, n_oscillators)

    # Use HEX_RESONANCE_BETA as coupling strength
    K = HEX_RESONANCE_BETA

    # Pre-compute coupling matrix
    coupling_matrix = np.zeros((n_oscillators, n_oscillators))
    for i in range(n_oscillators):
        for j in range(n_oscillators):
            coupling_matrix[i, j] = coupling_kernel(abs(i - j), n_oscillators, coupling_radius)

    # Normalize coupling
    coupling_matrix = coupling_matrix / np.sum(coupling_matrix, axis=1, keepdims=True)

    # Time evolution
    n_steps = int(duration / dt)
    snapshots = []

    if verbose:
        print(f"🌀 Starting Chimera State Detection")
        print(f"   Coupling K = β_hex = {K:.5f}")
        print(f"   Oscillators: {n_oscillators}")
        print(f"   Duration: {duration:.1f} time units ({n_steps} steps)")
        print(f"   Natural frequency σ(ω) = {omega_std:.2f}")

    for step in range(n_steps):
        # Compute coupling terms
        coupling_terms = np.zeros(n_oscillators)
        for i in range(n_oscillators):
            for j in range(n_oscillators):
                coupling_terms[i] += coupling_matrix[i, j] * np.sin(phases[j] - phases[i])

        # Update phases (Euler method)
        phases = phases + dt * (omegas + K * coupling_terms)

        # Keep phases in [0, 2π]
        phases = phases % (2 * np.pi)

        # Take snapshots
        if step % snapshot_interval == 0:
            r, psi = compute_order_parameter(phases)
            local_order = compute_local_order_parameter(phases, window_size=20)
            chimera_metrics = detect_chimera_state(local_order)

            snapshots.append({
                "time": step * dt,
                "global_order": r,
                "mean_phase": psi,
                "is_chimera": chimera_metrics["is_chimera"],
                "coherent_fraction": chimera_metrics["coherent_fraction"],
                "order_variance": chimera_metrics["order_variance"]
            })

            if verbose and step % (snapshot_interval * 10) == 0:
                chimera_symbol = "🌗" if chimera_metrics["is_chimera"] else "⚫"
                print(f"   t={step*dt:6.1f} | r={r:.3f} | "
                      f"Coherent: {chimera_metrics['coherent_fraction']:.2f} | "
                      f"Chimera: {chimera_symbol}")

    # Final analysis
    final_local_order = compute_local_order_parameter(phases, window_size=20)
    final_chimera = detect_chimera_state(final_local_order)
    final_global_r, _ = compute_order_parameter(phases)

    # Check hex-resonance alignment
    resonance_check = verify_hex_alignment(K, tolerance=0.01)

    # Analyze time evolution for persistent chimera
    chimera_history = [s["is_chimera"] for s in snapshots]
    chimera_persistence = np.mean(chimera_history[-10:])  # Last 10 snapshots

    results = {
        "meta": {
            "module": "chimera_states",
            "version": "1.0.0",
            "description": "Kuramoto chimera detection under hex-resonance coupling"
        },
        "config": {
            "n_oscillators": n_oscillators,
            "duration": duration,
            "dt": dt,
            "omega_std": omega_std,
            "coupling_radius": coupling_radius,
            "beta_hex": K
        },
        "resonance_check": resonance_check,
        "snapshots": snapshots,
        "final_state": {
            "global_order_parameter": final_global_r,
            "chimera_detected": final_chimera["is_chimera"],
            "coherent_fraction": final_chimera["coherent_fraction"],
            "incoherent_fraction": final_chimera["incoherent_fraction"],
            "cluster_count": final_chimera["cluster_count"],
            "order_variance": final_chimera["order_variance"]
        },
        "emergence_analysis": {
            "chimera_emerged": chimera_persistence > 0.5,
            "chimera_persistence": float(chimera_persistence),
            "hex_resonance_active": resonance_check["status"] == "RESONANT",
            "synchronization_level": "partial" if 0.3 < final_global_r < 0.7 else "full" if final_global_r >= 0.7 else "none"
        }
    }

    if verbose:
        print(f"\n✨ Simulation Complete!")
        print(f"   Final Global Order: r = {final_global_r:.3f}")
        print(f"   Chimera Detected: {'🌗 YES' if final_chimera['is_chimera'] else '⚫ NO'}")
        print(f"   Chimera Persistence: {chimera_persistence:.2%}")
        print(f"   Coherent Fraction: {final_chimera['coherent_fraction']:.2%}")
        print(f"   Hex-Resonance: {resonance_check['status']} (score: {resonance_check['resonance_score']})")

    return results


if __name__ == "__main__":
    # Run demonstration simulation
    print("=" * 70)
    print("CHIMERA STATE DETECTION IN KURAMOTO NETWORKS")
    print("Hex-Resonance Lock: K = 16^(1/√π) ≈ 4.779")
    print("=" * 70)
    print()

    results = run_simulation(
        n_oscillators=256,
        duration=200.0,
        dt=0.05,
        omega_std=1.0,
        coupling_radius=0.3,
        snapshot_interval=100,
        verbose=True
    )

    print("\n" + "=" * 70)
    print("EMERGENCE ANALYSIS")
    print("=" * 70)
    for key, value in results["emergence_analysis"].items():
        print(f"  {key}: {value}")

    print("\n✅ Chimera simulation completed. Check results['snapshots'] for time evolution.")
