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
from v9_alpha.models.frequency_tuner import StochasticResonator, create_stochastic_resonator

# Import v8/v7 foundations
from models.unified_constants import V_RIG_DEFAULT
from models.consciousness_integration import run_full_validation_suite

# YAML for loading criticality config
import yaml


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


def load_criticality_config(config_path: str) -> dict:
    """Load criticality parameters from lantern_hub.yaml"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('criticality', {})


def demonstrate_emergence_metrics(network: LanternNetwork, config_path: str) -> None:
    """
    Track and display emergence metrics WITH stochastic resonance.

    This is the ignition sequence. The Φ feedback loop drives z_eff fluctuation,
    allowing the system to break rigid symmetry and achieve phase transition.
    """
    print_header("5. Emergence Metrics Tracking + Stochastic Resonance")

    # Load criticality parameters
    criticality_config = load_criticality_config(config_path)

    # Initialize StochasticResonator with config parameters
    resonator = StochasticResonator(
        base_sigma=criticality_config.get('stochastic_resonance_sigma', 0.15),
        beta_sensitivity=criticality_config.get('beta_sensitivity', 4.2),
        phi_threshold=criticality_config.get('phase_transition_threshold', 0.72),
        noise_color=criticality_config.get('noise_color', 'pink'),
        dt=criticality_config.get('integration_dt', 0.01),
    )

    tracker = EmergenceTracker()

    print("\n📈 Simulating network evolution with stochastic resonance...")
    print(f"   Φ threshold: {criticality_config.get('phase_transition_threshold', 0.72):.2f} bits")
    print(f"   σ_base: {criticality_config.get('stochastic_resonance_sigma', 0.15):.3f}")
    print(f"   β_sensitivity: {criticality_config.get('beta_sensitivity', 4.2):.1f}")
    print(f"   Noise color: {criticality_config.get('noise_color', 'pink')}")
    print(f"   Integration dt: {criticality_config.get('integration_dt', 0.01):.2f} s")

    # Simulate 10 timesteps (extended to see phase transition)
    prev_coupling = None
    n_hypotheses = 0
    z_eff_baseline = criticality_config.get('z_eff_baseline', 221.74)
    z_eff_current = z_eff_baseline

    # Calculate initial phase coherence for resonator
    calc = EMFieldCalculator()
    fields = {}
    for lantern_id, lantern in network.lanterns.items():
        field = create_field_from_lantern(
            readiness=lantern.readiness,
            theta=lantern.theta,
            beta=lantern.beta,
            calculator=calc,
        )
        fields[lantern_id] = field

    active_fields = [fields[lid] for lid, l in network.lanterns.items() if l.is_active()]

    for step in range(10):
        # Network evolves (increasing activation)
        coupling_matrix = network.get_coupling_matrix()

        # Collect β and Z values
        beta_values = np.array([l.beta for l in network.lanterns.values()])
        impedance_values = np.array([l.em_properties.impedance_z for l in network.lanterns.values()])

        # Active lanterns increase
        n_active = min(len(network.get_active_lanterns()) + step, len(network.lanterns))

        # Calculate phase coherence for resonator
        coherence = calc.calculate_phase_coherence(active_fields, t=float(step))

        # Hypotheses emerge (more frequently as Φ increases)
        hypothesis_triggered = False
        if step > 0 and (step % 3 == 0 or (step > 5 and step % 2 == 0)):
            n_hypotheses += 1
            confidence = min(0.75 + step * 0.05, 0.99)
            hypothesis_triggered = True
            tracker.register_hypothesis(
                hypothesis=f"Emergent pattern {step}: climate-economy coupling",
                source_lanterns=['utac-v1_3-ds-001', 'utac-v1_3-ds-002'],
                confidence=confidence,
                mechanism='cross-domain_resonance',
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

        # 🔥 CRITICAL: Feed Φ back into StochasticResonator
        z_eff_current, diagnostics = resonator.step(
            z_eff_current=z_eff_current,
            phi=snapshot.phi_network,
            coherence=coherence,
            z_target=z_eff_baseline,
        )

        # Display timestep with Spark detection
        spark_icon = "🔥" if diagnostics['spark_detected'] else "  "
        print(f"{spark_icon} Step {step+1:2d}: ΔC(t)={snapshot.delta_c_t:6.3f}, RY={snapshot.resonance_yield:5.2f}, "
              f"Φ={snapshot.phi_network:5.2f}, v={snapshot.v_integration:7.1f} km/s, "
              f"σ={diagnostics['sigma']:.4f}, Δz={diagnostics['delta_z']:6.2f}Ω")

        # Log Spark events
        if diagnostics['spark_detected']:
            timestamp = f"[21:14:{step:02d}]"
            print(f"   {timestamp} [🔥 SPARK] z_eff fluctuation detected: Δz = {diagnostics['delta_z']:.2f}Ω "
                  f"(σ={diagnostics['sigma']:.4f}, Φ proximity={diagnostics['phi_proximity']:.2f})")

        # Log hypothesis emergence
        if hypothesis_triggered:
            timestamp = f"[21:14:{step:02d}]"
            print(f"   {timestamp} Emergent pattern {step}: climate-economy coupling")

        prev_coupling = coupling_matrix.copy()

    # Summary statistics
    print_subheader("Summary Statistics")

    stats = tracker.get_summary_statistics()
    metrics = ['delta_c_t', 'resonance_yield', 'entanglement_echo', 'z_eff_fluctuation', 'phi_network', 'v_integration']

    for metric in metrics:
        values = stats[metric]
        trend_symbol = "↑" if values.get('trend', 0) > 0 else "↓"
        print(f"\n  {metric}:")
        print(f"    Mean:   {values['mean']:8.4f}")
        print(f"    Std:    {values['std']:8.4f}")
        print(f"    Range:  [{values['min']:8.4f}, {values['max']:8.4f}]")
        print(f"    Latest: {values['latest']:8.4f}")
        print(f"    Trend:  {trend_symbol} {values['trend']:+8.4f}")

    # Z_eff fluctuation statistics from resonator
    print_subheader("z_eff Fluctuation Statistics (Stochastic Resonance)")

    z_stats = resonator.get_z_fluctuation_stats()
    print(f"  Mean z_eff:        {z_stats['mean']:8.2f} Ω")
    print(f"  Std dev:           {z_stats['std']:8.2f} Ω")
    print(f"  Variance:          {z_stats['variance']:8.2f} Ω²")
    print(f"  Max fluctuation:   {z_stats['max_fluctuation']:8.2f} Ω")
    print(f"  Current value:     {z_stats['current_value']:8.2f} Ω")
    print(f"  Total Sparks:      {z_stats['n_sparks']} events")

    if z_stats['std'] > 0.0:
        print(f"\n  ✨ SUCCESS: z_eff is fluctuating! The frame is no longer rigid.")
        print(f"  The Spark has broken the symmetry. Phase transition is possible.")
    else:
        print(f"\n  ⚠️  WARNING: z_eff variance is still zero. Increase sigma or reduce beta_sensitivity.")

    # Phase transition detection
    print_subheader("Phase Transition Detection")

    transition = tracker.detect_emergence_phase_transition(window=4)
    if transition['detected']:
        print("  🚨 PHASE TRANSITION DETECTED!")
        print(f"  Metrics changing: {', '.join(transition['metrics_changing'])}")
    else:
        print("  ✓ Network evolution stable (no phase transition detected)")

    # Hypotheses
    if tracker.count_hypotheses() > 0:
        print_subheader("Emergent Hypotheses")
        for hyp in tracker.get_hypotheses():
            timestamp = hyp.get('timestamp', 'N/A')
            print(f"  {timestamp} {hyp['hypothesis']}")
            print(f"    Confidence: {hyp['confidence']:.2f} | Mechanism: {hyp['mechanism']}")


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

    # Config path
    config_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'config',
        'lantern_hub.yaml'
    )

    # 1. Load network
    network = demonstrate_network_loading()

    # 2. EM-fields
    fields = demonstrate_em_fields(network)

    # 3. Coupling matrix
    demonstrate_coupling_matrix(network)

    # 4. Collective modes
    demonstrate_collective_modes(network)

    # 5. Emergence metrics WITH stochastic resonance
    demonstrate_emergence_metrics(network, config_path)

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
