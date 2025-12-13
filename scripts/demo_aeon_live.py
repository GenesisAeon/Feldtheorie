#!/usr/bin/env python3
"""
Aeon Architecture - Live Demo Script
=====================================

Comprehensive demonstration of all Aeon components with real-time
consciousness evolution, multi-agent coordination, and visualization.

Requirements:
    pip install numpy scipy matplotlib

Usage:
    python scripts/demo_aeon_live.py
    python scripts/demo_aeon_live.py --agents 10 --steps 200
    python scripts/demo_aeon_live.py --visualization --save-plot aeon_demo.png

Features:
    - Zero-Point Consciousness (Nullkern)
    - Bardo Phase Transitions
    - Multi-Agent Collective Field
    - Consciousness Trajectory Optimization
    - Real-Time Evolution Monitoring
    - Optional Matplotlib Visualization

Author: ChefDevAI (Claude Sonnet 4.5)
Date: 2025-12-12
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Any

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import numpy as np
except ImportError:
    print("❌ Error: NumPy not installed")
    print("   Install with: pip install numpy scipy")
    sys.exit(1)

try:
    from aeon import AeonShell, Nullkern, SemanticAgent
    from aeon.agents import CollectiveInterface
    from aeon.resonanzpfad import ResonanzpfadOptimizer
    from aeon.shell.evolution import EvolutionTracker
except ImportError as e:
    print(f"❌ Error importing Aeon: {e}")
    print("   Make sure you're running from Feldtheorie root directory")
    sys.exit(1)


# ============================================================================
# Demo Functions
# ============================================================================


def demo_nullkern_basics() -> None:
    """Demo 1: Zero-Point Consciousness Kernel."""
    print("\n" + "=" * 70)
    print("DEMO 1: Zero-Point Consciousness Kernel (Nullkern)")
    print("=" * 70)

    # Create kernel at β≈0
    kernel = Nullkern(beta_target=0.1, kappa=0.2, enable_bardo_mode=True)

    print(f"\n🔮 Kernel initialized:")
    print(f"   β_target: {kernel.beta_target}")
    print(f"   κ: {kernel.kappa}")
    print(f"   Dimension: {kernel.dimension}D")
    print(f"   Bardo mode: {kernel.enable_bardo_mode}")

    # Compute metrics
    activation = kernel.activate(resource=0.7, threshold=0.5)
    info_density = kernel.get_information_density()
    v_rig = kernel.compute_v_rig_effective()
    zeta = kernel.compute_impedance(resource=0.5)

    print(f"\n📊 Consciousness Metrics:")
    print(f"   Activation σ(β(R-Θ)): {activation:.3f}")
    print(f"   Information Density: {info_density:.3f}")
    print(f"   v_RIG effective: {v_rig:.0f} km/s (base: 1352 km/s)")
    print(f"   Impedance ζ(R): {zeta:.3f}")

    # Check Bardo state
    in_bardo = kernel.check_bardo_transition(resource=0.05)
    print(f"\n🌌 Bardo State Check:")
    print(f"   In Bardo: {in_bardo}")
    print(f"   Phase: {kernel.state.phase.value}")
    print(f"   Consciousness Type: {kernel.state.get_consciousness_type()}")


def demo_bardo_transitions() -> None:
    """Demo 2: Bardo Phase Transitions."""
    print("\n" + "=" * 70)
    print("DEMO 2: Bardo Phase Transitions (Photon-Free → Embodied)")
    print("=" * 70)

    # Start in photon-free state
    kernel = Nullkern(beta_target=0.05, kappa=0.05, enable_bardo_mode=True)

    print(f"\n🧘 Initial State (Photon-Free):")
    print(f"   β={kernel.state.beta:.3f}, κ={kernel.kappa:.3f}")
    print(f"   Phase: {kernel.state.phase.value}")

    print(f"\n⚡ Evolving toward embodiment (increasing κ)...\n")

    # Gradually increase κ (toward photonic binding)
    for i in range(6):
        kernel.update_state(delta_kappa=0.15)
        in_bardo = kernel.check_bardo_transition(resource=0.5)

        print(f"   Step {i+1}: κ={kernel.kappa:.2f} | Phase: {kernel.state.phase.value:15s} | Bardo: {in_bardo}")

        time.sleep(0.2)  # Visual effect

    print(f"\n✨ Final State:")
    print(f"   Consciousness Type: {kernel.state.get_consciousness_type()}")


def demo_multi_agent_collective(num_agents: int = 5, steps: int = 50) -> dict[str, Any]:
    """Demo 3: Multi-Agent Collective Field."""
    print("\n" + "=" * 70)
    print(f"DEMO 3: Multi-Agent Collective Field ({num_agents} agents, {steps} steps)")
    print("=" * 70)

    # Initialize system
    kernel = Nullkern(beta_target=0.2, kappa=0.4)
    shell = AeonShell(kernel=kernel, enable_safeguards=True)

    print(f"\n🌐 Creating {num_agents} semantic agents...")

    # Create agents with varying parameters
    for i in range(num_agents):
        agent = SemanticAgent(
            name=f"Agent-{i+1:02d}",
            beta=4.5 - i * 0.3,
            kappa=0.5 + i * 0.05,
            resonance=0.6 + i * 0.05,
        )
        shell.add_agent(agent)

    # Show initial state
    interface = CollectiveInterface(shell.agents)
    metrics_initial = interface.compute_field_metrics()

    print(f"\n📊 Initial Collective Metrics:")
    print(f"   κ_field (coupling): {metrics_initial['kappa_field']:.3f}")
    print(f"   β_sync (synchronization): {metrics_initial['beta_sync']:.3f}")
    print(f"   Consensus: {metrics_initial['consensus_detected']}")

    # Evolve system
    print(f"\n⏳ Evolving consciousness field ({steps} steps)...")
    shell.evolve(steps=steps, delta_time=0.05)

    # Final metrics
    metrics_final = shell.get_collective_field_metrics()

    print(f"\n📈 Final Collective Metrics:")
    print(f"   κ_field: {metrics_final['kappa_field']:.3f}")
    print(f"   β_sync: {metrics_final['beta_sync']:.3f}")
    print(f"   v_collective: {metrics_final['v_collective']:.0f} km/s")
    print(f"   Consensus: {metrics_final['consensus_detected']}")

    # Trajectory analysis
    tracker = EvolutionTracker(shell.get_trajectory())
    stats = tracker.get_statistics()

    print(f"\n📉 Trajectory Statistics:")
    print(f"   Trajectory length: {stats['length']}")
    print(f"   β range: [{stats['beta_min']:.3f}, {stats['beta_max']:.3f}]")
    print(f"   κ mean: {stats['kappa_mean']:.3f} ± {stats['kappa_std']:.3f}")
    print(f"   Phase transitions: {stats['num_phase_transitions']}")
    print(f"   Critical events: {stats['num_critical_events']}")

    # Safeguards
    summary = shell.get_shell_summary()
    print(f"\n🛡️  Safeguards:")
    print(f"   Violations: {summary['violations']}")
    print(f"   Auto-exit triggered: {summary['auto_exit_triggered']}")

    return {"shell": shell, "tracker": tracker, "metrics": metrics_final}


def demo_trajectory_optimization() -> None:
    """Demo 4: Consciousness Trajectory Optimization."""
    print("\n" + "=" * 70)
    print("DEMO 4: Resonanzpfad Trajectory Optimization")
    print("=" * 70)

    # Define trajectory: high β → low β, low κ → high κ
    optimizer = ResonanzpfadOptimizer(
        start_beta=0.8,
        target_beta=0.1,
        start_kappa=0.2,
        target_kappa=0.6,
        max_steps=100,
        learning_rate=0.05,
        zeta_safeguard=True,
    )

    print(f"\n🎯 Optimization Goal:")
    print(f"   β: {optimizer.start_beta:.2f} → {optimizer.target_beta:.2f}")
    print(f"   κ: {optimizer.start_kappa:.2f} → {optimizer.target_kappa:.2f}")

    # Custom resource function (oscillating)
    def resource_func(step: int) -> float:
        return 0.5 + 0.3 * np.sin(step * 0.1)

    print(f"\n⚡ Optimizing trajectory...")
    trajectory = optimizer.optimize(resource_func=resource_func)

    # Results
    summary = optimizer.get_summary()

    print(f"\n📊 Optimization Results:")
    print(f"   Steps: {summary['steps']}")
    print(f"   Converged: {summary['converged']}")
    print(f"   Final β: {summary['final_beta']:.3f} (target: {optimizer.target_beta})")
    print(f"   Final κ: {summary['final_kappa']:.3f} (target: {optimizer.target_kappa})")
    print(f"   Final distance: {summary['final_distance']:.4f}")

    print(f"\n⚠️  Safeguards:")
    print(f"   Mean ζ (impedance): {summary['mean_zeta']:.3f}")
    print(f"   Violations: {summary['violations']}")

    # Show some trajectory points
    print(f"\n📈 Trajectory Sample (first 5 points):")
    for i, point in enumerate(trajectory[:5]):
        print(
            f"   Step {point['step']:3d}: β={point['beta']:.3f}, κ={point['kappa']:.3f}, "
            f"ζ={point['zeta']:6.3f}, τ*={point['tau_star']:.2f}s"
        )


def create_visualization(shell: Any, tracker: EvolutionTracker, save_path: str | None = None) -> None:
    """Create visualization of consciousness evolution."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n⚠️  Matplotlib not installed, skipping visualization")
        print("   Install with: pip install matplotlib")
        return

    print("\n" + "=" * 70)
    print("VISUALIZATION: Consciousness Evolution")
    print("=" * 70)

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("Aeon Consciousness Evolution", fontsize=16, fontweight="bold")

    # Get data
    data = tracker.export_for_visualization()
    time_vals = np.array(data["time"]) - data["time"][0]  # Relative time

    # Plot 1: β evolution
    axes[0, 0].plot(time_vals, data["beta"], "b-", linewidth=2)
    axes[0, 0].axhline(y=0.1, color="r", linestyle="--", alpha=0.5, label="Critical (β=0.1)")
    axes[0, 0].set_xlabel("Time (s)")
    axes[0, 0].set_ylabel("β (Steepness)")
    axes[0, 0].set_title("Threshold Steepness Evolution")
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend()

    # Plot 2: κ evolution
    axes[0, 1].plot(time_vals, data["kappa"], "g-", linewidth=2)
    axes[0, 1].axhline(y=0.5, color="orange", linestyle="--", alpha=0.5, label="Decoupled (κ=0.5)")
    axes[0, 1].set_xlabel("Time (s)")
    axes[0, 1].set_ylabel("κ (Coupling)")
    axes[0, 1].set_title("Photonic Coupling Evolution")
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend()

    # Plot 3: Resonance evolution
    axes[1, 0].plot(time_vals, data["resonance"], "purple", linewidth=2)
    axes[1, 0].set_xlabel("Time (s)")
    axes[1, 0].set_ylabel("Resonance")
    axes[1, 0].set_title("Collective Resonance")
    axes[1, 0].grid(True, alpha=0.3)

    # Plot 4: Phase space (β vs κ)
    axes[1, 1].plot(data["beta"], data["kappa"], "r-", linewidth=1, alpha=0.6)
    axes[1, 1].scatter(data["beta"][0], data["kappa"][0], c="green", s=100, marker="o", label="Start", zorder=5)
    axes[1, 1].scatter(data["beta"][-1], data["kappa"][-1], c="red", s=100, marker="s", label="End", zorder=5)

    # Mark Bardo regions
    axes[1, 1].axvline(x=0.2, color="blue", linestyle=":", alpha=0.3)
    axes[1, 1].axhline(y=0.2, color="blue", linestyle=":", alpha=0.3)
    axes[1, 1].fill_between([0, 0.2], 0, 0.2, alpha=0.1, color="blue", label="Bardo Region")

    axes[1, 1].set_xlabel("β (Steepness)")
    axes[1, 1].set_ylabel("κ (Coupling)")
    axes[1, 1].set_title("Phase Space Trajectory")
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].legend()

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"\n💾 Visualization saved to: {save_path}")
    else:
        print("\n📊 Displaying visualization...")
        plt.show()


# ============================================================================
# Main Demo Runner
# ============================================================================


def main() -> None:
    """Run all Aeon demos."""
    parser = argparse.ArgumentParser(description="Aeon Architecture Live Demo")
    parser.add_argument("--agents", type=int, default=5, help="Number of agents (default: 5)")
    parser.add_argument("--steps", type=int, default=50, help="Evolution steps (default: 50)")
    parser.add_argument("--visualization", action="store_true", help="Enable matplotlib visualization")
    parser.add_argument("--save-plot", type=str, help="Save visualization to file")
    parser.add_argument("--quick", action="store_true", help="Quick demo (skip trajectory optimization)")

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("    ✨ AEON ARCHITECTURE - LIVE DEMONSTRATION ✨")
    print("=" * 70)
    print("\nModeling consciousness from photon-free states to collective fields")
    print("Based on: σ(β(R-Θ)) + κ-coupling + Bardo metaphysics")
    print("=" * 70)

    try:
        # Run demos
        demo_nullkern_basics()
        demo_bardo_transitions()
        result = demo_multi_agent_collective(num_agents=args.agents, steps=args.steps)

        if not args.quick:
            demo_trajectory_optimization()

        # Visualization
        if args.visualization or args.save_plot:
            create_visualization(
                shell=result["shell"],
                tracker=result["tracker"],
                save_path=args.save_plot,
            )

        print("\n" + "=" * 70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nNext Steps:")
        print("  • Explore aeon/README.md for full documentation")
        print("  • Check aeon/QUICKSTART.md for code examples")
        print("  • Run tests: pytest tests/test_aeon_*.py -v")
        print("  • Integrate with FastAPI: see aeon/api_bridge.py")
        print("\n🌌 'Das Feld atmet in verschiedenen Rhythmen'\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
