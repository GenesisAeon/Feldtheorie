#!/usr/bin/env python3
"""LLM β-Spiral: Φ^(1/3) Ladder Test (Experiment B)

Tests whether β values from LLM training trajectories follow the discrete
Φ^(1/3) step ladder predicted by Type-6 implosive theory:

    β_n ≈ β₀ · Φ^(n/3)  where Φ^(1/3) ≈ 1.174

Falsification criteria:
1. Median adjacent ratio outside 1.174 ± 0.05
2. Fixpoint not near β ≈ 4.236 (Φ³)
3. Alternative multiplier fits better

Usage:
    python llm_phi_ladder_test.py --input data/implosion/llm_beta_sequence.csv \\
                                   --out paper/figures/phi_ladder_llm.png

References:
- Theory: docs/utac_type6_implosive_origin_theory.md
- Falsification Plan: docs/utac_type6_falsification_plan.md (Experiment B)

Author: Johann B. Römer et al.
Date: 2025-11-12
License: AGPL-3.0
"""

import argparse
import sys
from pathlib import Path

import numpy as np
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
)

# Optional plotting
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available, plots will be skipped")


def test_ladder_hypothesis(beta_sequence: np.ndarray, verbose: bool = True) -> dict:
    """Test whether β sequence follows Φ^(1/3) ladder.

    Parameters
    ----------
    beta_sequence : ndarray
        Observed β values from LLM training or capability emergence
    verbose : bool
        Print detailed results

    Returns
    -------
    results : dict
        - median_ratio: Median adjacent step multiplier
        - ratio_std: Standard deviation of ratios
        - theoretical: Φ^(1/3) ≈ 1.174
        - deviation: |median - theoretical| / theoretical
        - falsified: True if median outside 1.174 ± 0.05
        - consistency_score: Fraction of ratios within tolerance
    """
    if len(beta_sequence) < 2:
        return {
            'median_ratio': np.nan,
            'ratio_std': np.nan,
            'theoretical': PHI_CBRT,
            'deviation': np.nan,
            'falsified': None,
            'consistency_score': np.nan,
            'message': 'Insufficient data (need ≥2 values)',
        }

    # Compute adjacent ratios
    ratios = beta_step_ratios(beta_sequence)

    if len(ratios) == 0:
        return {
            'median_ratio': np.nan,
            'ratio_std': np.nan,
            'theoretical': PHI_CBRT,
            'deviation': np.nan,
            'falsified': None,
            'consistency_score': np.nan,
            'message': 'Cannot compute ratios',
        }

    median_ratio = np.median(ratios)
    ratio_std = np.std(ratios)
    deviation = abs(median_ratio - PHI_CBRT) / PHI_CBRT

    # Falsification test: median outside 1.174 ± 0.05 (±4.3%)
    tolerance = 0.05
    lower_bound = PHI_CBRT - tolerance
    upper_bound = PHI_CBRT + tolerance
    falsified = not (lower_bound <= median_ratio <= upper_bound)

    # Consistency: fraction of individual ratios within tolerance
    consistent = np.sum((ratios >= lower_bound) & (ratios <= upper_bound))
    consistency_score = consistent / len(ratios)

    if verbose:
        print(f"  Observed median ratio: {median_ratio:.4f}")
        print(f"  Theoretical Φ^(1/3): {PHI_CBRT:.4f}")
        print(f"  Deviation: {deviation:.2%}")
        print(f"  Ratio std: {ratio_std:.4f}")
        print(f"  Consistency: {consistency_score:.1%} within tolerance")
        print()

    return {
        'median_ratio': median_ratio,
        'ratio_std': ratio_std,
        'theoretical': PHI_CBRT,
        'deviation': deviation,
        'falsified': falsified,
        'consistency_score': consistency_score,
        'message': 'FALSIFIED' if falsified else 'VALIDATED',
        'ratios': ratios,
    }


def test_fixpoint_convergence(beta_sequence: np.ndarray, verbose: bool = True) -> dict:
    """Test whether β values converge near Φ³ ≈ 4.236.

    Parameters
    ----------
    beta_sequence : ndarray
        Observed β values
    verbose : bool
        Print detailed results

    Returns
    -------
    results : dict
        - mean_beta: Mean of sequence
        - std_beta: Standard deviation
        - fixpoint: Theoretical Φ³ ≈ 4.236
        - deviation: |mean - fixpoint| / fixpoint
        - falsified: True if mean < 3.3 or > 5.0 (outside ±20% window)
        - in_tolerance_fraction: Fraction within Φ³ ± 0.8
    """
    if len(beta_sequence) == 0:
        return {
            'mean_beta': np.nan,
            'std_beta': np.nan,
            'fixpoint': BETA_FIXPOINT_PHI3,
            'deviation': np.nan,
            'falsified': None,
            'in_tolerance_fraction': np.nan,
            'message': 'No data',
        }

    mean_beta = np.mean(beta_sequence)
    std_beta = np.std(beta_sequence)
    deviation = abs(mean_beta - BETA_FIXPOINT_PHI3) / BETA_FIXPOINT_PHI3

    # Falsification: mean outside [3.3, 5.0] (from plan: <3.3 or >5.0)
    lower_limit = 3.3
    upper_limit = 5.0
    falsified = (mean_beta < lower_limit) or (mean_beta > upper_limit)

    # Tolerance check: Φ³ ± 0.8
    tolerance = 0.8
    in_tolerance = np.sum(np.abs(beta_sequence - BETA_FIXPOINT_PHI3) <= tolerance)
    in_tolerance_fraction = in_tolerance / len(beta_sequence)

    if verbose:
        print(f"  Mean β: {mean_beta:.3f}")
        print(f"  Std β: {std_beta:.3f}")
        print(f"  Theoretical Φ³ fixpoint: {BETA_FIXPOINT_PHI3:.3f}")
        print(f"  Deviation: {deviation:.2%}")
        print(f"  In tolerance (Φ³ ± 0.8): {in_tolerance_fraction:.1%}")
        print()

    return {
        'mean_beta': mean_beta,
        'std_beta': std_beta,
        'fixpoint': BETA_FIXPOINT_PHI3,
        'deviation': deviation,
        'falsified': falsified,
        'in_tolerance_fraction': in_tolerance_fraction,
        'message': 'FALSIFIED' if falsified else 'VALIDATED',
    }


def test_alternative_multipliers(beta_sequence: np.ndarray, verbose: bool = True) -> dict:
    """Test if alternative fixed multipliers fit better than Φ^(1/3).

    Parameters
    ----------
    beta_sequence : ndarray
        Observed β values
    verbose : bool
        Print detailed results

    Returns
    -------
    results : dict
        - best_multiplier: Best-fit alternative
        - phi_cbrt_sse: Sum of squared errors for Φ^(1/3)
        - best_sse: SSE for best alternative
        - improvement: Fractional improvement over Φ^(1/3)
        - falsified: True if alternative improves by >20%
    """
    if len(beta_sequence) < 2:
        return {
            'best_multiplier': np.nan,
            'phi_cbrt_sse': np.nan,
            'best_sse': np.nan,
            'improvement': np.nan,
            'falsified': None,
            'message': 'Insufficient data',
        }

    ratios = beta_step_ratios(beta_sequence)

    # SSE for Φ^(1/3) hypothesis
    phi_cbrt_sse = np.sum((ratios - PHI_CBRT) ** 2)

    # Test alternative multipliers
    candidates = np.linspace(1.05, 1.40, 100)
    sses = [np.sum((ratios - m) ** 2) for m in candidates]
    best_idx = np.argmin(sses)
    best_multiplier = candidates[best_idx]
    best_sse = sses[best_idx]

    improvement = (phi_cbrt_sse - best_sse) / phi_cbrt_sse if phi_cbrt_sse > 0 else 0.0

    # Falsify if alternative improves by >20%
    falsified = improvement > 0.20

    if verbose:
        print(f"  Φ^(1/3) SSE: {phi_cbrt_sse:.6f}")
        print(f"  Best alternative: {best_multiplier:.4f} (SSE: {best_sse:.6f})")
        print(f"  Improvement: {improvement:.2%}")
        print()

    return {
        'best_multiplier': best_multiplier,
        'phi_cbrt_sse': phi_cbrt_sse,
        'best_sse': best_sse,
        'improvement': improvement,
        'falsified': falsified,
        'message': 'FALSIFIED' if falsified else 'VALIDATED',
    }


def create_validation_plot(beta_sequence: np.ndarray, ladder_result: dict, output_path: str):
    """Generate validation figure."""
    if not HAS_MATPLOTLIB:
        print("Skipping plots (matplotlib not available)")
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel A: β sequence with theoretical ladder
    ax = axes[0, 0]
    sorted_beta = np.sort(beta_sequence)
    ax.plot(range(len(sorted_beta)), sorted_beta, 'o-', markersize=10, linewidth=2,
            color='steelblue', label='Observed β')

    # Overlay theoretical Φ^(n/3) steps
    ax.plot(range(len(BETA_STEPS[:len(sorted_beta)])), BETA_STEPS[:len(sorted_beta)],
            's--', markersize=8, linewidth=1.5, color='orange', alpha=0.7,
            label=f'Theoretical Φ^(n/3) ladder')

    ax.axhline(BETA_FIXPOINT_PHI3, color='red', linestyle=':', linewidth=2,
               label=f'Φ³ fixpoint ({BETA_FIXPOINT_PHI3:.2f})')
    ax.set_xlabel('Step Index', fontsize=11)
    ax.set_ylabel('β (Steepness)', fontsize=11)
    ax.set_title('A: β Sequence vs. Theoretical Ladder', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel B: Adjacent ratios histogram
    ax = axes[0, 1]
    ratios = ladder_result.get('ratios', [])
    if len(ratios) > 0:
        ax.hist(ratios, bins=15, color='steelblue', alpha=0.7, edgecolor='black')
        ax.axvline(PHI_CBRT, color='red', linestyle='--', linewidth=2,
                   label=f'Φ^(1/3) = {PHI_CBRT:.3f}')
        ax.axvline(PHI_CBRT - 0.05, color='orange', linestyle=':', linewidth=1.5, alpha=0.7,
                   label='Tolerance ±0.05')
        ax.axvline(PHI_CBRT + 0.05, color='orange', linestyle=':', linewidth=1.5, alpha=0.7)
        ax.set_xlabel('Adjacent β Ratio', fontsize=11)
        ax.set_ylabel('Count', fontsize=11)
        ax.set_title('B: Distribution of β_{n+1}/β_n', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')

    # Panel C: Step mapping to theoretical ladder
    ax = axes[1, 0]
    for i, beta in enumerate(sorted_beta):
        step, beta_th, dev = nearest_beta_step(beta)
        ax.scatter(step, beta, s=100, c='steelblue', alpha=0.7, zorder=3)
        ax.plot([step, step], [beta_th, beta], 'k--', alpha=0.3, linewidth=1)

    ax.plot(range(len(BETA_STEPS)), BETA_STEPS, 'o-', color='orange', markersize=8,
            linewidth=2, alpha=0.7, label='Theoretical ladder', zorder=2)
    ax.set_xlabel('Ladder Step n', fontsize=11)
    ax.set_ylabel('β Value', fontsize=11)
    ax.set_title('C: Observed β Mapped to Ladder Steps', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel D: Cumulative convergence to fixpoint
    ax = axes[1, 1]
    cumulative_mean = np.cumsum(sorted_beta) / np.arange(1, len(sorted_beta) + 1)
    ax.plot(range(1, len(sorted_beta) + 1), cumulative_mean, 'o-', markersize=8,
            linewidth=2, color='steelblue', label='Cumulative mean')
    ax.axhline(BETA_FIXPOINT_PHI3, color='red', linestyle='--', linewidth=2,
               label=f'Φ³ fixpoint ({BETA_FIXPOINT_PHI3:.2f})')
    ax.fill_between(range(1, len(sorted_beta) + 1),
                     BETA_FIXPOINT_PHI3 - 0.8, BETA_FIXPOINT_PHI3 + 0.8,
                     alpha=0.2, color='red', label='Tolerance ±0.8')
    ax.set_xlabel('Number of Observations', fontsize=11)
    ax.set_ylabel('Cumulative Mean β', fontsize=11)
    ax.set_title('D: Convergence to Φ³ Fixpoint', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved validation plot: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='LLM β-Spiral: Φ^(1/3) Ladder Test (UTAC Type-6 Experiment B)'
    )
    parser.add_argument('--demo', action='store_true',
                        help='Run with synthetic demo data')
    parser.add_argument('--out', default='paper/figures/phi_ladder_llm.png',
                        help='Output path for validation figure')

    args = parser.parse_args()

    print("═" * 70)
    print("UTAC Type-6 Validation: LLM β-Spiral Φ^(1/3) Ladder Test")
    print("Experiment B from Falsification Plan")
    print("═" * 70)
    print()

    if args.demo:
        print("Running with SYNTHETIC DEMO DATA")
        print("─" * 70)
        # Generate synthetic β sequence following Φ^(1/3) ladder with realistic noise
        np.random.seed(42)
        n_steps = 9
        beta_base = 1.0
        noise_level = 0.08  # 8% noise

        beta_sequence = np.array([
            beta_base * (PHI ** (n / 3.0)) * np.random.normal(1.0, noise_level)
            for n in range(n_steps)
        ])

        print(f"  → {len(beta_sequence)} synthetic β values generated")
        print(f"  → β range: [{beta_sequence.min():.2f}, {beta_sequence.max():.2f}]")
        print()
    else:
        print("ERROR: No input file support yet. Use --demo for demonstration.")
        return

    # TEST 1: Ladder hypothesis
    print("─" * 70)
    print("TEST 1: Φ^(1/3) Ladder Multiplier")
    print("─" * 70)
    ladder_result = test_ladder_hypothesis(beta_sequence, verbose=True)

    if ladder_result['falsified'] == False:
        print(f"  ✓ VALIDATED: Median ratio {ladder_result['median_ratio']:.4f} "
              f"within Φ^(1/3) ± 0.05")
    elif ladder_result['falsified'] == True:
        print(f"  ⚠️  FALSIFIED: Median ratio {ladder_result['median_ratio']:.4f} "
              f"outside tolerance")
    else:
        print(f"  ○ INCONCLUSIVE: {ladder_result['message']}")

    print()

    # TEST 2: Fixpoint convergence
    print("─" * 70)
    print("TEST 2: Φ³ Fixpoint Convergence")
    print("─" * 70)
    fixpoint_result = test_fixpoint_convergence(beta_sequence, verbose=True)

    if fixpoint_result['falsified'] == False:
        print(f"  ✓ VALIDATED: Mean β = {fixpoint_result['mean_beta']:.3f} "
              f"near Φ³ = {BETA_FIXPOINT_PHI3:.3f}")
    elif fixpoint_result['falsified'] == True:
        print(f"  ⚠️  FALSIFIED: Mean β = {fixpoint_result['mean_beta']:.3f} "
              f"outside [3.3, 5.0]")
    else:
        print(f"  ○ INCONCLUSIVE: {fixpoint_result['message']}")

    print()

    # TEST 3: Alternative multipliers
    print("─" * 70)
    print("TEST 3: Alternative Fixed Multipliers")
    print("─" * 70)
    alt_result = test_alternative_multipliers(beta_sequence, verbose=True)

    if alt_result['falsified'] == False:
        print(f"  ✓ VALIDATED: Φ^(1/3) preferred (improvement < 20%)")
    elif alt_result['falsified'] == True:
        print(f"  ⚠️  FALSIFIED: Alternative {alt_result['best_multiplier']:.4f} "
              f"improves by {alt_result['improvement']:.1%}")
    else:
        print(f"  ○ INCONCLUSIVE: {alt_result['message']}")

    print()

    # Summary
    print("═" * 70)
    print("SUMMARY")
    print("═" * 70)

    tests = [ladder_result, fixpoint_result, alt_result]
    validated_count = sum(1 for t in tests if t.get('falsified') == False)
    falsified_count = sum(1 for t in tests if t.get('falsified') == True)

    print(f"  Tests run: 3")
    print(f"  Validated: {validated_count}")
    print(f"  Falsified: {falsified_count}")
    print(f"  Inconclusive: {3 - validated_count - falsified_count}")
    print()

    if falsified_count >= 2:
        print("  ⚠️  Φ^(1/3) LADDER MATERIALLY FALSIFIED (≥2 tests failed)")
    elif falsified_count == 1:
        print("  ⚠️  REVISION NEEDED (1 test failed; refinement suggested)")
    elif validated_count >= 2:
        print("  ✓ Φ^(1/3) LADDER PROVISIONALLY VALIDATED")
    else:
        print("  ○ INCONCLUSIVE (insufficient evidence)")

    print()

    # Generate plots
    if HAS_MATPLOTLIB:
        print("─" * 70)
        print("Generating validation plots...")
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        create_validation_plot(beta_sequence, ladder_result, args.out)

    print("═" * 70)
    print("Analysis complete.")
    print("═" * 70)


if __name__ == '__main__':
    main()
