#!/usr/bin/env python3
"""Sensitivity Analysis: Preprocessing Effects on β-Estimation

Quantifies how preprocessing choices affect β-estimates in LLM training data:
1. Smoothing window size
2. Normalization methods
3. Outlier removal thresholds
4. Sampling rate/binning

This module helps determine whether β-patterns are robust or artifacts
of data preparation choices.

Usage:
    python sensitivity_analysis.py --input data/implosion/llm_runs_beta.csv \
                                    --out analysis/results/sensitivity_report.json

References:
- Theory: docs/utac_type6_implosive_origin_theory.md
- Falsification Plan: docs/utac_type6_falsification_plan.md
- ChatGPT-5 Recommendations: "Sensitivity Analysis: Preprocessing-Effekte quantifizieren"

Author: Claude Code + Johann B. Römer
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
from scipy.optimize import curve_fit
from scipy.ndimage import uniform_filter1d

# Add models to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.utac_field_v1_2 import logistic_utac


# ═══════════════════════════════════════════════════════════════
# PREPROCESSING VARIANTS
# ═══════════════════════════════════════════════════════════════

def apply_smoothing(data: np.ndarray, window_size: int) -> np.ndarray:
    """Apply moving average smoothing."""
    if window_size <= 1:
        return data
    return uniform_filter1d(data, size=window_size, mode='nearest')


def apply_normalization(data: np.ndarray, method: str) -> np.ndarray:
    """Apply normalization method.

    Methods:
    - 'minmax': Scale to [0, 100]
    - 'zscore': Standardize to mean=0, std=1, then rescale
    - 'robust': Use median/IQR for outlier-resistant scaling
    - 'none': No normalization
    """
    if method == 'none':
        return data
    elif method == 'minmax':
        return 100 * (data - np.min(data)) / (np.max(data) - np.min(data) + 1e-9)
    elif method == 'zscore':
        z = (data - np.mean(data)) / (np.std(data) + 1e-9)
        # Rescale to [0, 100] for comparability
        return 50 + 20 * z
    elif method == 'robust':
        median = np.median(data)
        iqr = np.percentile(data, 75) - np.percentile(data, 25)
        return 50 + 30 * (data - median) / (iqr + 1e-9)
    else:
        raise ValueError(f"Unknown normalization method: {method}")


def remove_outliers(data: np.ndarray, epochs: np.ndarray, threshold: float) -> Tuple[np.ndarray, np.ndarray]:
    """Remove outliers based on z-score threshold.

    Returns filtered data and epochs.
    """
    if threshold <= 0:
        return data, epochs

    z_scores = np.abs((data - np.mean(data)) / (np.std(data) + 1e-9))
    mask = z_scores < threshold
    return data[mask], epochs[mask]


def downsample_data(data: np.ndarray, epochs: np.ndarray, factor: int) -> Tuple[np.ndarray, np.ndarray]:
    """Downsample by taking every nth point."""
    if factor <= 1:
        return data, epochs
    return data[::factor], epochs[::factor]


# ═══════════════════════════════════════════════════════════════
# β ESTIMATION WITH PREPROCESSING
# ═══════════════════════════════════════════════════════════════

def estimate_beta_with_preprocessing(
    data: np.ndarray,
    epochs: np.ndarray,
    smooth_window: int = 1,
    norm_method: str = 'minmax',
    outlier_threshold: float = 0,
    downsample_factor: int = 1
) -> Dict:
    """Estimate β with specific preprocessing pipeline.

    Returns:
        dict with beta, Theta, R_squared, and preprocessing config
    """
    # Apply preprocessing pipeline
    processed_data = data.copy()
    processed_epochs = epochs.copy()

    # 1. Outlier removal (before smoothing to avoid contamination)
    if outlier_threshold > 0:
        processed_data, processed_epochs = remove_outliers(
            processed_data, processed_epochs, outlier_threshold
        )

    # 2. Downsampling
    if downsample_factor > 1:
        processed_data, processed_epochs = downsample_data(
            processed_data, processed_epochs, downsample_factor
        )

    # 3. Smoothing
    if smooth_window > 1:
        processed_data = apply_smoothing(processed_data, smooth_window)

    # 4. Normalization
    processed_data = apply_normalization(processed_data, norm_method)

    # Estimate β via logistic fit
    if len(processed_data) < 5:
        return {
            'beta': np.nan,
            'Theta': np.nan,
            'R_squared': np.nan,
            'n_points': len(processed_data),
            'preprocessing': {
                'smooth_window': smooth_window,
                'norm_method': norm_method,
                'outlier_threshold': outlier_threshold,
                'downsample_factor': downsample_factor,
            }
        }

    try:
        # Fit logistic: y = 1 / (1 + exp(-β(x - Θ)))
        # Use normalized epochs as x
        x_norm = processed_epochs / np.max(processed_epochs)

        # Initial guess: Θ at midpoint, β moderate
        Theta_init = 0.5
        beta_init = 4.0

        def sigmoid(x, Theta, beta):
            return 100 / (1 + np.exp(-beta * (x - Theta)))

        popt, pcov = curve_fit(
            sigmoid,
            x_norm,
            processed_data,
            p0=[Theta_init, beta_init],
            maxfev=5000,
            bounds=([0, 0.1], [1.0, 20.0])
        )

        Theta_fit, beta_fit = popt

        # Compute R²
        y_pred = sigmoid(x_norm, Theta_fit, beta_fit)
        ss_res = np.sum((processed_data - y_pred) ** 2)
        ss_tot = np.sum((processed_data - np.mean(processed_data)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        return {
            'beta': beta_fit,
            'Theta': Theta_fit,
            'R_squared': r_squared,
            'n_points': len(processed_data),
            'preprocessing': {
                'smooth_window': smooth_window,
                'norm_method': norm_method,
                'outlier_threshold': outlier_threshold,
                'downsample_factor': downsample_factor,
            }
        }

    except Exception as e:
        return {
            'beta': np.nan,
            'Theta': np.nan,
            'R_squared': np.nan,
            'n_points': len(processed_data),
            'error': str(e),
            'preprocessing': {
                'smooth_window': smooth_window,
                'norm_method': norm_method,
                'outlier_threshold': outlier_threshold,
                'downsample_factor': downsample_factor,
            }
        }


# ═══════════════════════════════════════════════════════════════
# SENSITIVITY GRID SEARCH
# ═══════════════════════════════════════════════════════════════

def run_sensitivity_analysis(
    df: pd.DataFrame,
    run_id: str,
    verbose: bool = True
) -> Dict:
    """Run sensitivity analysis on a single LLM run.

    Tests combinations of:
    - Smoothing: [1, 3, 5, 10] (window size)
    - Normalization: ['minmax', 'zscore', 'robust']
    - Outlier removal: [0, 2.5, 3.0] (z-score threshold)
    - Downsampling: [1, 2, 5] (factor)

    Total: 4 × 3 × 3 × 3 = 108 combinations

    Returns:
        dict with β statistics (mean, std, CV, range)
    """
    run_data = df[df['run_id'] == run_id].sort_values('epoch')
    epochs = run_data['epoch'].values
    capability = run_data['capability_score'].values

    if len(epochs) < 10:
        return {
            'run_id': run_id,
            'n_points': len(epochs),
            'message': 'Insufficient data points'
        }

    # Grid search parameters
    smooth_windows = [1, 3, 5, 10]
    norm_methods = ['minmax', 'zscore', 'robust']
    outlier_thresholds = [0, 2.5, 3.0]
    downsample_factors = [1, 2, 5]

    results = []

    for smooth in smooth_windows:
        for norm in norm_methods:
            for outlier in outlier_thresholds:
                for downsample in downsample_factors:
                    result = estimate_beta_with_preprocessing(
                        capability, epochs,
                        smooth_window=smooth,
                        norm_method=norm,
                        outlier_threshold=outlier,
                        downsample_factor=downsample
                    )
                    results.append(result)

    # Extract β estimates (ignore NaN)
    betas = [r['beta'] for r in results if not np.isnan(r['beta'])]
    r_squareds = [r['R_squared'] for r in results if not np.isnan(r['R_squared'])]

    if len(betas) == 0:
        return {
            'run_id': run_id,
            'n_combinations': len(results),
            'n_successful': 0,
            'message': 'No successful fits'
        }

    # Statistics
    beta_mean = np.mean(betas)
    beta_std = np.std(betas)
    beta_cv = beta_std / beta_mean if beta_mean != 0 else np.nan
    beta_range = np.max(betas) - np.min(betas)
    beta_iqr = np.percentile(betas, 75) - np.percentile(betas, 25)

    r2_mean = np.mean(r_squareds)
    r2_std = np.std(r_squareds)

    if verbose:
        print(f"Run {run_id}:")
        print(f"  β: {beta_mean:.3f} ± {beta_std:.3f} (CV={beta_cv:.3f})")
        print(f"  β range: [{np.min(betas):.3f}, {np.max(betas):.3f}] (Δ={beta_range:.3f})")
        print(f"  R²: {r2_mean:.3f} ± {r2_std:.3f}")
        print(f"  Successful fits: {len(betas)}/{len(results)}")
        print()

    return {
        'run_id': run_id,
        'n_combinations': len(results),
        'n_successful': len(betas),
        'beta_mean': beta_mean,
        'beta_std': beta_std,
        'beta_cv': beta_cv,
        'beta_range': beta_range,
        'beta_iqr': beta_iqr,
        'beta_min': np.min(betas),
        'beta_max': np.max(betas),
        'r2_mean': r2_mean,
        'r2_std': r2_std,
        'all_results': results,
    }


# ═══════════════════════════════════════════════════════════════
# MAIN ANALYSIS
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Sensitivity Analysis: Preprocessing Effects on β-Estimation'
    )
    parser.add_argument('--input', default='data/implosion/llm_runs_beta.csv',
                        help='Path to LLM training data CSV')
    parser.add_argument('--out', default='analysis/results/sensitivity_analysis.json',
                        help='Output path for sensitivity report (JSON)')
    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed results')

    args = parser.parse_args()

    print("═" * 70)
    print("SENSITIVITY ANALYSIS: Preprocessing Effects on β-Estimation")
    print("Testing 108 preprocessing combinations per run")
    print("═" * 70)
    print()

    # Load data
    print(f"Loading data from: {args.input}")
    try:
        df = pd.read_csv(args.input, comment='#')
        df = df.dropna(how='all')

        # Map column names
        column_mapping = {
            'training_step': 'epoch',
            'beta_estimate': 'beta',
            'grokking_detected': 'grokking_event'
        }
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns and new_col not in df.columns:
                df = df.rename(columns={old_col: new_col})

        print(f"  → {len(df)} training epochs loaded")
        print(f"  → Runs: {df['run_id'].nunique()}")
        print()
    except Exception as e:
        print(f"ERROR: Failed to load data: {e}")
        return

    # Run sensitivity analysis for each run
    print("─" * 70)
    print("Running sensitivity analysis per run...")
    print("─" * 70)
    print()

    all_run_results = []

    for run_id in df['run_id'].unique():
        result = run_sensitivity_analysis(df, run_id, verbose=args.verbose)
        if 'beta_mean' in result:
            all_run_results.append(result)

    if len(all_run_results) == 0:
        print("ERROR: No successful sensitivity analyses")
        return

    # Aggregate statistics across runs
    print("═" * 70)
    print("AGGREGATE SENSITIVITY STATISTICS")
    print("═" * 70)

    mean_cv = np.mean([r['beta_cv'] for r in all_run_results])
    mean_range = np.mean([r['beta_range'] for r in all_run_results])
    mean_iqr = np.mean([r['beta_iqr'] for r in all_run_results])

    print(f"  Mean β CV across runs: {mean_cv:.3f}")
    print(f"  Mean β range across runs: {mean_range:.3f}")
    print(f"  Mean β IQR across runs: {mean_iqr:.3f}")
    print()

    # Interpretation
    print("─" * 70)
    print("INTERPRETATION")
    print("─" * 70)

    if mean_cv < 0.1:
        print("  ✓ ROBUST: β estimates are highly stable (CV < 0.1)")
        print("    → Preprocessing choices have minimal impact")
    elif mean_cv < 0.2:
        print("  ○ MODERATE: β estimates show some sensitivity (0.1 ≤ CV < 0.2)")
        print("    → Preprocessing should be standardized and reported")
    else:
        print("  ⚠️  SENSITIVE: β estimates are highly sensitive (CV ≥ 0.2)")
        print("    → Results may be artifacts of preprocessing")
        print("    → Recommend robust estimation methods")

    print()

    if mean_range < 1.0:
        print(f"  ✓ Narrow β range: {mean_range:.3f} < 1.0")
    elif mean_range < 2.0:
        print(f"  ○ Moderate β range: {mean_range:.3f} < 2.0")
    else:
        print(f"  ⚠️  Wide β range: {mean_range:.3f} ≥ 2.0")

    print()

    # Save results
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    summary = {
        'metadata': {
            'input_file': args.input,
            'n_runs': len(all_run_results),
            'n_combinations_per_run': 108,
            'analysis_date': pd.Timestamp.now().isoformat(),
        },
        'aggregate_statistics': {
            'mean_beta_cv': mean_cv,
            'mean_beta_range': mean_range,
            'mean_beta_iqr': mean_iqr,
        },
        'interpretation': {
            'robustness': 'high' if mean_cv < 0.1 else ('moderate' if mean_cv < 0.2 else 'low'),
            'recommendation': (
                'Results are robust to preprocessing choices'
                if mean_cv < 0.1 else
                'Standardize preprocessing pipeline'
                if mean_cv < 0.2 else
                'Use robust estimation methods or report sensitivity'
            ),
        },
        'per_run_results': all_run_results,
    }

    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"✓ Saved sensitivity report: {output_path}")
    print()

    print("═" * 70)
    print("Analysis complete.")
    print("═" * 70)


if __name__ == '__main__':
    main()
