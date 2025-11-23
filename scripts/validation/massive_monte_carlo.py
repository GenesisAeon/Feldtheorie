#!/usr/bin/env python3
"""
Massive Monte Carlo Validation (UTAC v5.0)

This script performs large-scale robustness testing of the V5.0 models:
    1. Social Ising Model: Parameter space exploration (Gini × Load)
    2. Cosmic Quantization: Constant variation testing (α × Φ)

The goal is to map out where the models are robust vs. where they break,
providing transparent validation of their predictive domains.

OUTPUTS:
    - Heatmaps showing phase transitions and prediction accuracy
    - CSV files with full results for reproducibility
    - Statistical summaries of robustness

Author: Genesis Aeon (UTAC Framework)
Version: 5.0
"""

import sys
from pathlib import Path

# Add models directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'models'))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy import stats
from typing import Tuple, Dict
import multiprocessing as mp
from functools import partial
from tqdm import tqdm

# Import our models
from social_rigidity_ising import SocialIsingModel
from cosmic_alpha_phi import CosmicQuantization, BOEHME_VELOCITY_KM_S


# ============================================================================
# CONFIGURATION
# ============================================================================

# Monte Carlo parameters
N_ITERATIONS = 100_000  # Total iterations
N_GINI_POINTS = 100     # Grid resolution for heatmaps
N_LOAD_POINTS = 100
N_ALPHA_POINTS = 100
N_PHI_POINTS = 100

# Parameter ranges
GINI_RANGE = (0.1, 0.95)
LOAD_RANGE = (0.5, 3.0)
ALPHA_RANGE = (0.005, 0.01)    # Around 1/137
PHI_RANGE = (1.5, 1.8)          # Around golden ratio

# Random seed
RANDOM_SEED = 1337


# ============================================================================
# SOCIAL ISING MODEL VALIDATION
# ============================================================================

def compute_social_state_grid(
    gini_values: np.ndarray,
    load_values: np.ndarray
) -> Dict[str, np.ndarray]:
    """
    Compute social Ising model across Gini × Load parameter space.

    Args:
        gini_values: Array of Gini coefficients
        load_values: Array of load values

    Returns:
        Dictionary with 2D arrays: rigidity, magnetization, susceptibility
    """
    n_gini = len(gini_values)
    n_load = len(load_values)

    rigidity_grid = np.zeros((n_gini, n_load))
    magnetization_grid = np.zeros((n_gini, n_load))
    susceptibility_grid = np.zeros((n_gini, n_load))
    frozen_grid = np.zeros((n_gini, n_load), dtype=bool)

    model = SocialIsingModel()

    print("Computing social Ising model grid...")
    for i, gini in enumerate(tqdm(gini_values, desc="Gini sweep")):
        for j, load in enumerate(load_values):
            state = model.compute_state(gini, load)
            rigidity_grid[i, j] = state.rigidity
            magnetization_grid[i, j] = state.magnetization
            susceptibility_grid[i, j] = state.susceptibility
            frozen_grid[i, j] = state.is_frozen

    return {
        'rigidity': rigidity_grid,
        'magnetization': magnetization_grid,
        'susceptibility': susceptibility_grid,
        'frozen': frozen_grid,
        'gini_values': gini_values,
        'load_values': load_values
    }


def social_monte_carlo_scan() -> pd.DataFrame:
    """
    Random Monte Carlo sampling of social parameter space.

    Returns:
        DataFrame with sampled parameters and outcomes
    """
    np.random.seed(RANDOM_SEED)

    n_samples = N_ITERATIONS // 10  # Use subset for random scan

    gini_samples = np.random.uniform(GINI_RANGE[0], GINI_RANGE[1], n_samples)
    load_samples = np.random.uniform(LOAD_RANGE[0], LOAD_RANGE[1], n_samples)

    model = SocialIsingModel()
    results = []

    print("\nRandom Monte Carlo scan (social model)...")
    for gini, load in tqdm(zip(gini_samples, load_samples), total=n_samples, desc="MC samples"):
        state = model.compute_state(gini, load)
        results.append({
            'gini': gini,
            'load': load,
            'temperature': state.temperature,
            'rigidity': state.rigidity,
            'magnetization': state.magnetization,
            'susceptibility': state.susceptibility,
            'is_frozen': state.is_frozen
        })

    return pd.DataFrame(results)


# ============================================================================
# COSMIC QUANTIZATION VALIDATION
# ============================================================================

def compute_cosmic_grid(
    alpha_values: np.ndarray,
    phi_values: np.ndarray
) -> Dict[str, np.ndarray]:
    """
    Compute cosmic velocity predictions across α × Φ parameter space.

    Args:
        alpha_values: Array of fine-structure constant values
        phi_values: Array of golden ratio-like values

    Returns:
        Dictionary with 2D arrays: velocities, deviations
    """
    n_alpha = len(alpha_values)
    n_phi = len(phi_values)

    velocity_grid = np.zeros((n_alpha, n_phi))
    deviation_grid = np.zeros((n_alpha, n_phi))
    relative_error_grid = np.zeros((n_alpha, n_phi))

    print("\nComputing cosmic quantization grid...")
    for i, alpha in enumerate(tqdm(alpha_values, desc="α sweep")):
        for j, phi in enumerate(phi_values):
            model = CosmicQuantization(alpha=alpha, phi=phi)
            v = model.predict_velocity()
            deviation = abs(BOEHME_VELOCITY_KM_S - v)

            velocity_grid[i, j] = v
            deviation_grid[i, j] = deviation
            relative_error_grid[i, j] = deviation / BOEHME_VELOCITY_KM_S

    return {
        'velocity': velocity_grid,
        'deviation': deviation_grid,
        'relative_error': relative_error_grid,
        'alpha_values': alpha_values,
        'phi_values': phi_values
    }


def cosmic_monte_carlo_scan() -> pd.DataFrame:
    """
    Random Monte Carlo sampling of cosmic parameter space.

    Returns:
        DataFrame with sampled parameters and outcomes
    """
    np.random.seed(RANDOM_SEED + 1)

    n_samples = N_ITERATIONS // 10

    alpha_samples = np.random.uniform(ALPHA_RANGE[0], ALPHA_RANGE[1], n_samples)
    phi_samples = np.random.uniform(PHI_RANGE[0], PHI_RANGE[1], n_samples)

    results = []

    print("\nRandom Monte Carlo scan (cosmic model)...")
    for alpha, phi in tqdm(zip(alpha_samples, phi_samples), total=n_samples, desc="MC samples"):
        model = CosmicQuantization(alpha=alpha, phi=phi)
        v = model.predict_velocity()
        deviation = abs(BOEHME_VELOCITY_KM_S - v)

        results.append({
            'alpha': alpha,
            'phi': phi,
            'velocity_km_s': v,
            'deviation_km_s': deviation,
            'relative_error': deviation / BOEHME_VELOCITY_KM_S
        })

    return pd.DataFrame(results)


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_social_heatmaps(social_grid: Dict, output_path: Path):
    """Generate heatmap visualizations of social model parameter space."""
    fig = plt.figure(figsize=(18, 5))
    gs = GridSpec(1, 3, figure=fig, wspace=0.3)

    gini_vals = social_grid['gini_values']
    load_vals = social_grid['load_values']

    # Panel 1: Rigidity
    ax1 = fig.add_subplot(gs[0, 0])
    im1 = ax1.contourf(
        gini_vals, load_vals, social_grid['rigidity'].T,
        levels=20, cmap='YlOrRd'
    )
    ax1.set_xlabel('Gini Coefficient', fontsize=12)
    ax1.set_ylabel('Load Factor', fontsize=12)
    ax1.set_title('A. Rigidity β = 1/T', fontsize=14, fontweight='bold')
    plt.colorbar(im1, ax=ax1, label='β')

    # Panel 2: Magnetization
    ax2 = fig.add_subplot(gs[0, 1])
    im2 = ax2.contourf(
        gini_vals, load_vals, social_grid['magnetization'].T,
        levels=20, cmap='RdBu_r'
    )
    ax2.set_xlabel('Gini Coefficient', fontsize=12)
    ax2.set_ylabel('Load Factor', fontsize=12)
    ax2.set_title('B. Magnetization M', fontsize=14, fontweight='bold')
    plt.colorbar(im2, ax=ax2, label='M')

    # Panel 3: Phase diagram
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.contourf(
        gini_vals, load_vals, social_grid['frozen'].T.astype(int),
        levels=[0, 0.5, 1], colors=['#6A994E', '#C73E1D'], alpha=0.5
    )
    ax3.contour(
        gini_vals, load_vals, social_grid['frozen'].T.astype(int),
        levels=[0.5], colors='black', linewidths=2
    )
    ax3.set_xlabel('Gini Coefficient', fontsize=12)
    ax3.set_ylabel('Load Factor', fontsize=12)
    ax3.set_title('C. Phase Diagram', fontsize=14, fontweight='bold')

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#6A994E', alpha=0.5, label='Fluid (T > Tc)'),
        Patch(facecolor='#C73E1D', alpha=0.5, label='Frozen (T < Tc)')
    ]
    ax3.legend(handles=legend_elements, loc='upper left')

    fig.suptitle('Social Ising Model: Parameter Space Exploration', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Social heatmaps saved: {output_path}")


def plot_cosmic_heatmaps(cosmic_grid: Dict, output_path: Path):
    """Generate heatmap visualizations of cosmic model parameter space."""
    fig = plt.figure(figsize=(18, 5))
    gs = GridSpec(1, 3, figure=fig, wspace=0.3)

    alpha_vals = cosmic_grid['alpha_values']
    phi_vals = cosmic_grid['phi_values']

    # Convert to inverse for better readability
    alpha_inv = 1.0 / alpha_vals

    # Panel 1: Velocity prediction
    ax1 = fig.add_subplot(gs[0, 0])
    im1 = ax1.contourf(
        alpha_inv, phi_vals, cosmic_grid['velocity'].T,
        levels=20, cmap='viridis'
    )
    ax1.axvline(137.036, color='red', linestyle='--', linewidth=2, label='α⁻¹ (physical)')
    ax1.axhline(1.618, color='red', linestyle='--', linewidth=2, label='Φ (golden)')
    ax1.set_xlabel('α⁻¹ (inverse fine-structure)', fontsize=12)
    ax1.set_ylabel('Φ-like parameter', fontsize=12)
    ax1.set_title('A. Predicted Velocity [km/s]', fontsize=14, fontweight='bold')
    plt.colorbar(im1, ax=ax1, label='v [km/s]')
    ax1.legend(fontsize=9)

    # Panel 2: Absolute deviation
    ax2 = fig.add_subplot(gs[0, 1])
    im2 = ax2.contourf(
        alpha_inv, phi_vals, cosmic_grid['deviation'].T,
        levels=20, cmap='YlOrRd'
    )
    ax2.axvline(137.036, color='red', linestyle='--', linewidth=2)
    ax2.axhline(1.618, color='red', linestyle='--', linewidth=2)
    ax2.set_xlabel('α⁻¹ (inverse fine-structure)', fontsize=12)
    ax2.set_ylabel('Φ-like parameter', fontsize=12)
    ax2.set_title('B. Deviation from Böhme [km/s]', fontsize=14, fontweight='bold')
    plt.colorbar(im2, ax=ax2, label='|Δv| [km/s]')

    # Panel 3: Relative error
    ax3 = fig.add_subplot(gs[0, 2])
    im3 = ax3.contourf(
        alpha_inv, phi_vals, cosmic_grid['relative_error'].T * 100,
        levels=20, cmap='RdYlGn_r'
    )
    ax3.axvline(137.036, color='red', linestyle='--', linewidth=2)
    ax3.axhline(1.618, color='red', linestyle='--', linewidth=2)
    ax3.set_xlabel('α⁻¹ (inverse fine-structure)', fontsize=12)
    ax3.set_ylabel('Φ-like parameter', fontsize=12)
    ax3.set_title('C. Relative Error [%]', fontsize=14, fontweight='bold')
    plt.colorbar(im3, ax=ax3, label='Error [%]')

    fig.suptitle('Cosmic Quantization: Parameter Space Exploration', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Cosmic heatmaps saved: {output_path}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run complete massive Monte Carlo validation."""
    print("=" * 70)
    print("MASSIVE MONTE CARLO VALIDATION (UTAC v5.0)")
    print("=" * 70)
    print(f"Total iterations: {N_ITERATIONS:,}")
    print(f"Random seed: {RANDOM_SEED}")
    print()

    # Create output directories
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'derived'
    figures_dir = Path(__file__).parent.parent.parent / 'figures'
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # SOCIAL ISING MODEL
    # ========================================================================
    print("\n" + "=" * 70)
    print("PART 1: SOCIAL ISING MODEL VALIDATION")
    print("=" * 70)

    # Grid scan
    gini_grid = np.linspace(GINI_RANGE[0], GINI_RANGE[1], N_GINI_POINTS)
    load_grid = np.linspace(LOAD_RANGE[0], LOAD_RANGE[1], N_LOAD_POINTS)
    social_grid = compute_social_state_grid(gini_grid, load_grid)

    # Monte Carlo scan
    social_mc_df = social_monte_carlo_scan()

    # Save results
    social_mc_path = output_dir / 'monte_carlo_social_results.csv'
    social_mc_df.to_csv(social_mc_path, index=False)
    print(f"✓ Social MC results saved: {social_mc_path}")

    # Summary statistics
    print("\nSOCIAL MODEL SUMMARY:")
    print(f"  Frozen states: {social_mc_df['is_frozen'].sum()} / {len(social_mc_df)} ({100*social_mc_df['is_frozen'].mean():.1f}%)")
    print(f"  Mean rigidity: {social_mc_df['rigidity'].mean():.2f} ± {social_mc_df['rigidity'].std():.2f}")
    print(f"  Mean magnetization: {social_mc_df['magnetization'].mean():.3f} ± {social_mc_df['magnetization'].std():.3f}")

    # Visualize
    social_heatmap_path = figures_dir / 'monte_carlo_social_heatmaps.png'
    plot_social_heatmaps(social_grid, social_heatmap_path)

    # ========================================================================
    # COSMIC QUANTIZATION
    # ========================================================================
    print("\n" + "=" * 70)
    print("PART 2: COSMIC QUANTIZATION VALIDATION")
    print("=" * 70)

    # Grid scan
    alpha_grid = np.linspace(ALPHA_RANGE[0], ALPHA_RANGE[1], N_ALPHA_POINTS)
    phi_grid = np.linspace(PHI_RANGE[0], PHI_RANGE[1], N_PHI_POINTS)
    cosmic_grid = compute_cosmic_grid(alpha_grid, phi_grid)

    # Monte Carlo scan
    cosmic_mc_df = cosmic_monte_carlo_scan()

    # Save results
    cosmic_mc_path = output_dir / 'monte_carlo_cosmic_results.csv'
    cosmic_mc_df.to_csv(cosmic_mc_path, index=False)
    print(f"✓ Cosmic MC results saved: {cosmic_mc_path}")

    # Summary statistics
    print("\nCOSMIC MODEL SUMMARY:")
    print(f"  Mean deviation: {cosmic_mc_df['deviation_km_s'].mean():.2f} ± {cosmic_mc_df['deviation_km_s'].std():.2f} km/s")
    print(f"  Mean relative error: {100*cosmic_mc_df['relative_error'].mean():.2f} ± {100*cosmic_mc_df['relative_error'].std():.2f}%")
    print(f"  Min deviation: {cosmic_mc_df['deviation_km_s'].min():.2f} km/s")
    print(f"  Best parameters: α={cosmic_mc_df.loc[cosmic_mc_df['deviation_km_s'].idxmin(), 'alpha']:.6f}, Φ={cosmic_mc_df.loc[cosmic_mc_df['deviation_km_s'].idxmin(), 'phi']:.6f}")

    # Visualize
    cosmic_heatmap_path = figures_dir / 'monte_carlo_cosmic_heatmaps.png'
    plot_cosmic_heatmaps(cosmic_grid, cosmic_heatmap_path)

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)
    print(f"Results saved in: {output_dir}")
    print(f"Figures saved in: {figures_dir}")
    print("\nKey Findings:")
    print(f"  1. Social model: {100*social_mc_df['is_frozen'].mean():.1f}% of parameter space shows phase transition")
    print(f"  2. Cosmic model: Best-fit deviation = {cosmic_mc_df['deviation_km_s'].min():.2f} km/s")
    print("=" * 70)


if __name__ == "__main__":
    main()
