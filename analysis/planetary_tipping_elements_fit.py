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
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional

DATA_PATH = Path("data/socio_ecology/planetary_tipping_elements.json")
META_PATH = Path("data/socio_ecology/planetary_tipping_elements.metadata.json")
OUTPUT_PATH = Path("analysis/results/planetary_tipping_elements.json")


HYPOTHESIS_NOTES: List[Dict[str, Any]] = [
    {
        "id": "beta_universality",
        "title": "Sigmoid-Steigung konsistent mit β≈4.2",
        "description": (
            "Gemini skizzierte im Klimadiskurs drei kohärente Tests. Der erste prüft, ob die "
            "Zeitreihen einzelner Kippelemente (z. B. RAPID-AMOC, Grönland-Massenbilanz) die "
            "sigmoidale Übergangsform mit β≈4.2 besser stützen als lineare oder stochastische "
            "Alternativen."
        ),
        "evidence": {
            "beta_mean": None,  # gefüllt in compile_summary (μ_β)
            "beta_ci_width_mean": None,  # mittlere CI-Breite für β
            "delta_aic_linear": None,
            "delta_aic_power_law": None,
            "n_elements": None,
        },
        "status": "in_progress",
        "next_steps": [
            "BIC/AIC-Vergleich für AMOC-RAPID-Zeitreihen durchführen (Hypothese 1, Diskurs Klimamodul).",
            "TIPMIP-Multi-Model-Daten gegen das aktuelle β-Band testen.",
        ],
        "references": [
            "Docs/Kipppunkte der Teilkomponenten im Klimasystem.pdf",
            "Docs/Tiefgehende Recherche (DeepResearch) zu Aspekten der Teilfeld-Kartierung.pdf",
            "Docs/Diskurs Klimamodul.txt",
        ],
    },
    {
        "id": "adaptive_threshold",
        "title": "Dynamische Θ-Trigger vs. Stressakkumulation",
        "description": (
            "Die zweite Hypothese verlangt, dass Θ nicht statisch bleibt, sondern durch akkumulierten "
            "Stress R_acc moduliert wird. Wir halten fest, welche Elemente bereits adaptive Schwellen "
            "aufweisen und wo historische Daten noch eine feste Grenze suggerieren."
        ),
        "evidence": {
            "theta_trend_observed": False,
            "stress_proxy": "aggregierter Klimastress",
        },
        "status": "queued",
        "next_steps": [
            "Paleo- und Beobachtungsarchive für AMOC, Grönland und Permafrost auf zeitvariable Θ-Fenster auswerten.",
            "Vergleich mit R_acc-Szenarien aus Docs/'Adaptive Schwellenwerte in komplexen Systemen.pdf'.",
        ],
        "references": [
            "Docs/Adaptive Schwellenwerte in komplexen Systemen.pdf",
            "Docs/Tiefgehende Recherche (DeepResearch) zu Aspekten der Teilfeld-Kartierung.pdf",
            "Docs/Diskurs Klimamodul.txt",
        ],
    },
    {
        "id": "coupled_resonance",
        "title": "Gekoppelte Resonanz & Systemic Catalysis",
        "description": (
            "Hypothese drei adressiert die g_ij-Kopplungen: Kippvorgänge sollen transversal wirken, "
            "sodass minimale Impulse in Feld i nicht-linear auf Feld j zurückwirken."
        ),
        "evidence": {
            "simulator_preset": "simulator/presets/planetary_tipping_field.json",
            "coupling_matrix_documented": True,
        },
        "status": "prototype",
        "next_steps": [
            "Simulator-Sweeps mit variierten g_ij konfigurieren und ΔΘ_global protokollieren.",
            "Numerische ODE-Kopplung (Gemini Agenda Phase 3) gegen TIPMIP-Sensitivitäten prüfen.",
        ],
        "references": [
            "Docs/Diskurs Klimamodul.txt",
            "Docs/RepoPlan Projekt-Impulse_ Simulation, Theorie, Falsifizierung.pdf",
            "docs/socio_ecology/planetary_threshold_cartography.md",
        ],
    },
]


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


def _format_formal_beta_statement(beta_values: List[float], beta_mean: Optional[float]) -> str:
    """Generate the formal-layer beta summary with graceful fallbacks."""

    if not beta_values or beta_mean is None:
        return "σ(β(R-Θ)) koppelt lokale Felder via g_ij; neue Messungen müssen das β-Band noch füllen."

    beta_min = min(beta_values)
    beta_max = max(beta_values)
    return "σ(β(R-Θ)) koppelt lokale Felder via g_ij; β liegt zwischen {:.2f} und {:.2f} (μ≈{:.2f}).".format(
        beta_min,
        beta_max,
        beta_mean,
    )


def _utc_now_isoformat() -> str:
    """Return the current UTC timestamp in ISO-8601 with ``Z`` suffix."""

    timestamp = datetime.now(timezone.utc).replace(microsecond=0)
    return timestamp.isoformat().replace("+00:00", "Z")


def compile_summary(
    elements: List[LogisticElement],
    aggregate: AggregateLogistic,
    *,
    generated_at: Optional[str] = None,
) -> Dict[str, Any]:
    beta_values = [e.beta for e in elements if getattr(e, "beta", None) is not None]
    band_widths = [
        e.steepness_band for e in elements if getattr(e, "beta_ci95", None) is not None
    ]
    theta_values = [e.theta for e in elements if getattr(e, "theta", None) is not None]

    beta_mean: Optional[float]
    if beta_values:
        beta_mean = float(mean(beta_values))
    else:
        beta_mean = None

    beta_ci_width_mean: Optional[float]
    if band_widths:
        beta_ci_width_mean = float(mean(band_widths))
    else:
        beta_ci_width_mean = None

    if generated_at is None:
        generated_at = _utc_now_isoformat()

    hypotheses: List[Dict[str, Any]] = []
    for base in HYPOTHESIS_NOTES:
        note = deepcopy(base)
        if note["id"] == "beta_universality":
            note["evidence"]["beta_mean"] = beta_mean
            note["evidence"]["beta_ci_width_mean"] = beta_ci_width_mean
            note["evidence"]["n_elements"] = len(beta_values)
            note["evidence"]["delta_aic_linear"] = aggregate.null_models["linear"]["delta_aic"]
            note["evidence"]["delta_aic_power_law"] = aggregate.null_models["power_law"]["delta_aic"]

            delta_linear = aggregate.null_models["linear"]["delta_aic"]
            delta_power = aggregate.null_models["power_law"]["delta_aic"]
            aic_strong = delta_linear is not None and delta_power is not None and delta_linear > 30 and delta_power > 30
            beta_in_band = beta_mean is not None and 3.6 <= beta_mean <= 4.6
            enough_elements = len(beta_values) >= 3

            if aic_strong and beta_in_band and enough_elements:
                note["status"] = "supported"
            elif aic_strong and enough_elements and beta_mean is not None:
                note["status"] = "contradicted"
            else:
                note["status"] = "inconclusive"
        elif note["id"] == "adaptive_threshold":
            note["evidence"]["theta_trend_observed"] = any(
                abs(e.theta_ci95[1] - e.theta_ci95[0]) > 0.3 * e.theta for e in elements
            )
        elif note["id"] == "coupled_resonance":
            note["evidence"]["beta_range"] = [min(beta_values), max(beta_values)]
            note["evidence"]["theta_span"] = [min(theta_values), max(theta_values)]
        hypotheses.append(note)

    payload: Dict[str, Any] = {
        "generated_at": generated_at,
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
            "beta_mean": beta_mean,
            "beta_ci_width_mean": beta_ci_width_mean,
            "beta_min": min(beta_values) if beta_values else None,
            "beta_max": max(beta_values) if beta_values else None,
            "theta_min": min(theta_values) if theta_values else None,
            "theta_max": max(theta_values) if theta_values else None
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
        "hypotheses": hypotheses,
        "falsification": {
            "logistic_beats_linear": aggregate.null_models["linear"]["delta_aic"] > 0,
            "logistic_beats_power_law": aggregate.null_models["power_law"]["delta_aic"] > 0,
            "notes": "ΔAIC und ΔR² stammen aus DeepResearch-Synthesen; künftige TIPMIP-Datenläufe sollen diese Werte replizieren."
        },
        "tri_layer": {
            "formal": _format_formal_beta_statement(beta_values, beta_mean),
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
