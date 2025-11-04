"""
Threshold sandbox simulation for exploring β as a function of coupling and coherence.

This module implements a coupled logistic lattice with adjustable effective coupling (C_eff),
dimensionality (D_eff), and coherence/noise ratio (SNR). It allows systematic exploration
of how system architecture influences the steepness parameter β.

Author: Johann Römer et al.
License: MIT
DOI: 10.5281/zenodo.17472834
"""

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from pathlib import Path
import json
from typing import Tuple, Dict, List
import argparse


def logistic(x: np.ndarray, beta: float, theta: float) -> np.ndarray:
    """
    Standard logistic function.

    Parameters
    ----------
    x : array-like
        Control parameter values
    beta : float
        Steepness parameter
    theta : float
        Threshold parameter

    Returns
    -------
    array-like
        Logistic response values
    """
    return 1 / (1 + np.exp(-beta * (x - theta)))


def simulate_system(
    N: int = 1000,
    C_eff: float = 0.8,
    D_eff: int = 10,
    SNR: float = 5.0,
    noise: float = 0.05,
    seed: int = 1337
) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Simulate a threshold system with specified coupling and coherence parameters.

    Parameters
    ----------
    N : int
        Number of sample points
    C_eff : float
        Effective coupling strength [0, 1]
    D_eff : int
        Effective dimensionality (number of independent degrees of freedom)
    SNR : float
        Signal-to-noise ratio (coherent/stochastic forcing ratio)
    noise : float
        Gaussian noise amplitude
    seed : int
        Random seed for reproducibility

    Returns
    -------
    R : ndarray
        Control parameter values
    field : ndarray
        Observed field response with noise
    beta_true : float
        True underlying β parameter
    """
    np.random.seed(seed)

    R = np.linspace(0, 1, N)

    # β increases with coupling and coherence
    coupling_term = C_eff / (1 + D_eff * 0.1)  # Higher D_eff reduces effective coupling
    coherence = np.tanh(SNR * coupling_term)

    # Theoretical β ranges from 3 (low coupling) to 8 (high coupling)
    beta_true = 3.0 + 5.0 * coherence
    theta = 0.5

    # Generate clean response
    response = logistic(R, beta_true, theta)

    # Add stochastic noise
    noise_term = np.random.normal(0, noise, size=response.shape)
    field = np.clip(response + noise_term, 0, 1)

    return R, field, beta_true


def estimate_beta(R: np.ndarray, field: np.ndarray) -> Tuple[float, float, float]:
    """
    Estimate β and θ from simulated data.

    Parameters
    ----------
    R : ndarray
        Control parameter
    field : ndarray
        Observed response

    Returns
    -------
    beta_est : float
        Estimated β
    theta_est : float
        Estimated θ
    r_squared : float
        Goodness of fit
    """
    try:
        popt, _ = curve_fit(
            logistic,
            R,
            field,
            p0=[4.0, 0.5],
            bounds=([0.1, 0.0], [20.0, 1.0]),
            maxfev=10000
        )
        beta_est, theta_est = popt

        # Calculate R²
        residuals = field - logistic(R, beta_est, theta_est)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((field - np.mean(field))**2)
        r_squared = 1 - (ss_res / ss_tot)

        return beta_est, theta_est, r_squared
    except Exception as e:
        print(f"Fit failed: {e}")
        return np.nan, np.nan, np.nan


def run_experiment(
    output_dir: str = "analysis/results",
    plot: bool = True
) -> pd.DataFrame:
    """
    Run systematic parameter sweep over C_eff, D_eff, and SNR.

    Parameters
    ----------
    output_dir : str
        Directory for output files
    plot : bool
        Whether to generate plots

    Returns
    -------
    DataFrame
        Results table with beta estimates for each parameter combination
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = []

    # Parameter sweep
    C_values = np.linspace(0.1, 1.0, 5)
    D_values = [2, 5, 10, 20]
    SNR_values = [1, 3, 5, 10]

    print("Running β-driver simulation sweep...")
    print(f"Total combinations: {len(C_values) * len(D_values) * len(SNR_values)}")

    for C in C_values:
        for D in D_values:
            for SNR in SNR_values:
                R, field, beta_true = simulate_system(
                    C_eff=C,
                    D_eff=D,
                    SNR=SNR,
                    seed=1337
                )
                beta_est, theta_est, r2 = estimate_beta(R, field)

                results.append({
                    'C_eff': C,
                    'D_eff': D,
                    'SNR': SNR,
                    'beta_true': beta_true,
                    'beta_est': beta_est,
                    'theta_est': theta_est,
                    'r_squared': r2
                })

    df = pd.DataFrame(results)

    # Save results
    csv_path = output_path / "sandbox_beta_map.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ Results saved to {csv_path}")

    # Generate summary statistics
    summary = {
        "mean_beta": float(df['beta_est'].mean()),
        "median_beta": float(df['beta_est'].median()),
        "std_beta": float(df['beta_est'].std()),
        "min_beta": float(df['beta_est'].min()),
        "max_beta": float(df['beta_est'].max()),
        "mean_r_squared": float(df['r_squared'].mean()),
        "n_simulations": len(df)
    }

    summary_path = output_path / "sandbox_beta_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Summary saved to {summary_path}")

    # Generate plots
    if plot:
        generate_plots(df, output_path)

    return df


def generate_plots(df: pd.DataFrame, output_path: Path):
    """Generate visualization plots for β-parameter dependencies."""

    # Plot 1: β vs C_eff (averaged over D and SNR)
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # β vs C_eff
    ax = axes[0, 0]
    for SNR in df['SNR'].unique():
        subset = df[df['SNR'] == SNR].groupby('C_eff')['beta_est'].mean()
        ax.plot(subset.index, subset.values, marker='o', label=f'SNR={SNR}')
    ax.set_xlabel('Effective Coupling (C_eff)')
    ax.set_ylabel('Estimated β')
    ax.set_title('β vs Coupling Strength')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # β vs D_eff
    ax = axes[0, 1]
    for SNR in df['SNR'].unique():
        subset = df[df['SNR'] == SNR].groupby('D_eff')['beta_est'].mean()
        ax.plot(subset.index, subset.values, marker='s', label=f'SNR={SNR}')
    ax.set_xlabel('Effective Dimensionality (D_eff)')
    ax.set_ylabel('Estimated β')
    ax.set_title('β vs Dimensionality')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # β vs SNR
    ax = axes[1, 0]
    for C in [0.1, 0.5, 1.0]:
        subset = df[np.isclose(df['C_eff'], C, atol=0.01)].groupby('SNR')['beta_est'].mean()
        ax.plot(subset.index, subset.values, marker='^', label=f'C_eff={C:.1f}')
    ax.set_xlabel('Signal-to-Noise Ratio (SNR)')
    ax.set_ylabel('Estimated β')
    ax.set_title('β vs Coherence')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Heatmap: β as function of C_eff and SNR (D_eff = 10)
    ax = axes[1, 1]
    subset = df[df['D_eff'] == 10].pivot_table(
        values='beta_est',
        index='C_eff',
        columns='SNR'
    )
    im = ax.imshow(subset.values, aspect='auto', cmap='viridis', origin='lower')
    ax.set_xticks(range(len(subset.columns)))
    ax.set_xticklabels(subset.columns)
    ax.set_yticks(range(len(subset.index)))
    ax.set_yticklabels([f'{x:.2f}' for x in subset.index])
    ax.set_xlabel('SNR')
    ax.set_ylabel('C_eff')
    ax.set_title('β Heatmap (D_eff=10)')
    plt.colorbar(im, ax=ax, label='β')

    plt.tight_layout()
    plot_path = output_path / "sandbox_beta_analysis.png"
    plt.savefig(plot_path, dpi=300)
    print(f"✅ Plots saved to {plot_path}")
    plt.close()


def main():
    """Command-line interface for threshold sandbox."""
    parser = argparse.ArgumentParser(
        description="Simulate threshold systems to explore β-parameter drivers"
    )
    parser.add_argument(
        '--output',
        type=str,
        default='analysis/results',
        help='Output directory for results'
    )
    parser.add_argument(
        '--no-plot',
        action='store_true',
        help='Disable plot generation'
    )

    args = parser.parse_args()

    df = run_experiment(
        output_dir=args.output,
        plot=not args.no_plot
    )

    print("\n" + "="*60)
    print("SIMULATION COMPLETE")
    print("="*60)
    print(f"\nβ statistics:")
    print(f"  Mean:   {df['beta_est'].mean():.3f}")
    print(f"  Median: {df['beta_est'].median():.3f}")
    print(f"  Std:    {df['beta_est'].std():.3f}")
    print(f"  Range:  [{df['beta_est'].min():.3f}, {df['beta_est'].max():.3f}]")
    print(f"\nResults saved to: {args.output}/")


if __name__ == "__main__":
    main()
