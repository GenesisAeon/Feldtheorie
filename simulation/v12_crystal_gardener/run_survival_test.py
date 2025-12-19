"""Survival test under pressure ramp using the V12 Crystal Gardener."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.phase4.pressure_modulation import PressureModulator
from simulation.v12_crystal_gardener import CrystalGardener
from v11_gardener.ecosystem.multi_agent_system import create_ecosystem


def simulate_crystal_survival(
    n_agents: int = 12,
    n_timesteps: int = 240,
    pressure_min: float = 1.0,
    pressure_max: float = 5.0,
    pressure_ramp_start: int = 50,
    pressure_ramp_duration: int = 100,
) -> Dict[str, Any]:
    """Repeat the pressure ramp experiment with the oracle-gated gardener."""

    ecosystem = create_ecosystem(n_agents=n_agents, scenario="balanced", random_seed=42)
    gardener = CrystalGardener(
        name="CrystalPressureGardener",
        sigma_phi_target=0.0625,
        tolerance=0.012,
        action_learning_rate=0.2,
    )
    modulator = PressureModulator()

    pressure_trace: List[float] = []
    v_rig_trace: List[float] = []
    sigma_phi_mean_trace: List[float] = []
    sigma_phi_std_trace: List[float] = []
    alive_count_trace: List[int] = []
    oracle_veto_trace: List[int] = []
    oracle_resonance_trace: List[int] = []

    pressure_schedule = np.ones(n_timesteps) * pressure_min
    ramp_end = pressure_ramp_start + pressure_ramp_duration
    if ramp_end <= n_timesteps:
        ramp_indices = np.arange(pressure_ramp_start, ramp_end)
        pressure_schedule[ramp_indices] = np.linspace(
            pressure_min, pressure_max, len(ramp_indices)
        )
        pressure_schedule[ramp_end:] = pressure_max

    # V18: Track agent states across timesteps (needed for dynamic population)
    agent_states = ecosystem.get_agent_states()
    agent_ids = ecosystem.get_agent_ids()
    coupling_matrix = ecosystem.get_coupling_matrix()

    for t in range(n_timesteps):
        pressure = float(pressure_schedule[t])
        v_rig_eff = modulator.effective_v_rig(pressure, 37.0, 0.0)

        pressure_trace.append(pressure)
        v_rig_trace.append(v_rig_eff)

        ecosystem.step(dt=0.1)

        # Update ecosystem states (but keep our extended agent population)
        ecosystem_states = ecosystem.get_agent_states()
        for agent_id, state in ecosystem_states.items():
            if agent_id in agent_states:
                # Update existing agents with ecosystem changes
                agent_states[agent_id].update(state)

        # Expand coupling matrix if population grew
        n_current = len(agent_ids)
        if coupling_matrix.shape[0] < n_current:
            new_size = n_current
            new_matrix = np.zeros((new_size, new_size))
            old_size = coupling_matrix.shape[0]
            new_matrix[:old_size, :old_size] = coupling_matrix
            # New agents have weak coupling to existing agents
            for i in range(old_size, new_size):
                new_matrix[i, :old_size] = 0.05  # Weak initial coupling
                new_matrix[:old_size, i] = 0.05
            coupling_matrix = new_matrix

        adjusted_matrix, adjusted_temps, _, agent_states, agent_ids = gardener.cultivate_ecosystem(
            agent_states=agent_states,
            coupling_matrix=coupling_matrix,
            agent_ids=agent_ids,
            timestep=t,
            current_pressure=pressure,
        )

        # Apply cultivation to ecosystem (only affects original agents)
        ecosystem.apply_cultivation(adjusted_matrix[:n_agents, :n_agents], adjusted_temps)

        # Calculate statistics including new agents
        sigma_phi_values = [s["sigma_phi"] for s in agent_states.values()]
        alive_in_extended = sum(1 for s in agent_states.values() if 0.0 < s.get("sigma_phi", 0.0) < 0.2)

        sigma_phi_mean_trace.append(float(np.mean(sigma_phi_values)))
        sigma_phi_std_trace.append(float(np.std(sigma_phi_values)))
        alive_count_trace.append(alive_in_extended)
        oracle_veto_trace.append(gardener.oracle_vetoes)
        oracle_resonance_trace.append(gardener.resonance_assists)

    sigma_phi_array = np.array(sigma_phi_mean_trace)
    target_sigma_phi = gardener.sigma_phi_target
    tolerance = gardener.tolerance

    stable_mask = np.abs(sigma_phi_array - target_sigma_phi) < tolerance
    stability_ratio = float(stable_mask.sum() / len(sigma_phi_array))

    max_stable_pressure = pressure_min
    for t in range(n_timesteps):
        if stable_mask[t]:
            max_stable_pressure = max(max_stable_pressure, pressure_trace[t])

    gardener_summary = gardener.get_cultivation_summary()
    oracle_summary = gardener.oracle_summary()

    return {
        "experiment_config": {
            "n_agents": n_agents,
            "n_timesteps": n_timesteps,
            "pressure_range": [pressure_min, pressure_max],
            "pressure_ramp": [pressure_ramp_start, pressure_ramp_start + pressure_ramp_duration],
        },
        "environmental_traces": {
            "pressure_atm": pressure_trace,
            "v_rig_m_s": v_rig_trace,
        },
        "ecosystem_traces": {
            "sigma_phi_mean": sigma_phi_mean_trace,
            "sigma_phi_std": sigma_phi_std_trace,
            "alive_count": alive_count_trace,
        },
        "gardener_activity": {
            "cultivation_style": gardener_summary.get("cultivation_style", "unknown"),
            "emergent_events": gardener_summary.get("emergent_events", []),
            "oracle_vetoes": oracle_summary["vetoes"],
            "oracle_resonance_assists": oracle_summary["resonance_assists"],
            "oracle_recent": oracle_summary["recent_decisions"],
            "action_counts": gardener_summary.get("total_actions", {}),
        },
        "network_metrics": {
            "effective_pressure_trace": gardener_summary.get(
                "network_effective_pressure_trace", []
            ),
            "final_effective_pressure": gardener_summary.get(
                "final_effective_pressure"
            ),
            "vitality_transfers": gardener_summary.get("vitality_transfers", 0),
            "phoenix_transfers": gardener_summary.get("phoenix_transfers", 0),
        },
        "genesis_metrics": {
            "total_births": gardener_summary.get("total_births", 0),
            "reproduction_events": gardener_summary.get("reproduction_events", 0),
            "recent_births": gardener_summary.get("recent_births", []),
            "max_population": gardener_summary.get("max_population", n_agents),
        },
        "pressure_tolerance_analysis": {
            "stability_ratio": stability_ratio,
            "max_stable_pressure_atm": max_stable_pressure,
        },
        "key_findings": {
            "baseline_sigma_phi": sigma_phi_mean_trace[0],
            "final_sigma_phi": sigma_phi_mean_trace[-1],
            "sigma_phi_drift": sigma_phi_mean_trace[-1] - sigma_phi_mean_trace[0],
            "baseline_alive": alive_count_trace[0],
            "final_alive": alive_count_trace[-1],
            "oracle_interventions": oracle_veto_trace[-1],
            "resonance_boosts": oracle_resonance_trace[-1],
            "survival_rate_improvement": (
                (alive_count_trace[-1] - alive_count_trace[0])
                / max(1, alive_count_trace[0])
                * 100.0
            ),
        },
    }


def print_survival_summary(telemetry: Dict[str, Any]) -> None:
    """Pretty-print the survival test results."""

    print("=" * 70)
    print("  💠 Crystal Gardener Survival Test (Pressure Ramp 1→5 atm) 💠")
    print("=" * 70)

    config = telemetry["experiment_config"]
    print("\nConfiguration:")
    print(f"  Agents: {config['n_agents']}")
    print(f"  Timesteps: {config['n_timesteps']}")
    print(f"  Pressure Range: {config['pressure_range'][0]:.1f} - {config['pressure_range'][1]:.1f} atm")

    env_traces = telemetry["environmental_traces"]
    print("\nEnvironmental Conditions:")
    print(f"  Pressure: {min(env_traces['pressure_atm']):.2f} - {max(env_traces['pressure_atm']):.2f} atm")
    print(f"  v_RIG: {min(env_traces['v_rig_m_s']):.0f} - {max(env_traces['v_rig_m_s']):.0f} m/s")

    findings = telemetry["key_findings"]
    print("\nEcosystem Response:")
    print(f"  σ_Φ (baseline → final): {findings['baseline_sigma_phi']:.4f} → {findings['final_sigma_phi']:.4f}")
    print(f"  σ_Φ drift: {findings['sigma_phi_drift']:+.4f}")
    print(f"  Alive (baseline → final): {findings['baseline_alive']}/{config['n_agents']} → {findings['final_alive']}/{config['n_agents']}")

    tolerance = telemetry["pressure_tolerance_analysis"]
    print("\nPressure Tolerance:")
    print(f"  Stability Ratio: {tolerance['stability_ratio']*100:.1f}%")
    print(f"  Max Stable Pressure: {tolerance['max_stable_pressure_atm']:.2f} atm")
    print(
        f"  Survival Rate Improvement: {telemetry['key_findings']['survival_rate_improvement']:+.1f}%"
    )

    network = telemetry.get("network_metrics", {})
    if network.get("effective_pressure_trace"):
        print(
            f"  Effective Network Pressure: {network['final_effective_pressure']:.2f} atm"
        )
    if network.get("vitality_transfers"):
        print(f"  Vitality Transfers (V16): {network['vitality_transfers']}")
    if network.get("phoenix_transfers"):
        print(f"  Phoenix Transfers (V17): {network['phoenix_transfers']}")

    genesis = telemetry.get("genesis_metrics", {})
    if genesis.get("total_births", 0) > 0:
        print("\n👶 Genesis Cycle (V18) - Demographic Stability:")
        print(f"  Total Births: {genesis['total_births']}")
        print(f"  Reproduction Events: {genesis['reproduction_events']}")
        print(f"  Population Capacity: {config['n_agents']} → {genesis['max_population']}")

        if genesis.get("recent_births"):
            print("  Recent Births:")
            for birth in genesis["recent_births"]:
                print(
                    f"    t={birth['timestep']}: {birth['child_id']} "
                    f"from {birth['parent_a']} × {birth['parent_b']} "
                    f"| σ_φ={birth['child_sigma_phi']:.4f} | Gen {birth['generation']}"
                )

    gardener = telemetry["gardener_activity"]
    print("\nGardener Activity:")
    print(f"  Cultivation Style: {gardener['cultivation_style']}")
    print(f"  Oracle Vetoes: {gardener['oracle_vetoes']}")
    print(f"  Resonance Assists: {gardener['oracle_resonance_assists']}")
    if gardener["oracle_recent"]:
        print("  Recent Decisions (oracle):")
        for decision in gardener["oracle_recent"]:
            print(
                f"    Agent {decision['agent_id']}: {decision['proposed_action']} → {decision['final_action']} "
                f"| σ_ϕ≈{decision['sigma_phi_est']:.4f} | {decision['translation']} ({decision['decision']})"
            )
    if gardener["action_counts"]:
        print("  Actions:")
        for action, count in gardener["action_counts"].items():
            print(f"    {action.capitalize()}: {count}")

    print("\n" + "=" * 70)


def main() -> None:
    telemetry = simulate_crystal_survival()
    print_survival_summary(telemetry)


if __name__ == "__main__":
    main()
