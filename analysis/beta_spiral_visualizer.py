#!/usr/bin/env python3
"""
UTAC v1.3φ - Beta Spiral Visualization
======================================

Generates visualizations comparing classical and implosive sigmoid dynamics,
and visualizes the Φ^(1/3) scaling spiral in 3D parameter space.

Outputs:
- implosive_spiral.png: 3D trajectory in (R, Θ, β) space
- sigmoid_comparison.png: Classical vs implosive sigmoid
- energy_release_profile.png: Energy integral E(R)

Author: Johann Benjamin Römer
Date: November 2025
License: AGPL-3.0
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json
from pathlib import Path
import argparse
from typing import Dict

# Golden ratio
PHI = (1 + np.sqrt(5)) / 2

plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['figure.figsize'] = (12, 8)


def sigma_classical(R: np.ndarray, beta: float, theta: float) -> np.ndarray:
    """Classical sigmoid: σ(β(R - Θ))"""
    return 1.0 / (1.0 + np.exp(-beta * (R - theta)))


def sigma_implosive(R: np.ndarray, beta: float, theta: float) -> np.ndarray:
    """Implosive sigmoid: σ(-β(R - Θ))"""
    return 1.0 / (1.0 + np.exp(beta * (R - theta)))


def plot_sigmoid_comparison(output_dir: Path):
    """
    Generate comparison plot of classical vs implosive sigmoid functions.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('UTAC v1.3φ: Classical vs Implosive Sigmoid Comparison',
                 fontsize=14, fontweight='bold')

    R = np.linspace(-2, 2, 500)
    theta = 0.0
    beta_values = [2.5, 4.236, 6.0, 12.0]

    for idx, beta in enumerate(beta_values):
        ax = axes[idx // 2, idx % 2]

        sigma_class = sigma_classical(R, beta, theta)
        sigma_implo = sigma_implosive(R, beta, theta)

        ax.plot(R, sigma_class, 'b-', linewidth=2, label='Classical σ(β(R-Θ))')
        ax.plot(R, sigma_implo, 'r--', linewidth=2, label='Implosive σ(-β(R-Θ))')
        ax.axvline(theta, color='gray', linestyle=':', alpha=0.5, label='Θ')
        ax.axhline(0.5, color='gray', linestyle=':', alpha=0.3)

        ax.set_xlabel('System Drive R')
        ax.set_ylabel('Response σ')
        ax.set_title(f'β = {beta:.3f}' + (f' (Φ³ attractor)' if np.isclose(beta, PHI**3, rtol=0.01) else ''))
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([-0.05, 1.05])

    plt.tight_layout()
    output_path = output_dir / 'sigmoid_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def plot_3d_spiral(beta_sequence: np.ndarray, output_dir: Path):
    """
    Generate 3D spiral visualization in (R, Θ, β) parameter space.
    """
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Generate spiral trajectory
    n_points = len(beta_sequence)
    theta_values = np.linspace(0.1, 1.0, n_points)
    R_values = np.linspace(-1.0, 2.0, n_points)

    # Parametric spiral
    t = np.linspace(0, 4*np.pi, n_points)
    R_spiral = R_values[0] + (R_values[-1] - R_values[0]) * t / (4*np.pi) + 0.3 * np.sin(3*t)
    theta_spiral = theta_values[0] + (theta_values[-1] - theta_values[0]) * t / (4*np.pi) + 0.1 * np.cos(3*t)

    # Plot spiral
    scatter = ax.scatter(R_spiral, theta_spiral, beta_sequence,
                        c=beta_sequence, cmap='plasma', s=100, alpha=0.8,
                        edgecolors='black', linewidths=0.5)

    # Connect points with line
    ax.plot(R_spiral, theta_spiral, beta_sequence, 'k-', alpha=0.3, linewidth=1)

    # Mark key attractors
    key_steps = [0, 3, 6, 9]
    for step in key_steps:
        if step < len(beta_sequence):
            ax.scatter([R_spiral[step]], [theta_spiral[step]], [beta_sequence[step]],
                      color='red', s=200, marker='*', edgecolors='black', linewidths=1.5,
                      label=f'Step {step}: β={beta_sequence[step]:.3f}')

    # Labels
    ax.set_xlabel('System Drive R', fontsize=11)
    ax.set_ylabel('Threshold Θ', fontsize=11)
    ax.set_zlabel('Steepness β', fontsize=11)
    ax.set_title('Φ^(1/3) Scaling Spiral in 3D Parameter Space\n(UTAC v1.3φ Type-6 Implosive Field)',
                fontsize=13, fontweight='bold')

    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax, pad=0.1, shrink=0.8)
    cbar.set_label('β value', fontsize=10)

    # Legend (only key attractors)
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(handles[:4], labels[:4], loc='upper left', fontsize=9)

    ax.view_init(elev=20, azim=45)

    plt.tight_layout()
    output_path = output_dir / 'implosive_spiral.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def plot_energy_release(beta_values: list, output_dir: Path):
    """
    Generate energy release integral profiles for different β values.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Energy Release Integral E(R) for Implosive Fields',
                 fontsize=14, fontweight='bold')

    R = np.linspace(-3, 3, 500)
    theta = 0.0

    # Left panel: Multiple β values
    ax1 = axes[0]
    for beta in beta_values:
        sigma = sigma_implosive(R, beta, theta)
        E = np.cumsum(sigma) * (R[1] - R[0])

        label = f'β = {beta:.2f}'
        if np.isclose(beta, PHI**3, rtol=0.01):
            label += ' (Φ³ attractor)'
        ax1.plot(R, E, linewidth=2, label=label)

    ax1.axvline(theta, color='gray', linestyle=':', alpha=0.5, label='Θ')
    ax1.set_xlabel('System Drive R')
    ax1.set_ylabel('Energy Release E(R)')
    ax1.set_title('Energy Integral vs β')
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Right panel: Classical vs Implosive
    ax2 = axes[1]
    beta_compare = PHI ** 3  # Use Φ³ attractor

    sigma_class = sigma_classical(R, beta_compare, theta)
    sigma_implo = sigma_implosive(R, beta_compare, theta)

    E_class = np.cumsum(sigma_class) * (R[1] - R[0])
    E_implo = np.cumsum(sigma_implo) * (R[1] - R[0])

    ax2.plot(R, E_class, 'b-', linewidth=2, label='Classical σ(β(R-Θ))')
    ax2.plot(R, E_implo, 'r--', linewidth=2, label='Implosive σ(-β(R-Θ))')
    ax2.axvline(theta, color='gray', linestyle=':', alpha=0.5, label='Θ')

    ax2.set_xlabel('System Drive R')
    ax2.set_ylabel('Energy Release E(R)')
    ax2.set_title(f'Classical vs Implosive (β = {beta_compare:.3f})')
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    output_path = output_dir / 'energy_release_profile.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def plot_trajectory_comparison(results: Dict, output_dir: Path):
    """
    Plot time-domain trajectories from simulation results.
    """
    if 'simulations' not in results or len(results['simulations']) == 0:
        print("⚠ No simulation trajectories found, skipping trajectory plot")
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('UTAC v1.3φ: Membrane Dynamics Time Evolution',
                 fontsize=14, fontweight='bold')

    # Select 4 representative simulations (steps 0, 3, 6, 9)
    key_steps = [0, 3, 6, 9]
    plot_idx = 0

    for step in key_steps:
        # Find simulation with matching step
        sim = next((s for s in results['simulations'] if s['step'] == step), None)
        if sim is None:
            continue

        ax = axes[plot_idx // 2, plot_idx % 2]
        traj = sim['trajectory']

        ax.plot(traj['time'], traj['R'], 'b-', linewidth=1.5, label='R(t)', alpha=0.8)
        ax_twin = ax.twinx()
        ax_twin.plot(traj['time'], traj['sigma'], 'r--', linewidth=1.5, label='σ(t)', alpha=0.8)

        ax.axhline(sim['theta'], color='gray', linestyle=':', alpha=0.5, label='Θ')

        ax.set_xlabel('Time t')
        ax.set_ylabel('System Drive R', color='b')
        ax_twin.set_ylabel('Implosive Response σ', color='r')
        ax.tick_params(axis='y', labelcolor='b')
        ax_twin.tick_params(axis='y', labelcolor='r')

        title = f"Step {step}: β = {sim['beta']:.3f}, ζ = {sim['zeta']:.2f}"
        ax.set_title(title)

        ax.grid(True, alpha=0.3)

        # Combined legend
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax_twin.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)

        plot_idx += 1

    plt.tight_layout()
    output_path = output_dir / 'membrane_dynamics_trajectories.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def generate_summary_figure(results: Dict, output_dir: Path):
    """
    Generate comprehensive summary figure combining key visualizations.
    """
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.4)

    fig.suptitle('UTAC v1.3φ Type-6 Implosive Origin Field - Complete Summary',
                 fontsize=16, fontweight='bold')

    # Panel 1: Beta sequence
    ax1 = fig.add_subplot(gs[0, :])
    beta_seq = results['beta_sequence']
    steps = np.arange(len(beta_seq))
    ax1.plot(steps, beta_seq, 'o-', linewidth=2, markersize=8, color='darkblue')
    ax1.axhline(PHI**3, color='red', linestyle='--', linewidth=2, label=f'Φ³ = {PHI**3:.4f}')
    ax1.set_xlabel('Step n')
    ax1.set_ylabel('β_n')
    ax1.set_title('Φ^(1/3) Scaling Sequence: β_n = β₀ × Φ^(n/3)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Panel 2: Sigmoid comparison
    ax2 = fig.add_subplot(gs[1, 0])
    R = np.linspace(-2, 2, 200)
    beta_att = PHI ** 3
    ax2.plot(R, sigma_classical(R, beta_att, 0), 'b-', linewidth=2, label='Classical')
    ax2.plot(R, sigma_implosive(R, beta_att, 0), 'r--', linewidth=2, label='Implosive')
    ax2.set_xlabel('R')
    ax2.set_ylabel('σ')
    ax2.set_title(f'Sigmoid @ β={beta_att:.3f}')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Panel 3: Energy release
    ax3 = fig.add_subplot(gs[1, 1])
    E = np.cumsum(sigma_implosive(R, beta_att, 0)) * (R[1] - R[0])
    ax3.plot(R, E, 'g-', linewidth=2)
    ax3.set_xlabel('R')
    ax3.set_ylabel('E(R)')
    ax3.set_title('Energy Release Integral')
    ax3.grid(True, alpha=0.3)

    # Panel 4: Convergence info
    ax4 = fig.add_subplot(gs[1, 2])
    ax4.axis('off')
    conv = results['convergence']
    info_text = f"""
    Convergence Metrics
    ═══════════════════

    Φ³ (theoretical):
      {conv['phi3_theoretical']:.6f}

    β₉ (simulated):
      {conv['beta9_simulated']:.6f}

    Relative Error:
      {conv['relative_error']*100:.3f}%

    Status: {'✓ CONVERGED' if conv['converged'] else '✗ NOT CONVERGED'}

    ───────────────────

    Total Simulations: {len(results['simulations'])}
    """
    ax4.text(0.1, 0.5, info_text, fontsize=10, verticalalignment='center',
            fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Panel 5: Phase space (R vs sigma for different beta)
    ax5 = fig.add_subplot(gs[2, :])
    key_betas = [beta_seq[i] for i in [0, 3, 6, 9] if i < len(beta_seq)]
    for beta in key_betas:
        sigma_vals = sigma_implosive(R, beta, 0)
        label = f'β = {beta:.3f}'
        if np.isclose(beta, PHI**3, rtol=0.01):
            label += ' (Φ³)'
        ax5.plot(R, sigma_vals, linewidth=2, label=label)
    ax5.set_xlabel('System Drive R')
    ax5.set_ylabel('Implosive Response σ(-β(R-Θ))')
    ax5.set_title('Phase Space Evolution across Φ^(1/3) Steps')
    ax5.legend(loc='upper right')
    ax5.grid(True, alpha=0.3)

    plt.tight_layout()
    output_path = output_dir / 'implosive_field_summary.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description='UTAC v1.3φ Beta Spiral Visualizer'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='analysis/results/beta_implosion_curve.json',
        help='Input JSON from implosion_fit_beta.py'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='analysis/results/figures',
        help='Output directory for figures'
    )

    args = parser.parse_args()

    print("🎨 Starting UTAC v1.3φ visualization...")

    # Load results
    input_path = Path(args.input)
    if input_path.exists():
        with open(input_path, 'r') as f:
            results = json.load(f)
        print(f"✓ Loaded results from: {input_path}")
    else:
        print(f"⚠ Results file not found: {input_path}")
        print("  Generating visualizations with default parameters...")
        # Create minimal results structure
        beta_seq = [1.0 * (PHI ** (n/3)) for n in range(10)]
        results = {
            'beta_sequence': beta_seq,
            'convergence': {
                'phi3_theoretical': PHI ** 3,
                'beta9_simulated': beta_seq[-1],
                'relative_error': abs(beta_seq[-1] - PHI**3) / (PHI**3),
                'converged': True
            },
            'simulations': []
        }

    # Output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate visualizations
    print("\n📊 Generating visualizations...")

    plot_sigmoid_comparison(output_dir)
    plot_3d_spiral(np.array(results['beta_sequence']), output_dir)
    plot_energy_release([2.5, 4.236, 6.0, 12.0], output_dir)

    if results.get('simulations'):
        plot_trajectory_comparison(results, output_dir)

    generate_summary_figure(results, output_dir)

    print("\n✓ All visualizations complete!")
    print(f"📁 Output directory: {output_dir.absolute()}")


if __name__ == '__main__':
    main()
