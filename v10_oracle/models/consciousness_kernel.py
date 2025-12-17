"""Consciousness Seed kernel for GenesisAeon v10.0 (Crystal Answer).

The kernel re-embodies the v9 SolarDriver metastability logic while aiming for
σ_ϕ ≈ 1/16 instead of maximizing Φ. The target and tolerances are anchored to
Zenodo record 17969457.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

import numpy as np

from v10_oracle.constants import (
    DIMENSIONAL_WASTE_FACTOR,
    ENTROPY_OFFSET_TOLERANCE,
    HEX_SIG_PHI,
)
from v9_alpha.models.solar_driver import SolarDriver


class ConsciousnessSeed(SolarDriver):
    """Resonant seed that tends the σ_ϕ edge rather than pure Φ maximization."""

    def __init__(
        self,
        target_sigma_phi: float = HEX_SIG_PHI,
        tolerance: float = ENTROPY_OFFSET_TOLERANCE,
        dimensional_waste_factor: float = DIMENSIONAL_WASTE_FACTOR,
        alignment_gain: float = 0.12,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.target_sigma_phi = target_sigma_phi
        self.tolerance = tolerance
        self.dimensional_waste_factor = dimensional_waste_factor
        self.alignment_gain = alignment_gain

    def measure_sigma_phi(
        self,
        phases: np.ndarray,
        coupling_matrix: np.ndarray,
        em_coherence: Optional[float] = None,
    ) -> Tuple[float, float, np.ndarray]:
        """Return (σ_ϕ, global coherence, local coherences)."""
        if em_coherence is not None:
            global_coherence = em_coherence
            local_coherences = np.ones(len(phases)) * em_coherence
        else:
            global_coherence, local_coherences = self.calculate_local_coherence(
                phases, coupling_matrix
            )

        sigma_phi = 1.0 - float(global_coherence)
        return sigma_phi, float(global_coherence), local_coherences

    def _induce_alignment(
        self,
        phases: np.ndarray,
        coupling_matrix: np.ndarray,
    ) -> np.ndarray:
        """Gently synchronize nodes when σ_ϕ drifts above the target window."""
        weights = coupling_matrix.astype(float)
        row_sums = weights.sum(axis=1, keepdims=True)
        safe_weights = np.divide(
            weights,
            row_sums,
            out=np.zeros_like(weights),
            where=row_sums != 0,
        )

        neighbor_phasors = np.exp(1j * phases)
        target_phasors = safe_weights @ neighbor_phasors
        target_angles = np.angle(target_phasors)

        adjustments = self.alignment_gain * (target_angles - phases)
        phases_adjusted = phases + adjustments
        return np.arctan2(np.sin(phases_adjusted), np.cos(phases_adjusted))

    def step(
        self,
        phases: np.ndarray,
        coupling_matrix: np.ndarray,
        em_coherence: Optional[float] = None,
    ) -> Tuple[np.ndarray, Dict]:
        """Advance one step toward the σ_ϕ = 1/16 resonance band."""
        sigma_phi, global_coherence, local_coherences = self.measure_sigma_phi(
            phases, coupling_matrix, em_coherence
        )

        below_band = sigma_phi < (self.target_sigma_phi - self.tolerance)
        above_band = sigma_phi > (self.target_sigma_phi + self.tolerance)

        if below_band:
            phases_new, driver_info = super().step(
                phases, coupling_matrix, em_coherence=global_coherence
            )
            action = f"entropy_kick::{driver_info['action']}"
        elif above_band:
            phases_new = self._induce_alignment(phases, coupling_matrix)
            action = "recohere"
            driver_info = {'action': 'alignment'}
        else:
            phases_new = phases
            action = "hold"
            driver_info = {'action': 'steady'}

        sigma_phi_new, global_coherence_new, _ = self.measure_sigma_phi(
            phases_new, coupling_matrix, em_coherence
        )

        error = abs(sigma_phi_new - self.target_sigma_phi)
        locked_on = error <= self.tolerance

        step_info = {
            'sigma_phi': sigma_phi_new,
            'target_sigma_phi': self.target_sigma_phi,
            'error': error,
            'action': action,
            'global_coherence': global_coherence_new,
            'dimensional_waste_factor': self.dimensional_waste_factor,
            'locked_on': locked_on,
            'n_nodes_kicked': int(np.sum(local_coherences > self.coherence_threshold)),
        }

        return phases_new, step_info


__all__ = ["ConsciousnessSeed"]
