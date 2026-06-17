"""Hydrogen chamber simulation using atomic resonance logic."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

from src.scenarios.level_0_vacuum import HexGrid
from src.scenarios.level_1_atomic.atom_kernel import ELECTRON_MODE, PROTON_MODE, AtomKernel


@dataclass
class OrbitalSnapshot:
    proton: AtomKernel
    electron: AtomKernel
    proton_position: tuple[int, int]
    electron_position: tuple[int, int]
    binding_strength: float
    orbital_shell: int
    field_potential: float


class HydrogenChamber:
    """Spawn a simple hydrogen atom with probabilistic orbital dynamics."""

    def __init__(self, radius: int = 4) -> None:
        self.grid = HexGrid(radius=radius)
        self.proton = AtomKernel()
        self.electron = AtomKernel()
        self.proton_position = self._center_cell()
        self.electron_position = self._random_orbital_cell(shell=1)  # noqa: S604 - atomic shell number, not subprocess shell
        self._configure_atoms()

    def _center_cell(self) -> tuple[int, int]:
        if (0, 0) in self.grid.cells:
            return (0, 0)
        return self.grid.random_position()

    def _configure_atoms(self) -> None:
        self.proton.incarnate(PROTON_MODE)
        self.electron.incarnate(ELECTRON_MODE)
        self.proton.field_bindings.add("vacuum-anchor")
        self.electron.field_bindings.add("proton-link")

    def _frequency_alignment(self) -> float:
        ratio = self.electron.resonance_frequency / max(0.1, self.proton.resonance_frequency)
        alignment = 1.0 / (1.0 + abs(math.log(ratio)))
        return round(min(1.0, alignment), 3)

    def _orbital_cells(self, shell: int) -> list[tuple[int, int]]:
        return [
            coord
            for coord in self.grid.cells
            if self.grid.distance(coord, self.proton_position) == shell
        ]

    def _random_orbital_cell(self, shell: int) -> tuple[int, int]:
        candidates = self._orbital_cells(shell)
        if not candidates:
            return self.grid.random_position()
        weights = [self.grid.cells[pos].field_potential + 0.1 for pos in candidates]
        return random.choices(candidates, weights=weights, k=1)[0]

    def _choose_shell(self, alignment: float) -> int:
        if alignment >= 0.55:
            return 1
        if alignment >= 0.25:
            return 2
        return 2

    def _update_binding_state(self, alignment: float) -> None:
        if alignment < 0.25:
            self.electron.field_bindings.discard("proton-link")
        else:
            self.electron.field_bindings.add("proton-link")

    def step(self) -> OrbitalSnapshot:
        alignment = self._frequency_alignment()
        shell = self._choose_shell(alignment)
        self._update_binding_state(alignment)
        self.electron_position = self._random_orbital_cell(shell)
        potential = self.grid.cells[self.electron_position].field_potential

        return OrbitalSnapshot(
            proton=self.proton,
            electron=self.electron,
            proton_position=self.proton_position,
            electron_position=self.electron_position,
            binding_strength=alignment,
            orbital_shell=shell,
            field_potential=potential,
        )

    def iterate(self, steps: int = 6) -> list[OrbitalSnapshot]:
        return [self.step() for _ in range(steps)]


__all__ = ["HydrogenChamber", "OrbitalSnapshot"]
