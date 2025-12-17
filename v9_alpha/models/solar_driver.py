"""Solar Driver – Active Metastability Maintenance.

This module extracts the SolarDriver from the Experiment C demo so that
metastability kicks are reusable across the v9_alpha package. The driver
monitors local coherence and injects phase perturbations whenever
σ(β(R-Θ)) pushes the network toward crystallization (coherence → 1).
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple

import numpy as np


def phase_coherence(phases: np.ndarray) -> float:
    """Compute global phase coherence |⟨e^{iθ}⟩| for the network."""
    if len(phases) == 0:
        return 0.0
    return float(np.abs(np.mean(np.exp(1j * phases))))


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
            neighbors = np.where(coupling_matrix[i] > 0)[0]

            if len(neighbors) == 0:
                local_coherences[i] = 0.0
                continue

            phase_diffs = phases[neighbors] - phases[i]
            phasor = np.mean(np.exp(1j * phase_diffs))
            local_coherences[i] = np.abs(phasor)

        global_coherence = float(np.mean(local_coherences))
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

        if kick_indices is None:
            kick_indices = np.where(local_coherences > self.coherence_threshold)[0]

        if len(kick_indices) == 0:
            return phases_kicked

        if self.kick_strategy == "aggressive":
            kicks = np.random.uniform(
                -self.kick_amplitude,
                self.kick_amplitude,
                len(kick_indices)
            )
        elif self.kick_strategy == "gentle":
            kicks = np.random.normal(0, self.kick_amplitude / 2, len(kick_indices))
        else:
            kicks = np.zeros(len(kick_indices))

        phases_kicked[kick_indices] += kicks
        phases_kicked = np.arctan2(np.sin(phases_kicked), np.cos(phases_kicked))

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
            em_coherence: EM field coherence (if provided, use instead)

        Returns:
            (modified_phases, step_info)
        """
        if em_coherence is not None:
            global_coherence = em_coherence
            local_coherences = np.ones(len(phases)) * em_coherence
        else:
            global_coherence, local_coherences = self.calculate_local_coherence(
                phases, coupling_matrix
            )

        kick_needed = global_coherence > self.coherence_threshold

        if kick_needed:
            phases_new = self.inject_phase_kick(phases, local_coherences)
            action = "kick"
        else:
            phases_new = phases
            action = "none"

        step_info = {
            'global_coherence': float(global_coherence),
            'max_local_coherence': float(np.max(local_coherences) if len(local_coherences) else 0.0),
            'action': action,
            'n_nodes_kicked': int(np.sum(local_coherences > self.coherence_threshold)),
        }

        return phases_new, step_info

    def get_statistics(self) -> Dict:
        """Get Solar Driver statistics."""
        return {
            'total_kicks': self.n_kicks,
            'n_kick_events': len(self.kick_history),
            'kick_rate': self.n_kicks / max(1, len(self.kick_history)),
        }


__all__ = ["SolarDriver", "phase_coherence"]
