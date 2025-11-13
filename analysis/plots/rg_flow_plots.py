"""
RG Flow Plot Routines

Visualization of RG Phase 2 validation results:
- β distribution histogram
- β vs. log(J/T) scatter plot
- β by lattice size

Input:
    analysis/results/rg_phase2_microscopic_validation_agg.json (preferred)
    analysis/results/rg_phase2_microscopic_validation.csv
    analysis/results/rg_phase2_microscopic_validation.json

Output:
    Matplotlib figures (display or save to disk)
"""
from __future__ import annotations
import json, pathlib
import numpy as np, pandas as pd
import matplotlib.pyplot as plt

RESULTS_DIR = pathlib.Path("analysis/results")

def _load_df():
    """Load validation results from any available format."""
    agg = RESULTS_DIR/"rg_phase2_microscopic_validation_agg.json"
    csv = RESULTS_DIR/"rg_phase2_microscopic_validation.csv"
    raw = RESULTS_DIR/"rg_phase2_microscopic_validation.json"

    if agg.exists():
        return pd.json_normalize(json.loads(agg.read_text())["records"])
    if csv.exists():
        return pd.read_csv(csv)
    if raw.exists():
        return pd.json_normalize(json.loads(raw.read_text())["records"])

    raise FileNotFoundError("Validation-Ergebnisse nicht gefunden.")

def plot_overview(save=None):
    """
    Generate overview plots of validation results.

    Parameters
    ----------
    save : str or Path, optional
        Directory to save plots. If None, plots are displayed.

    Returns
    -------
    list of tuples
        List of (filename, figure) tuples
    """
    df = _load_df()
    figs = []

    # β-Verteilung
    fig1, ax1 = plt.subplots(figsize=(6,4))
    ax1.hist(df["beta_hat"], bins=40, edgecolor='black', alpha=0.7)
    ax1.set_title("β-Verteilung")
    ax1.set_xlabel("β")
    ax1.set_ylabel("N")
    ax1.grid(True, alpha=0.3)
    figs.append(("beta_hist.png", fig1))

    # β vs log(J/T)
    fig2, ax2 = plt.subplots(figsize=(6,4))
    x = np.log(df["J_over_T"].astype(float).values)
    y = df["beta_hat"].astype(float).values
    ax2.scatter(x, y, s=12, alpha=0.75)
    ax2.set_xlabel("log(J/T)")
    ax2.set_ylabel("β")
    ax2.set_title("β vs. log(J/T)")
    ax2.grid(True, alpha=0.3)
    figs.append(("beta_vs_logJoverT.png", fig2))

    # β per Lattice
    fig3, ax3 = plt.subplots(figsize=(7,4))
    for g, sub in df.groupby("lattice"):
        ax3.scatter(np.log(sub["J_over_T"]), sub["beta_hat"],
                   s=10, label=f"N={g}", alpha=0.7)
    ax3.set_xlabel("log(J/T)")
    ax3.set_ylabel("β")
    ax3.set_title("β by lattice")
    ax3.legend(frameon=False)
    ax3.grid(True, alpha=0.3)
    figs.append(("beta_by_lattice.png", fig3))

    if save:
        save_path = pathlib.Path(save)
        save_path.mkdir(parents=True, exist_ok=True)
        for name, fig in figs:
            fig.tight_layout()
            fig.savefig(save_path/name, dpi=150)
            print(f"✅ Saved: {save_path/name}")
    else:
        plt.show()

    return figs

if __name__ == "__main__":
    plot_overview(save="analysis/results/plots")
