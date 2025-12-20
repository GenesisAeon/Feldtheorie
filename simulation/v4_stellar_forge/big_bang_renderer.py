"""Frame-based renderer for the primordial timeline visualization.

This script initializes a proto-stellar cloud of hydrogen and renders each
physics step to disk. The goal is to illustrate expansion, collapse, and core
ignition in a compact 2D timeline that can be stitched into a GIF.
"""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from typing import Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

from simulation.v4_stellar_forge import multiverse_manager
from simulation.v4_stellar_forge.physics_engine import (
    AtomAgent,
    ElementTypes,
    apply_universe_dna,
    current_universe_dna,
    gravity_step,
    fusion_step,
)
from simulation.v4_stellar_forge.universe_dna import UniverseDNA

plt.switch_backend("Agg")


class BigBangRenderer:
    """Orchestrates initialization, simulation, and frame rendering."""

    def __init__(
        self,
        *,
        explosive_force: float = 1.5,
        swirl_factor: float = 0.4,
        seed: int = 42,
        dna: UniverseDNA | None = None,
    ) -> None:
        self.explosive_force = explosive_force
        self.swirl_factor = swirl_factor
        self.random_state = np.random.default_rng(seed)
        self.dna = dna or current_universe_dna()
        self.particles: List[AtomAgent] = []

    def initialize_bang(self, count: int = 150, radius: float = 2.0) -> None:
        """Spawn hydrogen particles near the origin with radial impulse."""

        positions = []
        for _ in range(count):
            r = radius * np.sqrt(self.random_state.random())
            theta = self.random_state.uniform(0, 2 * np.pi)
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            positions.append(np.array([x, y], dtype=float))

        particles: List[AtomAgent] = []
        for idx, pos in enumerate(positions):
            radial_dir = _unit_vector(pos)
            radial_velocity = radial_dir * self.explosive_force
            tangential = np.array([-radial_dir[1], radial_dir[0]]) * self.swirl_factor
            velocity = radial_velocity + tangential
            particles.append(
                AtomAgent(
                    position=pos,
                    velocity=velocity,
                    mass=1.0,
                    element=ElementTypes.HYDROGEN,
                )
            )

        self.particles = particles

    def _render_frame(self, frame_path: Path) -> None:
        fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
        fig.patch.set_facecolor("black")
        ax.set_facecolor("black")
        ax.set_xlim(-8, 8)
        ax.set_ylim(-8, 8)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal")

        hydrogen_x, hydrogen_y = [], []
        helium_x, helium_y = [], []
        carbon_x, carbon_y = [], []
        oxygen_x, oxygen_y = [], []
        silicon_x, silicon_y = [], []
        iron_x, iron_y = [], []
        remnant_x, remnant_y, remnant_sizes, remnant_colors = [], [], [], []
        photon_segments = []
        horizon_patches: List[Circle] = []

        for particle in self.particles:
            if particle.element is ElementTypes.HYDROGEN:
                hydrogen_x.append(particle.position[0])
                hydrogen_y.append(particle.position[1])
            elif particle.element is ElementTypes.HELIUM:
                helium_x.append(particle.position[0])
                helium_y.append(particle.position[1])
            elif particle.element is ElementTypes.CARBON:
                carbon_x.append(particle.position[0])
                carbon_y.append(particle.position[1])
            elif particle.element is ElementTypes.OXYGEN:
                oxygen_x.append(particle.position[0])
                oxygen_y.append(particle.position[1])
            elif particle.element is ElementTypes.SILICON:
                silicon_x.append(particle.position[0])
                silicon_y.append(particle.position[1])
            elif particle.element is ElementTypes.IRON:
                iron_x.append(particle.position[0])
                iron_y.append(particle.position[1])
            elif particle.element in (ElementTypes.NEUTRON_STAR, ElementTypes.BLACK_HOLE):
                remnant_x.append(particle.position[0])
                remnant_y.append(particle.position[1])
                if particle.element is ElementTypes.NEUTRON_STAR:
                    remnant_sizes.append(80)
                    remnant_colors.append(ElementTypes.NEUTRON_STAR.color)
                else:
                    remnant_sizes.append(120)
                    remnant_colors.append(ElementTypes.BLACK_HOLE.color)
                    horizon_patches.append(
                        Circle(
                            particle.position,
                            radius=max(0.2, particle.event_horizon),
                            fill=False,
                            edgecolor="#888888",
                            linewidth=1.2,
                            alpha=0.7,
                        )
                    )
            else:
                start = particle.position - particle.velocity * 0.3
                end = particle.position + particle.velocity * 0.3
                photon_segments.append((start, end))

        if hydrogen_x:
            ax.scatter(
                hydrogen_x,
                hydrogen_y,
                s=10,
                c=ElementTypes.HYDROGEN.color,
                alpha=0.9,
                label="H",
            )
        if helium_x:
            ax.scatter(
                helium_x,
                helium_y,
                s=60,
                c=ElementTypes.HELIUM.color,
                alpha=0.95,
                edgecolors="white",
                linewidths=0.5,
                label="He",
            )
        if carbon_x:
            ax.scatter(
                carbon_x,
                carbon_y,
                s=70,
                c=ElementTypes.CARBON.color,
                alpha=0.9,
                edgecolors="white",
                linewidths=0.4,
                label="C",
            )
        if oxygen_x:
            ax.scatter(
                oxygen_x,
                oxygen_y,
                s=75,
                c=ElementTypes.OXYGEN.color,
                alpha=0.9,
                edgecolors="white",
                linewidths=0.4,
                label="O",
            )
        if silicon_x:
            ax.scatter(
                silicon_x,
                silicon_y,
                s=80,
                c=ElementTypes.SILICON.color,
                alpha=0.9,
                edgecolors="white",
                linewidths=0.4,
                label="Si",
            )
        if iron_x:
            ax.scatter(
                iron_x,
                iron_y,
                s=90,
                c=ElementTypes.IRON.color,
                alpha=0.9,
                edgecolors="white",
                linewidths=0.4,
                label="Fe",
            )
        if remnant_x:
            ax.scatter(
                remnant_x,
                remnant_y,
                s=remnant_sizes,
                c=remnant_colors,
                alpha=0.95,
                edgecolors="white",
                linewidths=0.6,
                label="Remnant",
            )
        for patch in horizon_patches:
            ax.add_patch(patch)
        for start, end in photon_segments:
            ax.plot(
                [start[0], end[0]],
                [start[1], end[1]],
                c=ElementTypes.PHOTON.color,
                linewidth=1.5,
            )

        ax.legend(loc="upper right", frameon=False, fontsize=8, labelcolor="white")
        ax.spines[:].set_visible(False)
        ax.set_title("Cosmic Cinema: Primordial Timeline", color="white", fontsize=10)
        fig.savefig(frame_path, facecolor=fig.get_facecolor())
        plt.close(fig)

    def _step_physics(self) -> None:
        gravity_step(self.particles)
        self.particles = fusion_step(self.particles, dna=self.dna)

    def run_timeline(self, frames: int = 200, output_dir: str | Path = "output/v4_frames") -> None:
        """Run the physics loop and persist each frame to disk."""

        if not self.particles:
            self.initialize_bang()

        frame_dir = Path(output_dir)
        frame_dir.mkdir(parents=True, exist_ok=True)

        for idx in range(frames):
            self._step_physics()
            multiverse_manager.process_queue()
            frame_path = frame_dir / f"frame_{idx:03d}.png"
            self._render_frame(frame_path)

        # Final sweep to ensure any queued universes launch before exit
        multiverse_manager.process_queue()

        print(
            f"Timeline generated in {frame_dir}/. Use a GIF tool to watch the star be born."
        )


def _unit_vector(vector: Iterable[float]) -> np.ndarray:
    vec = np.array(list(vector), dtype=float)
    norm = float(np.linalg.norm(vec))
    if norm == 0.0:
        return np.array([1.0, 0.0], dtype=float)
    return vec / norm


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a primordial universe timeline.")
    parser.add_argument(
        "--seed",
        type=str,
        default="42",
        help="Integer seed or JSON-encoded UniverseDNA payload",
    )
    parser.add_argument(
        "--dna",
        type=str,
        default=None,
        help="Base64-encoded JSON UniverseDNA payload. Overrides --seed if provided.",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=200,
        help="Number of frames to render",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/v4_frames",
        help="Directory to store rendered frames",
    )
    parser.add_argument(
        "--gen",
        type=int,
        default=0,
        help="Generation index of this universe",
    )
    parser.add_argument(
        "--universe-id",
        type=str,
        default="local",
        help="Identifier assigned by the multiverse manager",
    )
    parser.add_argument(
        "--parent-id",
        type=str,
        default=None,
        help="Identifier of the parent universe, if any",
    )
    return parser.parse_args()


def _decode_dna(encoded: str | None) -> Tuple[UniverseDNA | None, int]:
    if not encoded:
        return None, 0

    try:
        decoded = base64.urlsafe_b64decode(encoded.encode("utf-8"))
        payload = json.loads(decoded.decode("utf-8"))
    except (ValueError, json.JSONDecodeError, KeyError):
        return None, 0

    dna = UniverseDNA(
        gravity_const=float(payload["gravity_const"]),
        fusion_threshold=float(payload["fusion_threshold"]),
        entropy_rate=float(payload["entropy_rate"]),
        mutation_scale=float(payload.get("mutation_scale", 0.05)),
    )
    seed_token = dna.to_seed_token()
    _, rng_seed = UniverseDNA.from_seed_token(seed_token)
    return dna, rng_seed


def main() -> None:
    args = _parse_args()
    dna, rng_seed = _decode_dna(args.dna)
    if dna is None:
        dna, rng_seed = UniverseDNA.from_seed_token(args.seed)
    if dna is not None:
        apply_universe_dna(dna)

    multiverse_manager.set_local_context(args.universe_id, args.gen)

    renderer = BigBangRenderer(seed=rng_seed, dna=dna)
    renderer.initialize_bang()
    renderer.run_timeline(frames=args.frames, output_dir=args.output)


if __name__ == "__main__":
    main()
