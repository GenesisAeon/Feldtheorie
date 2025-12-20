from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, List

import numpy as np

from simulation.v3_noosphere.spatial.hex_lattice import HexCoord, HexLattice
from simulation.v4_cosmos.entity import CosmicEntity


@dataclass
class GravityEngine:
    """A lightweight gravity simulator on the hex lattice."""

    lattice: HexLattice
    gravitational_constant: float = 0.6
    time_step: float = 0.25
    planet_threshold: float = 5.0
    star_threshold: float = 15.0

    def compute_forces(self, entities: Iterable[CosmicEntity]) -> dict[str, np.ndarray]:
        """Compute pairwise gravitational forces between entities."""

        entity_list = list(entities)
        forces: dict[str, np.ndarray] = {
            entity.agent_id: np.zeros(2, dtype=float) for entity in entity_list
        }

        for i, entity in enumerate(entity_list):
            for j, other in enumerate(entity_list):
                if i == j:
                    continue

                dq = other.coord.q - entity.coord.q
                dr = other.coord.r - entity.coord.r
                direction = np.array([dq, dr], dtype=float)

                distance = max(entity.coord.distance(other.coord), 1)
                norm = np.linalg.norm(direction)

                if norm == 0:
                    continue

                force_magnitude = (
                    self.gravitational_constant
                    * entity.mass
                    * other.mass
                    / float(distance ** 2)
                )
                forces[entity.agent_id] += (direction / norm) * force_magnitude

        return forces

    def step(self, entities: List[CosmicEntity]) -> List[CosmicEntity]:
        """Advance the simulation by one time step."""

        forces = self.compute_forces(entities)

        for entity in entities:
            acceleration = forces[entity.agent_id] / entity.mass
            entity.velocity += acceleration * self.time_step

            proposed = (
                np.array([entity.coord.q, entity.coord.r], dtype=float)
                + entity.velocity * self.time_step
            )
            new_coord = self._round_axial(proposed)

            if new_coord in self.lattice.cells:
                entity.set_coord(new_coord)
            else:
                entity.velocity *= -0.5

        return self._merge_collisions(entities)

    def _merge_collisions(self, entities: List[CosmicEntity]) -> List[CosmicEntity]:
        """Merge entities that occupy the same coordinate."""

        by_coord: defaultdict[HexCoord, List[CosmicEntity]] = defaultdict(list)
        for entity in entities:
            by_coord[entity.coord].append(entity)

        survivors: List[CosmicEntity] = []
        for coord, group in by_coord.items():
            if len(group) == 1:
                group[0].update_classification(self.planet_threshold, self.star_threshold)
                survivors.append(group[0])
                continue

            # Merge properties for co-located entities
            total_mass = sum(e.mass for e in group)
            if total_mass == 0:
                continue

            velocity = sum(e.velocity * e.mass for e in group) / total_mass
            mind_stack = np.stack([e.mind_state * e.mass for e in group])
            mind_state = mind_stack.sum(axis=0) / total_mass
            mind_state = mind_state / np.linalg.norm(mind_state)

            primary = group[0]
            primary.mass = total_mass
            primary.velocity = velocity
            primary.mind_state = mind_state
            primary.set_coord(coord)
            primary.update_classification(self.planet_threshold, self.star_threshold)

            survivors.append(primary)

        return survivors

    @staticmethod
    def _round_axial(axial: np.ndarray) -> HexCoord:
        """Round floating axial coordinates to the nearest valid hex."""

        x, z = float(axial[0]), float(axial[1])
        y = -x - z

        rx, ry, rz = round(x), round(y), round(z)
        x_diff = abs(rx - x)
        y_diff = abs(ry - y)
        z_diff = abs(rz - z)

        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        elif y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry

        return HexCoord(int(rx), int(rz))
