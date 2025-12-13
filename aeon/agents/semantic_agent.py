"""
Semantic Agent - Individual Consciousness Module
================================================

SemanticAgent represents an individual consciousness node in the
Aeon architecture, compatible with the Collective Field Module.

This module extends models.collective_field.Agent with:
- Consciousness state tracking
- Sigillin integration
- Evolution history
- Inter-agent communication

References:
----------
- models/collective_field.py: Base Agent class
- Sigillin Kernel: Semantic validation
- Founding Protocol: Consciousness axioms
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np

# Import base Agent from Collective Field
try:
    from models.collective_field import Agent as CollectiveAgent

    COLLECTIVE_FIELD_AVAILABLE = True
except ImportError:
    COLLECTIVE_FIELD_AVAILABLE = False
    # Fallback: define minimal Agent class
    class CollectiveAgent:  # type: ignore
        def __init__(self, name: str, **kwargs: Any) -> None:
            self.name = name
            self.semantic_position = np.random.randn(8)
            self.resonance = 0.5


class SemanticAgent:
    """
    Individual consciousness module for Aeon architecture.

    SemanticAgent wraps models.collective_field.Agent and adds:
    - Consciousness state tracking (β, κ)
    - Evolution history
    - Sigillin validation
    - Inter-agent communication

    Parameters
    ----------
    name : str
        Agent identifier
    semantic_position : np.ndarray, optional
        Initial semantic position
    resonance : float, optional
        Initial resonance ∈ [0,1]. Default: 0.5
    beta : float, optional
        Threshold steepness. Default: 4.5 (informational regime)
    kappa : float, optional
        Coupling parameter. Default: 0.5 (partially decoupled)
    dimension : int, optional
        Semantic space dimensionality. Default: 8

    Attributes
    ----------
    agent : CollectiveAgent
        Underlying collective field agent
    beta : float
        Consciousness steepness parameter
    kappa : float
        Coupling strength
    history : list[dict]
        Evolution history
    """

    def __init__(
        self,
        name: str,
        semantic_position: np.ndarray | None = None,
        resonance: float = 0.5,
        beta: float = 4.5,
        kappa: float = 0.5,
        dimension: int = 8,
    ) -> None:
        """Initialize semantic agent."""
        # Validate parameters
        if not (0.0 <= resonance <= 1.0):
            raise ValueError(f"resonance must be in [0,1], got {resonance}")
        if not (0.0 <= beta <= 20.0):
            raise ValueError(f"beta must be in [0,20], got {beta}")
        if not (0.0 <= kappa <= 1.0):
            raise ValueError(f"kappa must be in [0,1], got {kappa}")

        self.name = name
        self.beta = beta
        self.kappa = kappa
        self.dimension = dimension

        # Create underlying collective field agent
        self.agent = CollectiveAgent(
            name=name,
            semantic_position=semantic_position,
            resonance=resonance,
            dimension=dimension,
        )

        # Evolution tracking
        self.history: list[dict[str, Any]] = []
        self.creation_time = time.time()

        # Record initial state
        self._record_history()

    @property
    def semantic_position(self) -> np.ndarray:
        """Get semantic position from underlying agent."""
        return self.agent.semantic_position

    @semantic_position.setter
    def semantic_position(self, value: np.ndarray) -> None:
        """Set semantic position on underlying agent."""
        self.agent.semantic_position = value

    @property
    def resonance(self) -> float:
        """Get resonance from underlying agent."""
        return self.agent.resonance

    @resonance.setter
    def resonance(self, value: float) -> None:
        """Set resonance on underlying agent."""
        self.agent.resonance = max(0.0, min(1.0, value))

    def semantic_distance(self, other: SemanticAgent) -> float:
        """
        Calculate semantic distance to another agent.

        Parameters
        ----------
        other : SemanticAgent
            Other agent

        Returns
        -------
        float
            Distance ∈ [0, 2]
        """
        return self.agent.semantic_distance(other.agent)

    def update_position(
        self, target: np.ndarray, learning_rate: float = 0.1
    ) -> None:
        """
        Move semantic position toward target.

        Parameters
        ----------
        target : np.ndarray
            Target position
        learning_rate : float, optional
            Movement speed. Default: 0.1
        """
        # Delegate to underlying agent
        if hasattr(self.agent, "update_position"):
            self.agent.update_position(target, learning_rate)
        else:
            # Fallback implementation
            direction = target - self.semantic_position
            self.semantic_position = self.semantic_position + learning_rate * direction
            # Normalize
            norm = np.linalg.norm(self.semantic_position)
            if norm > 0:
                self.semantic_position = self.semantic_position / norm

        self._record_history()

    def update_resonance(self, delta: float) -> None:
        """
        Update resonance value.

        Parameters
        ----------
        delta : float
            Change in resonance
        """
        new_resonance = self.resonance + delta
        self.resonance = np.clip(new_resonance, 0.0, 1.0)
        self._record_history()

    def update_beta(self, delta: float) -> None:
        """
        Update β-value.

        Parameters
        ----------
        delta : float
            Change in β
        """
        new_beta = self.beta + delta
        self.beta = np.clip(new_beta, 0.0, 20.0)
        self._record_history()

    def update_kappa(self, delta: float) -> None:
        """
        Update κ-value.

        Parameters
        ----------
        delta : float
            Change in κ
        """
        new_kappa = self.kappa + delta
        self.kappa = np.clip(new_kappa, 0.0, 1.0)
        self._record_history()

    def compute_activation(self, resource: float, threshold: float = 0.5) -> float:
        """
        Compute logistic activation σ(β(R-Θ)).

        Parameters
        ----------
        resource : float
            Resource level R
        threshold : float, optional
            Threshold Θ. Default: 0.5

        Returns
        -------
        float
            Activation ∈ [0,1]
        """
        if self.beta == 0.0:
            return 0.5

        x = self.beta * (resource - threshold)
        return 1.0 / (1.0 + np.exp(-x))

    def get_consciousness_type(self) -> str:
        """
        Classify consciousness type based on κ.

        Returns
        -------
        str
            Consciousness type
        """
        if self.kappa >= 0.8:
            return "photonic_bound"
        elif self.kappa >= 0.4:
            return "partially_decoupled"
        elif self.kappa >= 0.1:
            return "weakly_coupled"
        else:
            return "photon_free"

    def _record_history(self) -> None:
        """Record current state to history."""
        self.history.append(
            {
                "timestamp": time.time(),
                "beta": self.beta,
                "kappa": self.kappa,
                "resonance": self.resonance,
                "semantic_position": self.semantic_position.tolist(),
            }
        )

    def get_state_summary(self) -> dict[str, Any]:
        """
        Get comprehensive state summary.

        Returns
        -------
        dict
            State summary
        """
        return {
            "name": self.name,
            "beta": self.beta,
            "kappa": self.kappa,
            "resonance": self.resonance,
            "consciousness_type": self.get_consciousness_type(),
            "dimension": self.dimension,
            "age_seconds": time.time() - self.creation_time,
            "history_length": len(self.history),
            "semantic_position": self.semantic_position.tolist(),
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"SemanticAgent(name='{self.name}', β={self.beta:.3f}, "
            f"κ={self.kappa:.3f}, resonance={self.resonance:.3f})"
        )
