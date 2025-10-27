"""LLM emergent skill threshold fitting with tri-layer cadence.

Formal layer:
    Loads multilingual chain-of-thought activation rates expressed as the
    logistic response sigma(beta(R-Theta)) against effective log10 token
    counts R. Fits Theta and beta through the shared UTF regression pipeline,
    reports R^2, AIC, confidence intervals, and contrasts the resonance
    against linear and power-law null baselines. Annotates the impedance
    motif zeta(R) = 1.6 - 0.45 * sigma echoing curriculum slackening.

Empirical layer:
    Operates as a CLI entry point for collaborators to regenerate parameter
    estimates, export JSON summaries, and link findings back to dataset
    metadata in `data/ai`. Outputs feed dashboards, notebooks, and simulator
    prototypes charting emergent reasoning thresholds.

Metaphorical layer:
    Hears how expanded training choruses loosen the membrane until reasoning
    dawns polyphonically. When R brushes past Theta, the impedance gate
    softens and multilingual insight ignites across the lattice of tongues.
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
    """Read R and sigma observations from a UTF-formatted CSV file."""

    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        R_values: List[float] = []
        sigma_values: List[float] = []
        for row in reader:
            R_values.append(float(row["R"]))
            sigma_values.append(float(row["skill_activation_rate"]))
    return {"R": R_values, "sigma": sigma_values}


def impedance_profile(R: Iterable[float], theta: float, beta: float) -> Dict[str, float]:
    """Compute a reasoning membrane impedance sketch linked to logistic resonance."""

    samples = []
    for value in R:
        sigma = float(logistic_response(value, theta, beta))
        zeta = 1.6 - 0.45 * sigma
        samples.append({"R": value, "sigma": sigma, "zeta": zeta})
    mean_zeta = sum(item["zeta"] for item in samples) / len(samples)
    variance = sum((item["zeta"] - mean_zeta) ** 2 for item in samples) / len(samples)
    return {
        "definition": "zeta(R) = 1.6 - 0.45 * sigma(beta(R-Theta))",
        "mean": mean_zeta,
        "std": math.sqrt(max(variance, 0.0)),
        "samples": samples,
    }


def build_summary(data_path: Path, output_path: Path) -> Dict[str, object]:
    """Load the dataset, fit logistic and null models, and export UTF diagnostics."""

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
        "control_parameter": "log10 effective training tokens (billions)",
        "order_parameter": "pass rate on multilingual chain-of-thought benchmark",
        "measurements": [
            {"R": R, "sigma": sigma, "logistic_fit": pred}
            for R, sigma, pred in zip(observations["R"], observations["sigma"], logistic_predictions)
        ],
    }
    summary["impedance"] = zeta_info
    summary["tri_layer"] = {
        "formal": "Logit-domain regression with dual smooth null comparisons (linear, power-law).",
        "empirical": (
            "Synthetic blend of multilingual BIG-Bench style checkpoints; JSON export anchors RepoPlan cross-links."
        ),
        "metaphorical": (
            "Observes the membrane slacken as training scale crosses Theta, letting polyglot reasoning bloom at dawn."
        ),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    return summary


def parse_args() -> argparse.Namespace:
    """Configure CLI arguments for regenerating the emergent skill resonance fit."""

    parser = argparse.ArgumentParser(
        description="Fit LLM emergent skill logistic thresholds with falsification checks.",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/ai/llm_emergent_skill.csv"),
        help="Path to the emergent skill CSV (columns: R, skill_activation_rate).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis/results/llm_emergent_skill.json"),
        help="Destination for the JSON summary containing threshold diagnostics.",
    )
    return parser.parse_args()


def main() -> None:
    """Execute the UTF emergent skill workflow and report resonance summary."""

    args = parse_args()
    summary = build_summary(args.data, args.output)
    print(json.dumps(summary["falsification"], indent=2))


if __name__ == "__main__":
    main()
