"""Urban heat canopy resilience threshold fitting with tri-layer cadence.

Formal layer:
    Treats shaded surface fraction R as the control parameter steering the
    logistic response sigma(beta(R-Theta)) for safe-night probabilities.
    Estimates Theta and beta through the UTF regression suite while reporting
    R^2, AIC, confidence corridors, and dual smooth null comparisons.
    Encodes an impedance sketch zeta(R) = 1.45 - 0.5 * sigma mirroring
    governance slackening when canopy restoration advances.

Empirical layer:
    Offers a CLI entry point that ingests `data/socio_ecology/urban_heat_canopy.csv`,
    regenerates fit diagnostics, exports JSON summaries, and links results back to
    RepoPlan cross-references in `docs/` and simulator briefs.

Metaphorical layer:
    Listens for the city's dawn chorus: when R crosses Theta the membrane loosens,
    night air cools, and the aurora of restful sleep returns to heat-burdened neighbourhoods.
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
    """Read canopy coverage R and safe night fraction sigma observations."""

    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        R_values: List[float] = []
        sigma_values: List[float] = []
        for row in reader:
            R_values.append(float(row["R"]))
            sigma_values.append(float(row["safe_night_fraction"]))
    return {"R": R_values, "sigma": sigma_values}


def impedance_profile(R: Iterable[float], theta: float, beta: float) -> Dict[str, float]:
    """Compute an urban heat impedance sketch tied to logistic resonance."""

    samples = []
    for value in R:
        sigma = float(logistic_response(value, theta, beta))
        zeta = 1.45 - 0.5 * sigma
        samples.append({"R": value, "sigma": sigma, "zeta": zeta})
    mean_zeta = sum(item["zeta"] for item in samples) / len(samples)
    variance = sum((item["zeta"] - mean_zeta) ** 2 for item in samples) / len(samples)
    return {
        "definition": "zeta(R) = 1.45 - 0.5 * sigma(beta(R-Theta))",
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
        "control_parameter": "fractional tree canopy coverage in heat-vulnerable districts",
        "order_parameter": "share of summer nights below heat-stress threshold",
        "measurements": [
            {"R": R, "sigma": sigma, "logistic_fit": pred}
            for R, sigma, pred in zip(observations["R"], observations["sigma"], logistic_predictions)
        ],
    }
    summary["impedance"] = zeta_info
    summary["tri_layer"] = {
        "formal": "Logit-domain regression with dual smooth null comparisons (linear, power-law).",
        "empirical": (
            "Synthetic blend of canopy audits and night-time heat index surveys; JSON export tethers RepoPlan cross-links."
        ),
        "metaphorical": (
            "Tracks how urban membranes slacken when tree canopies bloom, letting neighbourhoods breathe before dawn."
        ),
    }
    summary["ethics"] = {
        "notes": (
            "Highlights environmental justice commitments: prioritising cooling investments for frontline communities"
            " and co-designing data collection with local stewardship groups."
        ),
        "references": [
            "RepoPlan 2.0 socio-ecological membrane brief",
            "Urban heat resilience task force memoranda",
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    return summary


def parse_args() -> argparse.Namespace:
    """Configure CLI arguments for regenerating the canopy resilience fit."""

    parser = argparse.ArgumentParser(
        description="Fit urban heat canopy logistic thresholds with falsification checks.",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/socio_ecology/urban_heat_canopy.csv"),
        help="Path to the canopy vs. safe-night CSV (columns: R, safe_night_fraction).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis/results/urban_heat_canopy.json"),
        help="Destination for the JSON summary containing threshold diagnostics.",
    )
    return parser.parse_args()


def main() -> None:
    """Execute the UTF canopy resilience workflow and report resonance summary."""

    args = parse_args()
    summary = build_summary(args.data, args.output)
    print(json.dumps(summary["falsification"], indent=2))


if __name__ == "__main__":
    main()
