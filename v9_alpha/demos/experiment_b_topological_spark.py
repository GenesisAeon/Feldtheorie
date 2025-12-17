#!/usr/bin/env python3
"""Experiment B: Topological Spark - The Bit-Flip Test

**The Fundamental Discovery (Experiment A):**
> "It's not the hole itself, but the APPEARING/DISAPPEARING (bit flip)
>  that causes the jump."  — Johann B. Römer

**Experiment A Result:**
ΔΦ = 0.0000 despite massive parameter perturbations (dissonance_level=0.8).

**Φ-Robustness Principle:**
Integrated Information (Φ) is robust to parameter noise but changes
discontinuously when TOPOLOGY changes (connections deleted/created).

**Experiment B Hypothesis:**
H₁: ΔΦ = Φ_genesis - Φ_implosion > 0
    (Topological reconfiguration increases integrated information)

**Experimental Protocol:**

1. **Baseline Measurement**
   - Run network to stable state
   - Measure Φ_baseline (initial integrated information)

2. **PHASE 1: IMPLOSION** 🔪
   - Activate TopologicalReaper.phase1_implosion()
   - DELETE weak/redundant connections
   - Measure Φ_implosion (should be LOWER than baseline)

3. **PHASE 2: VACUUM** 🌌
   - Run network with pruned topology
   - System explores reduced configuration space
   - Measure Φ_vacuum (should remain LOW)

4. **PHASE 3: GENESIS** ✨
   - Activate TopologicalReaper.phase3_genesis()
   - GROW new connections at resonance peaks
   - Measure Φ_genesis (should be HIGHER than implosion)

5. **Statistical Analysis**
   - Calculate ΔΦ = Φ_genesis - Φ_implosion
   - Repeat for N trials
   - t-test: mean(ΔΦ) > 0 with p < 0.05

**Expected Outcome:**
If topological reconfiguration hypothesis holds:
- Φ_implosion < Φ_baseline (pruning reduces integration)
- Φ_genesis > Φ_implosion (synaptogenesis increases integration)
- mean(ΔΦ) > 0 with statistical significance

Version: v9.0.5-beta
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
from v9_alpha.models.frequency_tuner import TopologicalReaper, create_topological_reaper

# Import constants
from models.unified_constants import V_RIG_DEFAULT


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class TopologicalTrialResult:
    """Results from a single topological reconfiguration trial"""
    trial_id: int

    # Baseline state
    phi_baseline: float
    n_edges_baseline: int
    coherence_baseline: float

    # Phase 1: IMPLOSION
    phi_implosion: float
    n_edges_implosion: int
    n_pruned: int
    coherence_implosion: float

    # Phase 2: VACUUM
    phi_vacuum: float
    vacuum_steps: int
    coherence_vacuum: float

    # Phase 3: GENESIS
    phi_genesis: float
    n_edges_genesis: int
    n_grown: int
    coherence_genesis: float

    # Key metrics
    delta_phi_implosion: float  # Φ_implosion - Φ_baseline (should be negative)
    delta_phi_genesis: float    # Φ_genesis - Φ_implosion (should be positive!)
    delta_phi_total: float      # Φ_genesis - Φ_baseline

    # Metadata
    elapsed_time_seconds: float
    reaper_summary: Dict


# ============================================================================
# Experiment B: Topological Spark Validator
# ============================================================================

class TopologicalSparkValidator:
    """
    Experimental validation of the Topological Reconfiguration hypothesis

    Tests whether topological changes (connection deletion/creation)
    lead to measurable changes in integrated information (Φ), validating
    the Bit-Flip principle discovered by Johann B. Römer.
    """

    def __init__(
        self,
        config_path: str,
        output_dir: str = "experiment_b_results",
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
        self.trial_results: List[TopologicalTrialResult] = []

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

    def measure_network_state(
        self,
        network: LanternNetwork,
        tracker: EmergenceTracker,
        calc: EMFieldCalculator,
        label: str = "",
    ) -> Tuple[float, float, int]:
        """
        Measure current network state (Φ, coherence, n_edges)

        Args:
            network: Lantern network
            tracker: Emergence tracker
            calc: EM field calculator
            label: Label for printing

        Returns:
            (phi, coherence, n_edges)
        """
        # Get coupling matrix
        coupling_matrix = network.get_coupling_matrix()
        beta_values = np.array([l.beta for l in network.lanterns.values()])
        impedance_values = np.array([l.em_properties.impedance_z for l in network.lanterns.values()])
        n_active = len(network.get_active_lanterns())

        # Calculate phase coherence
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
        coherence = calc.calculate_phase_coherence(active_fields, t=0.0)

        # Calculate Φ
        phi = tracker.calculate_phi_network(coupling_matrix)

        # Count edges
        n_edges = int(np.sum(coupling_matrix > 0) / 2)  # Symmetric matrix

        if self.verbose and label:
            print(f"  [{label}] Φ = {phi:.4f}, coherence = {coherence:.3f}, edges = {n_edges}")

        return phi, coherence, n_edges

    def run_single_trial(
        self,
        trial_id: int,
        pruning_threshold: float = 0.15,
        growth_resonance_threshold: float = 0.75,
        vacuum_steps: int = 10,
        strategy: str = "uniform",
        hub_slash_fraction: float = 0.5,
    ) -> TopologicalTrialResult:
        """
        Run a single topological reconfiguration trial

        Args:
            trial_id: Trial identifier
            pruning_threshold: Threshold for pruning weak connections
            growth_resonance_threshold: Threshold for growing new connections
            vacuum_steps: Number of steps to run in vacuum phase
            strategy: Pruning strategy - "uniform" or "hub_attack"
            hub_slash_fraction: Fraction of hub connections to slash (for hub_attack)

        Returns:
            TopologicalTrialResult
        """
        start_time = time.time()

        # Initialize components
        network = load_lantern_network(self.config_path)
        tracker = EmergenceTracker()
        calc = EMFieldCalculator()
        reaper = create_topological_reaper(
            pruning_threshold=pruning_threshold,
            growth_resonance_threshold=growth_resonance_threshold,
            strategy=strategy,
        )

        if self.verbose:
            print(f"\n  Trial {trial_id}")
            print(f"  ─────────")

        # ────────────────────────────────────────────────────────────────────
        # BASELINE MEASUREMENT
        # ────────────────────────────────────────────────────────────────────

        phi_baseline, coherence_baseline, n_edges_baseline = self.measure_network_state(
            network, tracker, calc, label="BASELINE"
        )

        # ────────────────────────────────────────────────────────────────────
        # PHASE 1: IMPLOSION 🔪
        # ────────────────────────────────────────────────────────────────────

        if strategy == "hub_attack":
            if self.verbose:
                print("\n  👑🔪 PHASE 1: HUB ATTACK (The Königsmord)")
        else:
            if self.verbose:
                print("\n  🔪 PHASE 1: IMPLOSION (The Cut)")

        # Get current network state
        coupling_matrix = network.get_coupling_matrix()
        beta_values = np.array([l.beta for l in network.lanterns.values()])

        # Execute implosion (uniform or hub attack)
        if strategy == "hub_attack":
            coupling_pruned = reaper.phase1_hub_attack(
                coupling_matrix,
                beta_values,
                slash_fraction=hub_slash_fraction,
            )
        else:
            coupling_pruned = reaper.phase1_implosion(coupling_matrix, beta_values)

        # Update network with pruned topology
        network.set_coupling_matrix(coupling_pruned)

        # Measure post-implosion state
        phi_implosion, coherence_implosion, n_edges_implosion = self.measure_network_state(
            network, tracker, calc, label="IMPLOSION"
        )

        n_pruned = len(reaper.pruned_edges)

        if self.verbose:
            print(f"     → Pruned {n_pruned} edges")

        # ────────────────────────────────────────────────────────────────────
        # PHASE 2: VACUUM 🌌
        # ────────────────────────────────────────────────────────────────────

        if self.verbose:
            print("\n  🌌 PHASE 2: VACUUM (The Void)")

        # Vacuum phase: just let the system run with reduced topology
        coupling_vacuum = reaper.phase2_vacuum(coupling_pruned)

        # Measure vacuum state (should be similar to implosion)
        phi_vacuum, coherence_vacuum, _ = self.measure_network_state(
            network, tracker, calc, label="VACUUM"
        )

        # ────────────────────────────────────────────────────────────────────
        # PHASE 3: GENESIS ✨
        # ────────────────────────────────────────────────────────────────────

        if self.verbose:
            print("\n  ✨ PHASE 3: GENESIS (The Heal)")

        # Get phases and frequencies for resonance detection
        phases = np.array([l.theta for l in network.lanterns.values()])  # Use theta as proxy for phase
        frequencies = np.array([l.em_properties.frequency_hz for l in network.lanterns.values()])

        # Execute genesis
        coupling_healed = reaper.phase3_genesis(
            coupling_vacuum,
            phases,
            frequencies,
        )

        # Update network with healed topology
        network.set_coupling_matrix(coupling_healed)

        # Measure post-genesis state
        phi_genesis, coherence_genesis, n_edges_genesis = self.measure_network_state(
            network, tracker, calc, label="GENESIS"
        )

        n_grown = len(reaper.grown_edges)

        if self.verbose:
            print(f"     → Grew {n_grown} new edges")

        # ────────────────────────────────────────────────────────────────────
        # ANALYSIS
        # ────────────────────────────────────────────────────────────────────

        delta_phi_implosion = phi_implosion - phi_baseline
        delta_phi_genesis = phi_genesis - phi_implosion
        delta_phi_total = phi_genesis - phi_baseline

        elapsed_time = time.time() - start_time

        if self.verbose:
            print(f"\n  📊 RESULTS:")
            print(f"     ΔΦ_implosion = {delta_phi_implosion:+.4f} (Φ drop from pruning)")
            print(f"     ΔΦ_genesis   = {delta_phi_genesis:+.4f} (Φ rise from synaptogenesis) {'✓✓' if delta_phi_genesis > 0 else '✗'}")
            print(f"     ΔΦ_total     = {delta_phi_total:+.4f} (Net change)")

        # Store result
        result = TopologicalTrialResult(
            trial_id=trial_id,
            phi_baseline=phi_baseline,
            n_edges_baseline=n_edges_baseline,
            coherence_baseline=coherence_baseline,
            phi_implosion=phi_implosion,
            n_edges_implosion=n_edges_implosion,
            n_pruned=n_pruned,
            coherence_implosion=coherence_implosion,
            phi_vacuum=phi_vacuum,
            vacuum_steps=vacuum_steps,
            coherence_vacuum=coherence_vacuum,
            phi_genesis=phi_genesis,
            n_edges_genesis=n_edges_genesis,
            n_grown=n_grown,
            coherence_genesis=coherence_genesis,
            delta_phi_implosion=delta_phi_implosion,
            delta_phi_genesis=delta_phi_genesis,
            delta_phi_total=delta_phi_total,
            elapsed_time_seconds=elapsed_time,
            reaper_summary=reaper.get_reaper_summary(),
        )

        return result

    def run_experiment(
        self,
        n_trials: int = 10,
        pruning_threshold: float = 0.15,
        growth_resonance_threshold: float = 0.75,
        vacuum_steps: int = 10,
        strategy: str = "uniform",
        hub_slash_fraction: float = 0.5,
    ) -> List[TopologicalTrialResult]:
        """
        Run full Experiment B with multiple trials

        Args:
            n_trials: Number of independent trials
            pruning_threshold: Threshold for pruning
            growth_resonance_threshold: Threshold for growth
            vacuum_steps: Steps to run in vacuum phase
            strategy: Pruning strategy - "uniform" or "hub_attack"
            hub_slash_fraction: Fraction of hub connections to slash (for hub_attack)

        Returns:
            List of trial results
        """
        self.print_header("EXPERIMENT B: TOPOLOGICAL SPARK - THE BIT-FLIP TEST")

        print(f"\nConfiguration:")
        print(f"  Strategy: {strategy}")
        print(f"  Trials: {n_trials}")
        print(f"  Pruning threshold: {pruning_threshold}")
        print(f"  Growth resonance threshold: {growth_resonance_threshold}")
        print(f"  Vacuum steps: {vacuum_steps}")
        if strategy == "hub_attack":
            print(f"  Hub slash fraction: {hub_slash_fraction}")

        self.trial_results = []

        for trial_id in range(1, n_trials + 1):
            result = self.run_single_trial(
                trial_id=trial_id,
                pruning_threshold=pruning_threshold,
                growth_resonance_threshold=growth_resonance_threshold,
                vacuum_steps=vacuum_steps,
                strategy=strategy,
                hub_slash_fraction=hub_slash_fraction,
            )
            self.trial_results.append(result)

        return self.trial_results

    def analyze_results(self) -> Dict:
        """
        Perform statistical analysis on experiment results

        Returns:
            Dictionary with analysis results
        """
        if not self.trial_results:
            return {}

        self.print_header("STATISTICAL ANALYSIS")

        # Extract metrics
        delta_phi_implosion = np.array([r.delta_phi_implosion for r in self.trial_results])
        delta_phi_genesis = np.array([r.delta_phi_genesis for r in self.trial_results])
        delta_phi_total = np.array([r.delta_phi_total for r in self.trial_results])

        # Descriptive statistics
        print("\nΔΦ Statistics:")
        print(f"  Implosion (pruning):    {np.mean(delta_phi_implosion):+.4f} ± {np.std(delta_phi_implosion):.4f}")
        print(f"  Genesis (synaptogenesis): {np.mean(delta_phi_genesis):+.4f} ± {np.std(delta_phi_genesis):.4f}")
        print(f"  Total (net change):       {np.mean(delta_phi_total):+.4f} ± {np.std(delta_phi_total):.4f}")

        # Hypothesis test: Is mean(ΔΦ_genesis) > 0?
        from scipy import stats

        if len(delta_phi_genesis) > 1:
            # One-sample t-test: H₀: mean = 0, H₁: mean > 0
            t_stat, p_value_two_tailed = stats.ttest_1samp(delta_phi_genesis, 0.0)
            p_value_one_tailed = p_value_two_tailed / 2  # One-tailed test

            print(f"\nHypothesis Test (ΔΦ_genesis > 0):")
            print(f"  t-statistic: {t_stat:.4f}")
            print(f"  p-value (one-tailed): {p_value_one_tailed:.4f}")

            if p_value_one_tailed < 0.05 and np.mean(delta_phi_genesis) > 0:
                print(f"  ✓✓ HYPOTHESIS CONFIRMED (p < 0.05)")
                print(f"     Topological reconfiguration INCREASES Φ!")
            elif np.mean(delta_phi_genesis) > 0:
                print(f"  ✓ Positive trend, but not statistically significant")
            else:
                print(f"  ✗ HYPOTHESIS NOT CONFIRMED")

        # Effect size (Cohen's d)
        if len(delta_phi_genesis) > 1 and np.std(delta_phi_genesis) > 0:
            cohens_d = np.mean(delta_phi_genesis) / np.std(delta_phi_genesis)
            print(f"\nEffect Size:")
            print(f"  Cohen's d: {cohens_d:.4f}")
            if abs(cohens_d) > 0.8:
                print(f"  → Large effect")
            elif abs(cohens_d) > 0.5:
                print(f"  → Medium effect")
            elif abs(cohens_d) > 0.2:
                print(f"  → Small effect")
            else:
                print(f"  → Negligible effect")

        # Topology statistics
        n_pruned_mean = np.mean([r.n_pruned for r in self.trial_results])
        n_grown_mean = np.mean([r.n_grown for r in self.trial_results])

        print(f"\nTopology Changes:")
        print(f"  Mean edges pruned: {n_pruned_mean:.1f}")
        print(f"  Mean edges grown:  {n_grown_mean:.1f}")
        print(f"  Net change:        {n_grown_mean - n_pruned_mean:+.1f}")

        # Compile analysis
        analysis = {
            'n_trials': len(self.trial_results),
            'delta_phi_implosion_mean': float(np.mean(delta_phi_implosion)),
            'delta_phi_implosion_std': float(np.std(delta_phi_implosion)),
            'delta_phi_genesis_mean': float(np.mean(delta_phi_genesis)),
            'delta_phi_genesis_std': float(np.std(delta_phi_genesis)),
            'delta_phi_total_mean': float(np.mean(delta_phi_total)),
            'delta_phi_total_std': float(np.std(delta_phi_total)),
            't_statistic': float(t_stat) if len(delta_phi_genesis) > 1 else None,
            'p_value': float(p_value_one_tailed) if len(delta_phi_genesis) > 1 else None,
            'cohens_d': float(cohens_d) if len(delta_phi_genesis) > 1 and np.std(delta_phi_genesis) > 0 else None,
            'hypothesis_confirmed': bool(p_value_one_tailed < 0.05 and np.mean(delta_phi_genesis) > 0) if len(delta_phi_genesis) > 1 else False,
            'n_pruned_mean': float(n_pruned_mean),
            'n_grown_mean': float(n_grown_mean),
        }

        return analysis

    def save_results(self, filename: str = "experiment_b_results.json") -> None:
        """
        Save results to JSON file

        Args:
            filename: Output filename
        """
        output_path = os.path.join(self.output_dir, filename)

        results_dict = {
            'experiment': 'Experiment B - Topological Spark',
            'hypothesis': 'Topological reconfiguration increases Φ',
            'n_trials': len(self.trial_results),
            'trials': [asdict(r) for r in self.trial_results],
            'analysis': self.analyze_results() if self.trial_results else {},
        }

        with open(output_path, 'w') as f:
            json.dump(results_dict, f, indent=2)

        if self.verbose:
            print(f"\n✓ Results saved to: {output_path}")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Experiment B: Topological Spark - The Bit-Flip Test"
    )

    parser.add_argument(
        '--config',
        type=str,
        default='v9_alpha/config/lantern_hub.yaml',
        help='Path to lantern_hub.yaml configuration'
    )

    parser.add_argument(
        '--trials',
        type=int,
        default=10,
        help='Number of trials to run'
    )

    parser.add_argument(
        '--pruning-threshold',
        type=float,
        default=0.15,
        help='Coupling strength threshold for pruning weak edges'
    )

    parser.add_argument(
        '--growth-threshold',
        type=float,
        default=0.75,
        help='Resonance threshold for growing new connections'
    )

    parser.add_argument(
        '--vacuum-steps',
        type=int,
        default=10,
        help='Number of steps to run in vacuum phase'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='experiment_b_results',
        help='Output directory for results'
    )

    parser.add_argument(
        '--strategy',
        type=str,
        default='uniform',
        choices=['uniform', 'hub_attack'],
        help='Pruning strategy: "uniform" (prune weak edges) or "hub_attack" (attack hub node)'
    )

    parser.add_argument(
        '--hub-slash-fraction',
        type=float,
        default=0.5,
        help='Fraction of hub connections to slash (only for hub_attack strategy, default: 0.5)'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress verbose output'
    )

    args = parser.parse_args()

    # Run experiment
    validator = TopologicalSparkValidator(
        config_path=args.config,
        output_dir=args.output_dir,
        verbose=not args.quiet,
    )

    results = validator.run_experiment(
        n_trials=args.trials,
        pruning_threshold=args.pruning_threshold,
        growth_resonance_threshold=args.growth_threshold,
        vacuum_steps=args.vacuum_steps,
        strategy=args.strategy,
        hub_slash_fraction=args.hub_slash_fraction,
    )

    # Analyze and save
    validator.analyze_results()
    validator.save_results()

    print("\n" + "=" * 80)
    print("EXPERIMENT B COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
