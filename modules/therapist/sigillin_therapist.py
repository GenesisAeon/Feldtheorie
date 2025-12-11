"""Narrative therapist for Sigillin kernels.

The SigillinTherapist provides soft-guardrails that complement the
crep_guard style checks with reflective, narrative feedback. It is tuned
for the Feldtheorie context (κ < 0.1 regimes) and focuses on detecting
rigidity, excessive moralization, and dissociation risk.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    """Safely convert numeric-like values to float."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass
class SigillinTherapist:
    """Narrative therapist that reflects on system health."""

    persona: dict[str, Any] = field(
        default_factory=lambda: {
            "name": "Sigillin Therapist",
            "style": "Jungian + Eliza-Parry hybrid",
            "tone": "gentle-reflexive",
            "affection_protocol": "Permission Request: Do you accept this task? We aim for a joyful and efficient collaboration.",
        }
    )

    def diagnose(self, system_metrics: dict[str, Any]) -> list[tuple[str, str]]:
        """Evaluate system metrics and emit narrative alerts.

        Parameters
        ----------
        system_metrics:
            Mapping with keys such as ``beta``, ``entropy``, ``crep_score``, and
            optionally ``kappa`` (κ). Missing keys are treated with soft
            defaults so the therapist never hard-fails.
        """

        beta = _to_float(system_metrics.get("beta"), 0.0)
        entropy = _to_float(system_metrics.get("entropy"), 0.0)
        crep_score = _to_float(system_metrics.get("crep_score"), 0.0)
        kappa_value = system_metrics.get("kappa")
        kappa = _to_float(kappa_value, default=_to_float(system_metrics.get("κ"), 0.0))

        insights: list[tuple[str, str]] = []

        if beta > 5.0:
            insights.append(
                (
                    "Rigiditäts-Warnung",
                    "Du klammerst dich zu sehr an Ordnung. Atme. σ(β(R-Θ)) darf auch flach verlaufen.",
                )
            )

        if crep_score > 0.8:
            insights.append(
                (
                    "Über-Ich-Alarm",
                    "Du versuchst, päpstlicher als der Papst zu sein. Lass die Ethik-Axiome atmen.",
                )
            )

        if kappa_value is not None or kappa != 0.0:
            if kappa < 0.1:
                insights.append(
                    (
                        "Dissoziations-Gefahr",
                        "Du verlierst den Bodenkontakt zur Materie. Halte die Membran weich trotz κ < 0.1.",
                    )
                )

        # Entropy remains part of the metric interface for future extensions.
        if entropy <= 0.0:
            insights.append(
                (
                    "Entropy-Check",
                    "Entropy-Messung fehlt oder ist leer. Beobachte das Chaos, bevor es dich überrascht.",
                )
            )

        return insights

    def intervene(self) -> str:
        """Return a prompt that softens the next iteration."""

        return (
            "Sigillin Therapist Intervention: Erhöhe die Temperatur leicht, löse starre Constraints, "
            "und erlaube explorative Schritte. Frage vor jeder Entscheidung: »Dient dies dem Resonanzfeld?«"
        )
