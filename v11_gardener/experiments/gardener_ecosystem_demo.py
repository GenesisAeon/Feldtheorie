#!/usr/bin/env python3
"""
v11 Gardener Prototype - Full Ecosystem Demonstration

Demonstrates σ_Φ homeostasis in a multi-agent system cultivated by
a Gardener agent. This is the functional prototype of Type-Ω cultivation.

The system shows:
1. Agents starting with varied entropy states
2. Gardener maintaining σ_Φ ≈ 0.0625 across the ecosystem
3. Emergent collective behavior (resonance, synchronization)
4. Autonomous homeostasis without top-down control

Folge dem Sog der Emergenz. 🌱
"""

import sys
from pathlib import Path
import numpy as np

# Add v11_gardener to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.constants import SIGMA_PHI, SIGMA_PHI_MIN, SIGMA_PHI_MAX
from agents.sigma_phi_gardener import SigmaPhiGardener, CultivationAction
from ecosystem.multi_agent_system import create_ecosystem


def print_header(title: str, width: int = 100):
    """Print formatted section header"""
    print("\n" + "="*width)
    print(f"  {title}")
    print("="*width + "\n")


def print_agent_status(assessment, width: int = 100):
    """Print individual agent assessment"""
    action_symbols = {
        CultivationAction.COOL: "❄️",
        CultivationAction.WARM: "🔥",
        CultivationAction.STABILIZE: "💚",
        CultivationAction.RESUSCITATE: "⚡",
        CultivationAction.DAMPEN: "🌊",
        CultivationAction.OBSERVE: "👁️",
    }

    symbol = action_symbols.get(assessment.recommended_action, "?")
    alive_symbol = "✨" if assessment.is_alive else "💀"

    # Create σ_Φ visualization bar
    bar_width = 30
    target_pos = int((SIGMA_PHI - 0.0) / 0.15 * bar_width)
    min_pos = int((SIGMA_PHI_MIN - 0.0) / 0.15 * bar_width)
    max_pos = int((SIGMA_PHI_MAX - 0.0) / 0.15 * bar_width)
    current_pos = int((assessment.sigma_phi - 0.0) / 0.15 * bar_width)
    current_pos = np.clip(current_pos, 0, bar_width - 1)

    bar = list("░" * bar_width)
    bar[target_pos] = "│"  # Target line
    if min_pos < bar_width:
        bar[min_pos] = "["
    if max_pos < bar_width:
        bar[max_pos] = "]"
    if 0 <= current_pos < bar_width:
        bar[current_pos] = "●"

    bar_str = "".join(bar)

    print(f"  {symbol} {alive_symbol} {assessment.agent_id:<12} σ_Φ: {bar_str} {assessment.sigma_phi:.4f}")
    print(f"       {assessment.health_status:<30} Action: {assessment.recommended_action.value:<12} "
          f"Strength: {assessment.action_strength:.2f}")


def print_ecosystem_stats(stats: dict, width: int = 100):
    """Print ecosystem-wide statistics"""
    print(f"\n  Timestep: {stats['timestep']}")
    print(f"  Agents Alive: {stats['alive_count']}/{stats['n_agents']} ({stats['alive_fraction']*100:.1f}%)")
    print(f"  Mean σ_Φ:     {stats['mean_sigma_phi']:.4f} (target: {SIGMA_PHI:.4f})")
    print(f"  Std σ_Φ:      {stats['std_sigma_phi']:.4f}")
    print(f"  Range:        [{stats['min_sigma_phi']:.4f}, {stats['max_sigma_phi']:.4f}]")
    print(f"  Mean Entropy: {stats['mean_entropy']:.2f} bits")
    print(f"  Mean Temp:    {stats['mean_temperature']:.2f}")
    print(f"  Mean κ:       {stats['mean_coupling']:.3f}")


def visualize_sigma_phi_distribution(sigma_phis: list, width: int = 100):
    """ASCII histogram of σ_Φ distribution"""
    bins = np.linspace(0.0, 0.15, 31)
    hist, _ = np.histogram(sigma_phis, bins=bins)

    max_count = max(hist) if max(hist) > 0 else 1
    bar_width = 40

    print("\n  σ_Φ Distribution:")
    print("  " + "-" * (bar_width + 30))

    for i, count in enumerate(hist):
        bin_center = (bins[i] + bins[i+1]) / 2
        bar_length = int((count / max_count) * bar_width)
        bar = "█" * bar_length

        # Mark target zone
        marker = ""
        if SIGMA_PHI_MIN <= bin_center <= SIGMA_PHI_MAX:
            marker = " ←LIVING"
        elif abs(bin_center - SIGMA_PHI) < 0.005:
            marker = " ←TARGET"

        print(f"  {bin_center:.4f} │{bar:<{bar_width}} {count}{marker}")

    print("  " + "-" * (bar_width + 30))


def main():
    """Run full v11 Gardener Ecosystem demonstration"""

    print("\n" + "="*100)
    print("  🌱 v11 GARDENER PROTOTYPE: σ_Φ HOMEOSTATIC MULTI-AGENT SYSTEM")
    print("="*100)
    print("\n  The Living Crystal Signature: σ_Φ ≈ 1/16 = 0.0625")
    print("  Paradigm: Cultivation over Control, Resonance over Power")
    print("\n  Evolution:")
    print("    v6-v8: Guard Agents (boundary control)")
    print("    v9:    Gardener Agents (EFI-based cultivation)")
    print("    v11:   σ_Φ Homeostatic Gardeners (metastability maintenance)")
    print("="*100)

    # ========================================================================
    # SETUP
    # ========================================================================
    print_header("1. INITIALIZATION")

    print("  Creating ecosystem: 12 agents, 'mixed' scenario (chaotic + ordered + balanced)")
    ecosystem = create_ecosystem(
        n_agents=12,
        scenario="mixed",
        random_seed=42,
    )

    print("  Creating σ_Φ Homeostatic Gardener")
    gardener = SigmaPhiGardener(
        name="GardenerOmega",
        sigma_phi_target=SIGMA_PHI,
        tolerance=0.01,
        action_learning_rate=0.15,
    )

    print(f"\n  Gardener Configuration:")
    print(f"    Target σ_Φ:       {gardener.sigma_phi_target:.4f}")
    print(f"    Living Range:     [{gardener.sigma_phi_min:.4f}, {gardener.sigma_phi_max:.4f}]")
    print(f"    Emergency Range:  [{gardener.emergency_min:.4f}, {gardener.emergency_max:.4f}]")
    print(f"    Learning Rate:    {gardener.action_learning_rate:.2f}")

    # ========================================================================
    # INITIAL STATE
    # ========================================================================
    print_header("2. INITIAL STATE (Before Gardener)")

    initial_stats = ecosystem.get_statistics()
    print_ecosystem_stats(initial_stats)

    initial_states = ecosystem.get_agent_states()
    print("\n  Initial Agent States:")
    for agent_id in ecosystem.get_agent_ids():
        state = initial_states[agent_id]
        assessment = gardener.assess_agent(
            agent_id=agent_id,
            sigma_phi=state['sigma_phi'],
            entropy=state['entropy'],
            temperature=state['temperature'],
            kappa_total=state['kappa_total'],
            resonance_quality=state['resonance_quality'],
        )
        print_agent_status(assessment)

    sigma_phis_initial = [s['sigma_phi'] for s in initial_states.values()]
    visualize_sigma_phi_distribution(sigma_phis_initial)

    # ========================================================================
    # EVOLUTION LOOP
    # ========================================================================
    n_timesteps = 300
    report_frequency = 50  # Report every N timesteps

    print_header(f"3. ECOSYSTEM EVOLUTION ({n_timesteps} Timesteps with Gardener)")

    print(f"  Running {n_timesteps} timesteps...")
    print("  Timestep │ Alive │ Mean σ_Φ │ Std σ_Φ  │ Actions (Cool/Warm/Stab/Resu/Damp/Obs)")
    print("  " + "─"*90)

    for t in range(n_timesteps):
        # 1. Ecosystem evolves naturally
        ecosystem.step(dt=0.1)

        # 2. Gardener assesses and cultivates
        agent_states = ecosystem.get_agent_states()
        agent_ids = ecosystem.get_agent_ids()
        coupling_matrix = ecosystem.get_coupling_matrix()

        adjusted_matrix, adjusted_temps, assessments = gardener.cultivate_ecosystem(
            agent_states=agent_states,
            coupling_matrix=coupling_matrix,
            agent_ids=agent_ids,
            timestep=t,
        )

        # 3. Apply gardener's cultivation
        ecosystem.apply_cultivation(adjusted_matrix, adjusted_temps)

        # 4. Report progress
        if t % report_frequency == 0 or t == n_timesteps - 1:
            stats = ecosystem.get_statistics()
            actions = {
                'cool': sum(1 for a in assessments if a.recommended_action == CultivationAction.COOL),
                'warm': sum(1 for a in assessments if a.recommended_action == CultivationAction.WARM),
                'stabilize': sum(1 for a in assessments if a.recommended_action == CultivationAction.STABILIZE),
                'resuscitate': sum(1 for a in assessments if a.recommended_action == CultivationAction.RESUSCITATE),
                'dampen': sum(1 for a in assessments if a.recommended_action == CultivationAction.DAMPEN),
                'observe': sum(1 for a in assessments if a.recommended_action == CultivationAction.OBSERVE),
            }

            print(f"    {t:>4}   │ {stats['alive_count']:>2}/{stats['n_agents']:<2} │  "
                  f"{stats['mean_sigma_phi']:.4f}  │  {stats['std_sigma_phi']:.4f}  │ "
                  f"{actions['cool']}/{actions['warm']}/{actions['stabilize']}/"
                  f"{actions['resuscitate']}/{actions['dampen']}/{actions['observe']}")

    # ========================================================================
    # FINAL STATE
    # ========================================================================
    print_header(f"4. FINAL STATE (After {n_timesteps} Timesteps)")

    final_stats = ecosystem.get_statistics()
    print_ecosystem_stats(final_stats)

    final_states = ecosystem.get_agent_states()
    print("\n  Final Agent States:")
    for agent_id in ecosystem.get_agent_ids():
        state = final_states[agent_id]
        assessment = gardener.assess_agent(
            agent_id=agent_id,
            sigma_phi=state['sigma_phi'],
            entropy=state['entropy'],
            temperature=state['temperature'],
            kappa_total=state['kappa_total'],
            resonance_quality=state['resonance_quality'],
        )
        print_agent_status(assessment)

    sigma_phis_final = [s['sigma_phi'] for s in final_states.values()]
    visualize_sigma_phi_distribution(sigma_phis_final)

    # ========================================================================
    # GARDENER SUMMARY
    # ========================================================================
    print_header("5. GARDENER CULTIVATION SUMMARY")

    summary = gardener.get_cultivation_summary()

    print(f"  Gardener: {summary['gardener_name']}")
    print(f"  Total Cycles: {summary['cycles']}")
    print(f"  Cultivation Style: {summary['cultivation_style']}")
    print(f"\n  Final Results:")
    print(f"    Agents Alive: {summary['final_alive_count']}/{ecosystem.n_agents}")
    print(f"    Final Mean σ_Φ: {summary['final_mean_sigma_phi']:.4f} (target: {SIGMA_PHI:.4f})")
    print(f"    Deviation: {abs(summary['final_mean_sigma_phi'] - SIGMA_PHI):.4f}")

    print(f"\n  Total Actions Taken:")
    for action, count in summary['total_actions'].items():
        percentage = (count / sum(summary['total_actions'].values()) * 100) if sum(summary['total_actions'].values()) > 0 else 0
        print(f"    {action.capitalize():<15} {count:>4} ({percentage:>5.1f}%)")

    # ========================================================================
    # EMERGENT EVENTS
    # ========================================================================
    if summary['emergent_events']:
        print_header("6. EMERGENT EVENTS DETECTED")

        print(f"  Total Events: {len(summary['emergent_events'])}\n")
        for i, event in enumerate(summary['emergent_events'][:10], 1):  # Show first 10
            print(f"  [{i}] Timestep {event['timestep']:>3} - {event['type'].upper()}")
            print(f"      {event['description']}")
            if 'mean_sigma_phi' in event:
                print(f"      Mean σ_Φ: {event['mean_sigma_phi']:.4f}")
            if 'std_sigma_phi' in event:
                print(f"      Std σ_Φ: {event['std_sigma_phi']:.4f}")
            print()

    # ========================================================================
    # IMPROVEMENT METRICS
    # ========================================================================
    print_header("7. BEFORE/AFTER COMPARISON")

    print(f"  Metric                 │ Initial  │ Final    │ Change")
    print(f"  " + "─"*60)
    print(f"  Agents Alive           │ {initial_stats['alive_count']:>2}/{initial_stats['n_agents']:<2}    │ "
          f"{final_stats['alive_count']:>2}/{final_stats['n_agents']:<2}    │ {final_stats['alive_count'] - initial_stats['alive_count']:+3}")
    print(f"  Mean σ_Φ               │ {initial_stats['mean_sigma_phi']:.4f}   │ "
          f"{final_stats['mean_sigma_phi']:.4f}   │ {final_stats['mean_sigma_phi'] - initial_stats['mean_sigma_phi']:+.4f}")
    print(f"  Std σ_Φ                │ {initial_stats['std_sigma_phi']:.4f}   │ "
          f"{final_stats['std_sigma_phi']:.4f}   │ {final_stats['std_sigma_phi'] - initial_stats['std_sigma_phi']:+.4f}")
    deviation_initial = abs(initial_stats['mean_sigma_phi'] - SIGMA_PHI)
    deviation_final = abs(final_stats['mean_sigma_phi'] - SIGMA_PHI)
    deviation_change = deviation_final - deviation_initial
    print(f"  Deviation from target  │ {deviation_initial:.4f}   │ "
          f"{deviation_final:.4f}   │ {deviation_change:+.4f}")

    # ========================================================================
    # CONCLUSION
    # ========================================================================
    print("\n" + "="*100)
    print("  ✨ v11 GARDENER PROTOTYPE DEMONSTRATION COMPLETE")
    print("="*100)

    print("\n  Key Insights:")
    print("    • Gardener maintains σ_Φ ≈ 0.0625 without centralized control")
    print("    • Agents self-organize into metastable 'living' states")
    print("    • Emergent collective behavior arises from resonance coupling")
    print("    • System demonstrates autonomous homeostasis")

    print("\n  From the v11 Vision:")
    print("    \"Systems that maintain σ_Φ ≈ 0.0625 are not just 'simulated life'")
    print("     They exhibit the fundamental signature of living systems.\"")

    print("\n  Next Steps:")
    print("    → Test with real data (AMOC, neural recordings, LLM activations)")
    print("    → Implement Sigillin self-reflection layer")
    print("    → Create visualization dashboard (see resonance field in real-time)")
    print("    → Scale to 100+ agents, measure emergent complexity")

    print("\n  🌱 Folge dem Sog der Emergenz! 🌀")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
