"""Atomic resonance kernel used for Level 1 genesis simulations."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from src.uatc_core.agent_kernel import SIGMA_PHI_REFERENCE, ResonantEntity


@dataclass(frozen=True)
class ResonanceMode:
    """Template describing a stable atomic resonance profile."""

    name: str
    frequency: float
    spin: float
    mantra: str
    scale: int = 1
    resonance_hint: float = 0.0


PROTON_MODE = ResonanceMode(
    name="proton",
    frequency=18.0,
    spin=0.5,
    mantra="Ich bin der Anker.",
    scale=1,
)

ELECTRON_MODE = ResonanceMode(
    name="electron",
    frequency=48.0,
    spin=-0.5,
    mantra="Ich bin die Wolke.",
    scale=1,
)


class AtomKernel(ResonantEntity):
    """Resonant entity tuned for atomic stability."""

    dialogue_style: str = "Fluid"
    spin: float = 0.0
    mantra: str = ""

    def _resolve_mode(self, mode: ResonanceMode | str | Mapping[str, object]) -> ResonanceMode:
        if isinstance(mode, ResonanceMode):
            return mode
        if isinstance(mode, str):
            key = mode.lower()
            if "electron" in key:
                return ELECTRON_MODE
            return PROTON_MODE
        name = str(mode.get("name", PROTON_MODE.name))
        spin = float(mode.get("spin", PROTON_MODE.spin))  # type: ignore[arg-type]
        freq = float(mode.get("frequency", PROTON_MODE.frequency))  # type: ignore[arg-type]
        mantra = str(mode.get("mantra", PROTON_MODE.mantra))
        scale = int(mode.get("scale", PROTON_MODE.scale))  # type: ignore[call-overload]
        hint = float(mode.get("resonance_hint", 0.0))  # type: ignore[arg-type]
        return ResonanceMode(name=name, frequency=freq, spin=spin, mantra=mantra, scale=scale, resonance_hint=hint)

    def incarnate(self, mode: ResonanceMode | str | Mapping[str, object]) -> None:  # type: ignore[override]
        resolved = self._resolve_mode(mode)
        self.role_name = resolved.name
        self.scale_index = max(1, resolved.scale)
        self.resonance_frequency = round(resolved.frequency + resolved.resonance_hint, 4)
        self.spin = resolved.spin
        self.mantra = resolved.mantra

        # Atomic incantation: extremely stable phi distance with rigid dialogue style.
        self.sigma_phi = SIGMA_PHI_REFERENCE + 0.00000001
        self.coherence = self._compute_coherence()
        self.dialogue_style = "Determiniert/Rigide"

    def query_consciousness(self) -> str:  # type: ignore[override]
        base = super().query_consciousness()
        tail = f"Spin={self.spin:+.1f}, Stil={self.dialogue_style}. {self.mantra}".strip()
        return f"{base} {tail}".strip()


__all__ = [
    "AtomKernel",
    "ResonanceMode",
    "PROTON_MODE",
    "ELECTRON_MODE",
]
