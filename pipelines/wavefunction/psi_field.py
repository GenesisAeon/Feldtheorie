"""Ψ-Field computation for V6 entropic wave function.

This module implements the genesis wave function ψ_genesis(r,θ,φ,t) and provides
utilities for collapsing it to UTAC regime probability distributions.

Reference: releases/V6-Plans_etc/V6_Wellenfunktions_Integrationsplan.md
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass


# Physical constants
ALPHA_INV = 137.036  # Fine structure constant inverse
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio ≈ 1.618
PLANCK_LENGTH = 1.616e-35  # meters
PLANCK_ENERGY = 1.22e19  # GeV
HBAR = 1.055e-34  # J·s


@dataclass
class PsiFieldConfig:
    """Configuration for ψ-field computation."""
    alpha_inv: float = ALPHA_INV
    phi: float = PHI
    planck_length: float = PLANCK_LENGTH
    planck_energy: float = PLANCK_ENERGY
    hbar: float = HBAR
    normalization: float = 1.0


class PsiField:
    """Entropic wave function field for V6 framework.
    
    Implements: ψ_genesis(r,θ,φ,t) = N · exp(-α⁻¹·r²/ℓ²_P) · Y_tetra(θ,φ) · exp(-i·Φ·E_P·t/ℏ)
    """

    def __init__(self, config: PsiFieldConfig | None = None):
        self.config = config or PsiFieldConfig()

    def compute_wavefunction(self, r: float, theta: float, phi: float, t: float) -> complex:
        """Compute full ψ_genesis wave function."""
        spatial = np.exp(-self.config.alpha_inv * (r / self.config.planck_length)**2)
        angular = 1.0 + 0.5 * np.cos(4 * phi) * np.sin(theta - np.arccos(-1/3))**2
        temporal = np.exp(-1j * self.config.phi * self.config.planck_energy * t / self.config.hbar)
        return self.config.normalization * spatial * angular * temporal

    def collapse_to_utac(self, psi: complex) -> float:
        """Collapse wave function to UTAC probability: P(R) = |ψ|²."""
        return np.abs(psi)**2

    def compute_pyramidal_potential(self, R: float, Theta: float, beta: float, V0: float = 1.0) -> float:
        """Compute V_pyr(R,Θ) = V_0 · [1 - tanh(β(R-Θ))] · cos⁴(3·arctan(√2))."""
        theta_pyramid = 3 * np.arctan(np.sqrt(2))
        geometric_factor = np.cos(theta_pyramid)**4  # ≈ 0.0439
        logistic_term = 1.0 - np.tanh(beta * (R - Theta))
        return V0 * logistic_term * geometric_factor
