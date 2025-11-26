"""Ψ-Wellenfunktions-Pipeline für V6 Framework.

Implementiert die entropische Wellenfunktion ψ_genesis, die den Kollaps vom Punkt
zur 3D-Struktur beschreibt. Diese Pipeline integriert sich in den UTAC-Framework
und verbindet Quantenmechanik mit entropischer Governance.

Key Components:
---------------
1. ψ_genesis(r,θ,φ,t): Entropische Wellenfunktion mit α⁻¹ und Φ
2. |ψ|² → P(R) Mapping: Wahrscheinlichkeitsdichte zu UTAC-R Parameter
3. Integration mit genesis_cube.py und Simulator Output

Theoretische Grundlage:
-----------------------
- GrundPrinzip Simulation.txt (Wellenfunktions-Herleitung)
- Zusatz_bitte_integrieren!.txt (Kino-Modell + Δt_Q Empirie)
- V6_Wellenfunktions_Integrationsplan.md

Version: v6.0.0-alpha
Authors: Johann Benjamin Römer, MOR Framework
"""

from __future__ import annotations

import math
from typing import Dict, Tuple, Optional, Callable
from dataclasses import dataclass, field
import numpy as np
from scipy.special import sph_harm

# Import V6 constants
try:
    from models.unified_constants import (
        ALPHA_INV,
        PHI,
        C_LIGHT_M_S,
        V_RIG_DEFAULT,
        calculate_vrig,
    )
except ImportError:
    # Fallback constants if models not available
    ALPHA_INV = 137.036
    PHI = (1 + math.sqrt(5)) / 2
    C_LIGHT_M_S = 299792458.0
    V_RIG_DEFAULT = C_LIGHT_M_S / 1000 / (ALPHA_INV * PHI)


# Physical constants
L_PLANCK = 1.616e-35  # Planck length (m)
E_PLANCK = 1.956e9    # Planck energy (J)
HBAR = 1.055e-34      # Reduced Planck constant (J·s)


@dataclass
class PsiFieldConfig:
    """Configuration for Ψ-field computation."""

    alpha_inv: float = ALPHA_INV  # Fine-structure constant inverse
    phi: float = PHI  # Golden ratio
    l_planck: float = L_PLANCK  # Planck length scale
    e_planck: float = E_PLANCK  # Planck energy scale

    # Tetrahedral symmetry parameters
    use_tetrahedral: bool = True
    n_tetra_modes: int = 4  # Number of tetrahedral harmonic modes

    # Normalization
    normalize: bool = True

    notes: list = field(default_factory=lambda: [
        "ψ_genesis = N·exp(-α⁻¹·r²/ℓ²_P)·Y_tetra(θ,φ)·exp(-iΦ·E_P·t/ℏ)",
        "Combines radial collapse, tetrahedral symmetry, golden-ratio oscillation",
        "Maps to UTAC via |ψ|² → P(R) probability density"
    ])


class PsiField:
    """Entropische Wellenfunktion für pyramidale Genesis.

    Die Wellenfunktion ψ_genesis beschreibt den Kollaps eines Punktes in sich selbst,
    wobei durch Interferenz die "3 Strings" (tetraedrische Knoten) entstehen.

    Form:
        ψ(r,θ,φ,t) = N · ψ_radial(r) · ψ_angular(θ,φ) · ψ_time(t)

    Components:
        - ψ_radial: Gaußscher Kollaps mit α⁻¹ Dämpfung
        - ψ_angular: Tetraeder-Symmetrie (Kugelflächenfunktionen)
        - ψ_time: Φ-modulierte Planck-Energie-Oszillation
    """

    def __init__(self, config: Optional[PsiFieldConfig] = None):
        """Initialize Ψ-field with configuration.

        Parameters
        ----------
        config : PsiFieldConfig, optional
            Field configuration (uses defaults if not provided)
        """
        self.config = config or PsiFieldConfig()
        self._normalization = None

    def compute_wavefunction(
        self,
        r: np.ndarray | float,
        theta: np.ndarray | float,
        phi: np.ndarray | float,
        t: np.ndarray | float = 0.0,
    ) -> np.ndarray | complex:
        """Compute ψ_genesis(r,θ,φ,t).

        Parameters
        ----------
        r : array_like
            Radial coordinate (in Planck lengths)
        theta : array_like
            Polar angle [0, π]
        phi : array_like
            Azimuthal angle [0, 2π]
        t : array_like, optional
            Time coordinate (in Planck times)

        Returns
        -------
        complex array
            Complex-valued wavefunction ψ(r,θ,φ,t)

        Notes
        -----
        Formula:
            ψ = N · exp(-α⁻¹·r²/ℓ²_P) · Y_tetra(θ,φ) · exp(-iΦ·E_P·t/ℏ)
        """
        # Ensure arrays
        r = np.atleast_1d(r)
        theta = np.atleast_1d(theta)
        phi = np.atleast_1d(phi)
        t = np.atleast_1d(t)

        # Components
        psi_radial = self._radial_component(r)
        psi_angular = self._angular_component(theta, phi)
        psi_time = self._time_component(t)

        # Combine (broadcasting handles different array shapes)
        psi = psi_radial * psi_angular * psi_time

        # Normalization
        if self.config.normalize and self._normalization is None:
            self._compute_normalization()

        if self.config.normalize:
            psi = psi / np.sqrt(self._normalization)

        return psi

    def _radial_component(self, r: np.ndarray) -> np.ndarray:
        """Radial component: exp(-α⁻¹·r²/ℓ²_P).

        Gaussian collapse with fine-structure damping.
        """
        alpha_inv = self.config.alpha_inv
        l_p = self.config.l_planck

        return np.exp(-alpha_inv * r**2 / l_p**2)

    def _angular_component(self, theta: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Angular component: Y_tetra(θ,φ).

        Tetrahedral symmetry using spherical harmonics.
        For tetrahedron (T_d symmetry), use combination of Y_lm modes.

        Simplified: Superposition of l=2 spherical harmonics
        that respect tetrahedral point group.
        """
        if not self.config.use_tetrahedral:
            return np.ones_like(theta)

        # Tetrahedral harmonics (approximation using l=2)
        # True tetrahedral requires proper group theory decomposition
        # Here we use a simplified physically-motivated form

        # Combine multiple m-modes for tetrahedral symmetry
        y_angular = np.zeros_like(theta, dtype=complex)

        # l=0: s-wave (spherical)
        y_angular += sph_harm(0, 0, phi, theta).real

        # l=2, m=0: Contributes to tetrahedral pattern
        y_angular += 0.5 * sph_harm(0, 2, phi, theta).real

        # l=3: Cubic harmonics (tetrahedral subgroup)
        # Simplified approximation
        y_angular += 0.3 * (
            np.sin(theta)**2 * np.cos(2*phi) +
            np.cos(theta)**2 * np.sin(3*phi)
        )

        return y_angular

    def _time_component(self, t: np.ndarray) -> np.ndarray:
        """Time component: exp(-iΦ·E_P·t/ℏ).

        Golden-ratio modulated Planck energy oscillation.
        """
        phi_golden = self.config.phi
        e_p = self.config.e_planck
        hbar = HBAR

        # Frequency: ω = Φ·E_P/ℏ
        omega = phi_golden * e_p / hbar

        return np.exp(-1j * omega * t)

    def _compute_normalization(self) -> None:
        """Compute normalization constant for ψ.

        Requires numerical integration over r, θ, φ.
        """
        # Simplified: Approximate normalization
        # For Gaussian: ∫ exp(-αr²/ℓ²) r² dr ∝ (ℓ/√α)³
        alpha_inv = self.config.alpha_inv
        l_p = self.config.l_planck

        # Radial integral (Gaussian)
        radial_norm = (l_p / np.sqrt(alpha_inv))**3

        # Angular integral (spherical harmonics are normalized)
        angular_norm = 4 * np.pi  # Full solid angle

        self._normalization = radial_norm * angular_norm

    def collapse_to_utac(
        self,
        psi: np.ndarray,
        r_grid: np.ndarray,
    ) -> Dict[str, np.ndarray]:
        """Collapse |ψ|² → P(R) mapping for UTAC integration.

        Maps quantum probability density to UTAC regime parameter R.

        Parameters
        ----------
        psi : complex array
            Wavefunction values
        r_grid : array
            Radial grid corresponding to psi

        Returns
        -------
        dict
            - 'probability_density': |ψ|²
            - 'radial_distribution': P(r) = r²|ψ|²
            - 'mean_r': <r> expectation value
            - 'delta_r': √(<r²> - <r>²) uncertainty
        """
        # Probability density
        prob_density = np.abs(psi)**2

        # Radial distribution P(r) = r² |ψ|² (Jacobian for spherical)
        radial_dist = r_grid**2 * prob_density

        # Normalize radial distribution
        norm = np.trapz(radial_dist, r_grid)
        if norm > 0:
            radial_dist = radial_dist / norm

        # Expectation values
        mean_r = np.trapz(r_grid * radial_dist, r_grid)
        mean_r2 = np.trapz(r_grid**2 * radial_dist, r_grid)
        delta_r = np.sqrt(mean_r2 - mean_r**2)

        return {
            'probability_density': prob_density,
            'radial_distribution': radial_dist,
            'mean_r': mean_r,
            'delta_r': delta_r,
        }

    def compute_entropy(self, psi: np.ndarray) -> float:
        """Compute von Neumann entropy of ψ.

        S = -Tr(ρ log ρ) where ρ = |ψ⟩⟨ψ|

        For pure state: S = 0 (but we compute configurational entropy)
        """
        prob = np.abs(psi)**2
        prob = prob / np.sum(prob)  # Normalize

        # Shannon entropy (classical limit)
        prob_nonzero = prob[prob > 1e-12]
        entropy = -np.sum(prob_nonzero * np.log(prob_nonzero))

        return entropy


class PsiFieldPipeline:
    """Pipeline für Ψ-gestützte UTAC-Integration.

    Workflow:
    ---------
    1. Compute ψ_genesis on spatial grid
    2. Collapse to UTAC probability P(R)
    3. Output to Simulator metrics (|ψ|², ΔS)
    4. Integrate with genesis_cube.py
    """

    def __init__(self, config: Optional[PsiFieldConfig] = None):
        """Initialize pipeline.

        Parameters
        ----------
        config : PsiFieldConfig, optional
            Field configuration
        """
        self.psi_field = PsiField(config)
        self.config = config or PsiFieldConfig()

    def run(
        self,
        r_max: float = 10.0,
        n_points: int = 100,
        theta_phi_res: int = 20,
        t: float = 0.0,
    ) -> Dict[str, np.ndarray]:
        """Run complete Ψ-field pipeline.

        Parameters
        ----------
        r_max : float
            Maximum radius (in Planck lengths)
        n_points : int
            Number of radial grid points
        theta_phi_res : int
            Angular resolution (NxN grid)
        t : float
            Time point (in Planck times)

        Returns
        -------
        dict
            Pipeline outputs:
            - 'r_grid', 'theta_grid', 'phi_grid': Coordinate grids
            - 'psi': Complex wavefunction
            - 'probability_density': |ψ|²
            - 'radial_distribution': P(r)
            - 'mean_r', 'delta_r': Statistics
            - 'entropy': Von Neumann entropy
        """
        # Create grids
        r_grid = np.linspace(0, r_max, n_points)
        theta_grid = np.linspace(0, np.pi, theta_phi_res)
        phi_grid = np.linspace(0, 2*np.pi, theta_phi_res)

        # Meshgrid for full 3D
        R, Theta, Phi = np.meshgrid(r_grid, theta_grid, phi_grid, indexing='ij')

        # Compute wavefunction
        psi = self.psi_field.compute_wavefunction(R, Theta, Phi, t)

        # Collapse to UTAC
        # Average over angular dimensions for radial profile
        psi_radial = np.mean(np.abs(psi)**2, axis=(1, 2))
        utac_mapping = self.psi_field.collapse_to_utac(
            np.sqrt(psi_radial),  # Convert back to amplitude
            r_grid
        )

        # Compute entropy
        entropy = self.psi_field.compute_entropy(psi)

        return {
            'r_grid': r_grid,
            'theta_grid': theta_grid,
            'phi_grid': phi_grid,
            'psi': psi,
            **utac_mapping,
            'entropy': entropy,
        }


# Convenience function
def compute_psi_genesis(
    r: float | np.ndarray,
    theta: float | np.ndarray = 0.0,
    phi: float | np.ndarray = 0.0,
    t: float | np.ndarray = 0.0,
    alpha_inv: float = ALPHA_INV,
    phi_golden: float = PHI,
) -> complex | np.ndarray:
    """Convenience function to compute ψ_genesis.

    Quick access without class instantiation.

    Parameters
    ----------
    r, theta, phi, t : array_like
        Coordinates (r in Planck lengths, t in Planck times)
    alpha_inv : float
        Fine-structure constant inverse
    phi_golden : float
        Golden ratio

    Returns
    -------
    complex array
        ψ(r,θ,φ,t)

    Examples
    --------
    >>> r = np.linspace(0, 10, 100)
    >>> psi = compute_psi_genesis(r, theta=np.pi/2, phi=0)
    >>> prob_density = np.abs(psi)**2
    """
    config = PsiFieldConfig(alpha_inv=alpha_inv, phi=phi_golden)
    field = PsiField(config)
    return field.compute_wavefunction(r, theta, phi, t)


# For direct execution
if __name__ == '__main__':
    print("=" * 70)
    print("Ψ-FIELD GENESIS PIPELINE — V6 Framework")
    print("=" * 70)
    print()

    # Run pipeline
    pipeline = PsiFieldPipeline()

    print("Computing ψ_genesis(r,θ,φ,t=0)...")
    results = pipeline.run(r_max=10.0, n_points=100, theta_phi_res=20)

    print(f"  ✓ Wavefunction shape: {results['psi'].shape}")
    print(f"  ✓ <r> = {results['mean_r']:.4f} ℓ_P")
    print(f"  ✓ Δr = {results['delta_r']:.4f} ℓ_P")
    print(f"  ✓ Entropy S = {results['entropy']:.4f}")
    print()

    # Test collapse at t=0
    r_test = np.array([0.5, 1.0, 2.0, 5.0])
    psi_test = compute_psi_genesis(r_test, theta=np.pi/4, phi=0.0)
    prob_test = np.abs(psi_test)**2

    print("-" * 70)
    print("RADIAL PROBABILITY PROFILE")
    print("-" * 70)
    print(f"{'r (ℓ_P)':<15} {'|ψ|²':<20} {'Phase (rad)':<15}")
    print("-" * 70)
    for r_val, psi_val in zip(r_test, psi_test):
        phase = np.angle(psi_val)
        prob = np.abs(psi_val)**2
        print(f"{r_val:<15.2f} {prob:<20.6e} {phase:<15.4f}")
    print()

    print("=" * 70)
    print("Pipeline complete! Use results for UTAC integration.")
    print("=" * 70)
