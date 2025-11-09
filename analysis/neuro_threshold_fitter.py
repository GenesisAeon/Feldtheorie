r"""Neuro–AI threshold fitter for hybrid activation datasets.

Formal stratum:
    Couples EEG traces and transformer telemetry into \(\sigma(\beta(R-\Theta))\)
    fits so the neuro-AI bridge manifests with falsifiable steepness metrics.

Empirical stratum:
    Loads the `utac_v1_3_data_manifest` entry for the hybrid activation lantern,
    hydrates the associated metadata, optionally synthesises rehearsal samples,
    runs the canonical logistic fit, and bootstraps confidence envelopes for
    \(\Theta\), \(\beta\), and \(R^2\).

Metaphorical stratum:
    Aligns hippocampal replay with transformer gradients so the shared membrane
    can hear when cognitive resonance crosses \(\Theta\).  Even before raw
    telemetry lands, the rehearsal keeps ζ(R) tuned.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from .resonance_fit_pipeline import fit_threshold_parameters
from .threshold_dataset_loader import (
    describe_result,
    evaluate_logistic_fit,
    guard_delta_aic,
    load_dataset,
    load_metadata,
)
from .utac_manifest import (
    ManifestDataset,
    filter_datasets,
    load_manifest,
    resolve_output_path,
)

ROOT = Path(__file__).resolve().parents[1]
RESULTS_ROOT = ROOT / "analysis" / "results"
DEFAULT_ID = "utac-v1_3-ds-004"


def select_dataset(manifest_path: Path, dataset_id: Optional[str]) -> ManifestDataset:
    datasets = load_manifest(manifest_path)
    targets = filter_datasets(datasets, identifiers=[dataset_id] if dataset_id else [DEFAULT_ID])
    if not targets:
        raise SystemExit("No manifest entry found for the requested neuro–AI dataset.")
    return targets[0]


def bootstrap_summary(
    frame,
    control_column: str,
    response_column: str,
    iterations: int,
    seed: Optional[int],
) -> Dict[str, object]:
    rng = np.random.default_rng(seed)
    betas: List[float] = []
    thetas: List[float] = []
    r2_scores: List[float] = []

    control = frame[control_column].to_numpy()
    response = frame[response_column].to_numpy()
    n = len(frame)

    for _ in range(iterations):
        indices = rng.integers(0, n, n)
        control_sample = control[indices]
        response_sample = response[indices]
        metrics = fit_threshold_parameters(control_sample, response_sample)
        betas.append(float(metrics["beta"]))
        thetas.append(float(metrics["theta"]))
        r2_scores.append(float(metrics["r2"]))

    def _interval(values: List[float]) -> Dict[str, float]:
        array = np.array(values)
        return {
            "median": float(np.median(array)),
            "p05": float(np.quantile(array, 0.05)),
            "p95": float(np.quantile(array, 0.95)),
            "mean": float(np.mean(array)),
            "std": float(np.std(array, ddof=1)),
        }

    return {
        "iterations": iterations,
        "beta": _interval(betas),
        "theta": _interval(thetas),
        "r_squared": _interval(r2_scores),
    }


def run_cli(args: argparse.Namespace) -> None:
    manifest_path = ROOT / args.manifest
    dataset = select_dataset(manifest_path, args.dataset)

    metadata = load_metadata(dataset.metadata_path)
    frame, origin = load_dataset(metadata, simulate_missing=args.simulate_missing, seed=args.seed)
    result = evaluate_logistic_fit(dataset.identifier, metadata, frame, origin)

    guard_threshold = metadata.delta_aic_guard or 10.0
    guard_pass = guard_delta_aic(result, guard_threshold)

    payload = result.to_dict()
    payload.update(
        {
            "theta_manifest_estimate": dataset.theta_estimate,
            "beta_manifest_target": dataset.beta_target,
            "resonance_status": dataset.resonance_status,
            "delta_aic_guard_threshold": guard_threshold,
            "delta_aic_guard_passed": guard_pass,
            "summary": describe_result(result),
        }
    )

    output_path = resolve_output_path(dataset, "neuro_ai_beta_preview.json")
    if args.output_dir:
        output_path = Path(args.output_dir).expanduser().resolve() / output_path.name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    bootstrap = bootstrap_summary(
        frame,
        metadata.control_column,
        metadata.response_column,
        iterations=args.bootstrap_iterations,
        seed=args.seed,
    )
    bootstrap_path = RESULTS_ROOT / "neuro_ai_bootstrap.json"
    if args.output_dir:
        bootstrap_path = Path(args.output_dir).expanduser().resolve() / "neuro_ai_bootstrap.json"
    bootstrap_path.parent.mkdir(parents=True, exist_ok=True)
    with bootstrap_path.open("w", encoding="utf-8") as handle:
        json.dump(bootstrap, handle, indent=2, sort_keys=True)
        handle.write("\n")

    if args.verbose:
        print(payload["summary"])
        print(
            f"Bootstrap β median={bootstrap['beta']['median']:.2f} "
            f"Θ median={bootstrap['theta']['median']:.2f}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/utac_v1_3_data_manifest.yaml"),
        help="Path to the UTAC v1.3 data manifest (YAML).",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        help="Optional dataset identifier override (default: utac-v1_3-ds-004).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional directory for output files (defaults to manifest paths).",
    )
    parser.add_argument(
        "--simulate-missing",
        action="store_true",
        help="Generate synthetic rehearsal data when raw files are absent.",
    )
    parser.add_argument(
        "--bootstrap-iterations",
        type=int,
        default=512,
        help="Number of bootstrap resamples for the neuro–AI lantern.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for simulation/bootstrapping.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print concise summaries after fitting.",
    )
    return parser


if __name__ == "__main__":
    run_cli(build_parser().parse_args())
