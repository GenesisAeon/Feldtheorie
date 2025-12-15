"""
RG Flow Plot Routines for UTAC v2.0

Visualizes Renormalization Group validation results:
- β distribution across seeds/noise/lattice
- β vs log(J/T) scaling
- Lattice-size dependence
- Finite-size scaling analysis

Author: Johann Römer & Aeon
Date: December 2024
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RESULTS_DIR = Path("analysis/results")


def _load_df() -> pd.DataFrame:
    """
    Load validation results from available formats.

    Search order: aggregated JSON -> CSV -> raw JSON

    Returns
    -------
    DataFrame
        Validation results with columns: beta_hat, J_over_T, lattice, noise, seed

    Raises
    ------
    FileNotFoundError
        If no validation results found
    """
    agg = RESULTS_DIR / "rg_phase2_microscopic_validation_agg.json"
    csv = RESULTS_DIR / "rg_phase2_microscopic_validation.csv"
    raw = RESULTS_DIR / "rg_phase2_microscopic_validation.json"

    if agg.exists():
        return pd.json_normalize(json.loads(agg.read_text())["records"])
    if csv.exists():
        return pd.read_csv(csv)
    if raw.exists():
        return pd.json_normalize(json.loads(raw.read_text())["records"])

    raise FileNotFoundError(
        "Validation results not found. Expected one of:\n"
        f"  - {agg}\n"
        f"  - {csv}\n"
        f"  - {raw}"
    )


def plot_overview(save: str | Path | None = None) -> List[Tuple[str, plt.Figure]]:
    """
    Generate overview plots of RG validation results.

    Creates three plots:
    1. β histogram (distribution)
    2. β vs log(J/T) scatter (scaling relationship)
    3. β by lattice size (finite-size effects)

    Parameters
    ----------
    save : str or Path, optional
        Directory to save figures. If None, figures are returned but not saved.

    Returns
    -------
    list of tuples
        List of (filename, figure) tuples

    Examples
    --------
    >>> figures = plot_overview(save="analysis/results/figures")
    """
    df = _load_df()
    figs = []

    # Plot 1: β distribution
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.hist(df["beta_hat"], bins=40, alpha=0.7, edgecolor='black')
    ax1.set_title("β Distribution", fontsize=14, fontweight='bold')
    ax1.set_xlabel("β (Steepness Parameter)", fontsize=12)
    ax1.set_ylabel("Frequency", fontsize=12)
    ax1.axvline(4.2, color='red', linestyle='--', linewidth=1.5, label='Theory (β=4.2)')
    ax1.legend()
    ax1.grid(alpha=0.3)
    figs.append(("beta_hist.png", fig1))

    # Plot 2: β vs log(J/T)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    x = np.log(df["J_over_T"].astype(float).values)
    y = df["beta_hat"].astype(float).values
    ax2.scatter(x, y, s=12, alpha=0.75, c='steelblue', edgecolors='black', linewidth=0.5)
    ax2.set_xlabel("log(J/T)", fontsize=12)
    ax2.set_ylabel("β", fontsize=12)
    ax2.set_title("β vs. log(J/T) Scaling", fontsize=14, fontweight='bold')
    ax2.grid(alpha=0.3)

    # Add trend line
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    x_trend = np.linspace(x.min(), x.max(), 100)
    ax2.plot(x_trend, p(x_trend), "r--", linewidth=2, alpha=0.8, label=f'Linear fit: β={z[0]:.2f}·log(J/T)+{z[1]:.2f}')
    ax2.legend()
    figs.append(("beta_vs_logJoverT.png", fig2))

    # Plot 3: β by lattice size
    fig3, ax3 = plt.subplots(figsize=(7, 4))
    colors = plt.cm.viridis(np.linspace(0, 1, len(df["lattice"].unique())))

    for i, (g, sub) in enumerate(df.groupby("lattice")):
        ax3.scatter(
            np.log(sub["J_over_T"]),
            sub["beta_hat"],
            s=30,
            label=f"N={g}",
            alpha=0.7,
            color=colors[i],
            edgecolors='black',
            linewidth=0.5
        )
    ax3.set_xlabel("log(J/T)", fontsize=12)
    ax3.set_ylabel("β", fontsize=12)
    ax3.set_title("β by Lattice Size", fontsize=14, fontweight='bold')
    ax3.legend(frameon=True, loc='best')
    ax3.grid(alpha=0.3)
    figs.append(("beta_by_lattice.png", fig3))

    # Save if requested
    if save:
        save_path = Path(save)
        save_path.mkdir(parents=True, exist_ok=True)
        for name, fig in figs:
            fig.tight_layout()
            fig.savefig(save_path / name, dpi=150, bbox_inches='tight')
            print(f"✅ Saved: {save_path / name}")
        plt.close('all')

    return figs


if __name__ == "__main__":
    print("🌊 RG Flow Plots - UTAC v2.0")
    print("=" * 50)

    try:
        figures = plot_overview(save="analysis/results/figures")
        print(f"\n✅ Generated {len(figures)} plots")
        print("\nPlots created:")
        for name, _ in figures:
            print(f"  - {name}")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nRun validation first:")
        print("  python scripts/validate_phase2.py")

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
