"""
Tesseract-Timeslice Simulator: 4D Hypercube with Entropic Gravity

Implements:
1. 4D hypercube sliced into 3D spatial cubes
2. Entropic gravity from geometric verschnitt
3. Diagonal photon propagation through 2D slices
4. Consciousness as worldline through block universe

Version: v6.0.0-alpha
Source: releases/V6-Plans_etc/Zusatz_bitte_integrieren!.txt
Authors: Johann Benjamin Römer, MOR Framework
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass


@dataclass
class TesseractParameters:
    """Tesseract simulation parameters."""

    # Geometry
    resolution: int = 50  # Grid points per dimension
    num_slices: int = 100  # Number of time slices

    # Physics constants
    alpha_inv: float = 137.036  # Fine structure constant inverse
    phi: float = 1.618034  # Golden ratio
    c: float = 299792.0  # km/s, speed of light

    # Field parameters
    implosion_strength: float = 10.0  # Controls collapse rate
    entropy_coupling: float = 0.1  # Strength of entropic gravity


class TesseractTimeSlices:
    """
    4D Hypercube with timeslices.

    Block universe implementation where:
    - 4D hypercube represents all spacetime
    - Slicing at fixed t extracts 3D spatial cube
    - Each cube stands NORMAL on base (not tilted pyramid!)
    """

    def __init__(self, params: Optional[TesseractParameters] = None):
        """Initialize tesseract simulator."""
        self.params = params or TesseractParameters()

        # 4D block: [x, y, z, t]
        self.block_4d = np.zeros(
            (
                self.params.resolution,
                self.params.resolution,
                self.params.resolution,
                self.params.num_slices,
            )
        )

        # Entropy field (for gravitation)
        self.entropy_field = np.zeros_like(self.block_4d)

        self.initialize_4d_field()

    def initialize_4d_field(self):
        """
        Initialize implosive field in 4D block.

        The field represents the wavefunction Ψ(r,t) that collapses
        to the center over time.
        """
        x = np.linspace(-1, 1, self.params.resolution)
        y = np.linspace(-1, 1, self.params.resolution)
        z = np.linspace(-1, 1, self.params.resolution)
        t = np.linspace(0, 1, self.params.num_slices)

        X, Y, Z, T = np.meshgrid(x, y, z, t, indexing="ij")

        # Radial distance in 3D space (for each time)
        R = np.sqrt(X**2 + Y**2 + Z**2)

        # Implosive field: Collapse to center over time
        # ψ(r, t) = exp(-α⁻¹ · r² / (1 + strength·t))
        self.block_4d = np.exp(
            -self.params.alpha_inv
            * R**2
            / (1 + self.params.implosion_strength * T)
        )

        # Compute entropy field (S ∝ -ψ log ψ, von Neumann entropy)
        # Avoid log(0)
        psi_safe = np.clip(self.block_4d, 1e-10, None)
        self.entropy_field = -self.block_4d * np.log(psi_safe)

    def extract_timeslice(self, t_index: int) -> np.ndarray:
        """
        Extract 3D cube at fixed t.

        Args:
            t_index: Time slice index (0 to num_slices-1)

        Returns:
            3D array representing spatial slice
        """
        return self.block_4d[:, :, :, t_index]

    def compute_entropy_gradient(self, t_index: int) -> Tuple[np.ndarray, ...]:
        """
        Compute entropy gradient ∇S at given timeslice.

        This gradient generates entropic gravity force: F = T·∇S

        Returns:
            Tuple of (∇S_x, ∇S_y, ∇S_z) arrays
        """
        entropy_slice = self.entropy_field[:, :, :, t_index]

        # Compute gradients (finite differences)
        grad_x = np.gradient(entropy_slice, axis=0)
        grad_y = np.gradient(entropy_slice, axis=1)
        grad_z = np.gradient(entropy_slice, axis=2)

        return grad_x, grad_y, grad_z

    def compute_slice_spacing(self, t_index: int) -> float:
        """
        Compute spacing between slices as function of entropy.

        Hypothesis: Δz ∝ 1/√ρ where ρ ~ S (entropy density)

        This makes photons travel "diagonally" through denser regions.

        Args:
            t_index: Current time slice

        Returns:
            Spacing to next slice
        """
        entropy_slice = self.entropy_field[:, :, :, t_index]
        mean_entropy = np.mean(entropy_slice)

        # Avoid division by zero
        if mean_entropy < 1e-10:
            return 1.0

        # Inverse relationship
        spacing = 1.0 / np.sqrt(mean_entropy)

        return spacing * self.params.entropy_coupling

    def draw_cube_wireframe(self, ax, size: int = None):
        """
        Draw cube edges (not pyramid!).

        Args:
            ax: Matplotlib 3D axis
            size: Cube size (defaults to resolution-1)
        """
        if size is None:
            size = self.params.resolution - 1

        # 8 corners of a cube
        corners = np.array(
            [
                [0, 0, 0],
                [size, 0, 0],
                [size, size, 0],
                [0, size, 0],  # Bottom face
                [0, 0, size],
                [size, 0, size],
                [size, size, size],
                [0, size, size],  # Top face
            ]
        )

        # 12 edges
        edges = [
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 0],  # Bottom
            [4, 5],
            [5, 6],
            [6, 7],
            [7, 4],  # Top
            [0, 4],
            [1, 5],
            [2, 6],
            [3, 7],  # Vertical
        ]

        for edge in edges:
            points = corners[edge]
            ax.plot3D(*points.T, "k-", linewidth=0.5, alpha=0.3)

    def render_normal_cube(
        self, cube_3d: np.ndarray, ax, time_label: str = "", threshold: float = 0.5
    ):
        """
        Render 3D cube in NORMAL orientation (not rotated).

        Args:
            cube_3d: 3D array to visualize
            ax: Matplotlib 3D axis
            time_label: Label for time
            threshold: Isosurface threshold (fraction of max)
        """
        ax.clear()

        # Simple visualization: scatter points above threshold
        threshold_val = threshold * np.max(cube_3d)
        coords = np.where(cube_3d > threshold_val)

        if len(coords[0]) > 0:
            # Sample to avoid too many points
            sample = np.random.choice(len(coords[0]), min(1000, len(coords[0])))
            ax.scatter(
                coords[0][sample],
                coords[1][sample],
                coords[2][sample],
                c=cube_3d[coords[0][sample], coords[1][sample], coords[2][sample]],
                cmap="viridis",
                alpha=0.6,
                s=10,
            )

        # Cube wireframe
        self.draw_cube_wireframe(ax)

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title(f"Timeslice: {time_label}")

        # NORMAL standing: equal scaling all axes
        ax.set_box_aspect([1, 1, 1])

    def visualize_4d_projection(self, ax, current_t: int, stride: int = 10):
        """
        Project 4D hypercube onto 3D (show multiple timeslices).

        Args:
            ax: Matplotlib 3D axis
            current_t: Current time index (highlighted)
            stride: Show every stride-th slice
        """
        ax.clear()

        # Show multiple slices as stacked wireframes
        for t_idx in range(0, self.params.num_slices, stride):
            z_offset = t_idx * 0.05  # Vertical offset for time stacking

            alpha = 0.1 if t_idx != current_t else 0.8
            color = "gray" if t_idx != current_t else "red"

            # Draw wireframe at this time
            size = self.params.resolution - 1
            corners = np.array(
                [
                    [0, 0, z_offset],
                    [size, 0, z_offset],
                    [size, size, z_offset],
                    [0, size, z_offset],
                    [0, 0, z_offset + size * 0.05],
                    [size, 0, z_offset + size * 0.05],
                    [size, size, z_offset + size * 0.05],
                    [0, size, z_offset + size * 0.05],
                ]
            )

            edges = [
                [0, 1],
                [1, 2],
                [2, 3],
                [3, 0],
                [4, 5],
                [5, 6],
                [6, 7],
                [7, 4],
                [0, 4],
                [1, 5],
                [2, 6],
                [3, 7],
            ]

            for edge in edges:
                points = corners[edge]
                ax.plot3D(*points.T, color=color, linewidth=1, alpha=alpha)

        ax.set_title("4D Hypercube (all timeslices)")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z (+ Time)")


class PhotonBetweenSlices:
    """
    Photon propagation through timeslices.

    Implements diagonal propagation where photons traverse
    slices with spacing determined by entropy gradient.
    """

    def __init__(self, tesseract: TesseractTimeSlices):
        """Initialize photon propagator."""
        self.tesseract = tesseract

    def propagate_photon(
        self, start_xyz: Tuple[int, int, int], start_t: int
    ) -> np.ndarray:
        """
        Propagate photon from start position through slices.

        Args:
            start_xyz: Initial (x, y, z) position
            start_t: Initial time slice

        Returns:
            Array of shape (N, 4) with columns [x, y, z, t]
        """
        path_4d = []

        x, y, z = start_xyz
        k_vec = np.array([0.1, 0.1, 0.0])  # Direction in 3D (normalized later)
        k_norm = np.linalg.norm(k_vec)
        if k_norm > 0:
            k_vec /= k_norm

        for t_idx in range(start_t, self.tesseract.params.num_slices):
            # Get current slice
            cube_3d = self.tesseract.extract_timeslice(t_idx)

            # Standard propagation
            x += k_vec[0]
            y += k_vec[1]
            z += k_vec[2]

            # Boundary check
            res = self.tesseract.params.resolution
            if x < 0 or x >= res or y < 0 or y >= res or z < 0 or z >= res:
                break

            # Coupling to implosion field (photon slows down in high-entropy regions)
            field_strength = cube_3d[int(x), int(y), int(z)]
            k_vec *= 1 - 0.01 * field_strength  # Slight deceleration

            # Get slice spacing (diagonal component!)
            delta_z = self.tesseract.compute_slice_spacing(t_idx)

            # Record position in 4D
            path_4d.append([x, y, z + delta_z * t_idx, t_idx])

        return np.array(path_4d) if path_4d else np.array([])

    def visualize_light_path(
        self, start_positions: List[Tuple[int, int, int]], start_t: int = 0
    ):
        """
        Visualize multiple photon paths through slices.

        Args:
            start_positions: List of (x, y, z) starting positions
            start_t: Starting time index
        """
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection="3d")

        # Propagate and plot each photon
        for i, start_pos in enumerate(start_positions):
            path = self.propagate_photon(start_pos, start_t)
            if len(path) > 1:
                # Plot with time as "z" coordinate for visualization
                ax.plot3D(
                    path[:, 0],
                    path[:, 1],
                    path[:, 3],  # Use time as z
                    linewidth=2,
                    alpha=0.7,
                    label=f"Photon {i+1}",
                )

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Time (Slice Index)")
        ax.legend()
        ax.set_title("Photon Paths Through Timeslices (Diagonal Propagation)")

        return fig


def compute_wavefunction(
    r: np.ndarray, theta: np.ndarray, phi: np.ndarray, t: float
) -> np.ndarray:
    """
    Genesis wavefunction Ψ(r,θ,φ,t).

    Implements combined wavefunction:
    Ψ = ψ_genesis · ψ_angular · ψ_time

    Args:
        r: Radial coordinate (meters, Planck units)
        theta: Polar angle
        phi: Azimuthal angle
        t: Time (seconds, Planck units)

    Returns:
        Complex wavefunction array
    """
    # Constants
    alpha_inv = 137.036
    l_planck = 1.616e-35  # Planck length (meters)
    phi_golden = 1.618034
    E_planck = 1.956e9  # Planck energy (Joules)

    # Radial component (Gaussian collapse)
    psi_radial = np.exp(-alpha_inv * r**2 / l_planck**2)

    # Angular component (tetrahedral symmetry, simplified)
    psi_angular = np.cos(theta) ** 2 * np.sin(3 * phi) + np.sin(theta) ** 2 * np.cos(
        3 * phi
    )

    # Time evolution (golden ratio frequency)
    psi_time = np.exp(-1j * phi_golden * E_planck * t)

    return psi_radial * psi_angular * psi_time


def main():
    """Example usage."""
    print("🎲 Tesseract-Timeslice Simulator Demo")
    print("=" * 50)

    # Create tesseract with default parameters
    params = TesseractParameters(resolution=30, num_slices=50)

    print(f"   Resolution: {params.resolution}³")
    print(f"   Time slices: {params.num_slices}")
    print("   Initializing 4D block...")

    tesseract = TesseractTimeSlices(params)

    # Visualize a single timeslice
    print("\n📊 Visualizing timeslice...")
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection="3d")

    t_mid = params.num_slices // 2
    cube_3d = tesseract.extract_timeslice(t_mid)
    tesseract.render_normal_cube(cube_3d, ax, f"t = {t_mid}/{params.num_slices}")

    plt.savefig("/mnt/user-data/outputs/tesseract_slice.png", dpi=150)
    print("   Saved: tesseract_slice.png")

    # Visualize 4D projection
    print("\n📊 Visualizing 4D projection...")
    fig2 = plt.figure(figsize=(10, 10))
    ax2 = fig2.add_subplot(111, projection="3d")

    tesseract.visualize_4d_projection(ax2, current_t=t_mid, stride=5)

    plt.savefig("/mnt/user-data/outputs/tesseract_4d_projection.png", dpi=150)
    print("   Saved: tesseract_4d_projection.png")

    # Photon propagation
    print("\n🔦 Computing photon paths...")
    photon_sim = PhotonBetweenSlices(tesseract)

    # Start 3 photons at different positions
    start_positions = [
        (params.resolution // 4, params.resolution // 4, params.resolution // 2),
        (params.resolution // 2, params.resolution // 4, params.resolution // 2),
        (3 * params.resolution // 4, params.resolution // 4, params.resolution // 2),
    ]

    fig3 = photon_sim.visualize_light_path(start_positions, start_t=0)
    plt.savefig("/mnt/user-data/outputs/tesseract_photon_paths.png", dpi=150)
    print("   Saved: tesseract_photon_paths.png")

    # Compute entropy gradient at middle slice
    print("\n📈 Computing entropic gravity field...")
    grad_x, grad_y, grad_z = tesseract.compute_entropy_gradient(t_mid)
    grad_magnitude = np.sqrt(grad_x**2 + grad_y**2 + grad_z**2)

    print(f"   Mean ∇S: {np.mean(grad_magnitude):.6f}")
    print(f"   Max ∇S: {np.max(grad_magnitude):.6f}")
    print("   (Gravity emerges from this gradient: F = T·∇S)")

    # Test wavefunction
    print("\n🌊 Testing genesis wavefunction...")
    r_test = np.linspace(0, 1e-34, 100)  # Near Planck scale
    theta_test = np.pi / 4
    phi_test = 0
    t_test = 0

    psi = compute_wavefunction(r_test, theta_test, phi_test, t_test)
    probability = np.abs(psi) ** 2

    fig4 = plt.figure(figsize=(10, 5))
    ax4 = fig4.add_subplot(111)
    ax4.plot(r_test / 1e-35, probability, "b-", linewidth=2)
    ax4.set_xlabel("r / ℓ_Planck")
    ax4.set_ylabel("|Ψ|² (Probability Density)")
    ax4.set_title("Genesis Wavefunction at t=0")
    ax4.grid(True, alpha=0.3)

    plt.savefig("/mnt/user-data/outputs/tesseract_wavefunction.png", dpi=150)
    print("   Saved: tesseract_wavefunction.png")

    print("\n✅ Demo complete!")
    print("\nKey Results:")
    print(f"   1. Block universe: {params.resolution}³ × {params.num_slices} (4D)")
    print("   2. Photon paths: Diagonal through slices")
    print("   3. Gravity: Emergent from ∇S (entropy gradient)")
    print(
        f"   4. Slice spacing varies with entropy: Δz ∝ 1/√S (testable with Shapiro delay)"
    )

    plt.show()


if __name__ == "__main__":
    main()
