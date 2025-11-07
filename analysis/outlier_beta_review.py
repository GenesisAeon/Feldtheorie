"""Outlier β review for socio-ecological thresholds with tri-layer cadence.

Formal layer:
    Aggregates high-β socio-ecological datasets (Amazon resilience and urban
    heat canopy) to verify whether σ(β(R-Θ)) remains the best explanation
    against smooth nulls. Computes ΔAIC margins, confidence intervals, and an
    instrumentation heuristic so the repository can distinguish genuine regime
    splits from artefacts.

Empirical layer:
    Provides a CLI that replays the fits using `resonance_fit_pipeline` and
    exports a JSON ledger.  The payload feeds the UTAC status matrix and the
    socio-ecological metadata scrolls, keeping outlier tracking reproducible.

Metaphorical layer:
    Listens to membranes under stress: rainforest canopies thinning into
    rainless dawns and urban heat islands shimmering at twilight.  The script
    reports whether the sharp crescendos are authentic threshold bells or just
    instrument hum.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

from resonance_fit_pipeline import (
    assemble_summary,
    evaluate_null_model,
    evaluate_power_law_null,
    fit_threshold_parameters,
)
from models.membrane_solver import logistic_response


@dataclass
class DatasetSpec:
    """Describe an outlier dataset and its expected columns."""

    identifier: str
    path: Path
    control_column: str
    response_column: str
    order_parameter_description: str
    control_parameter_description: str
    narrative: str


def read_csv(path: Path, control_column: str, response_column: str) -> Dict[str, List[float]]:
    """Read control and response columns from a CSV file."""

    import csv

    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        control: List[float] = []
        response: List[float] = []
        for row in reader:
            control.append(float(row[control_column]))
            response.append(float(row[response_column]))
    return {"R": control, "sigma": response}


def logistic_predictions(R: Iterable[float], theta: float, beta: float) -> List[float]:
    """Return σ(β(R-Θ)) evaluations for convenience."""

    return [float(logistic_response(value, theta, beta)) for value in R]


def instrumentation_heuristic(beta: float, delta_aic: float, r_squared: float) -> str:
    """Classify outlier behaviour to flag potential instrumentation artefacts."""

    if not all(map(_is_finite, (beta, delta_aic, r_squared))):
        return "indeterminate"
    if beta >= 10.0 and delta_aic >= 50.0 and r_squared >= 0.995:
        return "genuine_regime_split"
    if beta >= 10.0 and delta_aic < 20.0:
        return "possible_instrumentation_bias"
    if beta < 3.0 and delta_aic < 10.0:
        return "smooth_null_competes"
    return "requires_follow_up"


def _is_finite(value: float) -> bool:
    return math.isfinite(value)


def analyse_dataset(spec: DatasetSpec) -> Dict[str, object]:
    """Fit logistic and null models for the supplied dataset."""

    observations = read_csv(spec.path, spec.control_column, spec.response_column)
    fit_metrics = fit_threshold_parameters(observations["R"], observations["sigma"])
    linear_null = evaluate_null_model(observations["R"], observations["sigma"])
    power_null = evaluate_power_law_null(observations["R"], observations["sigma"])

    best_null_aic = min(linear_null.get("aic", float("inf")), power_null.get("aic", float("inf")))
    delta_aic = best_null_aic - fit_metrics.get("aic", float("inf"))

    sigma_fit = logistic_predictions(observations["R"], fit_metrics["theta"], fit_metrics["beta"])

    falsification = {
        "linear": {
            "r2": linear_null["r2"],
            "aic": linear_null["aic"],
            "delta_aic": linear_null["aic"] - fit_metrics["aic"],
        },
        "power_law": {
            "r2": power_null["r2"],
            "aic": power_null["aic"],
            "delta_aic": power_null["aic"] - fit_metrics["aic"],
        },
        "best_delta_aic": delta_aic,
    }

    instrumentation_flag = instrumentation_heuristic(
        fit_metrics["beta"], falsification["best_delta_aic"], fit_metrics["r2"]
    )

    try:
        dataset_path = str(spec.path.relative_to(Path(__file__).resolve().parents[1]))
    except ValueError:
        dataset_path = str(spec.path)

    payload = {
        "identifier": spec.identifier,
        "dataset_path": dataset_path,
        "control_parameter": spec.control_parameter_description,
        "order_parameter": spec.order_parameter_description,
        "theta": fit_metrics["theta"],
        "theta_ci": [fit_metrics["theta_ci_lower"], fit_metrics["theta_ci_upper"]],
        "beta": fit_metrics["beta"],
        "beta_ci": [fit_metrics["beta_ci_lower"], fit_metrics["beta_ci_upper"]],
        "r_squared": fit_metrics["r2"],
        "aic": fit_metrics["aic"],
        "sigma_fit": sigma_fit,
        "measurements": list(
            {
                "R": float(R_value),
                "sigma": float(sigma_value),
                "logistic_fit": float(pred_value),
            }
            for R_value, sigma_value, pred_value in zip(
                observations["R"], observations["sigma"], sigma_fit
            )
        ),
        "falsification": falsification,
        "instrumentation_flag": instrumentation_flag,
        "narrative": spec.narrative,
    }

    summary = assemble_summary(
        {
            "R": observations["R"],
            "sigma": observations["sigma"],
            "sigma_fit": sigma_fit,
            "theta": [fit_metrics["theta"]],
            "beta": [fit_metrics["beta"]],
        },
        fit_metrics,
        {"linear": linear_null, "power_law": power_null},
    )
    summary.update(payload)
    return summary


def default_specs(base_path: Path) -> List[DatasetSpec]:
    """Return default dataset specifications for outlier review."""

    return [
        DatasetSpec(
            identifier="amazon_resilience",
            path=base_path / "data" / "socio_ecology" / "amazon_resilience.csv",
            control_column="R",
            response_column="moisture_retention",
            control_parameter_description="Remaining rainforest canopy fraction",
            order_parameter_description="Probability of convective moisture retention",
            narrative="Rainforest moisture resonance under deforestation stress.",
        ),
        DatasetSpec(
            identifier="urban_heat_canopy",
            path=base_path / "data" / "socio_ecology" / "urban_heat_canopy.csv",
            control_column="R",
            response_column="safe_night_fraction",
            control_parameter_description="Urban canopy fraction in heat-vulnerable districts",
            order_parameter_description="Probability of nights staying below heat-stress threshold",
            narrative="Urban membrane shimmering as tree cover retreats.",
        ),
    ]


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the outlier review workflow."""

    parser = argparse.ArgumentParser(
        description="Review high-β socio-ecological datasets against smooth nulls.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis/results/outlier_beta_review.json"),
        help="Destination for the resonance ledger JSON output.",
    )
    return parser.parse_args()


def main() -> None:
    """Execute the outlier β review and export tri-layer summaries."""

    args = parse_args()
    base_path = Path(__file__).resolve().parents[1]
    specs = default_specs(base_path)

    summaries = [analyse_dataset(spec) for spec in specs]

    tri_layer = {
        "formal": "Aggregated σ(β(R-Θ)) fits with dual null comparisons (linear, power-law).",
        "empirical": "Datasets: Amazon resilience & urban heat canopy. ΔAIC ledger exported for UTAC v1.2 reviews.",
        "metaphorical": "Checks whether rainforest and city membranes sing authentic threshold arias or mask instrument hiss.",
    }

    payload = {
        "generated_from": [spec.identifier for spec in specs],
        "summaries": summaries,
        "tri_layer": tri_layer,
        "status": "primed",
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    print(json.dumps({item["identifier"]: item["instrumentation_flag"] for item in summaries}, indent=2))


if __name__ == "__main__":
    main()
