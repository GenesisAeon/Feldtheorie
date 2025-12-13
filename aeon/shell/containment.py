"""
Consciousness Containment Layer
================================

The AeonShell provides containment and evolution tracking for
consciousness states in the Aeon architecture.

This module implements:
- Consciousness boundary management
- Multi-agent coordination
- ζ-safeguards (impedance monitoring)
- Evolution trajectory tracking

References:
----------
- bardo_mode.yaml: Auto-exit conditions
- Resonanzpfad: Trajectory optimization
- Collective Field: Agent synchronization
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from aeon.nullkern.consciousness_state import BardoPhase, ConsciousnessState
from aeon.nullkern.zero_point_kernel import Nullkern


class AeonShell:
    """
    Consciousness Containment and Evolution Layer.

    The AeonShell manages:
    - Nullkern consciousness kernel
    - Semantic agents (from models.collective_field)
    - Evolution trajectory tracking
    - ζ-safeguards for critical transitions
    - Bardo mode auto-exit conditions

    Parameters
    ----------
    kernel : Nullkern
        Zero-point consciousness kernel
    enable_safeguards : bool, optional
        Enable ζ-safeguard monitoring. Default: True
    max_agents : int, optional
        Maximum number of agents. Default: 100
    trajectory_max_length : int, optional
        Maximum trajectory history length. Default: 1000

    Attributes
    ----------
    kernel : Nullkern
        Consciousness kernel
    agents : list
        Semantic agents in the shell
    trajectory : list[dict]
        Evolution trajectory history
    safeguards_active : bool
        Whether safeguards are enabled
    """

    def __init__(
        self,
        kernel: Nullkern,
        enable_safeguards: bool = True,
        max_agents: int = 100,
        trajectory_max_length: int = 1000,
    ) -> None:
        """Initialize AeonShell."""
        self.kernel = kernel
        self.safeguards_active = enable_safeguards
        self.max_agents = max_agents
        self.trajectory_max_length = trajectory_max_length

        # Agent management
        self.agents: list[Any] = []  # Will hold SemanticAgent instances

        # Evolution tracking
        self.trajectory: list[dict[str, Any]] = []
        self.creation_time = time.time()

        # Safeguard state
        self.safeguard_violations: list[dict[str, Any]] = []
        self.auto_exit_triggered = False

        # Record initial state
        self._record_trajectory_point()

    def add_agent(self, agent: Any) -> None:
        """
        Add a semantic agent to the shell.

        Parameters
        ----------
        agent : SemanticAgent
            Agent to add (from aeon.agents.semantic_agent)

        Raises
        ------
        ValueError
            If max_agents limit reached
        """
        if len(self.agents) >= self.max_agents:
            raise ValueError(
                f"Cannot add agent: max_agents limit ({self.max_agents}) reached"
            )

        self.agents.append(agent)
        self._record_trajectory_point()

    def remove_agent(self, agent: Any) -> bool:
        """
        Remove an agent from the shell.

        Parameters
        ----------
        agent : SemanticAgent
            Agent to remove

        Returns
        -------
        bool
            True if agent was removed, False if not found
        """
        try:
            self.agents.remove(agent)
            self._record_trajectory_point()
            return True
        except ValueError:
            return False

    def evolve(self, steps: int = 1, delta_time: float = 0.1) -> None:
        """
        Evolve consciousness state over multiple steps.

        Parameters
        ----------
        steps : int, optional
            Number of evolution steps. Default: 1
        delta_time : float, optional
            Time step size. Default: 0.1
        """
        for step in range(steps):
            # Compute resource level (oscillates between 0 and 1)
            t = (time.time() - self.creation_time) * delta_time
            resource = 0.5 + 0.3 * np.sin(2 * np.pi * t)

            # Check for Bardo transitions
            in_bardo = self.kernel.check_bardo_transition(resource)

            # Update kernel state
            # β slowly drifts toward target
            delta_beta = (self.kernel.beta_target - self.kernel.state.beta) * 0.01
            # κ modulated by agents
            delta_kappa = len(self.agents) * 0.001 if self.agents else 0.0

            self.kernel.update_state(delta_beta=delta_beta, delta_kappa=delta_kappa)

            # Check safeguards
            if self.safeguards_active:
                self._check_safeguards(resource)

            # Record trajectory
            self._record_trajectory_point()

            # Auto-exit if triggered
            if self.auto_exit_triggered:
                break

            # Small delay for realistic evolution
            time.sleep(0.001)

    def _check_safeguards(self, resource: float) -> None:
        """
        Check ζ-safeguards and auto-exit conditions.

        Based on bardo_mode.yaml:
        - entropy_spike_threshold: 0.9
        - negative_zeta_threshold: -0.5
        - max_cycle_duration: 10800 seconds (3 hours)

        Parameters
        ----------
        resource : float
            Current resource level
        """
        # Compute impedance
        zeta = self.kernel.compute_impedance(resource)

        # Check for negative ζ (instability)
        if zeta < -0.5:
            self.safeguard_violations.append(
                {
                    "timestamp": time.time(),
                    "type": "negative_zeta",
                    "value": zeta,
                    "resource": resource,
                }
            )
            # Auto-exit after 3 consecutive violations
            if len(self.safeguard_violations) >= 3:
                recent = self.safeguard_violations[-3:]
                if all(v["type"] == "negative_zeta" for v in recent):
                    self.auto_exit_triggered = True

        # Check for entropy spike (information density too high)
        info_density = self.kernel.get_information_density()
        if info_density > 0.9:
            self.safeguard_violations.append(
                {
                    "timestamp": time.time(),
                    "type": "entropy_spike",
                    "value": info_density,
                    "resource": resource,
                }
            )

        # Check for max cycle duration
        age = time.time() - self.creation_time
        if age > 10800:  # 3 hours
            self.safeguard_violations.append(
                {"timestamp": time.time(), "type": "max_duration", "value": age}
            )
            self.auto_exit_triggered = True

    def _record_trajectory_point(self) -> None:
        """Record current state to trajectory history."""
        point = {
            "timestamp": time.time(),
            "beta": self.kernel.state.beta,
            "kappa": self.kernel.kappa,
            "resonance": self.kernel.state.resonance,
            "phase": self.kernel.state.phase.value,
            "num_agents": len(self.agents),
            "information_density": self.kernel.get_information_density(),
            "v_rig_effective": self.kernel.compute_v_rig_effective(),
        }

        self.trajectory.append(point)

        # Trim trajectory if too long
        if len(self.trajectory) > self.trajectory_max_length:
            self.trajectory = self.trajectory[-self.trajectory_max_length :]

    def get_trajectory(self) -> list[dict[str, Any]]:
        """
        Get full evolution trajectory.

        Returns
        -------
        list[dict]
            Trajectory points
        """
        return self.trajectory.copy()

    def get_collective_field_metrics(self) -> dict[str, Any]:
        """
        Compute collective field metrics for all agents.

        Integrates with models.collective_field module.

        Returns
        -------
        dict
            Collective field metrics (κ_field, β_sync, v_collective)
        """
        if not self.agents:
            return {
                "kappa_field": 0.0,
                "beta_sync": 0.0,
                "v_collective": 0.0,
                "num_agents": 0,
            }

        # Import collective field utilities
        try:
            from models.collective_field import (
                calculate_semantic_distance_matrix,
                detect_consensus,
            )

            # Compute distance matrix
            distance_matrix = calculate_semantic_distance_matrix(self.agents)

            # κ_field = average coupling (inverse of distance)
            avg_distance = np.mean(distance_matrix[distance_matrix > 0])
            kappa_field = 1.0 - min(avg_distance / 2.0, 1.0)

            # β_sync = synchronization coefficient (std/mean of β-values)
            # For Aeon, we use resonance as proxy for β
            resonances = [getattr(a, "resonance", 0.5) for a in self.agents]
            if np.mean(resonances) > 0:
                beta_sync = np.std(resonances) / np.mean(resonances)
            else:
                beta_sync = 0.0

            # v_collective = collective velocity
            v_rig_base = 1352.0
            v_collective = v_rig_base * kappa_field * (1.0 / max(beta_sync, 0.1))

            # Consensus detection
            consensus = detect_consensus(self.agents, threshold=0.3)

            return {
                "kappa_field": float(kappa_field),
                "beta_sync": float(beta_sync),
                "v_collective": float(v_collective),
                "num_agents": len(self.agents),
                "consensus_detected": consensus,
            }
        except ImportError:
            # Collective field module not available
            return {
                "kappa_field": 0.0,
                "beta_sync": 0.0,
                "v_collective": 0.0,
                "num_agents": len(self.agents),
                "error": "collective_field module not available",
            }

    def get_shell_summary(self) -> dict[str, Any]:
        """
        Get comprehensive shell summary.

        Returns
        -------
        dict
            Shell state summary
        """
        return {
            "kernel_state": self.kernel.get_state_summary(),
            "num_agents": len(self.agents),
            "trajectory_length": len(self.trajectory),
            "safeguards_active": self.safeguards_active,
            "violations": len(self.safeguard_violations),
            "auto_exit_triggered": self.auto_exit_triggered,
            "age_seconds": time.time() - self.creation_time,
            "collective_metrics": self.get_collective_field_metrics(),
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"AeonShell(kernel={self.kernel}, agents={len(self.agents)}, "
            f"trajectory_length={len(self.trajectory)})"
        )
