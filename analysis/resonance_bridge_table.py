r"""Resonance bridge table generator weaving cross-domain logistic diagnostics.

Formal layer:
    Aggregates `analysis/results/*.json` files carrying the quartet
    $(R, \Theta, \beta, \zeta(R))$ into a consolidated ledger.  For each
    membrane it reports threshold estimates, logistic $R^2$, AIC, and the
    strongest falsification gap against smooth null models.  The script
    exports a JSON summary and an optional Markdown table so downstream
    modules can ingest a harmonised resonance bridge.

Empirical layer:
    Designed for command-line execution.  Reads JSON exports produced by
    fit pipelines (e.g. `resonance_fit_pipeline.py`, domain-specific fits),
    filters out artefacts that lack threshold estimates, and computes
    cohort-wide statistics (counts per domain, median $\Delta\mathrm{AIC}$,
    logistic $R^2$ ranges).  Results are serialised to
    `analysis/results/resonance_bridge_table.json` and can be mirrored into
    `analysis/reports/resonance_bridge_table.md` for human-readable audits.

Metaphorical layer:
    Treats the collection as a lantern bridge: each dataset is a torch
    whose logistic dawn outshines null-model lullabies.  By threading the
    table we hear how bees, black holes, neural gates, and learning models
    share the same auroral membrane once $R$ crosses $\Theta$.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "analysis" / "results"
REPORTS_DIR = ROOT / "analysis" / "reports"


@dataclass
class BridgeEntry:
    """Container for a single resonance ledger row."""

    result_file: str
    domain: str
    dataset: str
    theta: float | None
    theta_ci: Sequence[float] | None
    beta: float | None
    beta_ci: Sequence[float] | None
    logistic_r2: float | None
    logistic_aic: float | None
    best_null: str | None
    delta_aic: float | None
    delta_r2: float | None
    zeta_mean: float | None
    falsification_flag: bool | None

    def as_dict(self) -> Dict[str, Any]:
        """Return a JSON-friendly representation of the entry."""

        return {
            "result_file": self.result_file,
            "domain": self.domain,
            "dataset": self.dataset,
            "theta": self.theta,
            "theta_ci": list(self.theta_ci) if self.theta_ci is not None else None,
            "beta": self.beta,
            "beta_ci": list(self.beta_ci) if self.beta_ci is not None else None,
            "logistic_r2": self.logistic_r2,
            "logistic_aic": self.logistic_aic,
            "best_null_model": self.best_null,
            "delta_aic_vs_best_null": self.delta_aic,
            "delta_r2_vs_best_null": self.delta_r2,
            "zeta_mean": self.zeta_mean,
            "logistic_beats_nulls": self.falsification_flag,
        }


def _mean(values: Iterable[float]) -> float:
    data = [value for value in values if value is not None]
    return sum(data) / len(data) if data else float("nan")


def _median(values: Iterable[float]) -> float:
    data = sorted(value for value in values if value is not None)
    n = len(data)
    if n == 0:
        return float("nan")
    mid = n // 2
    if n % 2 == 1:
        return data[mid]
    return 0.5 * (data[mid - 1] + data[mid])


def _safe_get(mapping: Mapping[str, Any], *keys: str) -> Any:
    current: Any = mapping
    for key in keys:
        if not isinstance(current, Mapping) or key not in current:
            return None
        current = current[key]
    return current


def _derive_domain(dataset_path: str | None) -> str:
    if not dataset_path:
        return "synthetic"
    path = Path(dataset_path)
    parts = path.parts
    try:
        index = parts.index("data")
    except ValueError:
        return "synthetic"
    if index + 1 < len(parts):
        return parts[index + 1]
    return "synthetic"


def _derive_dataset_label(dataset_info: Mapping[str, Any], fallback: str) -> str:
    if not isinstance(dataset_info, Mapping):
        return fallback
    label = dataset_info.get("name") or dataset_info.get("label")
    if isinstance(label, str) and label.strip():
        return label.strip()
    path = dataset_info.get("path")
    if isinstance(path, str) and path:
        return Path(path).stem
    return fallback


def parse_result(path: Path) -> BridgeEntry | None:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if "theta_estimate" not in payload or "beta_estimate" not in payload:
        return None

    dataset_info = payload.get("dataset", {}) if isinstance(payload.get("dataset"), Mapping) else {}
    dataset_path = dataset_info.get("path") if isinstance(dataset_info, Mapping) else None
    domain = _derive_domain(dataset_path if isinstance(dataset_path, str) else None)
    dataset_label = _derive_dataset_label(dataset_info, path.stem)

    theta_value = _safe_get(payload, "theta_estimate", "value")
    theta_ci = _safe_get(payload, "theta_estimate", "ci95")
    beta_value = _safe_get(payload, "beta_estimate", "value")
    beta_ci = _safe_get(payload, "beta_estimate", "ci95")
    logistic_r2 = _safe_get(payload, "logistic_model", "r2")
    logistic_aic = _safe_get(payload, "logistic_model", "aic")
    falsification_candidates = (
        _safe_get(payload, "falsification", "logistic_beats_all_nulls"),
        _safe_get(payload, "falsification", "logistic_beats_null"),
    )
    falsification_flag: bool | None = None
    for candidate in falsification_candidates:
        if isinstance(candidate, bool):
            falsification_flag = candidate
            break

    comparisons = _safe_get(payload, "falsification", "comparisons")
    best_null: str | None = None
    best_delta_aic: float | None = None
    best_delta_r2: float | None = None
    if isinstance(comparisons, Mapping):
        for name, stats in comparisons.items():
            if not isinstance(stats, Mapping):
                continue
            delta_aic = stats.get("delta_aic")
            if delta_aic is None:
                continue
            if best_delta_aic is None or float(delta_aic) > float(best_delta_aic):
                best_null = name
                best_delta_aic = float(delta_aic)
                delta_r2 = stats.get("delta_r2")
                best_delta_r2 = float(delta_r2) if delta_r2 is not None else None
    zeta_mean = _safe_get(payload, "membrane", "zeta_mean")

    return BridgeEntry(
        result_file=path.name,
        domain=domain,
        dataset=dataset_label,
        theta=float(theta_value) if theta_value is not None else None,
        theta_ci=theta_ci if isinstance(theta_ci, Sequence) else None,
        beta=float(beta_value) if beta_value is not None else None,
        beta_ci=beta_ci if isinstance(beta_ci, Sequence) else None,
        logistic_r2=float(logistic_r2) if logistic_r2 is not None else None,
        logistic_aic=float(logistic_aic) if logistic_aic is not None else None,
        best_null=best_null,
        delta_aic=float(best_delta_aic) if best_delta_aic is not None else None,
        delta_r2=float(best_delta_r2) if best_delta_r2 is not None else None,
        zeta_mean=float(zeta_mean) if zeta_mean is not None else None,
        falsification_flag=falsification_flag,
    )


def collect_entries(results_dir: Path) -> List[BridgeEntry]:
    entries: List[BridgeEntry] = []
    for path in sorted(results_dir.glob("*.json")):
        if path.name.endswith("resonance_bridge_table.json"):
            continue
        entry = parse_result(path)
        if entry is not None:
            entries.append(entry)
    return entries


def build_summary(entries: Sequence[BridgeEntry]) -> Dict[str, Any]:
    domain_counter = Counter(entry.domain for entry in entries)
    delta_aic_values = [entry.delta_aic for entry in entries if entry.delta_aic is not None]
    r2_values = [entry.logistic_r2 for entry in entries if entry.logistic_r2 is not None]
    zeta_values = [entry.zeta_mean for entry in entries if entry.zeta_mean is not None]

    return {
        "count": len(entries),
        "domains": dict(sorted(domain_counter.items())),
        "delta_aic": {
            "min": min(delta_aic_values) if delta_aic_values else None,
            "median": _median(delta_aic_values) if delta_aic_values else None,
            "mean": _mean(delta_aic_values) if delta_aic_values else None,
            "max": max(delta_aic_values) if delta_aic_values else None,
        },
        "logistic_r2": {
            "min": min(r2_values) if r2_values else None,
            "median": _median(r2_values) if r2_values else None,
            "mean": _mean(r2_values) if r2_values else None,
            "max": max(r2_values) if r2_values else None,
        },
        "zeta_mean": {
            "min": min(zeta_values) if zeta_values else None,
            "median": _median(zeta_values) if zeta_values else None,
            "mean": _mean(zeta_values) if zeta_values else None,
            "max": max(zeta_values) if zeta_values else None,
        },
    }


def write_json(entries: Sequence[BridgeEntry], aggregate: Mapping[str, Any], output_path: Path) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "aggregate": aggregate,
        "entries": [entry.as_dict() for entry in entries],
        "tri_layer": {
            "formal": "Consolidated logistic fits across domains; each row records Theta, beta, R^2, ΔAIC, and impedance means.",
            "empirical": "JSON prepared for docs overlays, simulator presets, and codex feedback ledgers to audit resonance breadth.",
            "metaphorical": "Lanterns strung between membranes—each dataset a dawn torch proving the chorus eclipses null winds.",
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def write_markdown(entries: Sequence[BridgeEntry], aggregate: Mapping[str, Any], output_path: Path) -> None:
    lines: List[str] = []
    lines.append("# Resonance Bridge Table")
    lines.append("")
    lines.append("## Formal")
    lines.append(
        "This ledger collates logistic resonance fits across domains, recording $\\Theta$, $\\beta$, $R^2$, and the strongest $\\Delta\\mathrm{AIC}$ wins against smooth null models."
    )
    lines.append("")
    lines.append("## Empirical")
    lines.append(
        "Entries draw from `analysis/results/*.json`; statistics summarise domain coverage, logistic accuracy, and impedance medians so reports and simulator presets remain in sync."
    )
    lines.append("")
    lines.append("## Metaphorical")
    lines.append(
        "Each row is a lantern along the resonance bridge—bees, membranes, forests, and models singing as $R$ crosses $\\Theta$ and the null breeze quiets."
    )
    lines.append("")

    lines.append("### Cohort Statistics")
    lines.append("")
    lines.append(f"*Datasets tallied:* {aggregate.get('count', 0)}")
    domain_stats = aggregate.get("domains", {})
    if domain_stats:
        domain_parts = ", ".join(f"{domain}: {count}" for domain, count in sorted(domain_stats.items()))
        lines.append(f"*Domain spread:* {domain_parts}")
    delta_stats = aggregate.get("delta_aic", {})
    if delta_stats and any(value is not None for value in delta_stats.values()):
        lines.append(
            f"*ΔAIC vs best null:* min={min_max_str(delta_stats.get('min'))}, "
            f"median={min_max_str(delta_stats.get('median'))}, "
            f"mean={min_max_str(delta_stats.get('mean'))}, max={min_max_str(delta_stats.get('max'))}"
        )
    r2_stats = aggregate.get("logistic_r2", {})
    if r2_stats and any(value is not None for value in r2_stats.values()):
        lines.append(
            f"*Logistic R²:* min={min_max_str(r2_stats.get('min'))}, "
            f"median={min_max_str(r2_stats.get('median'))}, "
            f"mean={min_max_str(r2_stats.get('mean'))}, max={min_max_str(r2_stats.get('max'))}"
        )
    zeta_stats = aggregate.get("zeta_mean", {})
    if zeta_stats and any(value is not None for value in zeta_stats.values()):
        lines.append(
            f"*Impedance ζ̄:* min={min_max_str(zeta_stats.get('min'))}, "
            f"median={min_max_str(zeta_stats.get('median'))}, "
            f"mean={min_max_str(zeta_stats.get('mean'))}, max={min_max_str(zeta_stats.get('max'))}"
        )
    lines.append("")

    lines.append("### Logistic Bridge")
    lines.append("")
    lines.append("| Domain | Dataset | Θ | β | R² | ΔAIC (best null) | Best null | ζ̄ |")
    lines.append("|--------|---------|---|---|----|------------------|-----------|----|")
    for entry in entries:
        theta_str = format_float(entry.theta)
        beta_str = format_float(entry.beta)
        r2_str = format_float(entry.logistic_r2)
        delta_aic_str = format_float(entry.delta_aic)
        zeta_str = format_float(entry.zeta_mean)
        lines.append(
            f"| {entry.domain} | {entry.dataset} | {theta_str} | {beta_str} | {r2_str} | {delta_aic_str} | {entry.best_null or '—'} | {zeta_str} |"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def min_max_str(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:.3f}"


def format_float(value: float | None) -> str:
    if value is None or (isinstance(value, float) and not (value == value)):
        return "—"
    if abs(value) >= 100 or abs(value) < 1e-3:
        return f"{value:.3e}"
    return f"{value:.3f}"


def run_cli(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate the cross-domain resonance bridge table.")
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=RESULTS_DIR,
        help="Directory containing analysis result JSON files.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=RESULTS_DIR / "resonance_bridge_table.json",
        help="Path for the aggregated JSON output.",
    )
    parser.add_argument(
        "--output-markdown",
        type=Path,
        default=REPORTS_DIR / "resonance_bridge_table.md",
        help="Optional Markdown ledger output path.",
    )
    parser.add_argument(
        "--no-markdown",
        action="store_true",
        help="Skip writing the Markdown summary.",
    )
    args = parser.parse_args(argv)

    entries = collect_entries(args.results_dir)
    aggregate = build_summary(entries)
    write_json(entries, aggregate, args.output_json)
    if not args.no_markdown:
        write_markdown(entries, aggregate, args.output_markdown)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    run_cli()
