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
PLANCK_ENERGY_GEV = 1.22e19  # GeV
PLANCK_ENERGY = PLANCK_ENERGY_GEV * 1.602e-10  # Convert to Joules (≈1.95e9 J)
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
    n_tetra_modes: int = 4  # Number of tetrahedral modes
    notes: list = field(
        default_factory=lambda: [
            "ψ_genesis entropic wavefunction with tetrahedral symmetry",
            "Implements: ψ = N·exp(-α⁻¹·r²/ℓ²_P)·Y_tetra(θ,φ)·exp(-iΦ·E_P·t/ℏ)",
        ]
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

    def collapse_to_utac(self, psi=None, r_vals=None, theta=np.pi / 2, phi=0, t=0):
        """Collapse wave function to UTAC probability: P(R) = |ψ|².

        Args:
            psi: Pre-computed wavefunction array (optional)
            r_vals: Radial grid values (optional)
            theta, phi, t: Coordinates for wavefunction computation if psi not provided

        Returns:
            dict with probability_density, radial_distribution, mean_r, delta_r
        """
        if r_vals is None:
            r_vals = np.linspace(0, 10, 100)

        if psi is None:
            psi = self.compute_wavefunction(r_vals, theta, phi, t)

        prob_density = np.abs(psi) ** 2

        # Normalize
        dr = r_vals[1] - r_vals[0] if len(r_vals) > 1 else 1.0
        norm = np.sum(prob_density * r_vals**2 * dr) * 4 * np.pi
        if norm > 0:
            prob_density = prob_density / norm

        # Radial distribution P(r) = 4πr² |ψ(r)|²
        radial_distribution = 4 * np.pi * r_vals**2 * prob_density

        # Renormalize radial distribution
        radial_norm = np.trapezoid(radial_distribution, r_vals)
        if radial_norm > 0:
            radial_distribution = radial_distribution / radial_norm

        # Compute expectation values using radial distribution
        mean_r = np.trapezoid(radial_distribution * r_vals, r_vals)
        mean_r2 = np.trapezoid(radial_distribution * r_vals**2, r_vals)
        delta_r = np.sqrt(np.abs(mean_r2 - mean_r**2))

        return {
            "probability_density": prob_density,
            "radial_distribution": radial_distribution,
            "mean_r": float(np.real(mean_r)),
            "delta_r": float(np.real(delta_r)),
        }

    def compute_entropy(self, psi=None, r_vals=None):
        """Compute von Neumann entropy S = -Σ p_i ln(p_i).

        Args:
            psi: Pre-computed wavefunction (optional, if array-like also sets r_vals size)
            r_vals: Radial grid (optional)

        Returns:
            Non-negative entropy value
        """
        # If psi is provided but r_vals is not, infer r_vals from psi shape
        if psi is not None and r_vals is None:
            psi = np.asarray(psi)
            n_points = len(psi)
            r_vals = np.linspace(0.1, 10, n_points)
        elif r_vals is None:
            r_vals = np.linspace(0.1, 10, 100)

        result = self.collapse_to_utac(psi=psi, r_vals=r_vals)
        p = result["radial_distribution"]

        # Ensure proper normalization
        p_sum = np.trapezoid(p, r_vals)
        if p_sum > 0:
            p = p / p_sum

        # Filter out near-zero probabilities
        p = p[p > 1e-15]

        if len(p) == 0:
            return 0.0

        # Normalize discrete probabilities
        p = p / np.sum(p)

        # Compute entropy (always non-negative for normalized p)
        entropy = -np.sum(p * np.log(p + 1e-15))

        # Ensure non-negative (handle floating point errors)
        return float(np.real(max(0.0, entropy)))

    def compute_pyramidal_potential(
        self, R: float, Theta: float, beta: float, V0: float = 1.0
    ) -> float:
        """Compute V_pyr(R,Θ) = V_0 · [1 - tanh(β(R-Θ))] · cos⁴(3·arctan(√2))."""
        theta_pyramid = 3 * np.arctan(np.sqrt(2))
        geometric_factor = np.cos(theta_pyramid) ** 4  # ≈ 0.0439
        logistic_term = 1.0 - np.tanh(beta * (R - Theta))
        return V0 * logistic_term * geometric_factor

    def compute_waste_wavefunction(
        self, x: float | np.ndarray, n_modes: int = 10
    ) -> float | np.ndarray:
        """Compute ψ_waste(x) = Σ_n (1/Φⁿ) · sin(α⁻¹ · k_n · x).

        This describes quantum fluctuations in the Verschnitt (waste) volume between
        spheres, providing a geometric origin for dark energy.

        Args:
            x: Spatial coordinate (or array)
            n_modes: Number of Fourier modes to include (default: 10)

        Returns:
            Waste wavefunction value(s)

        Physical interpretation:
        - Fourier series with Φ-damping: each "octave" damped by golden ratio
        - k_n ~ α⁻¹: Wave numbers scaled by fine structure constant
        - sin(...): Standing waves in "void" between spheres
        - Zero-point energy = Dark energy
        - Φ-damping prevents UV catastrophe
        """
        psi_waste = np.zeros_like(x, dtype=float)

        for n in range(1, n_modes + 1):
            # Wave number: k_n ~ α⁻¹ (scaled by mode number)
            k_n = self.config.alpha_inv * n

            # Φ-damping factor: 1/Φⁿ
            phi_damping = 1.0 / (self.config.phi**n)

            # Add Fourier mode
            psi_waste += phi_damping * np.sin(k_n * x)

        return psi_waste


# Legacy aliases for backward compatibility
L_PLANCK = PLANCK_LENGTH
E_PLANCK = PLANCK_ENERGY


class PsiFieldPipeline:
    """Pipeline for complete ψ-field workflow with UTAC integration."""

    def __init__(self, config: PsiFieldConfig | None = None):
        self.config = config or PsiFieldConfig()
        self.field = PsiField(self.config)

    def run(
        self,
        r_grid=None,
        theta_grid=None,
        phi_grid=None,
        t_vals=None,
        r_max=None,
        n_points=None,
        theta_phi_res=None,
        t=None,
    ):
        """Run complete pipeline.

        Args:
            r_grid: Radial grid (or use r_max/n_points)
            theta_grid: Theta grid (or use theta_phi_res)
            phi_grid: Phi grid (or use theta_phi_res)
            t_vals: Time values array (or use t scalar)
            r_max: Maximum radius (alternative to r_grid)
            n_points: Number of radial points (alternative to r_grid)
            theta_phi_res: Angular resolution (alternative to theta_grid/phi_grid)
            t: Single time value (alternative to t_vals)

        Returns:
            dict with r_grid, theta_grid, phi_grid, psi, probability_density,
            radial_distribution, mean_r, delta_r, entropy
        """
        # Handle alternative parameter formats
        if r_grid is None:
            if r_max is not None and n_points is not None:
                r_grid = np.linspace(0, r_max, n_points)
            else:
                r_grid = np.linspace(0.1, 10, 50)

        if theta_grid is None:
            if theta_phi_res is not None:
                theta_grid = np.linspace(0, np.pi, theta_phi_res)
            else:
                theta_grid = np.array([np.pi / 2])

        if phi_grid is None:
            if theta_phi_res is not None:
                phi_grid = np.linspace(0, 2 * np.pi, theta_phi_res)
            else:
                phi_grid = np.array([0])

        if t_vals is None:
            if t is not None:
                t_vals = np.array([t])
            else:
                t_vals = np.array([0])

        # Compute wavefunction on 3D grid (r, theta, phi) at time t_vals[0]
        t_val = t_vals[0]
        psi_3d = np.zeros((len(r_grid), len(theta_grid), len(phi_grid)), dtype=complex)

        for i, r_val in enumerate(r_grid):
            for j, theta_val in enumerate(theta_grid):
                for k, phi_val in enumerate(phi_grid):
                    psi_3d[i, j, k] = self.field.compute_wavefunction(
                        r_val, theta_val, phi_val, t_val
                    )

        # Compute UTAC collapse and entropy using radial average
        psi_radial = psi_3d[:, 0, 0]  # Use equatorial slice
        utac = self.field.collapse_to_utac(psi=psi_radial, r_vals=r_grid)
        entropy = self.field.compute_entropy(psi=psi_radial, r_vals=r_grid)

        return {
            "r_grid": r_grid,
            "theta_grid": theta_grid,
            "phi_grid": phi_grid,
            "psi": psi_3d,
            "probability_density": utac["probability_density"],
            "radial_distribution": utac["radial_distribution"],
            "mean_r": utac["mean_r"],
            "delta_r": utac["delta_r"],
            "entropy": entropy,
        }


def compute_psi_genesis(
    r,
    theta=np.pi / 2,
    phi=0,
    t=0,
    config=None,
    alpha_inv=None,
    phi_const=None,
    phi_golden=None,
):
    """Convenience function for quick ψ_genesis computation.

    Args:
        r: Radial distance (float or array)
        theta: Polar angle (default: π/2, equatorial)
        phi: Azimuthal angle (default: 0)
        t: Time (default: 0)
        config: Optional PsiFieldConfig
        alpha_inv: Override α⁻¹ value
        phi_const: Override Φ value (same as phi_golden)
        phi_golden: Override Φ value (golden ratio, alias for phi_const)

    Returns:
        Complex wavefunction value(s)
    """
    if config is None:
        config = PsiFieldConfig()
        if alpha_inv is not None:
            config.alpha_inv = alpha_inv
        if phi_const is not None:
            config.phi = phi_const
        if phi_golden is not None:
            config.phi = phi_golden

    field = PsiField(config)
    return field.compute_wavefunction(r, theta, phi, t)
