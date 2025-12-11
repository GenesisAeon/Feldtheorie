"""
Visualization: Historical Data vs. Theoretical Ising Predictions (UTAC v5.0)

This script creates publication-quality figures comparing:
    - Empirical stability scores
    - Theoretical susceptibility χ(Gini, Load)
    - Crisis event markers

Figures:
    1. Time series: Gini + Stability for 3 major nations
    2. Phase diagram: Gini vs. χ with crisis overlay
    3. Correlation scatter: χ vs. Stability

Author: Genesis Aeon (UTAC Framework)
Version: 5.0 "Empirical Grounding"
"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from models.social_rigidity_ising import SocialIsingModel

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_FILE = Path(__file__).parent.parent.parent / "data" / "grounding" / "historical_panel.csv"
PARAMS_FILE = Path(__file__).parent.parent.parent / "data" / "grounding" / "fitted_parameters.json"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "figures" / "v5_empirical"

# Focus countries for time series
FOCUS_COUNTRIES = ["United States", "China", "France"]

# Figure style
plt.style.use("seaborn-v0_8-darkgrid")
COLORS = {"USA": "#1f77b4", "China": "#ff7f0e", "France": "#2ca02c"}


# ============================================================================
# PLOTTING FUNCTIONS
# ============================================================================


def plot_time_series(data: pd.DataFrame, J: float, h: float):
    """
    Plot time series of Gini, Stability, and χ for focus countries.

    Args:
        data: Historical panel
        J: Fitted coupling strength
        h: Fitted external field
    """
    model = SocialIsingModel(coupling_strength=J, external_field=h)

    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    for country in FOCUS_COUNTRIES:
        country_data = data[data["Country"] == country].copy()

        # Compute theoretical susceptibility
        chi_values = []
        for _, row in country_data.iterrows():
            state = model.compute_state(row["Gini"], row["Load"])
            chi_values.append(state.susceptibility)

        country_data["Susceptibility"] = chi_values

        # Time series
        years = country_data["Year"].values
        gini = country_data["Gini"].values
        stability = country_data["Stability_Score"].values
        chi = np.array(chi_values)

        color = COLORS.get(country, "#333")

        # Plot 1: Gini
        axes[0].plot(years, gini, marker="o", label=country, color=color, linewidth=2)

        # Plot 2: Stability
        axes[1].plot(years, stability, marker="s", label=country, color=color, linewidth=2)

        # Plot 3: Susceptibility
        axes[2].plot(years, chi, marker="^", label=country, color=color, linewidth=2)

        # Mark crisis events
        crisis_years = country_data[country_data["Crisis_Event"] == 1]["Year"].values
        for crisis_year in crisis_years:
            for ax in axes:
                ax.axvline(crisis_year, color=color, linestyle="--", alpha=0.3, linewidth=1.5)

    # Formatting
    axes[0].set_ylabel("Gini Coefficient", fontsize=12, fontweight="bold")
    axes[0].legend(loc="upper left", fontsize=10)
    axes[0].set_title("Inequality Trajectory (1990-2024)", fontsize=14, fontweight="bold")
    axes[0].grid(True, alpha=0.3)

    axes[1].set_ylabel("Stability Score", fontsize=12, fontweight="bold")
    axes[1].legend(loc="upper left", fontsize=10)
    axes[1].set_title("Empirical Stability", fontsize=14, fontweight="bold")
    axes[1].grid(True, alpha=0.3)

    axes[2].set_ylabel("Susceptibility χ", fontsize=12, fontweight="bold")
    axes[2].set_xlabel("Year", fontsize=12, fontweight="bold")
    axes[2].legend(loc="upper left", fontsize=10)
    axes[2].set_title(
        f"Theoretical Susceptibility (J={J:.2f}, h={h:.2f})", fontsize=14, fontweight="bold"
    )
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()

    output_file = OUTPUT_DIR / "time_series_comparison.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"  ✓ Saved: {output_file}")

    plt.close()


def plot_phase_diagram(data: pd.DataFrame, J: float, h: float):
    """
    Plot Gini vs. Susceptibility with crisis event overlay.

    Args:
        data: Historical panel
        J: Fitted coupling
        h: Fitted field
    """
    model = SocialIsingModel(coupling_strength=J, external_field=h)

    # Compute susceptibility for all data
    chi_values = []
    for _, row in data.iterrows():
        state = model.compute_state(row["Gini"], row["Load"])
        chi_values.append(state.susceptibility)

    data["Susceptibility"] = chi_values

    # Separate crisis vs. non-crisis
    crisis_data = data[data["Crisis_Event"] == 1]
    normal_data = data[data["Crisis_Event"] == 0]

    fig, ax = plt.subplots(figsize=(12, 8))

    # Scatter plots
    ax.scatter(
        normal_data["Gini"],
        normal_data["Susceptibility"],
        c=normal_data["Stability_Score"],
        cmap="viridis",
        s=50,
        alpha=0.6,
        edgecolors="k",
        linewidth=0.5,
        label="Normal",
    )

    crisis_scatter = ax.scatter(
        crisis_data["Gini"],
        crisis_data["Susceptibility"],
        c="red",
        s=200,
        alpha=0.8,
        edgecolors="darkred",
        linewidth=2,
        marker="X",
        label="Crisis Event",
    )

    # Theoretical curve (mean Load)
    gini_range = np.linspace(0.25, 0.70, 200)
    mean_load = data["Load"].mean()

    chi_theory = []
    for g in gini_range:
        state = model.compute_state(g, mean_load)
        chi_theory.append(state.susceptibility)

    ax.plot(
        gini_range,
        chi_theory,
        "k--",
        linewidth=3,
        label=f"Theory (Load={mean_load:.2f})",
        alpha=0.7,
    )

    # Formatting
    ax.set_xlabel("Gini Coefficient", fontsize=14, fontweight="bold")
    ax.set_ylabel("Susceptibility χ", fontsize=14, fontweight="bold")
    ax.set_title(
        f"Phase Diagram: Ising Model (J={J:.2f}, h={h:.2f})", fontsize=16, fontweight="bold"
    )
    ax.legend(fontsize=12, loc="upper left")
    ax.grid(True, alpha=0.3)

    # Color bar
    cbar = plt.colorbar(cm.ScalarMappable(cmap="viridis"), ax=ax, label="Stability Score")
    cbar.set_label("Stability Score", fontsize=12, fontweight="bold")

    plt.tight_layout()

    output_file = OUTPUT_DIR / "phase_diagram.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"  ✓ Saved: {output_file}")

    plt.close()


def plot_correlation_scatter(data: pd.DataFrame, J: float, h: float):
    """
    Scatter plot: Susceptibility vs. Stability.

    Args:
        data: Historical panel
        J: Fitted coupling
        h: Fitted field
    """
    model = SocialIsingModel(coupling_strength=J, external_field=h)

    chi_values = []
    for _, row in data.iterrows():
        state = model.compute_state(row["Gini"], row["Load"])
        chi_values.append(state.susceptibility)

    data["Susceptibility"] = chi_values

    fig, ax = plt.subplots(figsize=(10, 8))

    # Scatter
    crisis_data = data[data["Crisis_Event"] == 1]
    normal_data = data[data["Crisis_Event"] == 0]

    ax.scatter(
        normal_data["Susceptibility"],
        normal_data["Stability_Score"],
        c="blue",
        s=60,
        alpha=0.5,
        edgecolors="k",
        linewidth=0.3,
        label="Normal",
    )

    ax.scatter(
        crisis_data["Susceptibility"],
        crisis_data["Stability_Score"],
        c="red",
        s=200,
        alpha=0.9,
        edgecolors="darkred",
        linewidth=2,
        marker="X",
        label="Crisis Event",
    )

    # Regression line
    from scipy.stats import linregress

    slope, intercept, r_value, p_value, std_err = linregress(
        data["Susceptibility"], data["Stability_Score"]
    )

    chi_fit = np.linspace(data["Susceptibility"].min(), data["Susceptibility"].max(), 100)
    stability_fit = slope * chi_fit + intercept

    ax.plot(
        chi_fit,
        stability_fit,
        "k--",
        linewidth=2,
        label=f"Linear fit: R²={r_value**2:.3f}, p={p_value:.4f}",
    )

    # Formatting
    ax.set_xlabel("Theoretical Susceptibility χ", fontsize=14, fontweight="bold")
    ax.set_ylabel("Empirical Stability Score", fontsize=14, fontweight="bold")
    ax.set_title("Correlation: Theory vs. Observation", fontsize=16, fontweight="bold")
    ax.legend(fontsize=11, loc="upper right")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    output_file = OUTPUT_DIR / "correlation_scatter.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"  ✓ Saved: {output_file}")

    plt.close()


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """Generate all visualizations."""

    print("=" * 70)
    print("VISUALIZATION: HISTORY VS. THEORY (UTAC v5.0)")
    print("=" * 70)
    print()

    # Load data
    if not DATA_FILE.exists():
        print(f"ERROR: Data file not found: {DATA_FILE}")
        print("Run: python scripts/grounding/ingest_historical_data.py")
        return

    data = pd.read_csv(DATA_FILE)
    print(f"Loaded {len(data)} observations")

    # Load fitted parameters
    if not PARAMS_FILE.exists():
        print(f"ERROR: Parameters not found: {PARAMS_FILE}")
        print("Run: python scripts/grounding/fit_ising_parameters.py")
        return

    with open(PARAMS_FILE) as f:
        params = json.load(f)

    # Use crisis-optimized parameters
    J = params["crisis_optimized"]["J"]
    h = params["crisis_optimized"]["h"]

    print(f"Using fitted parameters: J={J:.3f}, h={h:.3f}")
    print()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate figures
    print("Generating figures...")
    print()

    print("Figure 1: Time Series Comparison")
    plot_time_series(data, J, h)

    print("Figure 2: Phase Diagram (Gini vs. χ)")
    plot_phase_diagram(data, J, h)

    print("Figure 3: Correlation Scatter (χ vs. Stability)")
    plot_correlation_scatter(data, J, h)

    print()
    print("=" * 70)
    print("VISUALIZATION COMPLETE")
    print("=" * 70)
    print()
    print(f"Figures saved to: {OUTPUT_DIR}")
    print()
    print("NEXT STEPS:")
    print("  1. Review figures for model validation")
    print("  2. Run cosmic constant scan: scripts/validation/universal_constant_scan.py")
    print("  3. Generate LaTeX paper: scripts/paper/generate_latex_tables.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
