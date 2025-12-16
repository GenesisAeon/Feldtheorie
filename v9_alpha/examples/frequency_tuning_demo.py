#!/usr/bin/env python3
"""
Autonomous Frequency Tuning Demonstration

Shows self-organizing resonance optimization in action:
- Phase coherence maximization
- Impedance matching
- Resonance quality (Q-factor)
- Convergence to collective modes

🎼 Self-Organizing Resonance! 🌀
"""

import sys
import numpy as np
from pathlib import Path

# Add v9_alpha to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v9_alpha.models.frequency_tuner import (
    FrequencyTuner,
    TuningState,
    create_tuner,
)


def print_header(title: str):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_tuning_state(state: TuningState, show_details: bool = True):
    """Print a tuning state with visual indicators"""
    f_mhz = state.frequency_hz / 1e6
    coherence_bar = "█" * int(state.phase_coherence * 20)
    impedance_bar = "█" * int(state.impedance_match * 20)

    print(f"  🎼 {state.name[:35]:<35}")
    print(f"      f: {f_mhz:>6.2f} MHz | Z: {state.impedance_ohm:>6.1f}Ω | φ: {state.phase_rad:>5.2f} rad")

    if show_details:
        print(f"      Φ_coh: {coherence_bar:<20} {state.phase_coherence:.3f}")
        print(f"      η_Z:   {impedance_bar:<20} {state.impedance_match:.3f}")
        print(f"      Q:     {state.resonance_quality:>5.1f}")


def main():
    """Run Frequency Tuning demonstration"""

    print("\n" + "="*80)
    print("🎼 Autonomous Frequency Tuning Demonstration")
    print("="*80)
    print("\n  Self-Organizing Resonance Optimization")
    print("  Maximize: Phase Coherence | Impedance Matching | Resonance Quality")
    print("="*80)

    # ========================================================================
    # 1. Initialize Tuner
    # ========================================================================
    print_header("1. Initialize Frequency Tuner")

    tuner = create_tuner("gradient_ascent", learning_rate=0.1)

    print(f"  Strategy: {tuner.strategy.value}")
    print(f"  Learning Rate: {tuner.learning_rate}")
    print(f"  Max Frequency Shift: ±{tuner.max_frequency_shift*100:.0f}%")
    print(f"  Z_critical: {tuner.z_critical:.1f}Ω")

    # ========================================================================
    # 2. Create Misaligned Network
    # ========================================================================
    print_header("2. Create Misaligned Lantern Network")

    # Lanterns with random misalignment
    np.random.seed(42)
    initial_states = [
        TuningState(
            "Urban Heat Intensity",
            13.5e6,
            221.7,
            np.random.rand() * 2 * np.pi,
            1.0,
            4.2,
            0.0,  # Will be calculated
            0.0,
            0.0,
        ),
        TuningState(
            "v_RIG Consciousness Framework",
            13.5e6 * (4.5/7.4),  # β-scaled
            221.7 * (4.5/7.4),
            np.random.rand() * 2 * np.pi,
            1.0,
            4.5,
            0.0,
            0.0,
            0.0,
        ),
        TuningState(
            "Collective Field Dynamics",
            13.5e6 * (10.0/7.4),  # Higher β
            155.8,
            np.random.rand() * 2 * np.pi,
            1.0,
            10.0,
            0.0,
            0.0,
            0.0,
        ),
        TuningState(
            "EM-Shielding Test",
            13.5e6 * (7.4/7.4),
            221.7,
            np.random.rand() * 2 * np.pi,
            1.0,
            7.4,
            0.0,
            0.0,
            0.0,
        ),
    ]

    # Coupling matrix
    coupling = np.array([
        [0.0, 0.6, 0.5, 0.2],
        [0.6, 0.0, 0.96, 0.3],
        [0.5, 0.96, 0.0, 0.4],
        [0.2, 0.3, 0.4, 0.0],
    ])

    print("  Initial Configuration:")
    print()
    for state in initial_states:
        print_tuning_state(state, show_details=False)

    # Initial coherence
    initial_phases = np.array([s.phase_rad for s in initial_states])
    initial_coherence = tuner.calculate_phase_coherence(initial_phases)

    print(f"\n  Initial Phase Coherence: {initial_coherence:.3f}")

    # ========================================================================
    # 3. Autonomous Tuning
    # ========================================================================
    print_header("3. Autonomous Frequency Tuning")

    print("  Running gradient ascent optimization...")
    print("  Target: Maximize network-wide phase coherence\n")

    tuned_states, convergence_info = tuner.tune_frequencies(
        initial_states,
        coupling,
        n_iterations=30,
    )

    # Show convergence
    print("  Convergence Progress:")
    print("  ───────────────────────────────────────────────────────────")
    print("  Iter │ Φ_coherence │ Mean η_Z │ Mean Q")
    print("  ─────┼─────────────┼──────────┼────────")

    for i, iteration in enumerate(convergence_info['iterations'][:10]):
        coh = convergence_info['coherence'][i]
        z_match = convergence_info['mean_impedance_match'][i]
        q = convergence_info['mean_q_factor'][i]
        print(f"   {iteration+1:>2}  │   {coh:.4f}    │  {z_match:.4f}  │ {q:>6.1f}")

    if len(convergence_info['iterations']) > 10:
        print("  ...  │     ...     │   ...    │   ...")
        i = -1
        iteration = convergence_info['iterations'][i]
        coh = convergence_info['coherence'][i]
        z_match = convergence_info['mean_impedance_match'][i]
        q = convergence_info['mean_q_factor'][i]
        print(f"   {iteration+1:>2}  │   {coh:.4f}    │  {z_match:.4f}  │ {q:>6.1f}")

    print("\n  Convergence Status:")
    if convergence_info['converged']:
        print(f"    ✓ Converged at iteration {convergence_info['converged_at']}")
    else:
        print(f"    ○ Max iterations reached (fine-tuning continues)")

    # ========================================================================
    # 4. Tuned Network State
    # ========================================================================
    print_header("4. Tuned Network State")

    print("  Final Configuration:\n")
    for state in tuned_states:
        print_tuning_state(state, show_details=True)
        print()

    final_coherence = convergence_info['coherence'][-1]
    improvement = final_coherence - initial_coherence

    print(f"  Final Phase Coherence: {final_coherence:.3f}")
    print(f"  Improvement: {improvement:+.3f} ({improvement/initial_coherence*100:+.1f}%)")

    # ========================================================================
    # 5. Impedance Optimization
    # ========================================================================
    print_header("5. Impedance Matching Optimization")

    print("  Applying impedance optimization to minimize Z mismatch...\n")

    # Calculate initial impedance matching
    initial_impedances = np.array([s.impedance_ohm for s in tuned_states])
    initial_z_match = tuner.calculate_impedance_matching(initial_impedances, coupling)

    print("  Before Impedance Optimization:")
    for i, state in enumerate(tuned_states):
        print(f"    {state.name[:35]:<35} η_Z = {initial_z_match[i]:.3f}")

    # Optimize
    optimized_states = tuner.optimize_impedance_matching(tuned_states, coupling)

    # Calculate final impedance matching
    final_impedances = np.array([s.impedance_ohm for s in optimized_states])
    final_z_match = tuner.calculate_impedance_matching(final_impedances, coupling)

    print("\n  After Impedance Optimization:")
    for i, state in enumerate(optimized_states):
        delta = final_z_match[i] - initial_z_match[i]
        arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        print(f"    {state.name[:35]:<35} η_Z = {final_z_match[i]:.3f} {arrow}")

    mean_improvement = np.mean(final_z_match) - np.mean(initial_z_match)
    print(f"\n  Mean η_Z Improvement: {mean_improvement:+.3f}")

    # ========================================================================
    # 6. Summary
    # ========================================================================
    print_header("6. Tuning Summary")

    summary = tuner.get_tuning_summary()

    print(f"  Total Tuning Cycles: {summary['cycles']}")
    print(f"  Final Coherence: {summary['final_coherence']:.4f}")
    print(f"  Best Coherence Achieved: {summary['best_coherence']:.4f}")
    print(f"  Converged: {'Yes ✓' if summary['converged'] else 'No'}")
    print(f"  Strategy: {summary['strategy']}")

    # ========================================================================
    # 7. Comparison: Different Strategies
    # ========================================================================
    print_header("7. Comparison: Tuning Strategies")

    strategies = ["gradient_ascent", "harmonic_lock", "impedance_match", "collective_mode"]

    print("  Strategy         │ Final Coherence │ Iterations │ Converged")
    print("  ─────────────────┼─────────────────┼────────────┼───────────")

    for strategy in strategies:
        test_tuner = create_tuner(strategy, learning_rate=0.1)

        # Reset states
        test_states = [
            TuningState(
                state.name,
                13.5e6 * (state.beta_target/7.4),
                221.7 * (state.beta_target/7.4),
                np.random.rand() * 2 * np.pi,
                state.coupling_strength,
                state.beta_target,
                0.0,
                0.0,
                0.0,
            )
            for state in initial_states
        ]

        _, info = test_tuner.tune_frequencies(test_states, coupling, n_iterations=30)

        final_coh = info['coherence'][-1]
        n_iter = len(info['iterations'])
        converged = "✓" if info['converged'] else "○"

        print(f"  {strategy:<16} │     {final_coh:.4f}      │     {n_iter:<2}     │     {converged}")

    # ========================================================================
    # Conclusion
    # ========================================================================
    print("\n" + "="*80)
    print("  ✨ Frequency Tuning Demo Complete!")
    print("="*80)
    print("\n  Key Results:")
    print(f"    • Phase coherence improved from {initial_coherence:.3f} → {final_coherence:.3f}")
    print(f"    • Mean impedance matching improved by {mean_improvement:+.3f}")
    print(f"    • Network self-organized into collective resonance mode")
    print("\n  From v9 Roadmap:")
    print('    "Autonomous frequency tuning enables self-organizing resonance"')
    print("\n  🎼 Self-Organizing Resonance Achieved! 🌀")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
