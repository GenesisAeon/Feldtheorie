"""Prefrontal working-memory gate fitting with tri-layer cadence.

Formal layer:
    Loads dopamine burst amplitudes and working-memory success rates treated as
    the logistic response sigma(beta(R-Theta)). Fits Theta and beta via the
    shared UTF regression pipeline, reports R^2, AIC, confidence intervals, and
    evaluates both linear and power-law smooth nulls. Documents the impedance
    motif zeta(R) = 1.35 - 0.38 * sigma consistent with RepoPlan membrane tables.

Empirical layer:
    Provides a CLI entry point so collaborators can regenerate parameter
    estimates, export JSON summaries, and link results back to dataset metadata
    in `data/cognition`. Outputs feed simulators, notebooks, and manuscripts
    throughout the UTF roadmap.

Metaphorical layer:
    Listens for the cognitive dawn. As dopamine pulses raise R toward Theta,
    the membrane slackens, loops stabilise, and sustained rehearsal ignites.
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
    """Read dopamine burst amplitudes and success probabilities from CSV."""

    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        R_values: List[float] = []
        sigma_values: List[float] = []
        for row in reader:
            R_values.append(float(row["R"]))
            sigma_values.append(float(row["sigma"]))
    return {"R": R_values, "sigma": sigma_values}


def impedance_profile(R: Iterable[float], theta: float, beta: float) -> Dict[str, float]:
    """Compute a cognitive impedance sketch tied to logistic resonance."""

    samples = []
    for value in R:
        sigma = float(logistic_response(value, theta, beta))
        zeta = 1.35 - 0.38 * sigma
        samples.append({"R": value, "sigma": sigma, "zeta": zeta})
    mean_zeta = sum(item["zeta"] for item in samples) / len(samples)
    variance = sum((item["zeta"] - mean_zeta) ** 2 for item in samples) / len(samples)
    return {
        "definition": "zeta(R) = 1.35 - 0.38 * sigma(beta(R-Theta))",
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
        "control_parameter": "normalised phasic dopamine burst amplitude",
        "order_parameter": "probability of correct N-back recall",
        "measurements": [
            {"R": R, "sigma": sigma, "logistic_fit": pred}
            for R, sigma, pred in zip(observations["R"], observations["sigma"], logistic_predictions)
        ],
    }
    summary["impedance"] = zeta_info
    summary["tri_layer"] = {
        "formal": "Logit-domain regression with dual smooth null comparisons (linear, power-law).",
        "empirical": (
            "Synthetic cognitive-control checkpoints aligned with RepoPlan membrane parameters; JSON export for cross-links."
        ),
        "metaphorical": (
            "Tracks the prefrontal chorus as dopamine lifts R past Theta and rehearsal dawns."
        ),
    }
    summary["ethics"] = {
        "notes": "Synthetic reconstruction inspired by cognitive-control literature; no human-identifiable data.",
        "references": [
            "O'Reilly & Frank working-memory gating theory",
            "RepoPlan 2.0 cognition membrane brief",
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    return summary


def parse_args() -> argparse.Namespace:
    """Configure CLI arguments for regenerating the working-memory gate fit."""

    parser = argparse.ArgumentParser(
        description="Fit working-memory logistic thresholds with falsification checks.",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/cognition/working_memory_gate.csv"),
        help="Path to the working-memory CSV (columns: R, sigma).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis/results/working_memory_gate.json"),
        help="Destination for the JSON summary containing threshold diagnostics.",
    )
    return parser.parse_args()


def main() -> None:
    """Execute the UTF working-memory workflow and report resonance summary."""

    args = parse_args()
    summary = build_summary(args.data, args.output)
    print(json.dumps(summary["falsification"], indent=2))


if __name__ == "__main__":
    main()
