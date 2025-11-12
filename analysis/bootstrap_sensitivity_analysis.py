#!/usr/bin/env python3
"""Bootstrap & Jackknife Sensitivity Analysis for UTAC β-Estimates

Tests the robustness of β-estimates and meta-regression results through:
1. Bootstrap resampling (n=1000 iterations)
2. Jackknife leave-one-out analysis
3. Coefficient stability under subsample perturbations

This quantifies uncertainty and identifies influential observations.

Usage:
    python bootstrap_sensitivity_analysis.py --input data/derived/beta_estimates.csv \
                                              --covariates data/derived/domain_covariates.csv \
                                              --out analysis/results/bootstrap_sensitivity.json

Author: Claude Code
Date: 2025-11-12
License: AGPL-3.0
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats

# Set random seed for reproducibility
np.random.seed(42)


def bootstrap_beta_estimates(beta: np.ndarray, beta_ci_lower: np.ndarray, beta_ci_upper: np.ndarray,
                              n_iterations: int = 1000) -> Dict:
    """Bootstrap resampling of β estimates.

    Args:
        beta: Array of β point estimates
        beta_ci_lower: Array of lower CI bounds
        beta_ci_upper: Array of upper CI bounds
        n_iterations: Number of bootstrap iterations

    Returns:
        dict with bootstrap statistics
    """
    n_systems = len(beta)
    bootstrap_samples = []

    for _ in range(n_iterations):
        # Resample with replacement
        indices = np.random.choice(n_systems, size=n_systems, replace=True)
        bootstrap_samples.append(beta[indices])

    bootstrap_samples = np.array(bootstrap_samples)

    # Compute bootstrap statistics
    bootstrap_mean = np.mean(bootstrap_samples, axis=0)
    bootstrap_std = np.std(bootstrap_samples, axis=0)
    bootstrap_ci_lower = np.percentile(bootstrap_samples, 2.5, axis=0)
    bootstrap_ci_upper = np.percentile(bootstrap_samples, 97.5, axis=0)

    # Global statistics across all systems
    global_mean = np.mean(bootstrap_samples)
    global_std = np.std(bootstrap_samples)
    global_ci_lower = np.percentile(bootstrap_samples, 2.5)
    global_ci_upper = np.percentile(bootstrap_samples, 97.5)

    return {
        'n_iterations': n_iterations,
        'n_systems': n_systems,
        'bootstrap_mean': bootstrap_mean.tolist(),
        'bootstrap_std': bootstrap_std.tolist(),
        'bootstrap_ci_lower': bootstrap_ci_lower.tolist(),
        'bootstrap_ci_upper': bootstrap_ci_upper.tolist(),
        'global_mean': float(global_mean),
        'global_std': float(global_std),
        'global_ci_lower': float(global_ci_lower),
        'global_ci_upper': float(global_ci_upper),
        'coefficient_of_variation': float(global_std / global_mean),
    }


def jackknife_analysis(beta: np.ndarray, domains: List[str]) -> Dict:
    """Jackknife leave-one-out analysis.

    Args:
        beta: Array of β estimates
        domains: List of domain names

    Returns:
        dict with jackknife statistics and influential points
    """
    n_systems = len(beta)
    jackknife_means = []
    jackknife_stds = []
    influence_scores = []

    full_mean = np.mean(beta)
    full_std = np.std(beta)

    for i in range(n_systems):
        # Leave-one-out
        mask = np.ones(n_systems, dtype=bool)
        mask[i] = False
        beta_loo = beta[mask]

        loo_mean = np.mean(beta_loo)
        loo_std = np.std(beta_loo)

        jackknife_means.append(loo_mean)
        jackknife_stds.append(loo_std)

        # Influence score: how much mean changes when removing this point
        influence = np.abs(full_mean - loo_mean) / full_mean
        influence_scores.append(influence)

    jackknife_means = np.array(jackknife_means)
    jackknife_stds = np.array(jackknife_stds)
    influence_scores = np.array(influence_scores)

    # Identify influential points (top 20% influence)
    influence_threshold = np.percentile(influence_scores, 80)
    influential_indices = np.where(influence_scores >= influence_threshold)[0]
    influential_systems = [(domains[i], float(beta[i]), float(influence_scores[i]))
                          for i in influential_indices]

    return {
        'n_systems': n_systems,
        'full_mean': float(full_mean),
        'full_std': float(full_std),
        'jackknife_mean_range': [float(np.min(jackknife_means)), float(np.max(jackknife_means))],
        'jackknife_std_range': [float(np.min(jackknife_stds)), float(np.max(jackknife_stds))],
        'mean_influence_score': float(np.mean(influence_scores)),
        'max_influence_score': float(np.max(influence_scores)),
        'influential_systems': influential_systems,
        'influence_threshold': float(influence_threshold),
    }


def field_type_stability(beta: np.ndarray, field_types: List[str]) -> Dict:
    """Test stability of β estimates within field types.

    Args:
        beta: Array of β estimates
        field_types: List of field type labels

    Returns:
        dict with within-field-type statistics
    """
    unique_types = list(set(field_types))
    field_stats = {}

    for ftype in unique_types:
        mask = np.array([ft == ftype for ft in field_types])
        beta_field = beta[mask]

        if len(beta_field) < 2:
            continue

        field_stats[ftype] = {
            'n': int(len(beta_field)),
            'mean': float(np.mean(beta_field)),
            'std': float(np.std(beta_field)),
            'cv': float(np.std(beta_field) / np.mean(beta_field)),
            'range': [float(np.min(beta_field)), float(np.max(beta_field))],
        }

    # Between-field variance ratio
    grand_mean = np.mean(beta)
    within_var = np.mean([field_stats[ft]['std']**2 for ft in field_stats])
    between_var = np.var([field_stats[ft]['mean'] for ft in field_stats])
    variance_ratio = between_var / (within_var + 1e-9)

    return {
        'field_stats': field_stats,
        'within_variance': float(within_var),
        'between_variance': float(between_var),
        'variance_ratio': float(variance_ratio),
        'interpretation': 'High between/within ratio suggests field types explain β-heterogeneity'
    }


def coefficient_stability_test(beta: np.ndarray, n_subsamples: int = 100, subsample_fraction: float = 0.8) -> Dict:
    """Test coefficient stability under random subsampling.

    Args:
        beta: Array of β estimates
        n_subsamples: Number of subsample iterations
        subsample_fraction: Fraction of data to subsample

    Returns:
        dict with coefficient stability statistics
    """
    n_systems = len(beta)
    subsample_size = int(n_systems * subsample_fraction)

    subsample_means = []
    subsample_stds = []

    for _ in range(n_subsamples):
        indices = np.random.choice(n_systems, size=subsample_size, replace=False)
        subsample = beta[indices]
        subsample_means.append(np.mean(subsample))
        subsample_stds.append(np.std(subsample))

    subsample_means = np.array(subsample_means)
    subsample_stds = np.array(subsample_stds)

    # Coefficient of variation of subsample means
    cv_mean = np.std(subsample_means) / np.mean(subsample_means)

    return {
        'n_subsamples': n_subsamples,
        'subsample_fraction': subsample_fraction,
        'subsample_size': subsample_size,
        'mean_of_means': float(np.mean(subsample_means)),
        'std_of_means': float(np.std(subsample_means)),
        'cv_of_means': float(cv_mean),
        'mean_range': [float(np.min(subsample_means)), float(np.max(subsample_means))],
        'interpretation': f"CV = {cv_mean:.3f}: {'robust' if cv_mean < 0.1 else 'moderate' if cv_mean < 0.2 else 'sensitive'} to subsampling"
    }


def main():
    parser = argparse.ArgumentParser(description='Bootstrap & Jackknife Sensitivity Analysis')
    parser.add_argument('--input', required=True, help='Path to beta_estimates.csv')
    parser.add_argument('--covariates', required=True, help='Path to domain_covariates.csv')
    parser.add_argument('--out', required=True, help='Output JSON path')
    parser.add_argument('--n-bootstrap', type=int, default=1000, help='Number of bootstrap iterations')
    parser.add_argument('--verbose', action='store_true', help='Print detailed output')

    args = parser.parse_args()

    # Load data
    df_beta = pd.read_csv(args.input)
    df_cov = pd.read_csv(args.covariates)

    # Merge on domain
    df = pd.merge(df_beta, df_cov, on='domain', how='inner')

    beta = df['beta'].values
    beta_ci_lower = df['beta_ci_lower'].values
    beta_ci_upper = df['beta_ci_upper'].values
    domains = df['domain'].tolist()
    field_types = df['field_type'].tolist()

    if args.verbose:
        print("═" * 70)
        print("UTAC Bootstrap & Jackknife Sensitivity Analysis")
        print("═" * 70)
        print(f"\nLoaded {len(df)} systems")
        print(f"β range: [{np.min(beta):.2f}, {np.max(beta):.2f}]")
        print(f"β mean: {np.mean(beta):.2f} ± {np.std(beta):.2f}")
        print()

    # Run analyses
    results = {
        'meta': {
            'n_systems': len(df),
            'beta_mean': float(np.mean(beta)),
            'beta_std': float(np.std(beta)),
            'beta_range': [float(np.min(beta)), float(np.max(beta))],
            'timestamp': pd.Timestamp.now().isoformat(),
        }
    }

    # 1. Bootstrap
    if args.verbose:
        print("Running Bootstrap Analysis...")
    results['bootstrap'] = bootstrap_beta_estimates(beta, beta_ci_lower, beta_ci_upper, args.n_bootstrap)
    if args.verbose:
        print(f"  Bootstrap mean: {results['bootstrap']['global_mean']:.2f} ± {results['bootstrap']['global_std']:.2f}")
        print(f"  Bootstrap 95% CI: [{results['bootstrap']['global_ci_lower']:.2f}, {results['bootstrap']['global_ci_upper']:.2f}]")
        print(f"  Coefficient of variation: {results['bootstrap']['coefficient_of_variation']:.3f}")
        print()

    # 2. Jackknife
    if args.verbose:
        print("Running Jackknife Analysis...")
    results['jackknife'] = jackknife_analysis(beta, domains)
    if args.verbose:
        print(f"  Jackknife mean range: {results['jackknife']['jackknife_mean_range']}")
        print(f"  Mean influence score: {results['jackknife']['mean_influence_score']:.3f}")
        print(f"  Influential systems ({len(results['jackknife']['influential_systems'])}):")
        for domain, beta_val, influence in results['jackknife']['influential_systems']:
            print(f"    - {domain}: β={beta_val:.2f}, influence={influence:.3f}")
        print()

    # 3. Field Type Stability
    if args.verbose:
        print("Running Field Type Stability Analysis...")
    results['field_type_stability'] = field_type_stability(beta, field_types)
    if args.verbose:
        print(f"  Variance ratio (between/within): {results['field_type_stability']['variance_ratio']:.3f}")
        for ftype, stats in results['field_type_stability']['field_stats'].items():
            print(f"    {ftype}: n={stats['n']}, mean={stats['mean']:.2f}, CV={stats['cv']:.3f}")
        print()

    # 4. Coefficient Stability
    if args.verbose:
        print("Running Coefficient Stability Test...")
    results['coefficient_stability'] = coefficient_stability_test(beta, n_subsamples=100, subsample_fraction=0.8)
    if args.verbose:
        print(f"  {results['coefficient_stability']['interpretation']}")
        print()

    # Save results
    with open(args.out, 'w') as f:
        json.dump(results, f, indent=2)

    if args.verbose:
        print("═" * 70)
        print(f"✓ Saved results to: {args.out}")
        print("═" * 70)

    return results


if __name__ == '__main__':
    main()
