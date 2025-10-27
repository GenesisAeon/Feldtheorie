"""Amazon moisture resilience threshold fitting with tri-layer cadence.

Formal layer:
    Loads canopy fraction trajectories and treats moisture retention as the
    logistic response sigma(beta(R-Theta)). Fits Theta and beta via the shared
    logit regression, reports R^2, AIC, confidence intervals, and evaluates both
    linear and power-law smooth nulls. Documents the governance impedance
    profile zeta(R) = 1.8 - 0.6 * sigma to align with RepoPlan membrane tables.

Empirical layer:
    Provides a CLI entry point so collaborators can regenerate parameter
    estimates, export JSON summaries, and link results back to dataset metadata
    in `data/socio_ecology`. Outputs feed simulators, notebooks, and manuscripts
    throughout the UTF roadmap.

Metaphorical layer:
    Listens for the rainforest's dawn chorus. As canopy cover slips past Theta,
    the membrane stiffens and rainfall falters; when stewardship lifts R above
    the threshold, impedance softens and the moisture aurora rekindles.
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


def read_dataset(path: Path) -> Dict[str, List[float]]:
    """Read canopy fraction and moisture retention observations from CSV."""

    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        R_values: List[float] = []
        sigma_values: List[float] = []
        for row in reader:
            R_values.append(float(row["R"]))
            sigma_values.append(float(row["moisture_retention"]))
    return {"R": R_values, "sigma": sigma_values}


def impedance_profile(R: Iterable[float], theta: float, beta: float) -> Dict[str, float]:
    """Compute socio-ecological impedance sketch tied to logistic resonance."""

    samples = []
    for value in R:
        sigma = float(logistic_response(value, theta, beta))
        zeta = 1.8 - 0.6 * sigma
        samples.append({"R": value, "sigma": sigma, "zeta": zeta})
    mean_zeta = sum(item["zeta"] for item in samples) / len(samples)
    variance = sum((item["zeta"] - mean_zeta) ** 2 for item in samples) / len(samples)
    return {
        "definition": "zeta(R) = 1.8 - 0.6 * sigma(beta(R-Theta))",
        "mean": mean_zeta,
        "std": math.sqrt(max(variance, 0.0)),
        "samples": samples,
    }


def build_summary(data_path: Path, output_path: Path) -> Dict[str, object]:
    """Load dataset, fit logistic and null models, and export UTF diagnostics."""

    observations = read_dataset(data_path)
    fit_metrics = fit_threshold_parameters(observations["R"], observations["sigma"])
    null_metrics = {
        "linear": evaluate_null_model(observations["R"], observations["sigma"]),
        "power_law": evaluate_power_law_null(observations["R"], observations["sigma"]),
    }

    logistic_predictions = [
        float(logistic_response(value, fit_metrics["theta"], fit_metrics["beta"]))
        for value in observations["R"]
    ]
    zeta_info = impedance_profile(observations["R"], fit_metrics["theta"], fit_metrics["beta"])

    results_payload = {
        "R": observations["R"],
        "sigma": observations["sigma"],
        "sigma_fit": logistic_predictions,
        "zeta": [item["zeta"] for item in zeta_info["samples"]],
        "flux": [
            obs_sigma - pred for obs_sigma, pred in zip(observations["sigma"], logistic_predictions)
        ],
        "theta": [fit_metrics["theta"]],
        "beta": [fit_metrics["beta"]],
    }

    summary = assemble_summary(results_payload, fit_metrics, null_metrics)

    summary["dataset"] = {
        "path": str(data_path),
        "control_parameter": "remaining rainforest canopy fraction",
        "order_parameter": "probability of convective moisture retention",
        "measurements": [
            {"R": R, "sigma": sigma, "logistic_fit": pred}
            for R, sigma, pred in zip(observations["R"], observations["sigma"], logistic_predictions)
        ],
    }
    summary["impedance"] = zeta_info
    summary["tri_layer"] = {
        "formal": "Logistic regression on logit domain with dual smooth null comparisons (linear, power-law).",
        "empirical": "Socio-ecological tipping dataset calibrated from climate-forest syntheses; JSON export for RepoPlan cross-links.",
        "metaphorical": "Frames stewardship as slackening the membrane so rainforest dawn choruses can rekindle moisture.",
    }
    summary["ethics"] = {
        "notes": "Synthesised from public climate assessments; emphasises Indigenous guardianship and equitable restoration policies.",
        "references": [
            "Lovejoy & Nobre tipping point communiqués",
            "RepoPlan 2.0 socio-ecological membrane brief",
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    return summary


def parse_args() -> argparse.Namespace:
    """Configure CLI arguments for regenerating the resilience fit."""

    parser = argparse.ArgumentParser(
        description="Fit Amazon moisture resilience logistic thresholds with falsification checks.",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/socio_ecology/amazon_resilience.csv"),
        help="Path to the canopy vs. moisture CSV (columns: R, moisture_retention).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis/results/amazon_resilience_fit.json"),
        help="Destination for the JSON summary containing threshold diagnostics.",
    )
    return parser.parse_args()


def main() -> None:
    """Execute the UTF resilience fitting workflow and report resonance summary."""

    args = parse_args()
    summary = build_summary(args.data, args.output)
    print(json.dumps(summary["falsification"], indent=2))


if __name__ == "__main__":
    main()
