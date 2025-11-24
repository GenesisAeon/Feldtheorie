"""
4D Tesseract Time-Slicing with Implosive Genesis

Formal:
    Provides 4D hypercube (tesseract) slicing where each timeslice is a 3D cube
    standing normally (not inverted pyramid). Couples entropic wavefunction Ψ(r,θ,φ,t)
    with implosive field dynamics across temporal layers.

    Light propagates orthogonally through timeslices while space implodes radially,
    creating dual-flow geometry where consciousness integrates photon paths.

Empirical:
    Returns 4D block arrays, 3D timeslice extractions, and photon trajectories
    for visualization and ΔAIC testing against block-universe null models.

Poetic:
    Der 4D-Würfel atmet durch seine Zeitscheiben — jede Scheibe ein vollständiger
    Raum, während Licht als Uhr durch die Schichten springt und Bewusstsein die
    Bahn als Zeit erlebt.

Reference:
    See releases/V6-Plans_etc/Zusatz_bitte_integrieren!.txt for theoretical foundation
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np

# Import from genesis_cube for wavefunction integration
try:
    from .genesis_cube import GenesisCube, GenesisCubeConfig, ALPHA_INV, PHI_GOLDEN, L_PLANCK, E_PLANCK, HBAR
except ImportError:
    # Fallback if running as standalone
    ALPHA_INV = 137.036
    PHI_GOLDEN = 1.618034
    L_PLANCK = 1.616e-35
    E_PLANCK = 1.956e9
    HBAR = 1.055e-34


@dataclass
class TesseractConfig:
    """Configuration for 4D Tesseract time-slicing."""

    resolution: int = 50  # Spatial grid resolution (per dimension)
    num_slices: int = 100  # Number of temporal slices
    r_max: float = 10.0  # Maximum radial coordinate (Planck lengths)

    # Physical parameters
    alpha_inv: float = ALPHA_INV  # Fine structure constant
    phi_golden: float = PHI_GOLDEN  # Golden ratio

    # Implosive field parameters
    beta: float = 4.8  # Logistic steepness
    theta: float = 0.0  # Threshold parameter
    tau_implosion: float = 1.0  # Implosion timescale

    # Visualization
    enable_wireframe: bool = True
    isosurface_threshold: float = 0.5

    notes: List[str] = field(default_factory=lambda: [
        "4D-Tesseract [−1,1]⁴ sliced into temporal layers",
        "Each slice: normal 3D cube (not inverted pyramid)",
        "Light propagates orthogonally through t-axis",
        "Space implodes radially with exp(-α⁻¹·r²/ℓ²_P)",
    ])


class TesseractTimeSlices:
    """4D hypercube with temporal slicing and entropic wavefunction."""

    def __init__(self, config: TesseractConfig | None = None) -> None:
        self.config = config or TesseractConfig()

        # 4D block: shape (resolution, resolution, resolution, num_slices)
        # Axes: [x, y, z, t]
        self.block_4d: np.ndarray | None = None

        # Coordinate grids
        self.x_1d = np.linspace(-1, 1, self.config.resolution)
        self.y_1d = np.linspace(-1, 1, self.config.resolution)
        self.z_1d = np.linspace(-1, 1, self.config.resolution)
        self.t_1d = np.linspace(0, 1, self.config.num_slices)

        # Initialize 4D field
        self.initialize_4d_field()

    def initialize_4d_field(self) -> None:
        """Initialize implosive field in 4D block."""
        # Create 4D meshgrid
        X, Y, Z, T = np.meshgrid(
            self.x_1d, self.y_1d, self.z_1d, self.t_1d,
            indexing='ij'
        )

        # Radial distance in 3D space (for each time)
        R = np.sqrt(X**2 + Y**2 + Z**2)

        # Implosive field: Collapse toward center over time
        # ψ(r, t) = exp(-α⁻¹ · r² / (1 + t))
        # As t increases, the Gaussian spreads (backward in time = implosion)
        self.block_4d = np.exp(-self.config.alpha_inv * R**2 / (1.0 + 10*T))

        # Optional: Add tetrahedral modulation
        # theta = np.arccos(Z / (R + 1e-10))
        # phi = np.arctan2(Y, X)
        # self.block_4d *= self._tetrahedral_modulation(theta, phi)

    def _tetrahedral_modulation(self, theta: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Apply tetrahedral symmetry modulation (3-fold in φ)."""
        # Simplified form: cos(3φ) + sin(3φ)
        return np.abs(np.cos(3 * phi) + 1j * np.sin(3 * phi))

    def extract_timeslice(self, t_index: int) -> np.ndarray:
        """
        Extract 3D cube at fixed time index.

        Args:
            t_index: Temporal slice index (0 to num_slices-1)

        Returns:
            3D array of shape (resolution, resolution, resolution)
        """
        if self.block_4d is None:
            raise RuntimeError("4D block not initialized")

        if not (0 <= t_index < self.config.num_slices):
            raise ValueError(f"t_index {t_index} out of range [0, {self.config.num_slices})")

        return self.block_4d[:, :, :, t_index]

    def get_cube_wireframe_edges(self) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Get edges of a cube for wireframe rendering.

        Returns:
            List of (start_point, end_point) tuples for 12 edges
        """
        s = self.config.resolution - 1

        # 8 corners of cube
        corners = np.array([
            [0, 0, 0], [s, 0, 0], [s, s, 0], [0, s, 0],  # Bottom face
            [0, 0, s], [s, 0, s], [s, s, s], [0, s, s],  # Top face
        ])

        # 12 edges (pairs of corner indices)
        edge_indices = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Bottom
            (4, 5), (5, 6), (6, 7), (7, 4),  # Top
            (0, 4), (1, 5), (2, 6), (3, 7),  # Vertical
        ]

        edges = [(corners[i], corners[j]) for i, j in edge_indices]
        return edges

    def compute_isosurface(self, cube_3d: np.ndarray, threshold: float | None = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute isosurface of 3D cube using marching cubes.

        Args:
            cube_3d: 3D array to extract surface from
            threshold: Isosurface level (default: config value)

        Returns:
            Tuple of (vertices, faces) arrays for mesh rendering
        """
        try:
            from skimage import measure
        except ImportError:
            raise ImportError("scikit-image required for isosurface computation: pip install scikit-image")

        if threshold is None:
            threshold = self.config.isosurface_threshold * np.max(cube_3d)

        # Marching cubes algorithm
        verts, faces, _, _ = measure.marching_cubes(cube_3d, level=threshold)

        return verts, faces

    def slice_summary(self, t_index: int) -> Dict[str, object]:
        """
        Get summary statistics for a timeslice.

        Args:
            t_index: Temporal slice index

        Returns:
            Dict with time, max/min/mean field values, entropy estimate
        """
        cube_3d = self.extract_timeslice(t_index)
        t = self.t_1d[t_index]

        # Field statistics
        field_max = float(np.max(cube_3d))
        field_min = float(np.min(cube_3d))
        field_mean = float(np.mean(cube_3d))

        # Entropy estimate: S ∝ -∑ ρ ln(ρ) where ρ = |Ψ|²
        rho = cube_3d / (np.sum(cube_3d) + 1e-30)  # Normalize
        entropy = -float(np.sum(rho * np.log(rho + 1e-30)))

        return {
            "t": t,
            "t_index": t_index,
            "field_max": field_max,
            "field_min": field_min,
            "field_mean": field_mean,
            "entropy": entropy,
        }

    def all_slices_summary(self) -> List[Dict[str, object]]:
        """Get summary for all timeslices."""
        return [self.slice_summary(i) for i in range(self.config.num_slices)]


class PhotonPropagator:
    """Propagate photons through 4D tesseract timeslices."""

    def __init__(self, tesseract: TesseractTimeSlices) -> None:
        self.tesseract = tesseract

    def propagate_photon(
        self,
        start_xyz: Tuple[float, float, float],
        start_t_index: int,
        k_direction: Tuple[float, float, float] = (0.1, 0.1, 0.0),
        num_steps: int | None = None,
    ) -> np.ndarray:
        """
        Propagate photon through timeslices.

        Photon starts in slice t=start_t_index and propagates forward in time.
        Spatial position evolves via k_direction + coupling to implosive field.

        Args:
            start_xyz: Initial position (x, y, z) in grid coordinates
            start_t_index: Starting temporal slice
            k_direction: Photon momentum direction (3-vector)
            num_steps: Number of time steps (default: all remaining slices)

        Returns:
            Array of shape (num_steps, 4) with columns [x, y, z, t_index]
        """
        if num_steps is None:
            num_steps = self.tesseract.config.num_slices - start_t_index

        # Initialize
        x, y, z = start_xyz
        kx, ky, kz = k_direction

        path_4d = []

        for step in range(num_steps):
            t_index = start_t_index + step
            if t_index >= self.tesseract.config.num_slices:
                break

            # Get current timeslice
            cube_3d = self.tesseract.extract_timeslice(t_index)

            # Clamp position to grid bounds
            ix = int(np.clip(x, 0, self.tesseract.config.resolution - 1))
            iy = int(np.clip(y, 0, self.tesseract.config.resolution - 1))
            iz = int(np.clip(z, 0, self.tesseract.config.resolution - 1))

            # Sample field strength at current position
            field_strength = cube_3d[ix, iy, iz]

            # Record position
            path_4d.append([x, y, z, t_index])

            # Update position: free propagation + field coupling
            x += kx
            y += ky
            z += kz

            # Coupling to implosive field: photon "slows down" in high-density regions
            # k_vec *= (1 - coupling_strength * field_strength)
            coupling_strength = 0.01
            kx *= (1.0 - coupling_strength * field_strength)
            ky *= (1.0 - coupling_strength * field_strength)
            kz *= (1.0 - coupling_strength * field_strength)

            # Check bounds
            if x < 0 or x >= self.tesseract.config.resolution:
                break
            if y < 0 or y >= self.tesseract.config.resolution:
                break
            if z < 0 or z >= self.tesseract.config.resolution:
                break

        return np.array(path_4d)

    def compute_consciousness_integral(self, photon_paths: List[np.ndarray]) -> float:
        """
        Compute consciousness integral: I_C = ∫ F·u dτ over all photon paths.

        This represents the "experience" of an observer following light through
        the implosive block universe.

        Args:
            photon_paths: List of photon trajectory arrays

        Returns:
            Consciousness integral value
        """
        I_C = 0.0

        for path in photon_paths:
            if len(path) < 2:
                continue

            # Integrate F·u along path
            for i in range(len(path) - 1):
                # 4-velocity: u^μ = (dx, dy, dz) / dt
                dx = path[i+1, 0] - path[i, 0]
                dy = path[i+1, 1] - path[i, 1]
                dz = path[i+1, 2] - path[i, 2]
                dt_index = path[i+1, 3] - path[i, 3]

                if dt_index == 0:
                    continue

                u = np.array([dx, dy, dz]) / dt_index

                # Field strength (proxy for electromagnetic tensor F_μν)
                t_index = int(path[i, 3])
                cube_3d = self.tesseract.extract_timeslice(t_index)

                ix = int(np.clip(path[i, 0], 0, self.tesseract.config.resolution - 1))
                iy = int(np.clip(path[i, 1], 0, self.tesseract.config.resolution - 1))
                iz = int(np.clip(path[i, 2], 0, self.tesseract.config.resolution - 1))

                F = cube_3d[ix, iy, iz]

                # Contribution: F · u
                I_C += F * np.linalg.norm(u)

        return I_C


def demo_tesseract_slicing() -> None:
    """Demonstration of tesseract time-slicing functionality."""
    print("🎲 Initializing 4D Tesseract...")
    tesseract = TesseractTimeSlices(TesseractConfig(resolution=32, num_slices=50))

    print(f"✅ 4D block shape: {tesseract.block_4d.shape}")

    # Extract and analyze middle timeslice
    mid_t = tesseract.config.num_slices // 2
    print(f"\n📸 Extracting timeslice t={mid_t}...")
    cube_3d = tesseract.extract_timeslice(mid_t)
    print(f"   3D cube shape: {cube_3d.shape}")

    summary = tesseract.slice_summary(mid_t)
    print(f"   Field range: [{summary['field_min']:.6f}, {summary['field_max']:.6f}]")
    print(f"   Mean: {summary['field_mean']:.6f}")
    print(f"   Entropy: {summary['entropy']:.6f}")

    # Photon propagation
    print(f"\n🌊 Propagating photon through timeslices...")
    propagator = PhotonPropagator(tesseract)

    start_pos = (16.0, 16.0, 16.0)  # Center of grid
    path = propagator.propagate_photon(start_pos, start_t_index=0)

    print(f"   Photon path length: {len(path)} steps")
    print(f"   Start: t={path[0, 3]:.0f}, pos=({path[0, 0]:.1f}, {path[0, 1]:.1f}, {path[0, 2]:.1f})")
    print(f"   End:   t={path[-1, 3]:.0f}, pos=({path[-1, 0]:.1f}, {path[-1, 1]:.1f}, {path[-1, 2]:.1f})")

    # Consciousness integral
    I_C = propagator.compute_consciousness_integral([path])
    print(f"   Consciousness integral I_C = {I_C:.6f}")

    print("\n✨ Demo complete!")


__all__ = [
    "TesseractConfig",
    "TesseractTimeSlices",
    "PhotonPropagator",
    "demo_tesseract_slicing",
]


if __name__ == "__main__":
    demo_tesseract_slicing()
