"""
Historical Data Ingestion for Social Ising Model Validation (UTAC v5.0)

This script ingests real-world inequality and stability data to test whether
the theoretical Social Ising Model (T = 1/(Gini·Load)) can predict historical
phase transitions (revolutions, collapses, stability shifts).

Data Sources:
    1. World Bank Gini Index (or synthetic proxies)
    2. Fragile States Index (Fund for Peace)
    3. Historical crisis events (revolutions, collapses)

Output:
    - data/grounding/historical_panel.csv

Author: Genesis Aeon (UTAC Framework)
Version: 5.0 "Empirical Grounding"
"""

from pathlib import Path

import numpy as np
import pandas as pd

# ============================================================================
# CONFIGURATION
# ============================================================================

OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "grounding"
OUTPUT_FILE = OUTPUT_DIR / "historical_panel.csv"

# Countries for analysis (select historical data-rich cases)
FOCUS_COUNTRIES = [
    "United States",
    "China",
    "France",
    "Germany",
    "Brazil",
    "South Africa",
    "Russia",
    "India",
]

# Time range
START_YEAR = 1990
END_YEAR = 2024


# ============================================================================
# SYNTHETIC DATA GENERATION (Placeholder for Real API Integration)
# ============================================================================


def generate_synthetic_gini_data() -> pd.DataFrame:
    """
    Generate synthetic Gini coefficient data.

    In production, replace with:
        - World Bank API (wbdata library)
        - OECD data
        - UNU-WIDER WIID database

    Returns:
        DataFrame with columns: Country, Year, Gini
    """
    np.random.seed(42)

    data = []

    # Country-specific baseline Gini + trend
    country_params = {
        "United States": {"base": 0.38, "trend": 0.004, "volatility": 0.02},
        "China": {"base": 0.42, "trend": 0.003, "volatility": 0.03},
        "France": {"base": 0.30, "trend": 0.001, "volatility": 0.01},
        "Germany": {"base": 0.29, "trend": 0.002, "volatility": 0.015},
        "Brazil": {"base": 0.53, "trend": -0.002, "volatility": 0.025},
        "South Africa": {"base": 0.63, "trend": 0.001, "volatility": 0.02},
        "Russia": {"base": 0.40, "trend": 0.002, "volatility": 0.03},
        "India": {"base": 0.35, "trend": 0.003, "volatility": 0.02},
    }

    for country in FOCUS_COUNTRIES:
        params = country_params[country]

        for year in range(START_YEAR, END_YEAR + 1):
            t = year - START_YEAR

            # Trend + noise
            gini = params["base"] + params["trend"] * t + np.random.normal(0, params["volatility"])

            # Clamp to valid range
            gini = np.clip(gini, 0.20, 0.70)

            data.append({"Country": country, "Year": year, "Gini": gini})

    return pd.DataFrame(data)


def generate_synthetic_stability_data() -> pd.DataFrame:
    """
    Generate synthetic stability scores.

    In production, replace with:
        - Fragile States Index (Fund for Peace)
        - Polity IV Democracy Index
        - World Bank Governance Indicators

    Returns:
        DataFrame with columns: Country, Year, Stability_Score

    Stability_Score: 0 (collapsed) to 100 (perfectly stable)
    """
    np.random.seed(43)

    data = []

    # Country-specific baseline stability
    country_stability = {
        "United States": {"base": 85, "volatility": 3},
        "China": {"base": 70, "volatility": 5},
        "France": {"base": 88, "volatility": 2},
        "Germany": {"base": 90, "volatility": 2},
        "Brazil": {"base": 65, "volatility": 6},
        "South Africa": {"base": 55, "volatility": 8},
        "Russia": {"base": 60, "volatility": 7},
        "India": {"base": 70, "volatility": 5},
    }

    for country in FOCUS_COUNTRIES:
        params = country_stability[country]

        for year in range(START_YEAR, END_YEAR + 1):
            # Add historical shocks (simplified)
            shock = 0
            if country == "United States" and year == 2020:
                shock = -5  # Political crisis
            elif country == "Russia" and year == 2022:
                shock = -10  # Ukraine war
            elif country == "Brazil" and year in [2015, 2016]:
                shock = -8  # Political crisis

            stability = params["base"] + shock + np.random.normal(0, params["volatility"])

            stability = np.clip(stability, 0, 100)

            data.append({"Country": country, "Year": year, "Stability_Score": stability})

    return pd.DataFrame(data)


def compute_load_proxy(gini_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute cognitive/economic load proxy.

    For now, use a simple heuristic:
        Load = 1 + (Gini - 0.25) * 2

    This gives Load ∈ [1, 2] approximately, with higher inequality → higher load.

    In production, integrate:
        - GDP per capita (World Bank)
        - Unemployment rate (ILO)
        - Inflation rate (IMF)

    Args:
        gini_df: DataFrame with Gini data

    Returns:
        DataFrame with added Load column
    """
    load = 1.0 + (gini_df["Gini"] - 0.25) * 2.0
    gini_df["Load"] = load.clip(0.5, 3.0)
    return gini_df


# ============================================================================
# MAIN HARMONIZATION
# ============================================================================


def harmonize_data() -> pd.DataFrame:
    """
    Combine all data sources into unified panel.

    Returns:
        DataFrame with columns: Country, Year, Gini, Load, Stability_Score
    """
    # Generate/ingest data
    gini_df = generate_synthetic_gini_data()
    stability_df = generate_synthetic_stability_data()

    # Add load proxy
    gini_df = compute_load_proxy(gini_df)

    # Merge
    panel = pd.merge(gini_df, stability_df, on=["Country", "Year"], how="inner")

    # Sort
    panel = panel.sort_values(["Country", "Year"]).reset_index(drop=True)

    return panel


def annotate_crisis_events(panel: pd.DataFrame) -> pd.DataFrame:
    """
    Add binary indicator for known crisis events.

    Crisis events (simplified historical markers):
        - Major revolutions
        - Economic collapses
        - Political transitions

    Args:
        panel: Historical panel data

    Returns:
        Panel with added Crisis_Event column (0/1)
    """
    # Initialize
    panel["Crisis_Event"] = 0

    # Known crises (simplified)
    crisis_markers = [
        ("Russia", 1998, "Economic collapse"),
        ("Brazil", 2016, "Political crisis"),
        ("South Africa", 2008, "Political transition"),
        ("United States", 2008, "Financial crisis"),
        ("United States", 2020, "Political crisis"),
        ("Russia", 2022, "War initiation"),
    ]

    for country, year, description in crisis_markers:
        mask = (panel["Country"] == country) & (panel["Year"] == year)
        panel.loc[mask, "Crisis_Event"] = 1
        panel.loc[mask, "Crisis_Description"] = description

    # Fill missing descriptions
    panel["Crisis_Description"] = panel["Crisis_Description"].fillna("None")

    return panel


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """Ingest and harmonize all historical data."""

    print("=" * 70)
    print("HISTORICAL DATA INGESTION (UTAC v5.0)")
    print("=" * 70)
    print()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Harmonize data
    print("Harmonizing data sources...")
    panel = harmonize_data()

    # Annotate crises
    print("Annotating crisis events...")
    panel = annotate_crisis_events(panel)

    # Summary statistics
    print()
    print("PANEL SUMMARY:")
    print(f"  Countries:    {panel['Country'].nunique()}")
    print(f"  Years:        {panel['Year'].min()} - {panel['Year'].max()}")
    print(f"  Observations: {len(panel)}")
    print(f"  Crisis events: {panel['Crisis_Event'].sum()}")
    print()

    print("GINI STATISTICS:")
    print(f"  Mean:  {panel['Gini'].mean():.3f}")
    print(f"  Std:   {panel['Gini'].std():.3f}")
    print(f"  Range: [{panel['Gini'].min():.3f}, {panel['Gini'].max():.3f}]")
    print()

    print("STABILITY STATISTICS:")
    print(f"  Mean:  {panel['Stability_Score'].mean():.1f}")
    print(f"  Std:   {panel['Stability_Score'].std():.1f}")
    print(f"  Range: [{panel['Stability_Score'].min():.1f}, {panel['Stability_Score'].max():.1f}]")
    print()

    # Save
    panel.to_csv(OUTPUT_FILE, index=False)
    print(f"✓ Saved to: {OUTPUT_FILE}")
    print()

    # Preview
    print("PREVIEW (first 10 rows):")
    print(panel.head(10).to_string(index=False))
    print()

    print("=" * 70)
    print("DATA INGESTION COMPLETE")
    print("=" * 70)
    print()
    print("NEXT STEPS:")
    print("  1. Run parameter fitting: scripts/grounding/fit_ising_parameters.py")
    print("  2. Visualize results: scripts/grounding/visualize_history_vs_theory.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
