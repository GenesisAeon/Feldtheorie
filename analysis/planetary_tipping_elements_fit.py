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
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional, Sequence, Tuple

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


@dataclass
class BetaStatistics:
    """Bundle β statistics so the mean and CI width never blur."""

    count: int
    mean: Optional[float]
    std: Optional[float]
    sem: Optional[float]
    sem_ci95: Optional[Tuple[float, float]]
    ci_width_mean: Optional[float]
    ci_width_std: Optional[float]
    canonical: Optional[float]


def _mean(values: Sequence[float]) -> Optional[float]:
    return float(mean(values)) if values else None


def _sample_std(values: Sequence[float], centre: float) -> Optional[float]:
    if len(values) < 2:
        return None
    variance = sum((value - centre) ** 2 for value in values) / (len(values) - 1)
    return math.sqrt(max(variance, 0.0))


def compute_beta_statistics(
    elements: Sequence[LogisticElement],
    *,
    aggregate_beta: Optional[float] = None,
) -> BetaStatistics:
    """Return μβ, dispersion, and CI width diagnostics."""

    beta_values = [float(e.beta) for e in elements if getattr(e, "beta", None) is not None]
    width_values = [
        float(e.steepness_band)
        for e in elements
        if getattr(e, "beta_ci95", None) is not None
    ]

    beta_mean = _mean(beta_values)
    beta_std = None
    if beta_mean is not None:
        beta_std = _sample_std(beta_values, beta_mean)
    if beta_std is not None and beta_mean is not None and beta_values:
        beta_sem = beta_std / math.sqrt(len(beta_values))
        beta_sem_ci95 = (
            beta_mean - 1.96 * beta_sem,
            beta_mean + 1.96 * beta_sem,
        )
    else:
        beta_sem = None
        beta_sem_ci95 = None

    ci_width_mean = _mean(width_values)
    ci_width_std = (
        _sample_std(width_values, ci_width_mean) if ci_width_mean is not None else None
    )

    return BetaStatistics(
        count=len(beta_values),
        mean=beta_mean,
        std=beta_std,
        sem=beta_sem,
        sem_ci95=beta_sem_ci95,
        ci_width_mean=ci_width_mean,
        ci_width_std=ci_width_std,
        canonical=float(aggregate_beta) if aggregate_beta is not None else None,
    )


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


def _format_formal_beta_statement(
    beta_values: List[float],
    beta_mean: Optional[float],
    beta_canonical: Optional[float],
) -> str:
    """Generate the formal-layer beta summary with graceful fallbacks."""

    if beta_values and beta_mean is not None:
        beta_min = min(beta_values)
        beta_max = max(beta_values)
        return "σ(β(R-Θ)) koppelt lokale Felder via g_ij; β liegt zwischen {:.2f} und {:.2f} (μ≈{:.2f}).".format(
            beta_min,
            beta_max,
            beta_mean,
        )

    if beta_canonical is not None:
        return (
            "σ(β(R-Θ)) koppelt lokale Felder via g_ij; der kanonische Fit bestätigt β≈{:.2f}."
        ).format(beta_canonical)

    return "σ(β(R-Θ)) koppelt lokale Felder via g_ij; neue Messungen müssen das β-Band noch füllen."


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
    stats = compute_beta_statistics(elements, aggregate_beta=aggregate.beta)
    theta_values = [e.theta for e in elements if getattr(e, "theta", None) is not None]
    beta_canonical = stats.canonical if stats.canonical is not None else aggregate.beta
    beta_mean_report = stats.mean if stats.mean is not None else beta_canonical

    if generated_at is None:
        generated_at = _utc_now_isoformat()

    hypotheses: List[Dict[str, Any]] = []
    for base in HYPOTHESIS_NOTES:
        note = deepcopy(base)
        if note["id"] == "beta_universality":
            note["evidence"]["beta_mean"] = beta_mean_report
            note["evidence"]["beta_mean_observed"] = stats.mean
            note["evidence"]["beta_std"] = stats.std
            note["evidence"]["beta_sem"] = stats.sem
            note["evidence"]["beta_sem_ci95"] = (
                list(stats.sem_ci95) if stats.sem_ci95 is not None else None
            )
            note["evidence"]["beta_ci_width_mean"] = stats.ci_width_mean
            note["evidence"]["beta_ci_width_std"] = stats.ci_width_std
            note["evidence"]["n_elements"] = stats.count
            note["evidence"]["delta_aic_linear"] = aggregate.null_models["linear"]["delta_aic"]
            note["evidence"]["delta_aic_power_law"] = aggregate.null_models["power_law"]["delta_aic"]
            note["evidence"]["beta_canonical"] = beta_canonical

            delta_linear = aggregate.null_models["linear"]["delta_aic"]
            delta_power = aggregate.null_models["power_law"]["delta_aic"]
            aic_strong = (
                delta_linear is not None
                and delta_power is not None
                and delta_linear > 30
                and delta_power > 30
            )
            beta_in_band_value = (
                beta_mean_report if beta_mean_report is not None else beta_canonical
            )
            beta_in_band = (
                beta_in_band_value is not None and 3.6 <= beta_in_band_value <= 4.6
            )
            enough_elements = stats.count >= 3

            if aic_strong and beta_in_band and enough_elements:
                note["status"] = "supported"
            elif aic_strong and enough_elements and beta_in_band_value is not None:
                note["status"] = "contradicted"
            else:
                note["status"] = "inconclusive"
        elif note["id"] == "adaptive_threshold":
            note["evidence"]["theta_trend_observed"] = any(
                abs(e.theta_ci95[1] - e.theta_ci95[0]) > 0.3 * e.theta for e in elements
            )
        elif note["id"] == "coupled_resonance":
            if beta_values:
                beta_range = [min(beta_values), max(beta_values)]
            elif stats.canonical is not None:
                beta_range = [stats.canonical, stats.canonical]
            else:
                beta_range = None
            note["evidence"]["beta_range"] = beta_range
            if theta_values:
                theta_span = [min(theta_values), max(theta_values)]
            else:
                theta_span = None
            note["evidence"]["theta_span"] = theta_span
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
            "beta_mean": beta_mean_report,
            "beta_mean_observed": stats.mean,
            "beta_canonical": beta_canonical,
            "beta_std": stats.std,
            "beta_sem": stats.sem,
            "beta_sem_ci95": list(stats.sem_ci95) if stats.sem_ci95 is not None else None,
            "beta_ci_width_mean": stats.ci_width_mean,
            "beta_ci_width_std": stats.ci_width_std,
            "n_elements": stats.count,
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
            "formal": _format_formal_beta_statement(beta_values, stats.mean, beta_canonical),
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
