#!/usr/bin/env python3
"""Urban Heat Island Cubic-Root Jump Validation

Experiment A from UTAC Type-6 Falsification Plan
=================================================

Tests the cubic-root jump mechanism for extreme-β outliers:
    β(R) = k · ∛(R/Θ - 1) + β_base

Falsification criteria:
1. Cubic-root exponent p ≠ 1/3 (95% CI excludes 0.333)
2. β does not spike (β < 12) when R/Θ → 1
3. Inverted sigmoid does not outperform classical (ΔAIC ≤ 10)
4. Early warning thresholds fail >70% of cities

Usage:
    python urban_heat_cubic_fit.py --input data/implosion/urban_heat_catalog.csv \
                                    --out paper/figures/cubic_root_jump_heat.png

References:
- Falsification Plan: docs/utac_type6_falsification_plan.md
- Theory: docs/utac_type6_implosive_origin_theory.md
- Model: models/utac_type6_implosive.py

Author: Johann B. Römer et al.
Date: 2025-11-12
License: AGPL-3.0
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, stats

# Add models to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.utac_type6_implosive import (
    BETA_FIXPOINT_PHI3,
    PHI_CBRT,
    cubic_root_jump,
    inverted_sigmoid,
)

# Optional plotting
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available, plots will be skipped")


def load_urban_heat_data(filepath: str) -> pd.DataFrame:
    """Load urban heat catalog, skipping comment lines."""
    df = pd.read_csv(filepath, comment='#')
    # Remove any completely empty rows
    df = df.dropna(how='all')
    return df


def fit_cubic_root_exponent(
    R_over_Theta: np.ndarray,
    beta: np.ndarray,
    beta_base: float = BETA_FIXPOINT_PHI3,
) -> dict:
    """Fit exponent p in β(R) = k · (R/Θ - 1)^p + β_base.

    Falsification test: Does 95% CI include p = 1/3?

    Parameters
    ----------
    R_over_Theta : ndarray
        R/Θ ratios (should include values near 1.0)
    beta : ndarray
        Observed β values
    beta_base : float
        Baseline β far from threshold (default: Φ³ ≈ 4.236)

    Returns
    -------
    results : dict
        - p_fit: Best-fit exponent
        - p_ci_lower, p_ci_upper: 95% confidence interval
        - k_fit: Amplification coefficient
        - r_squared: Goodness of fit
        - falsified: True if 95% CI excludes p=1/3
    """
    # Only fit to critical regime (R/Θ > 0.95) where cubic root dominates
    critical_mask = R_over_Theta > 0.95

    if critical_mask.sum() < 3:
        return {
            'p_fit': np.nan,
            'p_ci_lower': np.nan,
            'p_ci_upper': np.nan,
            'k_fit': np.nan,
            'r_squared': np.nan,
            'falsified': None,
            'message': 'Insufficient critical regime data (need R/Θ > 0.95)',
        }

    R_crit = R_over_Theta[critical_mask]
    beta_crit = beta[critical_mask]

    # Define power-law model: β = k · (R/Θ - 1)^p + β_base
    def power_model(R_ratio, k, p):
        proximity = np.maximum(R_ratio - 1.0, 1e-9)
        return k * proximity ** p + beta_base

    try:
        # Fit with initial guess p=1/3, k=10
        popt, pcov = optimize.curve_fit(
            power_model,
            R_crit,
            beta_crit,
            p0=[10.0, 1.0/3.0],
            maxfev=10000,
        )

        k_fit, p_fit = popt

        # 95% confidence intervals from covariance matrix
        perr = np.sqrt(np.diag(pcov))
        k_ci_width = 1.96 * perr[0]
        p_ci_width = 1.96 * perr[1]

        p_ci_lower = p_fit - p_ci_width
        p_ci_upper = p_fit + p_ci_width

        # R² for goodness of fit
        beta_pred = power_model(R_crit, k_fit, p_fit)
        ss_res = np.sum((beta_crit - beta_pred) ** 2)
        ss_tot = np.sum((beta_crit - beta_crit.mean()) ** 2)
        r_squared = 1.0 - ss_res / ss_tot

        # Falsification test: Does 95% CI exclude p=1/3?
        p_target = 1.0 / 3.0
        falsified = not (p_ci_lower <= p_target <= p_ci_upper)

        return {
            'p_fit': p_fit,
            'p_ci_lower': p_ci_lower,
            'p_ci_upper': p_ci_upper,
            'k_fit': k_fit,
            'r_squared': r_squared,
            'falsified': falsified,
            'message': 'Fit converged',
        }

    except Exception as e:
        return {
            'p_fit': np.nan,
            'p_ci_lower': np.nan,
            'p_ci_upper': np.nan,
            'k_fit': np.nan,
            'r_squared': np.nan,
            'falsified': None,
            'message': f'Fit failed: {e}',
        }


def test_early_warning_thresholds(df: pd.DataFrame) -> dict:
    """Test operational early warning thresholds.

    Predictions:
    - YELLOW (R/Θ > 0.90): Next-season β rise
    - RED (R/Θ > 0.95): Current-season β jump

    Falsify if thresholds fail to distinguish regimes >70% of time.

    Parameters
    ----------
    df : DataFrame
        Urban heat catalog with R_over_Theta and beta columns

    Returns
    -------
    results : dict
        - yellow_accuracy: Fraction correctly classified
        - red_accuracy: Fraction correctly classified
        - falsified: True if accuracy < 0.30 (fails >70%)
    """
    # YELLOW threshold: R/Θ > 0.90 predicts β > 6.0
    yellow_mask = df['R_over_Theta'] > 0.90
    yellow_correct = ((yellow_mask & (df['beta_inverted'] > 6.0)) |
                      (~yellow_mask & (df['beta_inverted'] <= 6.0)))
    yellow_accuracy = yellow_correct.mean()

    # RED threshold: R/Θ > 0.95 predicts β > 12.0
    red_mask = df['R_over_Theta'] > 0.95
    red_correct = ((red_mask & (df['beta_inverted'] > 12.0)) |
                   (~red_mask & (df['beta_inverted'] <= 12.0)))
    red_accuracy = red_correct.mean()

    # Falsify if either threshold fails >70% (accuracy < 0.30)
    falsified = (yellow_accuracy < 0.30) or (red_accuracy < 0.30)

    return {
        'yellow_accuracy': yellow_accuracy,
        'red_accuracy': red_accuracy,
        'falsified': falsified,
        'message': 'FALSIFIED' if falsified else 'VALIDATED',
    }


def test_sigmoid_preference(df: pd.DataFrame) -> dict:
    """Test whether inverted sigmoid outperforms classical in critical regime.

    Prediction: Inverted sigmoid wins by ΔAIC > 10 when R/Θ > 0.95.
    Falsify if classical consistently wins by ΔAIC > 10.

    Parameters
    ----------
    df : DataFrame
        Catalog with delta_aic column (positive = inverted better)

    Returns
    -------
    results : dict
        - critical_inverted_wins: Fraction where inverted wins in critical regime
        - mean_delta_aic_critical: Mean ΔAIC in critical regime
        - falsified: True if classical wins >70% with ΔAIC > 10
    """
    critical = df[df['R_over_Theta'] > 0.95]

    if len(critical) == 0:
        return {
            'critical_inverted_wins': np.nan,
            'mean_delta_aic_critical': np.nan,
            'falsified': None,
            'message': 'No critical regime data',
        }

    # ΔAIC > 0 means inverted wins
    inverted_wins = (critical['delta_aic'] > 0).mean()
    mean_delta_aic = critical['delta_aic'].mean()

    # Falsify if classical wins >70% with strong preference (ΔAIC < -10)
    classical_strong_wins = (critical['delta_aic'] < -10).mean()
    falsified = classical_strong_wins > 0.70

    return {
        'critical_inverted_wins': inverted_wins,
        'mean_delta_aic_critical': mean_delta_aic,
        'falsified': falsified,
        'message': 'FALSIFIED' if falsified else 'VALIDATED',
    }


def test_beta_spike(df: pd.DataFrame) -> dict:
    """Test whether β spikes (≥12) in critical regime (0.95 < R/Θ < 1.05).

    Falsify if β does not spike in critical regime.

    Parameters
    ----------
    df : DataFrame
        Catalog with R_over_Theta and beta_inverted columns

    Returns
    -------
    results : dict
        - mean_beta_critical: Mean β in critical regime
        - fraction_spike: Fraction with β ≥ 12 in critical regime
        - falsified: True if no spikes observed
    """
    critical = df[(df['R_over_Theta'] > 0.95) & (df['R_over_Theta'] < 1.05)]

    if len(critical) == 0:
        return {
            'mean_beta_critical': np.nan,
            'fraction_spike': np.nan,
            'falsified': None,
            'message': 'No critical regime data',
        }

    mean_beta = critical['beta_inverted'].mean()
    fraction_spike = (critical['beta_inverted'] >= 12.0).mean()

    # Falsify if <10% show β≥12 (no spike pattern)
    falsified = fraction_spike < 0.10

    return {
        'mean_beta_critical': mean_beta,
        'fraction_spike': fraction_spike,
        'falsified': falsified,
        'message': 'FALSIFIED' if falsified else 'VALIDATED',
    }


def create_validation_plots(df: pd.DataFrame, cubic_fit: dict, output_path: str):
    """Generate 4-panel validation figure."""
    if not HAS_MATPLOTLIB:
        print("Skipping plots (matplotlib not available)")
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel A: β vs R/Θ with cubic-root fit
    ax = axes[0, 0]
    critical = df[df['R_over_Theta'] > 0.95]
    subcritical = df[df['R_over_Theta'] <= 0.95]

    ax.scatter(subcritical['R_over_Theta'], subcritical['beta_inverted'],
               c='gray', alpha=0.6, s=80, label='Sub-critical')
    ax.scatter(critical['R_over_Theta'], critical['beta_inverted'],
               c='red', alpha=0.8, s=100, label='Critical (R/Θ>0.95)')

    # Plot cubic-root fit if available
    if not np.isnan(cubic_fit['p_fit']):
        R_range = np.linspace(0.95, df['R_over_Theta'].max(), 100)
        proximity = np.maximum(R_range - 1.0, 1e-9)
        beta_fit = cubic_fit['k_fit'] * proximity ** cubic_fit['p_fit'] + BETA_FIXPOINT_PHI3
        ax.plot(R_range, beta_fit, 'r--', linewidth=2,
                label=f'p={cubic_fit["p_fit"]:.3f} ± {cubic_fit["p_ci_upper"]-cubic_fit["p_fit"]:.3f}')

    ax.axhline(BETA_FIXPOINT_PHI3, color='blue', linestyle=':', linewidth=1.5,
               label=f'Φ³ fixpoint ({BETA_FIXPOINT_PHI3:.2f})')
    ax.axhline(12.0, color='orange', linestyle=':', linewidth=1.5,
               label='Spike threshold (β=12)')
    ax.axvline(0.95, color='orange', linestyle=':', alpha=0.5, label='Critical boundary')

    ax.set_xlabel('R/Θ (Thermal Storage / Threshold)', fontsize=11)
    ax.set_ylabel('β (Steepness)', fontsize=11)
    ax.set_title('A: Cubic-Root Jump Mechanism', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel B: ΔAIC comparison (inverted vs classical)
    ax = axes[0, 1]
    colors = ['green' if aic > 0 else 'purple' for aic in df['delta_aic']]
    ax.bar(range(len(df)), df['delta_aic'], color=colors, alpha=0.7)
    ax.axhline(0, color='black', linewidth=1)
    ax.axhline(10, color='green', linestyle='--', linewidth=1.5,
               label='Strong inverted preference')
    ax.axhline(-10, color='purple', linestyle='--', linewidth=1.5,
               label='Strong classical preference')
    ax.set_xlabel('City-Season Index', fontsize=11)
    ax.set_ylabel('ΔAIC (Inverted - Classical)', fontsize=11)
    ax.set_title('B: Sigmoid Type Preference', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')

    # Panel C: Early warning threshold performance
    ax = axes[1, 0]

    R_bins = [0, 0.9, 0.95, 2.0]
    bin_labels = ['Safe\n(R/Θ<0.9)', 'Yellow\n(0.9-0.95)', 'Red\n(R/Θ>0.95)']

    df['regime'] = pd.cut(df['R_over_Theta'], bins=R_bins, labels=bin_labels)
    regime_beta = df.groupby('regime')['beta_inverted'].mean()

    colors_regime = ['green', 'yellow', 'red']
    ax.bar(range(len(regime_beta)), regime_beta, color=colors_regime, alpha=0.7)
    ax.set_xticks(range(len(regime_beta)))
    ax.set_xticklabels(bin_labels, fontsize=10)
    ax.set_ylabel('Mean β', fontsize=11)
    ax.set_title('C: Early Warning Thresholds', fontsize=12, fontweight='bold')
    ax.axhline(BETA_FIXPOINT_PHI3, color='blue', linestyle=':', linewidth=1.5,
               label=f'Φ³ baseline ({BETA_FIXPOINT_PHI3:.2f})')
    ax.axhline(12.0, color='orange', linestyle=':', linewidth=1.5, label='Spike threshold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')

    # Panel D: City-season trajectory
    ax = axes[1, 1]

    # Group by city, plot seasonal trajectories
    for city in df['city'].unique():
        city_data = df[df['city'] == city].sort_values('season')
        ax.plot(city_data['R_over_Theta'], city_data['beta_inverted'],
                marker='o', linewidth=2, markersize=8, alpha=0.7, label=city)

    ax.axvline(0.95, color='orange', linestyle=':', alpha=0.5, label='Critical boundary')
    ax.axhline(BETA_FIXPOINT_PHI3, color='blue', linestyle=':', linewidth=1.5)
    ax.set_xlabel('R/Θ', fontsize=11)
    ax.set_ylabel('β', fontsize=11)
    ax.set_title('D: Seasonal Trajectories', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9, loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved validation plot: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Urban Heat Island Cubic-Root Jump Validation (UTAC Type-6 Experiment A)'
    )
    parser.add_argument('--input', default='data/implosion/urban_heat_catalog.csv',
                        help='Path to urban heat catalog CSV')
    parser.add_argument('--out', default='paper/figures/cubic_root_jump_heat.png',
                        help='Output path for validation figure')
    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed results')

    args = parser.parse_args()

    print("═" * 70)
    print("UTAC Type-6 Validation: Urban Heat Island Cubic-Root Jump")
    print("Experiment A from Falsification Plan")
    print("═" * 70)
    print()

    # Load data
    print(f"Loading data from: {args.input}")
    df = load_urban_heat_data(args.input)
    print(f"  → {len(df)} city-season observations loaded")
    print(f"  → Cities: {df['city'].unique().tolist()}")
    print()

    # Test 1: Cubic-root exponent
    print("─" * 70)
    print("TEST 1: Cubic-Root Exponent (β ∝ (R/Θ - 1)^p)")
    print("─" * 70)
    cubic_fit = fit_cubic_root_exponent(
        df['R_over_Theta'].values,
        df['beta_inverted'].values,
    )

    if not np.isnan(cubic_fit['p_fit']):
        print(f"  Best-fit exponent: p = {cubic_fit['p_fit']:.4f}")
        print(f"  95% CI: [{cubic_fit['p_ci_lower']:.4f}, {cubic_fit['p_ci_upper']:.4f}]")
        print(f"  Theoretical: p = 1/3 ≈ 0.3333")
        print(f"  R² = {cubic_fit['r_squared']:.4f}")
        print(f"  Amplification: k = {cubic_fit['k_fit']:.2f}")
        print()

        if cubic_fit['falsified']:
            print("  ⚠️  FALSIFIED: 95% CI excludes p = 1/3")
        else:
            print("  ✓ VALIDATED: 95% CI includes p = 1/3")
    else:
        print(f"  ⚠️  {cubic_fit['message']}")

    print()

    # Test 2: β spike in critical regime
    print("─" * 70)
    print("TEST 2: β Spike in Critical Regime (0.95 < R/Θ < 1.05)")
    print("─" * 70)
    spike_test = test_beta_spike(df)

    if not np.isnan(spike_test['mean_beta_critical']):
        print(f"  Mean β (critical): {spike_test['mean_beta_critical']:.2f}")
        print(f"  Fraction β ≥ 12: {spike_test['fraction_spike']:.2%}")
        print()

        if spike_test['falsified']:
            print("  ⚠️  FALSIFIED: No β spike observed in critical regime")
        else:
            print("  ✓ VALIDATED: β spikes near R/Θ → 1")
    else:
        print(f"  ⚠️  {spike_test['message']}")

    print()

    # Test 3: Inverted sigmoid preference
    print("─" * 70)
    print("TEST 3: Inverted Sigmoid Preference (ΔAIC)")
    print("─" * 70)
    sigmoid_test = test_sigmoid_preference(df)

    if not np.isnan(sigmoid_test['critical_inverted_wins']):
        print(f"  Inverted wins (critical): {sigmoid_test['critical_inverted_wins']:.2%}")
        print(f"  Mean ΔAIC (critical): {sigmoid_test['mean_delta_aic_critical']:.2f}")
        print()

        if sigmoid_test['falsified']:
            print("  ⚠️  FALSIFIED: Classical sigmoid dominates")
        else:
            print("  ✓ VALIDATED: Inverted sigmoid preferred in critical regime")
    else:
        print(f"  ⚠️  {sigmoid_test['message']}")

    print()

    # Test 4: Early warning thresholds
    print("─" * 70)
    print("TEST 4: Early Warning Thresholds")
    print("─" * 70)
    threshold_test = test_early_warning_thresholds(df)

    print(f"  YELLOW (R/Θ > 0.90) accuracy: {threshold_test['yellow_accuracy']:.2%}")
    print(f"  RED (R/Θ > 0.95) accuracy: {threshold_test['red_accuracy']:.2%}")
    print()

    if threshold_test['falsified']:
        print("  ⚠️  FALSIFIED: Thresholds fail >70% of time")
    else:
        print("  ✓ VALIDATED: Thresholds distinguish regimes reliably")

    print()

    # Summary
    print("═" * 70)
    print("SUMMARY")
    print("═" * 70)

    tests = [cubic_fit, spike_test, sigmoid_test, threshold_test]
    falsified_count = sum(1 for t in tests if t.get('falsified') == True)
    validated_count = sum(1 for t in tests if t.get('falsified') == False)

    print(f"  Tests run: 4")
    print(f"  Validated: {validated_count}")
    print(f"  Falsified: {falsified_count}")
    print(f"  Inconclusive: {4 - validated_count - falsified_count}")
    print()

    if falsified_count >= 2:
        print("  ⚠️  TYPE-6 MATERIALLY FALSIFIED (≥2 core claims failed)")
    elif falsified_count == 1:
        print("  ⚠️  REVISION NEEDED (1 claim failed; framework requires refinement)")
    elif validated_count >= 3:
        print("  ✓ TYPE-6 PROVISIONALLY VALIDATED (awaiting expanded dataset)")
    else:
        print("  ○ INCONCLUSIVE (insufficient data for validation)")

    print()

    # Generate plots
    if HAS_MATPLOTLIB:
        print("─" * 70)
        print("Generating validation plots...")
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        create_validation_plots(df, cubic_fit, args.out)

    print("═" * 70)
    print("Analysis complete.")
    print("═" * 70)


if __name__ == '__main__':
    main()
