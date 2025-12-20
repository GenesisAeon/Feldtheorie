"""Frame-based renderer for the primordial timeline visualization.

This script initializes a proto-stellar cloud of hydrogen and renders each
physics step to disk. The goal is to illustrate expansion, collapse, and core
ignition in a compact 2D timeline that can be stitched into a GIF.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import matplotlib.pyplot as plt
import numpy as np

from simulation.v4_stellar_forge.physics_engine import (
    AtomAgent,
    ElementTypes,
    gravity_step,
    fusion_step,
)

plt.switch_backend("Agg")


class BigBangRenderer:
    """Orchestrates initialization, simulation, and frame rendering."""

    def __init__(
        self,
        *,
        explosive_force: float = 1.5,
        swirl_factor: float = 0.4,
        seed: int = 42,
    ) -> None:
        self.explosive_force = explosive_force
        self.swirl_factor = swirl_factor
        self.random_state = np.random.default_rng(seed)
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
        photon_segments = []

        for particle in self.particles:
            if particle.element is ElementTypes.HYDROGEN:
                hydrogen_x.append(particle.position[0])
                hydrogen_y.append(particle.position[1])
            elif particle.element is ElementTypes.HELIUM:
                helium_x.append(particle.position[0])
                helium_y.append(particle.position[1])
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
        self.particles = fusion_step(self.particles)

    def run_timeline(self, frames: int = 200, output_dir: str | Path = "output/v4_frames") -> None:
        """Run the physics loop and persist each frame to disk."""

        if not self.particles:
            self.initialize_bang()

        frame_dir = Path(output_dir)
        frame_dir.mkdir(parents=True, exist_ok=True)

        for idx in range(frames):
            self._step_physics()
            frame_path = frame_dir / f"frame_{idx:03d}.png"
            self._render_frame(frame_path)

        print("Timeline generated in output/v4_frames/. Use a GIF tool to watch the star be born.")


def _unit_vector(vector: Iterable[float]) -> np.ndarray:
    vec = np.array(list(vector), dtype=float)
    norm = float(np.linalg.norm(vec))
    if norm == 0.0:
        return np.array([1.0, 0.0], dtype=float)
    return vec / norm


if __name__ == "__main__":
    renderer = BigBangRenderer()
    renderer.initialize_bang()
    renderer.run_timeline()
