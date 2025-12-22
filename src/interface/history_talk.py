"""Chronicle dialogue interface for tracing cosmic ancestry."""
from __future__ import annotations

from typing import List, Optional

from core import AgentLog, TheChronicle


class HistoryTalk:
    """Provide narrative access to the Akasha Chronicle."""

    def __init__(self, chronicle: Optional[TheChronicle] = None) -> None:
        self.chronicle = chronicle or TheChronicle()

    def respond(self, question: str) -> str:
        material = self._extract_material(question)
        if not material:
            return "Die Chronik hört zu, aber kein bekanntes Material wurde gefragt."

        origin = self.chronicle.trace_resource(material)
        if not origin:
            return f"Keine Eintragung für {material.title()} in der Chronik gefunden."

        cycles_ago = max(0, self.chronicle.cycle - origin.cycle)
        ancestor = self._find_log(origin.producer_id)
        role = ancestor.role_name if ancestor else "Unbekannter Agent"
        resonance = ancestor.resonance if ancestor else 0.0

        if cycles_ago == 0:
            delta = "im aktuellen Zyklus"
        elif cycles_ago == 1:
            delta = "vor einem Zyklus"
        else:
            delta = f"vor {cycles_ago} Zyklen"

        return (
            f"{material.title()} stammt aus der {origin.cause} von Agent {origin.producer_id} "
            f"({role}), {delta}; Resonanzspur {resonance:.2f}."
        )

    def graveyard_overview(self) -> str:
        if not self.chronicle.graveyard:
            return "Der Friedhof ist leer. Noch keine Ahnen eingetragen."
        entries: List[str] = []
        for log in self.chronicle.graveyard[-5:]:
            entries.append(
                f"{log.agent_id}: {log.cause_of_death} → Materialien {dict(log.materials_released)}"
            )
        return " | ".join(entries)

    def _extract_material(self, prompt: str) -> Optional[str]:
        tokens = {"HYDROGEN", "HELIUM", "CARBON", "IRON", "GOLD", "HEAVY_METALS", "BLACK_HOLE_SEED"}
        prompt_upper = prompt.upper()
        for token in tokens:
            if token in prompt_upper:
                return token
        return None

    def _find_log(self, agent_id: str) -> Optional[AgentLog]:
        for log in reversed(self.chronicle.graveyard):
            if log.agent_id == agent_id:
                return log
        return None


__all__ = ["HistoryTalk"]
