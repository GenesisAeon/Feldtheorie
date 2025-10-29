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
    sigma_fraction_above_half: Optional[float]
    meta_gate_fraction_above_half: Optional[float]
    meta_gate_mean: Optional[float]
    theta_drift_total: Optional[float]
    beta_drift_total: Optional[float]
    gate_area: Optional[float]
    impedance_area: Optional[float]
    relief_area: Optional[float]
    recovery_area: Optional[float]
    hysteresis_area: Optional[float]
    relief_recovery_balance: Optional[float]
    relief_recovery_ratio: Optional[float]
    relief_recovery_symmetry: Optional[float]
    hysteresis_bias: Optional[float]
    relief_peak: Optional[float]
    recovery_peak: Optional[float]
    hysteresis_peak: Optional[float]
    relief_mean: Optional[float]
    recovery_mean: Optional[float]
    hysteresis_mean: Optional[float]
    relief_min: Optional[float]
    recovery_min: Optional[float]
    hysteresis_min: Optional[float]
    final_impedance: Optional[float]
    baseline_impedance: Optional[float]
    boundary_flux_mean: Optional[float]
    boundary_flux_std: Optional[float]
    boundary_flux_peak: Optional[float]
    boundary_flux_valley: Optional[float]
    boundary_gate_mean: Optional[float]
    boundary_gate_peak: Optional[float]
    boundary_gate_valley: Optional[float]

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
    logistic_fit = payload.get("logistic_fit") if isinstance(payload.get("logistic_fit"), Mapping) else {}
    meta_threshold = payload.get("meta_threshold") if isinstance(payload.get("meta_threshold"), Mapping) else {}
    null_models = payload.get("null_models") if isinstance(payload.get("null_models"), Mapping) else {}
    falsification = payload.get("falsification") if isinstance(payload.get("falsification"), Mapping) else {}
    comparisons = falsification.get("comparisons") if isinstance(falsification.get("comparisons"), Mapping) else {}
    membrane_info = payload.get("membrane") if isinstance(payload.get("membrane"), Mapping) else {}
    impedance_candidates: list[Mapping[str, Any]] = []
    raw_impedance = payload.get("impedance")
    if isinstance(raw_impedance, Mapping):
        impedance_candidates.append(raw_impedance)
    raw_impedance_diag = payload.get("impedance_diagnostics")
    if isinstance(raw_impedance_diag, Mapping):
        impedance_candidates.insert(0, raw_impedance_diag)
    impedance_info: Mapping[str, Any] = {}
    for candidate in impedance_candidates:
        impedance_info = candidate
        if "relief_peak" in candidate or "impedance_area" in candidate:
            break
    crossing_info = payload.get("threshold_crossing") if isinstance(payload.get("threshold_crossing"), Mapping) else {}
    boundary_info = payload.get("boundary") if isinstance(payload.get("boundary"), Mapping) else {}
    meta_gate_payload = payload.get("meta_gate")
    if isinstance(meta_gate_payload, Mapping):
        meta_gate_info: Mapping[str, Any] = meta_gate_payload
    elif isinstance(logistic_fit, Mapping) and isinstance(logistic_fit.get("meta_gate"), Mapping):
        meta_gate_info = logistic_fit["meta_gate"]  # type: ignore[assignment]
    elif isinstance(meta_threshold, Mapping) and isinstance(meta_threshold.get("meta_gate"), Mapping):
        meta_gate_info = meta_threshold["meta_gate"]  # type: ignore[assignment]
    else:
        meta_gate_info = {}

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

    def _fraction_above_half(series: Any) -> Optional[float]:
        if not isinstance(series, Sequence) or isinstance(series, (str, bytes)):
            return None
        values = []
        for item in series:
            numeric = _safe_float(item)
            if numeric is None or not math.isfinite(numeric):
                continue
            values.append(numeric)
        if not values:
            return None
        count = sum(1 for value in values if value >= 0.5)
        return count / len(values)

    sigma_fraction_above_half = _safe_float(logistic_fit.get("fraction_above_half")) if isinstance(logistic_fit, Mapping) else None
    if sigma_fraction_above_half is None:
        sigma_fraction_above_half = _fraction_above_half(logistic_fit.get("sigma_hat")) if isinstance(logistic_fit, Mapping) else None

    theta_drift_total = _safe_float(logistic_fit.get("theta_drift_total")) if isinstance(logistic_fit, Mapping) else None
    beta_drift_total = _safe_float(logistic_fit.get("beta_drift_total")) if isinstance(logistic_fit, Mapping) else None
    if theta_drift_total is None and isinstance(meta_threshold, Mapping):
        theta_drift_total = _safe_float(meta_threshold.get("theta_drift_total"))
    if beta_drift_total is None and isinstance(meta_threshold, Mapping):
        beta_drift_total = _safe_float(meta_threshold.get("beta_drift_total"))

    meta_gate_fraction_above_half = _safe_float(meta_gate_info.get("fraction_above_half")) if isinstance(meta_gate_info, Mapping) else None
    if meta_gate_fraction_above_half is None:
        meta_gate_fraction_above_half = _fraction_above_half(meta_gate_info.get("series")) if isinstance(meta_gate_info, Mapping) else None

    meta_gate_mean = None
    if isinstance(meta_gate_info, Mapping):
        stats_block = meta_gate_info.get("stats")
        if isinstance(stats_block, Mapping):
            meta_gate_mean = _safe_float(stats_block.get("mean"))

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
        sigma_fraction_above_half=sigma_fraction_above_half,
        meta_gate_fraction_above_half=meta_gate_fraction_above_half,
        meta_gate_mean=meta_gate_mean,
        theta_drift_total=theta_drift_total,
        beta_drift_total=beta_drift_total,
        gate_area=_safe_float(impedance_info.get("gate_area")) if isinstance(impedance_info, Mapping) else None,
        impedance_area=_safe_float(impedance_info.get("impedance_area")) if isinstance(impedance_info, Mapping) else None,
        relief_area=_safe_float(impedance_info.get("relief_area")) if isinstance(impedance_info, Mapping) else None,
        recovery_area=_safe_float(impedance_info.get("recovery_area")) if isinstance(impedance_info, Mapping) else None,
        hysteresis_area=_safe_float(impedance_info.get("hysteresis_area")) if isinstance(impedance_info, Mapping) else None,
        relief_recovery_balance=_safe_float(impedance_info.get("relief_recovery_balance"))
        if isinstance(impedance_info, Mapping)
        else None,
        relief_recovery_ratio=_safe_float(impedance_info.get("relief_recovery_ratio"))
        if isinstance(impedance_info, Mapping)
        else None,
        relief_recovery_symmetry=_safe_float(impedance_info.get("relief_recovery_symmetry"))
        if isinstance(impedance_info, Mapping)
        else None,
        hysteresis_bias=_safe_float(impedance_info.get("hysteresis_bias")) if isinstance(impedance_info, Mapping) else None,
        relief_peak=_safe_float(impedance_info.get("relief_peak")) if isinstance(impedance_info, Mapping) else None,
        recovery_peak=_safe_float(impedance_info.get("recovery_peak")) if isinstance(impedance_info, Mapping) else None,
        hysteresis_peak=_safe_float(impedance_info.get("hysteresis_peak")) if isinstance(impedance_info, Mapping) else None,
        relief_mean=_safe_float(impedance_info.get("relief_mean")) if isinstance(impedance_info, Mapping) else None,
        recovery_mean=_safe_float(impedance_info.get("recovery_mean")) if isinstance(impedance_info, Mapping) else None,
        hysteresis_mean=_safe_float(impedance_info.get("hysteresis_mean")) if isinstance(impedance_info, Mapping) else None,
        relief_min=_safe_float(impedance_info.get("relief_min")) if isinstance(impedance_info, Mapping) else None,
        recovery_min=_safe_float(impedance_info.get("recovery_min")) if isinstance(impedance_info, Mapping) else None,
        hysteresis_min=_safe_float(impedance_info.get("hysteresis_min")) if isinstance(impedance_info, Mapping) else None,
        final_impedance=_safe_float(impedance_info.get("final_impedance")) if isinstance(impedance_info, Mapping) else None,
        baseline_impedance=_safe_float(impedance_info.get("baseline_impedance")) if isinstance(impedance_info, Mapping) else None,
        boundary_flux_mean=_safe_float(boundary_info.get("boundary_flux_mean")) if isinstance(boundary_info, Mapping) else None,
        boundary_flux_std=_safe_float(boundary_info.get("boundary_flux_std")) if isinstance(boundary_info, Mapping) else None,
        boundary_flux_peak=_safe_float(boundary_info.get("boundary_flux_peak")) if isinstance(boundary_info, Mapping) else None,
        boundary_flux_valley=_safe_float(boundary_info.get("boundary_flux_valley")) if isinstance(boundary_info, Mapping) else None,
        boundary_gate_mean=_safe_float(boundary_info.get("boundary_gate_mean")) if isinstance(boundary_info, Mapping) else None,
        boundary_gate_peak=_safe_float(boundary_info.get("boundary_gate_peak")) if isinstance(boundary_info, Mapping) else None,
        boundary_gate_valley=_safe_float(boundary_info.get("boundary_gate_valley")) if isinstance(boundary_info, Mapping) else None,
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
    sigma_fraction_values = _flatten_sequences(record.sigma_fraction_above_half for record in records)
    meta_gate_fraction_values = _flatten_sequences(record.meta_gate_fraction_above_half for record in records)
    meta_gate_mean_values = _flatten_sequences(record.meta_gate_mean for record in records)
    theta_drift_totals = _flatten_sequences(record.theta_drift_total for record in records)
    beta_drift_totals = _flatten_sequences(record.beta_drift_total for record in records)
    gate_area_values = _flatten_sequences(record.gate_area for record in records)
    impedance_area_values = _flatten_sequences(record.impedance_area for record in records)
    relief_area_values = _flatten_sequences(record.relief_area for record in records)
    recovery_area_values = _flatten_sequences(record.recovery_area for record in records)
    hysteresis_area_values = _flatten_sequences(record.hysteresis_area for record in records)
    relief_recovery_balance_values = _flatten_sequences(
        record.relief_recovery_balance for record in records
    )
    relief_recovery_ratio_values = _flatten_sequences(
        record.relief_recovery_ratio for record in records
    )
    relief_recovery_symmetry_values = _flatten_sequences(
        record.relief_recovery_symmetry for record in records
    )
    hysteresis_bias_values = _flatten_sequences(record.hysteresis_bias for record in records)
    relief_peak_values = _flatten_sequences(record.relief_peak for record in records)
    recovery_peak_values = _flatten_sequences(record.recovery_peak for record in records)
    hysteresis_peak_values = _flatten_sequences(record.hysteresis_peak for record in records)
    relief_mean_values = _flatten_sequences(record.relief_mean for record in records)
    recovery_mean_values = _flatten_sequences(record.recovery_mean for record in records)
    hysteresis_mean_values = _flatten_sequences(record.hysteresis_mean for record in records)
    relief_min_values = _flatten_sequences(record.relief_min for record in records)
    recovery_min_values = _flatten_sequences(record.recovery_min for record in records)
    hysteresis_min_values = _flatten_sequences(record.hysteresis_min for record in records)
    final_impedance_values = _flatten_sequences(record.final_impedance for record in records)
    baseline_impedance_values = _flatten_sequences(record.baseline_impedance for record in records)
    boundary_flux_mean_values = _flatten_sequences(record.boundary_flux_mean for record in records)
    boundary_flux_std_values = _flatten_sequences(record.boundary_flux_std for record in records)
    boundary_flux_peak_values = _flatten_sequences(record.boundary_flux_peak for record in records)
    boundary_flux_valley_values = _flatten_sequences(record.boundary_flux_valley for record in records)
    boundary_gate_mean_values = _flatten_sequences(record.boundary_gate_mean for record in records)
    boundary_gate_peak_values = _flatten_sequences(record.boundary_gate_peak for record in records)
    boundary_gate_valley_values = _flatten_sequences(record.boundary_gate_valley for record in records)

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
            "sigma_fraction_above_half": stats(
                _flatten_sequences(r.sigma_fraction_above_half for r in domain_records)
            ),
            "meta_gate_fraction_above_half": stats(
                _flatten_sequences(r.meta_gate_fraction_above_half for r in domain_records)
            ),
            "meta_gate_mean": stats(
                _flatten_sequences(r.meta_gate_mean for r in domain_records)
            ),
            "theta_drift_total": stats(
                _flatten_sequences(r.theta_drift_total for r in domain_records)
            ),
            "beta_drift_total": stats(
                _flatten_sequences(r.beta_drift_total for r in domain_records)
            ),
            "gate_area": stats(_flatten_sequences(r.gate_area for r in domain_records)),
            "impedance_area": stats(
                _flatten_sequences(r.impedance_area for r in domain_records)
            ),
            "relief_area": stats(_flatten_sequences(r.relief_area for r in domain_records)),
            "recovery_area": stats(
                _flatten_sequences(r.recovery_area for r in domain_records)
            ),
            "hysteresis_area": stats(
                _flatten_sequences(r.hysteresis_area for r in domain_records)
            ),
            "relief_recovery_balance": stats(
                _flatten_sequences(r.relief_recovery_balance for r in domain_records)
            ),
            "relief_recovery_ratio": stats(
                _flatten_sequences(r.relief_recovery_ratio for r in domain_records)
            ),
            "relief_recovery_symmetry": stats(
                _flatten_sequences(r.relief_recovery_symmetry for r in domain_records)
            ),
            "hysteresis_bias": stats(
                _flatten_sequences(r.hysteresis_bias for r in domain_records)
            ),
            "relief_peak": stats(_flatten_sequences(r.relief_peak for r in domain_records)),
            "recovery_peak": stats(
                _flatten_sequences(r.recovery_peak for r in domain_records)
            ),
            "hysteresis_peak": stats(
                _flatten_sequences(r.hysteresis_peak for r in domain_records)
            ),
            "relief_mean": stats(_flatten_sequences(r.relief_mean for r in domain_records)),
            "recovery_mean": stats(
                _flatten_sequences(r.recovery_mean for r in domain_records)
            ),
            "hysteresis_mean": stats(
                _flatten_sequences(r.hysteresis_mean for r in domain_records)
            ),
            "relief_min": stats(_flatten_sequences(r.relief_min for r in domain_records)),
            "recovery_min": stats(
                _flatten_sequences(r.recovery_min for r in domain_records)
            ),
            "hysteresis_min": stats(
                _flatten_sequences(r.hysteresis_min for r in domain_records)
            ),
            "final_impedance": stats(
                _flatten_sequences(r.final_impedance for r in domain_records)
            ),
            "baseline_impedance": stats(
                _flatten_sequences(r.baseline_impedance for r in domain_records)
            ),
            "boundary_flux_mean": stats(
                _flatten_sequences(r.boundary_flux_mean for r in domain_records)
            ),
            "boundary_flux_std": stats(
                _flatten_sequences(r.boundary_flux_std for r in domain_records)
            ),
            "boundary_flux_peak": stats(
                _flatten_sequences(r.boundary_flux_peak for r in domain_records)
            ),
            "boundary_flux_valley": stats(
                _flatten_sequences(r.boundary_flux_valley for r in domain_records)
            ),
            "boundary_gate_mean": stats(
                _flatten_sequences(r.boundary_gate_mean for r in domain_records)
            ),
            "boundary_gate_peak": stats(
                _flatten_sequences(r.boundary_gate_peak for r in domain_records)
            ),
            "boundary_gate_valley": stats(
                _flatten_sequences(r.boundary_gate_valley for r in domain_records)
            ),
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
            "sigma_fraction_above_half": stats(sigma_fraction_values),
            "meta_gate_fraction_above_half": stats(meta_gate_fraction_values),
            "meta_gate_mean": stats(meta_gate_mean_values),
            "theta_drift_total": stats(theta_drift_totals),
            "beta_drift_total": stats(beta_drift_totals),
            "gate_area": stats(gate_area_values),
            "impedance_area": stats(impedance_area_values),
            "relief_area": stats(relief_area_values),
            "recovery_area": stats(recovery_area_values),
            "hysteresis_area": stats(hysteresis_area_values),
            "relief_recovery_balance": stats(relief_recovery_balance_values),
            "relief_recovery_ratio": stats(relief_recovery_ratio_values),
            "relief_recovery_symmetry": stats(relief_recovery_symmetry_values),
            "hysteresis_bias": stats(hysteresis_bias_values),
            "relief_peak": stats(relief_peak_values),
            "recovery_peak": stats(recovery_peak_values),
            "hysteresis_peak": stats(hysteresis_peak_values),
            "relief_mean": stats(relief_mean_values),
            "recovery_mean": stats(recovery_mean_values),
            "hysteresis_mean": stats(hysteresis_mean_values),
            "relief_min": stats(relief_min_values),
            "recovery_min": stats(recovery_min_values),
            "hysteresis_min": stats(hysteresis_min_values),
            "final_impedance": stats(final_impedance_values),
            "baseline_impedance": stats(baseline_impedance_values),
            "boundary_flux_mean": stats(boundary_flux_mean_values),
            "boundary_flux_std": stats(boundary_flux_std_values),
            "boundary_flux_peak": stats(boundary_flux_peak_values),
            "boundary_flux_valley": stats(boundary_flux_valley_values),
            "boundary_gate_mean": stats(boundary_gate_mean_values),
            "boundary_gate_peak": stats(boundary_gate_peak_values),
            "boundary_gate_valley": stats(boundary_gate_valley_values),
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
        extras = []
        if record.sigma_fraction_above_half is not None:
            extras.append(f"σ>½ {record.sigma_fraction_above_half:.2f}")
        if record.meta_gate_fraction_above_half is not None:
            extras.append(f"meta>½ {record.meta_gate_fraction_above_half:.2f}")
        drift_tokens = []
        if record.theta_drift_total is not None:
            drift_tokens.append(f"ΔΘ {record.theta_drift_total:.2f}")
        if record.beta_drift_total is not None:
            drift_tokens.append(f"Δβ {record.beta_drift_total:.2f}")
        if drift_tokens:
            extras.append(" ".join(drift_tokens))
        if record.meta_gate_mean is not None:
            extras.append(f"meta μ {record.meta_gate_mean:.2f}")
        if record.zeta_mean is not None:
            extras.append(f"ζ μ {record.zeta_mean:.2f}")
        if record.boundary_flux_mean is not None:
            extras.append(f"Robin flux μ {record.boundary_flux_mean:+.2f}")
        if record.boundary_gate_mean is not None:
            extras.append(f"Robin gate μ {record.boundary_gate_mean:.2f}")
        if record.relief_peak is not None:
            extras.append(f"relief↑ {record.relief_peak:.2f}")
        if record.recovery_peak is not None:
            extras.append(f"recovery↑ {record.recovery_peak:.2f}")
        if record.hysteresis_peak is not None:
            extras.append(f"hys↑ {record.hysteresis_peak:.2f}")
        if record.relief_recovery_ratio is not None:
            extras.append(f"rel/rec {record.relief_recovery_ratio:.2f}")
        if record.relief_recovery_symmetry is not None:
            extras.append(f"sym {record.relief_recovery_symmetry:+.2f}")
        if record.hysteresis_bias is not None:
            extras.append(f"hysΔ {record.hysteresis_bias:+.2f}")
        extras_note = f", {'; '.join(extras)}" if extras else ""
        print(
            f"  • {Path(record.result_path).name} [{record.domain}] — ΔAIC {delta_aic}, ΔR² {delta_r2}, "
            f"logistic R² {logistic_r2}, best null {best_null}, {crossing_note}{extras_note}"
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
