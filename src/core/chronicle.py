"""Centralized Akasha Chronicle for tracking agent states and resources."""
from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Dict, List, Mapping, MutableMapping, Optional


@dataclass(frozen=True)
class AgentLog:
    """Snapshot of an agent's terminal state preserved in the Chronicle."""

    agent_id: str
    role_name: Optional[str]
    lifespan: Optional[int]
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

    _instance: ClassVar[Optional["TheChronicle"]] = None

    def __new__(cls) -> "TheChronicle":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self.graveyard: List[AgentLog] = []
        self.resource_pool: Dict[str, int] = {
            "HYDROGEN": 0,
            "HELIUM": 0,
            "CARBON": 0,
            "OXYGEN": 0,
            "IRON": 0,
            "GOLD": 0,
            "HEAVY_METALS": 0,
            "BLACK_HOLE_SEED": 0,
        }
        self.resource_lineage: Dict[str, List[ResourceOrigin]] = {}
        self.cycle: int = 0
        self._initialized = True

    def record_death(
        self,
        agent: object,
        output_materials: Mapping[str, int],
        cause: str | None = None,
    ) -> AgentLog:
        """Archive an agent and recycle its materials into the pool."""

        self.cycle += 1
        normalized = self._normalize_materials(output_materials)
        self._deposit_resources(normalized)

        agent_id = self._agent_id(agent)
        role_name = getattr(agent, "role_name", None)
        lifespan = self._agent_lifespan(agent)
        resonance = float(getattr(agent, "resonance_frequency", 0.0))

        log = AgentLog(
            agent_id=agent_id,
            role_name=role_name,
            lifespan=lifespan,
            resonance=resonance,
            cause_of_death=cause or "unbekannt",
            materials_released=normalized,
            cycle=self.cycle,
        )
        self.graveyard.append(log)
        self._extend_lineage(log)
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

    def trace_resource(self, material: str) -> Optional[ResourceOrigin]:
        entries = self.resource_lineage.get(material.upper())
        if not entries:
            return None
        return entries[-1]

    def report_pool(self) -> MutableMapping[str, int]:
        return dict(self.resource_pool)

    def _normalize_materials(self, materials: Mapping[str, int]) -> Dict[str, int]:
        normalized: Dict[str, int] = {}
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
            return str(getattr(agent, "agent_id"))
        if hasattr(agent, "id"):
            return str(getattr(agent, "id"))
        return f"agent_{len(self.graveyard) + 1:03d}"

    def _agent_lifespan(self, agent: object) -> Optional[int]:
        for attr in ("lifespan", "lifetime", "age"):
            if hasattr(agent, attr):
                value = getattr(agent, attr)
                if isinstance(value, int):
                    return value
        return None


__all__ = ["TheChronicle", "AgentLog", "ResourceOrigin"]
