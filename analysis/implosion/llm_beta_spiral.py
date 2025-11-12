#!/usr/bin/env python3
"""LLM β-Spiral Trajectory Analysis: Training Dynamics & Grokking

Tests spiral dynamics in LLM training trajectories:
1. β evolution over training epochs
2. Grokking as β-jumps (sudden capability emergence)
3. Spiral convergence to Φ³ fixpoint
4. Temporal coherence of β-trajectory

Falsification criteria:
1. No spiral structure (β trajectory is random walk)
2. Grokking events don't correlate with β-jumps
3. No convergence to Φ³ fixpoint (β drifts unbounded)
4. Temporal autocorrelation < 0.3 (no coherent dynamics)

Usage:
    python llm_beta_spiral.py --input data/implosion/llm_runs_beta.csv \\
                               --out paper/figures/llm_beta_spiral.png

References:
- Theory: docs/utac_type6_implosive_origin_theory.md
- Falsification Plan: docs/utac_type6_falsification_plan.md (Experiment B)
- LLM Data: data/implosion/llm_runs_beta.csv

Author: Johann B. Römer et al.
Date: 2025-11-12
License: AGPL-3.0
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats

# Add models to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.utac_type6_implosive import (
    BETA_FIXPOINT_PHI3,
    BETA_STEPS,
    PHI,
    PHI_CBRT,
    beta_step_ratios,
    nearest_beta_step,
    tau_star,
)

# Optional plotting
try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch
    from mpl_toolkits.mplot3d import Axes3D
    from mpl_toolkits.mplot3d import proj3d
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available, plots will be skipped")


# ═══════════════════════════════════════════════════════════════
# DATA LOADING & PREPROCESSING
# ═══════════════════════════════════════════════════════════════

def load_llm_data(filepath: str) -> pd.DataFrame:
    """Load LLM training β trajectories."""
    df = pd.read_csv(filepath, comment='#')
    df = df.dropna(how='all')

    # Map column names to expected format
    column_mapping = {
        'training_step': 'epoch',
        'beta_estimate': 'beta',
        'grokking_detected': 'grokking_event'
    }

    # Rename columns if they exist
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df = df.rename(columns={old_col: new_col})

    # Ensure required columns
    required = ['run_id', 'epoch', 'beta', 'capability_score', 'grokking_event']
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Available: {df.columns.tolist()}")

    # Convert grokking_event to numeric (True/False → 1/0)
    if df['grokking_event'].dtype == bool or df['grokking_event'].dtype == object:
        df['grokking_event'] = df['grokking_event'].astype(str).str.lower().isin(['true', '1', 'yes']).astype(int)

    return df


# ═══════════════════════════════════════════════════════════════
# TEST 1: SPIRAL STRUCTURE (β TRAJECTORY COHERENCE)
# ═══════════════════════════════════════════════════════════════

def test_spiral_coherence(
    df: pd.DataFrame,
    verbose: bool = True
) -> Dict:
    """Test whether β trajectories exhibit spiral structure.

    Spiral structure implies:
    1. Temporal autocorrelation (β_t depends on β_{t-1})
    2. Rotational component (β oscillates around fixpoint)
    3. Radial convergence (β approaches Φ³ over time)

    Falsify if autocorrelation < 0.3 (random walk).

    Parameters
    ----------
    df : DataFrame
        LLM training data with columns: run_id, epoch, beta
    verbose : bool
        Print detailed results

    Returns
    -------
    results : dict
        - autocorr: Lag-1 temporal autocorrelation
        - rotation_score: Oscillation strength around fixpoint
        - radial_convergence: Final β closer to Φ³ than initial
        - falsified: True if autocorr < 0.3
    """
    results_per_run = []

    for run_id in df['run_id'].unique():
        run_data = df[df['run_id'] == run_id].sort_values('epoch')
        beta_seq = run_data['beta'].values

        if len(beta_seq) < 3:
            continue

        # Autocorrelation (lag-1)
        autocorr = np.corrcoef(beta_seq[:-1], beta_seq[1:])[0, 1]

        # Rotational component: oscillations around Φ³
        deviations = beta_seq - BETA_FIXPOINT_PHI3
        sign_changes = np.sum(np.diff(np.sign(deviations)) != 0)
        rotation_score = sign_changes / (len(beta_seq) - 1)

        # Radial convergence: distance to Φ³ decreases
        dist_initial = abs(beta_seq[0] - BETA_FIXPOINT_PHI3)
        dist_final = abs(beta_seq[-1] - BETA_FIXPOINT_PHI3)
        radial_convergence = (dist_initial - dist_final) / dist_initial if dist_initial > 0 else 0.0

        results_per_run.append({
            'run_id': run_id,
            'autocorr': autocorr,
            'rotation_score': rotation_score,
            'radial_convergence': radial_convergence,
        })

    if not results_per_run:
        return {
            'mean_autocorr': np.nan,
            'mean_rotation': np.nan,
            'mean_convergence': np.nan,
            'falsified': None,
            'message': 'Insufficient data',
        }

    mean_autocorr = np.mean([r['autocorr'] for r in results_per_run])
    mean_rotation = np.mean([r['rotation_score'] for r in results_per_run])
    mean_convergence = np.mean([r['radial_convergence'] for r in results_per_run])

    # Falsification: autocorr < 0.3 (no coherent spiral)
    falsified = mean_autocorr < 0.3

    if verbose:
        print(f"  Mean temporal autocorr: {mean_autocorr:.3f}")
        print(f"  Mean rotation score: {mean_rotation:.3f}")
        print(f"  Mean radial convergence: {mean_convergence:.3f}")
        print()

    return {
        'mean_autocorr': mean_autocorr,
        'mean_rotation': mean_rotation,
        'mean_convergence': mean_convergence,
        'falsified': falsified,
        'message': 'FALSIFIED' if falsified else 'VALIDATED',
        'per_run': results_per_run,
    }


# ═══════════════════════════════════════════════════════════════
# TEST 2: GROKKING AS β-JUMPS
# ═══════════════════════════════════════════════════════════════

def test_grokking_beta_jumps(
    df: pd.DataFrame,
    verbose: bool = True
) -> Dict:
    """Test whether grokking events correlate with β-jumps.

    Prediction: Grokking (sudden capability emergence) should coincide
    with jumps in β (steepness increase).

    Falsify if correlation < 0.3 or if grokking events show no β-jump.

    Parameters
    ----------
    df : DataFrame
        LLM data with columns: epoch, beta, grokking_event
    verbose : bool
        Print detailed results

    Returns
    -------
    results : dict
        - correlation: β-jump magnitude vs. grokking event
        - mean_beta_jump_grok: Mean Δβ during grokking
        - mean_beta_jump_nogrok: Mean Δβ without grokking
        - falsified: True if correlation < 0.3
    """
    results_per_run = []

    for run_id in df['run_id'].unique():
        run_data = df[df['run_id'] == run_id].sort_values('epoch')

        if len(run_data) < 2:
            continue

        # Compute β-jumps (Δβ between consecutive epochs)
        beta_jumps = np.diff(run_data['beta'].values)
        grokking_events = run_data['grokking_event'].values[1:]  # Align with jumps

        # Mean β-jump during grokking vs. no grokking
        grok_mask = grokking_events == 1
        if grok_mask.sum() > 0:
            mean_jump_grok = np.mean(np.abs(beta_jumps[grok_mask]))
            mean_jump_nogrok = np.mean(np.abs(beta_jumps[~grok_mask])) if (~grok_mask).sum() > 0 else 0.0
        else:
            mean_jump_grok = 0.0
            mean_jump_nogrok = np.mean(np.abs(beta_jumps))

        # Point-biserial correlation: grokking (binary) vs. |Δβ| (continuous)
        if len(beta_jumps) > 1 and grok_mask.sum() > 0:
            correlation, pval = stats.pointbiserialr(grokking_events, np.abs(beta_jumps))
        else:
            correlation = 0.0
            pval = 1.0

        results_per_run.append({
            'run_id': run_id,
            'correlation': correlation,
            'pval': pval,
            'mean_jump_grok': mean_jump_grok,
            'mean_jump_nogrok': mean_jump_nogrok,
        })

    if not results_per_run:
        return {
            'mean_correlation': np.nan,
            'mean_beta_jump_grok': np.nan,
            'mean_beta_jump_nogrok': np.nan,
            'falsified': None,
            'message': 'Insufficient data',
        }

    mean_corr = np.mean([r['correlation'] for r in results_per_run])
    mean_jump_grok = np.mean([r['mean_jump_grok'] for r in results_per_run])
    mean_jump_nogrok = np.mean([r['mean_jump_nogrok'] for r in results_per_run])

    # Falsification: correlation < 0.3 (grokking uncorrelated with β-jumps)
    falsified = mean_corr < 0.3

    if verbose:
        print(f"  Mean correlation (grokking ↔ |Δβ|): {mean_corr:.3f}")
        print(f"  Mean |Δβ| during grokking: {mean_jump_grok:.3f}")
        print(f"  Mean |Δβ| without grokking: {mean_jump_nogrok:.3f}")
        print(f"  Jump amplification: {mean_jump_grok / mean_jump_nogrok:.2f}x" if mean_jump_nogrok > 0 else "  Jump amplification: N/A")
        print()

    return {
        'mean_correlation': mean_corr,
        'mean_beta_jump_grok': mean_jump_grok,
        'mean_beta_jump_nogrok': mean_jump_nogrok,
        'falsified': falsified,
        'message': 'FALSIFIED' if falsified else 'VALIDATED',
        'per_run': results_per_run,
    }


# ═══════════════════════════════════════════════════════════════
# TEST 3: FIXPOINT CONVERGENCE (Φ³ ATTRACTOR)
# ═══════════════════════════════════════════════════════════════

def test_fixpoint_convergence(
    df: pd.DataFrame,
    verbose: bool = True
) -> Dict:
    """Test whether β converges to Φ³ fixpoint over training.

    Prediction: β should approach Φ³ ≈ 4.236 as training progresses.

    Falsify if:
    1. Final β mean outside [3.5, 5.0]
    2. Variance increases over time (no convergence)

    Parameters
    ----------
    df : DataFrame
        LLM data with columns: run_id, epoch, beta
    verbose : bool
        Print detailed results

    Returns
    -------
    results : dict
        - final_mean_beta: Mean β in final 20% of epochs
        - final_std_beta: Std β in final 20%
        - variance_ratio: Var(final) / Var(initial)
        - falsified: True if final mean outside [3.5, 5.0] or var_ratio > 1
    """
    final_betas = []
    initial_betas = []

    for run_id in df['run_id'].unique():
        run_data = df[df['run_id'] == run_id].sort_values('epoch')
        n_epochs = len(run_data)

        if n_epochs < 5:
            continue

        # Initial 20% and final 20%
        split = int(0.2 * n_epochs)
        initial_betas.extend(run_data['beta'].values[:split].tolist())
        final_betas.extend(run_data['beta'].values[-split:].tolist())

    if not final_betas:
        return {
            'final_mean_beta': np.nan,
            'final_std_beta': np.nan,
            'variance_ratio': np.nan,
            'falsified': None,
            'message': 'Insufficient data',
        }

    final_mean = np.mean(final_betas)
    final_std = np.std(final_betas)
    initial_var = np.var(initial_betas) if initial_betas else 1e-9
    final_var = np.var(final_betas)
    variance_ratio = final_var / initial_var if initial_var > 0 else np.inf

    # Falsification tests
    falsified_mean = (final_mean < 3.5) or (final_mean > 5.0)
    falsified_variance = variance_ratio > 1.0  # Variance should decrease
    falsified = falsified_mean or falsified_variance

    if verbose:
        print(f"  Final mean β: {final_mean:.3f} (target: Φ³ = {BETA_FIXPOINT_PHI3:.3f})")
        print(f"  Final std β: {final_std:.3f}")
        print(f"  Variance ratio (final/initial): {variance_ratio:.3f}")
        print(f"  Deviation from Φ³: {abs(final_mean - BETA_FIXPOINT_PHI3):.3f}")
        print()

    return {
        'final_mean_beta': final_mean,
        'final_std_beta': final_std,
        'variance_ratio': variance_ratio,
        'deviation_phi3': abs(final_mean - BETA_FIXPOINT_PHI3),
        'falsified': falsified,
        'message': 'FALSIFIED' if falsified else 'VALIDATED',
    }


# ═══════════════════════════════════════════════════════════════
# TEST 4: IMPLOSIVE DELAY & GROKKING TIME (REFINED v2.1)
# ═══════════════════════════════════════════════════════════════

def test_implosive_delay(
    df: pd.DataFrame,
    verbose: bool = True,
    n_bootstrap: int = 1000
) -> Dict:
    """Test whether grokking delay follows τ* = a/β + b·log(|R-Θ|) + c.

    Prediction: Time to grokking should be inversely proportional to β
    and logarithmically dependent on proximity to threshold.

    Refinements (v2.1):
    1. Full regression model (not just correlation)
    2. Null model comparison (ΔAIC)
    3. Bootstrap CIs for coefficients
    4. Multi-level falsification criteria

    Falsify if:
    1. ΔAIC < 4 vs. constant model (no predictive power)
    2. a coefficient not significant (1/β term irrelevant)
    3. Bootstrap CI for a includes zero

    Parameters
    ----------
    df : DataFrame
        LLM data with columns: run_id, epoch, beta, capability_score, grokking_event
    verbose : bool
        Print detailed results
    n_bootstrap : int
        Number of bootstrap iterations for CI estimation

    Returns
    -------
    results : dict
        - coefficients: Dict with a (1/β), b (log proximity), c (intercept)
        - r_squared: R² of full model
        - aic_full: AIC of full model
        - aic_null: AIC of null (constant) model
        - delta_aic: ΔAIC (null - full)
        - bootstrap_ci: 95% CIs for coefficients
        - falsified: Multi-level falsification result
    """
    from scipy.optimize import curve_fit

    # Extract grokking events with context
    grokking_data = []

    for run_id in df['run_id'].unique():
        run_data = df[df['run_id'] == run_id].sort_values('epoch')
        grok_epochs = run_data[run_data['grokking_event'] == 1]['epoch'].values

        if len(grok_epochs) == 0:
            continue

        for grok_epoch in grok_epochs:
            # Find β and capability score before grokking
            pre_grok = run_data[run_data['epoch'] < grok_epoch]
            if len(pre_grok) > 0:
                beta_pre = pre_grok['beta'].values[-1]
                capability_pre = pre_grok['capability_score'].values[-1]
                delay = grok_epoch - run_data['epoch'].values[0]

                # Estimate Θ from capability scores (normalize to 0-100)
                capability_seq = run_data['capability_score'].values
                if len(capability_seq) > 2:
                    # Θ ≈ midpoint of capability transition
                    Theta_est = (np.min(capability_seq) + np.max(capability_seq)) / 2.0
                    R_est = capability_pre
                    proximity = np.abs(R_est - Theta_est) + 1e-6  # Avoid log(0)

                    grokking_data.append({
                        'delay': delay,
                        'beta': beta_pre,
                        'inv_beta': 1.0 / beta_pre,
                        'log_proximity': np.log(proximity),
                        'R': R_est,
                        'Theta': Theta_est,
                    })

    if len(grokking_data) < 5:
        return {
            'coefficients': {'a': np.nan, 'b': np.nan, 'c': np.nan},
            'r_squared': np.nan,
            'aic_full': np.nan,
            'aic_null': np.nan,
            'delta_aic': np.nan,
            'bootstrap_ci': {},
            'falsified': None,
            'message': 'Insufficient grokking events (need ≥5)',
        }

    # Convert to arrays
    delays = np.array([d['delay'] for d in grokking_data])
    inv_betas = np.array([d['inv_beta'] for d in grokking_data])
    log_proximities = np.array([d['log_proximity'] for d in grokking_data])

    # Full model: τ* = a/β + b·log(|R-Θ|) + c
    def full_model(X, a, b, c):
        inv_beta, log_prox = X
        return a * inv_beta + b * log_prox + c

    try:
        X_full = np.vstack([inv_betas, log_proximities])
        popt_full, pcov_full = curve_fit(full_model, X_full, delays, maxfev=5000)
        a_fit, b_fit, c_fit = popt_full

        # Predictions and R²
        delays_pred = full_model(X_full, a_fit, b_fit, c_fit)
        ss_res = np.sum((delays - delays_pred) ** 2)
        ss_tot = np.sum((delays - np.mean(delays)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        # AIC calculation
        n = len(delays)
        k_full = 3  # 3 parameters (a, b, c)
        log_likelihood_full = -0.5 * n * np.log(2 * np.pi * ss_res / n) - 0.5 * n
        aic_full = 2 * k_full - 2 * log_likelihood_full

        # Null model: τ* = constant
        mean_delay = np.mean(delays)
        ss_res_null = np.sum((delays - mean_delay) ** 2)
        k_null = 1
        log_likelihood_null = -0.5 * n * np.log(2 * np.pi * ss_res_null / n) - 0.5 * n
        aic_null = 2 * k_null - 2 * log_likelihood_null

        delta_aic = aic_null - aic_full

        # Bootstrap CIs
        bootstrap_coeffs = {'a': [], 'b': [], 'c': []}
        rng = np.random.RandomState(42)

        for _ in range(n_bootstrap):
            indices = rng.choice(len(delays), size=len(delays), replace=True)
            delays_boot = delays[indices]
            inv_betas_boot = inv_betas[indices]
            log_prox_boot = log_proximities[indices]

            X_boot = np.vstack([inv_betas_boot, log_prox_boot])
            try:
                popt_boot, _ = curve_fit(full_model, X_boot, delays_boot, maxfev=5000)
                bootstrap_coeffs['a'].append(popt_boot[0])
                bootstrap_coeffs['b'].append(popt_boot[1])
                bootstrap_coeffs['c'].append(popt_boot[2])
            except:
                continue

        # Compute 95% CIs
        bootstrap_ci = {}
        for coef in ['a', 'b', 'c']:
            if len(bootstrap_coeffs[coef]) > 0:
                lower = np.percentile(bootstrap_coeffs[coef], 2.5)
                upper = np.percentile(bootstrap_coeffs[coef], 97.5)
                bootstrap_ci[coef] = (lower, upper)
            else:
                bootstrap_ci[coef] = (np.nan, np.nan)

        # Falsification criteria
        falsified_aic = delta_aic < 4  # No improvement over null
        falsified_coef_a = (bootstrap_ci['a'][0] <= 0 and bootstrap_ci['a'][1] >= 0)  # CI includes 0
        falsified_r2 = r_squared < 0.3  # Poor fit

        falsified = falsified_aic or falsified_coef_a or falsified_r2

        if verbose:
            print(f"  Full model: τ* = a/β + b·log(|R-Θ|) + c")
            print(f"    a (1/β coef): {a_fit:.3f} [{bootstrap_ci['a'][0]:.3f}, {bootstrap_ci['a'][1]:.3f}]")
            print(f"    b (log coef): {b_fit:.3f} [{bootstrap_ci['b'][0]:.3f}, {bootstrap_ci['b'][1]:.3f}]")
            print(f"    c (intercept): {c_fit:.3f} [{bootstrap_ci['c'][0]:.3f}, {bootstrap_ci['c'][1]:.3f}]")
            print(f"  R²: {r_squared:.3f}")
            print(f"  ΔAIC (null - full): {delta_aic:.1f}")
            print(f"  Mean grokking delay: {mean_delay:.1f} epochs")
            print()
            if falsified_aic:
                print(f"    ⚠️  ΔAIC={delta_aic:.1f} < 4 (no improvement over null)")
            if falsified_coef_a:
                print(f"    ⚠️  Coefficient 'a' CI includes zero (1/β term not significant)")
            if falsified_r2:
                print(f"    ⚠️  R²={r_squared:.3f} < 0.3 (poor fit)")
            print()

        return {
            'coefficients': {'a': a_fit, 'b': b_fit, 'c': c_fit},
            'r_squared': r_squared,
            'aic_full': aic_full,
            'aic_null': aic_null,
            'delta_aic': delta_aic,
            'bootstrap_ci': bootstrap_ci,
            'mean_delay': mean_delay,
            'n_events': len(delays),
            'falsified': falsified,
            'falsification_details': {
                'aic': falsified_aic,
                'coef_a': falsified_coef_a,
                'r2': falsified_r2,
            },
            'message': 'FALSIFIED' if falsified else 'VALIDATED',
        }

    except Exception as e:
        return {
            'coefficients': {'a': np.nan, 'b': np.nan, 'c': np.nan},
            'r_squared': np.nan,
            'aic_full': np.nan,
            'aic_null': np.nan,
            'delta_aic': np.nan,
            'bootstrap_ci': {},
            'falsified': None,
            'message': f'Fit failed: {str(e)}',
        }


# ═══════════════════════════════════════════════════════════════
# CROSS-VALIDATION: K-FOLD VALIDATION (v2.1)
# ═══════════════════════════════════════════════════════════════

def cross_validate_tests(
    df: pd.DataFrame,
    k_folds: int = 5,
    verbose: bool = True
) -> Dict:
    """Perform k-fold cross-validation on all 4 tests.

    Validates robustness of findings by splitting data into k folds
    and computing metrics on held-out test sets.

    Parameters
    ----------
    df : DataFrame
        LLM training data with all required columns
    k_folds : int
        Number of folds for cross-validation
    verbose : bool
        Print detailed results

    Returns
    -------
    results : dict
        Cross-validation scores for each test:
        - test1_autocorr: Mean autocorrelation across folds
        - test2_correlation: Mean grokking-β correlation across folds
        - test3_final_beta: Mean final β across folds
        - test4_r_squared: Mean R² for implosive delay model across folds
        - std_*: Standard deviations for each metric
    """
    from sklearn.model_selection import KFold

    # Get unique run IDs
    run_ids = df['run_id'].unique()
    n_runs = len(run_ids)

    if n_runs < k_folds:
        return {
            'message': f'Insufficient runs for {k_folds}-fold CV (have {n_runs})',
            'mean_test1_autocorr': np.nan,
            'mean_test2_corr': np.nan,
            'mean_test3_beta': np.nan,
            'mean_test4_r2': np.nan,
        }

    kf = KFold(n_splits=k_folds, shuffle=True, random_state=42)

    # Store fold results
    fold_results = {
        'test1_autocorr': [],
        'test2_corr': [],
        'test3_beta': [],
        'test4_r2': [],
        'test4_delta_aic': [],
    }

    for fold_idx, (train_idx, test_idx) in enumerate(kf.split(run_ids)):
        if verbose:
            print(f"  Fold {fold_idx + 1}/{k_folds}:")

        # Split data by run IDs
        test_run_ids = run_ids[test_idx]
        df_fold = df[df['run_id'].isin(test_run_ids)]

        # Test 1: Spiral Coherence
        result1 = test_spiral_coherence(df_fold, verbose=False)
        if not np.isnan(result1['mean_autocorr']):
            fold_results['test1_autocorr'].append(result1['mean_autocorr'])
            if verbose:
                print(f"    Test 1 (Autocorr): {result1['mean_autocorr']:.3f}")

        # Test 2: Grokking β-Jumps
        result2 = test_grokking_beta_jumps(df_fold, verbose=False)
        if not np.isnan(result2['mean_correlation']):
            fold_results['test2_corr'].append(result2['mean_correlation'])
            if verbose:
                print(f"    Test 2 (Grokking Corr): {result2['mean_correlation']:.3f}")

        # Test 3: Fixpoint Convergence
        result3 = test_fixpoint_convergence(df_fold, verbose=False)
        if not np.isnan(result3['final_mean_beta']):
            fold_results['test3_beta'].append(result3['final_mean_beta'])
            if verbose:
                print(f"    Test 3 (Final β): {result3['final_mean_beta']:.3f}")

        # Test 4: Implosive Delay (reduced bootstrap for speed)
        result4 = test_implosive_delay(df_fold, verbose=False, n_bootstrap=200)
        if not np.isnan(result4['r_squared']):
            fold_results['test4_r2'].append(result4['r_squared'])
            fold_results['test4_delta_aic'].append(result4['delta_aic'])
            if verbose:
                print(f"    Test 4 (R²): {result4['r_squared']:.3f}, ΔAIC: {result4['delta_aic']:.1f}")

        if verbose:
            print()

    # Compute statistics across folds
    cv_summary = {}
    for key, values in fold_results.items():
        if len(values) > 0:
            cv_summary[f'mean_{key}'] = np.mean(values)
            cv_summary[f'std_{key}'] = np.std(values)
            cv_summary[f'cv_{key}'] = np.std(values) / np.mean(values) if np.mean(values) != 0 else np.nan
        else:
            cv_summary[f'mean_{key}'] = np.nan
            cv_summary[f'std_{key}'] = np.nan
            cv_summary[f'cv_{key}'] = np.nan

    cv_summary['n_folds'] = k_folds
    cv_summary['n_folds_completed'] = len(fold_results['test1_autocorr'])

    if verbose:
        print("═" * 70)
        print(f"CROSS-VALIDATION SUMMARY ({k_folds}-Fold)")
        print("═" * 70)
        print(f"  Test 1 (Autocorr): {cv_summary['mean_test1_autocorr']:.3f} ± {cv_summary['std_test1_autocorr']:.3f}")
        print(f"  Test 2 (Grokking Corr): {cv_summary['mean_test2_corr']:.3f} ± {cv_summary['std_test2_corr']:.3f}")
        print(f"  Test 3 (Final β): {cv_summary['mean_test3_beta']:.3f} ± {cv_summary['std_test3_beta']:.3f}")
        print(f"  Test 4 (R²): {cv_summary['mean_test4_r2']:.3f} ± {cv_summary['std_test4_r2']:.3f}")
        print(f"  Test 4 (ΔAIC): {cv_summary['mean_test4_delta_aic']:.1f} ± {cv_summary['std_test4_delta_aic']:.1f}")
        print()

    return cv_summary


# ═══════════════════════════════════════════════════════════════
# VISUALIZATION
# ═══════════════════════════════════════════════════════════════

def create_spiral_plots(
    df: pd.DataFrame,
    spiral_result: Dict,
    grokking_result: Dict,
    output_path: str
):
    """Generate 4-panel validation figure."""
    if not HAS_MATPLOTLIB:
        print("Skipping plots (matplotlib not available)")
        return

    fig = plt.figure(figsize=(16, 12))

    # Panel A: 3D Spiral Trajectory
    ax = fig.add_subplot(2, 2, 1, projection='3d')

    for run_id in df['run_id'].unique()[:3]:  # Plot first 3 runs
        run_data = df[df['run_id'] == run_id].sort_values('epoch')
        epochs = run_data['epoch'].values
        betas = run_data['beta'].values

        # Spiral coordinates: (β·cos(epoch), β·sin(epoch), epoch)
        theta = epochs * 0.2  # Angular frequency
        x = betas * np.cos(theta)
        y = betas * np.sin(theta)
        z = epochs

        ax.plot(x, y, z, linewidth=2, alpha=0.7, label=f'Run {run_id}')

        # Mark grokking events
        grok_mask = run_data['grokking_event'] == 1
        if grok_mask.sum() > 0:
            x_grok = betas[grok_mask] * np.cos(theta[grok_mask])
            y_grok = betas[grok_mask] * np.sin(theta[grok_mask])
            z_grok = epochs[grok_mask]
            ax.scatter(x_grok, y_grok, z_grok, s=100, c='red', marker='*',
                      zorder=5, edgecolors='black', linewidths=1)

    ax.set_xlabel('β·cos(θ)', fontsize=10)
    ax.set_ylabel('β·sin(θ)', fontsize=10)
    ax.set_zlabel('Training Epoch', fontsize=10)
    ax.set_title('A: 3D β-Spiral Trajectories', fontsize=12, fontweight='bold')
    ax.legend(fontsize=8)

    # Panel B: β Temporal Evolution
    ax = fig.add_subplot(2, 2, 2)

    for run_id in df['run_id'].unique()[:5]:
        run_data = df[df['run_id'] == run_id].sort_values('epoch')
        ax.plot(run_data['epoch'], run_data['beta'], linewidth=2, alpha=0.6,
               label=f'Run {run_id}')

        # Mark grokking
        grok_epochs = run_data[run_data['grokking_event'] == 1]['epoch']
        grok_betas = run_data[run_data['grokking_event'] == 1]['beta']
        ax.scatter(grok_epochs, grok_betas, s=150, c='red', marker='*',
                  zorder=5, edgecolors='black', linewidths=1.5)

    ax.axhline(BETA_FIXPOINT_PHI3, color='blue', linestyle='--', linewidth=2,
              label=f'Φ³ fixpoint ({BETA_FIXPOINT_PHI3:.2f})')
    ax.fill_between([0, df['epoch'].max()],
                     BETA_FIXPOINT_PHI3 - 0.8, BETA_FIXPOINT_PHI3 + 0.8,
                     alpha=0.2, color='blue')
    ax.set_xlabel('Training Epoch', fontsize=11)
    ax.set_ylabel('β (Steepness)', fontsize=11)
    ax.set_title('B: β Temporal Evolution (⭐ = Grokking)', fontsize=12, fontweight='bold')
    ax.legend(fontsize=8, loc='best')
    ax.grid(True, alpha=0.3)

    # Panel C: Grokking β-Jump Distribution
    ax = fig.add_subplot(2, 2, 3)

    all_jumps_grok = []
    all_jumps_nogrok = []

    for run_id in df['run_id'].unique():
        run_data = df[df['run_id'] == run_id].sort_values('epoch')
        beta_jumps = np.diff(run_data['beta'].values)
        grok_events = run_data['grokking_event'].values[1:]

        grok_mask = grok_events == 1
        all_jumps_grok.extend(np.abs(beta_jumps[grok_mask]).tolist())
        all_jumps_nogrok.extend(np.abs(beta_jumps[~grok_mask]).tolist())

    if all_jumps_grok and all_jumps_nogrok:
        bins = np.linspace(0, max(max(all_jumps_grok), max(all_jumps_nogrok)), 20)
        ax.hist(all_jumps_nogrok, bins=bins, alpha=0.6, color='gray',
               label='Normal training', density=True)
        ax.hist(all_jumps_grok, bins=bins, alpha=0.8, color='red',
               label='Grokking events', density=True)

        ax.set_xlabel('|Δβ| (Jump Magnitude)', fontsize=11)
        ax.set_ylabel('Density', fontsize=11)
        ax.set_title(f'C: β-Jump Distribution (Corr={grokking_result["mean_correlation"]:.2f})',
                    fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')

    # Panel D: Convergence to Φ³ Fixpoint
    ax = fig.add_subplot(2, 2, 4)

    for run_id in df['run_id'].unique()[:5]:
        run_data = df[df['run_id'] == run_id].sort_values('epoch')

        # Cumulative mean β
        cumulative_mean = np.cumsum(run_data['beta'].values) / np.arange(1, len(run_data) + 1)
        ax.plot(run_data['epoch'], cumulative_mean, linewidth=2, alpha=0.6,
               label=f'Run {run_id}')

    ax.axhline(BETA_FIXPOINT_PHI3, color='blue', linestyle='--', linewidth=2,
              label=f'Φ³ fixpoint ({BETA_FIXPOINT_PHI3:.2f})')
    ax.fill_between([0, df['epoch'].max()],
                     BETA_FIXPOINT_PHI3 - 0.5, BETA_FIXPOINT_PHI3 + 0.5,
                     alpha=0.2, color='blue', label='Target zone')
    ax.set_xlabel('Training Epoch', fontsize=11)
    ax.set_ylabel('Cumulative Mean β', fontsize=11)
    ax.set_title('D: Convergence to Φ³ Attractor', fontsize=12, fontweight='bold')
    ax.legend(fontsize=8, loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved validation plot: {output_path}")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='LLM β-Spiral Trajectory Analysis (UTAC Type-6 Validation)'
    )
    parser.add_argument('--input', default='data/implosion/llm_runs_beta.csv',
                        help='Path to LLM training β trajectories CSV')
    parser.add_argument('--out', default='paper/figures/llm_beta_spiral.png',
                        help='Output path for validation figure')
    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed results')
    parser.add_argument('--cross-validate', action='store_true',
                        help='Perform k-fold cross-validation (adds ~2-3 minutes)')
    parser.add_argument('--k-folds', type=int, default=5,
                        help='Number of folds for cross-validation (default: 5)')

    args = parser.parse_args()

    print("═" * 70)
    print("UTAC Type-6 Validation: LLM β-Spiral Trajectory Analysis")
    print("Training Dynamics, Grokking, and Fixpoint Convergence")
    print("═" * 70)
    print()

    # Load data
    print(f"Loading data from: {args.input}")
    try:
        df = load_llm_data(args.input)
        print(f"  → {len(df)} training epochs loaded")
        print(f"  → Runs: {df['run_id'].nunique()}")
        print(f"  → Grokking events: {df['grokking_event'].sum()}")
        print()
    except Exception as e:
        print(f"ERROR: Failed to load data: {e}")
        return

    # TEST 1: Spiral Coherence
    print("─" * 70)
    print("TEST 1: Spiral Coherence (Temporal Autocorrelation)")
    print("─" * 70)
    spiral_result = test_spiral_coherence(df, verbose=True)

    if spiral_result['falsified'] == False:
        print(f"  ✓ VALIDATED: Autocorr={spiral_result['mean_autocorr']:.3f} > 0.3")
    elif spiral_result['falsified'] == True:
        print(f"  ⚠️  FALSIFIED: Autocorr={spiral_result['mean_autocorr']:.3f} < 0.3")
    else:
        print(f"  ○ INCONCLUSIVE: {spiral_result['message']}")
    print()

    # TEST 2: Grokking β-Jumps
    print("─" * 70)
    print("TEST 2: Grokking as β-Jumps")
    print("─" * 70)
    grokking_result = test_grokking_beta_jumps(df, verbose=True)

    if grokking_result['falsified'] == False:
        print(f"  ✓ VALIDATED: Correlation={grokking_result['mean_correlation']:.3f} > 0.3")
    elif grokking_result['falsified'] == True:
        print(f"  ⚠️  FALSIFIED: Correlation={grokking_result['mean_correlation']:.3f} < 0.3")
    else:
        print(f"  ○ INCONCLUSIVE: {grokking_result['message']}")
    print()

    # TEST 3: Fixpoint Convergence
    print("─" * 70)
    print("TEST 3: Convergence to Φ³ Fixpoint")
    print("─" * 70)
    fixpoint_result = test_fixpoint_convergence(df, verbose=True)

    if fixpoint_result['falsified'] == False:
        print(f"  ✓ VALIDATED: Final β={fixpoint_result['final_mean_beta']:.3f} ∈ [3.5, 5.0]")
    elif fixpoint_result['falsified'] == True:
        print(f"  ⚠️  FALSIFIED: Final β outside target range or variance increased")
    else:
        print(f"  ○ INCONCLUSIVE: {fixpoint_result['message']}")
    print()

    # TEST 4: Implosive Delay (REFINED v2.1)
    print("─" * 70)
    print("TEST 4: Implosive Delay (τ* = a/β + b·log(|R-Θ|) + c) [REFINED v2.1]")
    print("─" * 70)
    delay_result = test_implosive_delay(df, verbose=True, n_bootstrap=1000)

    if delay_result['falsified'] == False:
        print(f"  ✓ VALIDATED: R²={delay_result['r_squared']:.3f}, ΔAIC={delay_result['delta_aic']:.1f}")
    elif delay_result['falsified'] == True:
        print(f"  ⚠️  FALSIFIED: {delay_result['message']}")
        if 'falsification_details' in delay_result:
            details = delay_result['falsification_details']
            if details.get('aic'): print(f"      - Poor model fit (ΔAIC < 4)")
            if details.get('coef_a'): print(f"      - 1/β coefficient not significant")
            if details.get('r2'): print(f"      - R² < 0.3")
    else:
        print(f"  ○ INCONCLUSIVE: {delay_result['message']}")
    print()

    # Optional: Cross-Validation
    cv_result = None
    if args.cross_validate:
        print("─" * 70)
        print(f"CROSS-VALIDATION ({args.k_folds}-Fold)")
        print("─" * 70)
        print("Running k-fold cross-validation (this may take 2-3 minutes)...")
        print()
        cv_result = cross_validate_tests(df, k_folds=args.k_folds, verbose=True)

    # Summary
    print("═" * 70)
    print("SUMMARY")
    print("═" * 70)

    tests = [spiral_result, grokking_result, fixpoint_result, delay_result]
    validated_count = sum(1 for t in tests if t.get('falsified') == False)
    falsified_count = sum(1 for t in tests if t.get('falsified') == True)

    print(f"  Tests run: 4")
    print(f"  Validated: {validated_count}")
    print(f"  Falsified: {falsified_count}")
    print(f"  Inconclusive: {4 - validated_count - falsified_count}")
    if cv_result and 'n_folds_completed' in cv_result:
        print(f"  Cross-validation: {cv_result['n_folds_completed']}/{cv_result['n_folds']} folds completed")
    print()

    if falsified_count >= 2:
        print("  ⚠️  LLM β-SPIRAL MATERIALLY FALSIFIED (≥2 tests failed)")
    elif falsified_count == 1:
        print("  ⚠️  REVISION NEEDED (1 test failed; refinement suggested)")
    elif validated_count >= 3:
        print("  ✓ LLM β-SPIRAL PROVISIONALLY VALIDATED")
    else:
        print("  ○ INCONCLUSIVE (insufficient evidence)")
    print()

    # Generate plots
    if HAS_MATPLOTLIB:
        print("─" * 70)
        print("Generating spiral visualization...")
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        create_spiral_plots(df, spiral_result, grokking_result, args.out)

    print("═" * 70)
    print("Analysis complete.")
    print("═" * 70)


if __name__ == '__main__':
    main()
