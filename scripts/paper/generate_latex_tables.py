"""
LaTeX Table Generation for V5.0 Manuscript (UTAC v5.0)

This script generates publication-ready LaTeX tables from empirical results:

Tables:
    1. Social Ising Model: Fitted Parameters
    2. Social Ising Model: Fit Diagnostics
    3. Cosmic Constants: Top 10 Alternatives (Look-Elsewhere Effect)
    4. Historical Crisis Events vs. Susceptibility Peaks

Author: Genesis Aeon (UTAC Framework)
Version: 5.0 "Automated Manuscript Generation"
"""

import numpy as np
import pandas as pd
from pathlib import Path
import json
from typing import Dict, List

# ============================================================================
# CONFIGURATION
# ============================================================================

# Input files
DATA_DIR = Path(__file__).parent.parent.parent / "data"
GROUNDING_DIR = DATA_DIR / "grounding"
DERIVED_DIR = DATA_DIR / "derived"

PARAMS_FILE = GROUNDING_DIR / "fitted_parameters.json"
PANEL_FILE = GROUNDING_DIR / "historical_panel.csv"
COSMIC_FILE = DERIVED_DIR / "cosmic_alternatives.csv"
LEE_SUMMARY_FILE = DERIVED_DIR / "look_elsewhere_summary.json"

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent.parent / "paper" / "v5_manuscript"


# ============================================================================
# TABLE GENERATORS
# ============================================================================

def generate_ising_parameters_table() -> str:
    """
    Generate LaTeX table for fitted Ising parameters.

    Returns:
        LaTeX table code
    """
    if not PARAMS_FILE.exists():
        return "% ERROR: Fitted parameters file not found\n"

    with open(PARAMS_FILE, 'r') as f:
        params = json.load(f)

    crisis_opt = params["crisis_optimized"]
    stability_opt = params["stability_optimized"]

    table = r"""
\begin{table}[htbp]
\centering
\caption{Fitted Parameters for Social Ising Model}
\label{tab:ising_parameters}
\begin{tabular}{lcc}
\toprule
\textbf{Parameter} & \textbf{Crisis-Optimized} & \textbf{Stability-Optimized} \\
\midrule
Coupling $J$ & """ + f"{crisis_opt['J']:.3f}" + r""" & """ + f"{stability_opt['J']:.3f}" + r""" \\
External Field $h$ & """ + f"{crisis_opt['h']:.3f}" + r""" & """ + f"{stability_opt['h']:.3f}" + r""" \\
Critical Gini $G_c$ & """ + f"{crisis_opt['critical_gini']:.3f}" + r""" & """ + f"{stability_opt['critical_gini']:.3f}" + r""" \\
\bottomrule
\end{tabular}
\end{table}
"""

    return table


def generate_ising_diagnostics_table() -> str:
    """
    Generate LaTeX table for fit diagnostics.

    Returns:
        LaTeX table code
    """
    if not PARAMS_FILE.exists():
        return "% ERROR: Fitted parameters file not found\n"

    with open(PARAMS_FILE, 'r') as f:
        params = json.load(f)

    crisis_opt = params["crisis_optimized"]

    table = r"""
\begin{table}[htbp]
\centering
\caption{Social Ising Model: Empirical Validation Diagnostics}
\label{tab:ising_diagnostics}
\begin{tabular}{lcc}
\toprule
\textbf{Metric} & \textbf{Value} & \textbf{Significance} \\
\midrule
Crisis Event Correlation ($\rho$) & """ + f"{crisis_opt['crisis_correlation']:.3f}" + r""" & """ + \
    ("$p < 0.05$" if crisis_opt['crisis_p_value'] < 0.05 else f"$p = {crisis_opt['crisis_p_value']:.3f}$") + r""" \\
Stability Anti-Correlation ($r$) & """ + f"{crisis_opt['stability_correlation']:.3f}" + r""" & """ + \
    ("$p < 0.05$" if crisis_opt['stability_p_value'] < 0.05 else f"$p = {crisis_opt['stability_p_value']:.3f}$") + r""" \\
Max Susceptibility $\chi_{\max}$ & """ + f"{crisis_opt['max_susceptibility']:.2f}" + r""" & --- \\
\bottomrule
\end{tabular}
\vspace{0.3cm}
\begin{tablenotes}
\small
\item \textbf{Interpretation:} """ + \
    ("Significant correlation between theoretical susceptibility and empirical crisis events." \
     if crisis_opt['crisis_p_value'] < 0.05 else \
     "No significant correlation detected. Model requires revision.") + r"""
\end{tablenotes}
\end{table}
"""

    return table


def generate_cosmic_alternatives_table(top_n: int = 10) -> str:
    """
    Generate LaTeX table for top cosmic constant alternatives.

    Args:
        top_n: Number of top alternatives to include

    Returns:
        LaTeX table code
    """
    if not COSMIC_FILE.exists():
        return "% ERROR: Cosmic alternatives file not found\n"

    df = pd.read_csv(COSMIC_FILE).head(top_n)

    # Load summary for our baseline
    if LEE_SUMMARY_FILE.exists():
        with open(LEE_SUMMARY_FILE, 'r') as f:
            lee = json.load(f)
        our_percentile = lee["alpha_phi_performance"]["percentile"]
    else:
        our_percentile = 0.0

    table = r"""
\begin{table}[htbp]
\centering
\caption{Top 10 Constant Combinations (Look-Elsewhere Effect Scan)}
\label{tab:cosmic_alternatives}
\small
\begin{tabular}{clcc}
\toprule
\textbf{Rank} & \textbf{Formula} & \textbf{$v_{\text{pred}}$ (km/s)} & \textbf{Deviation (km/s)} \\
\midrule
"""

    for idx, row in enumerate(df.itertuples(), start=1):
        # Highlight alpha-phi if present
        formula = row.formula.replace("_", "\\_")

        if "alpha" in formula and "phi" in formula:
            formula = r"\textbf{" + formula + "}"

        table += f"{idx} & {formula} & {row.v_pred:.1f} & {row.deviation:.1f} \\\\\n"

    table += r"""\bottomrule
\end{tabular}
\vspace{0.3cm}
\begin{tablenotes}
\small
\item Target: $v_{\text{obs}} = 1370 \pm 10$ km/s (Böhme et al., 2021).
\item \textbf{Look-Elsewhere Penalty:} $\alpha$-$\Phi$ formula ranks in top """ + f"{100-our_percentile:.1f}" + r"""\% of tested pairs.
\end{tablenotes}
\end{table}
"""

    return table


def generate_crisis_events_table() -> str:
    """
    Generate table of crisis events with predicted susceptibility.

    Returns:
        LaTeX table code
    """
    if not PANEL_FILE.exists():
        return "% ERROR: Historical panel file not found\n"

    panel = pd.read_csv(PANEL_FILE)
    crises = panel[panel["Crisis_Event"] == 1].copy()

    if len(crises) == 0:
        return "% No crisis events in data\n"

    # Load fitted parameters
    if PARAMS_FILE.exists():
        with open(PARAMS_FILE, 'r') as f:
            params = json.load(f)
        J = params["crisis_optimized"]["J"]
        h = params["crisis_optimized"]["h"]

        # Compute susceptibility
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from models.social_rigidity_ising import SocialIsingModel

        model = SocialIsingModel(coupling_strength=J, external_field=h)

        chi_values = []
        for _, row in crises.iterrows():
            state = model.compute_state(row["Gini"], row["Load"])
            chi_values.append(state.susceptibility)

        crises["Susceptibility"] = chi_values
    else:
        crises["Susceptibility"] = 0.0

    # Sort by year
    crises = crises.sort_values("Year")

    table = r"""
\begin{table}[htbp]
\centering
\caption{Historical Crisis Events and Theoretical Susceptibility}
\label{tab:crisis_events}
\begin{tabular}{llccc}
\toprule
\textbf{Country} & \textbf{Year} & \textbf{Gini} & \textbf{$\chi$} & \textbf{Event} \\
\midrule
"""

    for row in crises.itertuples():
        country = row.Country
        year = row.Year
        gini = row.Gini
        chi = row.Susceptibility
        event = row.Crisis_Description if hasattr(row, 'Crisis_Description') else "Crisis"

        table += f"{country} & {year} & {gini:.2f} & {chi:.2f} & {event} \\\\\n"

    table += r"""\bottomrule
\end{tabular}
\end{table}
"""

    return table


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Generate all LaTeX tables."""

    print("=" * 70)
    print("LATEX TABLE GENERATION (UTAC v5.0)")
    print("=" * 70)
    print()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate tables
    tables = {
        "ising_parameters": generate_ising_parameters_table(),
        "ising_diagnostics": generate_ising_diagnostics_table(),
        "cosmic_alternatives": generate_cosmic_alternatives_table(top_n=10),
        "crisis_events": generate_crisis_events_table()
    }

    # Save individual tables
    for name, content in tables.items():
        output_file = OUTPUT_DIR / f"table_{name}.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        print(f"  ✓ Saved: {output_file.name}")

    # Save combined file
    combined_file = OUTPUT_DIR / "all_tables.tex"
    with open(combined_file, 'w') as f:
        f.write("% AUTO-GENERATED TABLES FOR UTAC V5.0 MANUSCRIPT\n")
        f.write("% Generated by scripts/paper/generate_latex_tables.py\n\n")
        for name, content in tables.items():
            f.write(f"% TABLE: {name}\n")
            f.write(content)
            f.write("\n\n")

    print(f"  ✓ Saved: {combined_file.name}")
    print()

    print("=" * 70)
    print("TABLE GENERATION COMPLETE")
    print("=" * 70)
    print()
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    print("NEXT STEP:")
    print("  Compile manuscript: python scripts/paper/compile_manuscript.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
