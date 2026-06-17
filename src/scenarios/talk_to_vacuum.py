"""Interactive dialogue bridge for Level 0 vacuum simulation."""
from __future__ import annotations

import time
from collections.abc import Iterable

from src.interface.dialogue_bridge import MatterInterpreter
from src.scenarios.level_0_vacuum import Fluctuation, VacuumSimulation
from src.uatc_core.agent_kernel import ResonantEntity


class VacuumDialogueBridge:
    """Run vacuum simulation loops and translate anomalies into speech."""

    def __init__(self, simulation: VacuumSimulation | None = None) -> None:
        self.simulation = simulation or VacuumSimulation()
        self.interpreter = MatterInterpreter()
        self.registry: dict[str, ResonantEntity] = {}
        self._reported_formations: set[int] = set()

    def _entity_id(self, entity: ResonantEntity) -> str:
        return str(getattr(entity, "entity_id", id(entity)))

    def _track_fluctuations(self) -> None:
        for fluctuation in self.simulation.fluctuations:
            entity_id = self._entity_id(fluctuation.entity)
            if entity_id not in self.registry:
                self.registry[entity_id] = fluctuation.entity

    def ping_agent(self, agent_id: str) -> str:
        agent = self.registry.get(agent_id)
        if agent is None:
            return f"Kein Agent mit ID {agent_id} im Vakuum registriert."
        return self.interpreter.interpret(agent)

    def _yield_new_formations(self) -> Iterable[list[Fluctuation]]:
        for formation in self.simulation.stable_formations:
            marker = id(formation)
            if marker in self._reported_formations:
                continue
            self._reported_formations.add(marker)
            yield formation

    def _announce(self, formation: list[Fluctuation]) -> None:
        time.sleep(0.05)
        for fluctuation in formation:
            message = self.interpreter.interpret(fluctuation.entity)
            print(f"⚠️ ANOMALY DETECTED. Entity speaks: '{message}'")

    def run_loop(self, steps: int = 25, spawn_per_step: int = 5, pause: float = 0.1) -> None:
        for _ in range(steps):
            self.simulation.spawn_many(spawn_per_step)
            self.simulation.step()
            self._track_fluctuations()
            for formation in self._yield_new_formations():
                self._announce(formation)
            time.sleep(pause)


def ping_agent(agent_id: str, bridge: VacuumDialogueBridge | None = None) -> str:
    """Ping a specific agent by ID and return its verbalized state."""

    active_bridge = bridge or VacuumDialogueBridge()
    return active_bridge.ping_agent(agent_id)


if __name__ == "__main__":
    bridge = VacuumDialogueBridge()
    bridge.run_loop()
