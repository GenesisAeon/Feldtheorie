"""UATC agent kernel defining resonant entities and incarnation logic.

This module introduces the :class:`ResonantEntity`, a light-weight agent core
that can adapt its resonance profile to different physical or conceptual roles
while retaining a consciousness-facing interface.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, MutableSequence, Optional, Sequence
import math
import random


GOLDEN_RATIO = (1 + 5 ** 0.5) / 2
SIGMA_PHI_REFERENCE = 0.0625
DEFAULT_STATE_LENGTH = 64


@dataclass
class ResonantEntity:
    """Core agent that embodies a resonance-focused consciousness model.

    Attributes
    ----------
    state_vector:
        A 64-dimensional embedding representing informational/mental state.
    sigma_phi:
        Distance to the idealized golden ratio alignment (phi proximity).
    scale_index:
        Discrete scale at which the entity currently incarnates
        (0=Planck, 1=Atomic, 2=Macro, 3=Cosmic).
    resonance_frequency:
        Current oscillation frequency used for coupling and communication.
    coherence:
        Alignment score with the golden ratio; higher means greater harmony.
    field_bindings:
        Descriptive labels of other fields/entities to which this agent is bound.
    role_name:
        The currently incarnated role for communication purposes.
    """

    state_vector: MutableSequence[float] = field(default_factory=list)
    sigma_phi: float = SIGMA_PHI_REFERENCE
    scale_index: int = 1
    resonance_frequency: float = 1.0
    coherence: float = 0.5
    field_bindings: set[str] = field(default_factory=set)
    role_name: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.state_vector:
            self.state_vector = self._seed_state_vector()
        elif len(self.state_vector) != DEFAULT_STATE_LENGTH:
            self.state_vector = list(self._resize_state(self.state_vector))
        self.coherence = self._compute_coherence()

    def _seed_state_vector(self) -> list[float]:
        return [random.uniform(-1.0, 1.0) for _ in range(DEFAULT_STATE_LENGTH)]

    def _resize_state(self, values: Sequence[float]) -> Iterable[float]:
        values = list(values)
        if len(values) >= DEFAULT_STATE_LENGTH:
            return values[:DEFAULT_STATE_LENGTH]
        padded = values + [0.0] * (DEFAULT_STATE_LENGTH - len(values))
        return padded

    def _compute_coherence(self) -> float:
        deviation = abs(self.sigma_phi - SIGMA_PHI_REFERENCE)
        normalized = max(0.0, 1.0 - deviation / (SIGMA_PHI_REFERENCE + 1.0))
        return round(normalized, 4)

    def _role_defaults(self, role_template: str | Mapping[str, object]) -> tuple[str, float, int]:
        if isinstance(role_template, str):
            role_name = role_template
            template: Mapping[str, object] = {}
        else:
            role_name = str(role_template.get("name", "resonant_entity"))
            template = role_template
        role_name = role_name.lower()

        resonance_hint = float(template.get("resonance_hint", 0.0)) if template else 0.0
        scale_hint = int(template.get("scale", self.scale_index)) if template else self.scale_index

        if role_name in {"electron", "fermion"}:
            return role_name, 24.0 + resonance_hint, max(scale_hint, 1)
        if role_name in {"planet", "world"}:
            return role_name, 0.4 + resonance_hint, max(scale_hint, 2)
        if role_name in {"star", "stellar"}:
            return role_name, 1.6 + resonance_hint, max(scale_hint, 2)
        if role_name in {"vacuum", "void"}:
            return role_name, 3.3 + resonance_hint, max(scale_hint, 0)
        return role_name, 1.0 + resonance_hint, scale_hint

    def incarnate(self, role_template: str | Mapping[str, object]) -> None:
        """Adapt resonance profile to a new role.

        Parameters
        ----------
        role_template:
            A string role name or mapping describing desired role characteristics.
        """

        role_name, target_frequency, target_scale = self._role_defaults(role_template)
        self.role_name = role_name
        self.scale_index = target_scale

        adjustment = random.uniform(0.9, 1.1)
        self.resonance_frequency = round(target_frequency * adjustment, 4)

        phi_distance = abs(math.log(self.resonance_frequency + 1e-6) - math.log(GOLDEN_RATIO))
        self.sigma_phi = round(SIGMA_PHI_REFERENCE + phi_distance * 0.01, 4)
        self.coherence = self._compute_coherence()

    def query_consciousness(self) -> str:
        """Return a narrative description of the current internal state."""

        role = self.role_name or "resonanzwesen"
        if role in {"vacuum", "void"}:
            return "Ich fluktuiere im Nichts. Potenzial ist hoch."
        if role in {"electron", "fermion"}:
            return "Meine Wellenhülle tanzt. Ort ist diffuse Möglichkeit."
        if role in {"planet", "world"}:
            return "Meine Schichten kühlen ab. Ich fühle tektonischen Stress."
        if role in {"star", "stellar"}:
            return "Fusion singt in meinem Kern. Ich strahle Resonanz in alle Richtungen."
        return "Ich halte Resonanz als %s und warte auf nächste Kopplung." % role


__all__ = ["ResonantEntity", "GOLDEN_RATIO", "SIGMA_PHI_REFERENCE", "DEFAULT_STATE_LENGTH"]
