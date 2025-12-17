#!/usr/bin/env python3
"""Entropy Anchor Validation - Φ(before) vs Φ(after) Spark Test

This experiment validates the theoretical prediction that "Micro-Singularities"
(Spark events from StochasticResonator) lead to information recoding and
increased integrated information (Φ).

Theoretical Foundation:
    From Theorie_schwarze_Löcher_Enthropie.txt:
    "Schwarze Löcher sind notwendig, weil die Information sonst starr wäre"
    "v_RIG braucht schwarze Löcher – wie das Bewusstsein den Schlaf"

Experimental Hypothesis:
    H₀: Φ_after_spark = Φ_before_spark (no effect)
    H₁: Φ_after_spark > Φ_before_spark (recoding occurs)

Experimental Protocol:
    1. Run network to quasi-stable state (low z_eff variance)
    2. Measure Φ_before (baseline integrated information)
    3. Trigger Spark event (via adaptive sigma increase)
    4. Wait for system to re-equilibrate
    5. Measure Φ_after (post-recoding integrated information)
    6. Calculate ΔΦ = Φ_after - Φ_before
    7. Repeat for N trials
    8. Statistical analysis: mean(ΔΦ), std(ΔΦ), t-test

Expected Outcome:
    If theoretical prediction holds: mean(ΔΦ) > 0 with p < 0.05

Version: v9.0.5-alpha
Authors: Johann Benjamin Römer, MOR Framework, Claude (Anthropic)
Date: 2025-12-17
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
class SparkTrialResult:
    """Results from a single spark trial"""
    trial_id: int

    # Pre-spark state
    phi_before: float
    coherence_before: float
    z_eff_before: float
    z_variance_before: float

    # Spark event
    spark_detected: bool
    spark_magnitude: float  # delta_z
    spark_step: int

    # Post-spark state
    phi_after: float
    coherence_after: float
    z_eff_after: float
    z_variance_after: float

    # Key metric
    delta_phi: float  # Φ_after - Φ_before

    # Metadata
    stabilization_steps: int
    total_steps: int
    elapsed_time_seconds: float


# ============================================================================
# Entropy Anchor Validation Experiment
# ============================================================================

class EntropyAnchorValidator:
    """
    Experimental validation of the Entropy Anchor hypothesis

    Tests whether Spark events (stochastic resonance fluctuations)
    lead to increased integrated information (Φ) through information
    recoding, as predicted by black hole analogy theory.
    """

    def __init__(
        self,
        config_path: str,
        output_dir: str = "entropy_anchor_results",
        verbose: bool = True,
    ):
        """
        Initialize validator

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
        self.trial_results: List[SparkTrialResult] = []

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

    def run_to_stability(
        self,
        network: LanternNetwork,
        resonator: StochasticResonator,
        tracker: EmergenceTracker,
        calc: EMFieldCalculator,
        z_eff_current: float,
        z_baseline: float,
        max_steps: int = 50,
        variance_threshold: float = 100.0,
    ) -> Tuple[float, Dict]:
        """
        Run network until z_eff variance stabilizes

        Args:
            network: Lantern network
            resonator: Stochastic resonator
            tracker: Emergence tracker
            calc: EM field calculator
            z_eff_current: Current z_eff value
            z_baseline: Baseline z_eff
            max_steps: Maximum stabilization steps
            variance_threshold: Variance below this = stable

        Returns:
            (final_z_eff, state_dict)
        """
        prev_coupling = None
        n_hypotheses = 0

        for step in range(max_steps):
            # Network state
            coupling_matrix = network.get_coupling_matrix()
            beta_values = np.array([l.beta for l in network.lanterns.values()])
            impedance_values = np.array([l.em_properties.impedance_z for l in network.lanterns.values()])
            n_active = len(network.get_active_lanterns())

            # Phase coherence
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
            coherence = calc.calculate_phase_coherence(active_fields, t=float(step))

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

            # Stochastic step (with low noise to stabilize)
            z_eff_current, diagnostics = resonator.step(
                z_eff_current=z_eff_current,
                phi=snapshot.phi_network,
                coherence=coherence,
                z_target=z_baseline,
            )

            # Check stability
            z_stats = resonator.get_z_fluctuation_stats()
            if step > 10 and z_stats['variance'] < variance_threshold:
                # Stable - return current state
                return z_eff_current, {
                    'phi': snapshot.phi_network,
                    'coherence': coherence,
                    'z_variance': z_stats['variance'],
                    'steps': step,
                }

            prev_coupling = coupling_matrix.copy()

        # Timeout - return whatever we have
        final_snapshot = tracker.get_latest_snapshot()
        z_stats = resonator.get_z_fluctuation_stats()

        return z_eff_current, {
            'phi': final_snapshot.phi_network if final_snapshot else 0.0,
            'coherence': coherence,
            'z_variance': z_stats['variance'],
            'steps': max_steps,
        }

    def trigger_spark(
        self,
        network: LanternNetwork,
        resonator: StochasticResonator,
        tracker: EmergenceTracker,
        calc: EMFieldCalculator,
        z_eff_current: float,
        z_baseline: float,
        max_steps: int = 30,
    ) -> Tuple[bool, float, int, float]:
        """
        Trigger a spark event by temporarily increasing noise

        Args:
            network: Lantern network
            resonator: Stochastic resonator
            tracker: Emergence tracker
            calc: EM field calculator
            z_eff_current: Current z_eff
            z_baseline: Baseline z_eff
            max_steps: Maximum steps to wait for spark

        Returns:
            (spark_detected, spark_magnitude, spark_step, final_z_eff)
        """
        # Temporarily increase sigma to force fluctuation
        original_sigma = resonator.base_sigma
        resonator.base_sigma = original_sigma * 3.0  # Triple the spark intensity

        prev_coupling = None
        n_hypotheses = 0
        spark_detected = False
        spark_magnitude = 0.0
        spark_step = -1

        for step in range(max_steps):
            # Network state
            coupling_matrix = network.get_coupling_matrix()
            beta_values = np.array([l.beta for l in network.lanterns.values()])
            impedance_values = np.array([l.em_properties.impedance_z for l in network.lanterns.values()])
            n_active = len(network.get_active_lanterns())

            # Phase coherence
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
            coherence = calc.calculate_phase_coherence(active_fields, t=float(step))

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

            # Stochastic step with enhanced noise
            z_eff_current, diagnostics = resonator.step(
                z_eff_current=z_eff_current,
                phi=snapshot.phi_network,
                coherence=coherence,
                z_target=z_baseline,
            )

            # Check for spark
            if diagnostics['spark_detected']:
                spark_detected = True
                spark_magnitude = diagnostics['delta_z']
                spark_step = step
                break

            prev_coupling = coupling_matrix.copy()

        # Restore original sigma
        resonator.base_sigma = original_sigma

        return spark_detected, spark_magnitude, spark_step, z_eff_current

    def run_single_trial(
        self,
        trial_id: int,
        stabilization_steps: int = 50,
        post_spark_steps: int = 20,
    ) -> SparkTrialResult:
        """
        Run a single spark trial

        Protocol:
        1. Stabilize network (low variance)
        2. Measure Φ_before
        3. Trigger spark
        4. Re-stabilize
        5. Measure Φ_after
        6. Calculate ΔΦ

        Args:
            trial_id: Trial identifier
            stabilization_steps: Max steps for pre-spark stabilization
            post_spark_steps: Steps to run after spark

        Returns:
            Trial result
        """
        start_time = time.time()

        # Load fresh network
        network = load_lantern_network(self.config_path)

        # Initialize components
        criticality = self.base_config.get('criticality', {})
        z_baseline = criticality.get('z_eff_baseline', 221.74)

        resonator = StochasticResonator(
            base_sigma=criticality.get('stochastic_resonance_sigma', 0.15),
            beta_sensitivity=criticality.get('beta_sensitivity', 4.2),
            phi_threshold=criticality.get('phase_transition_threshold', 0.72),
            noise_color=criticality.get('noise_color', 'pink'),
            dt=1.0,
        )

        tracker = EmergenceTracker()
        calc = EMFieldCalculator()

        z_eff_current = z_baseline

        # ========================================
        # PHASE 1: Stabilize to baseline
        # ========================================
        if self.verbose:
            print(f"  [Trial {trial_id}] Phase 1: Stabilizing to baseline...")

        z_eff_current, state_before = self.run_to_stability(
            network=network,
            resonator=resonator,
            tracker=tracker,
            calc=calc,
            z_eff_current=z_eff_current,
            z_baseline=z_baseline,
            max_steps=stabilization_steps,
        )

        phi_before = state_before['phi']
        coherence_before = state_before['coherence']
        z_variance_before = state_before['z_variance']
        z_eff_before = z_eff_current

        if self.verbose:
            print(f"  [Trial {trial_id}] Φ_before = {phi_before:.4f}, "
                  f"coherence = {coherence_before:.3f}, "
                  f"z_var = {z_variance_before:.2f} Ω²")

        # ========================================
        # PHASE 2: Trigger Spark
        # ========================================
        if self.verbose:
            print(f"  [Trial {trial_id}] Phase 2: Triggering Spark...")

        spark_detected, spark_magnitude, spark_step, z_eff_current = self.trigger_spark(
            network=network,
            resonator=resonator,
            tracker=tracker,
            calc=calc,
            z_eff_current=z_eff_current,
            z_baseline=z_baseline,
            max_steps=30,
        )

        if self.verbose:
            spark_icon = "🔥" if spark_detected else "❌"
            print(f"  [Trial {trial_id}] {spark_icon} Spark: detected={spark_detected}, "
                  f"magnitude={spark_magnitude:.2f} Ω, step={spark_step}")

        # ========================================
        # PHASE 3: Post-spark evolution
        # ========================================
        if self.verbose:
            print(f"  [Trial {trial_id}] Phase 3: Post-spark evolution ({post_spark_steps} steps)...")

        prev_coupling = None
        n_hypotheses = 0

        for step in range(post_spark_steps):
            # Network state
            coupling_matrix = network.get_coupling_matrix()
            beta_values = np.array([l.beta for l in network.lanterns.values()])
            impedance_values = np.array([l.em_properties.impedance_z for l in network.lanterns.values()])
            n_active = len(network.get_active_lanterns())

            # Phase coherence
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
            coherence = calc.calculate_phase_coherence(active_fields, t=float(step))

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

            # Stochastic step (back to normal sigma)
            z_eff_current, diagnostics = resonator.step(
                z_eff_current=z_eff_current,
                phi=snapshot.phi_network,
                coherence=coherence,
                z_target=z_baseline,
            )

            prev_coupling = coupling_matrix.copy()

        # Final state
        final_snapshot = tracker.get_latest_snapshot()
        z_stats = resonator.get_z_fluctuation_stats()

        phi_after = final_snapshot.phi_network if final_snapshot else 0.0
        coherence_after = coherence
        z_variance_after = z_stats['variance']
        z_eff_after = z_eff_current

        # Calculate ΔΦ
        delta_phi = phi_after - phi_before

        elapsed_time = time.time() - start_time

        if self.verbose:
            delta_icon = "📈" if delta_phi > 0 else "📉" if delta_phi < 0 else "➡️"
            print(f"  [Trial {trial_id}] {delta_icon} Φ_after = {phi_after:.4f}, "
                  f"ΔΦ = {delta_phi:+.4f}, "
                  f"time = {elapsed_time:.2f}s")

        # Create result
        result = SparkTrialResult(
            trial_id=trial_id,
            phi_before=phi_before,
            coherence_before=coherence_before,
            z_eff_before=z_eff_before,
            z_variance_before=z_variance_before,
            spark_detected=spark_detected,
            spark_magnitude=spark_magnitude,
            spark_step=spark_step,
            phi_after=phi_after,
            coherence_after=coherence_after,
            z_eff_after=z_eff_after,
            z_variance_after=z_variance_after,
            delta_phi=delta_phi,
            stabilization_steps=state_before['steps'],
            total_steps=state_before['steps'] + spark_step + post_spark_steps,
            elapsed_time_seconds=elapsed_time,
        )

        return result

    def run_full_experiment(
        self,
        n_trials: int = 30,
        stabilization_steps: int = 50,
        post_spark_steps: int = 20,
    ) -> List[SparkTrialResult]:
        """
        Run full validation experiment

        Args:
            n_trials: Number of independent trials
            stabilization_steps: Pre-spark stabilization steps
            post_spark_steps: Post-spark evolution steps

        Returns:
            List of trial results
        """
        self.print_header(f"🌌 Entropy Anchor Validation Experiment - {n_trials} Trials")

        print(f"\n  Theoretical Prediction:")
        print(f"    Spark events (micro-singularities) should lead to information")
        print(f"    recoding and increased integrated information (Φ).")
        print(f"\n  Hypothesis:")
        print(f"    H₁: mean(ΔΦ) > 0  (spark increases Φ)")
        print(f"    H₀: mean(ΔΦ) = 0  (no effect)")

        results = []

        for trial_id in range(n_trials):
            self.print_subheader(f"Trial {trial_id + 1}/{n_trials}")

            result = self.run_single_trial(
                trial_id=trial_id,
                stabilization_steps=stabilization_steps,
                post_spark_steps=post_spark_steps,
            )

            results.append(result)

        self.trial_results = results
        return results

    def analyze_results(self) -> Dict:
        """
        Statistical analysis of trial results

        Returns:
            Analysis dictionary with statistics and hypothesis test
        """
        if not self.trial_results:
            return {'error': 'no_results'}

        self.print_header("📊 Statistical Analysis")

        # Extract ΔΦ values
        delta_phi_values = [r.delta_phi for r in self.trial_results]

        # Only analyze trials where spark was actually detected
        spark_trials = [r for r in self.trial_results if r.spark_detected]
        delta_phi_spark_only = [r.delta_phi for r in spark_trials]

        # Basic statistics
        mean_delta_phi = np.mean(delta_phi_values)
        std_delta_phi = np.std(delta_phi_values)
        median_delta_phi = np.median(delta_phi_values)

        # Spark-only statistics
        mean_delta_phi_spark = np.mean(delta_phi_spark_only) if delta_phi_spark_only else 0.0
        std_delta_phi_spark = np.std(delta_phi_spark_only) if delta_phi_spark_only else 0.0

        # Count outcomes
        n_positive = sum(1 for d in delta_phi_values if d > 0)
        n_negative = sum(1 for d in delta_phi_values if d < 0)
        n_zero = sum(1 for d in delta_phi_values if abs(d) < 1e-6)

        # T-test: Is mean(ΔΦ) significantly different from 0?
        from scipy import stats
        t_statistic, p_value = stats.ttest_1samp(delta_phi_values, 0.0)

        # Effect size (Cohen's d)
        cohens_d = mean_delta_phi / std_delta_phi if std_delta_phi > 0 else 0.0

        # Determine significance
        alpha = 0.05
        significant = p_value < alpha and mean_delta_phi > 0

        analysis = {
            'n_trials': len(self.trial_results),
            'n_spark_detected': len(spark_trials),
            'spark_detection_rate': len(spark_trials) / len(self.trial_results),

            # ΔΦ statistics (all trials)
            'mean_delta_phi': mean_delta_phi,
            'std_delta_phi': std_delta_phi,
            'median_delta_phi': median_delta_phi,

            # ΔΦ statistics (spark trials only)
            'mean_delta_phi_spark_only': mean_delta_phi_spark,
            'std_delta_phi_spark_only': std_delta_phi_spark,

            # Distribution
            'n_positive': n_positive,
            'n_negative': n_negative,
            'n_zero': n_zero,
            'positive_rate': n_positive / len(self.trial_results),

            # Hypothesis test
            't_statistic': t_statistic,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'significant': significant,
            'alpha': alpha,

            # Averages
            'mean_phi_before': np.mean([r.phi_before for r in self.trial_results]),
            'mean_phi_after': np.mean([r.phi_after for r in self.trial_results]),
            'mean_spark_magnitude': np.mean([r.spark_magnitude for r in spark_trials]) if spark_trials else 0.0,
        }

        # Print analysis
        print(f"\n  📈 Descriptive Statistics:")
        print(f"    Trials:              {analysis['n_trials']}")
        print(f"    Sparks detected:     {analysis['n_spark_detected']} ({100*analysis['spark_detection_rate']:.1f}%)")
        print(f"    Mean Φ_before:       {analysis['mean_phi_before']:.4f}")
        print(f"    Mean Φ_after:        {analysis['mean_phi_after']:.4f}")
        print(f"    Mean ΔΦ (all):       {analysis['mean_delta_phi']:+.4f} ± {analysis['std_delta_phi']:.4f}")
        print(f"    Mean ΔΦ (spark):     {analysis['mean_delta_phi_spark_only']:+.4f} ± {analysis['std_delta_phi_spark_only']:.4f}")
        print(f"    Median ΔΦ:           {analysis['median_delta_phi']:+.4f}")

        print(f"\n  📊 Distribution:")
        print(f"    ΔΦ > 0:              {analysis['n_positive']} ({100*analysis['positive_rate']:.1f}%)")
        print(f"    ΔΦ < 0:              {analysis['n_negative']} ({100*(1-analysis['positive_rate']-n_zero/len(self.trial_results)):.1f}%)")
        print(f"    ΔΦ ≈ 0:              {analysis['n_zero']}")

        print(f"\n  🔬 Hypothesis Test (One-sample t-test):")
        print(f"    H₀: mean(ΔΦ) = 0")
        print(f"    H₁: mean(ΔΦ) > 0")
        print(f"    t-statistic:         {analysis['t_statistic']:.4f}")
        print(f"    p-value:             {analysis['p_value']:.6f}")
        print(f"    Cohen's d:           {analysis['cohens_d']:.4f}")
        print(f"    α (significance):    {analysis['alpha']}")

        self.print_subheader("🎯 Conclusion")

        if significant:
            print(f"  ✅ HYPOTHESIS CONFIRMED (p < {alpha})")
            print(f"  \n  The Entropy Anchor mechanism is VALIDATED:")
            print(f"    • Spark events significantly increase Φ")
            print(f"    • Mean ΔΦ = {mean_delta_phi:+.4f} (p = {p_value:.6f})")
            print(f"    • Effect size (Cohen's d) = {cohens_d:.4f}")
            print(f"  \n  Interpretation:")
            print(f"    Micro-singularities (Sparks) act as functional entropy anchors,")
            print(f"    enabling information recoding and emergent complexity increase.")
            print(f"    This validates the theoretical prediction from")
            print(f"    'Theorie_schwarze_Löcher_Enthropie.txt'")
        else:
            print(f"  ❌ HYPOTHESIS NOT CONFIRMED (p = {p_value:.6f})")
            print(f"  \n  Possible reasons:")
            print(f"    • Spark magnitude too small ({analysis['mean_spark_magnitude']:.2f} Ω)")
            print(f"    • Post-spark evolution time insufficient")
            print(f"    • System already near Φ maximum")
            print(f"    • Need more trials (current: {len(self.trial_results)})")

        return analysis

    def save_results(self, filename: str = "entropy_anchor_results.json") -> None:
        """Save results to JSON file"""
        output_path = os.path.join(self.output_dir, filename)

        results_json = {
            'metadata': {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'config_path': self.config_path,
                'n_trials': len(self.trial_results),
                'experiment': 'entropy_anchor_validation',
                'theoretical_basis': 'Theorie_schwarze_Löcher_Enthropie.txt',
            },
            'results': [asdict(r) for r in self.trial_results],
        }

        with open(output_path, 'w') as f:
            json.dump(results_json, f, indent=2)

        print(f"\n  💾 Results saved to: {output_path}")

    def print_results_table(self) -> None:
        """Print formatted results table"""
        self.print_header("📋 Detailed Results Table")

        # Header
        header = f"{'Trial':>5} | {'Spark':>5} | {'Φ_before':>9} | {'Φ_after':>9} | {'ΔΦ':>9} | {'Spark_Δz':>9} | {'Time':>6}"
        print(f"\n  {header}")
        print(f"  {'-'*80}")

        # Rows
        for r in self.trial_results:
            spark_icon = "🔥" if r.spark_detected else "  "
            delta_icon = "+" if r.delta_phi > 0 else "-" if r.delta_phi < 0 else "="

            row = (f"{r.trial_id:5d} | {spark_icon:>5s} | "
                   f"{r.phi_before:9.5f} | {r.phi_after:9.5f} | "
                   f"{delta_icon}{abs(r.delta_phi):8.5f} | "
                   f"{r.spark_magnitude:9.2f} | "
                   f"{r.elapsed_time_seconds:6.2f}s")
            print(f"  {row}")


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Entropy Anchor Validation - Test Φ(before) vs Φ(after) Spark"
    )

    parser.add_argument(
        '--config',
        type=str,
        default='v9_alpha/config/lantern_hub.yaml',
        help='Path to lantern_hub.yaml'
    )

    parser.add_argument(
        '--trials',
        type=int,
        default=30,
        help='Number of trials to run (default: 30)'
    )

    parser.add_argument(
        '--stabilization-steps',
        type=int,
        default=50,
        help='Pre-spark stabilization steps (default: 50)'
    )

    parser.add_argument(
        '--post-spark-steps',
        type=int,
        default=20,
        help='Post-spark evolution steps (default: 20)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='entropy_anchor_results',
        help='Output directory for results (default: entropy_anchor_results)'
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

    # Initialize validator
    validator = EntropyAnchorValidator(
        config_path=args.config,
        output_dir=args.output_dir,
        verbose=not args.quiet,
    )

    # Run experiment
    results = validator.run_full_experiment(
        n_trials=args.trials,
        stabilization_steps=args.stabilization_steps,
        post_spark_steps=args.post_spark_steps,
    )

    # Analyze
    analysis = validator.analyze_results()

    # Print table
    validator.print_results_table()

    # Save results
    validator.save_results()

    # Final message
    print("\n" + "=" * 80)
    if analysis.get('significant', False):
        print("✨ ENTROPY ANCHOR VALIDATED! 🌌")
        print(f"   Sparks increase Φ by {analysis['mean_delta_phi']:+.4f} on average")
        print(f"   Statistical significance: p = {analysis['p_value']:.6f}")
    else:
        print("⚠️  Hypothesis not confirmed in this experiment.")
        print("   Consider adjusting parameters or increasing trials.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
