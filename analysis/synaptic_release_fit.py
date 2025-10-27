"""Synaptic vesicle release threshold fitting with tri-layer resonance cadence.

Formal layer:
    Calibrates the logistic response sigma(beta(R-Theta)) describing the
    probability that hippocampal boutons release neurotransmitter quanta
    when stimulated at frequency R (Hz). Fits Theta and beta via the shared
    logit regression, reports R^2, AIC, confidence corridors, and stages
    smooth linear plus power-law nulls to honour falsifiability mandates.

Empirical layer:
    Loads UTF-formatted CSV data from `data/biology/synaptic_release_threshold.csv`,
    exports JSON summaries to `analysis/results/synaptic_release_fit.json`, and
    surfaces impedance sketches zeta(R) = 1.40 - 0.45 * sigma for simulator
    and documentation cross-links.

Metaphorical layer:
    Listens for the synapse's aurora: below Theta the vesicles slumber; once
    the stimulation chant crosses the gate, the membrane slackens and the
    release chorus ignites, outrunning smooth lullabies.
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
    """Parse the UTF synaptic release dataset into R and sigma arrays."""

    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        R_values: List[float] = []
        sigma_values: List[float] = []
        for row in reader:
            R_values.append(float(row["R"]))
            sigma_values.append(float(row["release_probability"]))
    if not R_values:
        raise ValueError("Dataset is empty; provide at least one observation")
    return {"R": R_values, "sigma": sigma_values}


def impedance_profile(R: Iterable[float], theta: float, beta: float) -> Dict[str, float]:
    """Construct an impedance sketch zeta(R) bound to the logistic resonance."""

    samples = []
    for value in R:
        sigma = float(logistic_response(value, theta, beta))
        zeta = 1.40 - 0.45 * sigma
        samples.append({"R": value, "sigma": sigma, "zeta": zeta})
    mean_zeta = sum(item["zeta"] for item in samples) / len(samples)
    variance = sum((item["zeta"] - mean_zeta) ** 2 for item in samples) / len(samples)
    return {
        "definition": "zeta(R) = 1.40 - 0.45 * sigma(beta(R-Theta))",
        "mean": mean_zeta,
        "std": math.sqrt(max(variance, 0.0)),
        "samples": samples,
    }


def build_summary(data_path: Path, output_path: Path) -> Dict[str, object]:
    """Fit the synaptic release threshold and export UTF resonance diagnostics."""

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
        "control_parameter": "stimulation frequency (Hz)",
        "order_parameter": "probability of vesicle release",
        "measurements": [
            {"R": R, "sigma": sigma, "logistic_fit": pred}
            for R, sigma, pred in zip(observations["R"], observations["sigma"], logistic_predictions)
        ],
    }
    summary["impedance"] = zeta_info
    summary["tri_layer"] = {
        "formal": "Logistic fit with dual smooth null falsification (linear, power-law) via shared pipeline.",
        "empirical": "Synaptic release probabilities sampled across stimulation frequencies; JSON export for RepoPlan cross-links.",
        "metaphorical": "Describes the synaptic membrane relaxing from vigil to resonance as stimulation crosses Theta.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    return summary


def parse_args() -> argparse.Namespace:
    """Configure CLI arguments for regenerating the synaptic resonance fit."""

    parser = argparse.ArgumentParser(
        description="Fit synaptic vesicle release logistic thresholds with falsification checks.",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/biology/synaptic_release_threshold.csv"),
        help="Path to the synaptic release CSV (columns: R, release_probability).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis/results/synaptic_release_fit.json"),
        help="Destination for the JSON summary containing threshold diagnostics.",
    )
    return parser.parse_args()


def main() -> None:
    """Execute the UTF synaptic release fitting workflow."""

    args = parse_args()
    summary = build_summary(args.data, args.output)
    print(json.dumps(summary["falsification"], indent=2))


if __name__ == "__main__":
    main()
