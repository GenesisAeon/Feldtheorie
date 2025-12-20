"""Lightweight physics engine for the stellar forge timeline renderer.

This module provides a compact 2D particle system with gravitational
interaction, staged fusion chains, and compact remnant dynamics. It now models
stellar death throes: fusion stalls on iron, supernovae eject outer layers, and
black holes accrete and evaporate via a Hawking-like process.
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
    CARBON = "CARBON"
    IRON = "IRON"
    NEUTRON_STAR = "NEUTRON_STAR"
    BLACK_HOLE = "BLACK_HOLE"
    PHOTON = "PHOTON"

    @property
    def color(self) -> str:
        """Return the matplotlib-compatible color for the element."""

        return {
            ElementTypes.HYDROGEN: "#3399ff",  # blue
            ElementTypes.HELIUM: "#ff4d4d",  # bright red
            ElementTypes.CARBON: "#9c27b0",  # purple
            ElementTypes.IRON: "#ff9800",  # orange
            ElementTypes.NEUTRON_STAR: "#cfd8dc",  # soft gray
            ElementTypes.BLACK_HOLE: "#111111",  # near-black
            ElementTypes.PHOTON: "#ffeb3b",  # yellow
        }[self]


@dataclass
class AtomAgent:
    """Particle representation used by the timeline simulation."""

    position: np.ndarray
    velocity: np.ndarray
    mass: float
    element: ElementTypes
    event_horizon: float = 0.0

    def __post_init__(self) -> None:
        self.position = np.array(self.position, dtype=float)
        self.velocity = np.array(self.velocity, dtype=float)
        self.refresh_horizon()

    def step(self, dt: float = 1.0) -> None:
        """Advance the particle in time using its current velocity."""

        self.position = self.position + self.velocity * dt

    def refresh_horizon(self) -> None:
        """Update the Schwarzschild-like horizon for black holes."""

        if self.element is ElementTypes.BLACK_HOLE:
            self.event_horizon = schwarzschild_radius(self.mass)


# Physical constants tailored for a visually stable simulation
GRAVITATIONAL_CONSTANT = 0.05
SOFTENING = 0.1
FUSION_DISTANCE = 0.5
PHOTON_SPEED = 3.0
EVENT_HORIZON_SCALE = 0.02
SUPERNOVA_MASS_THRESHOLD = 120.0
SUPERNOVA_IMPULSE = 2.5
BLACK_HOLE_THRESHOLD = 260.0
BLACK_HOLE_EVAPORATION_THRESHOLD = 35.0
HAWKING_DECAY_RATE = 0.001

MASS_BY_ELEMENT = {
    ElementTypes.HYDROGEN: 1.0,
    ElementTypes.HELIUM: 4.0,
    ElementTypes.CARBON: 12.0,
    ElementTypes.IRON: 56.0,
    ElementTypes.NEUTRON_STAR: 100.0,
    ElementTypes.BLACK_HOLE: 500.0,
    ElementTypes.PHOTON: 0.0,
}


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
    """Apply staged fusion, core collapse, and mass ejection events."""

    post_hydrogen = _fuse_clusters(
        particles,
        source_element=ElementTypes.HYDROGEN,
        distance=FUSION_DISTANCE,
        min_cluster_size=3,
        product_element=ElementTypes.HELIUM,
        product_mass=MASS_BY_ELEMENT[ElementTypes.HELIUM],
        velocity_scale=0.2,
        emit_photon=True,
    )

    post_helium = _fuse_clusters(
        post_hydrogen,
        source_element=ElementTypes.HELIUM,
        distance=FUSION_DISTANCE * 0.7,
        min_cluster_size=3,
        product_element=ElementTypes.CARBON,
        product_mass=MASS_BY_ELEMENT[ElementTypes.CARBON],
        velocity_scale=0.15,
        emit_photon=True,
    )

    post_carbon = _fuse_clusters(
        post_helium,
        source_element=ElementTypes.CARBON,
        distance=FUSION_DISTANCE * 0.8,
        min_cluster_size=2,
        product_element=ElementTypes.IRON,
        product_mass=MASS_BY_ELEMENT[ElementTypes.IRON],
        velocity_scale=0.1,
        emit_photon=False,
    )

    after_supernova = _supernova_step(post_carbon)
    return after_supernova


def _collect_clusters(
    particles: Sequence[AtomAgent],
    *,
    element: ElementTypes,
    distance: float,
) -> List[List[int]]:
    clusters: List[List[int]] = []
    visited: set[int] = set()

    for idx, particle in enumerate(particles):
        if idx in visited or particle.element is not element:
            continue
        stack = [idx]
        cluster: List[int] = []
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            cluster.append(current)
            for jdx, other in enumerate(particles):
                if jdx in visited or other.element is not element:
                    continue
                separation = float(
                    np.linalg.norm(particles[current].position - other.position)
                )
                if separation <= distance:
                    stack.append(jdx)
        clusters.append(cluster)
    return clusters


def _fuse_clusters(
    particles: Sequence[AtomAgent],
    *,
    source_element: ElementTypes,
    distance: float,
    min_cluster_size: int,
    product_element: ElementTypes,
    product_mass: float,
    velocity_scale: float,
    emit_photon: bool,
) -> List[AtomAgent]:
    remaining: List[AtomAgent] = []
    consumed: set[int] = set()

    clusters = _collect_clusters(particles, element=source_element, distance=distance)
    for cluster in clusters:
        if len(cluster) >= min_cluster_size:
            consumed.update(cluster)
            cluster_positions = [particles[i].position for i in cluster]
            cluster_velocities = [particles[i].velocity for i in cluster]
            centroid = np.mean(cluster_positions, axis=0)
            avg_velocity = np.mean(cluster_velocities, axis=0)

            product = AtomAgent(
                position=centroid,
                velocity=avg_velocity * velocity_scale,
                mass=product_mass,
                element=product_element,
            )
            remaining.append(product)
            if emit_photon:
                direction = _unit_vector(np.random.uniform(-1.0, 1.0, size=2))
                photon = AtomAgent(
                    position=centroid.copy(),
                    velocity=direction * PHOTON_SPEED,
                    mass=MASS_BY_ELEMENT[ElementTypes.PHOTON],
                    element=ElementTypes.PHOTON,
                )
                remaining.append(photon)
        else:
            for idx in cluster:
                consumed.add(idx)
                remaining.append(particles[idx])

    for idx, particle in enumerate(particles):
        if idx in consumed:
            continue
        remaining.append(particle)

    return remaining


def _supernova_step(particles: Sequence[AtomAgent]) -> List[AtomAgent]:
    non_photons = [p for p in particles if p.element is not ElementTypes.PHOTON]
    if not non_photons:
        return list(particles)

    total_mass = float(sum(p.mass for p in non_photons))
    iron_mass = float(
        sum(p.mass for p in non_photons if p.element is ElementTypes.IRON)
    )
    if total_mass < SUPERNOVA_MASS_THRESHOLD or iron_mass / total_mass < 0.5:
        return list(particles)

    center_of_mass = (
        sum(p.position * p.mass for p in non_photons) / max(total_mass, 1e-6)
    )
    ejected: List[AtomAgent] = []

    for particle in particles:
        if particle.element is ElementTypes.IRON:
            continue
        direction = particle.position - center_of_mass
        norm = float(np.linalg.norm(direction)) or 1.0
        impulse = direction / norm * SUPERNOVA_IMPULSE * (1.0 + norm * 0.05)
        particle.velocity = particle.velocity + impulse
        ejected.append(particle)

    collapse_mass = max(iron_mass, MASS_BY_ELEMENT[ElementTypes.NEUTRON_STAR])
    if collapse_mass >= BLACK_HOLE_THRESHOLD:
        remnant = AtomAgent(
            position=center_of_mass,
            velocity=np.zeros(2, dtype=float),
            mass=collapse_mass,
            element=ElementTypes.BLACK_HOLE,
            event_horizon=schwarzschild_radius(collapse_mass),
        )
        label = "BLACK HOLE"
    else:
        remnant = AtomAgent(
            position=center_of_mass,
            velocity=np.zeros(2, dtype=float),
            mass=collapse_mass,
            element=ElementTypes.NEUTRON_STAR,
        )
        label = "NEUTRON STAR"

    print(
        f"Supernova triggered: iron core mass={iron_mass:.1f}, remnant={label}, "
        f"ejecta={len(ejected)}"
    )
    return ejected + [remnant]


def accretion_step(particles: Sequence[AtomAgent]) -> List[AtomAgent]:
    """Allow black holes to accrete any particle inside their event horizon."""

    black_holes = [p for p in particles if p.element is ElementTypes.BLACK_HOLE]
    if not black_holes:
        return list(particles)

    survivors: List[AtomAgent] = []
    for particle in particles:
        if particle.element is ElementTypes.BLACK_HOLE:
            survivors.append(particle)
            continue
        consumed = False
        for bh in black_holes:
            distance = float(np.linalg.norm(particle.position - bh.position))
            if distance <= bh.event_horizon:
                pre_mass = bh.mass
                bh.mass += particle.mass
                if bh.mass > 0:
                    bh.velocity = (
                        (bh.velocity * pre_mass + particle.velocity * particle.mass)
                        / bh.mass
                    )
                bh.refresh_horizon()
                consumed = True
                break
        if not consumed:
            survivors.append(particle)
    return survivors


def hawking_process(particles: Sequence[AtomAgent]) -> List[AtomAgent]:
    """Evaporate black holes slowly and emit high-energy photons."""

    updated: List[AtomAgent] = []
    emissions: List[AtomAgent] = []

    for particle in particles:
        if particle.element is not ElementTypes.BLACK_HOLE:
            updated.append(particle)
            continue

        mass_loss = particle.mass * HAWKING_DECAY_RATE
        particle.mass -= mass_loss
        particle.refresh_horizon()
        direction = _unit_vector(np.random.uniform(-1.0, 1.0, size=2))
        emissions.append(
            AtomAgent(
                position=particle.position.copy(),
                velocity=direction * PHOTON_SPEED * 1.5,
                mass=MASS_BY_ELEMENT[ElementTypes.PHOTON],
                element=ElementTypes.PHOTON,
            )
        )
        if particle.mass <= BLACK_HOLE_EVAPORATION_THRESHOLD:
            burst = _gamma_flash(particle.position)
            emissions.extend(burst)
            print("Black hole evaporated in a final gamma flash.")
        else:
            updated.append(particle)

    return updated + emissions


def _gamma_flash(position: np.ndarray, rays: int = 6) -> List[AtomAgent]:
    photons: List[AtomAgent] = []
    for _ in range(rays):
        direction = _unit_vector(np.random.uniform(-1.0, 1.0, size=2))
        photons.append(
            AtomAgent(
                position=position.copy(),
                velocity=direction * PHOTON_SPEED * 3.0,
                mass=MASS_BY_ELEMENT[ElementTypes.PHOTON],
                element=ElementTypes.PHOTON,
            )
        )
    return photons


def schwarzschild_radius(mass: float) -> float:
    return max(0.2, mass * EVENT_HORIZON_SCALE)
