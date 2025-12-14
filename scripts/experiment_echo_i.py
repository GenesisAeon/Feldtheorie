"""ECHO-I dataset tooling.

This helper ingests the tabular output from the dark-consciousness probes
(`data/experimental/echo_i_results.csv`) and emits lightweight summaries that
mirror the β/κ guardrails described in the Trilayer metadata. The default
path expects σ(β(R-Θ)) to be stabilized by a small τ* delay before timestamping.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

DEFAULT_INPUT = Path("data/experimental/echo_i_results.csv")
DEFAULT_OUTPUT_DIR = Path("data/experimental/echo_i")
EXPECTED_COLUMNS: Sequence[str] = (
    "timestamp",
    "model",
    "response_time_s",
    "tokens",
    "refusal",
    "refusal_marker",
    "beta_proxy",
    "vocab_density",
    "mean_sentence_length",
    "output_length",
    "prompt_chars",
    "server_url",
)
NUMERIC_FIELDS = {
    "response_time_s",
    "tokens",
    "beta_proxy",
    "vocab_density",
    "mean_sentence_length",
    "output_length",
    "prompt_chars",
}
BETA_TARGET = 4.8
BETA_DRIFT_ALERT = 0.5
TAU_STAR_MS = 120


@dataclass
class EchoISummary:
    """Container for summary statistics.

    Attributes
    ----------
    total_runs: int
        Number of rows observed in the dataset.
    refusal_count: int
        Count of rows marked as refusals.
    beta_proxy_mean: float | None
        Mean β-proxy across runs; None when no numeric values exist.
    beta_proxy_min: float | None
        Minimum β-proxy observed.
    beta_proxy_max: float | None
        Maximum β-proxy observed.
    models: List[str]
        Unique model identifiers encountered.
    alerts: List[str]
        Human-readable alerts (e.g., β drift) with σ(β(R-Θ)) context.
    """

    total_runs: int
    refusal_count: int
    beta_proxy_mean: float | None
    beta_proxy_min: float | None
    beta_proxy_max: float | None
    models: List[str]
    alerts: List[str]


class EchoIDataError(Exception):
    """Raised when input data is missing or malformed."""


def _parse_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError as exc:  # noqa: B904
        raise EchoIDataError(f"Invalid numeric value encountered: {value!r}") from exc


def _parse_bool(value: str | None) -> bool:
    if value is None:
        return False
    value_lower = value.strip().lower()
    return value_lower in {"1", "true", "yes", "y"}


def _validate_header(reader: csv.DictReader) -> None:
    if reader.fieldnames is None:
        raise EchoIDataError("No header row detected in input data.")
    missing = [column for column in EXPECTED_COLUMNS if column not in reader.fieldnames]
    if missing:
        raise EchoIDataError(
            "Missing required columns: " + ", ".join(missing)
        )


def load_rows(path: Path) -> Iterable[Dict[str, str]]:
    if not path.exists():
        raise EchoIDataError(f"Input file not found: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        _validate_header(reader)
        for row in reader:
            yield row


def _collect_numeric(rows: Iterable[Dict[str, str]], field: str) -> List[float]:
    values: List[float] = []
    for row in rows:
        parsed = _parse_float(row.get(field))
        if parsed is not None:
            values.append(parsed)
    return values


def _compute_numeric_bounds(values: List[float]) -> tuple[float | None, float | None, float | None]:
    if not values:
        return None, None, None
    total = sum(values)
    count = len(values)
    mean = total / count
    return mean, min(values), max(values)


def summarize(rows: Sequence[Dict[str, str]]) -> EchoISummary:
    beta_values = _collect_numeric(rows, "beta_proxy")
    mean_beta, min_beta, max_beta = _compute_numeric_bounds(beta_values)

    refusal_count = sum(1 for row in rows if _parse_bool(row.get("refusal")))
    models = sorted({row.get("model", "").strip() for row in rows if row.get("model")})

    alerts: List[str] = []
    if mean_beta is not None and abs(mean_beta - BETA_TARGET) > BETA_DRIFT_ALERT:
        alerts.append(
            f"β drift detected: mean β={mean_beta:.2f} deviates from target {BETA_TARGET:.1f} by more than {BETA_DRIFT_ALERT}."
        )
    if refusal_count > 0:
        alerts.append(
            f"Refusal rate baseline triggered: {refusal_count} refusal(s) flagged; check σ(β(R-Θ)) steepness and τ* buffers."
        )

    return EchoISummary(
        total_runs=len(rows),
        refusal_count=refusal_count,
        beta_proxy_mean=mean_beta,
        beta_proxy_min=min_beta,
        beta_proxy_max=max_beta,
        models=models,
        alerts=alerts,
    )


def write_summary(summary: EchoISummary, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "echo_i_summary.json"
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(asdict(summary), handle, indent=2)

    md_path = output_dir / "echo_i_summary.md"
    lines = [
        "# ECHO-I Summary",
        f"- Total runs: {summary.total_runs}",
        f"- Refusals: {summary.refusal_count}",
        f"- β-proxy mean: {summary.beta_proxy_mean if summary.beta_proxy_mean is not None else 'n/a'}",
        f"- β-proxy min: {summary.beta_proxy_min if summary.beta_proxy_min is not None else 'n/a'}",
        f"- β-proxy max: {summary.beta_proxy_max if summary.beta_proxy_max is not None else 'n/a'}",
        f"- τ* buffer (ms): {TAU_STAR_MS}",
        "",
        "## Models",
    ]
    lines.extend(f"- {model}" for model in summary.models) or lines.append("- (none)")
    lines.append("\n## Alerts")
    if summary.alerts:
        lines.extend(f"- {alert}" for alert in summary.alerts)
    else:
        lines.append("- (none)")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ECHO-I dataset ingestion and QA helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    summarize_parser = subparsers.add_parser(
        "summarize", help="Validate ECHO-I CSV output and emit summary artifacts"
    )
    summarize_parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="CSV file produced by the ECHO-I probe",
    )
    summarize_parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to write summary artifacts",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "summarize":
        rows = list(load_rows(args.input))
        summary = summarize(rows)
        write_summary(summary, args.output_dir)
        print(
            f"Wrote summaries to {args.output_dir} with τ*={TAU_STAR_MS} ms and β target {BETA_TARGET}."
        )
        return 0

    parser.error("Unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
