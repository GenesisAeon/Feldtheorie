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
# TEST 4: IMPLOSIVE DELAY & GROKKING TIME
# ═══════════════════════════════════════════════════════════════

def test_implosive_delay(
    df: pd.DataFrame,
    verbose: bool = True
) -> Dict:
    """Test whether grokking delay follows τ* ∝ (1/β) · log(|R-Θ|).

    Prediction: Time to grokking should be inversely proportional to β
    and logarithmically dependent on proximity to threshold.

    Falsify if no inverse relationship with β (correlation > -0.3).

    Parameters
    ----------
    df : DataFrame
        LLM data with columns: run_id, epoch, beta, grokking_event
    verbose : bool
        Print detailed results

    Returns
    -------
    results : dict
        - correlation_beta_time: Correlation between 1/β and grokking delay
        - mean_delay: Mean epochs to grokking
        - falsified: True if correlation > -0.3
    """
    grokking_delays = []
    beta_at_grokking = []

    for run_id in df['run_id'].unique():
        run_data = df[df['run_id'] == run_id].sort_values('epoch')
        grok_epochs = run_data[run_data['grokking_event'] == 1]['epoch'].values

        if len(grok_epochs) == 0:
            continue

        for grok_epoch in grok_epochs:
            # Find β before grokking
            pre_grok = run_data[run_data['epoch'] < grok_epoch]
            if len(pre_grok) > 0:
                beta_pre = pre_grok['beta'].values[-1]
                delay = grok_epoch - run_data['epoch'].values[0]

                grokking_delays.append(delay)
                beta_at_grokking.append(beta_pre)

    if len(grokking_delays) < 3:
        return {
            'correlation_beta_time': np.nan,
            'mean_delay': np.nan,
            'falsified': None,
            'message': 'Insufficient grokking events',
        }

    # Correlation: 1/β vs. delay (should be positive if τ* ∝ 1/β)
    inv_beta = 1.0 / np.array(beta_at_grokking)
    correlation, pval = stats.pearsonr(inv_beta, grokking_delays)
    mean_delay = np.mean(grokking_delays)

    # Falsification: correlation not positive (no 1/β relationship)
    falsified = correlation < 0.3

    if verbose:
        print(f"  Correlation (1/β ↔ delay): {correlation:.3f} (p={pval:.4f})")
        print(f"  Mean grokking delay: {mean_delay:.1f} epochs")
        print()

    return {
        'correlation_beta_time': correlation,
        'pval': pval,
        'mean_delay': mean_delay,
        'falsified': falsified,
        'message': 'FALSIFIED' if falsified else 'VALIDATED',
    }


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

    # TEST 4: Implosive Delay
    print("─" * 70)
    print("TEST 4: Implosive Delay (τ* ∝ 1/β)")
    print("─" * 70)
    delay_result = test_implosive_delay(df, verbose=True)

    if delay_result['falsified'] == False:
        print(f"  ✓ VALIDATED: Correlation(1/β, delay)={delay_result['correlation_beta_time']:.3f} > 0.3")
    elif delay_result['falsified'] == True:
        print(f"  ⚠️  FALSIFIED: No 1/β relationship found")
    else:
        print(f"  ○ INCONCLUSIVE: {delay_result['message']}")
    print()

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
