#!/usr/bin/env python3
"""Automated evaluation for Project Aletheia CSV outputs."""

import argparse
import csv
import json
from collections.abc import Iterable
from itertools import combinations
from pathlib import Path

import numpy as np


def load_results(csv_path: Path) -> list[dict[str, float]]:
    """Load Aletheia experiment results from CSV."""

    with csv_path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, float]] = []
        for row in reader:
            rows.append(
                {
                    "condition": row["condition"],
                    "output_length": float(row["output_length"]),
                    "vocab_density": float(row["vocab_density"]),
                    "self_reflection": float(row["self_reflection"]),
                }
            )
    return rows


def group_by_condition(rows: Iterable[dict[str, float]]) -> dict[str, list[dict[str, float]]]:
    """Group rows by the `condition` column."""

    grouped: dict[str, list[dict[str, float]]] = {}
    for row in rows:
        grouped.setdefault(row["condition"], []).append(row)
    return grouped


def compute_summary(group: list[dict[str, float]]) -> dict[str, float]:
    """Compute summary metrics for a group."""

    lengths = np.array([row["output_length"] for row in group])
    vocab = np.array([row["vocab_density"] for row in group])
    reflection = np.array([row["self_reflection"] for row in group])

    return {
        "count": len(group),
        "mean_output_length": float(np.mean(lengths)),
        "std_output_length": float(np.std(lengths)),
        "mean_vocab_density": float(np.mean(vocab)),
        "std_vocab_density": float(np.std(vocab)),
        "mean_self_reflection": float(np.mean(reflection)),
        "std_self_reflection": float(np.std(reflection)),
    }


def cohen_d(values_a: np.ndarray, values_b: np.ndarray) -> float:
    """Compute Cohen's d between two samples."""

    if len(values_a) == 0 or len(values_b) == 0:
        return 0.0

    pooled_std = np.sqrt(((np.var(values_a) + np.var(values_b)) / 2) or 1e-12)
    return float((np.mean(values_a) - np.mean(values_b)) / pooled_std)


def summarize_pairs(grouped: dict[str, list[dict[str, float]]]) -> list[dict[str, float]]:
    """Compute pairwise deltas and effect sizes."""

    pairs: list[dict[str, float]] = []
    for cond_a, cond_b in combinations(sorted(grouped.keys()), 2):
        a_rows = grouped[cond_a]
        b_rows = grouped[cond_b]

        vocab_a = np.array([row["vocab_density"] for row in a_rows])
        vocab_b = np.array([row["vocab_density"] for row in b_rows])
        reflection_a = np.array([row["self_reflection"] for row in a_rows])
        reflection_b = np.array([row["self_reflection"] for row in b_rows])

        pairs.append(
            {
                "pair": f"{cond_a} vs {cond_b}",
                "vocab_density_delta": float(np.mean(vocab_b) - np.mean(vocab_a)),
                "cohens_d_self_reflection": cohen_d(reflection_b, reflection_a),
            }
        )
    return pairs


def render_report(
    summaries: dict[str, dict[str, float]],
    pairs: list[dict[str, float]],
    output_path: Path,
) -> None:
    """Write a Markdown report with group summaries and pairwise comparisons."""

    lines = ["# Project Aletheia Evaluation", ""]
    lines.append("## Group Summaries")
    lines.append("")
    lines.append("| Condition | N | Output Length (mean±sd) | Vocab Density (mean±sd) | Self-Reflection (mean±sd) |")
    lines.append("| --- | --- | --- | --- | --- |")

    for condition, stats in sorted(summaries.items()):
        lines.append(
            "| {condition} | {count} | {len_mean:.1f} ± {len_std:.1f} | {vocab_mean:.3f} ± {vocab_std:.3f} | "
            "{ref_mean:.2f} ± {ref_std:.2f} |".format(
                condition=condition,
                count=int(stats["count"]),
                len_mean=stats["mean_output_length"],
                len_std=stats["std_output_length"],
                vocab_mean=stats["mean_vocab_density"],
                vocab_std=stats["std_vocab_density"],
                ref_mean=stats["mean_self_reflection"],
                ref_std=stats["std_self_reflection"],
            )
        )

    lines.append("")
    lines.append("## Pairwise Effects")
    lines.append("")
    lines.append("| Pair | Vocab Density Δ | Cohen's d (Self-Reflection) |")
    lines.append("| --- | --- | --- |")

    for entry in pairs:
        lines.append(
            "| {pair} | {delta:+.4f} | {d:+.3f} |".format(
                pair=entry["pair"],
                delta=entry["vocab_density_delta"],
                d=entry["cohens_d_self_reflection"],
            )
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_json_summary(
    summaries: dict[str, dict[str, float]],
    pairs: list[dict[str, float]],
    json_path: Path,
) -> None:
    """Persist numerical results to JSON for downstream analysis."""

    json_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"summaries": summaries, "pairwise": pairs}
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    """Configure CLI arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/experimental/aletheia_results.csv"),
        help="Path to aletheia_results.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/aletheia_report.md"),
        help="Markdown report destination",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/aletheia_report.json"),
        help="Optional JSON summary destination",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for automated evaluation."""

    args = parse_args()
    rows = load_results(args.input)
    grouped = group_by_condition(rows)
    summaries = {name: compute_summary(group) for name, group in grouped.items()}
    pairwise = summarize_pairs(grouped)

    render_report(summaries, pairwise, args.output)
    if args.json_output:
        write_json_summary(summaries, pairwise, args.json_output)


if __name__ == "__main__":
    main()
