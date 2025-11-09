r"""Logistic fit pipeline for UTAC v1.3 climate lanterns.

Formal stratum:
    Harvests manifest entries so each climate dataset reports \(\sigma(\beta(R-\Theta))\),
    ΔAIC guards, and impedance sketches.  Uses the shared threshold dataset loader
    to deliver falsifiable logistic metrics for Urban Heat und Amazon Hydro fields.

Empirical stratum:
    Reads `data/utac_v1_3_data_manifest.yaml`, hydrates CSV/NetCDF payloads (or
    synthesises rehearsals when raw files are pending), fits against the canonical
    logistic response, and exports JSON ledgers ready for docs, simulator presets,
    and codex updates.

Metaphorical stratum:
    Lets the climate membrane rehearse even before the satellite rasters land.
    Urban heat dawns and rainforest breaths are woven into preview lanterns so the
    codex already hears wie \(R\) grazes \(\Theta\) und wie \(\beta\) sharpens.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional

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


def process_dataset(
    dataset: ManifestDataset,
    simulate_missing: bool,
    seed: Optional[int],
) -> Dict[str, object]:
    metadata = load_metadata(dataset.metadata_path)
    frame, origin = load_dataset(metadata, simulate_missing=simulate_missing, seed=seed)
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
    return payload


def write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def aggregate_summary(results: List[Dict[str, object]]) -> Dict[str, object]:
    return {
        "generated_at": "pending-runtime",
        "datasets": results,
        "notes": "Preview payload – timestamps populate when the CLI runs.",
    }


def run_cli(args: argparse.Namespace) -> None:
    manifest_path = ROOT / args.manifest
    datasets = load_manifest(manifest_path)
    targets = filter_datasets(datasets, domains=args.domain, identifiers=args.dataset)

    if not targets:
        raise SystemExit("No datasets matched the selection filters.")

    results: List[Dict[str, object]] = []
    for dataset in targets:
        payload = process_dataset(dataset, simulate_missing=args.simulate_missing, seed=args.seed)
        results.append(payload)
        output_path = resolve_output_path(dataset, f"{dataset.identifier}_preview.json")
        if args.output_dir:
            output_path = Path(args.output_dir).expanduser().resolve() / output_path.name
        write_json(output_path, payload)
        if args.verbose:
            print(payload["summary"])

    summary = aggregate_summary(results)
    summary_path = RESULTS_ROOT / "climate_beta_summary.json"
    if args.output_dir:
        summary_path = Path(args.output_dir).expanduser().resolve() / "climate_beta_summary.json"
    write_json(summary_path, summary)


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
        default=["climate"],
        help="Domains to process (default: climate).",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        nargs="*",
        help="Specific dataset identifiers to process (optional).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional directory for output files (defaults to manifest paths).",
    )
    parser.add_argument(
        "--simulate-missing",
        action="store_true",
        help="Generate synthetic data when raw files are absent.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for simulation mode.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print concise summaries for each dataset.",
    )
    return parser


if __name__ == "__main__":
    run_cli(build_parser().parse_args())
