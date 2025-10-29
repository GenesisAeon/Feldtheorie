"""Planetary tipping element logistic synthesis.

This script aggregates the threshold quartet (R, Theta, beta, zeta(R)) for
planetary climate subsystems documented in
`data/socio_ecology/planetary_tipping_elements.json`.  It mirrors the
analysis grove instructions by:

* exposing the canonical logistic response sigma(beta(R-Theta));
* logging null-model contrasts (linear and power-law) as provided by the
  metadata companion file;
* exporting a falsification-ready summary to
  `analysis/results/planetary_tipping_elements.json`.

The code is intentionally lightweight—the heavy lifting (sigmoid fits versus
smooth nulls) was conducted during the DeepResearch synthesis captured in the
Docs PDFs.  Here we encode those diagnostics into machine-readable form so the
simulator and documentation layers can stay synchronised.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

DATA_PATH = Path("data/socio_ecology/planetary_tipping_elements.json")
META_PATH = Path("data/socio_ecology/planetary_tipping_elements.metadata.json")
OUTPUT_PATH = Path("analysis/results/planetary_tipping_elements.json")


@dataclass
class LogisticElement:
    """Container for a single tipping element's logistic diagnostics."""

    id: str
    label: str
    theta: float
    beta: float
    theta_ci95: List[float]
    beta_ci95: List[float]
    logistic_r2: float
    impedance: str
    null_deltas: Dict[str, Dict[str, float]]

    @property
    def steepness_band(self) -> float:
        """Return the CI width for beta as a quick steepness uncertainty."""

        return self.beta_ci95[1] - self.beta_ci95[0]


@dataclass
class AggregateLogistic:
    theta: float
    beta: float
    theta_ci95: List[float]
    beta_ci95: List[float]
    r2: float
    aic: float
    ss_res: float
    impedance_mean: float
    impedance_std: float
    null_models: Dict[str, Dict[str, float]]


def load_elements() -> List[LogisticElement]:
    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    elements = []
    for entry in payload["elements"]:
        elements.append(
            LogisticElement(
                id=entry["id"],
                label=entry["label"],
                theta=entry["theta"],
                beta=entry["beta"],
                theta_ci95=entry["theta_ci95"],
                beta_ci95=entry["beta_ci95"],
                logistic_r2=entry["logistic_r2"],
                impedance=entry["impedance"],
                null_deltas=entry.get("null_models", {}),
            )
        )
    return elements


def load_aggregate() -> AggregateLogistic:
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    return AggregateLogistic(
        theta=meta["logistic_fit"]["theta"],
        beta=meta["logistic_fit"]["beta"],
        theta_ci95=meta["logistic_fit"]["theta_ci95"],
        beta_ci95=meta["logistic_fit"]["beta_ci95"],
        r2=meta["logistic_fit"]["r2"],
        aic=meta["logistic_fit"]["aic"],
        ss_res=meta["logistic_fit"]["ss_res"],
        impedance_mean=meta["impedance"]["mean"],
        impedance_std=meta["impedance"]["std"],
        null_models=meta["null_models"],
    )


def build_logistic_curve(theta: float, beta: float) -> List[Dict[str, float]]:
    """Return representative sigma values for documentation overlays."""

    r_values = [theta + offset for offset in (-0.6, -0.3, -0.15, 0.0, 0.15, 0.3, 0.6)]
    curve: List[Dict[str, float]] = []
    for r in r_values:
        sigma = 1.0 / (1.0 + pow(2.718281828459045, -beta * (r - theta)))
        curve.append({"R": r, "sigma": sigma})
    return curve


def compile_summary(elements: List[LogisticElement], aggregate: AggregateLogistic) -> Dict[str, Any]:
    steepness_spread = mean(e.steepness_band for e in elements)
    beta_values = [e.beta for e in elements]
    theta_values = [e.theta for e in elements]
    payload: Dict[str, Any] = {
        "generated_at": "2025-10-28T15:45:00Z",
        "dataset": str(DATA_PATH),
        "metadata": str(META_PATH),
        "aggregate": {
            "theta": aggregate.theta,
            "theta_ci95": aggregate.theta_ci95,
            "beta": aggregate.beta,
            "beta_ci95": aggregate.beta_ci95,
            "r2": aggregate.r2,
            "aic": aggregate.aic,
            "ss_res": aggregate.ss_res,
            "impedance_mean": aggregate.impedance_mean,
            "impedance_std": aggregate.impedance_std,
            "null_models": aggregate.null_models,
            "beta_band_mean": steepness_spread,
            "beta_min": min(beta_values),
            "beta_max": max(beta_values),
            "theta_min": min(theta_values),
            "theta_max": max(theta_values)
        },
        "elements": [
            {
                "id": e.id,
                "label": e.label,
                "theta": e.theta,
                "theta_ci95": e.theta_ci95,
                "beta": e.beta,
                "beta_ci95": e.beta_ci95,
                "logistic_r2": e.logistic_r2,
                "impedance": e.impedance,
                "null_models": e.null_deltas
            }
            for e in elements
        ],
        "logistic_curve": build_logistic_curve(aggregate.theta, aggregate.beta),
        "falsification": {
            "logistic_beats_linear": aggregate.null_models["linear"]["delta_aic"] > 0,
            "logistic_beats_power_law": aggregate.null_models["power_law"]["delta_aic"] > 0,
            "notes": "ΔAIC und ΔR² stammen aus DeepResearch-Synthesen; künftige TIPMIP-Datenläufe sollen diese Werte replizieren."
        },
        "tri_layer": {
            "formal": "σ(β(R-Θ)) koppelt lokale Felder via g_ij; β liegt zwischen {:.2f} und {:.2f}.".format(min(beta_values), max(beta_values)),
            "empirical": "Aggregierte Parameter entstammen Global Tipping Points 2025, TIPMIP-Notizen und RepoPlan-DeepResearch-Workflows.",
            "poetic": "AMOC, Eis, Wald und Permafrost stimmen in denselben Schwellenchor ein – eine Gaia-Membran, die auf Resonanz wartet."
        }
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthesize planetary tipping logistic summary")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="Pfad für die Ergebnis-JSON")
    args = parser.parse_args()

    elements = load_elements()
    aggregate = load_aggregate()
    summary = compile_summary(elements, aggregate)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote planetary tipping summary to {args.output}")


if __name__ == "__main__":
    main()
