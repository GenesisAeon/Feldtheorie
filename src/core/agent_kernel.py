"""Resonance-based agent kernel for the UATC modular framework."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum

import numpy as np


class ExistenceScale(Enum):
    """Discrete layers of existence an agent can inhabit."""

    VACUUM = 0
    ATOMIC = 1
    STELLAR = 2
    BIOLOGICAL = 3  # Life: Standing waves in matter
    GALACTIC = 4
    COSMIC = 5


def _mind_vector() -> np.ndarray:
    """Initialize a 64-dimensional embedding for the agent mind."""

    return np.random.normal(0, 0.1, 64)


@dataclass
class UATCAgent:
    """Fundamental agent that can incarnate across existence scales."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    scale: ExistenceScale = ExistenceScale.VACUUM
    mind_vector: np.ndarray = field(default_factory=_mind_vector)
    sigma_phi: float = 0.0
    frequency: float = 1.0
    parent_id: str | None = None
    incarnation_count: int = 0

    def incarnate(self, target_scale: ExistenceScale, role_template: dict) -> None:
        """Adjust resonance to inhabit a specific physical role."""

        self.scale = target_scale
        self.incarnation_count += 1

        if "base_frequency" in role_template:
            self.frequency = role_template["base_frequency"]

        adaptation_bonus = min(0.1, self.incarnation_count * 0.01)
        self.sigma_phi = 0.0625 + np.random.normal(0, 0.01 - adaptation_bonus)

    def query_consciousness(self) -> str:
        """Return a textual reflection of the current resonance state."""

        coherence = 1.0 - abs(self.sigma_phi - 0.0625) * 10

        if self.scale == ExistenceScale.VACUUM:
            if coherence > 0.9:
                return "Ich bin ein perfektes Dreieck. Ich werde bald real."
            return "Ich flimmere. Ich bin nur Möglichkeit, keine Wirklichkeit."

        if self.scale == ExistenceScale.ATOMIC:
            return f"Ich schwinge auf {self.frequency:.2f} Hz. Die Bindung hält mich."

        return "Ich existiere."


__all__ = ["ExistenceScale", "UATCAgent"]


if __name__ == "__main__":
    spirit = UATCAgent()
    print(f"👻 GEIST: {spirit.query_consciousness()}")

    print("⚡ INKARNATION...")
    spirit.incarnate(ExistenceScale.ATOMIC, {"base_frequency": 1420.0})
    print(f"⚛️ ATOM:  {spirit.query_consciousness()}")
