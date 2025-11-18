#!/usr/bin/env python3
"""
UTAC v2.0 Beta Distribution Visualization

Creates publication-ready visualizations of β-parameter distribution:
1. β-distribution histogram with Φ^(n/3) attractor markers
2. Domain clustering heatmap
3. β vs Domain with confidence intervals
4. Log-scale Φ-ladder visualization

Supports SVG/PNG export for papers and presentations.

Usage:
    python scripts/visualize_beta_distribution.py [--output-dir figures/] [--format svg]

Author: UTAC v2.0 Synthesis
Date: 2025-11-18
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import gridspec
import seaborn as sns

# Golden ratio for aesthetic figures
PHI = (1 + np.sqrt(5)) / 2

# Φ^(n/3) attractor ladder
PHI_ATTRACTORS = {
    "Φ³ (Informational)": PHI**3,
    "Φ⁴ (Biological)": PHI**4,
    "Φ⁵ (Climate)": PHI**5,
}

# Domain clustering (from UTAC v2.0 synthesis)
DOMAIN_CLUSTERS = {
    "Informational": {"beta_mean": 4.5, "beta_sd": 0.9, "color": "#3498db", "attractor": "Φ³"},
    "Geophysical": {"beta_mean": 4.6, "beta_sd": 0.8, "color": "#e67e22", "attractor": "Φ³"},
    "Biological": {"beta_mean": 7.4, "beta_sd": 0.9, "color": "#2ecc71", "attractor": "Φ⁴"},
    "Climate": {"beta_mean": 11.0, "beta_sd": 1.0, "color": "#e74c3c", "attractor": "Φ⁵"},
    "Extreme": {"beta_mean": 13.0, "beta_sd": 1.8, "color": "#9b59b6", "attractor": "Beyond"},
}

# Domain classification (heuristic mapping)
DOMAIN_MAP = {
    "llm": "Informational",
    "climate": "Climate",
    "honeybee": "Biological",
    "synapse": "Biological",
    "lenski": "Biological",
    "working_memory": "Informational",
    "theta": "Informational",
    "seismic": "Geophysical",
    "blackhole": "Geophysical",
    "urban_heat": "Extreme",
    "amazon": "Climate",
    "mycelial": "Biological",
    "quantum": "Geophysical",
    "weakly": "Informational",
    "systemic": "Extreme",
    "thermohaline": "Extreme",
    "supercritical": "Climate",
    "cmb": "Informational",
    "hubble": "Informational",
}


def classify_domain(domain_name: str) -> str:
    """Classify domain into cluster based on name heuristics."""
    domain_lower = domain_name.lower()
    for key, cluster in DOMAIN_MAP.items():
        if key in domain_lower:
            return cluster
    return "Other"


def load_beta_data(csv_path: Path) -> pd.DataFrame:
    """Load and preprocess beta estimates."""
    df = pd.read_csv(csv_path)

    # Add cluster classification
    df["cluster"] = df["domain"].apply(classify_domain)

    # Add color mapping
    df["color"] = df["cluster"].map(
        lambda c: DOMAIN_CLUSTERS.get(c, {}).get("color", "#95a5a6")
    )

    return df


def plot_beta_histogram_with_phi_ladder(df: pd.DataFrame, ax: plt.Axes):
    """Plot β-distribution histogram with Φ^(n/3) attractor markers."""

    # Histogram
    ax.hist(
        df["beta"],
        bins=20,
        alpha=0.6,
        color="#34495e",
        edgecolor="black",
        label="Observed β"
    )

    # Φ^(n/3) attractor lines
    colors = ["#3498db", "#2ecc71", "#e74c3c"]
    for (label, phi_value), color in zip(PHI_ATTRACTORS.items(), colors):
        ax.axvline(
            phi_value,
            color=color,
            linestyle="--",
            linewidth=2,
            alpha=0.8,
            label=f"{label} ({phi_value:.2f})"
        )

    ax.set_xlabel("β (Steepness Parameter)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Count", fontsize=12, fontweight="bold")
    ax.set_title("UTAC v2.0: β-Distribution with Φ^(n/3) Attractors", fontsize=14, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(alpha=0.3, linestyle=":")


def plot_domain_heatmap(df: pd.DataFrame, ax: plt.Axes):
    """Plot domain clustering heatmap."""

    # Aggregate by cluster
    cluster_stats = df.groupby("cluster").agg({
        "beta": ["mean", "std", "count"]
    }).round(2)
    cluster_stats.columns = ["β_mean", "β_sd", "n"]
    cluster_stats = cluster_stats.sort_values("β_mean")

    # Create heatmap data
    heatmap_data = cluster_stats[["β_mean"]].T

    # Plot
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".2f",
        cmap="RdYlGn_r",
        cbar_kws={"label": "β (mean)"},
        linewidths=0.5,
        ax=ax,
        vmin=4,
        vmax=14
    )

    ax.set_title("Domain Clustering: β_mean Heatmap", fontsize=14, fontweight="bold")
    ax.set_ylabel("")
    ax.set_xlabel("Domain Cluster", fontsize=12)


def plot_beta_by_domain_with_ci(df: pd.DataFrame, ax: plt.Axes):
    """Plot β vs Domain with confidence intervals."""

    # Sort by beta for better visualization
    df_sorted = df.sort_values("beta").reset_index(drop=True)

    # Plot points with error bars
    for i, row in df_sorted.iterrows():
        ax.errorbar(
            i,
            row["beta"],
            yerr=[[row["beta"] - row["beta_ci_lower"]],
                  [row["beta_ci_upper"] - row["beta"]]],
            fmt="o",
            color=row["color"],
            markersize=6,
            capsize=3,
            alpha=0.7
        )

    # Add Φ^(n/3) horizontal lines
    colors = ["#3498db", "#2ecc71", "#e74c3c"]
    for (label, phi_value), color in zip(PHI_ATTRACTORS.items(), colors):
        ax.axhline(
            phi_value,
            color=color,
            linestyle="--",
            linewidth=1.5,
            alpha=0.6,
            label=label
        )

    ax.set_xlabel("System Index (sorted by β)", fontsize=12, fontweight="bold")
    ax.set_ylabel("β (with 95% CI)", fontsize=12, fontweight="bold")
    ax.set_title("β-Values Across 36 Systems (sorted)", fontsize=14, fontweight="bold")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(alpha=0.3, linestyle=":", axis="y")

    # Set y-axis to log scale
    ax.set_yscale("log")
    ax.set_ylim([1, 20])


def plot_phi_ladder_logscale(df: pd.DataFrame, ax: plt.Axes):
    """Plot β-distribution on log scale with Φ^(n/3) ladder."""

    # Scatter plot by cluster
    for cluster, props in DOMAIN_CLUSTERS.items():
        cluster_df = df[df["cluster"] == cluster]
        if len(cluster_df) > 0:
            ax.scatter(
                cluster_df.index,
                cluster_df["beta"],
                color=props["color"],
                label=f"{cluster} (n={len(cluster_df)})",
                s=60,
                alpha=0.7,
                edgecolors="black",
                linewidths=0.5
            )

    # Φ^(n/3) ladder with step annotations
    phi_steps = [
        (3, PHI**3, "Φ³", "#3498db"),
        (4, PHI**4, "Φ⁴", "#2ecc71"),
        (5, PHI**5, "Φ⁵", "#e74c3c"),
    ]

    for step, value, label, color in phi_steps:
        ax.axhline(
            value,
            color=color,
            linestyle="--",
            linewidth=2,
            alpha=0.7
        )
        ax.text(
            len(df) + 1,
            value,
            f"{label} = {value:.2f}",
            fontsize=10,
            va="center",
            ha="left",
            color=color,
            fontweight="bold"
        )

    ax.set_yscale("log")
    ax.set_ylabel("β (log scale)", fontsize=12, fontweight="bold")
    ax.set_xlabel("System Index", fontsize=12, fontweight="bold")
    ax.set_title("Φ^(n/3) Ladder: Domain Clustering on Log Scale", fontsize=14, fontweight="bold")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.grid(alpha=0.3, linestyle=":", which="both")
    ax.set_ylim([1, 20])


def create_beta_visualization_suite(
    csv_path: Path,
    output_dir: Path,
    output_format: str = "svg"
):
    """Create complete β-visualization suite."""

    # Load data
    print(f"📊 Loading beta estimates from {csv_path}...")
    df = load_beta_data(csv_path)
    print(f"✅ Loaded {len(df)} systems across {df['cluster'].nunique()} clusters")

    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])

    # Generate plots
    print("📈 Generating visualizations...")
    plot_beta_histogram_with_phi_ladder(df, ax1)
    plot_domain_heatmap(df, ax2)
    plot_beta_by_domain_with_ci(df, ax3)
    plot_phi_ladder_logscale(df, ax4)

    # Add main title
    fig.suptitle(
        "UTAC v2.0 Multi-Attractor Framework: β-Distribution Analysis (n=36 systems)",
        fontsize=16,
        fontweight="bold",
        y=0.995
    )

    # Save
    output_path = output_dir / f"utac_v2_beta_distribution.{output_format}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"💾 Saving to {output_path}...")
    fig.savefig(
        output_path,
        format=output_format,
        dpi=300,
        bbox_inches="tight",
        facecolor="white"
    )

    print(f"✅ Visualization saved: {output_path}")

    # Also save individual plots
    individual_dir = output_dir / "individual"
    individual_dir.mkdir(exist_ok=True)

    for i, (ax, name) in enumerate([
        (ax1, "histogram_phi_ladder"),
        (ax2, "domain_heatmap"),
        (ax3, "beta_with_ci"),
        (ax4, "phi_ladder_logscale")
    ]):
        individual_fig = ax.get_figure()
        individual_path = individual_dir / f"utac_v2_{name}.{output_format}"

        # Create new figure with just this subplot
        new_fig, new_ax = plt.subplots(figsize=(8, 6))

        # Copy content (simplified approach)
        if name == "histogram_phi_ladder":
            plot_beta_histogram_with_phi_ladder(df, new_ax)
        elif name == "domain_heatmap":
            plot_domain_heatmap(df, new_ax)
        elif name == "beta_with_ci":
            plot_beta_by_domain_with_ci(df, new_ax)
        elif name == "phi_ladder_logscale":
            plot_phi_ladder_logscale(df, new_ax)

        new_fig.savefig(
            individual_path,
            format=output_format,
            dpi=300,
            bbox_inches="tight",
            facecolor="white"
        )
        plt.close(new_fig)

    print(f"✅ Individual plots saved to {individual_dir}/")

    plt.close(fig)

    # Generate summary statistics
    print("\n📊 Summary Statistics:")
    print(f"   β range: {df['beta'].min():.2f} → {df['beta'].max():.2f}")
    print(f"   β mean: {df['beta'].mean():.2f} ± {df['beta'].std():.2f}")
    print(f"   β median: {df['beta'].median():.2f}")
    print(f"\n   Cluster breakdown:")
    for cluster in sorted(df['cluster'].unique()):
        cluster_df = df[df['cluster'] == cluster]
        print(f"   - {cluster}: n={len(cluster_df)}, β={cluster_df['beta'].mean():.2f}±{cluster_df['beta'].std():.2f}")


def main():
    parser = argparse.ArgumentParser(
        description="UTAC v2.0 Beta Distribution Visualization Suite"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/derived/beta_estimates.csv"),
        help="Path to beta_estimates.csv (default: data/derived/beta_estimates.csv)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("figures/utac_v2"),
        help="Output directory for figures (default: figures/utac_v2/)"
    )
    parser.add_argument(
        "--format",
        choices=["svg", "png", "pdf"],
        default="svg",
        help="Output format (default: svg)"
    )

    args = parser.parse_args()

    # Validate input
    if not args.input.exists():
        print(f"❌ Error: Input file not found: {args.input}")
        sys.exit(1)

    # Create visualizations
    create_beta_visualization_suite(
        csv_path=args.input,
        output_dir=args.output_dir,
        output_format=args.format
    )

    print("\n✨ UTAC v2.0 Visualization Suite Complete!")
    print(f"   Output: {args.output_dir}/utac_v2_beta_distribution.{args.format}")
    print(f"   Individual plots: {args.output_dir}/individual/")


if __name__ == "__main__":
    main()
