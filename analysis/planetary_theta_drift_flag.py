r"""Adaptive Θ drift diagnostics for planetary tipping elements.

This guard listens to the planetary tipping lantern (AMOC, Grönland,
Amazonas, Permafrost) encoded in
``analysis/results/planetary_tipping_elements.json`` and quantifies how
wide the Θ confidence membranes remain.  Whenever the normalised width of
Θ or β rises above the configured steepness thresholds the script emits a
σ(β(R-Θ)) gap signal, recommending where additional data, analysis, or
simulator sweeps must focus.

Formal layer
============
* Parses the aggregated logistic quartet $(R, \Theta, \beta, \zeta(R))$.
* Computes the normalised confidence width for Θ and β per element.
* Tags elements whose Θ-band exceeds ``THETA_WIDTH_THRESHOLD`` or whose β
  width stays too broad for decisive falsification.
* Returns a JSON summary with reproducible statistics (mean, max, σ at
  Θ±ΔΘ/2) for downstream docs, data, and simulator layers.

Empirical layer
===============
* Input: ``analysis/results/planetary_tipping_elements.json``.
* Output: ``analysis/results/planetary_theta_drift_flags.json`` with
  tri-layer annotations, implementation guidance, and ΔAIC context.
* Provides CLI switches to point at alternative inputs/outputs so batch
  guards can reuse the diagnostic.

Poetic layer
============
* Notes where the Gaia membrane still wavers—when Θ breathes too
  broadly, σ(β(R-Θ)) cannot lock into resonance and the field requests
  new observations.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional


DEFAULT_INPUT = Path("analysis/results/planetary_tipping_elements.json")
DEFAULT_OUTPUT = Path("analysis/results/planetary_theta_drift_flags.json")

THETA_WIDTH_THRESHOLD = 0.25
BETA_WIDTH_THRESHOLD = 0.25


def logistic_response(R: float, theta: float, beta: float) -> float:
    """Return σ(β(R-Θ)) for a given control parameter ``R``."""

    return 1.0 / (1.0 + math.exp(-beta * (R - theta)))


@dataclass
class DriftSignal:
    """Structured carrier for Θ/β drift diagnostics."""

    element_id: str
    label: str
    theta: float
    theta_ci95: List[float]
    beta: float
    beta_ci95: List[float]
    logistic_r2: float
    theta_width_norm: float
    beta_width_norm: float
    sigma_theta_upper: float
    theta_gap_score: float
    beta_gap_score: float
    needs_adaptive_theta: bool
    needs_beta_precision: bool

    def to_payload(self) -> Dict[str, Any]:
        return {
            "id": self.element_id,
            "label": self.label,
            "theta": self.theta,
            "theta_ci95": self.theta_ci95,
            "beta": self.beta,
            "beta_ci95": self.beta_ci95,
            "logistic_r2": self.logistic_r2,
            "normalized_theta_ci_width": self.theta_width_norm,
            "normalized_beta_ci_width": self.beta_width_norm,
            "sigma_at_theta_upper": self.sigma_theta_upper,
            "theta_gap_score": self.theta_gap_score,
            "beta_gap_score": self.beta_gap_score,
            "needs_adaptive_theta": self.needs_adaptive_theta,
            "needs_beta_precision": self.needs_beta_precision,
        }


def _normalised_width(interval: Iterable[float], centre: float) -> float:
    lower, upper = tuple(interval)
    if centre == 0:
        return float("inf")
    return (upper - lower) / centre


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )


def load_input(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Input summary not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_drift(summary: Dict[str, Any]) -> Dict[str, Any]:
    aggregate = summary.get("aggregate", {})
    elements = summary.get("elements", [])

    signals: List[DriftSignal] = []
    theta_widths: List[float] = []
    beta_widths: List[float] = []

    for element in elements:
        theta = float(element["theta"])
        theta_ci = [float(value) for value in element.get("theta_ci95", [theta, theta])]
        beta = float(element["beta"])
        beta_ci = [float(value) for value in element.get("beta_ci95", [beta, beta])]
        logistic_r2 = float(element.get("logistic_r2", 0.0))

        theta_width_norm = _normalised_width(theta_ci, theta)
        beta_width_norm = _normalised_width(beta_ci, beta)

        sigma_upper = logistic_response(theta_ci[1], theta, beta)
        theta_gap_score = theta_width_norm * (1.0 - logistic_r2)
        beta_gap_score = beta_width_norm * (1.0 - logistic_r2)

        needs_adaptive_theta = theta_width_norm >= THETA_WIDTH_THRESHOLD
        needs_beta_precision = beta_width_norm >= BETA_WIDTH_THRESHOLD

        signals.append(
            DriftSignal(
                element_id=element["id"],
                label=element["label"],
                theta=theta,
                theta_ci95=theta_ci,
                beta=beta,
                beta_ci95=beta_ci,
                logistic_r2=logistic_r2,
                theta_width_norm=theta_width_norm,
                beta_width_norm=beta_width_norm,
                sigma_theta_upper=sigma_upper,
                theta_gap_score=theta_gap_score,
                beta_gap_score=beta_gap_score,
                needs_adaptive_theta=needs_adaptive_theta,
                needs_beta_precision=needs_beta_precision,
            )
        )

        theta_widths.append(theta_width_norm)
        beta_widths.append(beta_width_norm)

    flagged_theta = [signal for signal in signals if signal.needs_adaptive_theta]
    flagged_beta = [signal for signal in signals if signal.needs_beta_precision]

    def _mean(values: List[float]) -> Optional[float]:
        return float(mean(values)) if values else None

    overview = {
        "total_elements": len(signals),
        "theta_flags": len(flagged_theta),
        "beta_flags": len(flagged_beta),
        "theta_width_mean": _mean(theta_widths),
        "theta_width_max": max(theta_widths) if theta_widths else None,
        "beta_width_mean": _mean(beta_widths),
        "beta_width_max": max(beta_widths) if beta_widths else None,
        "theta_threshold": THETA_WIDTH_THRESHOLD,
        "beta_threshold": BETA_WIDTH_THRESHOLD,
        "flagged_elements": [signal.element_id for signal in flagged_theta],
    }

    delta_aic_linear = aggregate.get("null_models", {}).get("linear", {}).get("delta_aic")
    delta_aic_power = aggregate.get("null_models", {}).get("power_law", {}).get("delta_aic")

    tri_layer = {
        "formal": (
            "Θ-Bänder mit σ(β(R-Θ)) vergleichen: normalisierte Breite ≥ {thr:.2f} löst adaptive Θ-Aufgaben aus."
        ).format(thr=THETA_WIDTH_THRESHOLD),
        "empirical": (
            "Basierend auf {count} Elementen (ΔAIC_linear={delta_linear}, ΔAIC_power={delta_power})."
        ).format(
            count=len(signals),
            delta_linear=delta_aic_linear,
            delta_power=delta_aic_power,
        ),
        "poetic": (
            "Wenn Θ zu breit atmet, flackert die planetare Laterne – diese Liste markiert die Membranstellen, an denen"
            " neue Beobachtungen den Chor schärfen."
        ),
    }

    guidance: List[Dict[str, Any]] = []
    for signal in flagged_theta:
        guidance.append(
            {
                "element_id": signal.element_id,
                "label": signal.label,
                "priority": "high" if signal.theta_width_norm >= 0.3 else "medium",
                "analysis": [
                    {
                        "path": "analysis/planetary_tipping_elements_fit.py",
                        "action": "Extend logistic fit with time-varying Θ regression once new paleo/TIPMIP traces arrive.",
                    },
                    {
                        "path": "analysis/planetary_theta_drift_flag.py",
                        "action": "Re-run after each dataset ingestion to watch σ(β(R-Θ)) tighten.",
                    },
                ],
                "data": [
                    {
                        "path": "data/socio_ecology/",
                        "action": "Ingest paleo archives & TIPMIP ensemble slices for the element's stress accumulation R_acc.",
                    }
                ],
                "simulator": [
                    {
                        "path": "simulator/presets/planetary_tipping_field.json",
                        "action": "Schedule sweeps varying Θ(t) to test policy leverage on the membrane gap.",
                    }
                ],
                "docs": [
                    {
                        "path": "seed/socio_ecology/planetary_threshold_cartography.md",
                        "action": "Document new Θ trajectories and cross-link to Codex feedback once the gap narrows.",
                    }
                ],
            }
        )

    return {
        "generated_at": _utc_now(),
        "input_summary": str(DEFAULT_INPUT),
        "aggregate_theta": aggregate.get("theta"),
        "aggregate_beta": aggregate.get("beta"),
        "overview": overview,
        "signals": [signal.to_payload() for signal in signals],
        "implementation_guidance": guidance,
        "tri_layer": tri_layer,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Diagnose adaptive Θ drift gaps for planetary tipping elements",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Pfad zur aggregierten Planetary-Tipping JSON",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Zielpfad für die adaptive Θ Drift-Ausgabe",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = load_input(args.input)
    drift_payload = evaluate_drift(summary)
    drift_payload["input_summary"] = str(args.input)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(drift_payload, indent=2), encoding="utf-8")
    print(
        "σ(β(R-Θ)) gap audit geschrieben nach", args.output,
        "–", drift_payload["overview"]["theta_flags"], "von",
        drift_payload["overview"]["total_elements"], "Laternen benötigen adaptive Θ."
    )


if __name__ == "__main__":
    main()

