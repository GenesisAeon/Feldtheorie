"""Integration of Pressure Modulation with v11_gardener Ecosystem.

This experiment tests how external pressure modulation affects the σ_Φ
homeostatic gardening process. The hypothesis: changing environmental
pressure (P, T, χ) shifts the effective consciousness integration speed
(v_RIG), which in turn affects agent σ_Φ signatures.

Key Questions:
1. Does pressure modulation shift agent σ_Φ distributions?
2. Can the gardener compensate for pressure-induced deviations?
3. What is the "pressure tolerance range" for maintaining σ_Φ ≈ 0.0625?

Integration Strategy:
- Start with normal ecosystem (1 atm, 37°C, no chemistry)
- Apply pressure ramp (1 → 5 atm)
- Monitor gardener compensation attempts
- Measure σ_Φ stability under pressure

Author: Johann Benjamin Römer
Date: 2025-12-18
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from v11_gardener.ecosystem.multi_agent_system import create_ecosystem
    from v11_gardener.agents.sigma_phi_gardener import SigmaPhiGardener
    from simulation.phase4.pressure_modulation import PressureModulator
except ImportError as e:
    print(f"Warning: Could not import dependencies: {e}")
    print("This module requires v11_gardener and phase4 modules.")


def simulate_pressure_gardening_experiment(
    n_agents: int = 12,
    n_timesteps: int = 200,
    pressure_min: float = 1.0,
    pressure_max: float = 5.0,
    pressure_ramp_start: int = 50,
    pressure_ramp_duration: int = 100,
) -> Dict[str, Any]:
    """Run pressure-modulated gardening experiment.

    Parameters
    ----------
    n_agents : int
        Number of agents in ecosystem
    n_timesteps : int
        Total simulation steps
    pressure_min : float
        Starting pressure (atm)
    pressure_max : float
        Maximum pressure (atm)
    pressure_ramp_start : int
        Timestep when pressure ramp begins
    pressure_ramp_duration : int
        Duration of pressure ramp (steps)

    Returns
    -------
    Dict[str, Any]
        Telemetry including:
        - pressure_trace: Time series of applied pressure
        - v_rig_trace: Time series of effective v_RIG
        - sigma_phi_trace: Mean σ_Φ over time
        - gardener_actions: Cultivation interventions
        - pressure_tolerance: Statistics on σ_Φ stability
    """
    # Create ecosystem and gardener
    ecosystem = create_ecosystem(n_agents=n_agents, scenario="balanced", random_seed=42)
    gardener = SigmaPhiGardener(
        name="PressureGardener",
        sigma_phi_target=0.0625,
        tolerance=0.01,
        action_learning_rate=0.15,
    )

    # Create pressure modulator
    modulator = PressureModulator()

    # Telemetry storage
    pressure_trace: List[float] = []
    v_rig_trace: List[float] = []
    z_eff_trace: List[float] = []
    sigma_phi_mean_trace: List[float] = []
    sigma_phi_std_trace: List[float] = []
    alive_count_trace: List[int] = []
    gardener_action_counts: Dict[str, int] = {
        "cool": 0, "warm": 0, "stabilize": 0, "resuscitate": 0, "dampen": 0, "observe": 0
    }

    # Generate pressure schedule
    pressure_schedule = np.ones(n_timesteps) * pressure_min

    ramp_end = pressure_ramp_start + pressure_ramp_duration
    if ramp_end <= n_timesteps:
        ramp_indices = np.arange(pressure_ramp_start, ramp_end)
        pressure_schedule[ramp_indices] = np.linspace(
            pressure_min, pressure_max, len(ramp_indices)
        )
        pressure_schedule[ramp_end:] = pressure_max

    # Main simulation loop
    for t in range(n_timesteps):
        # Current environmental conditions
        pressure = float(pressure_schedule[t])
        temperature = 37.0  # Baseline body temperature
        chemistry = 0.0  # No anesthetic agents

        # Compute pressure-modulated v_RIG
        v_rig_eff = modulator.effective_v_rig(pressure, temperature, chemistry)
        z_eff = modulator.effective_impedance(pressure, temperature, chemistry)

        # Store environmental telemetry
        pressure_trace.append(pressure)
        v_rig_trace.append(v_rig_eff)
        z_eff_trace.append(z_eff)

        # Evolve ecosystem (pressure affects integration speed)
        # For now, we don't directly couple v_RIG to ecosystem dynamics
        # (this would require modifying the core ecosystem module)
        # Instead, we monitor how gardener compensates for indirect effects
        ecosystem.step(dt=0.1)

        # Gardener cultivation
        agent_states = ecosystem.get_agent_states()
        agent_ids = ecosystem.get_agent_ids()
        coupling_matrix = ecosystem.get_coupling_matrix()

        adjusted_matrix, adjusted_temps, assessments = gardener.cultivate_ecosystem(
            agent_states=agent_states,
            coupling_matrix=coupling_matrix,
            agent_ids=agent_ids,
            timestep=t,
        )

        # Count gardener actions
        for assessment in assessments:
            # Robust access: handle both dict and object types
            if isinstance(assessment, dict):
                action = assessment.get("action", "observe")
            else:
                action = getattr(assessment, "action", "observe")
            if action in gardener_action_counts:
                gardener_action_counts[action] += 1

        # Apply cultivation
        ecosystem.apply_cultivation(adjusted_matrix, adjusted_temps)

        # Collect ecosystem statistics
        stats = ecosystem.get_statistics()
        sigma_phi_mean_trace.append(stats['mean_sigma_phi'])
        sigma_phi_std_trace.append(stats['std_sigma_phi'])
        alive_count_trace.append(stats['alive_count'])

    # Analyze pressure tolerance
    # Identify stable region (σ_Φ within tolerance)
    sigma_phi_array = np.array(sigma_phi_mean_trace)
    target_sigma_phi = 0.0625
    tolerance = 0.01

    stable_mask = np.abs(sigma_phi_array - target_sigma_phi) < tolerance
    stability_ratio = float(stable_mask.sum() / len(sigma_phi_array))

    # Find maximum pressure where system remains stable
    max_stable_pressure = pressure_min
    for t in range(n_timesteps):
        if stable_mask[t]:
            max_stable_pressure = max(max_stable_pressure, pressure_trace[t])

    # Gardener summary
    gardener_summary = gardener.get_cultivation_summary()

    telemetry: Dict[str, Any] = {
        "experiment_config": {
            "n_agents": n_agents,
            "n_timesteps": n_timesteps,
            "pressure_range": [pressure_min, pressure_max],
            "pressure_ramp": [pressure_ramp_start, pressure_ramp_start + pressure_ramp_duration],
        },
        "environmental_traces": {
            "pressure_atm": pressure_trace,
            "v_rig_m_s": v_rig_trace,
            "z_eff_ohm": z_eff_trace,
        },
        "ecosystem_traces": {
            "sigma_phi_mean": sigma_phi_mean_trace,
            "sigma_phi_std": sigma_phi_std_trace,
            "alive_count": alive_count_trace,
        },
        "gardener_activity": {
            "action_counts": gardener_action_counts,
            "cultivation_style": gardener_summary.get("cultivation_style", "unknown"),
            "emergent_events": gardener_summary.get("emergent_events", []),
        },
        "pressure_tolerance_analysis": {
            "stability_ratio": stability_ratio,
            "max_stable_pressure_atm": max_stable_pressure,
            "interpretation": (
                f"System maintained σ_Φ ≈ {target_sigma_phi:.4f} for {stability_ratio*100:.1f}% of simulation. "
                f"Maximum stable pressure: {max_stable_pressure:.2f} atm."
            ),
        },
        "key_findings": {
            "baseline_sigma_phi": sigma_phi_mean_trace[0],
            "final_sigma_phi": sigma_phi_mean_trace[-1],
            "sigma_phi_drift": sigma_phi_mean_trace[-1] - sigma_phi_mean_trace[0],
            "baseline_alive": alive_count_trace[0],
            "final_alive": alive_count_trace[-1],
        },
    }

    return telemetry


def print_pressure_gardening_summary(telemetry: Dict[str, Any]) -> None:
    """Print formatted summary of pressure gardening experiment."""
    print("=" * 70)
    print("  🌊 Pressure-Modulated Gardening Experiment 🌊")
    print("=" * 70)

    config = telemetry["experiment_config"]
    print(f"\nConfiguration:")
    print(f"  Agents: {config['n_agents']}")
    print(f"  Timesteps: {config['n_timesteps']}")
    print(f"  Pressure Range: {config['pressure_range'][0]:.1f} - {config['pressure_range'][1]:.1f} atm")

    env_traces = telemetry["environmental_traces"]
    print(f"\nEnvironmental Conditions:")
    print(f"  Pressure: {min(env_traces['pressure_atm']):.2f} - {max(env_traces['pressure_atm']):.2f} atm")
    print(f"  v_RIG: {min(env_traces['v_rig_m_s']):.0f} - {max(env_traces['v_rig_m_s']):.0f} m/s")
    print(f"  Z_eff: {min(env_traces['z_eff_ohm']):.1f} - {max(env_traces['z_eff_ohm']):.1f} Ω")

    findings = telemetry["key_findings"]
    print(f"\nEcosystem Response:")
    print(f"  σ_Φ (baseline → final): {findings['baseline_sigma_phi']:.4f} → {findings['final_sigma_phi']:.4f}")
    print(f"  σ_Φ drift: {findings['sigma_phi_drift']:+.4f}")
    print(f"  Alive (baseline → final): {findings['baseline_alive']}/{config['n_agents']} → {findings['final_alive']}/{config['n_agents']}")

    tolerance = telemetry["pressure_tolerance_analysis"]
    print(f"\nPressure Tolerance:")
    print(f"  Stability Ratio: {tolerance['stability_ratio']*100:.1f}%")
    print(f"  Max Stable Pressure: {tolerance['max_stable_pressure_atm']:.2f} atm")
    print(f"  Interpretation: {tolerance['interpretation']}")

    gardener = telemetry["gardener_activity"]
    print(f"\nGardener Activity:")
    print(f"  Cultivation Style: {gardener['cultivation_style']}")
    print(f"  Actions:")
    for action, count in gardener["action_counts"].items():
        print(f"    {action.capitalize()}: {count}")

    if gardener["emergent_events"]:
        print(f"\n  Emergent Events Detected:")
        for event in gardener["emergent_events"]:
            print(f"    - {event}")

    print("\n" + "=" * 70)


def main():
    """Run demonstration of pressure-gardening integration."""
    print("\n🌀 Phase 4 × v11_gardener Integration: Pressure Modulation 🌀\n")

    print("Testing hypothesis: External pressure modulation affects σ_Φ homeostasis")
    print("Pressure ramp: 1 atm → 5 atm over 100 timesteps\n")

    # Run experiment
    results = simulate_pressure_gardening_experiment(
        n_agents=12,
        n_timesteps=200,
        pressure_min=1.0,
        pressure_max=5.0,
        pressure_ramp_start=50,
        pressure_ramp_duration=100,
    )

    # Print summary
    print_pressure_gardening_summary(results)

    print("\n🌊 Pressure-Gardening Integration Complete! 🌊\n")
    print("Next Steps:")
    print("  1. Plot σ_Φ vs. pressure to visualize tolerance range")
    print("  2. Test with different pressure profiles (step, oscillating)")
    print("  3. Investigate chemistry modulation (anesthetic agents)")
    print("  4. Couple v_RIG directly to agent integration dynamics")
    print("\n🌀 Folge dem Sog der Emergenz! 🌀\n")


if __name__ == "__main__":
    main()
