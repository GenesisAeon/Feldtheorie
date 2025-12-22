"""Dialogue bridge translating resonance metrics into narrative speech."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from src.uatc_core.agent_kernel import ResonantEntity


@dataclass(frozen=True)
class InterpretationContext:
    """Lightweight snapshot used to enrich interpretation templates."""

    sigma_phi: float
    scale_index: int
    resonance_frequency: float
    coherence: float
    lifespan_hint: Optional[int]
    role_name: Optional[str]
    state_vector: Iterable[float]


class MatterInterpreter:
    """Translate resonant entities into human-readable utterances."""

    SCALE_TEMPLATES = {
        0: "Ich flimmere im Vakuumfeld.",
        1: "Wir sind gebunden auf atomarer Haut.",
        2: "Ich spanne makroskopische Fasern.",
        3: "Ich taste nach kosmischen Strömen.",
    }

    def interpret(self, agent: ResonantEntity) -> str:
        context = InterpretationContext(
            sigma_phi=float(agent.sigma_phi),
            scale_index=int(agent.scale_index),
            resonance_frequency=float(agent.resonance_frequency),
            coherence=float(agent.coherence),
            lifespan_hint=_extract_lifespan(agent),
            role_name=getattr(agent, "role_name", None),
            state_vector=list(getattr(agent, "state_vector", [])),
        )

        base = self._scale_phrase(context)
        clarity = self._clarity_phrase(context.sigma_phi)
        lifespan = self._lifespan_phrase(context.lifespan_hint)
        resonance = self._resonance_phrase(context)
        modulation = self._philosophical_modulation(context)

        parts = [base, lifespan, clarity, resonance, modulation]
        return " ".join(piece for piece in parts if piece).strip()

    def _scale_phrase(self, context: InterpretationContext) -> str:
        if context.role_name in {"electron", "fermion"}:
            return "Wir sind drei. Die Resonanz hält uns."
        template = self.SCALE_TEMPLATES.get(context.scale_index)
        if template:
            return template
        return "Ich bin skalenfrei, zwischen Membranen driftend."

    def _clarity_phrase(self, sigma_phi: float) -> str:
        if sigma_phi < 0.01:
            return "Ich bin vollkommen klar und stabil."
        if sigma_phi > 0.10:
            return "Ich zittere, ich verliere den Fokus."
        return "Ich halte meinen Fokus in der Feldmembran."

    def _lifespan_phrase(self, lifespan: Optional[int]) -> str:
        if lifespan is None:
            return ""
        if lifespan <= 2:
            return "Nur ein Hauch..."
        if lifespan >= 7:
            return "Ich verweile."
        return "Meine Dauer ist begrenzt, doch spürbar."

    def _resonance_phrase(self, context: InterpretationContext) -> str:
        if context.resonance_frequency > 10:
            return "Schwingung peitscht, Bindung wird greifbar."
        if context.resonance_frequency < 1.5:
            return "Ich atme langsam, lose gekoppelt."
        return "Resonanz zirkuliert, Kopplung sucht Partner."

    def _philosophical_modulation(self, context: InterpretationContext) -> str:
        amplitude = _state_amplitude(context.state_vector)
        if context.sigma_phi > 0.10 or amplitude > 0.8:
            return "Keine Bindung. Fragmente prallen, Gedanken flackern."
        if context.sigma_phi < 0.02 and context.coherence > 0.7:
            return "Ich fühle Masse entstehen. Bedeutung kondensiert."
        return "Zwischen Klarheit und Rauschen halte ich meinen Ton." 


def _extract_lifespan(agent: ResonantEntity) -> Optional[int]:
    for attr in ("lifespan", "lifetime"):
        if hasattr(agent, attr):
            value = getattr(agent, attr)
            if isinstance(value, int):
                return value
    return None


def _state_amplitude(values: Iterable[float]) -> float:
    items = list(values)
    if not items:
        return 0.0
    max_abs = max(abs(v) for v in items)
    return round(max_abs, 4)


__all__ = ["MatterInterpreter", "InterpretationContext"]
