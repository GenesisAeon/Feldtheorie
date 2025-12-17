#!/usr/bin/env python3
"""Experiment C: Solar Engine - Breaking the Crystal-Death Paradox

**The Crystal-Death Paradox:**
> "Maximizing Φ through topology optimization leads to a frozen, dead state
>  (Coherence → 1.0). The system crystallizes into mathematical perfection
>  but loses the capacity for information dynamics." — The Missing Link

**Experiment A:** ΔΦ = 0 (Noise alone doesn't change Φ)
**Experiment B:** Φ ↑, but Coherence → 1.0 (System dies, frozen perfection)
**Experiment C:** The Solar Engine - "Let the system breathe"

**The Solution: Metastability via Active Symmetry Breaking**

The system needs TWO complementary mechanisms:

1. **Solar Driver (Metastability Injector)** ☀️
   - Monitors local coherence per cluster
   - When coherence > 0.95 (too perfect): inject PHASE KICKS
   - Prevents complete synchronization (thermal death)
   - Physics: Frustration term - system can't minimize all couplings simultaneously

2. **Comet Injector (Topology Mutation)** ☄️
   - Creates long-range connections (Watts-Strogatz mechanism)
   - Connects Edge Nodes (low degree) to Hub Nodes (high degree)
   - Induces Small-World topology: high Φ + low path length
   - Lowers mean path length without destroying clustering

**The Physics:**
- **Chimera States**: Islands of order in a sea of chaos (or vice versa)
- **Edge of Chaos**: Balanced between frozen order and random disorder
- **Degeneracy**: Redundancy that remains functionally flexible

**Success Metric:**
- High average Φ: E[Φ] > Φ_baseline
- High variance: σ_Φ > 0 (System oscillates, not flatlines)
- Breathing pattern: Φ(t) should fluctuate rhythmically

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
from v9_alpha.models.phase_dynamics import PhaseEvolver, create_natural_frequencies

# Import constants
from models.unified_constants import V_RIG_DEFAULT


# ============================================================================
# Solar Driver: Metastability Injector
# ============================================================================

class SolarDriver:
    """
    Solar Driver - Active Metastability Maintenance

    Monitors local coherence and injects energy (phase kicks) when
    clusters become too synchronized, preventing thermal death.

    Physics Analogy:
    - Like a metabolic engine that prevents a cell from freezing
    - Maintains system at "edge of chaos" via frustration
    """

    def __init__(
        self,
        coherence_threshold: float = 0.95,
        kick_amplitude: float = 0.5,
        kick_strategy: str = "aggressive",
    ):
        """
        Initialize Solar Driver

        Args:
            coherence_threshold: Coherence above which to inject kicks
            kick_amplitude: Phase shift amplitude (radians)
            kick_strategy: "aggressive" or "gentle"
        """
        self.coherence_threshold = coherence_threshold
        self.kick_amplitude = kick_amplitude
        self.kick_strategy = kick_strategy

        # Statistics
        self.n_kicks = 0
        self.kick_history: List[Dict] = []

    def calculate_local_coherence(
        self,
        phases: np.ndarray,
        coupling_matrix: np.ndarray,
    ) -> Tuple[float, np.ndarray]:
        """
        Calculate local coherence for each node

        Local coherence = average phase alignment with neighbors

        Args:
            phases: Array of phase values (θ)
            coupling_matrix: NxN coupling matrix

        Returns:
            (global_coherence, local_coherences)
        """
        n = len(phases)
        local_coherences = np.zeros(n)

        for i in range(n):
            # Get neighbors (nodes with coupling > 0)
            neighbors = np.where(coupling_matrix[i] > 0)[0]

            if len(neighbors) == 0:
                local_coherences[i] = 0.0
                continue

            # Calculate phase differences with neighbors
            phase_diffs = phases[neighbors] - phases[i]

            # Coherence = magnitude of mean complex phasor
            # High when phases aligned, low when scattered
            phasor = np.mean(np.exp(1j * phase_diffs))
            local_coherences[i] = np.abs(phasor)

        # Global coherence = mean of local coherences
        global_coherence = np.mean(local_coherences)

        return global_coherence, local_coherences

    def inject_phase_kick(
        self,
        phases: np.ndarray,
        local_coherences: np.ndarray,
        kick_indices: Optional[List[int]] = None,
    ) -> np.ndarray:
        """
        Inject phase kicks to break excessive synchronization

        Args:
            phases: Current phase values
            local_coherences: Local coherence per node
            kick_indices: Specific nodes to kick (if None, auto-detect)

        Returns:
            Modified phase array
        """
        phases_kicked = phases.copy()

        # Determine which nodes to kick
        if kick_indices is None:
            # Kick nodes with coherence above threshold
            kick_indices = np.where(local_coherences > self.coherence_threshold)[0]

        if len(kick_indices) == 0:
            return phases_kicked

        # Apply kicks based on strategy
        if self.kick_strategy == "aggressive":
            # Large random phase shifts
            kicks = np.random.uniform(
                -self.kick_amplitude,
                self.kick_amplitude,
                len(kick_indices)
            )
        elif self.kick_strategy == "gentle":
            # Small systematic shifts
            kicks = np.random.normal(0, self.kick_amplitude / 2, len(kick_indices))
        else:
            kicks = np.zeros(len(kick_indices))

        phases_kicked[kick_indices] += kicks

        # Wrap to [-π, π]
        phases_kicked = np.arctan2(np.sin(phases_kicked), np.cos(phases_kicked))

        # Update statistics
        self.n_kicks += len(kick_indices)
        self.kick_history.append({
            'timestamp': time.time(),
            'n_kicked': len(kick_indices),
            'kicked_indices': list(kick_indices),
            'kick_amplitude': self.kick_amplitude,
        })

        return phases_kicked

    def step(
        self,
        phases: np.ndarray,
        coupling_matrix: np.ndarray,
        em_coherence: Optional[float] = None,
    ) -> Tuple[np.ndarray, Dict]:
        """
        Execute one Solar Driver step

        Args:
            phases: Current phase values
            coupling_matrix: Coupling matrix
            em_coherence: EM field coherence (if provided, use instead of phase coherence)

        Returns:
            (modified_phases, step_info)
        """
        # Calculate coherence
        if em_coherence is not None:
            # Use provided EM coherence (ground truth)
            global_coherence = em_coherence
            local_coherences = np.ones(len(phases)) * em_coherence  # Assume uniform
        else:
            # Fallback to phase-based coherence
            global_coherence, local_coherences = self.calculate_local_coherence(
                phases, coupling_matrix
            )

        # Determine if intervention needed
        kick_needed = global_coherence > self.coherence_threshold

        if kick_needed:
            phases_new = self.inject_phase_kick(phases, local_coherences)
            action = "kick"
        else:
            phases_new = phases
            action = "none"

        step_info = {
            'global_coherence': float(global_coherence),
            'max_local_coherence': float(np.max(local_coherences)),
            'action': action,
            'n_nodes_kicked': int(np.sum(local_coherences > self.coherence_threshold)),
        }

        return phases_new, step_info

    def get_statistics(self) -> Dict:
        """Get Solar Driver statistics"""
        return {
            'total_kicks': self.n_kicks,
            'n_kick_events': len(self.kick_history),
            'kick_rate': self.n_kicks / max(1, len(self.kick_history)),
        }


# ============================================================================
# Comet Injector: Topology Mutation Engine
# ============================================================================

class CometInjector:
    """
    Comet Injector - Long-Range Connection Creator

    Periodically creates connections between Edge (low-degree) and
    Hub (high-degree) nodes to induce Small-World topology.

    Physics:
    - Watts-Strogatz rewiring mechanism
    - Lowers mean path length without destroying local clustering
    - Enables high Φ with dynamic information flow
    """

    def __init__(
        self,
        injection_probability: float = 0.1,
        connection_lifetime: int = 5,
        connection_strength: float = 0.3,
    ):
        """
        Initialize Comet Injector

        Args:
            injection_probability: Probability of creating connection per step
            connection_lifetime: How long connections persist (steps)
            connection_strength: Coupling strength of new connections
        """
        self.injection_probability = injection_probability
        self.connection_lifetime = connection_lifetime
        self.connection_strength = connection_strength

        # Track active comet connections
        self.active_comets: List[Dict] = []

        # Statistics
        self.n_comets_created = 0
        self.n_comets_expired = 0

    def identify_edge_and_hub_nodes(
        self,
        coupling_matrix: np.ndarray,
    ) -> Tuple[List[int], List[int]]:
        """
        Identify Edge (low-degree) and Hub (high-degree) nodes

        Args:
            coupling_matrix: NxN coupling matrix

        Returns:
            (edge_nodes, hub_nodes)
        """
        # Calculate degree (number of connections)
        degrees = np.sum(coupling_matrix > 0, axis=1)

        # Edge nodes: bottom 30% by degree
        edge_threshold = np.percentile(degrees, 30)
        edge_nodes = np.where(degrees <= edge_threshold)[0].tolist()

        # Hub nodes: top 30% by degree
        hub_threshold = np.percentile(degrees, 70)
        hub_nodes = np.where(degrees >= hub_threshold)[0].tolist()

        return edge_nodes, hub_nodes

    def create_comet_connection(
        self,
        edge_nodes: List[int],
        hub_nodes: List[int],
    ) -> Optional[Tuple[int, int]]:
        """
        Create a single comet connection

        Args:
            edge_nodes: List of edge node indices
            hub_nodes: List of hub node indices

        Returns:
            (source, target) or None if no connection created
        """
        if len(edge_nodes) == 0 or len(hub_nodes) == 0:
            return None

        # Randomly select edge and hub
        edge = np.random.choice(edge_nodes)
        hub = np.random.choice(hub_nodes)

        # Don't connect to self
        if edge == hub:
            return None

        return (edge, hub)

    def inject_comets(
        self,
        coupling_matrix: np.ndarray,
    ) -> np.ndarray:
        """
        Inject comet connections into network

        Args:
            coupling_matrix: Current coupling matrix

        Returns:
            Modified coupling matrix with comet connections
        """
        coupling_new = coupling_matrix.copy()

        # Age existing comets
        for comet in self.active_comets:
            comet['age'] += 1

        # Remove expired comets
        expired = [c for c in self.active_comets if c['age'] >= self.connection_lifetime]
        for comet in expired:
            i, j = comet['edge'], comet['hub']
            coupling_new[i, j] = 0.0
            coupling_new[j, i] = 0.0
            self.n_comets_expired += 1

        self.active_comets = [c for c in self.active_comets if c['age'] < self.connection_lifetime]

        # Probabilistically create new comet
        if np.random.random() < self.injection_probability:
            edge_nodes, hub_nodes = self.identify_edge_and_hub_nodes(coupling_matrix)
            connection = self.create_comet_connection(edge_nodes, hub_nodes)

            if connection is not None:
                edge, hub = connection

                # Add connection (bidirectional)
                coupling_new[edge, hub] = self.connection_strength
                coupling_new[hub, edge] = self.connection_strength

                # Track comet
                self.active_comets.append({
                    'edge': edge,
                    'hub': hub,
                    'age': 0,
                    'created_at': time.time(),
                })

                self.n_comets_created += 1

        return coupling_new

    def get_statistics(self) -> Dict:
        """Get Comet Injector statistics"""
        return {
            'total_comets_created': self.n_comets_created,
            'total_comets_expired': self.n_comets_expired,
            'active_comets': len(self.active_comets),
        }


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class SolarEngineSnapshot:
    """Single timestep snapshot of Solar Engine experiment"""
    step: int
    time: float

    # Φ and coherence
    phi: float
    coherence: float

    # Solar Driver
    solar_action: str
    n_nodes_kicked: int

    # Comet Injector
    n_active_comets: int
    n_comets_created_cumulative: int

    # Network topology
    n_edges: int
    mean_degree: float

    # Success metric
    phi_mean_so_far: float
    phi_std_so_far: float


@dataclass
class SolarEngineResult:
    """Complete results from Solar Engine experiment"""
    n_steps: int
    duration_seconds: float

    # Summary statistics
    phi_mean: float
    phi_std: float
    phi_min: float
    phi_max: float

    coherence_mean: float
    coherence_std: float

    # Mechanisms
    solar_driver_stats: Dict
    comet_injector_stats: Dict

    # Success evaluation
    breathing_detected: bool  # σ_Φ > threshold
    phi_improvement: float    # vs baseline

    # Time series
    snapshots: List[SolarEngineSnapshot]


# ============================================================================
# Experiment C: Solar Engine Validator
# ============================================================================

class SolarEngineValidator:
    """
    Experimental validation of the Solar Engine hypothesis

    Tests whether active metastability maintenance (Solar Driver)
    combined with topology mutation (Comet Injector) can achieve
    high Φ while maintaining dynamic oscillations (breathing).
    """

    def __init__(
        self,
        config_path: str,
        output_dir: str = "experiment_c_results",
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

    def print_header(self, title: str) -> None:
        """Print formatted header"""
        if self.verbose:
            print("\n" + "=" * 80)
            print(title)
            print("=" * 80)

    def measure_network_state(
        self,
        network: LanternNetwork,
        tracker: EmergenceTracker,
        calc: EMFieldCalculator,
    ) -> Tuple[float, float, int, float]:
        """
        Measure current network state

        Returns:
            (phi, coherence, n_edges, mean_degree)
        """
        # Get coupling matrix
        coupling_matrix = network.get_coupling_matrix()

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

        # Topology metrics
        n_edges = int(np.sum(coupling_matrix > 0) / 2)
        degrees = np.sum(coupling_matrix > 0, axis=1)
        mean_degree = np.mean(degrees)

        return phi, coherence, n_edges, mean_degree

    def run_solar_engine_experiment(
        self,
        n_steps: int = 50,
        solar_coherence_threshold: float = 0.85,
        solar_kick_amplitude: float = 0.5,
        comet_injection_probability: float = 0.15,
        comet_lifetime: int = 5,
    ) -> SolarEngineResult:
        """
        Run Solar Engine experiment

        Args:
            n_steps: Number of simulation steps
            solar_coherence_threshold: Coherence threshold for Solar Driver
            solar_kick_amplitude: Phase kick amplitude
            comet_injection_probability: Probability of comet injection
            comet_lifetime: Comet connection lifetime

        Returns:
            SolarEngineResult
        """
        start_time = time.time()

        self.print_header("EXPERIMENT C: SOLAR ENGINE - BREAKING THE CRYSTAL-DEATH PARADOX")

        print(f"\nConfiguration:")
        print(f"  Steps: {n_steps}")
        print(f"  Solar coherence threshold: {solar_coherence_threshold}")
        print(f"  Solar kick amplitude: {solar_kick_amplitude}")
        print(f"  Comet injection probability: {comet_injection_probability}")
        print(f"  Comet lifetime: {comet_lifetime} steps")

        # Initialize components
        network = load_lantern_network(self.config_path)
        tracker = EmergenceTracker()
        calc = EMFieldCalculator()

        solar_driver = SolarDriver(
            coherence_threshold=solar_coherence_threshold,
            kick_amplitude=solar_kick_amplitude,
            kick_strategy="aggressive",
        )

        comet_injector = CometInjector(
            injection_probability=comet_injection_probability,
            connection_lifetime=comet_lifetime,
            connection_strength=0.3,
        )

        # Phase dynamics (Kuramoto-like synchronization)
        # Stronger coupling (scale > 1) enables re-synchronization after Solar kicks
        phase_evolver = PhaseEvolver(
            dt=0.15,
            noise_level=0.01,
            coupling_strength_scale=8.0  # Strong enough to overcome perturbations
        )
        n_lanterns = len(network.lanterns)
        natural_frequencies = create_natural_frequencies(
            n_lanterns, mean_frequency=0.0, frequency_spread=0.01
        )

        # Measure baseline
        phi_baseline, coherence_baseline, n_edges_baseline, mean_degree_baseline = \
            self.measure_network_state(network, tracker, calc)

        if self.verbose:
            print(f"\n📊 BASELINE:")
            print(f"  Φ = {phi_baseline:.4f}")
            print(f"  Coherence = {coherence_baseline:.3f}")
            print(f"  Edges = {n_edges_baseline}, Mean degree = {mean_degree_baseline:.1f}")

        # Run simulation
        snapshots: List[SolarEngineSnapshot] = []

        if self.verbose:
            print(f"\n🌞☄️  SOLAR ENGINE ACTIVE - LET THE SYSTEM BREATHE")
            print(f"{'─' * 80}")

        for step in range(n_steps):
            # Get current state
            phases = np.array([l.theta for l in network.lanterns.values()])
            coupling_matrix = network.get_coupling_matrix()

            # 0. Measure current coherence (before intervention)
            phi_before, coherence_before, _, _ = self.measure_network_state(
                network, tracker, calc
            )

            # 1. Solar Driver: Break excessive synchronization
            phases_new, solar_info = solar_driver.step(
                phases, coupling_matrix, em_coherence=coherence_before
            )

            # Update phases in network
            for i, (lantern_id, lantern) in enumerate(network.lanterns.items()):
                lantern.theta = phases_new[i]

            # 2. Comet Injector: Create long-range connections
            coupling_new = comet_injector.inject_comets(coupling_matrix)
            network.set_coupling_matrix(coupling_new)

            # 3. Natural phase evolution (Kuramoto dynamics)
            # This allows the system to naturally re-synchronize after perturbations
            phase_evolver.evolve_network(network, natural_frequencies)

            # 4. Measure state (after interventions)
            phi, coherence, n_edges, mean_degree = self.measure_network_state(
                network, tracker, calc
            )

            # Calculate running statistics
            phis_so_far = [s.phi for s in snapshots] + [phi]
            phi_mean_so_far = np.mean(phis_so_far)
            phi_std_so_far = np.std(phis_so_far)

            # Create snapshot
            snapshot = SolarEngineSnapshot(
                step=step,
                time=time.time() - start_time,
                phi=phi,
                coherence=coherence,
                solar_action=solar_info['action'],
                n_nodes_kicked=solar_info['n_nodes_kicked'],
                n_active_comets=len(comet_injector.active_comets),
                n_comets_created_cumulative=comet_injector.n_comets_created,
                n_edges=n_edges,
                mean_degree=mean_degree,
                phi_mean_so_far=phi_mean_so_far,
                phi_std_so_far=phi_std_so_far,
            )

            snapshots.append(snapshot)

            # Print progress
            if self.verbose and (step % 10 == 0 or step == n_steps - 1):
                action_symbol = "☀️" if solar_info['action'] == 'kick' else "  "
                comet_symbol = "☄️" if snapshot.n_active_comets > 0 else "  "
                print(f"  Step {step:3d}: Φ={phi:.4f} (σ={phi_std_so_far:.4f}), "
                      f"C={coherence:.3f} {action_symbol} {comet_symbol}")

        # Final statistics
        phis = np.array([s.phi for s in snapshots])
        coherences = np.array([s.coherence for s in snapshots])

        phi_mean = float(np.mean(phis))
        phi_std = float(np.std(phis))
        phi_min = float(np.min(phis))
        phi_max = float(np.max(phis))

        coherence_mean = float(np.mean(coherences))
        coherence_std = float(np.std(coherences))

        # Success evaluation
        breathing_threshold = 0.05  # Minimum variance to indicate breathing
        breathing_detected = phi_std > breathing_threshold
        phi_improvement = phi_mean - phi_baseline

        elapsed_time = time.time() - start_time

        # Print results
        if self.verbose:
            print(f"\n{'═' * 80}")
            print("RESULTS")
            print(f"{'═' * 80}")
            print(f"\n📈 Φ Statistics:")
            print(f"  Mean:     {phi_mean:.4f} (baseline: {phi_baseline:.4f})")
            print(f"  Std Dev:  {phi_std:.4f} {'✓' if phi_std > breathing_threshold else '✗'}")
            print(f"  Range:    [{phi_min:.4f}, {phi_max:.4f}]")
            print(f"  Δ from baseline: {phi_improvement:+.4f}")

            print(f"\n🌊 Coherence Statistics:")
            print(f"  Mean:     {coherence_mean:.3f}")
            print(f"  Std Dev:  {coherence_std:.3f}")

            print(f"\n☀️  Solar Driver:")
            solar_stats = solar_driver.get_statistics()
            print(f"  Total kicks: {solar_stats['total_kicks']}")
            print(f"  Kick events: {solar_stats['n_kick_events']}")

            print(f"\n☄️  Comet Injector:")
            comet_stats = comet_injector.get_statistics()
            print(f"  Comets created: {comet_stats['total_comets_created']}")
            print(f"  Comets expired: {comet_stats['total_comets_expired']}")

            print(f"\n{'─' * 80}")
            print("SUCCESS EVALUATION")
            print(f"{'─' * 80}")

            if breathing_detected and phi_improvement > 0:
                print("  ✓✓ HYPOTHESIS CONFIRMED!")
                print("     The system BREATHES: High Φ with oscillations (σ_Φ > 0)")
                print("     Crystal-Death Paradox RESOLVED.")
            elif breathing_detected:
                print("  ✓ Breathing detected, but Φ not improved")
            elif phi_improvement > 0:
                print("  ✓ Φ improved, but system not breathing (low variance)")
            else:
                print("  ✗ Hypothesis not confirmed")

            print(f"\n  Duration: {elapsed_time:.2f} seconds")

        # Compile result
        result = SolarEngineResult(
            n_steps=n_steps,
            duration_seconds=elapsed_time,
            phi_mean=phi_mean,
            phi_std=phi_std,
            phi_min=phi_min,
            phi_max=phi_max,
            coherence_mean=coherence_mean,
            coherence_std=coherence_std,
            solar_driver_stats=solar_driver.get_statistics(),
            comet_injector_stats=comet_injector.get_statistics(),
            breathing_detected=breathing_detected,
            phi_improvement=phi_improvement,
            snapshots=snapshots,
        )

        return result

    def save_results(
        self,
        result: SolarEngineResult,
        filename: str = "experiment_c_solar_engine_results.json"
    ) -> None:
        """Save results to JSON file"""
        output_path = os.path.join(self.output_dir, filename)

        results_dict = {
            'experiment': 'Experiment C - Solar Engine',
            'hypothesis': 'Active metastability maintenance enables high Φ with breathing dynamics',
            'n_steps': result.n_steps,
            'duration_seconds': result.duration_seconds,
            'phi_mean': result.phi_mean,
            'phi_std': result.phi_std,
            'phi_min': result.phi_min,
            'phi_max': result.phi_max,
            'coherence_mean': result.coherence_mean,
            'coherence_std': result.coherence_std,
            'solar_driver_stats': result.solar_driver_stats,
            'comet_injector_stats': result.comet_injector_stats,
            'breathing_detected': result.breathing_detected,
            'phi_improvement': result.phi_improvement,
            'snapshots': [asdict(s) for s in result.snapshots],
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
        description="Experiment C: Solar Engine - Breaking the Crystal-Death Paradox"
    )

    parser.add_argument(
        '--config',
        type=str,
        default='v9_alpha/config/lantern_hub.yaml',
        help='Path to lantern_hub.yaml configuration'
    )

    parser.add_argument(
        '--steps',
        type=int,
        default=50,
        help='Number of simulation steps'
    )

    parser.add_argument(
        '--solar-threshold',
        type=float,
        default=0.85,
        help='Coherence threshold for Solar Driver kicks'
    )

    parser.add_argument(
        '--kick-amplitude',
        type=float,
        default=0.5,
        help='Phase kick amplitude (radians)'
    )

    parser.add_argument(
        '--comet-probability',
        type=float,
        default=0.15,
        help='Probability of comet injection per step'
    )

    parser.add_argument(
        '--comet-lifetime',
        type=int,
        default=5,
        help='Comet connection lifetime (steps)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='experiment_c_results',
        help='Output directory for results'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress verbose output'
    )

    args = parser.parse_args()

    # Run experiment
    validator = SolarEngineValidator(
        config_path=args.config,
        output_dir=args.output_dir,
        verbose=not args.quiet,
    )

    result = validator.run_solar_engine_experiment(
        n_steps=args.steps,
        solar_coherence_threshold=args.solar_threshold,
        solar_kick_amplitude=args.kick_amplitude,
        comet_injection_probability=args.comet_probability,
        comet_lifetime=args.comet_lifetime,
    )

    # Save results
    validator.save_results(result)

    print("\n" + "=" * 80)
    print("EXPERIMENT C COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
