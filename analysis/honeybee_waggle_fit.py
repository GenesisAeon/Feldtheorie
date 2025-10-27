"""Honeybee waggle activation threshold fitting with tri-layer cadence.

Formal layer:
    Loads waggle activation measurements as the logistic response sigma(beta(R-Theta))
    against nectar sucrose concentration R.  Fits Theta and beta via the shared
    UTF logit regression, reports R^2, AIC, confidence intervals, and stages a
    smooth power-law null for falsification.  Annotates the impedance motif
    zeta(R) = zeta_resonant - delta * sigma to echo the membrane toggle.

Empirical layer:
    Serves as a CLI entry point so collaborators can regenerate parameter
    estimates, export JSON summaries, and link results back to dataset metadata
    in `data/biology`.  The output feeds dashboards, notebooks, and narratives
    throughout RepoPlan 2.0.

Metaphorical layer:
    Hears how the nectar's sweetness coaxes the hive's dawn chorus to ignite.
    When R brushes past Theta, the impedance membrane slackens and the waggle
    dances bloom, letting us witness the aurora of collective decision.
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
            sigma_values.append(float(row["waggle_activation_rate"]))
    return {"R": R_values, "sigma": sigma_values}


def fit_power_law_null(R: Iterable[float], sigma: Iterable[float]) -> Dict[str, float]:
    """Calibrate a smooth power-law null sigma = A * R^k for falsification."""

    R_list = [float(value) for value in R]
    sigma_list = [float(value) for value in sigma]
    if not R_list:
        raise ValueError("Power-law null requires at least one observation")

    log_R = [math.log(max(value, 1e-6)) for value in R_list]
    log_sigma = [math.log(min(max(value, 1e-6), 1.0)) for value in sigma_list]
    mean_x = sum(log_R) / len(log_R)
    mean_y = sum(log_sigma) / len(log_sigma)
    Sxx = sum((value - mean_x) ** 2 for value in log_R)
    Sxy = sum((log_R[idx] - mean_x) * (log_sigma[idx] - mean_y) for idx in range(len(log_R)))

    exponent = Sxy / Sxx if Sxx > 0 else 0.0
    log_A = mean_y - exponent * mean_x
    amplitude = math.exp(log_A)
    predictions = [amplitude * (value ** exponent) for value in R_list]
    predictions = [min(max(pred, 0.0), 1.0) for pred in predictions]

    residuals = [sigma_list[idx] - predictions[idx] for idx in range(len(R_list))]
    ss_res = sum(value ** 2 for value in residuals)
    mean_sigma = sum(sigma_list) / len(sigma_list)
    ss_tot = sum((value - mean_sigma) ** 2 for value in sigma_list)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    n = len(R_list)
    aic = float("-inf") if ss_res <= 0 else n * math.log(ss_res / n) + 2 * 2

    return {
        "model": "sigma = A * R^k",
        "amplitude": amplitude,
        "exponent": exponent,
        "r2": r2,
        "aic": aic,
        "ss_res": ss_res,
    }


def impedance_profile(R: Iterable[float], theta: float, beta: float) -> Dict[str, float]:
    """Compute a nectar membrane impedance sketch linked to logistic resonance."""

    samples = []
    for value in R:
        sigma = float(logistic_response(value, theta, beta))
        zeta = 1.25 - 0.35 * sigma
        samples.append({"R": value, "sigma": sigma, "zeta": zeta})
    mean_zeta = sum(item["zeta"] for item in samples) / len(samples)
    variance = sum((item["zeta"] - mean_zeta) ** 2 for item in samples) / len(samples)
    return {
        "definition": "zeta(R) = 1.25 - 0.35 * sigma(beta(R-Theta))",
        "mean": mean_zeta,
        "std": math.sqrt(max(variance, 0.0)),
        "samples": samples,
    }


def build_summary(data_path: Path, output_path: Path) -> Dict[str, object]:
    """Load the dataset, fit logistic and null models, and export UTF diagnostics."""

    observations = read_dataset(data_path)
    fit_metrics = fit_threshold_parameters(observations["R"], observations["sigma"])
    null_metrics_linear = evaluate_null_model(observations["R"], observations["sigma"])
    null_metrics_power = fit_power_law_null(observations["R"], observations["sigma"])

    logistic_predictions = [
        float(logistic_response(value, fit_metrics["theta"], fit_metrics["beta"]))
        for value in observations["R"]
    ]
    zeta_info = impedance_profile(observations["R"], fit_metrics["theta"], fit_metrics["beta"])

    falsification = {
        "linear_null": {
            "delta_aic": null_metrics_linear["aic"] - fit_metrics["aic"],
            "delta_r2": fit_metrics["r2"] - null_metrics_linear["r2"],
        },
        "power_law_null": {
            "delta_aic": null_metrics_power["aic"] - fit_metrics["aic"],
            "delta_r2": fit_metrics["r2"] - null_metrics_power["r2"],
        },
    }

    summary = assemble_summary(
        {
            "R": observations["R"],
            "sigma": logistic_predictions,
            "zeta": [item["zeta"] for item in zeta_info["samples"]],
            "flux": [obs_sigma - pred for obs_sigma, pred in zip(observations["sigma"], logistic_predictions)],
            "theta": [fit_metrics["theta"]],
            "beta": [fit_metrics["beta"]],
        },
        fit_metrics,
        null_metrics_linear,
    )

    summary["dataset"] = {
        "path": str(data_path),
        "control_parameter": "nectar sucrose concentration (Brix)",
        "order_parameter": "probability of waggle recruitment",
        "measurements": [
            {"R": R, "sigma": sigma, "logistic_fit": pred}
            for R, sigma, pred in zip(observations["R"], observations["sigma"], logistic_predictions)
        ],
    }
    summary["null_models"] = {
        "linear": null_metrics_linear,
        "power_law": null_metrics_power,
    }
    summary["falsification"] = falsification
    summary["impedance"] = zeta_info
    summary["tri_layer"] = {
        "formal": "Logistic regression on logit domain with dual smooth null comparisons (linear, power-law).",
        "empirical": "Honeybee waggle activation sampled across sucrose gradients; JSON export for RepoPlan cross-links.",
        "metaphorical": "Notes how the hive's membrane relaxes as nectar sweetness breaches Theta, brightening the waggle dawn chorus.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    return summary


def parse_args() -> argparse.Namespace:
    """Configure CLI arguments for regenerating the waggle resonance fit."""

    parser = argparse.ArgumentParser(
        description="Fit honeybee waggle activation logistic thresholds with falsification checks.",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/biology/honeybee_waggle_activation.csv"),
        help="Path to the waggle activation CSV (columns: R, waggle_activation_rate).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis/results/honeybee_waggle_fit.json"),
        help="Destination for the JSON summary containing threshold diagnostics.",
    )
    return parser.parse_args()


def main() -> None:
    """Execute the UTF waggle fitting workflow and report resonance summary."""

    args = parse_args()
    summary = build_summary(args.data, args.output)
    print(json.dumps(summary["falsification"], indent=2))


if __name__ == "__main__":
    main()
