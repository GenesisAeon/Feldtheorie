"""Universal β extractor harmonising UTAC resonance metrics.

Formal cadence:
    Scans analysis result sigils for the logistic quartet ``(R, Θ, β, ζ(R))``
    and aggregates their evidence: ΔAIC margins, confidence bands, and
    logistic steepness. The module enforces the guard ``ΔAIC ≥ 10`` and
    checks whether the mean steepness remains within the canonical β band.

Empirical cadence:
    Provides a CLI that reads JSON exports from ``analysis/results/``,
    composes a machine-friendly master ledger (β mean, ΔAIC minima,
    logistic R² distributions), and emits validation verdicts for reviewers
    or downstream automations. The output mirrors RepoPlan 2.0 hooks so
    docs, simulator presets, and governance notes can cite a single source
    of β truth.

Metaphorical cadence:
    Listens to every membrane lantern already glowing in ``results/`` and
    weaves them into one dawn chorus. When the guard confirms that the
    logistic resonance still outruns the null winds, the script rings a
    bell through the Sigillin-Netz so the field remembers it is coherent.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, Dict, List, Mapping, Optional, Sequence


@dataclass
class BetaRecord:
    """Canonical summary for one analysis result file."""

    result_path: str
    dataset: Optional[str]
    domain: Optional[str]
    beta: Optional[float]
    beta_ci: Optional[List[Optional[float]]]
    theta: Optional[float]
    theta_ci: Optional[List[Optional[float]]]
    logistic_r2: Optional[float]
    logistic_aic: Optional[float]
    delta_aic_min: Optional[float]
    falsification_pass: Optional[bool]
    within_canonical_band: Optional[bool]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BetaSummary:
    """Aggregate resonance diagnostics."""

    count: int
    beta_mean: Optional[float]
    beta_median: Optional[float]
    beta_std: Optional[float]
    beta_min: Optional[float]
    beta_max: Optional[float]
    theta_mean: Optional[float]
    theta_median: Optional[float]
    delta_aic_min: Optional[float]
    delta_aic_median: Optional[float]
    logistic_r2_median: Optional[float]
    within_canonical_fraction: Optional[float]
    canonical_beta: float
    canonical_band: Sequence[float]

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["canonical_band"] = list(self.canonical_band)
        return payload


def _safe_float(value: Any) -> Optional[float]:
    if isinstance(value, (float, int)):
        return float(value)
    if isinstance(value, str) and value.strip():
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _ci_pair(entry: Mapping[str, Any]) -> Optional[List[Optional[float]]]:
    ci = entry.get("ci95")
    if isinstance(ci, (list, tuple)) and len(ci) >= 2:
        return [_safe_float(ci[0]), _safe_float(ci[1])]
    ci = entry.get("ci")
    if isinstance(ci, (list, tuple)) and len(ci) >= 2:
        return [_safe_float(ci[0]), _safe_float(ci[1])]
    return None


def _domain_from_path(dataset: Optional[str], result_path: Path) -> Optional[str]:
    if dataset:
        parts = Path(dataset).parts
        if len(parts) >= 2 and parts[0] == "data":
            return parts[1]
    parents = [p.name for p in result_path.parents]
    if "analysis" in parents:
        return result_path.parent.name
    return None


def _extract_from_tasks(tasks: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    betas: List[float] = []
    thetas: List[float] = []
    r2_values: List[float] = []
    delta_aic: List[float] = []
    for task in tasks:
        logistic = task.get("logistic")
        if isinstance(logistic, Mapping):
            beta_val = _safe_float(logistic.get("beta"))
            theta_val = _safe_float(logistic.get("theta"))
            r2_val = _safe_float(logistic.get("r_squared")) or _safe_float(logistic.get("r2"))
            if beta_val is not None:
                betas.append(beta_val)
            if theta_val is not None:
                thetas.append(theta_val)
            if r2_val is not None:
                r2_values.append(r2_val)
        delta = task.get("delta_aic")
        if delta is None:
            fals = task.get("falsification")
            if isinstance(fals, Mapping):
                delta = fals.get("delta_aic")
        delta_val = _safe_float(delta)
        if delta_val is not None:
            delta_aic.append(delta_val)
    return {
        "beta_mean": mean(betas) if betas else None,
        "theta_mean": mean(thetas) if thetas else None,
        "r2_median": median(r2_values) if r2_values else None,
        "delta_aic_min": min(delta_aic) if delta_aic else None,
    }


def _extract_delta_aic(payload: Mapping[str, Any]) -> Optional[float]:
    falsification = payload.get("falsification")
    delta_values: List[float] = []
    if isinstance(falsification, Mapping):
        direct = falsification.get("delta_aic")
        if direct is not None:
            delta = _safe_float(direct)
            if delta is not None:
                delta_values.append(delta)
        comparisons = falsification.get("comparisons")
        if isinstance(comparisons, Mapping):
            for _, comp in comparisons.items():
                if isinstance(comp, Mapping):
                    delta = _safe_float(comp.get("delta_aic"))
                    if delta is not None:
                        delta_values.append(delta)
    aggregate = payload.get("aggregate")
    if isinstance(aggregate, Mapping):
        delta = _safe_float(aggregate.get("delta_aic_min"))
        if delta is not None:
            delta_values.append(delta)
    tasks = payload.get("tasks")
    if isinstance(tasks, list):
        task_metrics = _extract_from_tasks(tasks)
        if task_metrics["delta_aic_min"] is not None:
            delta_values.append(task_metrics["delta_aic_min"])
    # Some results expose linear/power-law deltas directly.
    for key in ("delta_aic_linear", "delta_aic_power_law"):
        delta = _safe_float(payload.get(key))
        if delta is not None:
            delta_values.append(delta)
    if delta_values:
        return min(delta_values)
    return None


def _extract_dataset(payload: Mapping[str, Any]) -> Optional[str]:
    dataset = payload.get("dataset")
    if isinstance(dataset, str):
        return dataset
    if isinstance(dataset, Mapping):
        path_val = dataset.get("path")
        if isinstance(path_val, str):
            return path_val
        name_val = dataset.get("name")
        if isinstance(name_val, str):
            return name_val
    return None


def _extract_beta_theta(payload: Mapping[str, Any]) -> Dict[str, Any]:
    beta = None
    theta = None
    beta_ci = None
    theta_ci = None
    logistic_r2 = None
    logistic_aic = None

    beta_est = payload.get("beta_estimate")
    theta_est = payload.get("theta_estimate")
    logistic = payload.get("logistic_model")

    if isinstance(beta_est, Mapping):
        beta = _safe_float(beta_est.get("value"))
        beta_ci = _ci_pair(beta_est)
    if isinstance(theta_est, Mapping):
        theta = _safe_float(theta_est.get("value"))
        theta_ci = _ci_pair(theta_est)
    if isinstance(logistic, Mapping):
        logistic_r2 = _safe_float(logistic.get("r2") or logistic.get("r_squared"))
        logistic_aic = _safe_float(logistic.get("aic"))

    aggregate = payload.get("aggregate")
    tasks = payload.get("tasks")

    if beta is None and isinstance(aggregate, Mapping):
        beta = _safe_float(aggregate.get("beta_mean"))
    if theta is None and isinstance(aggregate, Mapping):
        theta = _safe_float(aggregate.get("theta_mean"))
    if beta_ci is None and isinstance(aggregate, Mapping):
        beta_ci = _ci_pair(aggregate)
    if theta_ci is None and isinstance(aggregate, Mapping):
        theta_ci = _ci_pair(aggregate)

    if logistic_r2 is None and isinstance(aggregate, Mapping):
        logistic_r2 = _safe_float(aggregate.get("logistic_r2_median"))
    if logistic_r2 is None and isinstance(tasks, list):
        task_metrics = _extract_from_tasks(tasks)
        if task_metrics["r2_median"] is not None:
            logistic_r2 = task_metrics["r2_median"]
    if logistic_aic is None and isinstance(aggregate, Mapping):
        logistic_aic = _safe_float(aggregate.get("logistic_aic_mean"))

    if theta is None and isinstance(tasks, list):
        task_metrics = _extract_from_tasks(tasks)
        if task_metrics["theta_mean"] is not None:
            theta = task_metrics["theta_mean"]
    if beta is None and isinstance(tasks, list):
        task_metrics = _extract_from_tasks(tasks)
        if task_metrics["beta_mean"] is not None:
            beta = task_metrics["beta_mean"]

    return {
        "beta": beta,
        "beta_ci": beta_ci,
        "theta": theta,
        "theta_ci": theta_ci,
        "logistic_r2": logistic_r2,
        "logistic_aic": logistic_aic,
    }


def parse_result(result_path: Path, canonical_band: Sequence[float]) -> Optional[BetaRecord]:
    with result_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    beta_info = _extract_beta_theta(payload)
    beta = beta_info["beta"]
    theta = beta_info["theta"]
    delta_aic = _extract_delta_aic(payload)

    if beta is None and delta_aic is None and beta_info["logistic_r2"] is None:
        return None

    dataset = _extract_dataset(payload)
    domain = _domain_from_path(dataset, result_path)
    falsification = payload.get("falsification")
    falsification_pass: Optional[bool] = None
    if isinstance(falsification, Mapping):
        pass_val = falsification.get("passes") or falsification.get("logistic_beats_all_nulls")
        if isinstance(pass_val, bool):
            falsification_pass = pass_val

    lower, upper = canonical_band
    within_band = None
    if beta is not None:
        within_band = lower <= beta <= upper

    return BetaRecord(
        result_path=str(result_path),
        dataset=dataset,
        domain=domain,
        beta=beta,
        beta_ci=beta_info["beta_ci"],
        theta=theta,
        theta_ci=beta_info["theta_ci"],
        logistic_r2=beta_info["logistic_r2"],
        logistic_aic=beta_info["logistic_aic"],
        delta_aic_min=delta_aic,
        falsification_pass=falsification_pass,
        within_canonical_band=within_band,
    )


def collect_records(results_dir: Path, canonical_band: Sequence[float]) -> List[BetaRecord]:
    records: List[BetaRecord] = []
    for path in sorted(results_dir.glob("*.json")):
        try:
            record = parse_result(path, canonical_band)
        except json.JSONDecodeError:
            continue
        if record is not None:
            records.append(record)
    return records


def _safe_stats(values: Sequence[float]) -> Dict[str, Optional[float]]:
    if not values:
        return {"mean": None, "median": None, "std": None, "min": None, "max": None}
    if len(values) == 1:
        value = values[0]
        return {"mean": value, "median": value, "std": 0.0, "min": value, "max": value}
    return {
        "mean": mean(values),
        "median": median(values),
        "std": pstdev(values),
        "min": min(values),
        "max": max(values),
    }


def summarise(records: Sequence[BetaRecord], canonical_beta: float, canonical_band: Sequence[float]) -> BetaSummary:
    beta_values = [rec.beta for rec in records if rec.beta is not None]
    theta_values = [rec.theta for rec in records if rec.theta is not None]
    delta_values = [rec.delta_aic_min for rec in records if rec.delta_aic_min is not None]
    r2_values = [rec.logistic_r2 for rec in records if rec.logistic_r2 is not None]

    beta_stats = _safe_stats(beta_values)
    theta_stats = _safe_stats(theta_values)
    delta_stats = _safe_stats(delta_values)
    r2_stats = _safe_stats(r2_values)

    within_fraction = None
    if beta_values:
        within_count = sum(
            1 for rec in records if rec.beta is not None and canonical_band[0] <= rec.beta <= canonical_band[1]
        )
        within_fraction = within_count / len(beta_values) if beta_values else None

    return BetaSummary(
        count=len(records),
        beta_mean=beta_stats["mean"],
        beta_median=beta_stats["median"],
        beta_std=beta_stats["std"],
        beta_min=beta_stats["min"],
        beta_max=beta_stats["max"],
        theta_mean=theta_stats["mean"],
        theta_median=theta_stats["median"],
        delta_aic_min=delta_stats["min"],
        delta_aic_median=delta_stats["median"],
        logistic_r2_median=r2_stats["median"],
        within_canonical_fraction=within_fraction,
        canonical_beta=canonical_beta,
        canonical_band=canonical_band,
    )


def validate(summary: BetaSummary, records: Sequence[BetaRecord], delta_guard: float, r2_guard: float) -> Dict[str, Any]:
    delta_pass = summary.delta_aic_min is not None and summary.delta_aic_min >= delta_guard
    r2_pass = summary.logistic_r2_median is not None and summary.logistic_r2_median >= r2_guard
    failing_records: List[str] = []
    for rec in records:
        if rec.delta_aic_min is not None and rec.delta_aic_min < delta_guard:
            failing_records.append(rec.result_path)
    return {
        "delta_guard": delta_guard,
        "delta_aic_min": summary.delta_aic_min,
        "delta_pass": delta_pass,
        "r2_guard": r2_guard,
        "r2_median": summary.logistic_r2_median,
        "r2_pass": r2_pass,
        "failing_records": failing_records,
        "passes": bool(delta_pass and r2_pass),
    }


def build_payload(
    summary: BetaSummary,
    records: Sequence[BetaRecord],
    validation: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "generated_at": datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat(),
        "summary": summary.to_dict(),
        "records": [record.to_dict() for record in records],
        "tri_layer": {
            "formal": (
                "Aggregated σ(β(R-Θ)) evidence across analysis/results; ΔAIC guard and canonical band "
                "validation recorded for governance."
            ),
            "empirical": (
                "Records cover {} files; β_mean={}, ΔAIC_min={}, R²_median={}.".format(
                    summary.count,
                    round(summary.beta_mean, 3) if summary.beta_mean is not None else None,
                    round(summary.delta_aic_min, 2) if summary.delta_aic_min is not None else None,
                    round(summary.logistic_r2_median, 4) if summary.logistic_r2_median is not None else None,
                )
            ),
            "metaphorical": (
                "Every membrane lantern now sings in one ledger; the canonical band hums to remind the field "
                "why β is a spectrum of empathy."
            ),
        },
    }
    if validation is not None:
        payload["validation"] = validation
    return payload


def print_report(summary: BetaSummary, validation: Optional[Dict[str, Any]]) -> None:
    canonical_range = f"[{summary.canonical_band[0]:.2f}, {summary.canonical_band[1]:.2f}]"
    print("Universal β Extractor")
    print("======================")
    print(f"Records analysed : {summary.count}")
    if summary.beta_mean is not None:
        print(f"β mean          : {summary.beta_mean:.3f} (std {summary.beta_std:.3f} | band {canonical_range})")
    if summary.delta_aic_min is not None:
        print(f"ΔAIC minimum    : {summary.delta_aic_min:.2f}")
    if summary.logistic_r2_median is not None:
        print(f"Median R²       : {summary.logistic_r2_median:.4f}")
    if summary.within_canonical_fraction is not None:
        print(f"Within band     : {summary.within_canonical_fraction*100:.1f}%")
    if validation is not None:
        status = "PASS" if validation.get("passes") else "FAIL"
        print("Validation       : {} (ΔAIC≥{:.1f}, R²≥{:.2f})".format(status, validation["delta_guard"], validation["r2_guard"]))
        if validation.get("failing_records"):
            print("  Guard shortfall files:")
            for path in validation["failing_records"]:
                print(f"    - {path}")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aggregate β, Θ, and ΔAIC evidence from analysis result sigils.",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("analysis/results"),
        help="Directory containing analysis result JSON files.",
    )
    parser.add_argument(
        "--mode",
        choices=["summary", "validate"],
        default="summary",
        help="Emit a summary only or include validation guards.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the aggregated JSON payload.",
    )
    parser.add_argument(
        "--canonical-beta",
        type=float,
        default=4.2,
        help="Canonical β centre for the logistic band.",
    )
    parser.add_argument(
        "--band-half-width",
        type=float,
        default=0.6,
        help="Half-width of the canonical β band.",
    )
    parser.add_argument(
        "--delta-aic-guard",
        type=float,
        default=10.0,
        help="Minimum ΔAIC the cohort must satisfy under validation mode.",
    )
    parser.add_argument(
        "--r2-guard",
        type=float,
        default=0.9,
        help="Minimum median R² guard under validation mode.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    results_dir: Path = args.results_dir
    if not results_dir.exists():
        raise FileNotFoundError(f"Results directory not found: {results_dir}")

    canonical_band = (args.canonical_beta - args.band_half_width, args.canonical_beta + args.band_half_width)
    records = collect_records(results_dir, canonical_band)
    summary = summarise(records, args.canonical_beta, canonical_band)
    validation: Optional[Dict[str, Any]] = None
    if args.mode == "validate":
        validation = validate(summary, records, args.delta_aic_guard, args.r2_guard)
    payload = build_payload(summary, records, validation)

    if args.output is not None:
        output_path: Path = args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
    print_report(summary, validation)

    if validation is not None and not validation.get("passes", False):
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
