"""
Ψ-Field Visualization Module

Provides comprehensive visualization tools for the entropische Wellenfunktion ψ_genesis:
- Probability density |ψ|² plots (1D, 2D, 3D)
- Radial distribution P(r) = r²|ψ|²
- Time evolution animations
- Tetrahedral symmetry visualization
- UTAC coupling plots (quantum → classical bridge)
- Entropy evolution

Usage:
    >>> from visualization.psi_field_viz import PsiFieldVisualizer
    >>> viz = PsiFieldVisualizer()
    >>> viz.plot_probability_density()
    >>> viz.plot_radial_distribution()
    >>> viz.animate_time_evolution()

References:
- pipelines/wavefunction/psi_field.py
- V6_Wellenfunktions_Integrationsplan.md
- GrundPrinzip Simulation.txt
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

try:
    from pipelines.wavefunction.psi_field import (
        ALPHA_INV,
        L_PLANCK,
        PHI,
        PsiField,
        PsiFieldConfig,
        PsiFieldPipeline,
        compute_psi_genesis,
    )

    PSIFIELD_AVAILABLE = True
except ImportError:
    PSIFIELD_AVAILABLE = False


class PsiFieldVisualizer:
    """Visualization tools for ψ_genesis wavefunction."""

    def __init__(
        self,
        config: PsiFieldConfig | None = None,
        figsize: tuple[int, int] = (12, 8),
        dpi: int = 100,
    ):
        """Initialize visualizer.

        Parameters
        ----------
        config : PsiFieldConfig, optional
            Wavefunction configuration
        figsize : tuple
            Figure size (width, height) in inches
        dpi : int
            Resolution (dots per inch)
        """
        if not PSIFIELD_AVAILABLE:
            raise ImportError("PsiFieldPipeline not available. Cannot create visualizer.")

        self.config = config or PsiFieldConfig()
        self.field = PsiField(self.config)
        self.pipeline = PsiFieldPipeline(self.config)
        self.figsize = figsize
        self.dpi = dpi

    def plot_probability_density(
        self,
        r_max: float = 5.0,
        n_points: int = 200,
        save_path: str | None = None,
    ) -> plt.Figure:
        """Plot radial probability density |ψ(r)|².

        Parameters
        ----------
        r_max : float
            Maximum radius (in Planck lengths)
        n_points : int
            Number of points
        save_path : str, optional
            Path to save figure

        Returns
        -------
        matplotlib Figure
        """
        # Compute wavefunction
        r = np.linspace(1e-37, r_max * L_PLANCK, n_points)
        theta = np.full_like(r, np.pi / 4)
        phi = np.full_like(r, 0.0)
        t = 0.0

        psi = self.field.compute_wavefunction(r, theta, phi, t)
        prob = np.abs(psi) ** 2

        # Plot
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        ax.plot(
            r / L_PLANCK, prob, linewidth=2, color="#2E86AB", label=r"$|\psi_{\mathrm{genesis}}|^2$"
        )
        ax.fill_between(r / L_PLANCK, 0, prob, alpha=0.3, color="#2E86AB")

        ax.set_xlabel(r"$r$ (Planck lengths $\ell_P$)", fontsize=12)
        ax.set_ylabel(r"Probability Density $|\psi|^2$", fontsize=12)
        ax.set_title(
            r"Entropische Wellenfunktion: $|\psi_{\mathrm{genesis}}(r)|^2$",
            fontsize=14,
            fontweight="bold",
        )
        ax.grid(True, alpha=0.3, linestyle="--")
        ax.legend(fontsize=10)

        # Add annotations
        max_prob_idx = np.argmax(prob)
        ax.annotate(
            f"Peak: r = {r[max_prob_idx]/L_PLANCK:.2f} ℓ_P",
            xy=(r[max_prob_idx] / L_PLANCK, prob[max_prob_idx]),
            xytext=(r[max_prob_idx] / L_PLANCK + r_max * 0.3, prob[max_prob_idx] * 0.8),
            arrowprops=dict(arrowstyle="->", color="red", lw=1.5),
            fontsize=10,
            color="red",
        )

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches="tight")
            print(f"Saved probability density plot to {save_path}")

        return fig

    def plot_radial_distribution(
        self,
        r_max: float = 10.0,
        n_points: int = 200,
        save_path: str | None = None,
    ) -> plt.Figure:
        """Plot radial distribution P(r) = r²|ψ|².

        Parameters
        ----------
        r_max : float
            Maximum radius
        n_points : int
            Number of points
        save_path : str, optional
            Path to save figure

        Returns
        -------
        matplotlib Figure
        """
        # Compute via pipeline
        results = self.pipeline.run(r_max=r_max, n_points=n_points, theta_phi_res=10, t=0.0)

        r_grid = results["r_grid"]
        radial_dist = results["radial_distribution"]
        mean_r = results["mean_r"]
        delta_r = results["delta_r"]

        # Plot
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        ax.plot(r_grid, radial_dist, linewidth=2, color="#A23B72", label=r"$P(r) = r^2 |\psi|^2$")
        ax.fill_between(r_grid, 0, radial_dist, alpha=0.3, color="#A23B72")

        # Mark mean and uncertainty
        ax.axvline(
            mean_r, color="green", linestyle="--", linewidth=2, label=f"⟨r⟩ = {mean_r:.2f} ℓ_P"
        )
        ax.axvspan(
            mean_r - delta_r,
            mean_r + delta_r,
            alpha=0.2,
            color="green",
            label=f"Δr = {delta_r:.2f} ℓ_P",
        )

        ax.set_xlabel(r"Radius $r$ (Planck lengths)", fontsize=12)
        ax.set_ylabel(r"Radial Distribution $P(r)$", fontsize=12)
        ax.set_title(r"Radiale Verteilung der Wellenfunktion", fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3, linestyle="--")
        ax.legend(fontsize=10)

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches="tight")
            print(f"Saved radial distribution plot to {save_path}")

        return fig

    def plot_2d_probability_map(
        self,
        r_max: float = 5.0,
        n_points: int = 100,
        t: float = 0.0,
        save_path: str | None = None,
    ) -> plt.Figure:
        """Plot 2D probability density map (x-y plane).

        Parameters
        ----------
        r_max : float
            Maximum radius
        n_points : int
            Grid resolution
        t : float
            Time point
        save_path : str, optional
            Path to save figure

        Returns
        -------
        matplotlib Figure
        """
        # Create 2D grid
        x = np.linspace(-r_max, r_max, n_points)
        y = np.linspace(-r_max, r_max, n_points)
        X, Y = np.meshgrid(x, y)

        # Convert to spherical
        R = np.sqrt(X**2 + Y**2)
        Theta = np.arccos(np.clip(0 / (R + 1e-10), -1, 1))  # z=0 plane
        Phi = np.arctan2(Y, X)

        # Compute wavefunction
        psi = self.field.compute_wavefunction(R, Theta, Phi, t)
        prob = np.abs(psi) ** 2

        # Plot
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Use log scale for better visibility
        prob_log = np.log10(prob + 1e-100)

        im = ax.contourf(X, Y, prob_log, levels=20, cmap="plasma")
        cbar = fig.colorbar(im, ax=ax, label=r"$\log_{10}(|\psi|^2)$")

        ax.set_xlabel(r"$x$ (Planck lengths)", fontsize=12)
        ax.set_ylabel(r"$y$ (Planck lengths)", fontsize=12)
        ax.set_title(r"2D Wahrscheinlichkeitsdichte (z=0 Ebene)", fontsize=14, fontweight="bold")
        ax.set_aspect("equal")

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches="tight")
            print(f"Saved 2D probability map to {save_path}")

        return fig

    def plot_tetrahedral_symmetry(
        self,
        r: float = 1.0,
        n_points: int = 100,
        save_path: str | None = None,
    ) -> plt.Figure:
        """Visualize tetrahedral angular symmetry Y_tetra(θ,φ).

        Parameters
        ----------
        r : float
            Fixed radius
        n_points : int
            Angular resolution
        save_path : str, optional
            Path to save figure

        Returns
        -------
        matplotlib Figure
        """
        # Angular grid
        theta = np.linspace(0, np.pi, n_points)
        phi = np.linspace(0, 2 * np.pi, n_points)
        Theta, Phi = np.meshgrid(theta, phi)

        # Compute angular component
        r_fixed = np.full_like(Theta, r)
        psi = self.field.compute_wavefunction(r_fixed, Theta, Phi, 0.0)
        angular_mag = np.abs(psi)

        # Convert to Cartesian for 3D plot
        X = angular_mag * np.sin(Theta) * np.cos(Phi)
        Y = angular_mag * np.sin(Theta) * np.sin(Phi)
        Z = angular_mag * np.cos(Theta)

        # Plot
        fig = plt.figure(figsize=self.figsize, dpi=self.dpi)
        ax = fig.add_subplot(111, projection="3d")

        # Surface plot with color based on magnitude
        surf = ax.plot_surface(
            X,
            Y,
            Z,
            cmap="viridis",
            facecolors=plt.cm.viridis(angular_mag / angular_mag.max()),
            alpha=0.8,
            edgecolor="none",
        )

        ax.set_xlabel("X", fontsize=10)
        ax.set_ylabel("Y", fontsize=10)
        ax.set_zlabel("Z", fontsize=10)
        ax.set_title(
            r"Tetraedrische Symmetrie $Y_{\mathrm{tetra}}(\theta, \phi)$",
            fontsize=14,
            fontweight="bold",
        )

        # Add colorbar
        mappable = plt.cm.ScalarMappable(cmap="viridis")
        mappable.set_array(angular_mag)
        fig.colorbar(mappable, ax=ax, shrink=0.5, label=r"$|Y_{\mathrm{tetra}}|$")

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches="tight")
            print(f"Saved tetrahedral symmetry plot to {save_path}")

        return fig

    def plot_time_evolution(
        self,
        r_max: float = 5.0,
        n_points: int = 100,
        t_values: list[float] | None = None,
        save_path: str | None = None,
    ) -> plt.Figure:
        """Plot time evolution of wavefunction.

        Parameters
        ----------
        r_max : float
            Maximum radius
        n_points : int
            Number of points
        t_values : list, optional
            Time points (in Planck times)
        save_path : str, optional
            Path to save figure

        Returns
        -------
        matplotlib Figure
        """
        if t_values is None:
            t_values = [0, 1e-44, 5e-44, 1e-43]

        r = np.linspace(1e-37, r_max * L_PLANCK, n_points)
        theta = np.full_like(r, np.pi / 4)
        phi = np.full_like(r, 0.0)

        fig, axes = plt.subplots(2, 2, figsize=self.figsize, dpi=self.dpi)
        axes = axes.flatten()

        for i, t in enumerate(t_values):
            psi = self.field.compute_wavefunction(r, theta, phi, t)
            prob = np.abs(psi) ** 2
            phase = np.angle(psi)

            ax = axes[i]
            ax2 = ax.twinx()

            # Probability
            ax.plot(r / L_PLANCK, prob, color="blue", linewidth=2, label=r"$|\psi|^2$")
            ax.fill_between(r / L_PLANCK, 0, prob, alpha=0.3, color="blue")

            # Phase
            ax2.plot(
                r / L_PLANCK,
                phase,
                color="red",
                linewidth=1.5,
                linestyle="--",
                alpha=0.7,
                label=r"Phase",
            )

            ax.set_xlabel(r"$r$ (ℓ_P)", fontsize=10)
            ax.set_ylabel(r"$|\psi|^2$", fontsize=10, color="blue")
            ax2.set_ylabel(r"Phase (rad)", fontsize=10, color="red")
            ax.set_title(f"t = {t:.2e} Planck times", fontsize=11)
            ax.tick_params(axis="y", labelcolor="blue")
            ax2.tick_params(axis="y", labelcolor="red")
            ax.grid(True, alpha=0.3)

        fig.suptitle(
            r"Zeitliche Evolution von $\psi_{\mathrm{genesis}}(r, t)$",
            fontsize=14,
            fontweight="bold",
        )
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches="tight")
            print(f"Saved time evolution plot to {save_path}")

        return fig

    def plot_entropy_evolution(
        self,
        r_max: float = 10.0,
        n_points: int = 50,
        n_times: int = 20,
        save_path: str | None = None,
    ) -> plt.Figure:
        """Plot entropy evolution S(t).

        Parameters
        ----------
        r_max : float
            Maximum radius
        n_points : int
            Spatial resolution
        n_times : int
            Number of time steps
        save_path : str, optional
            Path to save figure

        Returns
        -------
        matplotlib Figure
        """
        t_values = np.linspace(0, 1e-43, n_times)
        entropies = []

        r = np.linspace(1e-37, r_max * L_PLANCK, n_points)
        theta = np.full_like(r, np.pi / 4)
        phi = np.full_like(r, 0.0)

        for t in t_values:
            psi = self.field.compute_wavefunction(r, theta, phi, t)
            entropy = self.field.compute_entropy(psi)
            entropies.append(entropy)

        # Plot
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        ax.plot(t_values * 1e44, entropies, linewidth=2, color="#F18F01", marker="o", markersize=4)
        ax.fill_between(t_values * 1e44, 0, entropies, alpha=0.3, color="#F18F01")

        ax.set_xlabel(r"Zeit $t$ (in $10^{-44}$ s)", fontsize=12)
        ax.set_ylabel(r"von Neumann Entropie $S$", fontsize=12)
        ax.set_title(r"Entropie-Evolution $S(t)$", fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3, linestyle="--")

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches="tight")
            print(f"Saved entropy evolution plot to {save_path}")

        return fig

    def animate_wavefunction(
        self,
        r_max: float = 5.0,
        n_points: int = 150,
        n_frames: int = 50,
        save_path: str | None = None,
    ) -> FuncAnimation:
        """Create animation of wavefunction time evolution.

        Parameters
        ----------
        r_max : float
            Maximum radius
        n_points : int
            Spatial resolution
        n_frames : int
            Number of frames
        save_path : str, optional
            Path to save animation (GIF)

        Returns
        -------
        FuncAnimation
        """
        # Setup
        r = np.linspace(1e-37, r_max * L_PLANCK, n_points)
        theta = np.full_like(r, np.pi / 4)
        phi = np.full_like(r, 0.0)
        t_values = np.linspace(0, 5e-43, n_frames)

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        (line,) = ax.plot([], [], linewidth=2, color="#2E86AB")
        fill = ax.fill_between([], 0, [], alpha=0.3, color="#2E86AB")

        ax.set_xlim(0, r_max)
        ax.set_xlabel(r"$r$ (Planck lengths)", fontsize=12)
        ax.set_ylabel(r"$|\psi|^2$", fontsize=12)
        ax.set_title(r"$\psi_{\mathrm{genesis}}$ Animation", fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3)

        time_text = ax.text(
            0.02, 0.95, "", transform=ax.transAxes, fontsize=10, verticalalignment="top"
        )

        def init():
            line.set_data([], [])
            return line, time_text

        def animate(frame):
            t = t_values[frame]
            psi = self.field.compute_wavefunction(r, theta, phi, t)
            prob = np.abs(psi) ** 2

            line.set_data(r / L_PLANCK, prob)

            # Update fill (clear and redraw)
            nonlocal fill
            for coll in ax.collections:
                coll.remove()
            fill = ax.fill_between(r / L_PLANCK, 0, prob, alpha=0.3, color="#2E86AB")

            time_text.set_text(f"t = {t:.2e} Planck times")

            return line, time_text

        anim = FuncAnimation(
            fig, animate, init_func=init, frames=n_frames, interval=100, blit=False
        )

        if save_path:
            writer = PillowWriter(fps=10)
            anim.save(save_path, writer=writer)
            print(f"Saved animation to {save_path}")

        return anim


def create_full_visualization_suite(
    output_dir: str = "./outputs/psi_field_viz",
    r_max: float = 5.0,
    dpi: int = 150,
) -> None:
    """Create complete visualization suite for ψ_genesis.

    Parameters
    ----------
    output_dir : str
        Directory to save outputs
    r_max : float
        Maximum radius for plots
    dpi : int
        Resolution

    Creates:
    --------
    - probability_density.png
    - radial_distribution.png
    - probability_map_2d.png
    - tetrahedral_symmetry.png
    - time_evolution.png
    - entropy_evolution.png
    - wavefunction_animation.gif
    """
    import os

    os.makedirs(output_dir, exist_ok=True)

    viz = PsiFieldVisualizer(dpi=dpi)

    print("Creating ψ-field visualization suite...")

    viz.plot_probability_density(r_max=r_max, save_path=f"{output_dir}/probability_density.png")
    viz.plot_radial_distribution(r_max=r_max * 2, save_path=f"{output_dir}/radial_distribution.png")
    viz.plot_2d_probability_map(r_max=r_max, save_path=f"{output_dir}/probability_map_2d.png")
    viz.plot_tetrahedral_symmetry(r=1.0, save_path=f"{output_dir}/tetrahedral_symmetry.png")
    viz.plot_time_evolution(r_max=r_max, save_path=f"{output_dir}/time_evolution.png")
    viz.plot_entropy_evolution(r_max=r_max * 2, save_path=f"{output_dir}/entropy_evolution.png")
    viz.animate_wavefunction(r_max=r_max, save_path=f"{output_dir}/wavefunction_animation.gif")

    print(f"\n✓ Visualization suite complete! Saved to {output_dir}/")
    print("Files created:")
    for file in os.listdir(output_dir):
        print(f"  - {file}")


if __name__ == "__main__":
    print("=" * 70)
    print("Ψ-FIELD VISUALIZATION MODULE — V6 Framework")
    print("=" * 70)
    print()

    if not PSIFIELD_AVAILABLE:
        print("ERROR: PsiFieldPipeline not available. Cannot run visualizations.")
        exit(1)

    # Create full suite
    create_full_visualization_suite(
        output_dir="./outputs/psi_field_viz",
        r_max=5.0,
        dpi=100,
    )
