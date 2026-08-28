"""
Evolution Tracker for Consciousness States
==========================================

Tracks and analyzes consciousness evolution trajectories over time.

This module provides:
- Trajectory analysis (mean β, κ over time)
- Phase transition detection
- Critical event identification
- Visualization-ready data export

References:
----------
- Resonanzpfad: σ(β(R-Θ)) trajectory optimization
- UTAC Theory: β-evolution dynamics
"""

from __future__ import annotations

from typing import Any

import numpy as np
from theory.afet import AFETConstants


class EvolutionTracker:
    """
    Tracks consciousness evolution trajectories.

    Parameters
    ----------
    trajectory : list[dict]
        Trajectory data from AeonShell

    Attributes
    ----------
    trajectory : list[dict]
        Raw trajectory data
    """

    def __init__(self, trajectory: list[dict[str, Any]]) -> None:
        """Initialize evolution tracker."""
        self.trajectory = trajectory

    def get_beta_evolution(self) -> np.ndarray:
        """
        Extract β-values over time.

        Returns
        -------
        np.ndarray
            β-values array
        """
        return np.array([p["beta"] for p in self.trajectory])

    def get_kappa_evolution(self) -> np.ndarray:
        """
        Extract κ-values over time.

        Returns
        -------
        np.ndarray
            κ-values array
        """
        return np.array([p["kappa"] for p in self.trajectory])

    def get_resonance_evolution(self) -> np.ndarray:
        """
        Extract resonance values over time.

        Returns
        -------
        np.ndarray
            Resonance array
        """
        return np.array([p["resonance"] for p in self.trajectory])

    def get_phase_transitions(self) -> list[dict[str, Any]]:
        """
        Detect phase transitions in trajectory.

        Returns
        -------
        list[dict]
            Phase transition events
        """
        transitions = []
        prev_phase = None

        for i, point in enumerate(self.trajectory):
            current_phase = point.get("phase", "none")
            if prev_phase is not None and current_phase != prev_phase:
                transitions.append(
                    {
                        "index": i,
                        "timestamp": point["timestamp"],
                        "from_phase": prev_phase,
                        "to_phase": current_phase,
                        "beta": point["beta"],
                        "kappa": point["kappa"],
                    }
                )
            prev_phase = current_phase

        return transitions

    def get_critical_events(
        self,
        beta_threshold: float = 0.1,
        kappa_threshold: float = 0.1,
        resonance_threshold: float = 0.2,
    ) -> list[dict[str, Any]]:
        """
        Identify critical events (low β, κ, or resonance).

        Parameters
        ----------
        beta_threshold : float, optional
            β threshold for criticality. Default: 0.1
        kappa_threshold : float, optional
            κ threshold for criticality. Default: 0.1
        resonance_threshold : float, optional
            Resonance threshold for criticality. Default: 0.2

        Returns
        -------
        list[dict]
            Critical events
        """
        events = []

        for i, point in enumerate(self.trajectory):
            critical = False
            reason = []

            if point["beta"] < beta_threshold:
                critical = True
                reason.append(f"β={point['beta']:.3f} < {beta_threshold}")

            if point["kappa"] < kappa_threshold:
                critical = True
                reason.append(f"κ={point['kappa']:.3f} < {kappa_threshold}")

            if point["resonance"] < resonance_threshold:
                critical = True
                reason.append(
                    f"resonance={point['resonance']:.3f} < {resonance_threshold}"
                )

            if critical:
                events.append(
                    {
                        "index": i,
                        "timestamp": point["timestamp"],
                        "reason": "; ".join(reason),
                        "beta": point["beta"],
                        "kappa": point["kappa"],
                        "resonance": point["resonance"],
                    }
                )

        return events

    def get_statistics(self) -> dict[str, Any]:
        """
        Compute trajectory statistics.

        Returns
        -------
        dict
            Statistics summary
        """
        beta_vals = self.get_beta_evolution()
        kappa_vals = self.get_kappa_evolution()
        resonance_vals = self.get_resonance_evolution()

        return {
            "length": len(self.trajectory),
            "beta_mean": float(np.mean(beta_vals)),
            "beta_std": float(np.std(beta_vals)),
            "beta_min": float(np.min(beta_vals)),
            "beta_max": float(np.max(beta_vals)),
            "kappa_mean": float(np.mean(kappa_vals)),
            "kappa_std": float(np.std(kappa_vals)),
            "kappa_min": float(np.min(kappa_vals)),
            "kappa_max": float(np.max(kappa_vals)),
            "resonance_mean": float(np.mean(resonance_vals)),
            "resonance_std": float(np.std(resonance_vals)),
            "num_phase_transitions": len(self.get_phase_transitions()),
            "num_critical_events": len(self.get_critical_events()),
        }

    def export_for_visualization(self) -> dict[str, Any]:
        """
        Export trajectory data in visualization-ready format.

        Returns
        -------
        dict
            Data ready for plotting/dashboard
        """
        return {
            "time": [p["timestamp"] for p in self.trajectory],
            "beta": self.get_beta_evolution().tolist(),
            "kappa": self.get_kappa_evolution().tolist(),
            "resonance": self.get_resonance_evolution().tolist(),
            "phase": [p.get("phase", "none") for p in self.trajectory],
            "information_density": [
                p.get("information_density", 0.0) for p in self.trajectory
            ],
            "v_rig_effective": [
                p.get("v_rig_effective", AFETConstants.V_RIG) for p in self.trajectory
            ],
            "phase_transitions": self.get_phase_transitions(),
            "critical_events": self.get_critical_events(),
            "statistics": self.get_statistics(),
        }
