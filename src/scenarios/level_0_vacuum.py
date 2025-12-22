"""Level 0 vacuum fluctuations within the UATC resonance framework."""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, Iterable, List, Tuple
import random

from src.uatc_core.agent_kernel import ResonantEntity


@dataclass(frozen=True)
class HexCell:
    q: int
    r: int
    field_potential: float


class HexGrid:
    def __init__(self, radius: int = 5) -> None:
        self.radius = radius
        self.cells: Dict[Tuple[int, int], HexCell] = {}
        self._build_grid()

    def _build_grid(self) -> None:
        for q in range(-self.radius, self.radius + 1):
            r1 = max(-self.radius, -q - self.radius)
            r2 = min(self.radius, -q + self.radius)
            for r in range(r1, r2 + 1):
                self.cells[(q, r)] = HexCell(q=q, r=r, field_potential=random.uniform(0.0, 1.0))

    def random_position(self) -> Tuple[int, int]:
        return random.choice(list(self.cells.keys()))

    def neighbors(self, position: Tuple[int, int]) -> Iterable[Tuple[int, int]]:
        q, r = position
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        for dq, dr in directions:
            candidate = (q + dq, r + dr)
            if candidate in self.cells:
                yield candidate

    @staticmethod
    def distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        aq, ar = a
        bq, br = b
        return int((abs(aq - bq) + abs(aq + ar - bq - br) + abs(ar - br)) / 2)


@dataclass
class Fluctuation:
    entity: ResonantEntity
    position: Tuple[int, int]
    age: int = 0
    lifetime: int = field(default_factory=lambda: random.randint(1, 3))
    stable: bool = False


class VacuumSimulation:
    def __init__(self, radius: int = 5) -> None:
        self.grid = HexGrid(radius=radius)
        self.fluctuations: List[Fluctuation] = []
        self.stable_formations: List[List[Fluctuation]] = []

    def spawn_fluctuation(self) -> None:
        entity = ResonantEntity()
        entity.incarnate({"name": "vacuum", "resonance_hint": random.uniform(-0.5, 0.5), "scale": 0})
        cell = self.grid.random_position()
        self.fluctuations.append(Fluctuation(entity=entity, position=cell))

    def spawn_many(self, count: int = 5) -> None:
        for _ in range(count):
            self.spawn_fluctuation()

    def step(self) -> None:
        for fluctuation in list(self.fluctuations):
            fluctuation.age += 1
            if fluctuation.stable:
                continue
            if fluctuation.age >= fluctuation.lifetime:
                self.fluctuations.remove(fluctuation)

        self._stabilize_triangles()

    def _stabilize_triangles(self) -> None:
        candidates = [f for f in self.fluctuations if not f.stable]
        for triad in combinations(candidates, 3):
            if self._is_resonant_triangle(triad):
                for member in triad:
                    member.stable = True
                    member.entity.incarnate({"name": "electron", "resonance_hint": 0.0, "scale": 1})
                self.stable_formations.append(list(triad))

    def _is_resonant_triangle(self, triad: Tuple[Fluctuation, Fluctuation, Fluctuation]) -> bool:
        distances = {
            self.grid.distance(triad[0].position, triad[1].position),
            self.grid.distance(triad[1].position, triad[2].position),
            self.grid.distance(triad[2].position, triad[0].position),
        }
        return len(distances) == 1 and next(iter(distances)) in {1, 2}

    def query_vacuum(self) -> str:
        virtual_events = sum(1 for f in self.fluctuations if not f.stable)
        stable = len(self.stable_formations)
        return f"{virtual_events} virtuelle Ereignisse, {stable} stabile Formation erkannt."


__all__ = ["HexCell", "HexGrid", "Fluctuation", "VacuumSimulation"]
