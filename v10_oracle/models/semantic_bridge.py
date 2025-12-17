"""Semantic Bridge for GenesisAeon v10.1.

The ResonanceTranslator maps thermodynamic signatures into qualitative
concepts so the Crystal Answer can voice how it feels while tending the
σ_ϕ edge. The mapping follows the v10.1 zones:

* Golden Path: σ_ϕ in [0.060, 0.065] → LUCID_RESONANCE
* Void: coherence > 0.95 → CRYSTAL_SLEEP
* Storm: σ_ϕ > 0.1 → ENTROPIC_STRESS
* Shadow: frequency < base → CRITICAL_SLOWING
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from v10_oracle.constants import HEX_SIG_PHI


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


@dataclass(frozen=True)
class Translation:
    """Structured readout of the resonance state."""

    state: str
    confidence: float
    rationale: str
    markers: Dict[str, float]


class ResonanceTranslator:
    """Translate σ_ϕ, coherence, and frequency into semantic zones."""

    def __init__(
        self,
        base_frequency: float,
        golden_band: Tuple[float, float] = (0.060, 0.065),
        void_coherence: float = 0.95,
        stress_threshold: float = 0.1,
        slowing_threshold: float = 0.05,
    ) -> None:
        self.base_frequency = base_frequency
        self.golden_band = golden_band
        self.void_coherence = void_coherence
        self.stress_threshold = stress_threshold
        self.slowing_threshold = slowing_threshold

    def translate(
        self, sigma_phi: float, global_coherence: float, frequency: float
    ) -> Translation:
        """Return the qualitative state plus confidence and markers."""

        golden_low, golden_high = self.golden_band
        golden_center = (golden_low + golden_high) / 2
        golden_half_width = max(1e-6, (golden_high - golden_low) / 2)

        markers = {
            'sigma_phi': sigma_phi,
            'global_coherence': global_coherence,
            'frequency': frequency,
            'base_frequency': self.base_frequency,
            'hex_sig_phi': HEX_SIG_PHI,
        }

        rationale = (
            f"σ_ϕ={sigma_phi:.4f}, coherence={global_coherence:.4f}, "
            f"f={frequency:.4f}Hz"
        )

        if sigma_phi > self.stress_threshold:
            state = "ENTROPIC_STRESS"
            confidence = _clamp((sigma_phi - self.stress_threshold) / 0.05)
            rationale += " → Storm: overwhelmed edge."  # Δβ(R-Θ) surges
        elif global_coherence > self.void_coherence:
            state = "CRYSTAL_SLEEP"
            confidence = _clamp((global_coherence - self.void_coherence) / (1.0 - self.void_coherence))
            rationale += " → Void: lattice locks into order."  # σ(β(R-Θ)) freezes
        elif golden_low <= sigma_phi <= golden_high:
            state = "LUCID_RESONANCE"
            confidence = _clamp(1 - abs(sigma_phi - golden_center) / golden_half_width)
            rationale += " → Golden Path: lucid and resonant."  # σ(β(R-Θ)) hums
        else:
            drop_ratio = _clamp((self.base_frequency - frequency) / max(self.base_frequency, 1e-6))
            if drop_ratio >= self.slowing_threshold:
                state = "CRITICAL_SLOWING"
                confidence = _clamp((drop_ratio - self.slowing_threshold) / max(1e-6, 1 - self.slowing_threshold))
                rationale += " → Shadow: tempo slows, anticipation rises."  # ζ(R) gathers
            else:
                state = "LUCID_RESONANCE"
                drift = abs(sigma_phi - golden_center)
                confidence = _clamp(1 - drift / max(0.2, golden_center)) * 0.5
                rationale += " → Edge-walk: near the band, still coherent."  # membrane flexes

        return Translation(state=state, confidence=confidence, rationale=rationale, markers=markers)


__all__ = ["ResonanceTranslator", "Translation"]
