"""
OIPK Simulator: Orthogonal Implosion-Photon-Kinematik

Implements dual-flow spacetime architecture with:
1. Vertical implosion (τ-time)
2. Horizontal photon propagation (t-time)
3. Consciousness integration (Δt_Q windows)

Version: v6.0.0-alpha
Source: releases/V6-Plans_etc/GrundPrinzip Simulation.txt
Authors: Johann Benjamin Römer, MOR Framework
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass
import sys
from pathlib import Path

# Add models directory to path for v_RIG constant
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.unified_constants import calculate_vrig, V_RIG_DEFAULT


@dataclass
class OIPKParameters:
    """OIPK simulation parameters."""

    # Geometry
    tau_max: float = 13.8e9  # years, age of universe
    a_max: float = 46.5e9  # light-years, maximum radius
    b_max: float = 1.0  # Vertical height (normalized, to be determined!)

    # Physics
    c: float = 299792.0  # km/s, speed of light
    v_imp: Optional[float] = None  # Implosion velocity (to be determined!)
    xi: float = 0.01  # Lorentz-violation parameter

    # Time steps
    delta_tau: float = 1.0  # Myr, implosion time step
    delta_t_photon: float = 1e-15  # s, photon time step (femtoseconds)
    delta_t_Q: float = 0.150  # s, consciousness integration window

    # Symmetry
    n_edges: int = 12  # Number of recursive mirror axes
    reflection_coefficient: float = 0.99  # How much light reflects

    # Cosmic constants
    alpha_inv: float = 137.036  # Fine structure constant inverse
    phi: float = 1.618034  # Golden ratio
    v_rig: Optional[float] = None  # Regime Integration Gradient velocity (km/s)

    def __post_init__(self):
        """Calculate derived parameters."""
        if self.v_imp is None:
            # Estimate from Hubble constant
            H0 = 70  # km/s/Mpc
            # v_imp ~ H0 * a_max
            self.v_imp = H0 * self.a_max / 1e6  # Approximate

        if self.v_rig is None:
            # Calculate v_RIG from fundamental constants
            # v_RIG = c / (α⁻¹ · Φ) ≈ 1,351.8 km/s
            # This represents the 2D→3D consciousness integration rate
            self.v_rig = calculate_vrig(self.alpha_inv, self.phi, self.c)


class OIPKSimulator:
    """
    OIPK Simulation: Dual-flow spacetime with orthogonal time axes.

    The simulation implements:
    1. Vertical implosion: τ runs from 0 → τ_max (slow)
    2. Horizontal photons: Light flies through 2D slices (fast, c)
    3. 12-fold reflection: Along cube edges
    4. Consciousness integration: Samples every Δt_Q
    """

    def __init__(self, params: Optional[OIPKParameters] = None):
        """Initialize OIPK simulator."""
        self.params = params or OIPKParameters()
        self.tau = 0.0  # Current implosion time
        self.t = 0.0  # Current photon time

        # Geometry arrays
        self.a_tau = []  # Scale factor history
        self.b_tau = []  # Vertical dimension history
        self.tau_history = []  # Time history

        # Photon arrays
        self.photon_positions = []  # List of photon (x, y, z, t) arrays
        self.photon_paths = []  # List of paths for each photon

        # Consciousness arrays
        self.consciousness_frames = []  # Integrated 3D reconstructions

    def compute_radius(self, tau: float) -> float:
        """
        Compute scale factor a(τ) - horizontal radius.

        Diamond geometry: expands from 0 → a_max → 0
        """
        tau_max = self.params.tau_max
        a_max = self.params.a_max

        if tau <= tau_max:
            # Expansion phase: 0 → max
            return a_max * np.sin(np.pi * tau / (2 * tau_max))
        else:
            # Contraction phase: max → 0
            return a_max * np.sin(np.pi * (2 - tau / tau_max) / 2)

    def compute_height(self, tau: float) -> float:
        """
        Compute vertical dimension b(τ).

        Inverted: contracts from b_max → 0 → b_max
        """
        tau_max = self.params.tau_max
        b_max = self.params.b_max

        if tau <= tau_max:
            # Contraction phase: max → 0
            return b_max * (1 - tau / tau_max)
        else:
            # Expansion phase: 0 → max
            return b_max * (tau / tau_max - 1)

    def get_slice(self, tau: float) -> np.ndarray:
        """
        Extract 2D slice at given τ.

        Returns 2D array representing spatial slice.
        """
        # Stub: Create empty slice
        # In full implementation: Extract from 4D field
        a = self.compute_radius(tau)
        resolution = 100
        x = np.linspace(-a, a, resolution)
        y = np.linspace(-a, a, resolution)
        X, Y = np.meshgrid(x, y)

        # Example: Gaussian field
        R = np.sqrt(X**2 + Y**2)
        field = np.exp(-self.params.alpha_inv * R**2 / a**2)

        return field

    def implosion_step(self):
        """Execute one vertical implosion step."""
        self.tau += self.params.delta_tau

        # Update geometry
        a = self.compute_radius(self.tau)
        b = self.compute_height(self.tau)

        self.a_tau.append(a)
        self.b_tau.append(b)
        self.tau_history.append(self.tau)

    def propagate_photon(self, photon: np.ndarray, slice_field: np.ndarray) -> np.ndarray:
        """
        Propagate single photon through slice.

        Args:
            photon: [x, y, z, kx, ky, kz] position and momentum
            slice_field: 2D field at current slice

        Returns:
            Updated photon state
        """
        x, y, z, kx, ky, kz = photon
        dt = self.params.delta_t_photon

        # Standard propagation
        x += kx * self.params.c * dt
        y += ky * self.params.c * dt
        z += kz * self.params.c * dt

        # Check if hits edge (simplified: circular boundary)
        a = self.compute_radius(self.tau)
        r = np.sqrt(x**2 + y**2)

        if r > a:
            # Reflect at boundary (12-fold symmetry)
            angle = np.arctan2(y, x)
            # Snap to nearest of 12 directions
            n_edges = self.params.n_edges
            snap_angle = np.round(angle / (2 * np.pi / n_edges)) * (2 * np.pi / n_edges)

            # Reflect momentum
            kx = -kx * self.params.reflection_coefficient * np.cos(snap_angle)
            ky = -ky * self.params.reflection_coefficient * np.sin(snap_angle)

        return np.array([x, y, z, kx, ky, kz])

    def photon_step(self, num_photons: int = 10):
        """Execute one horizontal photon propagation step."""
        self.t += self.params.delta_t_photon

        # Get current slice
        slice_field = self.get_slice(self.tau)

        # Initialize photons if first step
        if len(self.photon_positions) == 0:
            # Create random photons
            a = self.compute_radius(self.tau)
            photons = []
            for _ in range(num_photons):
                # Random position in circle
                r = np.random.uniform(0, a * 0.5)
                theta = np.random.uniform(0, 2 * np.pi)
                x = r * np.cos(theta)
                y = r * np.sin(theta)
                z = 0

                # Random direction (normalized)
                kx = np.random.uniform(-1, 1)
                ky = np.random.uniform(-1, 1)
                kz = 0
                k_norm = np.sqrt(kx**2 + ky**2 + kz**2)
                kx /= k_norm
                ky /= k_norm

                photons.append(np.array([x, y, z, kx, ky, kz]))

            self.photon_positions = photons
            self.photon_paths = [[] for _ in range(num_photons)]

        # Propagate all photons
        for i, photon in enumerate(self.photon_positions):
            updated = self.propagate_photon(photon, slice_field)
            self.photon_positions[i] = updated
            self.photon_paths[i].append(updated[:3].copy())

    def consciousness_integrate(self):
        """
        Integrate over Δt_Q to reconstruct 3D world.

        Implements motion parallax and structure-from-motion.

        The integration rate is fundamentally limited by v_RIG = c/(α⁻¹·Φ),
        representing the velocity at which 2D-slice information can be
        synthesized into 3D conscious perception.

        Integration mechanism:
        1. Collect photon trajectories over Δt_Q window
        2. Apply structure-from-motion to reconstruct 3D geometry
        3. Rate-limited by v_RIG ≈ 1,352 km/s (not c!)
        """
        # Stub: Collect frames over Δt_Q window
        # In full implementation: Apply structure-from-motion algorithm

        # Calculate effective integration distance based on v_RIG
        integration_distance = self.params.v_rig * self.params.delta_t_Q

        frame = {
            "tau": self.tau,
            "t": self.t,
            "photon_positions": [p[:3].copy() for p in self.photon_positions],
            "integration_distance": integration_distance,  # Max distance for coherent 3D reconstruction
            "v_rig": self.params.v_rig,  # Integration velocity
            "reconstruction": "3D world model",  # Placeholder for SfM algorithm
        }

        self.consciousness_frames.append(frame)

    def run_asynchronous(
        self, num_tau_steps: int = 100, num_t_steps_per_tau: int = 1000
    ):
        """
        Run asynchronous dual-flow simulation.

        Args:
            num_tau_steps: Number of implosion steps
            num_t_steps_per_tau: Number of photon steps per implosion step
        """
        print(f"🎬 Starting OIPK simulation...")
        print(f"   Implosion steps: {num_tau_steps}")
        print(f"   Photon steps per τ: {num_t_steps_per_tau}")

        for tau_step in range(num_tau_steps):
            # VERTICAL: Implosion step
            self.implosion_step()

            for t_step in range(num_t_steps_per_tau):
                # HORIZONTAL: Photon propagation
                self.photon_step()

                # CONSCIOUSNESS: Integrate every Δt_Q
                if (t_step * self.params.delta_t_photon) % self.params.delta_t_Q < 1e-9:
                    self.consciousness_integrate()

            if (tau_step + 1) % 10 == 0:
                print(f"   τ step {tau_step+1}/{num_tau_steps} complete")

        print("✅ Simulation complete!")

    def visualize_geometry(self):
        """Visualize diamond/octahedron geometry."""
        fig = plt.figure(figsize=(12, 5))

        # Panel 1: Scale factor a(τ)
        ax1 = fig.add_subplot(131)
        ax1.plot(self.tau_history, self.a_tau, "b-", linewidth=2)
        ax1.axhline(self.params.a_max, color="r", linestyle="--", label="a_max")
        ax1.set_xlabel("τ (Implosion time)")
        ax1.set_ylabel("a(τ) (Radius)")
        ax1.set_title("Horizontal Scale Factor")
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Panel 2: Vertical dimension b(τ)
        ax2 = fig.add_subplot(132)
        ax2.plot(self.tau_history, self.b_tau, "g-", linewidth=2)
        ax2.set_xlabel("τ (Implosion time)")
        ax2.set_ylabel("b(τ) (Height)")
        ax2.set_title("Vertical Dimension")
        ax2.grid(True, alpha=0.3)

        # Panel 3: Diamond cross-section
        ax3 = fig.add_subplot(133)
        tau_plot = np.array(self.tau_history)
        a_plot = np.array(self.a_tau)
        ax3.plot(a_plot, tau_plot, "r-", linewidth=2, label="Expansion")
        ax3.plot(-a_plot, tau_plot, "r-", linewidth=2)
        ax3.axhline(self.params.tau_max, color="k", linestyle="--", alpha=0.5)
        ax3.set_xlabel("Radius a")
        ax3.set_ylabel("τ (Time)")
        ax3.set_title("Diamond Geometry")
        ax3.grid(True, alpha=0.3)
        ax3.legend()

        plt.tight_layout()
        return fig

    def visualize_photon_paths(self):
        """Visualize photon trajectories in 3D."""
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection="3d")

        # Draw current slice boundary
        a = self.compute_radius(self.tau)
        theta = np.linspace(0, 2 * np.pi, 100)
        x_circle = a * np.cos(theta)
        y_circle = a * np.sin(theta)
        z_circle = np.zeros_like(theta)
        ax.plot(x_circle, y_circle, z_circle, "k--", linewidth=2, alpha=0.5)

        # Draw photon paths
        for i, path in enumerate(self.photon_paths):
            if len(path) > 1:
                path_array = np.array(path)
                ax.plot(
                    path_array[:, 0],
                    path_array[:, 1],
                    path_array[:, 2],
                    linewidth=1,
                    alpha=0.7,
                    label=f"Photon {i+1}" if i < 5 else None,
                )

        # Draw current photon positions
        current_pos = np.array([p[:3] for p in self.photon_positions])
        ax.scatter(
            current_pos[:, 0],
            current_pos[:, 1],
            current_pos[:, 2],
            c="red",
            s=50,
            marker="o",
            label="Current",
        )

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title(f"Photon Paths (τ = {self.tau:.2e})")
        ax.legend()

        return fig


def main():
    """Example usage."""
    print("🎲 OIPK Simulator Demo")
    print("=" * 50)

    # Create simulator with default parameters
    params = OIPKParameters(
        tau_max=100.0,  # Simplified for demo
        a_max=10.0,
        delta_tau=1.0,
        delta_t_photon=0.01,
        delta_t_Q=0.1,
    )

    sim = OIPKSimulator(params)

    # Run simulation
    sim.run_asynchronous(num_tau_steps=50, num_t_steps_per_tau=100)

    # Visualize
    print("\n📊 Generating visualizations...")
    fig_geom = sim.visualize_geometry()
    plt.savefig("/mnt/user-data/outputs/oipk_geometry.png", dpi=150)
    print("   Saved: oipk_geometry.png")

    fig_photons = sim.visualize_photon_paths()
    plt.savefig("/mnt/user-data/outputs/oipk_photon_paths.png", dpi=150)
    print("   Saved: oipk_photon_paths.png")

    plt.show()


if __name__ == "__main__":
    main()
