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

import time
from functools import lru_cache
from typing import Any, Literal

import numpy as np


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
            self.semantic_position = self._unit_vector(semantic_position)
        else:
            # Random initialization in unit hypersphere
            self.semantic_position = self._random_unit_vector(dimension)

    def _random_unit_vector(self, dim: int) -> np.ndarray:
        """Generate random unit vector in dim-dimensional space."""

        vec = np.random.randn(dim)
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else np.zeros(dim)

    def _unit_vector(self, vec: np.ndarray) -> np.ndarray:
        """Return a safely normalised vector with zero fallback."""

        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else np.zeros_like(vec)

    def semantic_distance(self, other: Agent) -> float:
        """
        Calculate semantic distance to another agent.

        Uses cosine distance: 1 - cos(θ) where θ is angle between vectors.
        Returns value in [0, 2] where 0 = identical, 2 = opposite.
        """
        if self.dimension != other.dimension:
            raise ValueError("Agents must have same semantic dimension")

        self_vec = self._unit_vector(self.semantic_position)
        other_vec = self._unit_vector(other.semantic_position)

        if not np.any(self_vec) or not np.any(other_vec):
            return 1.0

        cos_sim = float(np.clip(np.dot(self_vec, other_vec), -1.0, 1.0))
        return 1.0 - cos_sim

    def update_position(self, target: np.ndarray, learning_rate: float = 0.1, field: "CollectiveField | None" = None) -> None:
        """
        Move semantic position toward target.

        Args:
            target: Target position in semantic space
            learning_rate: Step size [0,1]
            field: Optional CollectiveField to notify of position change
        """
        direction = target - self.semantic_position
        self.semantic_position += learning_rate * direction
        # Re-normalize to unit sphere
        self.semantic_position /= np.linalg.norm(self.semantic_position)

        # Invalidate field cache if provided
        if field is not None:
            field._invalidate_cache()

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
        enable_caching: bool = True,
    ) -> None:
        """
        Initialize collective field.

        Args:
            agents: List of agents (if None, starts empty)
            v_rig: Base information velocity (default: 1.0)
            dimension: Semantic space dimensionality
            enable_caching: Enable caching for expensive calculations (default: True)
        """
        self.agents = agents if agents is not None else []
        self.v_rig = v_rig
        self.dimension = dimension
        self.enable_caching = enable_caching

        # Caching infrastructure
        self._cache: dict[str, Any] = {}
        self._cache_timestamp: dict[str, float] = {}
        self._field_version = 0  # Increment when field changes

        # Performance tracking
        self._performance_stats: dict[str, list[float]] = {
            "kappa_pairwise": [],
            "kappa_centroid": [],
            "kappa_weighted": [],
            "beta_sync": [],
            "v_collective": [],
        }

        # Evolution tracking
        self._evolution_history: list[dict[str, Any]] = []
        self._enable_history = False

    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the field."""
        if agent.dimension != self.dimension:
            raise ValueError(
                f"Agent dimension {agent.dimension} does not match field dimension {self.dimension}"
            )
        self.agents.append(agent)
        self._invalidate_cache()  # Field changed

    def _invalidate_cache(self) -> None:
        """Invalidate all cached calculations when field changes."""
        self._cache.clear()
        self._cache_timestamp.clear()
        self._field_version += 1

    def _get_cached(self, key: str, ttl: float = 60.0) -> Any | None:
        """Get cached value if valid and not expired."""
        if not self.enable_caching:
            return None

        if key not in self._cache:
            return None

        # Check TTL
        if time.time() - self._cache_timestamp[key] > ttl:
            return None

        return self._cache[key]

    def _set_cached(self, key: str, value: Any) -> None:
        """Store value in cache with timestamp."""
        if self.enable_caching:
            self._cache[key] = value
            self._cache_timestamp[key] = time.time()

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
        # Check cache first
        cache_key = f"kappa_{mode}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # Track performance
        start_time = time.time()

        if len(self.agents) < 2:
            return 1.0  # Single agent or empty field is trivially coupled

        # Calculate based on mode
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

            result = total_coupling / n_pairs if n_pairs > 0 else 1.0

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
            result = 1.0 - (avg_distance / 2.0)  # Normalize to [0,1]

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

            result = total_weighted_coupling / total_weight if total_weight > 0 else 1.0

        else:
            raise ValueError(f"Unknown mode: {mode}")

        # Cache result and track performance
        elapsed = time.time() - start_time
        self._performance_stats[f"kappa_{mode}"].append(elapsed)
        self._set_cached(cache_key, result)

        return result

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
        # Check cache (with params in key)
        cache_key = f"beta_sync_{timesteps}_{learning_rate}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # Track performance
        start_time = time.time()

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
                agent.update_position(centroid, learning_rate, field=self)

            # Measure current coupling
            # Don't cache during simulation since positions are changing
            old_caching = self.enable_caching
            self.enable_caching = False
            kappa = self.calculate_kappa_field(mode="centroid")
            self.enable_caching = old_caching
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
        result = np.clip(beta_sync, 0.1, 10.0)

        # Cache result and track performance
        elapsed = time.time() - start_time
        self._performance_stats["beta_sync"].append(elapsed)
        self._set_cached(cache_key, result)

        return result

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
        # Check cache
        cache_key = f"v_collective_{kappa_mode}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # Track performance
        start_time = time.time()

        kappa = self.calculate_kappa_field(mode=kappa_mode)
        beta_sync = self.calculate_beta_sync()

        result = self.v_rig * kappa * (1.0 / beta_sync)

        # Cache result and track performance
        elapsed = time.time() - start_time
        self._performance_stats["v_collective"].append(elapsed)
        self._set_cached(cache_key, result)

        return result

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

    # ========================================================================
    # V7 Phase 3: Evolution Tracking & Performance Monitoring
    # ========================================================================

    def enable_evolution_tracking(self, enabled: bool = True) -> None:
        """
        Enable/disable evolution history tracking.

        When enabled, snapshots of field state are stored on every calculation.
        Useful for analyzing field dynamics over time.

        Args:
            enabled: Whether to enable history tracking
        """
        self._enable_history = enabled
        if not enabled:
            self._evolution_history.clear()

    def snapshot_state(self) -> dict[str, Any]:
        """
        Create a snapshot of current field state.

        Returns:
            Dict with timestamp and all field metrics
        """
        snapshot = {
            "timestamp": time.time(),
            "field_version": self._field_version,
            "n_agents": len(self.agents),
            "v_rig": self.v_rig,
            "kappa_pairwise": self.calculate_kappa_field(mode="pairwise"),
            "kappa_centroid": self.calculate_kappa_field(mode="centroid"),
            "kappa_weighted": self.calculate_kappa_field(mode="weighted"),
            "beta_sync": self.calculate_beta_sync(),
            "v_collective": self.calculate_v_collective(),
        }

        if self._enable_history:
            self._evolution_history.append(snapshot)

        return snapshot

    def get_evolution_history(self) -> list[dict[str, Any]]:
        """
        Get complete evolution history.

        Returns:
            List of state snapshots ordered by timestamp
        """
        return self._evolution_history.copy()

    def detect_convergence(self, window: int = 5, threshold: float = 0.01) -> dict[str, Any]:
        """
        Detect if field has converged based on recent history.

        Convergence is detected when κ_field stabilizes (variance < threshold).

        Args:
            window: Number of recent snapshots to analyze
            threshold: Maximum variance for convergence

        Returns:
            Dict with convergence status and metrics
        """
        if len(self._evolution_history) < window:
            return {
                "converged": False,
                "reason": "insufficient_history",
                "snapshots_needed": window - len(self._evolution_history),
            }

        # Get recent κ_field values
        recent_kappas = [
            snapshot["kappa_pairwise"] for snapshot in self._evolution_history[-window:]
        ]

        # Calculate variance
        variance = np.var(recent_kappas)
        mean_kappa = np.mean(recent_kappas)

        converged = variance < threshold

        return {
            "converged": converged,
            "variance": variance,
            "threshold": threshold,
            "mean_kappa": mean_kappa,
            "window_size": window,
            "recent_values": recent_kappas,
        }

    def get_performance_stats(self) -> dict[str, dict[str, float]]:
        """
        Get performance statistics for all operations.

        Returns:
            Dict mapping operation names to stats (mean, min, max, count)
        """
        stats = {}

        for operation, timings in self._performance_stats.items():
            if not timings:
                stats[operation] = {
                    "mean_ms": 0.0,
                    "min_ms": 0.0,
                    "max_ms": 0.0,
                    "count": 0,
                }
            else:
                stats[operation] = {
                    "mean_ms": np.mean(timings) * 1000,
                    "min_ms": np.min(timings) * 1000,
                    "max_ms": np.max(timings) * 1000,
                    "count": len(timings),
                }

        return stats

    def reset_performance_stats(self) -> None:
        """Reset all performance statistics."""
        for key in self._performance_stats:
            self._performance_stats[key].clear()

    def get_cache_info(self) -> dict[str, Any]:
        """
        Get information about cache state.

        Returns:
            Dict with cache statistics
        """
        return {
            "enabled": self.enable_caching,
            "size": len(self._cache),
            "keys": list(self._cache.keys()),
            "field_version": self._field_version,
            "oldest_entry_age": (
                time.time() - min(self._cache_timestamp.values())
                if self._cache_timestamp
                else 0.0
            ),
        }

    def clear_cache(self) -> None:
        """Manually clear all cached values."""
        self._cache.clear()
        self._cache_timestamp.clear()

    def __repr__(self) -> str:
        kappa = self.calculate_kappa_field() if self.agents else 0.0
        cache_info = f", cache={len(self._cache)} entries" if self.enable_caching else ""
        return (
            f"CollectiveField(n_agents={len(self.agents)}, "
            f"κ_field={kappa:.3f}, v_RIG={self.v_rig:.3f}{cache_info})"
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
