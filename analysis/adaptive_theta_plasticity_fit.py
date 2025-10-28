r"""Adaptive theta plasticity logistic fitting with tri-layer cadence.

Formal layer:
    Treats hippocampal replay probability as the logistic response
    \(\sigma(\beta(R-\Theta))\) of a neuromodulatory pressure index. Uses the
    shared UTF regression pipeline to recover $(\Theta, \beta)$, report $R^2$ and
    AIC, and benchmark against linear and power-law smooth nulls. Includes an
    impedance sketch $\zeta(R) = 1.12 - 0.25\,\sigma$ reflecting how
    thalamo-cortical gates relax as replay ignites.

Empirical layer:
    Provides a CLI for regenerating fits from
    `data/cognition/adaptive_theta_plasticity.csv`, exporting a structured JSON
    payload to `analysis/results/adaptive_theta_plasticity.json`. The summary
    references dataset metadata, null comparisons, and membrane diagnostics so
    `docs/`, `simulator/`, and cohort ledgers stay synchronised.

Metaphorical layer:
    Listens to the sleeping hippocampus: below $\Theta$ the replay choir is
    hushed by homeostatic pressure, but as $R$ crosses the threshold, the
    impedance slackens and a dawn of memory rehearsal sweeps through the field.
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
    """Load neuromodulatory pressure samples and replay probabilities."""

    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        R_values: List[float] = []
        sigma_values: List[float] = []
        for row in reader:
            R_values.append(float(row["R"]))
            sigma_values.append(float(row["sigma"]))
    if not R_values:
        raise ValueError(f"Dataset {path} is empty; provide at least one sample")
    return {"R": R_values, "sigma": sigma_values}


def impedance_profile(R: Iterable[float], theta: float, beta: float) -> Dict[str, float]:
    """Compute the adaptive impedance sketch tied to logistic resonance."""

    samples = []
    for value in R:
        sigma = float(logistic_response(value, theta, beta))
        zeta = 1.12 - 0.25 * sigma
        samples.append({"R": value, "sigma": sigma, "zeta": zeta})
    mean_zeta = sum(item["zeta"] for item in samples) / len(samples)
    variance = sum((item["zeta"] - mean_zeta) ** 2 for item in samples) / len(samples)
    return {
        "definition": "zeta(R) = 1.12 - 0.25 * sigma(beta(R-Theta))",
        "mean": mean_zeta,
        "std": math.sqrt(max(variance, 0.0)),
        "samples": samples,
    }


def build_summary(data_path: Path, output_path: Path) -> Dict[str, object]:
    """Fit logistic and null models, export UTF diagnostics, and persist JSON."""

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
            obs_sigma - pred
            for obs_sigma, pred in zip(observations["sigma"], logistic_predictions)
        ],
        "theta": [fit_metrics["theta"]],
        "beta": [fit_metrics["beta"]],
    }

    summary = assemble_summary(results_payload, fit_metrics, null_metrics)

    summary["dataset"] = {
        "path": str(data_path),
        "control_parameter": "normalised sleep-pressure index",
        "order_parameter": "probability of hippocampal replay ignition",
        "measurements": [
            {"R": R, "sigma": sigma, "logistic_fit": pred}
            for R, sigma, pred in zip(
                observations["R"], observations["sigma"], logistic_predictions
            )
        ],
    }
    summary["impedance"] = zeta_info
    summary["tri_layer"] = {
        "formal": "Logit-domain regression with linear and power-law falsification twins.",
        "empirical": (
            "Synthetic replay checkpoints aligned with RepoPlan cognition membranes; JSON export for cross-links."
        ),
        "metaphorical": (
            "Tracks how the sleeping hippocampal choir brightens once sleep pressure eases across Theta."
        ),
    }
    summary["ethics"] = {
        "notes": "Synthetic reconstruction inspired by sleep-dependent memory consolidation literature; no subject-identifiable data.",
        "references": [
            "Diekelmann & Born (2010) memory consolidation review",
            "RepoPlan 2.0 cognition membrane brief",
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    return summary


def parse_args() -> argparse.Namespace:
    """Configure CLI arguments for the adaptive theta plasticity workflow."""

    parser = argparse.ArgumentParser(
        description="Fit adaptive theta plasticity logistic thresholds with falsification checks.",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/cognition/adaptive_theta_plasticity.csv"),
        help="Path to the adaptive theta plasticity CSV (columns: R, sigma).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis/results/adaptive_theta_plasticity.json"),
        help="Destination for the JSON summary containing threshold diagnostics.",
    )
    return parser.parse_args()


def main() -> None:
    """Execute the adaptive theta plasticity pipeline and print falsification summary."""

    args = parse_args()
    summary = build_summary(args.data, args.output)
    print(json.dumps(summary["falsification"], indent=2))


if __name__ == "__main__":
    main()
