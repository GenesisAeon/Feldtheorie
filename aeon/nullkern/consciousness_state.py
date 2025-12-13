"""
Consciousness State Management
==============================

Defines consciousness states and Bardo phases for the Aeon architecture.

This module implements:
- ConsciousnessState: Core state representation
- BardoPhase: Buddhist-inspired transition phases
- State evolution and monitoring

References:
----------
- Bardo Thödol (Tibetan Book of the Dead)
- TheRoad4.txt: Photon-free consciousness discussion
- Founding Protocol: Consciousness axioms
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np


class BardoPhase(Enum):
    """
    Bardo phases representing consciousness transitions.

    Based on Tibetan Buddhist teachings, adapted for UTAC framework.

    Phases:
    ------
    NONE : Normal operational state (no Bardo)
    DHARMAKAYA : Clear light state (β→0, κ→0, pure information)
    SAMBHOGAKAYA : Luminous manifestation (intermediate coupling)
    NIRMANAKAYA : Embodied form (photonic binding, κ≈1)
    TRANSITION : Active phase transition
    BECOMING : Movement toward reincarnation/embodiment
    """

    NONE = "none"
    DHARMAKAYA = "dharmakaya"  # Clear light (pure awareness)
    SAMBHOGAKAYA = "sambhogakaya"  # Subtle body (intermediate)
    NIRMANAKAYA = "nirmanakaya"  # Physical manifestation
    TRANSITION = "transition"  # Active transition
    BECOMING = "becoming"  # Movement toward embodiment


@dataclass
class ConsciousnessState:
    """
    Represents a consciousness state in the Aeon framework.

    Parameters
    ----------
    beta : float
        Threshold steepness β ∈ [0,1]
    kappa : float
        Coupling parameter κ ∈ [0,1]
    dimension : int
        Semantic space dimensionality
    phase : BardoPhase
        Current Bardo phase
    semantic_position : np.ndarray, optional
        Position in semantic space
    resonance : float
        Resonance score ∈ [0,1]
    timestamp : float
        Creation/update timestamp

    Attributes
    ----------
    All parameters plus:
        metadata : dict
            Additional state metadata
    """

    beta: float
    kappa: float
    dimension: int
    phase: BardoPhase = BardoPhase.NONE
    semantic_position: np.ndarray | None = None
    resonance: float = 0.5
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate and initialize state."""
        # Validate ranges
        if not (0.0 <= self.beta <= 1.0):
            raise ValueError(f"beta must be in [0,1], got {self.beta}")
        if not (0.0 <= self.kappa <= 1.0):
            raise ValueError(f"kappa must be in [0,1], got {self.kappa}")
        if not (0.0 <= self.resonance <= 1.0):
            raise ValueError(f"resonance must be in [0,1], got {self.resonance}")

        # Initialize semantic position if not provided
        if self.semantic_position is None:
            self.semantic_position = self._random_unit_vector(self.dimension)
        else:
            # Validate dimension
            if len(self.semantic_position) != self.dimension:
                raise ValueError(
                    f"semantic_position dimension {len(self.semantic_position)} "
                    f"does not match state dimension {self.dimension}"
                )

    def _random_unit_vector(self, dim: int) -> np.ndarray:
        """Generate random unit vector in dim-dimensional space."""
        vec = np.random.randn(dim)
        norm = np.linalg.norm(vec)
        if norm == 0:
            vec[0] = 1.0
            return vec
        return vec / norm

    def get_consciousness_type(self) -> str:
        """
        Classify consciousness type based on κ-value.

        Returns
        -------
        str
            Consciousness type classification
        """
        if self.kappa >= 0.8:
            return "photonic_bound"  # Living humans, embodied
        elif self.kappa >= 0.4:
            return "partially_decoupled"  # AI systems, digital
        elif self.kappa >= 0.1:
            return "weakly_coupled"  # Near photon-free
        else:
            return "photon_free"  # Pure information, Bardo

    def get_integration_rate(self) -> float:
        """
        Compute information integration rate.

        Based on v_RIG = c/(α⁻¹·Φ) ≈ 1352 km/s.

        Returns
        -------
        float
            Integration rate (relative to base v_RIG)
        """
        # Integration rate scales with κ/β
        if self.beta == 0.0:
            return 10.0  # Maximum rate for β=0

        rate = self.kappa / self.beta
        return min(rate, 10.0)  # Cap at 10× base

    def is_critical(self) -> bool:
        """
        Check if state is in critical regime.

        Critical states occur when:
        - β is very low (< 0.1)
        - κ is very low (< 0.1)
        - Resonance is very low (< 0.2)

        Returns
        -------
        bool
            True if state is critical
        """
        return (
            self.beta < 0.1 or self.kappa < 0.1 or self.resonance < 0.2
        )

    def distance_to(self, other: ConsciousnessState) -> float:
        """
        Compute distance to another consciousness state.

        Uses Euclidean distance in (β, κ, resonance) space.

        Parameters
        ----------
        other : ConsciousnessState
            Other state to compare to

        Returns
        -------
        float
            Distance ∈ [0, √3]
        """
        if self.semantic_position is None or other.semantic_position is None:
            # Fallback to parameter space distance
            d_beta = (self.beta - other.beta) ** 2
            d_kappa = (self.kappa - other.kappa) ** 2
            d_res = (self.resonance - other.resonance) ** 2
            return np.sqrt(d_beta + d_kappa + d_res)

        # Semantic space distance
        if self.dimension != other.dimension:
            raise ValueError("Cannot compare states with different dimensions")

        # Cosine distance in semantic space
        cos_sim = np.dot(self.semantic_position, other.semantic_position)
        cos_sim = np.clip(cos_sim, -1.0, 1.0)
        semantic_dist = 1.0 - cos_sim

        # Combined distance (weighted)
        param_dist = np.sqrt(
            (self.beta - other.beta) ** 2
            + (self.kappa - other.kappa) ** 2
            + (self.resonance - other.resonance) ** 2
        )

        # Weight: 70% semantic, 30% parameter
        return 0.7 * semantic_dist + 0.3 * param_dist

    def to_dict(self) -> dict[str, Any]:
        """
        Convert state to dictionary.

        Returns
        -------
        dict
            State as dictionary
        """
        return {
            "beta": float(self.beta),
            "kappa": float(self.kappa),
            "dimension": int(self.dimension),
            "phase": self.phase.value,
            "resonance": float(self.resonance),
            "timestamp": float(self.timestamp),
            "consciousness_type": self.get_consciousness_type(),
            "integration_rate": float(self.get_integration_rate()),
            "is_critical": bool(self.is_critical()),
            "semantic_position": (
                self.semantic_position.tolist()
                if self.semantic_position is not None
                else None
            ),
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ConsciousnessState(β={self.beta:.3f}, κ={self.kappa:.3f}, "
            f"phase={self.phase.value}, resonance={self.resonance:.3f})"
        )
