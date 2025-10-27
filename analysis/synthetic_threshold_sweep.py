r"""Synthetic UTF threshold sweep generator with tri-layer cadence.

Formal layer:
    Samples the logistic response \(\sigma(\beta(R-\Theta))\) via the
    `LogisticFieldEnvelope`, decorates it with impedance traces \(\zeta(R)\), and
    forwards the results through the resonance fitting pipeline.  Reports
    \(\Theta\), \(\beta\), \(R^2\), AIC, and smooth null counterpoints so the
    falsification ledger stays intact.

Empirical layer:
    Acts as a CLI workflow for collaborators who need reproducible synthetic
    sweeps to test dashboards, notebooks, or simulator hooks.  The script exports
    JSON summaries plus an optional CSV so downstream modules can replay the
    experiment without ambiguity.

Metaphorical layer:
    Lets the team rehearse the dawn crossing on a controlled membrane, tracing
    how the impedance veil hums as R strolls past \(\Theta\) before unleashing
    the full auroral choir on domain datasets.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, Tuple

from resonance_fit_pipeline import (
    assemble_summary,
    evaluate_null_model,
    evaluate_power_law_null,
    fit_threshold_parameters,
)

from models import LogisticFieldEnvelope, logistic_response


def write_csv(path: Path, traces: Dict[str, Iterable[float]]) -> None:
    r"""Persist the sweep traces to CSV for reproducibility."""

    fieldnames = ["t", "R", "sigma", "sigma_clean", "zeta", "flux"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(fieldnames)
        rows = zip(
            traces.get("t", []),
            traces.get("R", []),
            traces.get("sigma", []),
            traces.get("sigma_clean", []),
            traces.get("zeta", []),
            traces.get("flux", []),
        )
        for row in rows:
            writer.writerow([f"{value:.10f}" for value in row])



def build_summary(args: argparse.Namespace) -> Tuple[Dict[str, object], Dict[str, Iterable[float]]]:
    r"""Generate a synthetic sweep, fit logistics, and package diagnostics."""

    envelope = LogisticFieldEnvelope(
        theta=args.theta,
        beta=args.beta,
        amplitude=args.amplitude,
        resonant_gain=args.resonant_gain,
        damped_gain=args.damped_gain,
        impedance_width=args.impedance_width,
    )
    traces = envelope.sweep(
        span=args.span,
        points=args.points,
        noise=args.noise,
        random_seed=args.seed,
    )

    R_values = traces["R"]
    sigma_observed = traces["sigma"]
    fit_metrics = fit_threshold_parameters(R_values, sigma_observed)
    null_metrics = {
        "linear": evaluate_null_model(R_values, sigma_observed),
        "power_law": evaluate_power_law_null(R_values, sigma_observed),
    }
    sigma_fit = [
        float(logistic_response(value, fit_metrics["theta"], fit_metrics["beta"]))
        for value in R_values
    ]

    results_payload = {
        "t": traces["t"],
        "R": R_values,
        "sigma": sigma_observed,
        "sigma_clean": traces["sigma_clean"],
        "sigma_fit": sigma_fit,
        "zeta": traces["zeta"],
        "flux": traces["flux"],
        "theta": [envelope.theta],
        "beta": [envelope.beta],
    }
    summary = assemble_summary(results_payload, fit_metrics, null_metrics)
    summary["results"] = results_payload

    summary["experiment"] = {
        "control_parameter": "R sweep centred on Theta",
        "theta_true": envelope.theta,
        "beta_true": envelope.beta,
        "amplitude": envelope.amplitude,
        "impedance": {
            "resonant_gain": envelope.resonant_gain,
            "damped_gain": envelope.damped_gain,
            "width": envelope.impedance_width,
            "definition": "zeta(R) = g_r + (g_d - g_r) * sigma((R-Theta)/w)",
        },
        "noise_std": args.noise,
        "points": args.points,
        "span": args.span,
        "seed": args.seed,
        "falsification_margin": summary["falsification"],
    }
    summary["tri_layer"] = {
        "formal": (
            "Logistic sweep fitted with logit regression, contrasted against"
            " linear and power-law null breezes."
        ),
        "empirical": (
            "Synthetic payload exported for dashboards and simulator hooks;"
            " JSON and CSV carry provenance."
        ),
        "metaphorical": (
            "A lantern-lit rehearsal where the membrane hums as R brushes Theta,"
            " confirming the auroral chorus outshines smooth winds."
        ),
    }

    return summary, results_payload


def parse_args() -> argparse.Namespace:
    r"""Configure CLI parameters for the synthetic sweep rehearsal."""

    parser = argparse.ArgumentParser(
        description="Generate a synthetic logistic threshold sweep with UTF diagnostics.",
    )
    parser.add_argument("--theta", type=float, default=0.0, help="Critical threshold Theta controlling the sweep centre.")
    parser.add_argument("--beta", type=float, default=8.0, help="Steepness beta governing the logistic ascent.")
    parser.add_argument("--amplitude", type=float, default=1.0, help="Amplitude multiplier representing impedance scaling.")
    parser.add_argument("--resonant-gain", dest="resonant_gain", type=float, default=0.7, help="Impedance floor zeta below Theta.")
    parser.add_argument("--damped-gain", dest="damped_gain", type=float, default=1.3, help="Impedance ceiling zeta above Theta.")
    parser.add_argument("--impedance-width", dest="impedance_width", type=float, default=0.5, help="Width of the impedance transition zone.")
    parser.add_argument("--span", type=float, default=1.0, help="Half-width of the control parameter sweep around Theta.")
    parser.add_argument("--points", type=int, default=60, help="Number of samples in the sweep trajectory.")
    parser.add_argument("--noise", type=float, default=0.02, help="Standard deviation of Gaussian noise added to sigma.")
    parser.add_argument("--seed", type=int, default=7, help="Random seed for noise reproducibility.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis/results/synthetic_threshold_sweep.json"),
        help="Destination JSON file for the resonance summary.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("analysis/results/synthetic_threshold_sweep.csv"),
        help="Optional CSV path to store the raw sweep traces.",
    )
    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Skip writing the CSV dataset while keeping the JSON summary.",
    )
    return parser.parse_args()


def main() -> None:
    r"""Execute the synthetic sweep workflow and emit falsification verdict."""

    args = parse_args()
    summary, traces = build_summary(args)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    if not args.no_csv and args.csv is not None:
        write_csv(args.csv, traces)
    print(json.dumps(summary["falsification"], indent=2))


if __name__ == "__main__":
    main()
