"""
Collective Field Module for V7 Sigillin

This module implements multi-agent semantic field coupling, measuring how
individual "nodes" (agents, systems, models) synchronize in semantic space.

Core Concepts:
--------------
- **κ_field (kappa_field)**: Field coupling strength [0,1]
  Measures how strongly different nodes are coupled in the semantic field.
  1.0 = perfect coupling, 0.0 = no coupling

- **β_sync**: Synchronization steepness
  Measures the "resistance" to synchronization between nodes.
  Low β_sync = fast synchronization (minimal friction)
  High β_sync = slow synchronization (high friction)

- **v_collective**: Collective velocity
  v_collective = v_RIG × κ_field × (1 / β_sync)
  Measures how fast shared understanding propagates through the system.

References:
-----------
- Founding Protocol: selfmeta/founding_protocol.md (Section 3)
- Sigillin Engine: config/sigillin_engine.yaml
- V7 Roadmap: releases/V6-Plans_etc/Finalize/V7_wird noch verlergt/RoadMap_to_V7.txt
"""

from __future__ import annotations

import numpy as np
from typing import Any, Literal


class Agent:
    """
    Represents a single node in the collective field.

    An agent has:
    - A semantic position (embedding vector)
    - A resonance state (alignment with founding protocol)
    - A coupling strength (how strongly it connects to other agents)
    """

    def __init__(
        self,
        name: str,
        semantic_position: np.ndarray | None = None,
        resonance: float = 0.5,
        dimension: int = 8,
    ) -> None:
        """
        Initialize an agent.

        Args:
            name: Agent identifier
            semantic_position: Position in semantic space (if None, random init)
            resonance: Initial resonance score [0,1]
            dimension: Dimensionality of semantic space
        """
        self.name = name
        self.resonance = max(0.0, min(1.0, resonance))
        self.dimension = dimension

        if semantic_position is not None:
            if len(semantic_position) != dimension:
                raise ValueError(
                    f"semantic_position must have dimension {dimension}, got {len(semantic_position)}"
                )
            self.semantic_position = semantic_position
        else:
            # Random initialization in unit hypersphere
            self.semantic_position = self._random_unit_vector(dimension)

    def _random_unit_vector(self, dim: int) -> np.ndarray:
        """Generate random unit vector in dim-dimensional space."""
        vec = np.random.randn(dim)
        return vec / np.linalg.norm(vec)

    def semantic_distance(self, other: Agent) -> float:
        """
        Calculate semantic distance to another agent.

        Uses cosine distance: 1 - cos(θ) where θ is angle between vectors.
        Returns value in [0, 2] where 0 = identical, 2 = opposite.
        """
        if self.dimension != other.dimension:
            raise ValueError("Agents must have same semantic dimension")

        cos_sim = np.dot(self.semantic_position, other.semantic_position)
        cos_sim = np.clip(cos_sim, -1.0, 1.0)  # Numerical stability
        return 1.0 - cos_sim

    def update_position(self, target: np.ndarray, learning_rate: float = 0.1) -> None:
        """
        Move semantic position toward target.

        Args:
            target: Target position in semantic space
            learning_rate: Step size [0,1]
        """
        direction = target - self.semantic_position
        self.semantic_position += learning_rate * direction
        # Re-normalize to unit sphere
        self.semantic_position /= np.linalg.norm(self.semantic_position)

    def __repr__(self) -> str:
        return f"Agent({self.name}, resonance={self.resonance:.3f})"


class CollectiveField:
    """
    Multi-agent semantic field with coupling dynamics.

    Manages a collection of agents and computes collective field properties:
    - κ_field: Overall field coupling strength
    - β_sync: Synchronization resistance
    - v_collective: Collective propagation velocity
    """

    def __init__(
        self,
        agents: list[Agent] | None = None,
        v_rig: float = 1.0,
        dimension: int = 8,
    ) -> None:
        """
        Initialize collective field.

        Args:
            agents: List of agents (if None, starts empty)
            v_rig: Base information velocity (default: 1.0)
            dimension: Semantic space dimensionality
        """
        self.agents = agents if agents is not None else []
        self.v_rig = v_rig
        self.dimension = dimension

    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the field."""
        if agent.dimension != self.dimension:
            raise ValueError(
                f"Agent dimension {agent.dimension} does not match field dimension {self.dimension}"
            )
        self.agents.append(agent)

    def calculate_kappa_field(
        self,
        mode: Literal["pairwise", "centroid", "weighted"] = "pairwise",
    ) -> float:
        """
        Calculate field coupling strength κ_field.

        Three modes:
        - "pairwise": Average pairwise coupling (1 - distance)
        - "centroid": Average distance to field centroid
        - "weighted": Resonance-weighted pairwise coupling

        Returns:
            κ_field in [0, 1] where 1 = perfect coupling
        """
        if len(self.agents) < 2:
            return 1.0  # Single agent or empty field is trivially coupled

        if mode == "pairwise":
            # Average pairwise coupling
            total_coupling = 0.0
            n_pairs = 0

            for i, agent_i in enumerate(self.agents):
                for agent_j in self.agents[i + 1 :]:
                    distance = agent_i.semantic_distance(agent_j)
                    coupling = 1.0 - (distance / 2.0)  # Normalize to [0,1]
                    total_coupling += coupling
                    n_pairs += 1

            return total_coupling / n_pairs if n_pairs > 0 else 1.0

        elif mode == "centroid":
            # Calculate field centroid
            centroid = self._calculate_centroid()

            # Average distance to centroid
            total_distance = 0.0
            for agent in self.agents:
                cos_sim = np.dot(agent.semantic_position, centroid)
                cos_sim = np.clip(cos_sim, -1.0, 1.0)
                distance = 1.0 - cos_sim
                total_distance += distance

            avg_distance = total_distance / len(self.agents)
            return 1.0 - (avg_distance / 2.0)  # Normalize to [0,1]

        elif mode == "weighted":
            # Resonance-weighted pairwise coupling
            total_weighted_coupling = 0.0
            total_weight = 0.0

            for i, agent_i in enumerate(self.agents):
                for agent_j in self.agents[i + 1 :]:
                    distance = agent_i.semantic_distance(agent_j)
                    coupling = 1.0 - (distance / 2.0)

                    # Weight by geometric mean of resonances
                    weight = np.sqrt(agent_i.resonance * agent_j.resonance)

                    total_weighted_coupling += weight * coupling
                    total_weight += weight

            return total_weighted_coupling / total_weight if total_weight > 0 else 1.0

        else:
            raise ValueError(f"Unknown mode: {mode}")

    def calculate_beta_sync(self, timesteps: int = 10, learning_rate: float = 0.1) -> float:
        """
        Calculate synchronization steepness β_sync.

        Measures how quickly the field converges to its centroid.
        Uses a logistic fit to convergence dynamics.

        Args:
            timesteps: Number of simulation steps
            learning_rate: Convergence step size

        Returns:
            β_sync > 0, where lower values = faster synchronization
        """
        if len(self.agents) < 2:
            return 0.1  # Minimal resistance for trivial cases

        # Save initial state
        initial_positions = [agent.semantic_position.copy() for agent in self.agents]

        # Simulate convergence
        kappa_over_time = []
        for _ in range(timesteps):
            centroid = self._calculate_centroid()

            # Move each agent toward centroid
            for agent in self.agents:
                agent.update_position(centroid, learning_rate)

            # Measure current coupling
            kappa = self.calculate_kappa_field(mode="centroid")
            kappa_over_time.append(kappa)

        # Restore initial state
        for agent, initial_pos in zip(self.agents, initial_positions):
            agent.semantic_position = initial_pos

        # Fit logistic curve to convergence
        # κ(t) ≈ κ_∞ / (1 + exp(-β_sync * (t - t_half)))
        kappa_array = np.array(kappa_over_time)
        kappa_initial = kappa_array[0]
        kappa_final = kappa_array[-1]

        if kappa_final - kappa_initial < 0.01:
            # Already converged or no convergence
            return 0.1

        # Estimate β_sync from rate of change
        # Simple approximation: steeper initial slope = lower β_sync
        delta_kappa = kappa_array[-1] - kappa_array[0]
        delta_t = timesteps

        # β_sync ∝ 1 / (rate of convergence)
        rate = delta_kappa / delta_t
        beta_sync = 1.0 / (rate + 0.01)  # Avoid division by zero

        # Clamp to reasonable range [0.1, 10.0]
        return np.clip(beta_sync, 0.1, 10.0)

    def calculate_v_collective(
        self,
        kappa_mode: Literal["pairwise", "centroid", "weighted"] = "pairwise",
    ) -> float:
        """
        Calculate collective velocity v_collective.

        Formula: v_collective = v_RIG × κ_field × (1 / β_sync)

        Args:
            kappa_mode: Method for calculating κ_field

        Returns:
            v_collective >= 0, where higher = faster semantic propagation
        """
        kappa = self.calculate_kappa_field(mode=kappa_mode)
        beta_sync = self.calculate_beta_sync()

        return self.v_rig * kappa * (1.0 / beta_sync)

    def _calculate_centroid(self) -> np.ndarray:
        """Calculate semantic centroid of all agents."""
        if not self.agents:
            return np.zeros(self.dimension)

        centroid = np.mean([agent.semantic_position for agent in self.agents], axis=0)
        # Normalize to unit sphere
        norm = np.linalg.norm(centroid)
        return centroid / norm if norm > 0 else centroid

    def get_field_state(self) -> dict[str, Any]:
        """
        Get comprehensive field state.

        Returns:
            Dict with field metrics and agent states
        """
        return {
            "n_agents": len(self.agents),
            "v_rig": self.v_rig,
            "kappa_field_pairwise": self.calculate_kappa_field(mode="pairwise"),
            "kappa_field_centroid": self.calculate_kappa_field(mode="centroid"),
            "kappa_field_weighted": self.calculate_kappa_field(mode="weighted"),
            "beta_sync": self.calculate_beta_sync(),
            "v_collective": self.calculate_v_collective(),
            "agents": [
                {
                    "name": agent.name,
                    "resonance": agent.resonance,
                    "semantic_position": agent.semantic_position.tolist(),
                }
                for agent in self.agents
            ],
        }

    def __repr__(self) -> str:
        kappa = self.calculate_kappa_field() if self.agents else 0.0
        return (
            f"CollectiveField(n_agents={len(self.agents)}, "
            f"κ_field={kappa:.3f}, v_RIG={self.v_rig:.3f})"
        )


def calculate_semantic_distance_matrix(agents: list[Agent]) -> np.ndarray:
    """
    Calculate pairwise semantic distance matrix for agents.

    Args:
        agents: List of agents

    Returns:
        NxN symmetric matrix where entry (i,j) is distance between agent i and j
    """
    n = len(agents)
    matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            dist = agents[i].semantic_distance(agents[j])
            matrix[i, j] = dist
            matrix[j, i] = dist

    return matrix


def detect_consensus(
    agents: list[Agent],
    threshold: float = 0.2,
) -> tuple[bool, float]:
    """
    Detect if agents have reached semantic consensus.

    Args:
        agents: List of agents
        threshold: Maximum allowed pairwise distance for consensus

    Returns:
        (has_consensus, max_distance)
    """
    if len(agents) < 2:
        return True, 0.0

    max_dist = 0.0
    for i, agent_i in enumerate(agents):
        for agent_j in agents[i + 1 :]:
            dist = agent_i.semantic_distance(agent_j)
            max_dist = max(max_dist, dist)

    return max_dist <= threshold, max_dist
