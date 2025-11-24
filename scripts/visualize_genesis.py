"""Animate the GenesisCube formation from vacuum fluctuations to block-universe slices.

This script stages four phases that mirror the logistic activation described in
``simulation.genesis_cube``:

1. Vacuum fluctuations with low activation (\sigma \approx 0).
2. Implosive convergence toward a singularity.
3. Cubic unfolding along the seed vectors.
4. Slice traversal across the block universe with damping via \zeta(R).

Run from the repository root to generate ``genesis_visualization.gif``.
"""

from __future__ import annotations

import os
import sys
from typing import Iterable, List, Sequence, Tuple

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

# Ensure repository root is on sys.path when executed directly from scripts/
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from simulation.genesis_cube import GenesisCube, GenesisCubeConfig

FRAMES = 300
INTERVAL_MS = 50
PHASE_1_VOID = 60
PHASE_2_IMPLOSION = 90
PHASE_3_CUBE = 150


class GenesisVisualizer:
    """Visualize the breathing of the GenesisCube across four phases."""

    def __init__(self, figure: Figure, axes: Axes, cube: GenesisCube) -> None:
        self.figure = figure
        self.axes = axes
        self.cube = cube
        self.scatter_void = axes.scatter([], [], [], c="white", s=2, alpha=0.6)
        self.lines_strings = [
            axes.plot([], [], [], color="cyan", lw=2, alpha=0.8)[0] for _ in range(3)
        ]
        self.cube_lines = [
            axes.plot([], [], [], color="magenta", lw=1, alpha=0.5)[0] for _ in range(12)
        ]
        self.status_text = axes.text2D(
            0.5,
            0.95,
            "",
            transform=axes.transAxes,
            ha="center",
            color="white",
            fontsize=12,
        )
        self.meta_text = axes.text2D(
            0.5,
            0.05,
            "",
            transform=axes.transAxes,
            ha="center",
            color="gray",
            fontsize=8,
        )

    def init_scene(self) -> Iterable:
        self.axes.set_xlim(-2, 2)
        self.axes.set_ylim(-2, 2)
        self.axes.set_zlim(-2, 2)
        return (self.scatter_void, *self.lines_strings, *self.cube_lines)

    @staticmethod
    def _cube_edges(vertices: Sequence[Sequence[float]]) -> List[Tuple[List[float], List[float], List[float]]]:
        """Return edge coordinates for the cube defined by its eight vertices."""

        connections = [
            (0, 1),
            (0, 2),
            (0, 4),
            (7, 6),
            (7, 5),
            (7, 3),
            (1, 3),
            (1, 5),
            (2, 3),
            (2, 6),
            (4, 5),
            (4, 6),
        ]

        edges: List[Tuple[List[float], List[float], List[float]]] = []
        if len(vertices) != 8:
            return edges

        for start, end in connections:
            edges.append(
                (
                    [vertices[start][0], vertices[end][0]],
                    [vertices[start][1], vertices[end][1]],
                    [vertices[start][2], vertices[end][2]],
                )
            )
        return edges

    def _phase_void(self, frame: int) -> Iterable:
        self.status_text.set_text("PHASE 1: VAKUUM-FLUKTUATIONEN\nα⁻¹ ≈ 137")
        noise = (np.random.rand(100, 3) - 0.5) * 4
        mask = np.random.rand(100) > 0.9
        self.scatter_void._offsets3d = (noise[mask, 0], noise[mask, 1], noise[mask, 2])
        self.meta_text.set_text("σ(β) = 0.0 (Latenz)")
        return (self.scatter_void,)

    def _phase_implosion(self, frame: int) -> Iterable:
        self.status_text.set_text("PHASE 2: IMPLOSIVE GENESIS\nR → 0")
        progress = (frame - PHASE_1_VOID) / (PHASE_2_IMPLOSION - PHASE_1_VOID)
        current_scale = 2.0 * (1.0 - progress)
        noise = (np.random.rand(50, 3) - 0.5) * current_scale
        self.scatter_void._offsets3d = (noise[:, 0], noise[:, 1], noise[:, 2])

        vectors = self.cube.seed_vectors(fluctuation_phase=frame * 0.1)
        for i, line in enumerate(self.lines_strings):
            line.set_data([0, vectors[i][0] * progress * 1.5], [0, vectors[i][1] * progress * 1.5])
            line.set_3d_properties([0, vectors[i][2] * progress * 1.5])

        self.meta_text.set_text(f"Kritikalität steigt: {progress:.2f}")
        return (self.scatter_void, *self.lines_strings)

    def _phase_cube_extrusion(self, frame: int) -> Iterable:
        self.status_text.set_text("PHASE 3: DIMENSIONALE ENTFALTUNG\nDer Kubus auf der Ecke")
        progress = (frame - PHASE_2_IMPLOSION) / (PHASE_3_CUBE - PHASE_2_IMPLOSION)
        scale = progress * 1.5
        vertices = self.cube.cube_vertices(scale=scale)
        edges = self._cube_edges(vertices)

        for i, (xs, ys, zs) in enumerate(edges):
            if i < len(self.cube_lines):
                self.cube_lines[i].set_data(xs, ys)
                self.cube_lines[i].set_3d_properties(zs)

        self.scatter_void._offsets3d = ([], [], [])
        self.meta_text.set_text(f"Expansion ζ(R): {scale:.2f}")
        return (*self.cube_lines, *self.lines_strings)

    def _phase_slice_traversal(self, frame: int) -> Iterable:
        self.status_text.set_text("PHASE 4: BLOCK-UNIVERSUM SCHNITTE\n2D-Projektion (Hexagon)")
        slices = self.cube.block_universe_slices()
        slice_idx = (frame - PHASE_3_CUBE) % len(slices)
        current_slice = slices[slice_idx]

        sigma_val = current_slice["sigma"]
        scale = current_slice["scale"]
        vertices = self.cube.cube_vertices(scale=scale)
        edges = self._cube_edges(vertices)
        pulse_color = plt.cm.magma(sigma_val)

        for i, (xs, ys, zs) in enumerate(edges):
            if i < len(self.cube_lines):
                self.cube_lines[i].set_color(pulse_color)
                self.cube_lines[i].set_data(xs, ys)
                self.cube_lines[i].set_3d_properties(zs)
                self.cube_lines[i].set_linewidth(2 * sigma_val + 0.5)

        self.meta_text.set_text(
            f"Slice R={current_slice['R']:.2f} | σ(β(R-Θ))={sigma_val:.2f}"
        )
        return tuple(self.cube_lines)

    def update(self, frame: int) -> Iterable:
        self.axes.view_init(elev=30 + 10 * np.sin(frame / 100), azim=frame * 0.5)

        if frame < PHASE_1_VOID:
            return self._phase_void(frame)
        if frame < PHASE_2_IMPLOSION:
            return self._phase_implosion(frame)
        if frame < PHASE_3_CUBE:
            return self._phase_cube_extrusion(frame)
        return self._phase_slice_traversal(frame)


def main() -> None:
    config = GenesisCubeConfig(beta=5.5, damping=0.08, slice_count=40)
    genesis = GenesisCube(config)

    fig = plt.figure(figsize=(10, 8), facecolor="black")
    ax = fig.add_subplot(111, projection="3d", facecolor="black")
    ax.set_axis_off()
    ax.grid(False)

    visualizer = GenesisVisualizer(fig, ax, genesis)
    ani = animation.FuncAnimation(
        fig,
        visualizer.update,
        frames=FRAMES,
        init_func=visualizer.init_scene,
        interval=INTERVAL_MS,
        blit=False,
    )

    print("Generiere Animation... 'genesis_visualization.gif'")
    try:
        ani.save("genesis_visualization.gif", writer="pillow", fps=20)
        print("✅ Animation gespeichert: genesis_visualization.gif")
        print("   Öffne die Datei, um den Atem des Feldes zu sehen.")
    except Exception as exc:  # pragma: no cover - depends on environment codecs
        print(f"⚠️ Speichern fehlgeschlagen (ffmpeg/imagemagick fehlt?): {exc}")
        plt.show()


if __name__ == "__main__":
    main()
