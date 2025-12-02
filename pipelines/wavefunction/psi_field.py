"""Ψ-Field computation for V6 entropic wave function.

This module implements the genesis wave function ψ_genesis(r,θ,φ,t) and provides
utilities for collapsing it to UTAC regime probability distributions.

Reference: releases/V6-Plans_etc/V6_Wellenfunktions_Integrationsplan.md
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

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
    l_planck: float = PLANCK_LENGTH  # Legacy alias
    planck_energy: float = PLANCK_ENERGY
    e_planck: float = PLANCK_ENERGY  # Legacy alias
    hbar: float = HBAR
    normalization: float = 1.0
    normalize: bool = True
    use_tetrahedral: bool = True
    notes: list = field(
        default_factory=lambda: ["V6 entropic wavefunction", "Tetrahedral symmetry enabled"]
    )


class PsiField:
    """Entropic wave function field for V6 framework.

    Implements: ψ_genesis(r,θ,φ,t) = N · exp(-α⁻¹·r²/ℓ²_P) · Y_tetra(θ,φ) · exp(-i·Φ·E_P·t/ℏ)
    """

    def __init__(self, config: PsiFieldConfig | None = None):
        self.config = config or PsiFieldConfig()

    def _radial_component(self, r):
        """Compute radial component: exp(-α⁻¹·r²/ℓ²_P)"""
        return np.exp(-self.config.alpha_inv * (r / self.config.planck_length) ** 2)

    def _angular_component(self, theta, phi):
        """Compute angular component with tetrahedral symmetry Y_tetra(θ,φ)"""
        if not self.config.use_tetrahedral:
            return 1.0
        # Tetrahedral symmetry approximation
        return 1.0 + 0.5 * np.cos(4 * phi) * np.sin(theta - np.arccos(-1 / 3)) ** 2

    def _time_component(self, t):
        """Compute time component: exp(-i·Φ·E_P·t/ℏ)"""
        return np.exp(-1j * self.config.phi * self.config.planck_energy * t / self.config.hbar)

    def compute_wavefunction(self, r, theta=np.pi / 2, phi=0, t=0):
        """Compute full ψ_genesis wave function."""
        spatial = self._radial_component(r)
        angular = self._angular_component(theta, phi)
        temporal = self._time_component(t)

        psi = spatial * angular * temporal

        if self.config.normalize:
            psi = psi * self.config.normalization

        return psi

    def collapse_to_utac(self, r_vals=None, theta=np.pi / 2, phi=0, t=0):
        """Collapse wave function to UTAC probability: P(R) = |ψ|²."""
        if r_vals is None:
            r_vals = np.linspace(0, 10, 100)

        psi = self.compute_wavefunction(r_vals, theta, phi, t)
        prob_density = np.abs(psi) ** 2

        # Normalize
        dr = r_vals[1] - r_vals[0] if len(r_vals) > 1 else 1.0
        norm = np.sum(prob_density * r_vals**2 * dr) * 4 * np.pi
        if norm > 0:
            prob_density = prob_density / norm

        # Compute expectation values
        mean_r = np.sum(prob_density * r_vals**3 * dr) * 4 * np.pi
        mean_r2 = np.sum(prob_density * r_vals**4 * dr) * 4 * np.pi
        delta_r = np.sqrt(mean_r2 - mean_r**2)

        return {
            "r": r_vals,
            "probability_density": prob_density,
            "mean_r": mean_r,
            "delta_r": delta_r,
        }

    def compute_entropy(self, r_vals=None):
        """Compute von Neumann entropy S = -Σ p_i ln(p_i)"""
        if r_vals is None:
            r_vals = np.linspace(0.1, 10, 100)

        result = self.collapse_to_utac(r_vals)
        p = result["probability_density"]

        # Avoid log(0)
        p = p[p > 1e-15]

        if len(p) == 0:
            return 0.0

        return -np.sum(p * np.log(p + 1e-15))

    def compute_pyramidal_potential(
        self, R: float, Theta: float, beta: float, V0: float = 1.0
    ) -> float:
        """Compute V_pyr(R,Θ) = V_0 · [1 - tanh(β(R-Θ))] · cos⁴(3·arctan(√2))."""
        theta_pyramid = 3 * np.arctan(np.sqrt(2))
        geometric_factor = np.cos(theta_pyramid) ** 4  # ≈ 0.0439
        logistic_term = 1.0 - np.tanh(beta * (R - Theta))
        return V0 * logistic_term * geometric_factor


# Legacy aliases for backward compatibility
L_PLANCK = PLANCK_LENGTH
E_PLANCK = PLANCK_ENERGY


class PsiFieldPipeline:
    """Pipeline for complete ψ-field workflow with UTAC integration."""

    def __init__(self, config: PsiFieldConfig | None = None):
        self.config = config or PsiFieldConfig()
        self.field = PsiField(self.config)

    def run(self, r_grid=None, theta_grid=None, phi_grid=None, t_vals=None):
        """Run complete pipeline."""
        if r_grid is None:
            r_grid = np.linspace(0.1, 10, 50)
        if theta_grid is None:
            theta_grid = np.array([np.pi / 2])
        if phi_grid is None:
            phi_grid = np.array([0])
        if t_vals is None:
            t_vals = np.array([0])

        results = {
            "r_grid": r_grid,
            "theta_grid": theta_grid,
            "phi_grid": phi_grid,
            "t_vals": t_vals,
            "wavefunction": [],
            "probability": [],
            "entropy": [],
        }

        for t in t_vals:
            psi_t = []
            for theta in theta_grid:
                for phi in phi_grid:
                    psi = self.field.compute_wavefunction(r_grid, theta, phi, t)
                    psi_t.append(psi)

            results["wavefunction"].append(psi_t)

            # Compute probability and entropy
            utac = self.field.collapse_to_utac(r_grid)
            results["probability"].append(utac)
            results["entropy"].append(self.field.compute_entropy(r_grid))

        return results


def compute_psi_genesis(
    r, theta=np.pi / 2, phi=0, t=0, config=None, alpha_inv=None, phi_const=None
):
    """Convenience function for quick ψ_genesis computation.

    Args:
        r: Radial distance (float or array)
        theta: Polar angle (default: π/2, equatorial)
        phi: Azimuthal angle (default: 0)
        t: Time (default: 0)
        config: Optional PsiFieldConfig
        alpha_inv: Override α⁻¹ value
        phi_const: Override Φ value

    Returns:
        Complex wavefunction value(s)
    """
    if config is None:
        config = PsiFieldConfig()
        if alpha_inv is not None:
            config.alpha_inv = alpha_inv
        if phi_const is not None:
            config.phi = phi_const

    field = PsiField(config)
    return field.compute_wavefunction(r, theta, phi, t)
