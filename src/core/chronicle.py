"""Centralized Akasha Chronicle for tracking agent states and resources."""
from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from typing import Any, ClassVar


@dataclass(frozen=True)
class AgentLog:
    """Snapshot of an agent's terminal state preserved in the Chronicle."""

    agent_id: str
    role_name: str | None
    lifespan: int | None
    resonance: float
    cause_of_death: str
    materials_released: Mapping[str, int]
    cycle: int


@dataclass(frozen=True)
class ResourceOrigin:
    """Lineage information for resources recycled through the Chronicle."""

    material: str
    quantity: int
    producer_id: str
    cause: str
    cycle: int


class TheChronicle:
    """Singleton memory that conserves agent information and matter."""

    _instance: ClassVar[TheChronicle | None] = None

    def __new__(cls) -> TheChronicle:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self.graveyard: list[AgentLog] = []
        self.resource_pool: dict[str, int] = {
            "HYDROGEN": 1_000_000,
            "HELIUM": 0,
            "METALS": 0,
            "DUST": 0,
            "CARBON": 0,
            "OXYGEN": 0,
            "IRON": 0,
            "GOLD": 0,
            "HEAVY_METALS": 0,
            "BLACK_HOLE_SEED": 0,
        }
        self.elemental_pool = self.resource_pool
        self.resource_lineage: dict[str, list[ResourceOrigin]] = {}
        self.cycle: int = 0
        self.cycle_count: int = 0
        self._initialized = True

    def record_death(
        self,
        agent: object | Mapping[str, Any],
        output_materials: Mapping[str, int] | None = None,
        cause: str | None = None,
    ) -> AgentLog:
        """Archive an agent and recycle its materials into the pool.

        The Chronicle accepts either structured agent objects (legacy path)
        or plain dictionaries containing ``id``, ``role``, ``age`` and
        ``yield`` entries for rapid prototyping scenarios.
        """

        self.cycle += 1
        self.cycle_count = self.cycle

        # Support dictionary payloads coming from scripted scenarios
        if isinstance(agent, Mapping) and output_materials is None:
            payload = agent
            output_materials = payload.get("yield", {})  # type: ignore[assignment]
            agent_id = str(payload.get("id", "unknown"))
            role_name = payload.get("role", "PARTICLE")
            lifespan = self._coerce_int(payload.get("age"))
            resonance = float(payload.get("resonance", 0.0))
            cause = cause or payload.get("death_reason") or "recycled"
        else:
            agent_id = self._agent_id(agent)
            role_name = getattr(agent, "role_name", None)
            lifespan = self._agent_lifespan(agent)
            resonance = float(getattr(agent, "resonance_frequency", 0.0))
            cause = cause or "unbekannt"

        normalized = self._normalize_materials(output_materials or {})
        self._deposit_resources(normalized)

        log = AgentLog(
            agent_id=agent_id,
            role_name=role_name,
            lifespan=lifespan,
            resonance=resonance,
            cause_of_death=cause,
            materials_released=normalized,
            cycle=self.cycle,
        )
        self.graveyard.append(log)
        self._extend_lineage(log)

        print(f"📜 CHRONICLE: Agent {log.agent_id} recorded. Pool updated: {self.resource_pool}")
        return log

    def request_resources(self, resource: str, amount: int) -> int:
        """Withdraw a portion of a resource from the pool."""

        key = resource.upper()
        available = self.resource_pool.get(key, 0)
        granted = min(amount, available)
        self.resource_pool[key] = available - granted
        return granted

    def has_resources(self, required: Mapping[str, int]) -> bool:
        return all(self.resource_pool.get(k.upper(), 0) >= v for k, v in required.items())

    def request_incarnation(self, required_materials: Mapping[str, int]) -> bool:
        """Reserve materials for a new agent if the pool is sufficient."""

        if not self.has_resources(required_materials):
            return False
        for element, amount in required_materials.items():
            self.request_resources(element, amount)
        return True

    def trace_resource(self, material: str) -> ResourceOrigin | None:
        entries = self.resource_lineage.get(material.upper())
        if not entries:
            return None
        return entries[-1]

    def get_ancestry(self, agent_id: str) -> str:
        return f"Du bist Teil von Zyklus {self.cycle_count}. Vor dir starben {len(self.graveyard)} Ahnen."

    def report_pool(self) -> MutableMapping[str, int]:
        return dict(self.resource_pool)

    def _normalize_materials(self, materials: Mapping[str, int]) -> dict[str, int]:
        normalized: dict[str, int] = {}
        for key, value in materials.items():
            if value <= 0:
                continue
            normalized[key.upper()] = normalized.get(key.upper(), 0) + int(value)
        return normalized

    def _deposit_resources(self, materials: Mapping[str, int]) -> None:
        for key, value in materials.items():
            self.resource_pool[key] = self.resource_pool.get(key, 0) + int(value)

    def _extend_lineage(self, log: AgentLog) -> None:
        for material, quantity in log.materials_released.items():
            origin = ResourceOrigin(
                material=material,
                quantity=quantity,
                producer_id=log.agent_id,
                cause=log.cause_of_death,
                cycle=log.cycle,
            )
            lineage = self.resource_lineage.setdefault(material, [])
            lineage.append(origin)

    def _agent_id(self, agent: object) -> str:
        if hasattr(agent, "agent_id"):
            return str(agent.agent_id)
        if hasattr(agent, "id"):
            return str(agent.id)
        return f"agent_{len(self.graveyard) + 1:03d}"

    def _agent_lifespan(self, agent: object) -> int | None:
        for attr in ("lifespan", "lifetime", "age"):
            if hasattr(agent, attr):
                value = getattr(agent, attr)
                coerced = self._coerce_int(value)
                if coerced is not None:
                    return coerced
        return None

    def _coerce_int(self, value: object | None) -> int | None:
        if value is None:
            return None
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return int(value)
        return None


__all__ = ["TheChronicle", "AgentLog", "ResourceOrigin"]
