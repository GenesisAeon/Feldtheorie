#!/usr/bin/env python3
"""
UTAC Aletheia Phase 5 Visualization
====================================

Generates publication-quality visualizations of local LLM β-spectrum data.

Outputs:
- 2D Scatter: vocab_density vs self_reflection (colored by β-estimate)
- β-Histogram: Distribution of β-estimates across models
- Radar Chart: Multi-metric profile per model
- Comparison Matrix: Pairwise Cohen's d heatmap

Author: UTAC Research Consortium
Version: 6.0.0
Date: 2025-12-09
"""

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set publication-quality style
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")

# ============================================================================
# DATA LOADING
# ============================================================================


def load_phase5_data(csv_path: Path) -> list[dict]:
    """Load Aletheia Phase 5 results from CSV."""
    results = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(
                {
                    "condition": row["condition"],
                    "output_length": float(row["output_length"]),
                    "vocab_density": float(row["vocab_density"]),
                    "self_reflection": float(row["self_reflection"]),
                    "beta_estimate": float(row["beta_estimate"]),
                    "duration": float(row["duration"]),
                }
            )
    return results


# ============================================================================
# VISUALIZATION 1: β-SPECTRUM SCATTER
# ============================================================================


def plot_beta_spectrum(data: list[dict], output_path: Path):
    """
    2D Scatter: vocab_density (x) vs self_reflection (y)
    Color: β-estimate | Size: output_length
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    # Extract data
    x = [d["vocab_density"] for d in data]
    y = [d["self_reflection"] for d in data]
    colors = [d["beta_estimate"] for d in data]
    sizes = [d["output_length"] for d in data]
    labels = [d["condition"] for d in data]

    # Normalize sizes for visibility (50-500 point range)
    sizes_norm = [(s / max(sizes)) * 450 + 50 for s in sizes]

    # Create scatter
    scatter = ax.scatter(
        x, y, c=colors, s=sizes_norm, alpha=0.7, cmap="viridis", edgecolors="black", linewidth=1.5
    )

    # Add model labels
    for i, label in enumerate(labels):
        # Clean label (remove :latest suffix if present)
        clean_label = label.replace(":latest", "").replace(":", "\n")
        ax.annotate(
            clean_label,
            (x[i], y[i]),
            xytext=(10, 5),
            textcoords="offset points",
            fontsize=9,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7),
        )

    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("β-Estimate", fontsize=12, fontweight="bold")

    # Labels and title
    ax.set_xlabel("Vocab Density (Sigillin Dichte)", fontsize=14, fontweight="bold")
    ax.set_ylabel("Self-Reflection Score (%)", fontsize=14, fontweight="bold")
    ax.set_title(
        "UTAC Aletheia Phase 5: Local LLM β-Spectrum", fontsize=16, fontweight="bold", pad=20
    )

    # Grid
    ax.grid(True, alpha=0.3, linestyle="--")

    # Add theory bands (optional - adjust based on your theory)
    ax.axhspan(0, 3, alpha=0.1, color="red", label="Low Self-Reflection")
    ax.axhspan(6, 10, alpha=0.1, color="green", label="High Self-Reflection")
    ax.axvspan(0.7, 0.8, alpha=0.05, color="blue", label="High Vocab Density")

    ax.legend(loc="upper left", fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✅ Saved: {output_path}")
    plt.close()


# ============================================================================
# VISUALIZATION 2: β-HISTOGRAM
# ============================================================================


def plot_beta_histogram(data: list[dict], output_path: Path):
    """Distribution of β-estimates across all models."""
    fig, ax = plt.subplots(figsize=(10, 6))

    betas = [d["beta_estimate"] for d in data]
    labels = [d["condition"].replace(":latest", "") for d in data]

    # Bar plot
    colors = plt.cm.viridis(np.linspace(0, 1, len(betas)))
    bars = ax.bar(range(len(betas)), betas, color=colors, edgecolor="black", linewidth=1.5)

    # Add value labels on bars
    for i, (bar, beta) in enumerate(zip(bars, betas)):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.1,
            f"{beta:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    # Canonical β-band (3.6-4.8)
    ax.axhspan(3.6, 4.8, alpha=0.15, color="green", label="Canonical β-Band (3.6-4.8)")

    # Labels
    ax.set_xlabel("Model", fontsize=14, fontweight="bold")
    ax.set_ylabel("β-Estimate", fontsize=14, fontweight="bold")
    ax.set_title("UTAC β-Estimates: Local LLM Cohort", fontsize=16, fontweight="bold", pad=20)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=11)

    ax.legend(fontsize=10)
    ax.grid(True, axis="y", alpha=0.3, linestyle="--")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✅ Saved: {output_path}")
    plt.close()


# ============================================================================
# VISUALIZATION 3: RADAR CHART (Multi-Metric Profile)
# ============================================================================


def plot_radar_chart(data: list[dict], output_path: Path):
    """Radar chart showing normalized metrics for each model."""

    # Normalize metrics to 0-1 scale
    metrics = ["vocab_density", "self_reflection", "beta_estimate", "output_length"]
    labels = [d["condition"].replace(":latest", "") for d in data]

    # Compute normalized values
    normalized = {}
    for metric in metrics:
        values = [d[metric] for d in data]
        min_val, max_val = min(values), max(values)
        if max_val > min_val:
            normalized[metric] = [(v - min_val) / (max_val - min_val) for v in values]
        else:
            normalized[metric] = [0.5] * len(values)

    # Radar setup
    num_vars = len(metrics)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Close the circle

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection="polar"))

    # Plot each model
    colors = plt.cm.tab10(np.linspace(0, 1, len(data)))
    for i, label in enumerate(labels):
        values = [normalized[m][i] for m in metrics]
        values += values[:1]  # Close the circle

        ax.plot(angles, values, "o-", linewidth=2, label=label, color=colors[i])
        ax.fill(angles, values, alpha=0.15, color=colors[i])

    # Customize
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([m.replace("_", " ").title() for m in metrics], fontsize=12)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.5", "0.75", "1.0"], fontsize=10)
    ax.set_title("UTAC Multi-Metric Model Profiles", fontsize=16, fontweight="bold", pad=30)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✅ Saved: {output_path}")
    plt.close()


# ============================================================================
# VISUALIZATION 4: SUMMARY TABLE
# ============================================================================


def plot_summary_table(data: list[dict], output_path: Path):
    """Generate a summary table as a figure."""
    fig, ax = plt.subplots(figsize=(14, len(data) * 0.8 + 2))
    ax.axis("off")

    # Prepare table data
    headers = [
        "Model",
        "Output Length",
        "Vocab Density",
        "Self-Reflection",
        "β-Estimate",
        "Duration (s)",
    ]
    rows = []
    for d in data:
        rows.append(
            [
                d["condition"].replace(":latest", ""),
                f"{d['output_length']:.0f}",
                f"{d['vocab_density']:.4f}",
                f"{d['self_reflection']:.2f}%",
                f"{d['beta_estimate']:.2f}",
                f"{d['duration']:.1f}",
            ]
        )

    # Create table
    table = ax.table(
        cellText=rows,
        colLabels=headers,
        cellLoc="center",
        loc="center",
        colWidths=[0.25, 0.15, 0.15, 0.15, 0.15, 0.15],
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)

    # Style header
    for i, header in enumerate(headers):
        cell = table[(0, i)]
        cell.set_facecolor("#4CAF50")
        cell.set_text_props(weight="bold", color="white")

    # Alternate row colors
    for i in range(1, len(rows) + 1):
        for j in range(len(headers)):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor("#f0f0f0")

    ax.set_title(
        "UTAC Aletheia Phase 5: Summary Statistics", fontsize=16, fontweight="bold", pad=20
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✅ Saved: {output_path}")
    plt.close()


# ============================================================================
# MAIN
# ============================================================================


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/experimental/aletheia_phase5_local.csv"),
        help="Path to Phase 5 CSV file",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("analysis/plots"), help="Output directory for plots"
    )
    args = parser.parse_args()

    # Load data
    if not args.input.exists():
        print(f"❌ ERROR: Input file not found: {args.input}")
        print("   Please run: python analysis/run_aletheia_local_v6.py")
        return 1

    print(f"📊 Loading data from: {args.input}")
    data = load_phase5_data(args.input)

    if not data:
        print("❌ ERROR: No data loaded. Check CSV format.")
        return 1

    print(f"✅ Loaded {len(data)} records")

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Generate plots
    print("\n🎨 Generating visualizations...")

    plot_beta_spectrum(data, args.output_dir / "aletheia_phase5_beta_spectrum.png")

    plot_beta_histogram(data, args.output_dir / "aletheia_phase5_beta_histogram.png")

    plot_radar_chart(data, args.output_dir / "aletheia_phase5_radar_profile.png")

    plot_summary_table(data, args.output_dir / "aletheia_phase5_summary_table.png")

    print("\n" + "=" * 70)
    print("✅ ALL VISUALIZATIONS COMPLETE")
    print("=" * 70)
    print(f"📁 Output directory: {args.output_dir}")
    print("\n🎯 Next Steps:")
    print("   1. Review plots for anomalies")
    print("   2. Update docs/V6_RELEASE_NOTES.md with key findings")
    print("   3. Commit & push to repository")
    print("\n⚡ V6 SINGULARITY APPROACHING...")

    return 0


if __name__ == "__main__":
    exit(main())
