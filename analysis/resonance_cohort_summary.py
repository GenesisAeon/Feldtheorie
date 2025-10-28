#!/usr/bin/env python3
r"""Cohort-wide resonance summary for UTF logistic fits.

Formal cadence
--------------
Aggregates the threshold quartet \((R, \Theta, \beta, \zeta(R))\) across analysis
results by ingesting JSON exports of \(\sigma(\beta(R-\Theta))\) fits. For each
result file we extract the estimated \(\Theta\), \(\beta\), the logistic
goodness-of-fit, and falsification deltas against the smooth null baselines.
Summary statistics (mean/median/min/max) keep the repository aligned on when the
logistic membrane decisively outruns its null counterparts.

Empirical cadence
-----------------
Designed as a CLI utility that scans `analysis/results/` (or user-specified
folders), composes a cohort summary, and emits a machine-friendly JSON payload
ready for dashboards, notebooks, or cross-references in `docs/` and the
simulator presets. The script also prints a compact textual roster highlighting
the strongest resonance gains and any files that lack falsification coverage.

Metaphorical cadence
--------------------
Listens across the resonance grove to hear which membranes already sing in
auroral unison and where the null-model winds still whisper. The exported
summary becomes a lantern string guiding collaborators toward thresholds that
shine and those needing renewed attention.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence


@dataclass
class CohortRecord:
    """Structured metrics for one analysis result file."""

    result_path: str
    domain: str
    dataset_path: Optional[str]
    theta: Optional[float]
    theta_ci: Optional[List[Optional[float]]]
    beta: Optional[float]
    beta_ci: Optional[List[Optional[float]]]
    logistic_r2: Optional[float]
    logistic_aic: Optional[float]
    best_null_model: Optional[str]
    best_null_aic: Optional[float]
    delta_aic: Optional[float]
    delta_r2: Optional[float]
    logistic_minus_best_r2: Optional[float]
    zeta_mean: Optional[float]
    threshold_crossed: Optional[bool]
    crossing_time: Optional[float]
    crossing_R: Optional[float]
    crossing_sigma: Optional[float]
    overshoot: Optional[float]
    zeta_at_crossing: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serialisable representation."""

        return asdict(self)


def _safe_float(value: Any) -> Optional[float]:
    """Convert ``value`` to float when possible, else return ``None``."""

    if value is None:
        return None
    try:
        if isinstance(value, (float, int)):
            return float(value)
        if isinstance(value, str) and value.strip():
            return float(value)
    except (TypeError, ValueError):
        return None
    return None


def _domain_from_dataset(dataset_path: Optional[str], fallback: str) -> str:
    """Infer the domain label from a dataset path or fallback name."""

    if dataset_path:
        dataset = Path(dataset_path)
        parts = dataset.parts
        if len(parts) >= 2 and parts[0] == "data":
            return parts[1]
        if parts:
            return parts[0]
    token = fallback.split("_")[0]
    return token or "unscoped"


def _ci_pair(entry: Mapping[str, Any]) -> Optional[List[Optional[float]]]:
    """Return a two-element list for a 95% confidence interval."""

    ci = entry.get("ci95")
    if isinstance(ci, (list, tuple)) and len(ci) >= 2:
        return [_safe_float(ci[0]), _safe_float(ci[1])]
    return None


def parse_result(result_path: Path) -> CohortRecord:
    """Parse a single JSON result file into a :class:`CohortRecord`."""

    with result_path.open("r", encoding="utf-8") as handle:
        payload: Mapping[str, Any] = json.load(handle)

    dataset_path = None
    dataset_info = payload.get("dataset")
    if isinstance(dataset_info, Mapping):
        path_value = dataset_info.get("path")
        if isinstance(path_value, str):
            dataset_path = path_value

    theta_info = payload.get("theta_estimate") if isinstance(payload.get("theta_estimate"), Mapping) else {}
    beta_info = payload.get("beta_estimate") if isinstance(payload.get("beta_estimate"), Mapping) else {}
    logistic_info = payload.get("logistic_model") if isinstance(payload.get("logistic_model"), Mapping) else {}
    null_models = payload.get("null_models") if isinstance(payload.get("null_models"), Mapping) else {}
    falsification = payload.get("falsification") if isinstance(payload.get("falsification"), Mapping) else {}
    comparisons = falsification.get("comparisons") if isinstance(falsification.get("comparisons"), Mapping) else {}
    membrane_info = payload.get("membrane") if isinstance(payload.get("membrane"), Mapping) else {}
    crossing_info = payload.get("threshold_crossing") if isinstance(payload.get("threshold_crossing"), Mapping) else {}

    best_null_model: Optional[str] = None
    best_delta_aic: Optional[float] = None
    best_delta_r2: Optional[float] = None
    for name, comp in comparisons.items():
        if not isinstance(comp, Mapping):
            continue
        delta_aic = _safe_float(comp.get("delta_aic"))
        if delta_aic is None:
            continue
        if best_delta_aic is None or delta_aic > best_delta_aic:
            best_delta_aic = delta_aic
            best_null_model = name
            best_delta_r2 = _safe_float(comp.get("delta_r2"))

    best_null_aic: Optional[float] = None
    best_null_r2: Optional[float] = None
    if best_null_model and isinstance(null_models.get(best_null_model), Mapping):
        candidate = null_models[best_null_model]
        best_null_aic = _safe_float(candidate.get("aic"))
        best_null_r2 = _safe_float(candidate.get("r2"))

    logistic_r2 = _safe_float(logistic_info.get("r2"))
    logistic_aic = _safe_float(logistic_info.get("aic"))
    logistic_minus_best_r2 = None
    if logistic_r2 is not None and best_null_r2 is not None:
        logistic_minus_best_r2 = logistic_r2 - best_null_r2

    threshold_crossed: Optional[bool] = None
    if isinstance(crossing_info, Mapping):
        crossed_value = crossing_info.get("crossed")
        if isinstance(crossed_value, bool):
            threshold_crossed = crossed_value
        elif crossed_value in (0, 1):
            threshold_crossed = bool(crossed_value)

    try:
        relative_path = result_path.relative_to(Path.cwd())
    except ValueError:
        relative_path = result_path

    return CohortRecord(
        result_path=str(relative_path),
        domain=_domain_from_dataset(dataset_path, result_path.stem),
        dataset_path=dataset_path,
        theta=_safe_float(theta_info.get("value")) if isinstance(theta_info, Mapping) else None,
        theta_ci=_ci_pair(theta_info) if isinstance(theta_info, Mapping) else None,
        beta=_safe_float(beta_info.get("value")) if isinstance(beta_info, Mapping) else None,
        beta_ci=_ci_pair(beta_info) if isinstance(beta_info, Mapping) else None,
        logistic_r2=logistic_r2,
        logistic_aic=logistic_aic,
        best_null_model=best_null_model,
        best_null_aic=best_null_aic,
        delta_aic=best_delta_aic,
        delta_r2=best_delta_r2,
        logistic_minus_best_r2=logistic_minus_best_r2,
        zeta_mean=_safe_float(membrane_info.get("zeta_mean")) if isinstance(membrane_info, Mapping) else None,
        threshold_crossed=threshold_crossed,
        crossing_time=_safe_float(crossing_info.get("crossing_time")) if isinstance(crossing_info, Mapping) else None,
        crossing_R=_safe_float(crossing_info.get("crossing_R")) if isinstance(crossing_info, Mapping) else None,
        crossing_sigma=_safe_float(crossing_info.get("crossing_sigma")) if isinstance(crossing_info, Mapping) else None,
        overshoot=_safe_float(crossing_info.get("overshoot")) if isinstance(crossing_info, Mapping) else None,
        zeta_at_crossing=_safe_float(crossing_info.get("zeta_at_crossing")) if isinstance(crossing_info, Mapping) else None,
    )


def _flatten_sequences(records: Iterable[Optional[float]]) -> List[float]:
    """Collect finite floats from an iterable, ignoring missing values."""

    values: List[float] = []
    for value in records:
        if value is None:
            continue
        numeric = _safe_float(value)
        if numeric is None or not math.isfinite(numeric):
            continue
        values.append(numeric)
    return values


def summarise_records(records: Sequence[CohortRecord]) -> Dict[str, Any]:
    """Compute aggregate statistics across the cohort."""

    theta_values = _flatten_sequences(record.theta for record in records)
    beta_values = _flatten_sequences(record.beta for record in records)
    logistic_r2_values = _flatten_sequences(record.logistic_r2 for record in records)
    delta_aic_values = _flatten_sequences(record.delta_aic for record in records)
    delta_r2_values = _flatten_sequences(record.delta_r2 for record in records)
    zeta_mean_values = _flatten_sequences(record.zeta_mean for record in records)

    def stats(series: List[float]) -> Optional[Dict[str, float]]:
        if not series:
            return None
        return {
            "mean": mean(series),
            "median": median(series),
            "min": min(series),
            "max": max(series),
        }

    domain_map: MutableMapping[str, List[CohortRecord]] = {}
    for record in records:
        domain_map.setdefault(record.domain, []).append(record)

    def crossing_stats(domain_records: Sequence[CohortRecord]) -> Dict[str, Any]:
        reporting = [
            r
            for r in domain_records
            if (
                r.threshold_crossed is not None
                or r.crossing_time is not None
                or r.overshoot is not None
            )
        ]
        reports = len(reporting)
        crossed_count = sum(1 for r in reporting if r.threshold_crossed)
        fraction = (crossed_count / reports) if reports else None
        return {
            "reports": reports,
            "crossed_count": crossed_count,
            "crossed_fraction": fraction,
            "time": stats(_flatten_sequences(r.crossing_time for r in reporting)),
            "R": stats(_flatten_sequences(r.crossing_R for r in reporting)),
            "sigma": stats(_flatten_sequences(r.crossing_sigma for r in reporting)),
            "overshoot": stats(_flatten_sequences(r.overshoot for r in reporting)),
            "zeta": stats(_flatten_sequences(r.zeta_at_crossing for r in reporting)),
        }

    domain_stats: Dict[str, Any] = {}
    for domain, domain_records in domain_map.items():
        domain_stats[domain] = {
            "count": len(domain_records),
            "delta_aic": stats(_flatten_sequences(r.delta_aic for r in domain_records)),
            "delta_r2": stats(_flatten_sequences(r.delta_r2 for r in domain_records)),
            "logistic_r2": stats(_flatten_sequences(r.logistic_r2 for r in domain_records)),
            "threshold_crossing": crossing_stats(domain_records),
        }

    crossing_summary = crossing_stats(records)

    return {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "cohort_size": len(records),
            "logistic_response": "sigma(beta * (R - Theta))",
        },
        "aggregate": {
            "theta": stats(theta_values),
            "beta": stats(beta_values),
            "logistic_r2": stats(logistic_r2_values),
            "delta_aic": stats(delta_aic_values),
            "delta_r2": stats(delta_r2_values),
            "zeta_mean": stats(zeta_mean_values),
            "threshold_crossing": crossing_summary,
        },
        "domains": domain_stats,
        "records": [record.to_dict() for record in records],
    }


def iter_result_files(sources: Sequence[Path]) -> List[Path]:
    """Return sorted JSON files from the supplied source directories."""

    files: List[Path] = []
    for source in sources:
        if source.is_file() and source.suffix == ".json":
            files.append(source)
            continue
        if not source.exists():
            continue
        for path in sorted(source.rglob("*.json")):
            files.append(path)
    # Deduplicate while preserving order
    seen: Dict[Path, None] = {}
    for path in files:
        seen.setdefault(path, None)
    return list(seen.keys())


def render_console_report(records: Sequence[CohortRecord]) -> None:
    """Print a concise textual roster of resonance metrics."""

    if not records:
        print("No resonance records discovered.\n")
        return

    sorted_records = sorted(
        records,
        key=lambda rec: rec.delta_aic if rec.delta_aic is not None else float("-inf"),
        reverse=True,
    )
    print("Cohort resonance roster (sorted by ΔAIC advantage):")
    for record in sorted_records:
        delta_aic = "–" if record.delta_aic is None else f"{record.delta_aic:.2f}"
        delta_r2 = "–" if record.delta_r2 is None else f"{record.delta_r2:.4f}"
        logistic_r2 = "–" if record.logistic_r2 is None else f"{record.logistic_r2:.4f}"
        best_null = record.best_null_model or "(none)"
        if record.threshold_crossed is True:
            crossing_note = (
                "crossed at t≈"
                f"{record.crossing_time:.2f}" if record.crossing_time is not None else "crossed"
            )
        elif record.threshold_crossed is False:
            crossing_note = "no crossing"
        elif record.crossing_time is not None:
            crossing_note = f"t≈{record.crossing_time:.2f}"
        else:
            crossing_note = "crossing n/a"
        print(
            f"  • {Path(record.result_path).name} [{record.domain}] — ΔAIC {delta_aic}, ΔR² {delta_r2}, "
            f"logistic R² {logistic_r2}, best null {best_null}, {crossing_note}"
        )
    print()


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entry point for the resonance cohort summariser."""

    parser = argparse.ArgumentParser(
        description="Summarise UTF resonance cohort statistics across analysis results."
    )
    parser.add_argument(
        "--sources",
        nargs="*",
        default=[Path(__file__).resolve().parent / "results"],
        type=Path,
        help="Directories or JSON files to ingest (default: analysis/results).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the cohort summary JSON.",
    )
    args = parser.parse_args(argv)

    source_paths = [path if path.is_absolute() else (Path.cwd() / path).resolve() for path in args.sources]
    result_files = iter_result_files(source_paths)

    output_path = args.output.resolve() if args.output else None
    if output_path is not None:
        result_files = [path for path in result_files if path.resolve() != output_path]

    records = [parse_result(path) for path in result_files]

    render_console_report(records)
    summary = summarise_records(records)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        print(f"Wrote cohort summary to {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
