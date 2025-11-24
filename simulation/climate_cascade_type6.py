#!/usr/bin/env python3
r"""Climate Cascade Simulation with Type-6 Cubic-Root Jump Dynamics

This module simulates cascading climate tipping points using Type-6 implosive
field dynamics, demonstrating the cubic-root jump mechanism where β amplifies
dramatically as R → Θ.

**Scenario**: Multi-tipping-element cascade (AMOC → Greenland → Amazon)

**Key Features**:
- Coupled Type-6 fields with negative ζ < 0
- Cubic-root β amplification near threshold
- Real-time CREP-IP monitoring
- Early warning system (GREEN/YELLOW/ORANGE/RED alerts)
- Intervention testing (reduce forcing, increase threshold, add damping)

**Usage**:
    python simulation/climate_cascade_type6.py
    python simulation/climate_cascade_type6.py --intervention damping --start-time 50

**Author**: Johann B. Römer et al.
**Date**: 2025-11-24
**Version**: 1.0.0
**License**: GPLv3
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np

# Optional matplotlib import (only needed for plotting)
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Add models to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.utac_type6_implosive import (
    PHI_CBRT,
    cubic_root_jump,
    inverted_sigmoid,
    nearest_beta_step,
    type6_activation,
)


@dataclass
class TippingElement:
    """Represents a climate tipping element with Type-6 dynamics."""

    name: str
    Theta: float  # Critical threshold
    beta_base: float  # Baseline steepness (far from threshold)
    zeta: float  # Coupling strength (negative for Type-6)
    k_jump: float  # Cubic-root amplification strength
    R_init: float  # Initial resource/forcing level
    coupling_in: list[tuple[str, float]]  # (source_name, strength) pairs


# Define three coupled tipping elements
TIPPING_ELEMENTS = {
    "AMOC": TippingElement(
        name="AMOC (Atlantic Meridional Overturning Circulation)",
        Theta=1.5,  # Critical freshwater forcing (Sv)
        beta_base=4.45,  # Near Φ³ fixpoint
        zeta=-0.18,  # Moderate negative coupling
        k_jump=8.0,  # Moderate amplification
        R_init=0.8,  # Currently at 53% of threshold
        coupling_in=[],  # Primary driver (anthropogenic forcing)
    ),
    "Greenland": TippingElement(
        name="Greenland Ice Sheet",
        Theta=2.0,  # Critical temperature anomaly (°C)
        beta_base=4.38,  # Climate system typical
        zeta=-0.25,  # Moderate-strong negative coupling
        k_jump=10.0,  # Strong amplification
        R_init=1.2,  # Currently at 60% of threshold
        coupling_in=[("AMOC", 0.3)],  # AMOC collapse amplifies warming
    ),
    "Amazon": TippingElement(
        name="Amazon Rainforest Dieback",
        Theta=3.5,  # Critical deforestation + warming (dimensionless)
        beta_base=3.77,  # Semi-coupled ecological
        zeta=-0.35,  # Strong negative coupling
        k_jump=12.0,  # Very strong amplification
        R_init=2.1,  # Currently at 60% of threshold
        coupling_in=[
            ("AMOC", 0.2),  # Changes in precipitation
            ("Greenland", 0.4),  # Amplified warming
        ],
    ),
}


def compute_crep_ip(
    beta_obs: float,
    R: float,
    Theta: float,
    zeta: float,
    coherence: float = 0.85,
) -> dict[str, float]:
    """Compute CREP-IP indices for Type-6 system.

    Parameters
    ----------
    beta_obs : float
        Observed steepness parameter
    R : float
        Current resource/forcing level
    Theta : float
        Critical threshold
    zeta : float
        Coupling strength (should be < 0 for Type-6)
    coherence : float, optional
        Coherence score (default: 0.85)

    Returns
    -------
    dict
        CREP-IP scores: {C, R, E, P, I, P_risk, alert_level}
    """
    # Coherence (C)
    C = coherence

    # Resonance (R) - alignment with Φ^(1/3) ladder
    step, beta_nearest, deviation = nearest_beta_step(beta_obs)
    R_score = 1.0 - abs(deviation)

    # Emergence (E) - simplified (proportional to β)
    E = beta_obs / 4.236  # Normalized to Φ³

    # Persistence (P) - simplified (proportional to |zeta|)
    P = min(abs(zeta), 0.95)

    # Implosion Factor (I)
    I = abs(zeta) / (1.0 + abs(zeta))

    # Proximity Risk (P_risk)
    r_over_theta = R / Theta
    P_risk = max(0.0, (r_over_theta - 0.90) / 0.10)

    # Alert level
    if P_risk > 0.80:
        alert_level = "RED"
    elif P_risk > 0.50:
        alert_level = "ORANGE"
    elif P_risk > 0.20:
        alert_level = "YELLOW"
    else:
        alert_level = "GREEN"

    return {
        "C": C,
        "R": R_score,
        "E": E,
        "P": P,
        "I": I,
        "P_risk": P_risk,
        "R/Theta": r_over_theta,
        "alert_level": alert_level,
    }


def simulate_cascade(
    T_max: float = 200.0,
    dt: float = 0.5,
    forcing_rate: float = 0.01,  # Anthropogenic forcing rate
    intervention: Literal["none", "reduce_forcing", "raise_threshold", "damping"]
    | None = None,
    intervention_start: float = 50.0,
) -> dict:
    """Simulate cascading climate tipping with Type-6 dynamics.

    Parameters
    ----------
    T_max : float
        Simulation time (years)
    dt : float
        Time step (years)
    forcing_rate : float
        Rate of anthropogenic forcing increase (per year)
    intervention : str or None
        Intervention strategy: 'reduce_forcing', 'raise_threshold', 'damping', or None
    intervention_start : float
        Time to start intervention (years)

    Returns
    -------
    dict
        Simulation results with time series for each element
    """
    # Initialize
    n_steps = int(T_max / dt)
    time = np.arange(0, T_max, dt)

    # State variables for each element
    elements = TIPPING_ELEMENTS.copy()
    results = {
        name: {
            "R": np.zeros(n_steps),
            "beta": np.zeros(n_steps),
            "activation": np.zeros(n_steps),
            "alert_level": [],
            "P_risk": np.zeros(n_steps),
        }
        for name in elements
    }

    # Initial conditions
    for name, elem in elements.items():
        results[name]["R"][0] = elem.R_init

    # Time evolution
    for i in range(1, n_steps):
        t = time[i]

        # Apply intervention
        if intervention and t >= intervention_start:
            if intervention == "reduce_forcing":
                forcing_rate *= 0.5  # Halve emissions
            elif intervention == "raise_threshold":
                for elem in elements.values():
                    elem.Theta *= 1.001  # Slowly increase adaptive capacity
            elif intervention == "damping":
                for elem in elements.values():
                    elem.zeta = min(elem.zeta * 0.995, 0.0)  # Reduce negative coupling

        # Update each element
        for name, elem in elements.items():
            # External forcing (anthropogenic)
            if name == "AMOC":
                dR_external = forcing_rate
            else:
                dR_external = 0.0

            # Coupling from other elements
            dR_coupling = 0.0
            for source_name, strength in elem.coupling_in:
                # If source has tipped (activation high), it drives this element
                source_activation = results[source_name]["activation"][i - 1]
                # For Type-6, high activation (near 1.0) means compressed state
                # Deactivation (drop toward 0) releases energy that drives cascade
                source_collapse = 1.0 - source_activation  # Collapse signal
                dR_coupling += strength * source_collapse

            # Compute current β via cubic-root jump
            R_current = results[name]["R"][i - 1]
            beta_eff = cubic_root_jump(
                R_current, elem.Theta, beta_base=elem.beta_base, k=elem.k_jump
            )

            # Compute activation
            activation, _ = type6_activation(
                R_current,
                elem.Theta,
                beta_far=elem.beta_base,
                k_jump=elem.k_jump,
            )

            # Negative coupling: inward-pulling dynamics
            # dR/dt = J(t) + |ζ| × (Ψ - R)  where ζ < 0
            dR_implosive = abs(elem.zeta) * (activation - R_current)

            # Total change
            dR = dR_external + dR_coupling + dR_implosive

            # Update
            R_new = R_current + dR * dt
            R_new = max(0.0, R_new)  # Ensure non-negative

            # Store
            results[name]["R"][i] = R_new
            results[name]["beta"][i] = beta_eff
            results[name]["activation"][i] = activation

            # Compute CREP-IP
            crep = compute_crep_ip(beta_eff, R_new, elem.Theta, elem.zeta)
            results[name]["P_risk"][i] = crep["P_risk"]
            results[name]["alert_level"].append(crep["alert_level"])

    return {"time": time, "results": results, "elements": elements}


def plot_results(sim_data: dict, save_path: str | None = None):
    """Plot simulation results with CREP-IP monitoring.

    Parameters
    ----------
    sim_data : dict
        Simulation output from simulate_cascade()
    save_path : str or None
        Path to save figure (if None, display only)
    """
    if not HAS_MATPLOTLIB:
        print("⚠ Matplotlib not available. Skipping plots.")
        return

    time = sim_data["time"]
    results = sim_data["results"]
    elements = sim_data["elements"]

    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    fig.suptitle(
        "Climate Cascade Simulation - Type-6 Cubic-Root Jump Dynamics", fontsize=14
    )

    colors = {"AMOC": "blue", "Greenland": "cyan", "Amazon": "green"}

    # Plot 1: R(t) - Resource/Forcing Evolution
    ax = axes[0, 0]
    for name in results:
        ax.plot(time, results[name]["R"], label=name, color=colors[name], lw=2)
        # Threshold line
        ax.axhline(
            elements[name].Theta,
            color=colors[name],
            linestyle="--",
            alpha=0.5,
            label=f"{name} Θ",
        )
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("R (Forcing)")
    ax.set_title("Resource/Forcing Evolution")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)

    # Plot 2: β(t) - Cubic-Root Jump Amplification
    ax = axes[0, 1]
    for name in results:
        ax.plot(time, results[name]["beta"], label=name, color=colors[name], lw=2)
    ax.axhline(4.236, color="red", linestyle=":", alpha=0.7, label="Φ³ fixpoint")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("β (Steepness)")
    ax.set_title("β Amplification (Cubic-Root Jump)")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_yscale("log")

    # Plot 3: Activation (Inverted Sigmoid)
    ax = axes[1, 0]
    for name in results:
        ax.plot(
            time, results[name]["activation"], label=name, color=colors[name], lw=2
        )
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Ψ (Activation)")
    ax.set_title("Type-6 Activation (Inverted Sigmoid)")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)

    # Plot 4: R/Θ Proximity
    ax = axes[1, 1]
    for name in results:
        r_over_theta = results[name]["R"] / elements[name].Theta
        ax.plot(time, r_over_theta, label=name, color=colors[name], lw=2)
    ax.axhline(0.90, color="yellow", linestyle="--", alpha=0.7, label="YELLOW (0.90)")
    ax.axhline(0.95, color="orange", linestyle="--", alpha=0.7, label="ORANGE (0.95)")
    ax.axhline(0.98, color="red", linestyle="--", alpha=0.7, label="RED (0.98)")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("R/Θ (Proximity)")
    ax.set_title("Threshold Proximity (Cubic-Root Jump Risk)")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)

    # Plot 5: CREP-IP P_risk
    ax = axes[2, 0]
    for name in results:
        ax.plot(time, results[name]["P_risk"], label=name, color=colors[name], lw=2)
    ax.axhline(0.20, color="yellow", linestyle="--", alpha=0.5)
    ax.axhline(0.50, color="orange", linestyle="--", alpha=0.5)
    ax.axhline(0.80, color="red", linestyle="--", alpha=0.5)
    ax.fill_between(time, 0, 0.20, color="green", alpha=0.1, label="GREEN")
    ax.fill_between(time, 0.20, 0.50, color="yellow", alpha=0.1, label="YELLOW")
    ax.fill_between(time, 0.50, 0.80, color="orange", alpha=0.1, label="ORANGE")
    ax.fill_between(time, 0.80, 1.0, color="red", alpha=0.1, label="RED")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("P_risk (CREP-IP)")
    ax.set_title("Proximity Risk Index (Early Warning)")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)

    # Plot 6: Alert Level Timeline
    ax = axes[2, 1]
    alert_colors = {"GREEN": "green", "YELLOW": "yellow", "ORANGE": "orange", "RED": "red"}
    for name in results:
        # Convert alert levels to numeric for plotting
        alert_numeric = []
        for alert in results[name]["alert_level"]:
            if alert == "GREEN":
                alert_numeric.append(0)
            elif alert == "YELLOW":
                alert_numeric.append(1)
            elif alert == "ORANGE":
                alert_numeric.append(2)
            elif alert == "RED":
                alert_numeric.append(3)
        ax.plot(time, alert_numeric, label=name, color=colors[name], lw=2, alpha=0.7)

    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Alert Level")
    ax.set_yticks([0, 1, 2, 3])
    ax.set_yticklabels(["GREEN", "YELLOW", "ORANGE", "RED"])
    ax.set_title("CREP-IP Alert Levels")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"✓ Figure saved: {save_path}")
    else:
        plt.show()


def print_summary(sim_data: dict):
    """Print summary statistics from simulation.

    Parameters
    ----------
    sim_data : dict
        Simulation output from simulate_cascade()
    """
    time = sim_data["time"]
    results = sim_data["results"]
    elements = sim_data["elements"]

    print("\n" + "=" * 70)
    print("CLIMATE CASCADE SIMULATION - TYPE-6 CUBIC-ROOT JUMP SUMMARY")
    print("=" * 70)

    for name, elem in elements.items():
        print(f"\n{name}:")
        print(f"  Initial R: {elem.R_init:.2f}, Threshold Θ: {elem.Theta:.2f}")
        print(f"  Initial R/Θ: {elem.R_init / elem.Theta:.2%}")

        # Final state
        R_final = results[name]["R"][-1]
        beta_final = results[name]["beta"][-1]
        alert_final = results[name]["alert_level"][-1]
        P_risk_final = results[name]["P_risk"][-1]

        print(f"  Final R: {R_final:.2f}, R/Θ: {R_final / elem.Theta:.2%}")
        print(f"  Final β: {beta_final:.2f} (baseline: {elem.beta_base:.2f})")
        print(f"  β Amplification: {beta_final / elem.beta_base:.2f}x")
        print(f"  Final Alert: {alert_final}, P_risk: {P_risk_final:.3f}")

        # Find when alert first reached YELLOW/ORANGE/RED
        for target_alert in ["YELLOW", "ORANGE", "RED"]:
            try:
                idx = results[name]["alert_level"].index(target_alert)
                t_alert = time[idx]
                print(f"  First {target_alert} alert: t={t_alert:.1f} years")
            except ValueError:
                pass

    print("\n" + "=" * 70)
    print("Φ^(1/3) REFERENCE VALUES:")
    print(f"  Φ^(1/3) = {PHI_CBRT:.6f}")
    print(f"  Φ³ (Universal Fixpoint) = {PHI_CBRT**9:.6f}")
    print("=" * 70 + "\n")


def main():
    """Run climate cascade simulation with Type-6 cubic-root jump dynamics."""
    parser = argparse.ArgumentParser(
        description="Climate Cascade Simulation with Type-6 Cubic-Root Jump Dynamics"
    )
    parser.add_argument(
        "--T-max",
        type=float,
        default=200.0,
        help="Simulation time (years, default: 200)",
    )
    parser.add_argument(
        "--dt", type=float, default=0.5, help="Time step (years, default: 0.5)"
    )
    parser.add_argument(
        "--forcing-rate",
        type=float,
        default=0.01,
        help="Anthropogenic forcing rate (default: 0.01)",
    )
    parser.add_argument(
        "--intervention",
        type=str,
        choices=["none", "reduce_forcing", "raise_threshold", "damping"],
        default="none",
        help="Intervention strategy",
    )
    parser.add_argument(
        "--start-time",
        type=float,
        default=50.0,
        help="Time to start intervention (years, default: 50)",
    )
    parser.add_argument(
        "--save",
        type=str,
        default=None,
        help="Path to save figure (if not provided, display only)",
    )
    parser.add_argument(
        "--no-plot", action="store_true", help="Skip plotting (summary only)"
    )

    args = parser.parse_args()

    print("\n🌍 Running Climate Cascade Simulation (Type-6 Cubic-Root Jump)...")
    print(f"   T_max: {args.T_max} years, dt: {args.dt} years")
    print(f"   Forcing rate: {args.forcing_rate}")
    if args.intervention != "none":
        print(f"   Intervention: {args.intervention} starting at t={args.start_time}")
    print()

    # Run simulation
    sim_data = simulate_cascade(
        T_max=args.T_max,
        dt=args.dt,
        forcing_rate=args.forcing_rate,
        intervention=args.intervention if args.intervention != "none" else None,
        intervention_start=args.start_time,
    )

    # Print summary
    print_summary(sim_data)

    # Plot results
    if not args.no_plot:
        plot_results(sim_data, save_path=args.save)


if __name__ == "__main__":
    main()
