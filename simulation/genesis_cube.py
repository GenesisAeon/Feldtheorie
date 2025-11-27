"""
Genesis Cube with Entropic Wavefunction

Formal:
    Provides a deterministische σ(β(R-Θ)) driver that seeds three orthogonal
    vectors from a vacuum-fluctuation phase, extrudes a cube, and projects it
    onto a hexagonal mid-membrane. The block-universe slices are parametrized
    by ζ(R) as damping so that implosion→expansion can be inspected without
    rendering dependencies.

    Extended with entropic wavefunction Ψ(r,θ,φ,t) that couples geometric
    frustration to gravitation via the holographic principle and emergent gravity.

Empirical:
    Returns structured dictionaries with vectors, cube vertices, hexagon
    projections, and slice-wise coupling values. These outputs can feed
    notebooks for ΔAIC/CI checks against null models (random vectors or β→∞).

    Wavefunction outputs include |Ψ|² (probability density), ΔS (entropy gradient),
    and phase information for visualization.

Poetic:
    Ein Punkt atmet ein, streckt drei Fäden in die Dämmerung, faltet sich zum
    Würfel auf der Ecke und wirft sein sechseckiges Echo auf die Membran, während
    σ(β(R-Θ)) den Puls zwischen Nichts und Raumzeit zählt. Die Wellenfunktion Ψ
    trägt die Entropie des Verschnitts und gebiert Gravitation aus dem geometrischen
    Zwang.
"""
from __future__ import annotations

import math
import cmath
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence, Tuple, Optional
import numpy as np

from models.utac_type6_implosive import cubic_root_jump, inverted_sigmoid, tau_star

# Import PsiFieldPipeline for advanced wavefunction computation
try:
    from pipelines.wavefunction.psi_field import PsiFieldPipeline, PsiFieldConfig
    PSIFIELD_AVAILABLE = True
except ImportError:
    PSIFIELD_AVAILABLE = False


# Physical constants for entropic wavefunction
ALPHA_INV = 137.036  # Fine structure constant α⁻¹
PHI_GOLDEN = 1.618034  # Golden ratio Φ
L_PLANCK = 1.616e-35  # Planck length (m)
E_PLANCK = 1.956e9  # Planck energy (J)
HBAR = 1.055e-34  # Reduced Planck constant (J·s)


@dataclass
class GenesisCubeConfig:
    """Configuration for the GenesisCube engine."""

    beta: float = 4.8
    theta: float = 0.0
    damping: float = 0.04
    expansion_rate: float = 1.015
    slice_count: int = 24
    fluctuation_phase: float = 0.137
    # Wavefunction parameters
    enable_wavefunction: bool = True
    wavefunction_resolution: int = 32  # Grid resolution for Ψ computation
    time_steps: int = 100  # RK4 integration steps
    dt: float = 1e-44  # Time step in Planck units
    # Integration with PsiFieldPipeline
    use_psifield_pipeline: bool = False  # Use advanced PsiFieldPipeline if True
    notes: List[str] = field(default_factory=lambda: [
        "σ(β(R-Θ)) steuert die Aktivierungsschärfe",
        "ζ(R) dämpft die implosiv→expansive Übergangskurve",
        "Ψ(r,θ,φ,t) koppelt Entropie an Gravitation via holographisches Prinzip",
    ])


class GenesisCube:
    """Generate cube-to-hexagon slices driven by σ(β(R-Θ))."""

    def __init__(self, config: GenesisCubeConfig | None = None) -> None:
        self.config = config or GenesisCubeConfig()

        # Initialize PsiFieldPipeline if requested and available
        self.psi_pipeline = None
        if self.config.use_psifield_pipeline and PSIFIELD_AVAILABLE:
            psi_config = PsiFieldConfig(
                alpha_inv=ALPHA_INV,
                phi=PHI_GOLDEN,
                l_planck=L_PLANCK,
                e_planck=E_PLANCK,
                use_tetrahedral=True,
                normalize=True,
            )
            self.psi_pipeline = PsiFieldPipeline(psi_config)

    def sigma(self, r: float) -> float:
        """Compute σ(β(R-Θ)) for a given field coordinate R."""

        theta = self.config.theta if self.config.theta != 0 else 1e-6
        beta = cubic_root_jump(r, theta, beta_base=self.config.beta, k=6.5)
        return float(inverted_sigmoid(r, theta, beta))

    def _normalized(self, vector: Sequence[float]) -> Tuple[float, float, float]:
        x, y, z = vector
        norm = math.sqrt(x * x + y * y + z * z)
        if norm == 0:
            return 0.0, 0.0, 0.0
        return x / norm, y / norm, z / norm

    def seed_vectors(self, fluctuation_phase: float | None = None) -> List[Tuple[float, float, float]]:
        """Create three orthogonal-ish vectors from a fluctuation seed."""

        phase = fluctuation_phase if fluctuation_phase is not None else self.config.fluctuation_phase
        base_vectors = [
            (math.sin(phase), math.cos(phase), 1.0),
            (math.cos(phase * 2.0), 1.0, -math.sin(phase * 2.0)),
            (1.0, -math.sin(phase * 3.0), math.cos(phase * 3.0)),
        ]
        return [self._normalized(vec) for vec in base_vectors]

    def cube_vertices(self, scale: float = 1.0, fluctuation_phase: float | None = None) -> List[Tuple[float, float, float]]:
        """Construct cube vertices using seeded vectors."""

        axes = self.seed_vectors(fluctuation_phase)
        vertices: List[Tuple[float, float, float]] = []
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                for sz in (-1.0, 1.0):
                    vx = sx * axes[0][0] + sy * axes[1][0] + sz * axes[2][0]
                    vy = sx * axes[0][1] + sy * axes[1][1] + sz * axes[2][1]
                    vz = sx * axes[0][2] + sy * axes[1][2] + sz * axes[2][2]
                    vertices.append((scale * vx, scale * vy, scale * vz))
        return vertices

    def project_hexagon(self, scale: float = 1.0, fluctuation_phase: float | None = None) -> List[Tuple[float, float]]:
        """Project cube vertices to a hexagon-like footprint on the mid-membrane."""

        vertices = self.cube_vertices(scale=scale, fluctuation_phase=fluctuation_phase)
        footprint = []
        for vx, vy, vz in vertices:
            u = vx - vz
            v = vy - vz
            footprint.append((u, v))
        unique = []
        for u, v in footprint:
            if all(abs(u - a) > 1e-6 or abs(v - b) > 1e-6 for a, b in unique):
                unique.append((u, v))
        # Select first 6 unique vertices to sketch a hexagon outline
        return unique[:6]

    def block_universe_slices(self, r_values: Iterable[float] | None = None) -> List[Dict[str, object]]:
        """Generate slice-wise states across R with σ(β(R-Θ)) and ζ(R) damping."""

        if r_values is None:
            r_values = [i / max(1, self.config.slice_count - 1) for i in range(self.config.slice_count)]

        slices: List[Dict[str, object]] = []
        for idx, r in enumerate(r_values):
            theta = self.config.theta if self.config.theta != 0 else 1e-6
            beta = cubic_root_jump(r, theta, beta_base=self.config.beta, k=6.5)
            coupling = float(inverted_sigmoid(r, theta, beta))
            delay = float(tau_star(r, theta, beta))
            damping = (1.0 - self.config.damping) ** idx
            scale = damping * (1.0 + coupling * self.config.expansion_rate)
            slices.append(
                {
                    "R": r,
                    "sigma": coupling,
                    "beta": beta,
                    "tau_star": delay,
                    "zeta": damping,
                    "scale": scale,
                    "hexagon": self.project_hexagon(scale=scale),
                }
            )
        return slices

    def as_dict(self) -> Dict[str, object]:
        """Expose a configuration snapshot suitable for JSON/Trilayer exports."""

        return {
            "config": self.config,
            "seed_vectors": self.seed_vectors(),
            "hexagon_preview": self.project_hexagon(),
            "slices": self.block_universe_slices(),
        }

    # ========== Entropic Wavefunction Extension ==========

    def compute_tetrahedral_harmonics(self, theta: float | np.ndarray, phi: float | np.ndarray) -> complex | np.ndarray:
        """
        Tetrahedral angular harmonics Y_tetra(θ,φ).

        Simplified form using T_d symmetry (tetrahedral group).
        Exact form would use Wigner-D matrices with tetrahedral irreps.

        Args:
            theta: Polar angle (0 to π)
            phi: Azimuthal angle (0 to 2π)

        Returns:
            Complex tetrahedral harmonic value(s)
        """
        # Tetrahedral binding angle: arccos(-1/3) ≈ 109.47°
        # Use combination of cos(3φ) and sin(3φ) for 3-fold symmetry
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)

        # Three-fold rotational symmetry in φ (for 3 strings)
        y_tetra = (cos_theta**2 * np.sin(3 * phi) +
                   sin_theta**2 * np.cos(3 * phi) +
                   1j * sin_theta * cos_theta * np.exp(1j * phi))

        return y_tetra

    def compute_wavefunction(
        self,
        r: float | np.ndarray,
        theta: float | np.ndarray,
        phi: float | np.ndarray,
        t: float,
    ) -> complex | np.ndarray:
        """
        Compute entropic genesis wavefunction Ψ(r,θ,φ,t).

        Ψ(r,θ,φ,t) = N · exp(-α⁻¹·r²/ℓ²_P) · Y_tetra(θ,φ) · exp(-iΦ·E_P·t/ℏ)

        Physical interpretation:
        - exp(-α⁻¹·r²): Feinstrukturkonstante steuert radialen Kollaps
        - Y_tetra(θ,φ): Tetraeder-Symmetrie erzeugt 3 String-Knoten
        - exp(-iΦ·E_P·t): Goldener Schnitt moduliert Planck-Oszillation

        Args:
            r: Radial coordinate (in Planck lengths)
            theta: Polar angle
            phi: Azimuthal angle
            t: Time (in Planck units)

        Returns:
            Complex wavefunction value(s) Ψ
        """
        # Radial component: Gaussian collapse driven by fine structure constant
        psi_radial = np.exp(-ALPHA_INV * r**2)

        # Angular component: Tetrahedral harmonics
        psi_angular = self.compute_tetrahedral_harmonics(theta, phi)

        # Time evolution: Golden ratio modulates Planck frequency
        omega = PHI_GOLDEN * E_PLANCK / HBAR
        psi_time = np.exp(-1j * omega * t)

        # Normalization factor (approximate)
        N = (ALPHA_INV / np.pi)**(3/4)

        return N * psi_radial * psi_angular * psi_time

    def compute_probability_density(
        self,
        r: float | np.ndarray,
        theta: float | np.ndarray,
        phi: float | np.ndarray,
        t: float,
    ) -> float | np.ndarray:
        """
        Compute probability density |Ψ(r,θ,φ,t)|².

        This represents the information density on the holographic screen.

        Args:
            r, theta, phi, t: Spacetime coordinates

        Returns:
            Real probability density |Ψ|²
        """
        psi = self.compute_wavefunction(r, theta, phi, t)
        return np.abs(psi)**2

    def compute_entropy_gradient(
        self,
        r: float | np.ndarray,
        theta: float | np.ndarray,
        phi: float | np.ndarray,
        t: float,
        dr: float = 1e-3,
    ) -> float | np.ndarray:
        """
        Compute entropy gradient ∇S from probability density.

        Via emergent gravity: F_grav ∝ T · ∇S
        The entropy is related to |Ψ|² via S ∝ ln(|Ψ|²)

        Args:
            r, theta, phi, t: Spacetime coordinates
            dr: Step size for numerical derivative

        Returns:
            Entropy gradient magnitude |∇S|
        """
        # Compute |Ψ|² at r and r+dr
        rho_0 = self.compute_probability_density(r, theta, phi, t)
        rho_1 = self.compute_probability_density(r + dr, theta, phi, t)

        # Entropy: S ∝ ln(ρ) (Boltzmann relation)
        # Avoid log(0) by adding small epsilon
        epsilon = 1e-30
        S_0 = np.log(rho_0 + epsilon)
        S_1 = np.log(rho_1 + epsilon)

        # Gradient (radial component only for simplicity)
        grad_S = (S_1 - S_0) / dr

        return grad_S

    def rk4_step(
        self,
        psi: np.ndarray,
        t: float,
        dt: float,
        r_grid: np.ndarray,
        theta_grid: np.ndarray,
        phi_grid: np.ndarray,
    ) -> np.ndarray:
        """
        Single RK4 integration step for wavefunction evolution.

        Solves: iℏ ∂Ψ/∂t = Ĥ Ψ
        where Ĥ = -ℏ²/(2m)∇² + V_pyr(r,Θ,β)

        Args:
            psi: Current wavefunction array
            t: Current time
            dt: Time step
            r_grid, theta_grid, phi_grid: Coordinate grids

        Returns:
            Updated wavefunction after one RK4 step
        """
        def dpsi_dt(psi_current: np.ndarray, time: float) -> np.ndarray:
            """Compute time derivative of wavefunction."""
            # Pyramidal potential: V_pyr = V_0 · [1 - tanh(β(R-Θ))]
            r_vals = np.abs(r_grid)
            V_0 = E_PLANCK  # Energy scale
            V_pyr = V_0 * (1.0 - np.tanh(self.config.beta * (r_vals - self.config.theta)))

            # Kinetic term: -ℏ²/(2m)∇² (simplified as Laplacian)
            # For proper implementation, use finite differences
            # Here we use a simplified decay term
            kinetic = -1j * E_PLANCK * psi_current / HBAR

            # Potential term
            potential = -1j * V_pyr * psi_current / HBAR

            return kinetic + potential

        # RK4 coefficients
        k1 = dpsi_dt(psi, t)
        k2 = dpsi_dt(psi + 0.5 * dt * k1, t + 0.5 * dt)
        k3 = dpsi_dt(psi + 0.5 * dt * k2, t + 0.5 * dt)
        k4 = dpsi_dt(psi + dt * k3, t + dt)

        # RK4 update
        psi_next = psi + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

        return psi_next

    def evolve_wavefunction(
        self,
        r_max: float = 10.0,
        save_every: int = 10,
    ) -> List[Dict[str, object]]:
        """
        Evolve wavefunction Ψ(r,θ,φ,t) using RK4 integration.

        Returns snapshots of |Ψ|², ΔS, and phase for visualization.

        Args:
            r_max: Maximum radial coordinate (in Planck lengths)
            save_every: Save snapshot every N time steps

        Returns:
            List of dicts with time, |Ψ|², ΔS, phase
        """
        if not self.config.enable_wavefunction:
            return []

        # Create spatial grid
        n = self.config.wavefunction_resolution
        r_1d = np.linspace(0, r_max, n)
        theta_1d = np.linspace(0, np.pi, n)
        phi_1d = np.linspace(0, 2*np.pi, n)

        # Use 1D arrays for efficiency (full 3D would be r×theta×phi)
        # Here we track radial profile for each slice
        r_grid = r_1d
        theta_grid = np.full_like(r_1d, np.pi/4)  # Fixed slice
        phi_grid = np.full_like(r_1d, 0.0)  # Fixed slice

        # Initialize wavefunction
        t = 0.0
        psi = self.compute_wavefunction(r_grid, theta_grid, phi_grid, t)

        snapshots = []

        # Time evolution loop
        for step in range(self.config.time_steps):
            t = step * self.config.dt

            # RK4 integration step
            psi = self.rk4_step(psi, t, self.config.dt, r_grid, theta_grid, phi_grid)

            # Save snapshot
            if step % save_every == 0:
                rho = np.abs(psi)**2
                grad_S = self.compute_entropy_gradient(r_grid, theta_grid, phi_grid, t)
                phase = np.angle(psi)

                snapshots.append({
                    "t": t,
                    "r": r_grid.tolist() if hasattr(r_grid, 'tolist') else list(r_grid),
                    "probability_density": rho.tolist() if hasattr(rho, 'tolist') else list(rho),
                    "entropy_gradient": grad_S.tolist() if hasattr(grad_S, 'tolist') else list(grad_S),
                    "phase": phase.tolist() if hasattr(phase, 'tolist') else list(phase),
                })

        return snapshots

    def compute_psifield_analysis(
        self,
        r_max: float = 10.0,
        n_points: int = 100,
        theta_phi_res: int = 20,
        t: float = 0.0,
    ) -> Optional[Dict[str, object]]:
        """
        Compute advanced wavefunction analysis using PsiFieldPipeline.

        This method integrates the PsiFieldPipeline (psi_field.py) with GenesisCube
        to provide:
        - Full 3D wavefunction ψ(r,θ,φ,t)
        - UTAC collapse mapping |ψ|² → P(R)
        - von Neumann entropy
        - Radial distribution statistics

        Args:
            r_max: Maximum radial coordinate (in Planck lengths)
            n_points: Number of radial grid points
            theta_phi_res: Angular resolution
            t: Time point (in Planck times)

        Returns:
            Dict with PsiFieldPipeline results, or None if pipeline not available

        Example:
            >>> config = GenesisCubeConfig(use_psifield_pipeline=True)
            >>> cube = GenesisCube(config)
            >>> results = cube.compute_psifield_analysis(r_max=5.0)
            >>> print(f"Entropy: {results['entropy']}")
            >>> print(f"Mean radius: {results['mean_r']} ℓ_P")
        """
        if self.psi_pipeline is None:
            if not PSIFIELD_AVAILABLE:
                print("Warning: PsiFieldPipeline not available (import failed)")
            else:
                print("Warning: PsiFieldPipeline not enabled (set use_psifield_pipeline=True)")
            return None

        # Run PsiFieldPipeline
        results = self.psi_pipeline.run(
            r_max=r_max,
            n_points=n_points,
            theta_phi_res=theta_phi_res,
            t=t,
        )

        # Add UTAC coupling via current GenesisCube state
        # Map mean_r to R coordinate for σ(β(R-Θ)) coupling
        mean_r = results['mean_r']
        delta_r = results['delta_r']

        # Convert Planck lengths to UTAC R parameter (normalized)
        # This is where quantum (Planck scale) meets classical (UTAC)
        r_normalized = mean_r / r_max  # Normalize to [0, 1]

        # Compute UTAC coupling at this R
        sigma_coupling = self.sigma(r_normalized)

        # Extend results with UTAC integration
        results['utac_coupling'] = {
            'R': r_normalized,
            'sigma': sigma_coupling,
            'mean_r_planck': mean_r,
            'delta_r_planck': delta_r,
            'beta': self.config.beta,
            'theta': self.config.theta,
        }

        return results

    def hybrid_evolution(
        self,
        r_max: float = 10.0,
        n_points: int = 50,
    ) -> Dict[str, object]:
        """
        Hybrid evolution combining:
        1. GenesisCube geometric slicing (block universe)
        2. PsiFieldPipeline quantum wavefunction (ψ_genesis)

        This represents the full V6 integration: Tesseract slicing + entropische Wellenfunktion.

        Args:
            r_max: Maximum radial extent
            n_points: Resolution

        Returns:
            Dict containing both geometric and quantum outputs
        """
        # 1. Geometric evolution (GenesisCube slices)
        r_values = np.linspace(0, 1, n_points)
        slices = self.block_universe_slices(r_values)

        # 2. Quantum evolution (PsiFieldPipeline)
        psi_results = None
        if self.psi_pipeline is not None:
            psi_results = self.psi_pipeline.run(
                r_max=r_max,
                n_points=n_points,
                theta_phi_res=16,
                t=0.0,
            )

        # 3. Combine outputs
        return {
            'geometric': {
                'slices': slices,
                'slice_count': len(slices),
                'config': self.config,
            },
            'quantum': psi_results,
            'integration': {
                'description': 'V6 Hybrid: Tesseract slicing + ψ_genesis wavefunction',
                'psifield_enabled': psi_results is not None,
                'r_max': r_max,
                'n_points': n_points,
            }
        }


__all__ = ["GenesisCube", "GenesisCubeConfig"]
