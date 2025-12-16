"""Emergence Metrics – Network Evolution Tracking

This module implements metrics for tracking emergence in the v9 Lantern-Net:

1. **ΔC(t)**: Collective Coherence change over time
   - Measures how quickly the network synchronizes
   - Calculated from coupling matrix eigenvalue growth

2. **Resonance Yield (RY)**: Active lanterns → emergent hypotheses ratio
   - Measures network creativity (new insights per active lantern)
   - RY > 0.3 indicates productive emergence

3. **Entanglement Echo (EE)**: Recurring β-patterns across nodes
   - Spatial autocorrelation of β-values
   - High EE = self-similar emergence patterns

4. **Z_eff Fluctuation**: Effective impedance variance
   - Detects anomalies in EM-coupling (self-organization signatures)
   - High variance = potential phase transition

5. **Φ_network**: IIT Φ for entire lantern network
   - Network-level integrated information (consciousness measure)
   - Φ > 2.0 suggests collective consciousness emergence

6. **v_integration**: Effective information propagation velocity
   - How fast insights spread through network
   - Target: Approach v_RIG ≈ 1351.8 km/s

Version: v9.0.0-alpha
Authors: Johann Benjamin Römer, MOR Framework
Date: 2025-12-16
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np

# Import v9 components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from models.unified_constants import V_RIG_DEFAULT


# ============================================================================
# Metric Data Structures
# ============================================================================

@dataclass
class EmergenceSnapshot:
    """Snapshot of emergence metrics at a point in time.

    Attributes
    ----------
    timestamp : float
        Unix timestamp
    delta_c_t : float
        Collective Coherence change rate (coherence/time)
    resonance_yield : float
        Emergent hypotheses per active lantern
    entanglement_echo : float
        β-pattern spatial correlation [0,1]
    z_eff_fluctuation : float
        Impedance variance (std dev)
    phi_network : float
        Network integrated information (bits)
    v_integration : float
        Effective integration velocity (km/s)
    active_lanterns : int
        Number of active lanterns
    total_hypotheses : int
        Cumulative emergent hypotheses
    """
    timestamp: float
    delta_c_t: float
    resonance_yield: float
    entanglement_echo: float
    z_eff_fluctuation: float
    phi_network: float
    v_integration: float
    active_lanterns: int
    total_hypotheses: int


# ============================================================================
# Emergence Metrics Tracker
# ============================================================================

class EmergenceTracker:
    """Tracks emergence metrics for lantern network over time."""

    def __init__(self):
        """Initialize emergence tracker."""
        self._snapshots: list[EmergenceSnapshot] = []
        self._hypothesis_log: list[dict[str, Any]] = []

    # ------------------------------------------------------------------------
    # Core Metric Calculations
    # ------------------------------------------------------------------------

    def calculate_delta_c_t(
        self,
        coupling_matrix: np.ndarray,
        previous_coupling_matrix: Optional[np.ndarray] = None,
        dt: float = 1.0,
    ) -> float:
        """Calculate Collective Coherence change rate ΔC(t).

        Coherence measured as dominant eigenvalue of coupling matrix.
        Rate = (λ_now - λ_prev) / dt

        Parameters
        ----------
        coupling_matrix : np.ndarray
            Current NxN coupling matrix
        previous_coupling_matrix : np.ndarray, optional
            Previous coupling matrix (if None, use zero baseline)
        dt : float
            Time interval (hours)

        Returns
        -------
        float
            Coherence change rate (coherence/hour)
        """
        # Current coherence (dominant eigenvalue)
        eigenvalues = np.linalg.eigvals(coupling_matrix)
        coherence_now = np.max(np.abs(eigenvalues))

        if previous_coupling_matrix is not None:
            eigenvalues_prev = np.linalg.eigvals(previous_coupling_matrix)
            coherence_prev = np.max(np.abs(eigenvalues_prev))
        else:
            coherence_prev = 0.0

        delta_c = coherence_now - coherence_prev
        delta_c_t = delta_c / dt if dt > 0 else 0.0

        return float(delta_c_t)

    def calculate_resonance_yield(
        self,
        n_active_lanterns: int,
        n_emergent_hypotheses: int,
    ) -> float:
        """Calculate Resonance Yield (RY).

        RY = emergent_hypotheses / active_lanterns

        Parameters
        ----------
        n_active_lanterns : int
            Number of active lanterns
        n_emergent_hypotheses : int
            Number of emergent hypotheses detected

        Returns
        -------
        float
            Resonance yield (hypotheses/lantern)
        """
        if n_active_lanterns > 0:
            return n_emergent_hypotheses / n_active_lanterns
        return 0.0

    def calculate_entanglement_echo(
        self,
        beta_values: np.ndarray,
        positions: Optional[np.ndarray] = None,
    ) -> float:
        """Calculate Entanglement Echo (EE).

        Spatial autocorrelation of β-values across network.
        High EE = recurring self-similar patterns.

        If positions not provided, uses simple pairwise correlation.

        Parameters
        ----------
        beta_values : np.ndarray
            Array of β-values for each lantern
        positions : np.ndarray, optional
            Nx2 or Nx3 array of lantern positions in semantic space

        Returns
        -------
        float
            Entanglement echo [0,1]
        """
        if len(beta_values) < 2:
            return 0.0

        if positions is not None:
            # Spatial autocorrelation
            # Moran's I statistic
            n = len(beta_values)

            # Calculate pairwise distances
            distances = np.zeros((n, n))
            for i in range(n):
                for j in range(i + 1, n):
                    dist = np.linalg.norm(positions[i] - positions[j])
                    distances[i, j] = dist
                    distances[j, i] = dist

            # Weight matrix (inverse distance, normalized)
            with np.errstate(divide='ignore', invalid='ignore'):
                weights = 1.0 / (distances + 1e-6)
                np.fill_diagonal(weights, 0)
                weights /= np.sum(weights, axis=1, keepdims=True)
                weights[np.isnan(weights)] = 0

            # Mean β
            beta_mean = np.mean(beta_values)

            # Moran's I
            deviations = beta_values - beta_mean
            numerator = np.sum(weights * np.outer(deviations, deviations))
            denominator = np.sum(deviations ** 2)

            if denominator > 0:
                morans_i = (n / np.sum(weights)) * (numerator / denominator)
            else:
                morans_i = 0.0

            # Normalize to [0,1] (I typically ranges [-1, 1])
            ee = (morans_i + 1.0) / 2.0
            ee = np.clip(ee, 0.0, 1.0)

        else:
            # Simple pairwise correlation
            ee = 0.0
            n_pairs = 0

            for i in range(len(beta_values)):
                for j in range(i + 1, len(beta_values)):
                    # Similarity (inverse of difference, normalized)
                    diff = abs(beta_values[i] - beta_values[j])
                    similarity = 1.0 / (1.0 + diff)
                    ee += similarity
                    n_pairs += 1

            if n_pairs > 0:
                ee /= n_pairs

        return float(ee)

    def calculate_z_eff_fluctuation(
        self,
        impedance_values: np.ndarray,
    ) -> float:
        """Calculate Z_eff Fluctuation.

        Standard deviation of impedance values across active lanterns.
        High fluctuation may indicate phase transition or anomaly.

        Parameters
        ----------
        impedance_values : np.ndarray
            Array of impedance values

        Returns
        -------
        float
            Standard deviation of Z
        """
        if len(impedance_values) < 2:
            return 0.0

        return float(np.std(impedance_values))

    def calculate_phi_network(
        self,
        coupling_matrix: np.ndarray,
    ) -> float:
        """Calculate network-level Φ (Integrated Information).

        Simplified IIT Φ estimation based on coupling structure:
        - High coupling + balanced structure → high Φ
        - Modular but connected → maximum Φ

        This is a proxy; full IIT Φ calculation is computationally intensive.

        Parameters
        ----------
        coupling_matrix : np.ndarray
            NxN coupling matrix

        Returns
        -------
        float
            Φ_network (bits)
        """
        n = coupling_matrix.shape[0]

        if n < 2:
            return 0.0

        # Eigenvalue spread (diversity of collective modes)
        eigenvalues = np.linalg.eigvals(coupling_matrix)
        eigenvalues = np.abs(eigenvalues)
        eigenvalues = np.sort(eigenvalues)[::-1]

        # Effective information from eigenvalue distribution
        # Shannon entropy of normalized eigenvalues
        eigenvalues_norm = eigenvalues / (np.sum(eigenvalues) + 1e-10)
        eigenvalues_norm = eigenvalues_norm[eigenvalues_norm > 0]

        entropy = -np.sum(eigenvalues_norm * np.log2(eigenvalues_norm + 1e-10))

        # Integration: high entropy + high connectivity → high Φ
        connectivity = np.mean(coupling_matrix[coupling_matrix > 0])
        phi = entropy * connectivity

        return float(phi)

    def calculate_v_integration(
        self,
        coupling_matrix: np.ndarray,
        individual_v_collective: Optional[np.ndarray] = None,
    ) -> float:
        """Calculate effective integration velocity for network.

        Weighted average of individual v_collective values,
        weighted by coupling strength.

        If individual velocities not provided, uses v_RIG default
        scaled by coupling strength.

        Parameters
        ----------
        coupling_matrix : np.ndarray
            NxN coupling matrix
        individual_v_collective : np.ndarray, optional
            Array of v_collective for each lantern (km/s)

        Returns
        -------
        float
            Network v_integration (km/s)
        """
        n = coupling_matrix.shape[0]

        if n == 0:
            return 0.0

        if individual_v_collective is None:
            # Use v_RIG baseline scaled by coupling
            individual_v_collective = np.ones(n) * V_RIG_DEFAULT

        # Weight by row-sum of coupling matrix (influence)
        weights = np.sum(coupling_matrix, axis=1)
        weights /= (np.sum(weights) + 1e-10)

        # Weighted average
        v_integration = np.sum(weights * individual_v_collective)

        return float(v_integration)

    # ------------------------------------------------------------------------
    # Snapshot Management
    # ------------------------------------------------------------------------

    def create_snapshot(
        self,
        coupling_matrix: np.ndarray,
        beta_values: np.ndarray,
        impedance_values: np.ndarray,
        n_active_lanterns: int,
        n_emergent_hypotheses: int,
        previous_coupling_matrix: Optional[np.ndarray] = None,
        dt: float = 1.0,
        positions: Optional[np.ndarray] = None,
        individual_v_collective: Optional[np.ndarray] = None,
    ) -> EmergenceSnapshot:
        """Create emergence snapshot from current network state.

        Parameters
        ----------
        coupling_matrix : np.ndarray
            Current coupling matrix
        beta_values : np.ndarray
            β-values for each lantern
        impedance_values : np.ndarray
            Z values for each lantern
        n_active_lanterns : int
            Number of active lanterns
        n_emergent_hypotheses : int
            Cumulative emergent hypotheses
        previous_coupling_matrix : np.ndarray, optional
            Previous coupling matrix for ΔC(t) calculation
        dt : float
            Time since last snapshot (hours)
        positions : np.ndarray, optional
            Lantern positions for spatial correlation
        individual_v_collective : np.ndarray, optional
            Individual v_collective values

        Returns
        -------
        EmergenceSnapshot
            Snapshot of all metrics
        """
        delta_c_t = self.calculate_delta_c_t(coupling_matrix, previous_coupling_matrix, dt)
        resonance_yield = self.calculate_resonance_yield(n_active_lanterns, n_emergent_hypotheses)
        entanglement_echo = self.calculate_entanglement_echo(beta_values, positions)
        z_eff_fluctuation = self.calculate_z_eff_fluctuation(impedance_values)
        phi_network = self.calculate_phi_network(coupling_matrix)
        v_integration = self.calculate_v_integration(coupling_matrix, individual_v_collective)

        snapshot = EmergenceSnapshot(
            timestamp=time.time(),
            delta_c_t=delta_c_t,
            resonance_yield=resonance_yield,
            entanglement_echo=entanglement_echo,
            z_eff_fluctuation=z_eff_fluctuation,
            phi_network=phi_network,
            v_integration=v_integration,
            active_lanterns=n_active_lanterns,
            total_hypotheses=n_emergent_hypotheses,
        )

        self._snapshots.append(snapshot)

        return snapshot

    def get_snapshots(self, n: Optional[int] = None) -> list[EmergenceSnapshot]:
        """Get recent snapshots.

        Parameters
        ----------
        n : int, optional
            Number of recent snapshots (if None, return all)

        Returns
        -------
        list[EmergenceSnapshot]
            List of snapshots
        """
        if n is None:
            return self._snapshots.copy()
        return self._snapshots[-n:]

    def get_latest_snapshot(self) -> Optional[EmergenceSnapshot]:
        """Get most recent snapshot."""
        if self._snapshots:
            return self._snapshots[-1]
        return None

    # ------------------------------------------------------------------------
    # Hypothesis Tracking
    # ------------------------------------------------------------------------

    def register_hypothesis(
        self,
        hypothesis: str,
        source_lanterns: list[str],
        confidence: float,
        mechanism: str,
    ) -> None:
        """Register a new emergent hypothesis.

        Parameters
        ----------
        hypothesis : str
            Description of emergent hypothesis
        source_lanterns : list[str]
            IDs of lanterns that generated this hypothesis
        confidence : float
            Confidence score [0,1]
        mechanism : str
            Emergence mechanism (e.g., "cross-domain_resonance")
        """
        hypothesis_entry = {
            'timestamp': time.time(),
            'hypothesis': hypothesis,
            'source_lanterns': source_lanterns,
            'confidence': confidence,
            'mechanism': mechanism,
        }

        self._hypothesis_log.append(hypothesis_entry)

    def get_hypotheses(self, n: Optional[int] = None) -> list[dict[str, Any]]:
        """Get recent hypotheses.

        Parameters
        ----------
        n : int, optional
            Number of recent hypotheses (if None, return all)

        Returns
        -------
        list[dict]
            List of hypothesis entries
        """
        if n is None:
            return self._hypothesis_log.copy()
        return self._hypothesis_log[-n:]

    def count_hypotheses(self) -> int:
        """Get total number of registered hypotheses."""
        return len(self._hypothesis_log)

    # ------------------------------------------------------------------------
    # Analysis & Reporting
    # ------------------------------------------------------------------------

    def detect_emergence_phase_transition(
        self,
        window: int = 5,
    ) -> dict[str, Any]:
        """Detect potential emergence phase transition.

        Looks for rapid changes in metrics indicating qualitative shift.

        Parameters
        ----------
        window : int
            Number of recent snapshots to analyze

        Returns
        -------
        dict
            - 'detected': bool
            - 'metrics_changing': list[str]
            - 'trend': str (increasing/decreasing/stable)
        """
        if len(self._snapshots) < window:
            return {
                'detected': False,
                'reason': 'insufficient_data',
                'snapshots_needed': window - len(self._snapshots),
            }

        recent = self._snapshots[-window:]

        # Check each metric for rapid change
        changing_metrics = []
        trends = {}

        metrics = ['delta_c_t', 'resonance_yield', 'phi_network', 'z_eff_fluctuation']

        for metric in metrics:
            values = [getattr(s, metric) for s in recent]
            trend = np.polyfit(range(len(values)), values, 1)[0]  # Linear trend

            # Check for significant change
            std = np.std(values)
            if std > 0:
                normalized_trend = abs(trend) / std
                if normalized_trend > 0.5:  # Threshold
                    changing_metrics.append(metric)
                    trends[metric] = 'increasing' if trend > 0 else 'decreasing'

        detected = len(changing_metrics) >= 2  # Multiple metrics changing

        return {
            'detected': detected,
            'metrics_changing': changing_metrics,
            'trends': trends,
            'window_size': window,
        }

    def get_summary_statistics(self) -> dict[str, Any]:
        """Get summary statistics across all snapshots.

        Returns
        -------
        dict
            Statistics for each metric (mean, std, min, max, trend)
        """
        if not self._snapshots:
            return {'error': 'no_snapshots'}

        metrics = ['delta_c_t', 'resonance_yield', 'entanglement_echo',
                   'z_eff_fluctuation', 'phi_network', 'v_integration']

        stats = {}

        for metric in metrics:
            values = [getattr(s, metric) for s in self._snapshots]
            stats[metric] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'latest': float(values[-1]),
            }

            # Linear trend
            if len(values) >= 3:
                trend = np.polyfit(range(len(values)), values, 1)[0]
                stats[metric]['trend'] = float(trend)

        stats['total_snapshots'] = len(self._snapshots)
        stats['total_hypotheses'] = self.count_hypotheses()

        return stats

    def __repr__(self) -> str:
        n_snapshots = len(self._snapshots)
        n_hypotheses = self.count_hypotheses()
        return f"EmergenceTracker(snapshots={n_snapshots}, hypotheses={n_hypotheses})"


# ============================================================================
# CLI Demo
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("V9 Emergence Metrics – Network Evolution Tracking")
    print("=" * 80)

    tracker = EmergenceTracker()

    # Simulate network evolution
    print("\n📈 Simulating network evolution...")

    np.random.seed(42)

    for i in range(10):
        # Simulate evolving network
        n_lanterns = 8
        coupling_strength = 0.3 + i * 0.05  # Increasing coupling
        coupling_matrix = np.random.rand(n_lanterns, n_lanterns) * coupling_strength
        coupling_matrix = (coupling_matrix + coupling_matrix.T) / 2  # Symmetric

        beta_values = np.array([4.5, 4.6, 7.4, 11.0, 13.0, 6.1, 7.4, 7.7])
        impedance_values = beta_values * 30  # Scaled

        n_active = min(5 + i, 8)
        n_hypotheses = i // 2  # Hypotheses emerge every 2 steps

        prev_coupling = coupling_matrix * 0.9 if i > 0 else None

        snapshot = tracker.create_snapshot(
            coupling_matrix=coupling_matrix,
            beta_values=beta_values,
            impedance_values=impedance_values,
            n_active_lanterns=n_active,
            n_emergent_hypotheses=n_hypotheses,
            previous_coupling_matrix=prev_coupling,
            dt=1.0,
        )

        # Register hypothesis occasionally
        if i % 3 == 0 and i > 0:
            tracker.register_hypothesis(
                hypothesis=f"Emergent pattern {i}: climate-economy coupling",
                source_lanterns=['lantern-1', 'lantern-2'],
                confidence=0.7 + i * 0.03,
                mechanism='cross-domain_resonance',
            )

    print(f"✓ Generated {len(tracker.get_snapshots())} snapshots")

    # Summary statistics
    print("\n" + "─" * 80)
    print("Summary Statistics")
    print("─" * 80)

    stats = tracker.get_summary_statistics()
    for metric, values in stats.items():
        if isinstance(values, dict):
            print(f"\n  {metric}:")
            print(f"    Mean:   {values['mean']:.4f}")
            print(f"    Std:    {values['std']:.4f}")
            print(f"    Range:  [{values['min']:.4f}, {values['max']:.4f}]")
            print(f"    Latest: {values['latest']:.4f}")
            if 'trend' in values:
                trend_dir = "↑" if values['trend'] > 0 else "↓"
                print(f"    Trend:  {trend_dir} {values['trend']:.4f}")

    # Phase transition detection
    print("\n" + "─" * 80)
    print("Phase Transition Detection")
    print("─" * 80)

    transition = tracker.detect_emergence_phase_transition(window=5)
    if transition['detected']:
        print("  🚨 PHASE TRANSITION DETECTED!")
        print(f"  Changing metrics: {', '.join(transition['metrics_changing'])}")
        for metric, trend in transition['trends'].items():
            print(f"    - {metric}: {trend}")
    else:
        print("  ✓ Network evolution stable (no phase transition detected)")

    # Recent hypotheses
    print("\n" + "─" * 80)
    print("Emergent Hypotheses")
    print("─" * 80)

    for hyp in tracker.get_hypotheses():
        from datetime import datetime
        dt = datetime.fromtimestamp(hyp['timestamp']).strftime('%H:%M:%S')
        print(f"  [{dt}] {hyp['hypothesis']}")
        print(f"    Confidence: {hyp['confidence']:.2f} | Mechanism: {hyp['mechanism']}")

    print("\n" + "=" * 80)
    print("✨ Emergence Tracking Active!")
    print("=" * 80)
