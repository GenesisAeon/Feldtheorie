r"""Guardrail for high-β logistic fits across UTAC manifest entries.

Formal stratum:
    Revisits datasets with steep \(\beta\) targets, runs \(\sigma(\beta(R-\Theta))\)
    fits via the shared loader, and reports ΔAIC guards alongside instrumentation
    heuristics.

Empirical stratum:
    Filters `data/utac_v1_3_data_manifest.yaml` for entries exceeding a configurable
    β-threshold, hydrates metadata, optionally synthesises rehearsals, and emits a
    consolidated JSON report for codex and UTAC-status mirrors.

Metaphorical stratum:
    When a lantern blazes with β>10, this validator checks whether the light is a
    genuine regime split or an instrumentation glare, letting ζ(R) stay calm.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

from .outlier_beta_review import instrumentation_heuristic
from .threshold_dataset_loader import (
    describe_result,
    evaluate_logistic_fit,
    guard_delta_aic,
    load_dataset,
    load_metadata,
)
from .utac_manifest import ManifestDataset, filter_datasets, load_manifest

ROOT = Path(__file__).resolve().parents[1]
RESULTS_ROOT = ROOT / "analysis" / "results"


def is_outlier_candidate(dataset: ManifestDataset, beta_threshold: float) -> bool:
    if dataset.beta_target is None:
        return False
    return dataset.beta_target >= beta_threshold


def analyse_dataset(
    dataset: ManifestDataset,
    simulate_missing: bool,
    seed: Optional[int],
) -> Dict[str, object]:
    metadata = load_metadata(dataset.metadata_path)
    frame, origin = load_dataset(metadata, simulate_missing=simulate_missing, seed=seed)
    result = evaluate_logistic_fit(dataset.identifier, metadata, frame, origin)

    guard_threshold = metadata.delta_aic_guard or 10.0
    guard_pass = guard_delta_aic(result, guard_threshold)
    instrument_flag = instrumentation_heuristic(result.beta, result.delta_aic_best, result.r_squared)

    payload = result.to_dict()
    payload.update(
        {
            "theta_manifest_estimate": dataset.theta_estimate,
            "beta_manifest_target": dataset.beta_target,
            "resonance_status": dataset.resonance_status,
            "delta_aic_guard_threshold": guard_threshold,
            "delta_aic_guard_passed": guard_pass,
            "instrumentation_flag": instrument_flag,
            "summary": describe_result(result),
        }
    )
    return payload


def run_cli(args: argparse.Namespace) -> None:
    manifest_path = ROOT / args.manifest
    datasets = load_manifest(manifest_path)
    filtered = filter_datasets(datasets, domains=args.domain, identifiers=args.dataset)

    candidates: List[ManifestDataset] = [
        dataset
        for dataset in filtered
        if is_outlier_candidate(dataset, args.beta_threshold)
    ]

    if not candidates:
        raise SystemExit("No datasets exceeded the β threshold. Adjust filters if needed.")

    results: List[Dict[str, object]] = []
    for dataset in candidates:
        payload = analyse_dataset(dataset, simulate_missing=args.simulate_missing, seed=args.seed)
        results.append(payload)
        if args.verbose:
            print(payload["summary"], payload["instrumentation_flag"])

    report = {
        "generated_at": "pending-runtime",
        "beta_threshold": args.beta_threshold,
        "datasets": results,
    }

    output_path = RESULTS_ROOT / "outlier_validator_report.json"
    if args.output_path:
        output_path = Path(args.output_path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/utac_v1_3_data_manifest.yaml"),
        help="Path to the UTAC v1.3 data manifest (YAML).",
    )
    parser.add_argument(
        "--domain",
        type=str,
        nargs="*",
        help="Restrict to specific domains (optional).",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        nargs="*",
        help="Restrict to specific dataset identifiers (optional).",
    )
    parser.add_argument(
        "--beta-threshold",
        type=float,
        default=10.0,
        help="Minimum manifest β target to flag as outlier candidate.",
    )
    parser.add_argument(
        "--simulate-missing",
        action="store_true",
        help="Generate synthetic rehearsal data when raw files are absent.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for simulation mode.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        help="Write the consolidated report to a custom path.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-dataset summaries to stdout.",
    )
    return parser


if __name__ == "__main__":
    run_cli(build_parser().parse_args())
