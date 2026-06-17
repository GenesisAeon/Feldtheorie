"""Stellar reincarnation loop connecting matter to the Chronicle."""
from __future__ import annotations

import random
from dataclasses import dataclass

from src.core import TheChronicle
from src.uatc_core.agent_kernel import ResonantEntity


@dataclass
class StarAgent:
    """Simple stellar agent representing a population tier."""

    entity: ResonantEntity
    generation: str
    mass: float
    metallicity: float
    agent_id: str
    age: int = 0
    lifespan: int = 3

    def tick(self) -> bool:
        self.age += 1
        return self.age >= self.lifespan


class StellarLifecycle:
    """Manage stellar birth, evolution, and recycling into the Chronicle."""

    def __init__(self, chronicle: TheChronicle | None = None) -> None:
        self.chronicle = chronicle or TheChronicle()
        self.population: list[StarAgent] = []
        self._sequence = 0

    def spawn_population_three(self, hydrogen_cost: int = 400) -> StarAgent | None:
        """Spawn a primordial Pop III star if hydrogen is abundant."""

        if not self.chronicle.has_resources({"HYDROGEN": hydrogen_cost}):
            return None

        consumed = self.chronicle.request_resources("HYDROGEN", hydrogen_cost)
        self._sequence += 1
        entity = ResonantEntity()
        entity.agent_id = f"pop3-{self._sequence:03d}"  # type: ignore[attr-defined]
        entity.incarnate({"name": "star", "resonance_hint": 1.3, "scale": 3})
        star = StarAgent(
            entity=entity,
            generation="Pop III",
            mass=max(1.0, consumed / 120.0),
            metallicity=0.0,
            agent_id=entity.agent_id,
            lifespan=random.randint(2, 4),
        )
        self.population.append(star)
        return star

    def spawn_population_two(self, hydrogen_cost: int = 300, metal_cost: int = 10) -> StarAgent | None:
        """Spawn a Pop II star when metals from older generations are present."""

        required = {"HYDROGEN": hydrogen_cost, "HEAVY_METALS": metal_cost}
        if not self.chronicle.has_resources(required):
            return None

        self.chronicle.request_resources("HYDROGEN", hydrogen_cost)
        self.chronicle.request_resources("HEAVY_METALS", metal_cost)
        self._sequence += 1
        entity = ResonantEntity()
        entity.agent_id = f"pop2-{self._sequence:03d}"  # type: ignore[attr-defined]
        entity.incarnate({"name": "star", "resonance_hint": 0.6, "scale": 3})
        star = StarAgent(
            entity=entity,
            generation="Pop II",
            mass=max(0.8, hydrogen_cost / 150.0),
            metallicity=0.15,
            agent_id=entity.agent_id,
            lifespan=random.randint(3, 6),
        )
        self.population.append(star)
        return star

    def step(self) -> list[StarAgent]:
        """Advance all stars by one epoch, recycling those that collapse."""

        ended: list[StarAgent] = []
        for star in list(self.population):
            if star.tick():
                ended.append(star)
                self._collapse(star)
                self.population.remove(star)
        return ended

    def _collapse(self, star: StarAgent) -> None:
        yields: dict[str, int] = {"HELIUM": int(star.mass * 40)}
        if star.generation == "Pop III":
            yields.update({
                "BLACK_HOLE_SEED": 1,
                "HEAVY_METALS": int(star.mass * 6) + 8,
            })
            cause = "hypernova"
        else:
            yields.update({
                "HEAVY_METALS": int(star.mass * 3) + 4,
                "GOLD": max(1, int(star.metallicity * 12)),
                "IRON": int(star.mass * 5),
            })
            cause = "angereicherte Supernova"
        self.chronicle.record_death(star.entity, yields, cause=cause)

    def narrative_state(self) -> str:
        """Return a concise textual snapshot of the current stellar field."""

        if not self.population:
            return "Keine Sterne aktiv. Der Pool wartet auf neue Inkarnationen."
        lines = []
        for star in self.population:
            remaining = max(0, star.lifespan - star.age)
            lines.append(
                f"{star.agent_id} ({star.generation}) — Masse {star.mass:.2f} M☉, Restlebensdauer {remaining}"
            )
        return " | ".join(lines)


__all__ = ["StarAgent", "StellarLifecycle"]
