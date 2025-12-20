"""Physical rules for nucleosynthesis on the hex lattice."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, List, Tuple

import numpy as np

from simulation.v3_noosphere.spatial.hex_lattice import HexCoord, HexLattice
from simulation.v4_stellar_forge.atomic_kernel import AtomAgent


@dataclass
class StellarForgeEngine:
    """Physics engine that combines gravity, degeneracy pressure, and fusion."""

    lattice: HexLattice
    gravitational_constant: float = 0.8
    time_step: float = 0.5
    pauli_limit: int = 3
    fusion_pressure_threshold: int = 4
    energy_per_fusion: float = 5.0
    rng: np.random.Generator = field(default_factory=np.random.default_rng)

    def compute_gravity(self, atoms: Iterable[AtomAgent]) -> dict[str, np.ndarray]:
        """Compute pairwise gravitational forces for massive particles."""

        particles = [a for a in atoms if a.mass > 0]
        forces: dict[str, np.ndarray] = {p.agent_id: np.zeros(2, dtype=float) for p in particles}

        for i, entity in enumerate(particles):
            for j, other in enumerate(particles):
                if i == j:
                    continue

                dq = other.coord.q - entity.coord.q
                dr = other.coord.r - entity.coord.r
                direction = np.array([dq, dr], dtype=float)
                distance = max(entity.coord.distance(other.coord), 1)
                norm = np.linalg.norm(direction)
                if norm == 0:
                    continue

                magnitude = (
                    self.gravitational_constant
                    * entity.mass
                    * other.mass
                    / float(distance**2)
                )
                forces[entity.agent_id] += (direction / norm) * magnitude

        return forces

    def step(self, atoms: List[AtomAgent]) -> List[AtomAgent]:
        """Advance the simulation by one tick."""

        atoms = self._advance_masses(atoms)
        atoms = self._handle_pauli_pressure(atoms)
        atoms = self._handle_fusion(atoms)
        atoms = self._advance_photons(atoms)
        return atoms

    def _advance_masses(self, atoms: List[AtomAgent]) -> List[AtomAgent]:
        forces = self.compute_gravity(atoms)

        for atom in atoms:
            if atom.mass <= 0:
                continue

            acceleration = forces.get(atom.agent_id, np.zeros(2, dtype=float)) / max(atom.mass, 1e-6)
            atom.velocity += acceleration * self.time_step

            proposed = (
                np.array([atom.coord.q, atom.coord.r], dtype=float)
                + atom.velocity * self.time_step
            )
            new_coord = self._round_axial(proposed)
            if new_coord in self.lattice.cells:
                atom.set_coord(new_coord)
            else:
                atom.velocity *= -0.25

        return atoms

    def _handle_pauli_pressure(self, atoms: List[AtomAgent]) -> List[AtomAgent]:
        occupancy: defaultdict[HexCoord, List[AtomAgent]] = defaultdict(list)
        for atom in atoms:
            occupancy[atom.coord].append(atom)

        for coord, group in occupancy.items():
            if len(group) <= 1:
                continue

            if len(group) < self.fusion_pressure_threshold:
                for atom in group:
                    jitter_direction = self.rng.normal(0, 1, 2)
                    norm = np.linalg.norm(jitter_direction) or 1.0
                    atom.velocity += (jitter_direction / norm) * 0.1
            elif len(group) <= self.pauli_limit:
                continue

        return atoms

    def _handle_fusion(self, atoms: List[AtomAgent]) -> List[AtomAgent]:
        occupancy: defaultdict[HexCoord, List[AtomAgent]] = defaultdict(list)
        for atom in atoms:
            occupancy[atom.coord].append(atom)

        updated: List[AtomAgent] = []
        next_id = max((int(a.agent_id.split("-")[-1]) for a in atoms if "-" in a.agent_id), default=0) + 1

        for coord, group in occupancy.items():
            hydrogens = [a for a in group if a.charge == 1.0 and a.mass > 0]
            if len(hydrogens) >= self.fusion_pressure_threshold:
                consumed = hydrogens[:4]
                survivors = [a for a in group if a not in consumed]
                for atom in consumed:
                    atoms.remove(atom)

                helium_temp = sum(a.temperature for a in consumed) / 4.0 + self.energy_per_fusion
                helium = AtomAgent.helium(
                    agent_id=f"He-{next_id}",
                    coord=coord,
                    temperature=helium_temp,
                )
                next_id += 1

                photons = self._spawn_photons(coord, count=2, start_id=next_id)
                next_id += len(photons)

                updated.extend(survivors)
                updated.append(helium)
                updated.extend(photons)
            else:
                updated.extend(group)

        return updated

    def _spawn_photons(self, coord: HexCoord, count: int, start_id: int) -> List[AtomAgent]:
        photons: List[AtomAgent] = []
        for i in range(count):
            direction = self._random_neighbor_direction()
            photons.append(
                AtomAgent.photon(
                    agent_id=f"γ-{start_id + i}",
                    coord=coord,
                    direction=direction,
                )
            )
        return photons

    def _advance_photons(self, atoms: List[AtomAgent]) -> List[AtomAgent]:
        for atom in atoms:
            if atom.type != "PHOTON":
                continue

            step_vec = atom.velocity
            axial = np.array([atom.coord.q, atom.coord.r], dtype=float) + step_vec
            new_coord = self._round_axial(axial)
            if new_coord in self.lattice.cells:
                atom.set_coord(new_coord)

        return atoms

    @staticmethod
    def _random_neighbor_direction() -> Tuple[float, float]:
        directions = [
            (1.0, 0.0),
            (1.0, -1.0),
            (0.0, -1.0),
            (-1.0, 0.0),
            (-1.0, 1.0),
            (0.0, 1.0),
        ]
        idx = np.random.randint(0, len(directions))
        return directions[idx]

    @staticmethod
    def _round_axial(axial: np.ndarray) -> HexCoord:
        x, z = float(axial[0]), float(axial[1])
        y = -x - z

        rx, ry, rz = round(x), round(y), round(z)
        x_diff, y_diff, z_diff = abs(rx - x), abs(ry - y), abs(rz - z)

        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        elif y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry

        return HexCoord(int(rx), int(rz))

