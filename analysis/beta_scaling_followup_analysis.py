#!/usr/bin/env python3
"""
Beta Scaling Follow-up Analysis: Post-Φ Falsification
======================================================

After falsifying the Φ-scaling hypothesis, we investigate:
1. Field Type cluster-specific growth factors
2. β correlation with effective dimensionality (D_eff)
3. Mathematical meaning of observed factor 1.18

Author: Claude Code, Johann Römer
Date: 2025-11-11
Version: 1.0
"""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

# Known mathematical constants for comparison
CONSTANTS = {
    'phi': 1.61803398875,
    'phi_cbrt': 1.61803398875**(1/3),  # Φ^(1/3) ≈ 1.176
    'phi_sqrt': 1.61803398875**0.5,    # √Φ ≈ 1.272
    'e_sixth': np.e**(1/6),            # e^(1/6) ≈ 1.181
    'sqrt_2_cbrt': 2**(1/6),           # 2^(1/6) ≈ 1.122
    'sqrt_3_cbrt': 3**(1/6),           # 3^(1/6) ≈ 1.201
}


def load_data(beta_path, covariate_path):
    """Load beta estimates and domain covariates."""
    beta_df = pd.read_csv(beta_path)
    cov_df = pd.read_csv(covariate_path)

    # Merge datasets
    df = pd.merge(beta_df, cov_df, on='domain', how='inner')

    return df


def analyze_field_type_clusters(df):
    """
    Research Question 1: Is the growth factor domain-cluster specific?

    Compute growth factors (ratios) for each Field Type separately.
    """
    print("\n" + "="*60)
    print("RESEARCH QUESTION 1: Field Type Cluster Analysis")
    print("="*60)

    results = {}

    # Group by field type
    field_types = df['field_type'].unique()

    for ft in sorted(field_types):
        subset = df[df['field_type'] == ft].copy()

        # Sort by beta
        subset = subset.sort_values('beta')
        betas = subset['beta'].values

        if len(betas) < 2:
            print(f"\n{ft}: Insufficient data (n={len(betas)})")
            continue

        # Compute ratios
        ratios = betas[1:] / betas[:-1]

        # Statistics
        mean_ratio = float(np.mean(ratios))
        std_ratio = float(np.std(ratios, ddof=1)) if len(ratios) > 1 else 0.0

        print(f"\n{ft}:")
        print(f"  n = {len(betas)} systems")
        print(f"  β-range: [{betas.min():.2f}, {betas.max():.2f}]")
        print(f"  Ratios: {[f'{r:.3f}' for r in ratios]}")
        print(f"  Mean ratio: {mean_ratio:.3f} ± {std_ratio:.3f}")

        # Test against global mean (1.18)
        if len(ratios) > 1:
            t_stat, p_val = stats.ttest_1samp(ratios, 1.18)
            print(f"  t-test vs 1.18: t={t_stat:.2f}, p={p_val:.4f}")

        results[ft] = {
            'n': int(len(betas)),
            'beta_range': [float(betas.min()), float(betas.max())],
            'ratios': [float(r) for r in ratios],
            'mean_ratio': mean_ratio,
            'std_ratio': std_ratio,
            'systems': subset['domain'].tolist()
        }

    # Overall ANOVA: Do field types have different mean ratios?
    all_ratios = []
    all_labels = []

    for ft in sorted(field_types):
        subset = df[df['field_type'] == ft].sort_values('beta')
        betas = subset['beta'].values
        if len(betas) >= 2:
            ratios = betas[1:] / betas[:-1]
            all_ratios.extend(ratios)
            all_labels.extend([ft] * len(ratios))

    # ANOVA if we have multiple groups
    groups = {}
    for label in set(all_labels):
        groups[label] = [r for r, l in zip(all_ratios, all_labels) if l == label]

    if len(groups) > 1:
        f_stat, p_val = stats.f_oneway(*groups.values())
        print("\n--- ANOVA: Field Type Effect on Growth Factor ---")
        print(f"F-statistic: {f_stat:.3f}")
        print(f"p-value: {p_val:.4f}")

        if p_val < 0.05:
            print("✅ Field Types have DIFFERENT growth factors (p<0.05)")
        else:
            print("❌ No significant difference between Field Types (p≥0.05)")

        results['anova'] = {
            'f_statistic': float(f_stat),
            'p_value': float(p_val),
            'significant': bool(p_val < 0.05)
        }

    return results


def analyze_dimensionality_correlation(df):
    """
    Research Question 2: Does β correlate with effective dimensionality?

    Test correlations: β ~ D_eff, C_eff, SNR, Memory
    """
    print("\n" + "="*60)
    print("RESEARCH QUESTION 2: β-Dimensionality Correlation")
    print("="*60)

    results = {}
    covariates = ['D_eff', 'C_eff', 'SNR', 'Memory']

    for cov in covariates:
        if cov not in df.columns:
            continue

        # Remove NaNs
        valid = df[[cov, 'beta']].dropna()
        x = valid[cov].values
        y = valid['beta'].values

        # Pearson correlation
        r, p_val = stats.pearsonr(x, y)

        # Linear regression
        slope, intercept, r_value, p_reg, stderr = stats.linregress(x, y)

        print(f"\n{cov}:")
        print(f"  Pearson r = {r:.3f} (p={p_val:.4f})")
        print(f"  Linear fit: β = {slope:.3f}·{cov} + {intercept:.3f}")
        print(f"  R² = {r_value**2:.3f}, p={p_reg:.4f}")

        if abs(r) > 0.5 and p_val < 0.05:
            direction = "positive" if r > 0 else "negative"
            print(f"  ✅ SIGNIFICANT {direction} correlation!")
        else:
            print("  ❌ No significant correlation")

        results[cov] = {
            'pearson_r': float(r),
            'p_value': float(p_val),
            'regression': {
                'slope': float(slope),
                'intercept': float(intercept),
                'r_squared': float(r_value**2),
                'p_value': float(p_reg),
                'stderr': float(stderr)
            },
            'significant': bool(abs(r) > 0.5 and p_val < 0.05)
        }

    # Log-log analysis: log(β) ~ log(D_eff)
    if 'D_eff' in df.columns:
        valid = df[['D_eff', 'beta']].dropna()
        log_x = np.log(valid['D_eff'].values)
        log_y = np.log(valid['beta'].values)

        slope, intercept, r_value, p_val, stderr = stats.linregress(log_x, log_y)

        print("\n--- Log-Log Analysis: log(β) ~ log(D_eff) ---")
        print(f"  Power law: β ∝ D_eff^{slope:.3f}")
        print(f"  R² = {r_value**2:.3f}, p={p_val:.4f}")

        if abs(slope) < 0.1:
            print("  → β is approximately INDEPENDENT of D_eff (exponent ≈ 0)")
        elif slope < 0:
            print("  → β DECREASES with D_eff (inverse scaling)")
        else:
            print("  → β INCREASES with D_eff (direct scaling)")

        results['log_log_D_eff'] = {
            'exponent': float(slope),
            'r_squared': float(r_value**2),
            'p_value': float(p_val)
        }

    return results


def analyze_mathematical_meaning(observed_ratio=1.18):
    """
    Research Question 3: What is the mathematical meaning of 1.18?

    Test against known mathematical constants.
    """
    print("\n" + "="*60)
    print("RESEARCH QUESTION 3: Mathematical Meaning of 1.18")
    print("="*60)

    results = {}

    print(f"\nObserved mean ratio: {observed_ratio:.4f}")
    print("\nComparison with mathematical constants:")

    best_match = None
    min_diff = float('inf')

    for name, value in CONSTANTS.items():
        diff = abs(value - observed_ratio)
        rel_diff = diff / observed_ratio * 100

        print(f"  {name:12s} = {value:.6f}  (Δ = {diff:.6f}, {rel_diff:.2f}%)")

        if diff < min_diff:
            min_diff = diff
            best_match = name

        results[name] = {
            'value': float(value),
            'absolute_difference': float(diff),
            'relative_difference_percent': float(rel_diff)
        }

    print(f"\n✅ BEST MATCH: {best_match} = {CONSTANTS[best_match]:.6f}")
    print(f"   Difference: {min_diff:.6f} ({min_diff/observed_ratio*100:.2f}%)")

    # Interpret best match
    if best_match == 'phi_cbrt':
        interpretation = "Φ^(1/3) ≈ 1.176: Sub-Φ scaling (cubic root of golden ratio)"
    elif best_match == 'e_sixth':
        interpretation = "e^(1/6) ≈ 1.181: Exponential growth with characteristic scale 6"
    else:
        interpretation = f"Related to {best_match}"

    print(f"\n📐 INTERPRETATION: {interpretation}")

    results['best_match'] = {
        'constant': best_match,
        'value': float(CONSTANTS[best_match]),
        'difference': float(min_diff),
        'interpretation': interpretation
    }

    return results


def visualize_results(df, ft_results, dim_results, output_dir):
    """Create comprehensive visualization of all results."""

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('β-Scaling Follow-up Analysis: Post-Φ Falsification',
                 fontsize=16, fontweight='bold')

    # Plot 1: Field Type β-ranges
    ax = axes[0, 0]
    field_types = sorted([ft for ft in ft_results.keys() if ft != 'anova'])

    for i, ft in enumerate(field_types):
        data = ft_results[ft]
        if data['n'] > 0:
            beta_range = data['beta_range']
            ax.barh(i, beta_range[1] - beta_range[0],
                   left=beta_range[0], alpha=0.6)
            ax.text(beta_range[1] + 0.5, i,
                   f"μ_ratio={data.get('mean_ratio', 'N/A'):.2f}",
                   va='center', fontsize=9)

    ax.set_yticks(range(len(field_types)))
    ax.set_yticklabels(field_types)
    ax.set_xlabel('β-value')
    ax.set_title('β-Range by Field Type')
    ax.grid(alpha=0.3, axis='x')

    # Plot 2: Growth factors by Field Type (boxplot)
    ax = axes[0, 1]
    ratios_by_type = []
    labels = []

    for ft in field_types:
        if 'ratios' in ft_results[ft] and len(ft_results[ft]['ratios']) > 0:
            ratios_by_type.append(ft_results[ft]['ratios'])
            labels.append(ft[:12])  # Truncate labels

    if ratios_by_type:
        bp = ax.boxplot(ratios_by_type, labels=labels, patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')
        ax.axhline(1.18, color='red', linestyle='--', label='Global mean (1.18)')
        ax.axhline(CONSTANTS['phi'], color='green', linestyle=':', alpha=0.5, label='Φ (1.62)')
        ax.set_ylabel('Growth Factor (β_{i+1}/β_i)')
        ax.set_title('Growth Factors by Field Type')
        ax.legend()
        ax.grid(alpha=0.3, axis='y')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # Plot 3: β vs D_eff
    ax = axes[0, 2]
    if 'D_eff' in df.columns:
        for ft in df['field_type'].unique():
            subset = df[df['field_type'] == ft]
            ax.scatter(subset['D_eff'], subset['beta'],
                      label=ft[:12], alpha=0.7, s=80)

        # Regression line
        valid = df[['D_eff', 'beta']].dropna()
        x = valid['D_eff'].values
        y = valid['beta'].values
        slope, intercept = np.polyfit(x, y, 1)
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = slope * x_line + intercept
        ax.plot(x_line, y_line, 'k--', alpha=0.5,
               label=f'Linear fit: β={slope:.2f}·D+{intercept:.2f}')

        r = dim_results['D_eff']['pearson_r']
        ax.set_xlabel('Effective Dimensionality (D_eff)')
        ax.set_ylabel('β-value')
        ax.set_title(f'β vs D_eff (r={r:.3f})')
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)

    # Plot 4: β vs C_eff
    ax = axes[1, 0]
    if 'C_eff' in df.columns:
        for ft in df['field_type'].unique():
            subset = df[df['field_type'] == ft]
            ax.scatter(subset['C_eff'], subset['beta'],
                      label=ft[:12], alpha=0.7, s=80)

        # Regression line
        valid = df[['C_eff', 'beta']].dropna()
        x = valid['C_eff'].values
        y = valid['beta'].values
        slope, intercept = np.polyfit(x, y, 1)
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = slope * x_line + intercept
        ax.plot(x_line, y_line, 'k--', alpha=0.5)

        r = dim_results['C_eff']['pearson_r']
        ax.set_xlabel('Effective Coupling (C_eff)')
        ax.set_ylabel('β-value')
        ax.set_title(f'β vs C_eff (r={r:.3f})')
        ax.grid(alpha=0.3)

    # Plot 5: Mathematical Constants Comparison
    ax = axes[1, 1]
    constants = list(CONSTANTS.keys())
    values = [CONSTANTS[c] for c in constants]
    diffs = [abs(v - 1.18) for v in values]

    colors = ['green' if d < 0.02 else 'orange' if d < 0.05 else 'red'
              for d in diffs]

    bars = ax.barh(constants, values, color=colors, alpha=0.6)
    ax.axvline(1.18, color='blue', linestyle='--', linewidth=2,
              label='Observed (1.18)')
    ax.set_xlabel('Value')
    ax.set_title('Mathematical Constants vs Observed 1.18')
    ax.legend()
    ax.grid(alpha=0.3, axis='x')

    # Plot 6: Correlation Matrix
    ax = axes[1, 2]
    covariates = ['D_eff', 'C_eff', 'SNR', 'Memory']
    correlations = []
    labels_corr = []

    for cov in covariates:
        if cov in dim_results:
            correlations.append(dim_results[cov]['pearson_r'])
            labels_corr.append(cov)

    if correlations:
        colors_corr = ['green' if abs(r) > 0.5 else 'orange' if abs(r) > 0.3 else 'red'
                       for r in correlations]
        bars = ax.barh(labels_corr, correlations, color=colors_corr, alpha=0.6)
        ax.axvline(0, color='black', linestyle='-', linewidth=0.8)
        ax.set_xlabel('Pearson r')
        ax.set_title('β Correlations with Covariates')
        ax.set_xlim(-1, 1)
        ax.grid(alpha=0.3, axis='x')

    plt.tight_layout()

    # Save plot
    output_path = output_dir / 'beta_scaling_followup_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✅ Visualization saved: {output_path}")

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description='β-Scaling Follow-up Analysis (Post-Φ Falsification)'
    )
    parser.add_argument('--beta-estimates',
                       default='data/derived/beta_estimates.csv',
                       help='Path to beta estimates CSV')
    parser.add_argument('--covariates',
                       default='data/derived/domain_covariates.csv',
                       help='Path to domain covariates CSV')
    parser.add_argument('--output-dir',
                       default='analysis/results',
                       help='Output directory for results')
    parser.add_argument('--observed-ratio',
                       type=float,
                       default=1.18,
                       help='Observed mean growth factor')

    args = parser.parse_args()

    # Setup paths
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    print("Loading data...")
    df = load_data(args.beta_estimates, args.covariates)
    print(f"Loaded {len(df)} domains with complete data")

    # Run analyses
    ft_results = analyze_field_type_clusters(df)
    dim_results = analyze_dimensionality_correlation(df)
    math_results = analyze_mathematical_meaning(args.observed_ratio)

    # Visualize
    print("\nGenerating visualizations...")
    plot_path = visualize_results(df, ft_results, dim_results, output_dir)

    # Compile results
    results = {
        'meta': {
            'analysis': 'Beta Scaling Follow-up (Post-Phi Falsification)',
            'version': '1.0',
            'date': '2025-11-11',
            'n_domains': int(len(df)),
            'observed_mean_ratio': float(args.observed_ratio)
        },
        'research_question_1_field_types': ft_results,
        'research_question_2_dimensionality': dim_results,
        'research_question_3_mathematical': math_results,
        'visualization': plot_path
    }

    # Save JSON
    output_json = output_dir / 'beta_scaling_followup_summary.json'
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Results saved: {output_json}")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    print("\n1. Field Type Cluster Analysis:")
    if 'anova' in ft_results and ft_results['anova']['significant']:
        print("   ✅ Field Types have DIFFERENT growth factors")
    else:
        print("   ❌ No significant Field Type effect")

    print("\n2. Dimensionality Correlation:")
    sig_correlations = [cov for cov, res in dim_results.items()
                       if isinstance(res, dict) and res.get('significant', False)]
    if sig_correlations:
        print(f"   ✅ Significant correlations: {', '.join(sig_correlations)}")
    else:
        print("   ❌ No strong correlations found")

    print("\n3. Mathematical Meaning of 1.18:")
    best = math_results['best_match']
    print(f"   ✅ Best match: {best['constant']} = {best['value']:.6f}")
    print(f"   📐 {best['interpretation']}")

    print("\n" + "="*60)
    print("Analysis complete! 🎯")
    print("="*60)


if __name__ == '__main__':
    main()
