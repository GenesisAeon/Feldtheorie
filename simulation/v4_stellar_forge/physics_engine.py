"""Lightweight physics engine for the stellar forge timeline renderer.

This module provides a minimal 2D particle system with gravitational
interaction and a toy fusion rule that converts clustered hydrogen into helium
and photons. It is intentionally simple to keep the visualization fast and
reproducible for the frame-by-frame renderer.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Sequence

import numpy as np


class ElementTypes(str, Enum):
    """Supported element types for the stellar forge timeline."""

    HYDROGEN = "HYDROGEN"
    HELIUM = "HELIUM"
    PHOTON = "PHOTON"

    @property
    def color(self) -> str:
        """Return the matplotlib-compatible color for the element."""

        return {
            ElementTypes.HYDROGEN: "#3399ff",  # blue
            ElementTypes.HELIUM: "#ff4d4d",  # bright red
            ElementTypes.PHOTON: "#ffeb3b",  # yellow
        }[self]


@dataclass
class AtomAgent:
    """Particle representation used by the timeline simulation."""

    position: np.ndarray
    velocity: np.ndarray
    mass: float
    element: ElementTypes

    def step(self, dt: float = 1.0) -> None:
        """Advance the particle in time using its current velocity."""

        self.position = self.position + self.velocity * dt


# Physical constants tailored for a visually stable simulation
GRAVITATIONAL_CONSTANT = 0.05
SOFTENING = 0.1
FUSION_DISTANCE = 0.5
PHOTON_SPEED = 3.0


def gravity_step(particles: Sequence[AtomAgent], dt: float = 1.0) -> None:
    """Apply mutual gravitational acceleration between all massive particles.

    Photons (massless) drift without acceleration. A small softening term keeps
    forces bounded when particles get very close.
    """

    count = len(particles)
    forces: List[np.ndarray] = [np.zeros(2, dtype=float) for _ in range(count)]

    for i in range(count):
        for j in range(i + 1, count):
            delta = particles[j].position - particles[i].position
            distance = float(np.linalg.norm(delta))
            if distance == 0.0:
                continue

            direction = delta / distance
            magnitude = GRAVITATIONAL_CONSTANT * particles[i].mass * particles[j].mass
            magnitude /= (distance ** 2 + SOFTENING ** 2)
            force = direction * magnitude
            forces[i] += force
            forces[j] -= force

    for idx, particle in enumerate(particles):
        if particle.mass == 0:
            particle.step(dt)
            continue
        acceleration = forces[idx] / particle.mass
        particle.velocity = particle.velocity + acceleration * dt
        particle.step(dt)


def _unit_vector(seed_vector: Iterable[float]) -> np.ndarray:
    vector = np.array(list(seed_vector), dtype=float)
    norm = float(np.linalg.norm(vector))
    if norm == 0.0:
        return np.array([1.0, 0.0], dtype=float)
    return vector / norm


def fusion_step(particles: Sequence[AtomAgent]) -> List[AtomAgent]:
    """Fuse clusters of nearby hydrogen into helium and emit photons.

    Clusters of three or more hydrogen atoms within ``FUSION_DISTANCE`` collapse
    into a single helium nucleus placed at the cluster centroid. A photon is
    emitted in a random direction with high speed to visualize energy release.
    """

    remaining: List[AtomAgent] = []
    consumed: set[int] = set()

    for idx, particle in enumerate(particles):
        if particle.element is not ElementTypes.HYDROGEN or idx in consumed:
            continue

        cluster_indices = [idx]
        for jdx, other in enumerate(particles):
            if jdx == idx or jdx in consumed:
                continue
            if other.element is not ElementTypes.HYDROGEN:
                continue
            separation = float(np.linalg.norm(other.position - particle.position))
            if separation <= FUSION_DISTANCE:
                cluster_indices.append(jdx)

        if len(cluster_indices) >= 3:
            consumed.update(cluster_indices)
            cluster_positions = [particles[i].position for i in cluster_indices]
            cluster_velocities = [particles[i].velocity for i in cluster_indices]
            centroid = np.mean(cluster_positions, axis=0)
            avg_velocity = np.mean(cluster_velocities, axis=0)

            helium = AtomAgent(
                position=centroid,
                velocity=avg_velocity * 0.2,
                mass=4.0,
                element=ElementTypes.HELIUM,
            )
            photon_direction = _unit_vector(np.random.uniform(-1.0, 1.0, size=2))
            photon = AtomAgent(
                position=centroid.copy(),
                velocity=photon_direction * PHOTON_SPEED,
                mass=0.0,
                element=ElementTypes.PHOTON,
            )
            remaining.extend([helium, photon])
        else:
            remaining.append(particle)
            consumed.add(idx)

    for idx, particle in enumerate(particles):
        if idx in consumed:
            continue
        remaining.append(particle)

    return remaining
