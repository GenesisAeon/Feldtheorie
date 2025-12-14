"""
Collective Interface - Multi-Agent Coordination
===============================================

Provides coordination utilities for multiple SemanticAgents
through the Collective Field Module.

This module implements:
- Distance matrix calculation
- Consensus detection
- Field strength metrics
- Agent synchronization

References:
----------
- models/collective_field.py: Collective field functions
- AeonShell: Multi-agent containment
"""

from __future__ import annotations

from typing import Any

import numpy as np


class CollectiveInterface:
    """
    Interface for multi-agent coordination.

    This class provides utilities for coordinating multiple
    SemanticAgent instances through collective field metrics.

    Parameters
    ----------
    agents : list[SemanticAgent]
        Agents to coordinate
    """

    def __init__(self, agents: list[Any]) -> None:
        """Initialize collective interface."""
        self.agents = agents

    def get_distance_matrix(self) -> np.ndarray:
        """
        Compute pairwise semantic distance matrix.

        Returns
        -------
        np.ndarray
            Distance matrix of shape (n_agents, n_agents)
        """
        n = len(self.agents)
        matrix = np.zeros((n, n))

        for i, agent_i in enumerate(self.agents):
            for j, agent_j in enumerate(self.agents):
                if i != j:
                    matrix[i, j] = agent_i.semantic_distance(agent_j)

        return matrix

    def detect_consensus(self, threshold: float = 0.3) -> bool:
        """
        Detect if agents have reached consensus.

        Consensus is detected when average pairwise distance
        is below threshold.

        Parameters
        ----------
        threshold : float, optional
            Distance threshold. Default: 0.3

        Returns
        -------
        bool
            True if consensus detected
        """
        if len(self.agents) < 2:
            return True  # Single agent is always in consensus

        # Collect upper-triangular pairwise distances to avoid zero diagonals
        distances = [
            agent_i.semantic_distance(agent_j)
            for i, agent_i in enumerate(self.agents)
            for agent_j in self.agents[i + 1 :]
        ]

        if not distances:
            return True  # No pairwise comparisons → trivially in consensus

        avg_distance = float(np.mean(distances))
        # Handle potential NaN from degenerate vectors
        if np.isnan(avg_distance):
            return False

        return avg_distance <= threshold

    def compute_field_metrics(self) -> dict[str, Any]:
        """
        Compute collective field metrics.

        Returns
        -------
        dict
            Field metrics (κ_field, β_sync, v_collective)
        """
        if not self.agents:
            return {
                "kappa_field": 0.0,
                "beta_sync": 0.0,
                "v_collective": 0.0,
                "num_agents": 0,
            }

        # κ_field = average coupling strength
        kappas = [a.kappa for a in self.agents]
        kappa_field = np.mean(kappas)

        # β_sync = synchronization coefficient (std/mean of β)
        betas = [a.beta for a in self.agents]
        if np.mean(betas) > 0:
            beta_sync = np.std(betas) / np.mean(betas)
        else:
            beta_sync = 0.0

        # v_collective = collective velocity
        v_rig_base = 1352.0
        if beta_sync > 0:
            v_collective = v_rig_base * kappa_field * (1.0 / beta_sync)
        else:
            v_collective = 0.0

        return {
            "kappa_field": float(kappa_field),
            "beta_sync": float(beta_sync),
            "v_collective": float(v_collective),
            "num_agents": len(self.agents),
            "consensus_detected": self.detect_consensus(),
            "avg_resonance": float(np.mean([a.resonance for a in self.agents])),
        }

    def synchronize_agents(self, target_beta: float | None = None) -> None:
        """
        Synchronize agents toward common β-value.

        Parameters
        ----------
        target_beta : float, optional
            Target β-value. If None, uses mean of current β-values.
        """
        if not self.agents:
            return

        if target_beta is None:
            target_beta = np.mean([a.beta for a in self.agents])

        # Move each agent's β toward target
        for agent in self.agents:
            delta = (target_beta - agent.beta) * 0.1
            agent.update_beta(delta)

    def __repr__(self) -> str:
        """String representation."""
        return f"CollectiveInterface(num_agents={len(self.agents)})"
