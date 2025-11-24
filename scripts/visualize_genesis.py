r"""Animate the GenesisCube formation from vacuum fluctuations to block-universe slices.

This script stages four phases that mirror the logistic activation described in
``simulation.genesis_cube``:

1. Vacuum fluctuations with low activation (\sigma \approx 0).
2. Implosive convergence toward a singularity.
3. Cubic unfolding along the seed vectors.
4. Slice traversal across the block universe with damping via \zeta(R).

Run from the repository root to generate ``genesis_visualization.gif``.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import matplotlib

if os.environ.get("MPLBACKEND") is None:
    matplotlib.use("Agg")

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

# Ensure repository root is on sys.path when executed directly from scripts/
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from simulation.genesis_cube import GenesisCube, GenesisCubeConfig
from simulation.genesis_loader import index_presets, load_beta_presets, resolve_preset

FRAMES = 300
FPS = 20
INTERVAL_MS = 50
PHASE_1_RATIO = 0.2
PHASE_2_RATIO = 0.3
PHASE_3_RATIO = 0.5
DEFAULT_BETA = 5.5
DEFAULT_DAMPING = 0.08
DEFAULT_SLICES = 40


@dataclass(frozen=True)
class PhaseCutoffs:
    """Frame indices that delimit the four breathing phases."""

    phase_1: int
    phase_2: int
    phase_3: int

    @classmethod
    def from_total_frames(cls, total_frames: int) -> "PhaseCutoffs":
        phase_1 = max(1, int(total_frames * PHASE_1_RATIO))
        phase_2 = max(phase_1 + 1, int(total_frames * PHASE_2_RATIO))
        phase_3 = max(phase_2 + 1, int(total_frames * PHASE_3_RATIO))
        return cls(phase_1=phase_1, phase_2=phase_2, phase_3=phase_3)


class GenesisVisualizer:
    """Visualize the breathing of the GenesisCube across four phases."""

    def __init__(
        self,
        figure: Figure,
        axes: Axes,
        cube: GenesisCube,
        phase_cutoffs: PhaseCutoffs,
        preset_label: str | None = None,
        preset_color: str | None = None,
    ) -> None:
        self.figure = figure
        self.axes = axes
        self.cube = cube
        self.phase_cutoffs = phase_cutoffs
        self.preset_label = preset_label
        self.preset_color = preset_color
        self.scatter_void = axes.scatter([], [], [], c="white", s=2, alpha=0.6)
        self.lines_strings = [
            axes.plot([], [], [], color=self.preset_color or "cyan", lw=2, alpha=0.8)[0]
            for _ in range(3)
        ]
        self.cube_lines = [
            axes.plot([], [], [], color=self.preset_color or "magenta", lw=1, alpha=0.5)[0]
            for _ in range(12)
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
        self.meta_text.set_text(self._meta("σ(β) = 0.0 (Latenz)"))
        return (self.scatter_void,)

    def _phase_implosion(self, frame: int) -> Iterable:
        self.status_text.set_text("PHASE 2: IMPLOSIVE GENESIS\nR → 0")
        progress = (frame - self.phase_cutoffs.phase_1) / max(
            1, self.phase_cutoffs.phase_2 - self.phase_cutoffs.phase_1
        )
        current_scale = 2.0 * (1.0 - progress)
        noise = (np.random.rand(50, 3) - 0.5) * current_scale
        self.scatter_void._offsets3d = (noise[:, 0], noise[:, 1], noise[:, 2])

        vectors = self.cube.seed_vectors(fluctuation_phase=frame * 0.1)
        for i, line in enumerate(self.lines_strings):
            line.set_data([0, vectors[i][0] * progress * 1.5], [0, vectors[i][1] * progress * 1.5])
            line.set_3d_properties([0, vectors[i][2] * progress * 1.5])

        self.meta_text.set_text(self._meta(f"Kritikalität steigt: {progress:.2f}"))
        return (self.scatter_void, *self.lines_strings)

    def _phase_cube_extrusion(self, frame: int) -> Iterable:
        self.status_text.set_text("PHASE 3: DIMENSIONALE ENTFALTUNG\nDer Kubus auf der Ecke")
        progress = (frame - self.phase_cutoffs.phase_2) / max(
            1, self.phase_cutoffs.phase_3 - self.phase_cutoffs.phase_2
        )
        scale = progress * 1.5
        vertices = self.cube.cube_vertices(scale=scale)
        edges = self._cube_edges(vertices)

        for i, (xs, ys, zs) in enumerate(edges):
            if i < len(self.cube_lines):
                self.cube_lines[i].set_data(xs, ys)
                self.cube_lines[i].set_3d_properties(zs)

        self.scatter_void._offsets3d = ([], [], [])
        self.meta_text.set_text(self._meta(f"Expansion ζ(R): {scale:.2f}"))
        return (*self.cube_lines, *self.lines_strings)

    def _phase_slice_traversal(self, frame: int) -> Iterable:
        self.status_text.set_text("PHASE 4: BLOCK-UNIVERSUM SCHNITTE\n2D-Projektion (Hexagon)")
        slices = self.cube.block_universe_slices()
        slice_idx = (frame - self.phase_cutoffs.phase_3) % len(slices)
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
            self._meta(f"Slice R={current_slice['R']:.2f} | σ(β(R-Θ))={sigma_val:.2f}")
        )
        return tuple(self.cube_lines)

    def _meta(self, base: str) -> str:
        if self.preset_label:
            return f"{base} • Preset: {self.preset_label}"
        return base

    def update(self, frame: int) -> Iterable:
        self.axes.view_init(elev=30 + 10 * np.sin(frame / 100), azim=frame * 0.5)

        if frame < self.phase_cutoffs.phase_1:
            return self._phase_void(frame)
        if frame < self.phase_cutoffs.phase_2:
            return self._phase_implosion(frame)
        if frame < self.phase_cutoffs.phase_3:
            return self._phase_cube_extrusion(frame)
        return self._phase_slice_traversal(frame)


def parse_args(args: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Visualisiert die GenesisCube-Aktivierung mit σ(β(R-Θ))-Pulse. "
            "Standardmäßig wird genesis_visualization.gif erzeugt."
        )
    )
    parser.add_argument(
        "--preset",
        type=str,
        help=(
            "Name eines β/Θ-Presets aus data/derived/beta_estimates.csv, "
            "z.B. climate_amoc oder llm_emergent."
        ),
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="Zeige verfügbare Presets aus den empirischen β-Schätzungen und beende das Programm.",
    )
    parser.add_argument(
        "--beta",
        type=float,
        default=DEFAULT_BETA,
        help="Manuelle β-Vorgabe, falls kein Preset genutzt wird.",
    )
    parser.add_argument(
        "--theta",
        type=float,
        help="Optionaler Θ-Offset (überschreibt Wert aus Preset, falls gesetzt).",
    )
    parser.add_argument(
        "--damping",
        type=float,
        default=DEFAULT_DAMPING,
        help="ζ(R) Dämpfungsfaktor für die Scheiben." \
             " Standard: %(default)s",
    )
    parser.add_argument(
        "--slices",
        type=int,
        default=DEFAULT_SLICES,
        dest="slice_count",
        help="Anzahl der Block-Universum-Schnitte." \
             " Standard: %(default)s",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("genesis_visualization.gif"),
        help="Zielpfad für die Animation (Dateiendung bestimmt Writer).",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=FRAMES,
        help="Gesamtanzahl der Frames (Phasen werden proportional skaliert).",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=FPS,
        help="Bildrate beim Speichern der Animation.",
    )
    parser.add_argument(
        "--interval-ms",
        type=int,
        default=INTERVAL_MS,
        dest="interval_ms",
        help="Intervall zwischen Frames während der Generierung.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Zeige die Animation nach dem Speichern an (erfordert GUI-Backend).",
    )
    return parser.parse_args(args)


def main(cli_args: Sequence[str] | None = None) -> None:
    args = parse_args(cli_args)

    presets = load_beta_presets()
    if args.list_presets:
        print("Verfügbare Presets aus data/derived/beta_estimates.csv:")
        for preset in sorted(presets, key=lambda p: p.name):
            theta_str = f", Θ={preset.theta:.3f}" if preset.theta is not None else ""
            source_str = f" | Quelle: {preset.source}" if preset.source else ""
            domain_str = f" | Domäne: {preset.domain}" if getattr(preset, "domain", None) else ""
            color_str = f" | Farbe: {preset.color_hex}" if getattr(preset, "color_hex", None) else ""
            description = f" | {preset.description}" if getattr(preset, "description", None) else ""
            print(
                f"  - {preset.name}: β={preset.beta:.3f}{theta_str}{source_str}{domain_str}{color_str}{description}"
            )
        return

    phase_cutoffs = PhaseCutoffs.from_total_frames(args.frames)

    config = GenesisCubeConfig(beta=args.beta, damping=args.damping, slice_count=args.slice_count)
    if args.theta is not None:
        config.theta = args.theta

    preset_label = None
    preset_color = None
    if args.preset:
        preset_index = index_presets(presets)
        preset = resolve_preset(args.preset, preset_index)
        config = preset.apply_to_config(config)
        preset_label = f"{preset.name} ({preset.domain})" if preset.domain else preset.name
        preset_color = preset.color_hex

    genesis = GenesisCube(config)

    fig = plt.figure(figsize=(10, 8), facecolor="black")
    ax = fig.add_subplot(111, projection="3d", facecolor="black")
    ax.set_axis_off()
    ax.grid(False)

    visualizer = GenesisVisualizer(
        fig, ax, genesis, phase_cutoffs, preset_label=preset_label, preset_color=preset_color
    )
    ani = animation.FuncAnimation(
        fig,
        visualizer.update,
        frames=args.frames,
        init_func=visualizer.init_scene,
        interval=args.interval_ms,
        blit=False,
    )

    output_path = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = "pillow" if output_path.suffix.lower() == ".gif" else "ffmpeg"

    print(f"Generiere Animation... '{output_path}'")
    try:
        ani.save(output_path, writer=writer, fps=args.fps)
        print(f"✅ Animation gespeichert: {output_path}")
        print("   Öffne die Datei, um den Atem des Feldes zu sehen.")
    except Exception as exc:  # pragma: no cover - depends on environment codecs
        print(f"⚠️ Speichern fehlgeschlagen (ffmpeg/imagemagick fehlt?): {exc}")
    finally:
        if args.show:
            plt.show()


if __name__ == "__main__":
    main()
