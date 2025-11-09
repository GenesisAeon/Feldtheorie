"""Scan UTAC v2 readiness manifest and report missing activation components.

This helper re-reads ``analysis/reports/utac_v2_readiness.json`` (or a
user-specified manifest), checks the filesystem for every declared component,
and emits a concise summary describing what already exists versus the gaps
that still keep σ(β(R-Θ)) below the activation threshold.

Usage
-----
Run the module as a script to generate a fresh timestamped JSON report under
``analysis/results/`` and echo a human-readable synopsis::

    python -m analysis.utac_manifest_gap_scan --output analysis/results/...

The output file name defaults to the current UTC timestamp so repeated scans
can be archived without overwriting earlier audits.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence


DEFAULT_MANIFEST = Path("analysis/reports/utac_v2_readiness.json")
RESULT_DIRECTORY = Path("analysis/results")


def _logistic(beta: float, r_value: float, theta: float) -> float:
    """Compute σ(β(R-Θ)) for the given parameters."""

    return 1.0 / (1.0 + math.exp(-beta * (r_value - theta)))


def _ensure_exists(path: Path) -> bool:
    """Return True when ``path`` exists on disk."""

    return path.exists()


def _collect_missing_components(
    components: Sequence[Mapping[str, Any]]
) -> List[Dict[str, Any]]:
    """Return metadata for components that do not exist on disk."""

    missing: List[Dict[str, Any]] = []
    for comp in components:
        path = Path(comp.get("path", ""))
        exists = _ensure_exists(path)
        if not exists:
            missing.append(
                {
                    "name": comp.get("name") or path.name,
                    "path": str(path),
                    "kind": comp.get("kind", "unknown"),
                }
            )
    return missing


def _collect_target_gaps(targets: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Return a list with every missing target and expected output."""

    gaps: List[Dict[str, Any]] = []
    for target in targets:
        path = Path(target.get("path", ""))
        description = target.get("description")
        category = target.get("category")

        if not _ensure_exists(path):
            gaps.append(
                {
                    "path": str(path),
                    "category": category,
                    "description": description,
                    "kind": "target",
                }
            )

        for output in target.get("expected_outputs", []):
            out_path = Path(output.get("path", ""))
            if not _ensure_exists(out_path):
                gaps.append(
                    {
                        "path": str(out_path),
                        "category": category,
                        "description": output.get("description") or description,
                        "kind": output.get("kind", "expected_output"),
                    }
                )
    return gaps


def scan_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Generate a gap summary for the provided manifest file."""

    manifest_data = json.loads(manifest_path.read_text())

    logistic_meta = manifest_data.get("meta", {}).get("logistic", {})
    beta = float(logistic_meta.get("beta", 0.0))
    theta = float(logistic_meta.get("theta", 0.0))
    readiness = float(logistic_meta.get("mean_readiness", 0.0))
    sigma = _logistic(beta, readiness, theta)

    dataset_entries: List[Dict[str, Any]] = []
    total_missing_components = 0

    for dataset in manifest_data.get("datasets", []):
        components = dataset.get("components", [])
        missing_components = _collect_missing_components(components)
        total_missing_components += len(missing_components)

        observed_ratio = 0.0
        if components:
            observed_ratio = (len(components) - len(missing_components)) / len(components)

        dataset_entries.append(
            {
                "id": dataset.get("id"),
                "domain": dataset.get("domain"),
                "reported_ratio": dataset.get("actual_readiness_ratio"),
                "observed_ratio": observed_ratio,
                "missing_components": missing_components,
            }
        )

    dataset_ready = sum(1 for entry in dataset_entries if entry["observed_ratio"] >= 1.0)
    dataset_partial = sum(
        1 for entry in dataset_entries if 0.0 < entry["observed_ratio"] < 1.0
    )

    analysis_gaps = _collect_target_gaps(manifest_data.get("analysis_targets", []))
    doc_gaps = _collect_target_gaps(manifest_data.get("doc_targets", []))
    sigillin_gaps = _collect_target_gaps(manifest_data.get("sigillin_targets", []))
    simulator_gaps = _collect_target_gaps(manifest_data.get("simulator_targets", []))

    now = _dt.datetime.now(tz=_dt.timezone.utc)

    summary: Dict[str, Any] = {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "source_manifest": str(manifest_path),
        "logistic": {
            "beta": beta,
            "theta": theta,
            "mean_readiness": readiness,
            "sigma": sigma,
        },
        "datasets": dataset_entries,
        "summary": {
            "datasets_total": len(dataset_entries),
            "datasets_ready": dataset_ready,
            "datasets_partial": dataset_partial,
            "datasets_pending": len(dataset_entries) - dataset_ready,
            "missing_components_total": total_missing_components,
            "analysis_gaps": len(analysis_gaps),
            "documentation_gaps": len(doc_gaps),
            "sigillin_gaps": len(sigillin_gaps),
            "simulator_gaps": len(simulator_gaps),
        },
        "gaps": {
            "analysis": analysis_gaps,
            "documentation": doc_gaps,
            "sigillin": sigillin_gaps,
            "simulator": simulator_gaps,
        },
    }

    return summary


def _default_output_path(timestamp: str) -> Path:
    return RESULT_DIRECTORY / f"utac_v2_manifest_gap_scan_{timestamp}.json"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to the UTAC v2 readiness manifest JSON.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Where to write the gap scan JSON report. Defaults to analysis/results/ with a timestamped filename.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress the brief stdout summary.",
    )

    args = parser.parse_args(argv)

    manifest_path = args.manifest
    if not manifest_path.exists():
        parser.error(f"manifest file not found: {manifest_path}")

    summary = scan_manifest(manifest_path)
    timestamp = summary["generated_at"].replace(":", "").replace("-", "")
    if args.output is None:
        output_path = _default_output_path(timestamp)
    else:
        output_path = args.output

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2))

    if not args.quiet:
        sigma = summary["logistic"]["sigma"]
        readiness = summary["logistic"]["mean_readiness"]
        theta = summary["logistic"]["theta"]
        beta = summary["logistic"]["beta"]
        missing = summary["summary"]["missing_components_total"]
        datasets_pending = summary["summary"]["datasets_pending"]

        print(
            "σ(β(R-Θ))={sigma:.3f} (β={beta:.2f}, R={readiness:.2f}, Θ={theta:.2f}) → "
            "{pending} datasets pending, {missing} components missing".format(
                sigma=sigma,
                beta=beta,
                readiness=readiness,
                theta=theta,
                pending=datasets_pending,
                missing=missing,
            )
        )

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
