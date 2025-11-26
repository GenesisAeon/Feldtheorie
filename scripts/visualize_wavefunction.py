#!/usr/bin/env python3
"""
Visualize Entropic Wavefunction Ψ(r,θ,φ,t) from Genesis Cube

This script creates visualizations of:
1. Probability density |Ψ(r,θ,φ,t)|²
2. Entropy gradient ∇S
3. Phase information arg(Ψ)
4. Time evolution animation

Usage:
    python scripts/visualize_wavefunction.py --output analysis/results/wavefunction/
    python scripts/visualize_wavefunction.py --animate --frames 100

Reference:
    - simulation/genesis_cube.py: GenesisCube.compute_wavefunction()
    - releases/V6-Plans_etc/papers/paper_v_rig_consciousness.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Tuple

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Add repository root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from simulation.genesis_cube import GenesisCube, GenesisCubeConfig


class WavefunctionVisualizer:
    """Visualizer for entropic wavefunction Ψ(r,θ,φ,t)."""

    def __init__(self, output_dir: str = "analysis/results/wavefunction"):
        """Initialize visualizer.

        Parameters
        ----------
        output_dir : str
            Directory to save output plots
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Genesis Cube with wavefunction enabled
        config = GenesisCubeConfig(
            enable_wavefunction=True,
            wavefunction_resolution=64,
            time_steps=100,
            beta=4.8,
            theta=0.0
        )
        self.cube = GenesisCube(config)

        print(f"✓ Initialized WavefunctionVisualizer")
        print(f"  Output directory: {self.output_dir}")
        print(f"  Resolution: {config.wavefunction_resolution}")
        print(f"  Time steps: {config.time_steps}")

    def plot_probability_density(
        self,
        t: float = 0.0,
        r_max: float = 10.0,
        filename: str = "probability_density.png"
    ) -> None:
        """Plot |Ψ(r,θ,φ,t)|² probability density.

        Parameters
        ----------
        t : float
            Time coordinate (in Planck units)
        r_max : float
            Maximum radial coordinate
        filename : str
            Output filename
        """
        n = self.cube.config.wavefunction_resolution
        r = np.linspace(0, r_max, n)
        theta = np.linspace(0, np.pi, n)

        # Create 2D grid (r, theta) at fixed phi=0
        R, Theta = np.meshgrid(r, theta)
        Phi = np.zeros_like(R)

        # Compute |Ψ|²
        psi_squared = self.cube.compute_probability_density(R, Theta, Phi, t)

        # Plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Heatmap
        im1 = ax1.imshow(
            psi_squared,
            extent=[0, r_max, 0, np.pi],
            origin='lower',
            cmap='viridis',
            aspect='auto'
        )
        ax1.set_xlabel('Radial coordinate r (Planck lengths)', fontsize=11)
        ax1.set_ylabel('Polar angle θ (radians)', fontsize=11)
        ax1.set_title(f'|Ψ(r,θ,φ=0,t={t:.2e})|² Probability Density', fontsize=12, fontweight='bold')
        plt.colorbar(im1, ax=ax1, label='|Ψ|²')

        # Radial profile at theta=π/4
        theta_idx = n // 4
        radial_profile = psi_squared[theta_idx, :]

        ax2.plot(r, radial_profile, 'b-', linewidth=2, label=f'θ = π/4')
        ax2.set_xlabel('Radial coordinate r (Planck lengths)', fontsize=11)
        ax2.set_ylabel('|Ψ|²', fontsize=11)
        ax2.set_title('Radial Probability Profile', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        plt.tight_layout()
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved probability density plot: {output_path}")

    def plot_entropy_gradient(
        self,
        t: float = 0.0,
        r_max: float = 10.0,
        filename: str = "entropy_gradient.png"
    ) -> None:
        """Plot entropy gradient ∇S from emergent gravity.

        Parameters
        ----------
        t : float
            Time coordinate
        r_max : float
            Maximum radial coordinate
        filename : str
            Output filename
        """
        n = self.cube.config.wavefunction_resolution
        r = np.linspace(0.1, r_max, n)  # Avoid r=0 for gradient
        theta = np.linspace(0, np.pi, n)

        R, Theta = np.meshgrid(r, theta)
        Phi = np.zeros_like(R)

        # Compute ∇S
        grad_S = self.cube.compute_entropy_gradient(R, Theta, Phi, t)

        # Plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Heatmap
        im1 = ax1.imshow(
            grad_S,
            extent=[0.1, r_max, 0, np.pi],
            origin='lower',
            cmap='RdBu_r',
            aspect='auto'
        )
        ax1.set_xlabel('Radial coordinate r (Planck lengths)', fontsize=11)
        ax1.set_ylabel('Polar angle θ (radians)', fontsize=11)
        ax1.set_title(f'∇S Entropy Gradient (t={t:.2e})', fontsize=12, fontweight='bold')
        plt.colorbar(im1, ax=ax1, label='∇S')

        # Radial profile
        theta_idx = n // 4
        radial_grad = grad_S[theta_idx, :]

        ax2.plot(r, radial_grad, 'r-', linewidth=2, label=f'θ = π/4')
        ax2.axhline(0, color='k', linestyle='--', alpha=0.3)
        ax2.set_xlabel('Radial coordinate r (Planck lengths)', fontsize=11)
        ax2.set_ylabel('∇S', fontsize=11)
        ax2.set_title('Radial Entropy Gradient Profile', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        plt.tight_layout()
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved entropy gradient plot: {output_path}")

    def plot_phase_evolution(
        self,
        r_fixed: float = 5.0,
        theta_fixed: float = np.pi/4,
        phi_fixed: float = 0.0,
        num_steps: int = 50,
        filename: str = "phase_evolution.png"
    ) -> None:
        """Plot phase evolution arg(Ψ) over time at fixed position.

        Parameters
        ----------
        r_fixed, theta_fixed, phi_fixed : float
            Fixed spatial coordinates
        num_steps : int
            Number of time steps
        filename : str
            Output filename
        """
        dt = self.cube.config.dt
        times = np.arange(num_steps) * dt * 10  # Scale up for visibility

        phases = []
        amplitudes = []

        for t in times:
            psi = self.cube.compute_wavefunction(r_fixed, theta_fixed, phi_fixed, t)
            phases.append(np.angle(psi))
            amplitudes.append(np.abs(psi))

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

        # Amplitude
        ax1.plot(times, amplitudes, 'b-', linewidth=2)
        ax1.set_ylabel('|Ψ|', fontsize=11)
        ax1.set_title(f'Wavefunction Evolution at (r={r_fixed:.1f}, θ={theta_fixed:.2f}, φ={phi_fixed:.2f})',
                     fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Phase
        ax2.plot(times, phases, 'r-', linewidth=2)
        ax2.set_xlabel('Time t (Planck units × 10)', fontsize=11)
        ax2.set_ylabel('arg(Ψ) (radians)', fontsize=11)
        ax2.set_title('Phase Evolution', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved phase evolution plot: {output_path}")

    def create_animation(
        self,
        frames: int = 50,
        r_max: float = 10.0,
        filename: str = "wavefunction_animation.gif"
    ) -> None:
        """Create animation of |Ψ|² evolution over time.

        Parameters
        ----------
        frames : int
            Number of animation frames
        r_max : float
            Maximum radial coordinate
        filename : str
            Output filename
        """
        print(f"Creating animation with {frames} frames...")

        n = 32  # Reduced resolution for animation performance
        r = np.linspace(0, r_max, n)
        theta = np.linspace(0, np.pi, n)
        R, Theta = np.meshgrid(r, theta)
        Phi = np.zeros_like(R)

        fig, ax = plt.subplots(figsize=(10, 8))

        def animate(frame):
            ax.clear()
            t = frame * self.cube.config.dt * 10
            psi_squared = self.cube.compute_probability_density(R, Theta, Phi, t)

            im = ax.imshow(
                psi_squared,
                extent=[0, r_max, 0, np.pi],
                origin='lower',
                cmap='viridis',
                aspect='auto',
                vmin=0,
                vmax=np.max(psi_squared) * 1.2
            )
            ax.set_xlabel('Radial coordinate r (Planck lengths)', fontsize=11)
            ax.set_ylabel('Polar angle θ (radians)', fontsize=11)
            ax.set_title(f'|Ψ(r,θ,φ=0,t)|² Evolution (frame {frame}/{frames})',
                        fontsize=12, fontweight='bold')

            return [im]

        anim = animation.FuncAnimation(fig, animate, frames=frames, interval=100, blit=False)

        output_path = self.output_dir / filename
        anim.save(output_path, writer='pillow', fps=10, dpi=100)
        plt.close()

        print(f"✓ Saved animation: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Visualize entropic wavefunction Ψ(r,θ,φ,t)")
    parser.add_argument("--output", default="analysis/results/wavefunction", help="Output directory")
    parser.add_argument("--animate", action="store_true", help="Create animation")
    parser.add_argument("--frames", type=int, default=50, help="Animation frames")
    parser.add_argument("--time", type=float, default=0.0, help="Time coordinate for static plots")
    parser.add_argument("--r-max", type=float, default=10.0, help="Maximum radial coordinate")

    args = parser.parse_args()

    print("=" * 70)
    print("Wavefunction Visualizer: Ψ(r,θ,φ,t)")
    print("=" * 70)
    print()

    visualizer = WavefunctionVisualizer(output_dir=args.output)

    # Create static plots
    print("\nGenerating static plots...")
    visualizer.plot_probability_density(t=args.time, r_max=args.r_max)
    visualizer.plot_entropy_gradient(t=args.time, r_max=args.r_max)
    visualizer.plot_phase_evolution()

    # Create animation if requested
    if args.animate:
        print("\nGenerating animation...")
        visualizer.create_animation(frames=args.frames, r_max=args.r_max)

    print("\n" + "=" * 70)
    print("✓ Visualization complete!")
    print(f"  Output directory: {visualizer.output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
