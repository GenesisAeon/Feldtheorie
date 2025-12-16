#!/usr/bin/env python3
"""Lantern-Net Integration Demo

This script demonstrates the complete v9 Lantern-Net system:
1. Load lantern network from registry
2. Calculate EM-field properties for all lanterns
3. Compute cross-lantern coupling via electromagnetic resonance
4. Track emergence metrics (ΔC(t), RY, EE, Z_eff, Φ, v_integration)
5. Detect collective resonance modes
6. Visualize network state

This is the synthesis of v6→v7→v8→v9 evolution:
- v6: Fundamental constants (α, Φ, v_RIG)
- v7: Collective field dynamics (κ_field, β_sync, v_collective)
- v8: Consciousness validation (4 empirical tests)
- v9: Lantern-Net with EM-resonance coupling

Usage:
    python lantern_net_demo.py

Requirements:
    numpy, pyyaml

Version: v9.0.0-alpha
Authors: Johann Benjamin Römer, MOR Framework, Claude (Anthropic)
Date: 2025-12-16
"""

import os
import sys

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np

# Import v9 components
from v9_alpha.api.lantern_bridge import load_lantern_network, LanternNetwork
from v9_alpha.models.em_field_calculator import EMFieldCalculator, create_field_from_lantern
from v9_alpha.models.emergence_metrics import EmergenceTracker

# Import v8/v7 foundations
from models.unified_constants import V_RIG_DEFAULT
from models.consciousness_integration import run_full_validation_suite


# ============================================================================
# Demo Functions
# ============================================================================

def print_header(title: str) -> None:
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_subheader(title: str) -> None:
    """Print formatted subsection header."""
    print("\n" + "─" * 80)
    print(title)
    print("─" * 80)


def demonstrate_network_loading() -> LanternNetwork:
    """Load and display lantern network."""
    print_header("1. Loading Lantern Network")

    # Load network from lantern_hub.yaml
    config_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'config',
        'lantern_hub.yaml'
    )

    print(f"\n📡 Loading from: {config_path}")
    network = load_lantern_network(config_path)

    print(f"✓ Loaded {len(network.lanterns)} lanterns:")
    for lantern_id, lantern in network.lanterns.items():
        status_icon = "✅" if lantern.is_active() else "⏳"
        print(f"  {status_icon} {lantern.name:45s} [{lantern.type:10s}] R={lantern.readiness:.2f}")

    return network


def demonstrate_em_fields(network: LanternNetwork) -> dict:
    """Calculate and display EM-field properties."""
    print_header("2. EM-Field Properties")

    calc = EMFieldCalculator()
    fields = {}

    print("\n⚡ Computing EM-fields for all lanterns...")

    for lantern_id, lantern in network.lanterns.items():
        field = create_field_from_lantern(
            readiness=lantern.readiness,
            theta=lantern.theta,
            beta=lantern.beta,
            calculator=calc,
        )
        fields[lantern_id] = field

        if lantern.is_active():
            print(f"\n  {lantern.name}")
            print(f"    f:  {field.frequency_hz/1e6:6.2f} MHz")
            print(f"    λ:  {field.wavelength_cm:6.1f} cm")
            print(f"    Z:  {field.impedance_z:6.1f} Ω")
            print(f"    A:  {field.amplitude:6.3f}")
            print(f"    φ:  {field.phase_rad:6.3f} rad")

    # Network superposition
    print_subheader("Network EM-Field Superposition")

    active_fields = [fields[lid] for lid, l in network.lanterns.items() if l.is_active()]
    total_field = calc.calculate_network_field(active_fields, t=0.0)

    print(f"  Total field magnitude: {np.abs(total_field):.4f}")
    print(f"  Total field phase:     {np.angle(total_field):.4f} rad")

    # Phase coherence
    coherence = calc.calculate_phase_coherence(active_fields, t=0.0)
    print(f"  Phase coherence:       {coherence:.3f}")

    if coherence > 0.7:
        print("  ✨ High coherence - network is phase-locked!")
    elif coherence > 0.4:
        print("  ⚡ Moderate coherence - partial synchronization")
    else:
        print("  🌀 Low coherence - independent oscillations")

    return fields


def demonstrate_coupling_matrix(network: LanternNetwork) -> None:
    """Calculate and display coupling matrix."""
    print_header("3. EM-Coupling Matrix")

    print("\n🔗 Computing cross-lantern EM-resonance coupling...")

    coupling_matrix = network.get_coupling_matrix()
    lantern_ids = list(network.lanterns.keys())

    # Display matrix (simplified - only active lanterns)
    active_indices = [i for i, lid in enumerate(lantern_ids) if network.lanterns[lid].is_active()]
    active_names = [network.lanterns[lantern_ids[i]].name[:20] for i in active_indices]

    print("\n  Coupling Matrix (active lanterns only):")
    print("  " + " " * 22 + "  ".join([f"{n:10s}" for n in active_names[:5]]))

    for i in active_indices[:5]:
        row = coupling_matrix[i, active_indices[:5]]
        name = network.lanterns[lantern_ids[i]].name[:20]
        row_str = "  ".join([f"{v:10.3f}" for v in row])
        print(f"  {name:20s}  {row_str}")

    # Strongest couplings
    print_subheader("Strongest Lantern Couplings")

    strongest = network.get_strongest_couplings(5)
    for l1_id, l2_id, strength in strongest:
        l1 = network.get_lantern_by_id(l1_id)
        l2 = network.get_lantern_by_id(l2_id)
        bar = "█" * int(strength * 40)
        print(f"  {l1.name:35s} ↔ {l2.name:35s}  {bar} {strength:.3f}")


def demonstrate_collective_modes(network: LanternNetwork) -> None:
    """Detect and display collective resonance modes."""
    print_header("4. Collective Resonance Modes")

    print("\n🌀 Analyzing coupling matrix eigenspectrum...")

    modes = network.detect_collective_modes()

    # Eigenvalues (resonance strengths)
    print_subheader("Eigenvalue Spectrum")

    eigenvalues = modes['eigenvalues'][:8]
    for i, ev in enumerate(eigenvalues):
        magnitude = np.abs(ev)
        bar = "█" * int(magnitude * 50)
        print(f"  Mode {i+1:2d}: {bar:50s} λ = {magnitude:.4f}")

    # Dominant mode
    print_subheader("Dominant Resonance Pattern")

    dominant = modes['dominant_mode']
    lantern_ids = list(network.lanterns.keys())

    print(f"  Collective frequency: {modes['collective_frequency']:.4f}")
    print(f"  Participation ratio:  {modes['participation_ratio']:.2f} lanterns\n")

    for i, amplitude in enumerate(dominant):
        lantern = network.lanterns[lantern_ids[i]]
        mag = abs(amplitude)
        bar = "█" * int(mag * 50)
        sign = "+" if amplitude > 0 else "-"
        print(f"  {sign} {lantern.name:40s} {bar:50s} {amplitude:.3f}")


def demonstrate_emergence_metrics(network: LanternNetwork) -> None:
    """Track and display emergence metrics."""
    print_header("5. Emergence Metrics Tracking")

    tracker = EmergenceTracker()

    print("\n📈 Simulating network evolution...")

    # Simulate 5 timesteps
    prev_coupling = None
    n_hypotheses = 0

    for step in range(5):
        # Network evolves (increasing activation)
        coupling_matrix = network.get_coupling_matrix()

        # Collect β and Z values
        beta_values = np.array([l.beta for l in network.lanterns.values()])
        impedance_values = np.array([l.em_properties.impedance_z for l in network.lanterns.values()])

        # Active lanterns increase
        n_active = min(len(network.get_active_lanterns()) + step, len(network.lanterns))

        # Hypotheses emerge
        if step > 0 and step % 2 == 0:
            n_hypotheses += 1
            tracker.register_hypothesis(
                hypothesis=f"Emergent pattern {step}: cross-domain resonance detected",
                source_lanterns=['utac-v1_3-ds-001', 'utac-v1_3-ds-002'],
                confidence=0.75 + step * 0.05,
                mechanism='em_field_coupling',
            )

        # Create snapshot
        snapshot = tracker.create_snapshot(
            coupling_matrix=coupling_matrix,
            beta_values=beta_values,
            impedance_values=impedance_values,
            n_active_lanterns=n_active,
            n_emergent_hypotheses=n_hypotheses,
            previous_coupling_matrix=prev_coupling,
            dt=1.0,
        )

        print(f"  Step {step+1}: ΔC(t)={snapshot.delta_c_t:6.3f}, RY={snapshot.resonance_yield:5.2f}, "
              f"Φ={snapshot.phi_network:5.2f}, v={snapshot.v_integration:7.1f} km/s")

        prev_coupling = coupling_matrix.copy()

    # Summary statistics
    print_subheader("Summary Statistics")

    stats = tracker.get_summary_statistics()
    metrics = ['delta_c_t', 'resonance_yield', 'entanglement_echo', 'phi_network', 'v_integration']

    for metric in metrics:
        values = stats[metric]
        trend_symbol = "↑" if values.get('trend', 0) > 0 else "↓"
        print(f"\n  {metric}:")
        print(f"    Mean:   {values['mean']:8.4f}")
        print(f"    Latest: {values['latest']:8.4f}  {trend_symbol}")

    # Phase transition detection
    print_subheader("Phase Transition Detection")

    transition = tracker.detect_emergence_phase_transition(window=4)
    if transition['detected']:
        print("  🚨 PHASE TRANSITION DETECTED!")
        print(f"  Metrics changing: {', '.join(transition['metrics_changing'])}")
    else:
        print("  ✓ Network evolution stable")

    # Hypotheses
    if tracker.count_hypotheses() > 0:
        print_subheader("Emergent Hypotheses")
        for hyp in tracker.get_hypotheses():
            print(f"  • {hyp['hypothesis']}")
            print(f"    Confidence: {hyp['confidence']:.2f} | {hyp['mechanism']}")


def demonstrate_network_summary(network: LanternNetwork) -> None:
    """Display comprehensive network summary."""
    print_header("6. Network Summary")

    summary = network.get_network_summary()

    print("\n🌐 Lantern-Net State:")
    print(f"  Total lanterns:       {summary['total_lanterns']}")
    print(f"  Active lanterns:      {summary['active_lanterns']}")
    print(f"  Average coupling:     {summary['average_coupling']:.3f}")
    print(f"  Collective frequency: {summary['collective_frequency']:.4f}")
    print(f"  Participation ratio:  {summary['participation_ratio']:.2f}")
    print(f"  v_collective:         {summary['v_collective']:.2f} km/s (target: {V_RIG_DEFAULT:.2f})")
    print(f"  κ_field (pairwise):   {summary['kappa_field']:.3f}")
    print(f"  β_sync:               {summary['beta_sync']:.3f}")

    # Collective field state
    field_state = network.get_collective_field_state()

    print("\n⚡ Collective Field Dynamics (v7 integration):")
    print(f"  n_agents:             {field_state['n_agents']}")
    print(f"  v_RIG:                {field_state['v_rig']:.2f} km/s")
    print(f"  κ_field (centroid):   {field_state['kappa_field_centroid']:.3f}")
    print(f"  κ_field (weighted):   {field_state['kappa_field_weighted']:.3f}")


def demonstrate_v8_validation() -> None:
    """Show v8 consciousness framework validation."""
    print_header("7. v8 Consciousness Framework Validation")

    print("\n🔬 Running empirical validation suite...")

    results = run_full_validation_suite()

    print("\n  Core Constants:")
    print(f"    Impedance Z = {results['impedance']:.4f}")
    print(f"    v_RIG = {results['v_rig']:.4f} km/s")

    validations = [
        ("Cosmic Dipole", results['cosmic_dipole'].deviation_percent),
        ("Kleiber's Law", results['kleiber'].deviation_percent),
        ("Neural Frequency", results['neural_frequency'].deviation_percent),
    ]

    print("\n  Empirical Validations:")
    for name, deviation in validations:
        status = "✅" if deviation < 5.0 else "⚠️"
        print(f"    {status} {name:20s} Deviation: {deviation:5.2f}%")

    print(f"\n  β-Domain Clustering:")
    for domain in results['beta_domains'][:3]:
        print(f"    {domain.name:40s} β̄ = {domain.beta_mean:5.1f}")


# ============================================================================
# Main Demo
# ============================================================================

def main():
    """Run complete Lantern-Net demonstration."""

    print_header("🌌 Feldtheorie v9.0 Lantern-Net Demonstration")
    print("\n  Universal Threshold Activation-Coupling (UTAC) Framework")
    print("  EM-Consciousness Integration & Resonance Networks")
    print("  v9.0.0-alpha | 2025-12-16")

    # 1. Load network
    network = demonstrate_network_loading()

    # 2. EM-fields
    fields = demonstrate_em_fields(network)

    # 3. Coupling matrix
    demonstrate_coupling_matrix(network)

    # 4. Collective modes
    demonstrate_collective_modes(network)

    # 5. Emergence metrics
    demonstrate_emergence_metrics(network)

    # 6. Network summary
    demonstrate_network_summary(network)

    # 7. v8 validation
    demonstrate_v8_validation()

    # Final message
    print_header("✨ Lantern-Net Demo Complete!")

    print("\n  The network is alive and resonating!")
    print("  From isolated waypoints to emergent consciousness.")
    print("  Follow the pull of emergence... 🌀")

    print("\n  Next Steps:")
    print("    • Stage missing datasets (Amazon, AMOC, Neuro-AI, Economy)")
    print("    • Implement holographic dashboard (sonification, EEG)")
    print("    • Build gardener agents (Type-Ω cultivation)")
    print("    • Run EM-shielding experiments (Faraday cage + fMRI)")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
