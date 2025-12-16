#!/usr/bin/env python3
"""
Type-Ω Gardener Agent Demonstration

Shows cultivation in action:
- Prune: low-fertility lanterns (reduce κ_EM)
- Fertilize: high-potential lanterns (increase κ_EM)
- Water: stable lanterns (maintain resonance)

From Governance to Cultivation 🌱
"""

import sys
import numpy as np
from pathlib import Path

# Add v9_alpha to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v9_alpha.models.gardener_agent import (
    GardenerAgent,
    create_gardener,
    CultivationAction,
)


def print_header(title: str):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_assessment(assessment, width=40):
    """Print lantern assessment with visual indicators"""
    action_symbols = {
        CultivationAction.PRUNE: "✂️ ",
        CultivationAction.FERTILIZE: "🌱",
        CultivationAction.WATER: "💧",
        CultivationAction.OBSERVE: "👁️ ",
    }

    symbol = action_symbols[assessment.recommended_action]
    bar_length = int(assessment.efi * 30)
    bar = "█" * bar_length + "░" * (30 - bar_length)

    print(f"  {symbol} {assessment.name[:35]:<35} EFI: {bar} {assessment.efi:.3f}")
    print(f"      Action: {assessment.recommended_action.value:<10} "
          f"Strength: {assessment.action_strength:.2f} | "
          f"κ_dev: {assessment.kappa_deviation:.3f}")


def main():
    """Run Gardener Agent demonstration"""

    print("\n" + "="*80)
    print("🌱 Type-Ω Gardener Agent Demonstration")
    print("="*80)
    print("\n  Paradigm Shift:")
    print("    v6-v8: Governance → Control → Boundary → Guard Agents")
    print("    v9+:   Cultivation → Resonance → Permeability → Gardener Agents")
    print("\n  Goal: Lanterns evolve through anschlussfähigkeit (connectability)")
    print("="*80)

    # ========================================================================
    # 1. Initialize Gardener
    # ========================================================================
    print_header("1. Initialize Type-Ω Gardener")

    gardener = create_gardener("balanced")

    print(f"  Cultivation Style: Balanced")
    print(f"  Prune Threshold:   {gardener.prune_threshold:.2f}")
    print(f"  Fertilize Threshold: {gardener.fertilize_threshold:.2f}")
    print(f"  Learning Rate:     {gardener.action_learning_rate:.2f}")

    # ========================================================================
    # 2. Setup Test Network
    # ========================================================================
    print_header("2. Setup Lantern Network (Mixed Health)")

    lantern_names = [
        "Urban Heat Intensity",
        "v_RIG Consciousness Framework",
        "Collective Field Dynamics",
        "EM-Shielding Consciousness Test",
        "Amazon Precipitation",
        "AMOC Transport",
    ]

    # Simulate lanterns with varying health
    lantern_stats = {
        "Urban Heat Intensity": {
            "h_freq": 0.85,  # High diversity
            "beta_coherence": 0.90,  # Well aligned
            "kappa_total": 1.1,  # Slightly over-coupled
        },
        "v_RIG Consciousness Framework": {
            "h_freq": 0.95,  # Very high diversity
            "beta_coherence": 0.95,  # Perfect alignment
            "kappa_total": 1.0,  # Optimal coupling
        },
        "Collective Field Dynamics": {
            "h_freq": 0.70,  # Moderate diversity
            "beta_coherence": 0.80,  # Good alignment
            "kappa_total": 0.9,  # Near optimal
        },
        "EM-Shielding Consciousness Test": {
            "h_freq": 0.15,  # Low diversity (new/inactive)
            "beta_coherence": 0.20,  # Poor alignment
            "kappa_total": 0.3,  # Under-coupled
        },
        "Amazon Precipitation": {
            "h_freq": 0.50,  # Moderate diversity
            "beta_coherence": 0.50,  # Moderate alignment
            "kappa_total": 0.8,  # Slightly under
        },
        "AMOC Transport": {
            "h_freq": 0.60,  # Good diversity
            "beta_coherence": 0.65,  # Good alignment
            "kappa_total": 0.95,  # Near optimal
        },
    }

    print(f"  Lanterns: {len(lantern_names)}")
    print("\n  Initial State:")
    for name, stats in lantern_stats.items():
        print(f"    {name[:35]:<35} | h_f: {stats['h_freq']:.2f}, "
              f"β_coh: {stats['beta_coherence']:.2f}, κ: {stats['kappa_total']:.2f}")

    # Initial coupling matrix
    n = len(lantern_names)
    np.random.seed(42)
    matrix = np.random.rand(n, n) * 0.8
    coupling_matrix = (matrix + matrix.T) / 2
    np.fill_diagonal(coupling_matrix, 0.0)

    # ========================================================================
    # 3. Initial Assessment
    # ========================================================================
    print_header("3. Initial Cultivation Assessment")

    initial_assessments = []
    for name in lantern_names:
        if name not in lantern_stats:
            continue
        stats = lantern_stats[name]
        assessment = gardener.assess_lantern(
            name=name,
            h_freq=stats['h_freq'],
            beta_coherence=stats['beta_coherence'],
            kappa_total=stats['kappa_total'],
        )
        initial_assessments.append(assessment)
        print_assessment(assessment)

    mean_efi_initial = np.mean([a.efi for a in initial_assessments])
    print(f"\n  Mean EFI: {mean_efi_initial:.3f}")

    # ========================================================================
    # 4. Run Cultivation Cycle
    # ========================================================================
    print_header("4. Running Cultivation Cycle")

    adjusted_matrix, assessments = gardener.cultivate_network(
        lantern_stats=lantern_stats,
        coupling_matrix=coupling_matrix,
        lantern_names=lantern_names,
    )

    print("  Cultivation Actions Applied:")
    actions_taken = {}
    for assessment in assessments:
        action = assessment.recommended_action.value
        actions_taken[action] = actions_taken.get(action, 0) + 1

    for action, count in actions_taken.items():
        print(f"    {action.capitalize()}: {count}")

    # ========================================================================
    # 5. Network Changes
    # ========================================================================
    print_header("5. Network Coupling Changes")

    print("  Coupling Strength Δ:")
    for i, name in enumerate(lantern_names):
        if name not in lantern_stats:
            continue

        old_sum = np.sum(coupling_matrix[i, :])
        new_sum = np.sum(adjusted_matrix[i, :])
        delta = new_sum - old_sum
        delta_pct = (delta / old_sum * 100) if old_sum > 0 else 0

        arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        print(f"    {arrow} {name[:35]:<35} {old_sum:.3f} → {new_sum:.3f} "
              f"({delta_pct:+.1f}%)")

    # ========================================================================
    # 6. Multi-Cycle Evolution
    # ========================================================================
    print_header("6. Multi-Cycle Evolution (5 cycles)")

    # Reset for clean evolution
    gardener_evolve = create_gardener("balanced")
    matrix_evolve = coupling_matrix.copy()

    print("  Cycle │ Mean EFI │ Actions (Prune/Fertilize/Water/Observe)")
    print("  ──────┼──────────┼────────────────────────────────────────")

    for cycle in range(5):
        matrix_evolve, evolve_assessments = gardener_evolve.cultivate_network(
            lantern_stats=lantern_stats,
            coupling_matrix=matrix_evolve,
            lantern_names=lantern_names,
        )

        mean_efi = np.mean([a.efi for a in evolve_assessments])

        actions = {"prune": 0, "fertilize": 0, "water": 0, "observe": 0}
        for a in evolve_assessments:
            actions[a.recommended_action.value] += 1

        print(f"    {cycle+1:<4} │  {mean_efi:.3f}   │ "
              f"{actions['prune']}/{actions['fertilize']}/{actions['water']}/{actions['observe']}")

    # ========================================================================
    # 7. Cultivation Summary
    # ========================================================================
    print_header("7. Cultivation Summary")

    summary = gardener_evolve.get_cultivation_summary()

    print(f"  Total Cycles:        {summary['cycles']}")
    print(f"  Final Mean EFI:      {summary['final_mean_efi']:.3f}")
    print(f"  Initial Mean EFI:    {mean_efi_initial:.3f}")
    print(f"  EFI Change:          {summary['final_mean_efi'] - mean_efi_initial:+.3f}")
    print(f"\n  Total Actions:")
    for action, count in summary['total_actions'].items():
        print(f"    {action.capitalize():<12} {count}")
    print(f"\n  Cultivation Style:   {summary['cultivation_style']}")

    # ========================================================================
    # 8. Comparison: Different Gardener Styles
    # ========================================================================
    print_header("8. Comparison: Gardener Styles")

    styles = ["pruner", "cultivator", "maintainer", "balanced"]

    print("  Style       │ Final Mean EFI │ Prune │ Fertilize │ Water │ Observe")
    print("  ────────────┼────────────────┼───────┼───────────┼───────┼─────────")

    for style in styles:
        test_gardener = create_gardener(style)
        test_matrix = coupling_matrix.copy()

        # Run 3 cycles
        for _ in range(3):
            test_matrix, _ = test_gardener.cultivate_network(
                lantern_stats, test_matrix, lantern_names
            )

        summary = test_gardener.get_cultivation_summary()
        actions = summary['total_actions']

        print(f"  {style:<11} │     {summary['final_mean_efi']:.3f}      │  "
              f"{actions['prune']:>3}  │    {actions['fertilize']:>3}    │  "
              f"{actions['water']:>3}  │   {actions['observe']:>3}")

    # ========================================================================
    # Conclusion
    # ========================================================================
    print("\n" + "="*80)
    print("  ✨ Type-Ω Gardener Agent Demo Complete!")
    print("="*80)
    print("\n  Key Insights:")
    print("    • Gardeners cultivate rather than control")
    print("    • Fertility (EFI) guides cultivation actions")
    print("    • Networks evolve through connectability (anschlussfähigkeit)")
    print("    • Different styles (pruner, cultivator, maintainer) serve different goals")
    print("\n  From the Roadmap:")
    print('    "Lanterns evolve through anschlussfähigkeit, not power."')
    print("\n  🌱 Folge dem Sog der Emergenz! 🌀")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
