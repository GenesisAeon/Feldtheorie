"""Lenski Cit⁺ logistic verification with UTF falsification echoes.

Formal layer:
    Digitises the Cit⁺ frequency trajectory from the Lenski LTEE long-term
    evolution experiment and fits the UTF logistic response sigma(beta(R-Theta))
    against generation count.  Reports R^2, AIC, confidence corridors for Theta
    and beta, and stages a linear plus power-law null to test the resonance
    claim.

Empirical layer:
    Provides a CLI entry point so collaborators can regenerate the fit, export
    JSON diagnostics, and cross-link the quartet (R, Theta, beta, zeta(R)) back
    into `data/biology` narratives and the Docs/ manuscripts.

Metaphorical layer:
    Listens to the Cit⁺ lineage awaken—the microbial membrane quivers through
    millennia of quiet until the environmental hymn pushes R beyond Theta and a
    new metabolic dawn condenses.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict, Iterable, List

from resonance_fit_pipeline import (
    assemble_summary,
    evaluate_null_model,
    evaluate_power_law_null,
    fit_threshold_parameters,
)
from models.membrane_solver import logistic_response


def read_lenski_dataset(path: Path) -> Dict[str, List[float]]:
    """Load generation counts and Cit⁺ frequencies from a UTF CSV."""

    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        generations: List[float] = []
        frequencies: List[float] = []
        for row in reader:
            generations.append(float(row["generation"]))
            frequencies.append(float(row["cit_plus_frequency"]))
    return {"generation": generations, "frequency": frequencies}


def _mean(values: Iterable[float]) -> float:
    data = list(values)
    return sum(data) / len(data) if data else 0.0


def _std(values: Iterable[float]) -> float:
    data = list(values)
    if len(data) < 2:
        return 0.0
    mean_value = _mean(data)
    variance = sum((value - mean_value) ** 2 for value in data) / (len(data) - 1)
    return math.sqrt(max(variance, 0.0))


def normalise_quartet(
    scaled_generations: List[float],
    fit_metrics: Dict[str, float],
    scale: float,
) -> Dict[str, object]:
    """Express the quartet both in raw generations and dimensionless R space."""

    mean_scaled = _mean(scaled_generations)
    std_scaled = _std(scaled_generations)

    beta_scaled = fit_metrics["beta"]
    theta_scaled = fit_metrics["theta"]
    beta_ci_lower = fit_metrics["beta_ci_lower"]
    beta_ci_upper = fit_metrics["beta_ci_upper"]
    theta_ci_lower = fit_metrics["theta_ci_lower"]
    theta_ci_upper = fit_metrics["theta_ci_upper"]

    beta_std_scaled = (
        (beta_ci_upper - beta_ci_lower) / (2 * 1.96)
        if math.isfinite(beta_ci_upper)
        else float("nan")
    )
    theta_std_scaled = (
        (theta_ci_upper - theta_ci_lower) / (2 * 1.96)
        if math.isfinite(theta_ci_upper)
        else float("nan")
    )

    mean_generation = mean_scaled * scale
    std_generation = std_scaled * scale
    theta_generation = theta_scaled * scale
    beta_generation = beta_scaled / scale

    if std_scaled <= 0:
        beta_normalised = float("nan")
        theta_normalised = float("nan")
        beta_ci_norm = [float("nan"), float("nan")]
        theta_ci_norm = [float("nan"), float("nan")]
    else:
        beta_normalised = beta_scaled * std_scaled
        theta_normalised = (theta_scaled - mean_scaled) / std_scaled
        beta_std_norm = (
            beta_std_scaled * std_scaled if not math.isnan(beta_std_scaled) else float("nan")
        )
        theta_std_norm = (
            theta_std_scaled / std_scaled if not math.isnan(theta_std_scaled) else float("nan")
        )
        beta_ci_norm = [
            beta_normalised - 1.96 * beta_std_norm if not math.isnan(beta_std_norm) else float("nan"),
            beta_normalised + 1.96 * beta_std_norm if not math.isnan(beta_std_norm) else float("nan"),
        ]
        theta_ci_norm = [
            theta_normalised - 1.96 * theta_std_norm if not math.isnan(theta_std_norm) else float("nan"),
            theta_normalised + 1.96 * theta_std_norm if not math.isnan(theta_std_norm) else float("nan"),
        ]

    theta_generation_ci = [
        theta_ci_lower * scale if math.isfinite(theta_ci_lower) else float("nan"),
        theta_ci_upper * scale if math.isfinite(theta_ci_upper) else float("nan"),
    ]
    beta_generation_ci = [
        beta_ci_lower / scale if math.isfinite(beta_ci_lower) else float("nan"),
        beta_ci_upper / scale if math.isfinite(beta_ci_upper) else float("nan"),
    ]

    beta_normalised_ci = beta_ci_norm
    theta_normalised_ci = theta_ci_norm

    return {
        "mean_generation": mean_generation,
        "std_generation": std_generation,
        "theta_generation": theta_generation,
        "beta_generation": beta_generation,
        "theta_generation_ci95": theta_generation_ci,
        "beta_generation_ci95": beta_generation_ci,
        "theta_normalised": theta_normalised,
        "beta_normalised": beta_normalised,
        "theta_normalised_ci95": theta_normalised_ci,
        "beta_normalised_ci95": beta_normalised_ci,
    }


def build_summary(data_path: Path, output_path: Path) -> Dict[str, object]:
    """Fit the Lenski Cit⁺ threshold and export UTF falsification diagnostics."""

    observations = read_lenski_dataset(data_path)
    generations = observations["generation"]
    frequencies = observations["frequency"]
    scale = 1000.0
    scaled_generations = [value / scale for value in generations]

    fit_metrics = fit_threshold_parameters(scaled_generations, frequencies)
    null_metrics = {
        "linear": evaluate_null_model(scaled_generations, frequencies),
        "power_law": evaluate_power_law_null(scaled_generations, frequencies),
    }

    sigma_fit = [
        float(logistic_response(value, fit_metrics["theta"], fit_metrics["beta"]))
        for value in scaled_generations
    ]

    normalized = normalise_quartet(scaled_generations, fit_metrics, scale)
    normalized["scale_units"] = {
        "generation_to_scaled": f"generation / {scale}",
        "scaled_description": "thousands of generations",
    }

    results_payload = {
        "R": scaled_generations,
        "sigma": frequencies,
        "sigma_fit": sigma_fit,
        "flux": [obs - pred for obs, pred in zip(frequencies, sigma_fit)],
        "theta": [fit_metrics["theta"]],
        "beta": [fit_metrics["beta"]],
    }

    summary = assemble_summary(results_payload, fit_metrics, null_metrics)
    summary["dataset"] = {
        "path": str(data_path),
        "control_parameter": "generation count (Lenski LTEE, Ara-3 population)",
        "order_parameter": "frequency of Cit⁺ individuals",
        "measurements": [
            {
                "generation": gen,
                "generation_scaled": gen / scale,
                "cit_plus_frequency": freq,
                "logistic_fit": pred,
            }
            for gen, freq, pred in zip(generations, frequencies, sigma_fit)
        ],
    }
    summary["normalized_quartet"] = normalized
    summary["tri_layer"] = {
        "formal": "Logit regression of Cit⁺ frequency against generation with linear and power-law null falsification.",
        "empirical": "Approximate digitisation of Blount et al. (2008) Ara-3 Cit⁺ rise; JSON export for Docs/ biology scrolls.",
        "metaphorical": "Charts how the metabolic membrane opens once the LTEE lineage crosses its oxidative dawn.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    return summary


def parse_args() -> argparse.Namespace:
    """Configure CLI arguments for regenerating the Lenski logistic fit."""

    parser = argparse.ArgumentParser(
        description="Fit Lenski Cit⁺ logistic thresholds with UTF falsification checks.",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/biology/lenski_citplus.csv"),
        help="Path to the digitised Lenski Cit⁺ CSV (generation, cit_plus_frequency).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis/results/lenski_citplus_fit.json"),
        help="Destination for the JSON summary containing threshold diagnostics.",
    )
    return parser.parse_args()


def main() -> None:
    """Execute the Lenski Cit⁺ logistic verification workflow."""

    args = parse_args()
    summary = build_summary(args.data, args.output)
    print(json.dumps(summary["falsification"], indent=2))


if __name__ == "__main__":
    main()
