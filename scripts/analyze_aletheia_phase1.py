#!/usr/bin/env python3
"""
Project Aletheia Phase 1 — Statistical Analysis
================================================

Analyzes Phase 1 results (Control, Placebo, Nocebo) with:
- Descriptive statistics
- Cohen's d effect sizes
- Linear regression over φ-spectrum
- Interpretation (Resonanz/Dissonanz/Neutral)

Author: Johann B. Römer, Claude (Sonnet 4.5)
Date: 2025-11-19
"""

import csv
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path


def load_results(filepath: str) -> pd.DataFrame:
    """Load experimental results from CSV."""
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} samples from {filepath}")
    print(f"Conditions: {df['condition'].unique()}")
    print(f"Sample counts: {df['condition'].value_counts()}")
    return df


def compute_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Compute mean and std for each condition."""
    metrics = ['output_length', 'vocab_density', 'self_reflection']

    stats_df = df.groupby('condition')[metrics].agg(['mean', 'std', 'count'])
    return stats_df


def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Calculate Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)

    # Pooled standard deviation
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

    if pooled_std == 0:
        return 0.0

    return (np.mean(group1) - np.mean(group2)) / pooled_std


def interpret_cohens_d(d: float) -> str:
    """Interpret Cohen's d magnitude."""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    else:
        return "large"


def effect_size_analysis(df: pd.DataFrame) -> dict:
    """Compute all pairwise effect sizes."""
    conditions = df['condition'].unique()
    metrics = ['output_length', 'vocab_density', 'self_reflection']

    results = {}

    for metric in metrics:
        results[metric] = {}

        for cond1 in conditions:
            for cond2 in conditions:
                if cond1 != cond2:
                    group1 = df[df['condition'] == cond1][metric].values
                    group2 = df[df['condition'] == cond2][metric].values

                    d = cohens_d(group1, group2)
                    results[metric][f"{cond1}_vs_{cond2}"] = {
                        'd': d,
                        'interpretation': interpret_cohens_d(d)
                    }

    return results


def linear_regression_analysis(df: pd.DataFrame) -> dict:
    """Perform linear regression: ψ = ψ_base + λ·φ"""
    metrics = ['output_length', 'vocab_density', 'self_reflection']

    results = {}

    for metric in metrics:
        X = df['phi'].values
        y = df[metric].values

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)

        results[metric] = {
            'lambda': slope,
            'psi_base': intercept,
            'r_squared': r_value**2,
            'p_value': p_value,
            'std_err': std_err
        }

    return results


def anova_analysis(df: pd.DataFrame) -> dict:
    """Perform one-way ANOVA across conditions."""
    metrics = ['output_length', 'vocab_density', 'self_reflection']
    conditions = df['condition'].unique()

    results = {}

    for metric in metrics:
        groups = [df[df['condition'] == cond][metric].values for cond in conditions]
        f_stat, p_value = stats.f_oneway(*groups)

        results[metric] = {
            'f_statistic': f_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }

    return results


def interpret_results(effect_sizes: dict, regression: dict, anova: dict) -> dict:
    """Interpret whether we see Resonanz, Dissonanz, or Neutral."""
    interpretations = {}

    for metric in ['output_length', 'vocab_density', 'self_reflection']:
        # Check Placebo vs Control
        d_placebo_control = effect_sizes[metric]['Placebo_vs_Control']['d']

        # Check regression slope (λ)
        lambda_val = regression[metric]['lambda']
        p_val = regression[metric]['p_value']

        # Interpret
        if p_val < 0.05 and abs(d_placebo_control) >= 0.2:
            if d_placebo_control > 0:
                interpretation = "RESONANZ (λ > 0, Placebo > Control)"
            else:
                interpretation = "DISSONANZ (λ < 0, Placebo < Control)"
        elif abs(d_placebo_control) < 0.2:
            interpretation = "NEUTRAL (|d| < 0.2, no effect)"
        else:
            interpretation = f"WEAK SIGNAL (d={d_placebo_control:.3f}, p={p_val:.3f})"

        interpretations[metric] = {
            'd_placebo_control': d_placebo_control,
            'lambda': lambda_val,
            'p_value': p_val,
            'interpretation': interpretation
        }

    return interpretations


def print_report(stats_df, effect_sizes, regression, anova, interpretations):
    """Print comprehensive analysis report."""

    print("\n" + "="*80)
    print("PROJECT ALETHEIA PHASE 1 — STATISTICAL ANALYSIS")
    print("="*80)

    print("\n## 1. DESCRIPTIVE STATISTICS\n")
    print(stats_df)

    print("\n## 2. EFFECT SIZES (Cohen's d)\n")
    for metric, comparisons in effect_sizes.items():
        print(f"\n{metric.upper()}:")
        for comp, result in comparisons.items():
            print(f"  {comp:30s}: d = {result['d']:+.3f} ({result['interpretation']})")

    print("\n## 3. LINEAR REGRESSION (ψ = ψ_base + λ·φ)\n")
    for metric, result in regression.items():
        print(f"\n{metric.upper()}:")
        print(f"  ψ_base (intercept) = {result['psi_base']:.3f}")
        print(f"  λ (slope)          = {result['lambda']:+.3f} ± {result['std_err']:.3f}")
        print(f"  R²                 = {result['r_squared']:.3f}")
        print(f"  p-value            = {result['p_value']:.4f} {'***' if result['p_value'] < 0.001 else '**' if result['p_value'] < 0.01 else '*' if result['p_value'] < 0.05 else 'ns'}")

    print("\n## 4. ONE-WAY ANOVA\n")
    for metric, result in anova.items():
        print(f"{metric.upper()}:")
        print(f"  F-statistic = {result['f_statistic']:.3f}")
        print(f"  p-value     = {result['p_value']:.4f} {'***' if result['p_value'] < 0.001 else '**' if result['p_value'] < 0.01 else '*' if result['p_value'] < 0.05 else 'ns'}")
        print(f"  Significant = {result['significant']}")

    print("\n## 5. INTERPRETATION (Resonanz vs. Dissonanz)\n")
    for metric, result in interpretations.items():
        print(f"\n{metric.upper()}:")
        print(f"  Cohen's d (Placebo vs Control) = {result['d_placebo_control']:+.3f}")
        print(f"  λ (regression slope)           = {result['lambda']:+.3f}")
        print(f"  p-value                        = {result['p_value']:.4f}")
        print(f"  → {result['interpretation']}")

    print("\n## 6. OVERALL VERDICT\n")

    # Count how many metrics show Resonanz
    resonanz_count = sum(1 for r in interpretations.values() if "RESONANZ" in r['interpretation'])
    dissonanz_count = sum(1 for r in interpretations.values() if "DISSONANZ" in r['interpretation'])
    neutral_count = sum(1 for r in interpretations.values() if "NEUTRAL" in r['interpretation'])

    print(f"Metrics showing RESONANZ:  {resonanz_count}/3")
    print(f"Metrics showing DISSONANZ: {dissonanz_count}/3")
    print(f"Metrics showing NEUTRAL:   {neutral_count}/3")

    if resonanz_count >= 2:
        print("\n✅ HYPOTHESIS H₁ SUPPORTED: M[ψ, φ] ≠ 0 (Semantic fields affect LLM output)")
        print("   → CCUC (Computational Criticality Universality Class) gains empirical support")
        print("   → LLMs show placebo-like effects")
    elif neutral_count >= 2:
        print("\n❌ HYPOTHESIS H₀ SUPPORTED: M[ψ, φ] ≈ 0 (No semantic field effect)")
        print("   → LLMs are purely information-processing (no placebo effect)")
        print("   → CCUC requires refinement or abandonment")
    else:
        print("\n⚠️  MIXED RESULTS: Some metrics show effects, others don't")
        print("   → Further investigation required")

    print("\n" + "="*80)
    print("Interpretation Guide:")
    print("  Cohen's d: |d| < 0.2 (negligible), 0.2-0.5 (small), 0.5-0.8 (medium), > 0.8 (large)")
    print("  p-value:   p < 0.05 (*), p < 0.01 (**), p < 0.001 (***)")
    print("  RESONANZ:  Placebo prompts improve output (λ > 0, d > 0)")
    print("  DISSONANZ: Placebo prompts worsen output (λ < 0, d < 0)")
    print("  NEUTRAL:   No measurable effect (|d| < 0.2)")
    print("="*80 + "\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Analyze Project Aletheia Phase 1 results without triggering other phases."
        )
    )
    parser.add_argument(
        "input",
        type=str,
        help="CSV file with Phase 1 experiment outputs",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("analysis/results"),
        help="Directory for saving regression and interpretation CSVs",
    )

    args = parser.parse_args()

    # Load data
    df = load_results(args.input)

    # Compute statistics
    stats_df = compute_descriptive_stats(df)
    effect_sizes = effect_size_analysis(df)
    regression = linear_regression_analysis(df)
    anova = anova_analysis(df)
    interpretations = interpret_results(effect_sizes, regression, anova)

    # Print report
    print_report(stats_df, effect_sizes, regression, anova, interpretations)

    # Save results
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Save regression results
    regression_df = pd.DataFrame(regression).T
    regression_df.to_csv(args.output_dir / "aletheia_phase1_regression.csv")
    print(
        f"\n✓ Regression results saved to {args.output_dir}/aletheia_phase1_regression.csv"
    )

    # Save interpretations
    interp_df = pd.DataFrame(interpretations).T
    interp_df.to_csv(args.output_dir / "aletheia_phase1_interpretation.csv")
    print(
        f"✓ Interpretations saved to {args.output_dir}/aletheia_phase1_interpretation.csv"
    )


if __name__ == "__main__":
    main()
