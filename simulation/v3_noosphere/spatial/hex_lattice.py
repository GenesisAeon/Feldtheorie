"""Hexagonal Lattice System for V3 Noosphere.

This module implements the spatial foundation for Project Noosphere — a hexagonal
grid topology that allows agents to inhabit real geometric space. Unlike the
abstract agent lists of V2.0, V3 agents exist at specific hex coordinates and
interact based on spatial proximity.

Hex grids use axial coordinates (q, r) where:
- q: column (horizontal axis)
- r: row (diagonal axis)

References:
- Red Blob Games: https://www.redblobgames.com/grids/hexagons/
- Crystalline lattices in condensed matter physics
- V10 Oracle HEX resonance (16-dimensional embedding)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

import numpy as np


@dataclass(frozen=True)
class HexCoord:
    """Axial coordinate for hexagonal grids.

    Uses the "pointy-top" orientation with axial (q, r) coordinates.
    The third cube coordinate s = -q - r is derived (ensuring q + r + s = 0).
    """

    q: int  # Column
    r: int  # Row

    @property
    def s(self) -> int:
        """Derived cube coordinate."""
        return -self.q - self.r

    def __add__(self, other: HexCoord) -> HexCoord:
        return HexCoord(self.q + other.q, self.r + other.r)

    def __sub__(self, other: HexCoord) -> HexCoord:
        return HexCoord(self.q - other.q, self.r - other.r)

    def __mul__(self, scalar: int) -> HexCoord:
        return HexCoord(self.q * scalar, self.r * scalar)

    def distance(self, other: HexCoord) -> int:
        """Manhattan distance on hex grid (minimum number of steps)."""
        return (abs(self.q - other.q) + abs(self.q + self.r - other.q - other.r) + abs(self.r - other.r)) // 2

    def neighbors(self) -> List[HexCoord]:
        """Six adjacent hex cells in clockwise order (starting from +q direction)."""
        directions = [
            HexCoord(+1, 0),   # East
            HexCoord(+1, -1),  # Northeast
            HexCoord(0, -1),   # Northwest
            HexCoord(-1, 0),   # West
            HexCoord(-1, +1),  # Southwest
            HexCoord(0, +1),   # Southeast
        ]
        return [self + d for d in directions]

    def ring(self, radius: int) -> List[HexCoord]:
        """All hex cells at exactly 'radius' distance from this coordinate."""
        if radius == 0:
            return [self]

        results = []
        # Start at radius steps in the -q direction
        hex_coord = self + HexCoord(-radius, radius)

        # Walk around the ring (6 sides, each with 'radius' steps)
        directions = [
            HexCoord(+1, 0),   # East
            HexCoord(+1, -1),  # Northeast
            HexCoord(0, -1),   # Northwest
            HexCoord(-1, 0),   # West
            HexCoord(-1, +1),  # Southwest
            HexCoord(0, +1),   # Southeast
        ]

        for direction in directions:
            for _ in range(radius):
                results.append(hex_coord)
                hex_coord = hex_coord + direction

        return results

    def spiral(self, max_radius: int) -> List[HexCoord]:
        """All hex cells within 'max_radius' distance (including center)."""
        results = [self]
        for r in range(1, max_radius + 1):
            results.extend(self.ring(r))
        return results

    def to_pixel(self, hex_size: float = 1.0) -> Tuple[float, float]:
        """Convert axial coordinates to pixel coordinates (pointy-top orientation).

        Args:
            hex_size: Distance from hex center to vertex (radius)

        Returns:
            (x, y) pixel coordinates
        """
        x = hex_size * (math.sqrt(3) * self.q + math.sqrt(3) / 2 * self.r)
        y = hex_size * (3.0 / 2 * self.r)
        return (x, y)


@dataclass
class HexCell:
    """A single hex cell in the lattice with associated properties."""

    coord: HexCoord
    terrain: str = "plains"  # Terrain type (plains, forest, mountain, water)
    resource: float = 1.0    # Resource density (0.0 = barren, 1.0 = abundant)
    occupied_by: str | None = None  # Agent ID if occupied

    def is_passable(self) -> bool:
        """Check if agents can move into this cell."""
        return self.terrain != "water"

    def is_habitable(self) -> bool:
        """Check if agents can settle/spawn here."""
        return self.terrain in {"plains", "forest"} and self.resource >= 0.3


class HexLattice:
    """Hexagonal grid lattice for spatial agent simulations.

    This lattice provides the spatial substrate for V3 Noosphere. Agents
    occupy hex cells, move between neighbors, and interact based on distance.
    """

    def __init__(self, radius: int = 10, seed: int | None = None):
        """Initialize hex lattice.

        Args:
            radius: Maximum distance from origin (creates hexagonal map)
            seed: Random seed for terrain generation
        """
        self.radius = radius
        self.rng = np.random.default_rng(seed)

        # Generate all hex coordinates within radius
        self.cells: Dict[HexCoord, HexCell] = {}
        origin = HexCoord(0, 0)
        for coord in origin.spiral(radius):
            self.cells[coord] = self._generate_cell(coord)

    def _generate_cell(self, coord: HexCoord) -> HexCell:
        """Generate a hex cell with random terrain and resources."""
        # Simple terrain generation (can be replaced with Perlin noise)
        terrain_roll = self.rng.random()

        if terrain_roll < 0.1:
            terrain = "water"
            resource = 0.0
        elif terrain_roll < 0.4:
            terrain = "forest"
            resource = self.rng.uniform(0.8, 1.5)
        elif terrain_roll < 0.65:
            terrain = "plains"
            resource = self.rng.uniform(0.5, 1.2)
        else:
            terrain = "mountain"
            resource = self.rng.uniform(0.2, 0.6)

        return HexCell(coord=coord, terrain=terrain, resource=resource)

    def get_cell(self, coord: HexCoord) -> HexCell | None:
        """Get hex cell at coordinate (returns None if out of bounds)."""
        return self.cells.get(coord)

    def get_neighbors(self, coord: HexCoord) -> List[HexCell]:
        """Get all valid neighboring cells."""
        neighbor_coords = coord.neighbors()
        return [self.cells[nc] for nc in neighbor_coords if nc in self.cells]

    def find_path(self, start: HexCoord, end: HexCoord) -> List[HexCoord] | None:
        """Find shortest path between two coordinates (A* search).

        Returns None if no path exists (e.g., blocked by water).
        """
        if start not in self.cells or end not in self.cells:
            return None

        # Simple breadth-first search (can be upgraded to A*)
        from collections import deque

        queue = deque([(start, [start])])
        visited = {start}

        while queue:
            current, path = queue.popleft()

            if current == end:
                return path

            for neighbor in current.neighbors():
                if neighbor not in visited and neighbor in self.cells:
                    cell = self.cells[neighbor]
                    if cell.is_passable():
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))

        return None  # No path found

    def get_area(self, center: HexCoord, radius: int) -> List[HexCell]:
        """Get all cells within radius of center."""
        coords = center.spiral(radius)
        return [self.cells[c] for c in coords if c in self.cells]

    def place_agent(self, coord: HexCoord, agent_id: str) -> bool:
        """Place agent at coordinate. Returns True if successful."""
        cell = self.get_cell(coord)
        if cell is None or cell.occupied_by is not None:
            return False

        cell.occupied_by = agent_id
        return True

    def remove_agent(self, coord: HexCoord) -> bool:
        """Remove agent from coordinate. Returns True if successful."""
        cell = self.get_cell(coord)
        if cell is None or cell.occupied_by is None:
            return False

        cell.occupied_by = None
        return True

    def move_agent(self, from_coord: HexCoord, to_coord: HexCoord) -> bool:
        """Move agent from one cell to another. Returns True if successful."""
        from_cell = self.get_cell(from_coord)
        to_cell = self.get_cell(to_coord)

        if from_cell is None or to_cell is None:
            return False

        if from_cell.occupied_by is None:
            return False

        if to_cell.occupied_by is not None or not to_cell.is_passable():
            return False

        agent_id = from_cell.occupied_by
        from_cell.occupied_by = None
        to_cell.occupied_by = agent_id
        return True

    def find_spawn_points(self, count: int) -> List[HexCoord]:
        """Find suitable spawn points for agents (habitable, unoccupied cells)."""
        habitable = [
            coord for coord, cell in self.cells.items()
            if cell.is_habitable() and cell.occupied_by is None
        ]

        if len(habitable) < count:
            return habitable  # Return all available

        # Random sampling without replacement
        indices = self.rng.choice(len(habitable), size=count, replace=False)
        return [habitable[i] for i in indices]

    def get_territory_map(self) -> Dict[str, Set[HexCoord]]:
        """Calculate territory control (Voronoi diagram based on agent positions).

        Returns mapping of agent_id -> set of controlled coordinates.
        """
        # Find all agent positions
        agent_positions: Dict[str, HexCoord] = {}
        for coord, cell in self.cells.items():
            if cell.occupied_by is not None:
                agent_positions[cell.occupied_by] = coord

        if not agent_positions:
            return {}

        # Assign each cell to nearest agent
        territories: Dict[str, Set[HexCoord]] = {aid: set() for aid in agent_positions}

        for coord in self.cells:
            min_distance = float('inf')
            closest_agent = None

            for agent_id, agent_coord in agent_positions.items():
                distance = coord.distance(agent_coord)
                if distance < min_distance:
                    min_distance = distance
                    closest_agent = agent_id

            if closest_agent is not None:
                territories[closest_agent].add(coord)

        return territories

    def render_ascii(self, width: int = 40, height: int = 20) -> str:
        """Render hex lattice as ASCII art.

        Legend:
        - . = plains
        - T = forest
        - ^ = mountain
        - ~ = water
        - @ = occupied by agent
        """
        lines = []

        for r in range(-height // 2, height // 2):
            line_chars = []
            for q in range(-width // 2, width // 2):
                coord = HexCoord(q, r)
                cell = self.get_cell(coord)

                if cell is None:
                    line_chars.append(" ")
                elif cell.occupied_by is not None:
                    line_chars.append("@")
                elif cell.terrain == "water":
                    line_chars.append("~")
                elif cell.terrain == "forest":
                    line_chars.append("T")
                elif cell.terrain == "mountain":
                    line_chars.append("^")
                else:
                    line_chars.append(".")

            # Offset every other row for hex grid appearance
            if r % 2 == 0:
                line_chars.insert(0, " ")

            lines.append("".join(line_chars))

        return "\n".join(lines)

    def get_statistics(self) -> Dict[str, float]:
        """Calculate lattice statistics."""
        total_cells = len(self.cells)
        terrain_counts = {}
        resource_sum = 0.0
        occupied_count = 0

        for cell in self.cells.values():
            terrain_counts[cell.terrain] = terrain_counts.get(cell.terrain, 0) + 1
            resource_sum += cell.resource
            if cell.occupied_by is not None:
                occupied_count += 1

        return {
            "total_cells": total_cells,
            "occupied_cells": occupied_count,
            "occupation_rate": occupied_count / total_cells if total_cells > 0 else 0.0,
            "average_resource": resource_sum / total_cells if total_cells > 0 else 0.0,
            "terrain_distribution": {
                terrain: count / total_cells
                for terrain, count in terrain_counts.items()
            },
        }


__all__ = ["HexCoord", "HexCell", "HexLattice"]
