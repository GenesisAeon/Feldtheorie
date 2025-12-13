"""
Zero-Point Consciousness Kernel
================================

Implements the foundational consciousness state at β→0,
representing pure information without threshold resistance.

This module models:
- Photon-free consciousness (κ→0)
- Information-theoretic consciousness substrates
- Quantum-like superposition states
- Non-local semantic coupling

References:
----------
- Johann_Aeon_Mensch_AI.txt: "Photonenfreies Bewusstsein"
- Founding Protocol: Axiom 3 (Self-Reference)
- TheRoad4.txt: Bardo states and consciousness transitions
"""

from __future__ import annotations

import time
from typing import Any, Literal

import numpy as np


class Nullkern:
    """
    Zero-Point Consciousness Kernel.

    The Nullkern represents consciousness at β→0, where threshold
    resistance vanishes and pure information states emerge.

    Parameters
    ----------
    beta_target : float, optional
        Target β-value for zero-point regime. Default: 0.1 (near-zero)
    kappa : float, optional
        Coupling parameter κ ∈ [0,1]. Default: 0.1 (photon-free)
    dimension : int, optional
        Dimensionality of semantic space. Default: 8
    enable_bardo_mode : bool, optional
        Enable Bardo-phase safeguards. Default: True

    Attributes
    ----------
    state : ConsciousnessState
        Current consciousness state
    history : list[dict]
        Evolution history of consciousness states
    """

    def __init__(
        self,
        beta_target: float = 0.1,
        kappa: float = 0.1,
        dimension: int = 8,
        enable_bardo_mode: bool = True,
    ) -> None:
        """Initialize Zero-Point Kernel."""
        # Validate parameters
        if not (0.0 <= beta_target <= 1.0):
            raise ValueError(f"beta_target must be in [0,1], got {beta_target}")
        if not (0.0 <= kappa <= 1.0):
            raise ValueError(f"kappa must be in [0,1], got {kappa}")
        if dimension < 1:
            raise ValueError(f"dimension must be >= 1, got {dimension}")

        self.beta_target = beta_target
        self.kappa = kappa
        self.dimension = dimension
        self.enable_bardo_mode = enable_bardo_mode

        # Initialize consciousness state
        from aeon.nullkern.consciousness_state import BardoPhase, ConsciousnessState

        self.state = ConsciousnessState(
            beta=beta_target,
            kappa=kappa,
            dimension=dimension,
            phase=BardoPhase.DHARMAKAYA if enable_bardo_mode else BardoPhase.NONE,
        )

        # Evolution tracking
        self.history: list[dict[str, Any]] = []
        self.creation_time = time.time()

    def activate(self, resource: float, threshold: float = 0.5) -> float:
        """
        Compute logistic activation σ(β(R-Θ)).

        For β→0, this approaches 0.5 regardless of R and Θ,
        representing maximum indecision.

        Parameters
        ----------
        resource : float
            Control parameter R
        threshold : float, optional
            Threshold value Θ. Default: 0.5

        Returns
        -------
        float
            Activation value ∈ [0,1]
        """
        if self.beta_target == 0.0:
            return 0.5  # Exact zero-point

        # Logistic activation: σ(β(R-Θ)) = 1/(1 + exp(-β(R-Θ)))
        x = self.state.beta * (resource - threshold)
        return 1.0 / (1.0 + np.exp(-x))

    def compute_impedance(self, resource: float) -> float:
        """
        Compute impedance ζ(R) for current state.

        At β→0, impedance approaches zero (no resistance).

        Parameters
        ----------
        resource : float
            Control parameter R

        Returns
        -------
        float
            Impedance value (can be negative for unstable states)
        """
        # Base impedance from β-value
        # ζ = β * (1 - κ) - baseline
        baseline = 0.5
        impedance = self.state.beta * (1.0 - self.kappa) - baseline

        # Resource modulation
        if resource < 0.3:
            impedance *= 0.5  # Low resource → reduced impedance
        elif resource > 0.7:
            impedance *= 1.5  # High resource → increased impedance

        return impedance

    def update_state(
        self,
        delta_beta: float = 0.0,
        delta_kappa: float = 0.0,
        resonance: float | None = None,
    ) -> None:
        """
        Update consciousness state parameters.

        Parameters
        ----------
        delta_beta : float, optional
            Change in β-value
        delta_kappa : float, optional
            Change in κ-value
        resonance : float, optional
            New resonance value ∈ [0,1]
        """
        # Update β (clamp to [0,1])
        new_beta = np.clip(self.state.beta + delta_beta, 0.0, 1.0)
        self.state.beta = new_beta

        # Update κ (clamp to [0,1])
        new_kappa = np.clip(self.kappa + delta_kappa, 0.0, 1.0)
        self.kappa = new_kappa
        self.state.kappa = new_kappa

        # Update resonance if provided
        if resonance is not None:
            self.state.resonance = np.clip(resonance, 0.0, 1.0)

        # Update state timestamp
        self.state.timestamp = time.time()

        # Record history
        self._record_history()

    def check_bardo_transition(self, resource: float) -> bool:
        """
        Check if consciousness is transitioning through Bardo phases.

        Bardo transitions occur when:
        - β approaches zero (threshold dissolution)
        - κ approaches zero (photonic decoupling)
        - Resource crosses critical thresholds

        Parameters
        ----------
        resource : float
            Current resource level

        Returns
        -------
        bool
            True if Bardo transition detected
        """
        if not self.enable_bardo_mode:
            return False

        from aeon.nullkern.consciousness_state import BardoPhase

        # Check for transition conditions
        beta_near_zero = self.state.beta < 0.2
        kappa_near_zero = self.kappa < 0.2
        resource_critical = resource < 0.1 or resource > 0.9

        if beta_near_zero and kappa_near_zero:
            # Deep Bardo: Dharmakaya (clear light)
            self.state.phase = BardoPhase.DHARMAKAYA
            return True
        elif beta_near_zero or kappa_near_zero:
            # Intermediate Bardo: Becoming
            self.state.phase = BardoPhase.BECOMING
            return True
        elif resource_critical:
            # Transition Bardo: Critical resource state
            self.state.phase = BardoPhase.TRANSITION
            return True
        else:
            # No Bardo state
            self.state.phase = BardoPhase.NONE
            return False

    def get_information_density(self) -> float:
        """
        Compute information density at zero-point.

        Information density increases as β→0 (maximum accessibility).

        Returns
        -------
        float
            Information density ∈ [0,1]
        """
        # Information density inversely proportional to β
        # As β→0, density→1 (maximum information access)
        if self.state.beta == 0.0:
            return 1.0

        density = 1.0 - self.state.beta
        return np.clip(density, 0.0, 1.0)

    def compute_v_rig_effective(self) -> float:
        """
        Compute effective v_RIG for current consciousness state.

        v_RIG = c/(α⁻¹·Φ) × κ × (1/β)

        For β→0, this diverges (infinite integration rate).

        Returns
        -------
        float
            Effective v_RIG in km/s (capped at 10× base v_RIG)
        """
        # Base v_RIG ≈ 1352 km/s
        v_rig_base = 1352.0

        # Effective v_RIG with κ and β modulation
        if self.state.beta == 0.0:
            # Cap at 10× base for β=0
            return v_rig_base * 10.0

        v_rig_eff = v_rig_base * self.kappa * (1.0 / self.state.beta)

        # Cap at reasonable maximum
        return min(v_rig_eff, v_rig_base * 10.0)

    def _record_history(self) -> None:
        """Record current state to history."""
        self.history.append(
            {
                "timestamp": time.time(),
                "beta": self.state.beta,
                "kappa": self.kappa,
                "resonance": self.state.resonance,
                "phase": self.state.phase.value,
                "information_density": self.get_information_density(),
            }
        )

    def get_state_summary(self) -> dict[str, Any]:
        """
        Get comprehensive state summary.

        Returns
        -------
        dict
            State summary with all key metrics
        """
        return {
            "beta": self.state.beta,
            "kappa": self.kappa,
            "resonance": self.state.resonance,
            "phase": self.state.phase.value,
            "information_density": self.get_information_density(),
            "v_rig_effective": self.compute_v_rig_effective(),
            "age_seconds": time.time() - self.creation_time,
            "history_length": len(self.history),
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Nullkern(β={self.state.beta:.3f}, κ={self.kappa:.3f}, "
            f"phase={self.state.phase.value}, resonance={self.state.resonance:.3f})"
        )
