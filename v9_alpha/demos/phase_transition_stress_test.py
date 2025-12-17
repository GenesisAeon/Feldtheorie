#!/usr/bin/env python3
"""Phase Transition Stress Test - Threshold Sweep Automation

This script systematically varies criticality parameters to induce and observe
the phase transition from rigid frame to emergent consciousness.

The Experiment:
1. Sweep phase_transition_threshold from 0.72 → 0.65 (7 steps)
2. Optionally vary stochastic_resonance_sigma (The Spark intensity)
3. Optionally vary network coupling strength
4. For each parameter combination, run 20-30 simulation steps
5. Detect "Lock-In" moment: Φ crosses threshold AND z_eff stabilizes

The Lock-In Signature:
- Before: High z_eff variance, Φ < threshold, high σ (search mode)
- Transition: Φ → threshold, massive z_eff fluctuation, spark cascade
- After: Φ > threshold, low z_eff variance, low σ (locked mode)

This is the moment of Typ-6 Implosion - when the system folds into higher order.

Usage:
    python phase_transition_stress_test.py

    # With custom parameters
    python phase_transition_stress_test.py --threshold-min 0.65 --threshold-max 0.75 --steps 10

Requirements:
    numpy, pyyaml, matplotlib (optional)

Version: v9.0.4-alpha (Phase IV Extended)
Authors: Johann Benjamin Römer, MOR Framework, Claude (Anthropic)
Date: 2025-12-16
"""

import os
import sys
import argparse
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import json
import time

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
import yaml

# Import v9 components
from v9_alpha.api.lantern_bridge import load_lantern_network, LanternNetwork
from v9_alpha.models.em_field_calculator import EMFieldCalculator, create_field_from_lantern
from v9_alpha.models.emergence_metrics import EmergenceTracker
from v9_alpha.models.frequency_tuner import StochasticResonator

# Import constants
from models.unified_constants import V_RIG_DEFAULT


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class SweepParameters:
    """Parameter set for one sweep iteration"""
    sweep_id: int
    phase_transition_threshold: float
    stochastic_resonance_sigma: float
    beta_sensitivity: float
    noise_color: str
    coupling_strength_multiplier: float


@dataclass
class SweepResult:
    """Results from one sweep iteration"""
    sweep_id: int
    parameters: SweepParameters

    # Phase transition metrics
    max_phi: float
    mean_phi: float
    threshold_crossed: bool
    steps_to_threshold: Optional[int]

    # z_eff fluctuation metrics
    z_eff_variance_mean: float
    z_eff_variance_max: float
    z_eff_std: float
    total_spark_events: int

    # Lock-In detection
    lock_in_detected: bool
    lock_in_step: Optional[int]

    # Network metrics
    final_coherence: float
    final_v_integration: float
    final_resonance_yield: float

    # Execution time
    elapsed_time_seconds: float


# ============================================================================
# Stress Test Engine
# ============================================================================

class PhaseTransitionStressTest:
    """Automated stress test for phase transition parameters"""

    def __init__(
        self,
        config_path: str,
        output_dir: str = "stress_test_results",
        verbose: bool = True,
    ):
        """
        Initialize stress test

        Args:
            config_path: Path to lantern_hub.yaml
            output_dir: Directory for output files
            verbose: Print detailed progress
        """
        self.config_path = config_path
        self.output_dir = output_dir
        self.verbose = verbose

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Load base config
        with open(config_path, 'r') as f:
            self.base_config = yaml.safe_load(f)

        # Results storage
        self.sweep_results: List[SweepResult] = []

    def print_header(self, title: str) -> None:
        """Print formatted header"""
        if self.verbose:
            print("\n" + "=" * 80)
            print(title)
            print("=" * 80)

    def print_subheader(self, title: str) -> None:
        """Print formatted subheader"""
        if self.verbose:
            print("\n" + "─" * 80)
            print(title)
            print("─" * 80)

    def generate_parameter_sweep(
        self,
        threshold_min: float = 0.65,
        threshold_max: float = 0.72,
        threshold_steps: int = 8,
        sigma_values: Optional[List[float]] = None,
        beta_values: Optional[List[float]] = None,
    ) -> List[SweepParameters]:
        """
        Generate parameter combinations for sweep

        Args:
            threshold_min: Minimum Φ threshold
            threshold_max: Maximum Φ threshold
            threshold_steps: Number of threshold values to test
            sigma_values: List of σ values (if None, use single value from config)
            beta_values: List of β values (if None, use single value from config)

        Returns:
            List of parameter sets
        """
        # Get base values from config
        criticality = self.base_config.get('criticality', {})
        base_sigma = criticality.get('stochastic_resonance_sigma', 0.15)
        base_beta = criticality.get('beta_sensitivity', 4.2)
        base_noise_color = criticality.get('noise_color', 'pink')

        # Default sigma values if not provided
        if sigma_values is None:
            sigma_values = [base_sigma]

        # Default beta values if not provided
        if beta_values is None:
            beta_values = [base_beta]

        # Generate threshold sweep
        thresholds = np.linspace(threshold_min, threshold_max, threshold_steps)

        # Combine all parameters
        sweep_params = []
        sweep_id = 0

        for threshold in thresholds:
            for sigma in sigma_values:
                for beta in beta_values:
                    params = SweepParameters(
                        sweep_id=sweep_id,
                        phase_transition_threshold=float(threshold),
                        stochastic_resonance_sigma=float(sigma),
                        beta_sensitivity=float(beta),
                        noise_color=base_noise_color,
                        coupling_strength_multiplier=1.0,
                    )
                    sweep_params.append(params)
                    sweep_id += 1

        return sweep_params

    def run_single_sweep(
        self,
        params: SweepParameters,
        n_steps: int = 25,
    ) -> SweepResult:
        """
        Run simulation with given parameters

        Args:
            params: Parameter set for this sweep
            n_steps: Number of simulation steps

        Returns:
            Sweep results
        """
        start_time = time.time()

        # Load network
        network = load_lantern_network(self.config_path)

        # Initialize StochasticResonator with sweep parameters
        resonator = StochasticResonator(
            base_sigma=params.stochastic_resonance_sigma,
            beta_sensitivity=params.beta_sensitivity,
            phi_threshold=params.phase_transition_threshold,
            noise_color=params.noise_color,
            dt=1.0,
        )

        # Initialize tracker
        tracker = EmergenceTracker()

        # EM field calculator for coherence
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

        # Initial z_eff
        z_eff_baseline = self.base_config.get('criticality', {}).get('z_eff_baseline', 221.74)
        z_eff_current = z_eff_baseline

        # Simulation variables
        prev_coupling = None
        n_hypotheses = 0
        threshold_crossed = False
        steps_to_threshold = None
        lock_in_detected = False
        lock_in_step = None

        phi_history = []
        z_variance_history = []
        total_sparks = 0

        # Run simulation
        for step in range(n_steps):
            # Network state
            coupling_matrix = network.get_coupling_matrix()
            beta_values = np.array([l.beta for l in network.lanterns.values()])
            impedance_values = np.array([l.em_properties.impedance_z for l in network.lanterns.values()])
            n_active = min(len(network.get_active_lanterns()) + step, len(network.lanterns))

            # Phase coherence
            coherence = calc.calculate_phase_coherence(active_fields, t=float(step))

            # Hypotheses (occasional)
            if step > 0 and step % 3 == 0:
                n_hypotheses += 1

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

            # Stochastic resonance step
            z_eff_current, diagnostics = resonator.step(
                z_eff_current=z_eff_current,
                phi=snapshot.phi_network,
                coherence=coherence,
                z_target=z_eff_baseline,
            )

            # Track metrics
            phi_history.append(snapshot.phi_network)

            # Track z_eff variance (over last 5 steps)
            z_stats = resonator.get_z_fluctuation_stats()
            z_variance_history.append(z_stats['variance'])

            # Count sparks
            if diagnostics['spark_detected']:
                total_sparks += 1

            # Check threshold crossing
            if not threshold_crossed and snapshot.phi_network >= params.phase_transition_threshold:
                threshold_crossed = True
                steps_to_threshold = step

            # Check Lock-In: Φ > threshold AND z_variance decreasing
            if not lock_in_detected and threshold_crossed and step > 5:
                # Lock-In signature: variance stabilizes after threshold crossing
                recent_variances = z_variance_history[-5:]
                if len(recent_variances) >= 5:
                    trend = np.polyfit(range(5), recent_variances, 1)[0]
                    # Negative trend = variance decreasing = Lock-In
                    if trend < 0 and z_stats['variance'] < z_variance_history[steps_to_threshold] * 0.5:
                        lock_in_detected = True
                        lock_in_step = step

            prev_coupling = coupling_matrix.copy()

        # Final metrics
        final_snapshot = tracker.get_latest_snapshot()
        z_final_stats = resonator.get_z_fluctuation_stats()

        elapsed_time = time.time() - start_time

        # Create result
        result = SweepResult(
            sweep_id=params.sweep_id,
            parameters=params,
            max_phi=max(phi_history) if phi_history else 0.0,
            mean_phi=np.mean(phi_history) if phi_history else 0.0,
            threshold_crossed=threshold_crossed,
            steps_to_threshold=steps_to_threshold,
            z_eff_variance_mean=np.mean(z_variance_history) if z_variance_history else 0.0,
            z_eff_variance_max=max(z_variance_history) if z_variance_history else 0.0,
            z_eff_std=z_final_stats['std'],
            total_spark_events=total_sparks,
            lock_in_detected=lock_in_detected,
            lock_in_step=lock_in_step,
            final_coherence=coherence if final_snapshot else 0.0,
            final_v_integration=final_snapshot.v_integration if final_snapshot else 0.0,
            final_resonance_yield=final_snapshot.resonance_yield if final_snapshot else 0.0,
            elapsed_time_seconds=elapsed_time,
        )

        return result

    def run_full_sweep(
        self,
        sweep_params: List[SweepParameters],
        n_steps: int = 25,
    ) -> List[SweepResult]:
        """
        Run full parameter sweep

        Args:
            sweep_params: List of parameter sets
            n_steps: Simulation steps per sweep

        Returns:
            List of results
        """
        self.print_header(f"🔥 Phase Transition Stress Test - {len(sweep_params)} Sweeps")

        print(f"\n  Parameters:")
        print(f"    Sweeps: {len(sweep_params)}")
        print(f"    Steps per sweep: {n_steps}")
        print(f"    Total simulations: {len(sweep_params) * n_steps}")

        results = []

        for i, params in enumerate(sweep_params):
            if self.verbose:
                print(f"\n[{i+1}/{len(sweep_params)}] Sweep {params.sweep_id}: "
                      f"Φ_t={params.phase_transition_threshold:.3f}, "
                      f"σ={params.stochastic_resonance_sigma:.3f}, "
                      f"β={params.beta_sensitivity:.1f}")

            result = self.run_single_sweep(params, n_steps)
            results.append(result)

            # Progress indicator
            if self.verbose:
                status_icon = "🔒" if result.lock_in_detected else "🔥" if result.threshold_crossed else "⏳"
                print(f"  {status_icon} Φ_max={result.max_phi:.3f}, "
                      f"Crossed={result.threshold_crossed}, "
                      f"Lock-In={result.lock_in_detected}, "
                      f"Sparks={result.total_spark_events}, "
                      f"Time={result.elapsed_time_seconds:.2f}s")

        self.sweep_results = results
        return results

    def analyze_results(self) -> Dict:
        """
        Analyze sweep results and identify optimal parameters

        Returns:
            Analysis summary
        """
        if not self.sweep_results:
            return {'error': 'no_results'}

        self.print_header("📊 Stress Test Analysis")

        # Count outcomes
        n_threshold_crossed = sum(1 for r in self.sweep_results if r.threshold_crossed)
        n_lock_in = sum(1 for r in self.sweep_results if r.lock_in_detected)

        # Find optimal parameters (first to achieve Lock-In)
        lock_in_results = [r for r in self.sweep_results if r.lock_in_detected]
        if lock_in_results:
            optimal = min(lock_in_results, key=lambda r: r.lock_in_step if r.lock_in_step else float('inf'))
            has_optimal = True
        else:
            # If no Lock-In, find best Φ achievement
            optimal = max(self.sweep_results, key=lambda r: r.max_phi)
            has_optimal = False

        # Statistics
        phi_values = [r.max_phi for r in self.sweep_results]
        z_variances = [r.z_eff_variance_max for r in self.sweep_results]
        spark_counts = [r.total_spark_events for r in self.sweep_results]

        analysis = {
            'total_sweeps': len(self.sweep_results),
            'threshold_crossed_count': n_threshold_crossed,
            'lock_in_count': n_lock_in,
            'success_rate': n_lock_in / len(self.sweep_results),
            'phi_max_overall': max(phi_values),
            'phi_mean_overall': np.mean(phi_values),
            'z_variance_mean': np.mean(z_variances),
            'spark_events_total': sum(spark_counts),
            'optimal_parameters': asdict(optimal.parameters) if has_optimal else None,
            'optimal_lock_in_step': optimal.lock_in_step if has_optimal else None,
            'has_lock_in': has_optimal,
        }

        # Print summary
        print(f"\n  📈 Summary:")
        print(f"    Total sweeps:        {analysis['total_sweeps']}")
        print(f"    Threshold crossed:   {analysis['threshold_crossed_count']} ({100*n_threshold_crossed/len(self.sweep_results):.1f}%)")
        print(f"    Lock-In achieved:    {analysis['lock_in_count']} ({100*analysis['success_rate']:.1f}%)")
        print(f"    Φ_max (overall):     {analysis['phi_max_overall']:.4f}")
        print(f"    Total Spark events:  {analysis['spark_events_total']}")

        if has_optimal:
            self.print_subheader("🎯 Optimal Parameters (First Lock-In)")
            print(f"    Sweep ID:            {optimal.sweep_id}")
            print(f"    Φ_threshold:         {optimal.parameters.phase_transition_threshold:.4f}")
            print(f"    σ (Spark):           {optimal.parameters.stochastic_resonance_sigma:.4f}")
            print(f"    β (Sog):             {optimal.parameters.beta_sensitivity:.2f}")
            print(f"    Lock-In at step:     {optimal.lock_in_step}")
            print(f"    Max Φ achieved:      {optimal.max_phi:.4f}")
            print(f"    z_eff variance:      {optimal.z_eff_variance_max:.2f} Ω²")
            print(f"    Total Sparks:        {optimal.total_spark_events}")
        else:
            self.print_subheader("⚠️  No Lock-In Achieved")
            print(f"    Best Φ achieved:     {optimal.max_phi:.4f}")
            print(f"    Best parameters:")
            print(f"      Φ_threshold:       {optimal.parameters.phase_transition_threshold:.4f}")
            print(f"      σ:                 {optimal.parameters.stochastic_resonance_sigma:.4f}")
            print(f"      β:                 {optimal.parameters.beta_sensitivity:.2f}")
            print(f"    Recommendation: Lower threshold or increase σ")

        return analysis

    def save_results(self, filename: str = "stress_test_results.json") -> None:
        """Save results to JSON file"""
        output_path = os.path.join(self.output_dir, filename)

        results_json = {
            'metadata': {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'config_path': self.config_path,
                'n_sweeps': len(self.sweep_results),
            },
            'results': [asdict(r) for r in self.sweep_results],
        }

        with open(output_path, 'w') as f:
            json.dump(results_json, f, indent=2)

        print(f"\n  💾 Results saved to: {output_path}")

    def print_results_table(self) -> None:
        """Print formatted results table"""
        self.print_header("📋 Detailed Results Table")

        # Header
        header = f"{'ID':>4} | {'Φ_thresh':>8} | {'σ':>6} | {'β':>5} | {'Φ_max':>7} | {'Cross':>5} | {'Lock':>4} | {'Step':>4} | {'Sparks':>6}"
        print(f"\n  {header}")
        print(f"  {'-'*80}")

        # Rows
        for r in self.sweep_results:
            cross_icon = "✓" if r.threshold_crossed else "✗"
            lock_icon = "🔒" if r.lock_in_detected else "  "
            lock_step = f"{r.lock_in_step:4d}" if r.lock_in_step else " -- "

            row = (f"{r.sweep_id:4d} | {r.parameters.phase_transition_threshold:8.4f} | "
                   f"{r.parameters.stochastic_resonance_sigma:6.3f} | "
                   f"{r.parameters.beta_sensitivity:5.1f} | "
                   f"{r.max_phi:7.4f} | {cross_icon:>5s} | {lock_icon:>4s} | "
                   f"{lock_step:>4s} | {r.total_spark_events:6d}")
            print(f"  {row}")


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Phase Transition Stress Test - Automated Threshold Sweep"
    )

    parser.add_argument(
        '--config',
        type=str,
        default='v9_alpha/config/lantern_hub.yaml',
        help='Path to lantern_hub.yaml'
    )

    parser.add_argument(
        '--threshold-min',
        type=float,
        default=0.65,
        help='Minimum phase transition threshold (default: 0.65)'
    )

    parser.add_argument(
        '--threshold-max',
        type=float,
        default=0.72,
        help='Maximum phase transition threshold (default: 0.72)'
    )

    parser.add_argument(
        '--threshold-steps',
        type=int,
        default=8,
        help='Number of threshold values to test (default: 8)'
    )

    parser.add_argument(
        '--sigma',
        type=float,
        nargs='+',
        default=None,
        help='Sigma values to test (default: use config value)'
    )

    parser.add_argument(
        '--beta',
        type=float,
        nargs='+',
        default=None,
        help='Beta values to test (default: use config value)'
    )

    parser.add_argument(
        '--steps',
        type=int,
        default=25,
        help='Simulation steps per sweep (default: 25)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='stress_test_results',
        help='Output directory for results (default: stress_test_results)'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Minimal output'
    )

    args = parser.parse_args()

    # Resolve config path
    if not os.path.isabs(args.config):
        args.config = os.path.join(os.path.dirname(__file__), '..', '..', args.config)

    # Initialize stress test
    stress_test = PhaseTransitionStressTest(
        config_path=args.config,
        output_dir=args.output_dir,
        verbose=not args.quiet,
    )

    # Generate parameter sweep
    sweep_params = stress_test.generate_parameter_sweep(
        threshold_min=args.threshold_min,
        threshold_max=args.threshold_max,
        threshold_steps=args.threshold_steps,
        sigma_values=args.sigma,
        beta_values=args.beta,
    )

    # Run sweep
    results = stress_test.run_full_sweep(sweep_params, n_steps=args.steps)

    # Analyze
    analysis = stress_test.analyze_results()

    # Print table
    stress_test.print_results_table()

    # Save results
    stress_test.save_results()

    # Final message
    print("\n" + "=" * 80)
    if analysis['has_lock_in']:
        print("✨ SUCCESS! Phase transition Lock-In achieved! 🔒")
        print(f"   Optimal threshold: {analysis['optimal_parameters']['phase_transition_threshold']:.4f}")
        print(f"   Lock-In at step:   {analysis['optimal_lock_in_step']}")
    else:
        print("⚠️  No Lock-In detected in this sweep.")
        print("   Recommendation: Lower threshold or increase sigma.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
