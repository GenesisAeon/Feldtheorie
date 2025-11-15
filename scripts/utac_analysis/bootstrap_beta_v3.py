#!/usr/bin/env python3
"""
Bootstrap Confidence Intervals for UTAC V3 β-Parameters

Computes robust 95% confidence intervals for all 6 V3 systems through
bootstrap resampling (n=1000 iterations).

Systems:
1. WAIS (West Antarctic Ice Sheet) - β ≈ 13.5
2. AMOC (Atlantic Circulation) - β ≈ 10.2
3. Coral Reefs - β ≈ 7.5
4. Measles (Canada) - β ≈ 5.8
5. Finance 2008 - β ≈ 4.9
6. Cancer-Immune - β ≈ 3.5

Output: beta_fits_v3_bootstrap.json with:
- Point estimates (β_mean)
- Bootstrap 95% CI (β_ci_lower, β_ci_upper)
- Standard errors (β_se)
- Coefficient of variation (CV)

Usage:
    python bootstrap_beta_v3.py --data-dir ../analysis/results \
                                 --output beta_fits_v3_bootstrap.json \
                                 --n-bootstrap 1000

Author: Claude Code (Anthropic)
Date: 2025-11-15
Version: 1.0.0
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

# Set random seed for reproducibility
np.random.seed(42)


# ═══════════════════════════════════════════════════════════════════
# UTAC Logistic Function
# ═══════════════════════════════════════════════════════════════════

def utac_logistic(R: np.ndarray, beta: float, Theta: float) -> np.ndarray:
    """UTAC activation function: σ(β(R-Θ))

    Args:
        R: Control parameter (state variable)
        beta: Steepness parameter
        Theta: Threshold value

    Returns:
        σ: Activation level (0-1)
    """
    return 1.0 / (1.0 + np.exp(-beta * (R - Theta)))


def fit_utac_beta(R: np.ndarray, sigma: np.ndarray,
                  Theta: float) -> Tuple[float, float]:
    """Fit β parameter given R, σ data and fixed Θ

    Args:
        R: Control parameter values
        sigma: Observed activation (0-1)
        Theta: Fixed threshold value

    Returns:
        beta_fit: Fitted β parameter
        beta_se: Standard error of β
    """
    try:
        # Define simplified fit function with Theta fixed
        def logistic_fit(R, beta):
            return utac_logistic(R, beta, Theta)

        # Fit using curve_fit
        popt, pcov = curve_fit(logistic_fit, R, sigma,
                               p0=[5.0],  # Initial guess for β
                               bounds=([0.5], [20.0]),  # β ∈ [0.5, 20]
                               maxfev=10000)

        beta_fit = popt[0]
        beta_se = np.sqrt(np.diag(pcov))[0]

        return beta_fit, beta_se

    except Exception as e:
        # If fit fails, return NaN
        return np.nan, np.nan


# ═══════════════════════════════════════════════════════════════════
# Bootstrap Resampling
# ═══════════════════════════════════════════════════════════════════

def bootstrap_beta_single_system(R: np.ndarray, sigma: np.ndarray,
                                   Theta: float,
                                   n_bootstrap: int = 1000) -> Dict:
    """Bootstrap confidence intervals for single system's β

    Args:
        R: Control parameter array
        sigma: Activation array
        Theta: Threshold value
        n_bootstrap: Number of bootstrap iterations

    Returns:
        dict with bootstrap statistics
    """
    n_samples = len(R)
    beta_bootstrap = []

    for i in range(n_bootstrap):
        # Resample with replacement
        indices = np.random.choice(n_samples, size=n_samples, replace=True)
        R_boot = R[indices]
        sigma_boot = sigma[indices]

        # Fit β on bootstrap sample
        beta_fit, _ = fit_utac_beta(R_boot, sigma_boot, Theta)

        if not np.isnan(beta_fit):
            beta_bootstrap.append(beta_fit)

    beta_bootstrap = np.array(beta_bootstrap)

    # Compute statistics
    beta_mean = np.mean(beta_bootstrap)
    beta_std = np.std(beta_bootstrap)
    beta_ci_lower = np.percentile(beta_bootstrap, 2.5)
    beta_ci_upper = np.percentile(beta_bootstrap, 97.5)

    # Coefficient of variation
    cv = beta_std / beta_mean if beta_mean != 0 else np.nan

    return {
        'beta_mean': float(beta_mean),
        'beta_std': float(beta_std),
        'beta_ci_lower': float(beta_ci_lower),
        'beta_ci_upper': float(beta_ci_upper),
        'beta_ci_width': float(beta_ci_upper - beta_ci_lower),
        'beta_ci_width_relative': float((beta_ci_upper - beta_ci_lower) / beta_mean) if beta_mean != 0 else np.nan,
        'coefficient_of_variation': float(cv),
        'n_bootstrap': n_bootstrap,
        'n_successful_fits': len(beta_bootstrap),
        'convergence_rate': len(beta_bootstrap) / n_bootstrap
    }


# ═══════════════════════════════════════════════════════════════════
# V3 System Definitions
# ═══════════════════════════════════════════════════════════════════

def get_v3_system_data() -> Dict[str, Dict]:
    """Get data for all 6 V3 systems

    Returns:
        dict mapping system_id to {R, sigma, Theta, beta_expected}

    NOTE: This uses MOCK data. Replace with real data adapters:
    - WAIS: GRACE/GRACE-FO
    - AMOC: RAPID-MOCHA
    - Coral: NOAA OISST
    - Measles: WHO/PAHO
    - Finance: Historical market data
    - Cancer: Clinical trial data
    """

    systems = {}

    # ───────────────────────────────────────────────────────────────
    # 1. WAIS (West Antarctic Ice Sheet)
    # ───────────────────────────────────────────────────────────────
    # R = Global temperature anomaly (°C above pre-industrial)
    # Theta = 1.5°C (ice sheet destabilization threshold)
    # Current: R ≈ 1.17°C

    systems['wais'] = {
        'name': 'West Antarctic Ice Sheet',
        'R': np.array([0.5, 0.7, 0.9, 1.0, 1.1, 1.17, 1.2, 1.3]),
        'sigma': np.array([0.02, 0.05, 0.15, 0.25, 0.45, 0.65, 0.75, 0.88]),
        'Theta': 1.5,
        'beta_expected': 13.5,
        'domain': 'Climate',
        'utac_type': 'Type-2 Thermodynamic'
    }

    # ───────────────────────────────────────────────────────────────
    # 2. AMOC (Atlantic Meridional Overturning Circulation)
    # ───────────────────────────────────────────────────────────────
    # R = Freshwater input (Sv, normalized)
    # Theta = 0.46 Sv (bifurcation threshold)
    # Current: R ≈ 0.38 Sv

    systems['amoc'] = {
        'name': 'Atlantic Meridional Overturning Circulation',
        'R': np.array([0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.38, 0.42]),
        'sigma': np.array([0.01, 0.02, 0.05, 0.10, 0.20, 0.35, 0.48, 0.70]),
        'Theta': 0.46,
        'beta_expected': 10.2,
        'domain': 'Climate',
        'utac_type': 'Type-2 Thermodynamic (Bistable)'
    }

    # ───────────────────────────────────────────────────────────────
    # 3. Coral Reefs
    # ───────────────────────────────────────────────────────────────
    # R = SST anomaly (°C above MMM)
    # Theta = 1.0°C (bleaching threshold)
    # Current: R ≈ 1.4°C (POST-TIPPING)

    systems['coral'] = {
        'name': 'Coral Reef Bleaching',
        'R': np.array([0.3, 0.5, 0.7, 0.9, 1.0, 1.2, 1.4, 1.6]),
        'sigma': np.array([0.01, 0.03, 0.08, 0.22, 0.50, 0.82, 0.95, 0.98]),
        'Theta': 1.0,
        'beta_expected': 7.5,
        'domain': 'Ecology',
        'utac_type': 'Type-2/3 Hybrid'
    }

    # ───────────────────────────────────────────────────────────────
    # 4. Measles (Canada Elimination Status)
    # ───────────────────────────────────────────────────────────────
    # R = Vaccination coverage (fraction, 0-1)
    # Theta = 0.95 (herd immunity threshold)
    # Current: R ≈ 0.90 (below threshold → outbreak)

    systems['measles'] = {
        'name': 'Measles Herd Immunity (Canada)',
        'R': np.array([0.70, 0.75, 0.80, 0.85, 0.90, 0.92, 0.94, 0.96]),
        'sigma': np.array([0.95, 0.88, 0.72, 0.50, 0.28, 0.18, 0.08, 0.02]),
        'Theta': 0.95,
        'beta_expected': 5.8,
        'domain': 'Health',
        'utac_type': 'Type-4 Informational'
    }

    # ───────────────────────────────────────────────────────────────
    # 5. Financial Contagion 2008
    # ───────────────────────────────────────────────────────────────
    # R = Interbank network connectivity (0-1)
    # Theta = 0.42 (cascade threshold)
    # Current: R ≈ 0.55 (POST-EVENT, studied retrospectively)

    systems['finance'] = {
        'name': 'Financial Contagion 2008',
        'R': np.array([0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55]),
        'sigma': np.array([0.02, 0.05, 0.10, 0.22, 0.48, 0.75, 0.90, 0.96]),
        'Theta': 0.42,
        'beta_expected': 4.9,
        'domain': 'Economics',
        'utac_type': 'Type-4 Network'
    }

    # ───────────────────────────────────────────────────────────────
    # 6. Cancer-Immune Threshold
    # ───────────────────────────────────────────────────────────────
    # R = Immune cell count (normalized, 0-1)
    # Theta = 0.35 (tumor control threshold)
    # Current: Variable (individual-level)

    systems['cancer'] = {
        'name': 'Cancer-Immune Threshold',
        'R': np.array([0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45]),
        'sigma': np.array([0.95, 0.88, 0.75, 0.58, 0.42, 0.25, 0.12, 0.05]),
        'Theta': 0.35,
        'beta_expected': 3.5,
        'domain': 'Biology',
        'utac_type': 'Type-3 Electrochemical'
    }

    return systems


# ═══════════════════════════════════════════════════════════════════
# Main Bootstrap Pipeline
# ═══════════════════════════════════════════════════════════════════

def run_bootstrap_v3(n_bootstrap: int = 1000,
                     output_file: Path = None) -> Dict:
    """Run bootstrap analysis for all 6 V3 systems

    Args:
        n_bootstrap: Number of bootstrap iterations
        output_file: Path to save JSON output

    Returns:
        dict with bootstrap results for all systems
    """

    print(f"╔══════════════════════════════════════════════════════════╗")
    print(f"║  UTAC V3 Bootstrap Confidence Intervals (n={n_bootstrap})  ║")
    print(f"╚══════════════════════════════════════════════════════════╝\n")

    systems = get_v3_system_data()
    results = {}

    for system_id, system_data in systems.items():
        print(f"Bootstrap: {system_data['name']} ({system_id})...")
        print(f"  Expected β: {system_data['beta_expected']}")
        print(f"  UTAC Type: {system_data['utac_type']}")
        print(f"  Domain: {system_data['domain']}")

        # Run bootstrap
        bootstrap_stats = bootstrap_beta_single_system(
            R=system_data['R'],
            sigma=system_data['sigma'],
            Theta=system_data['Theta'],
            n_bootstrap=n_bootstrap
        )

        # Add metadata
        bootstrap_stats['system_id'] = system_id
        bootstrap_stats['system_name'] = system_data['name']
        bootstrap_stats['beta_expected'] = system_data['beta_expected']
        bootstrap_stats['Theta'] = system_data['Theta']
        bootstrap_stats['domain'] = system_data['domain']
        bootstrap_stats['utac_type'] = system_data['utac_type']

        # Calculate how close fitted β is to expected β
        beta_diff = abs(bootstrap_stats['beta_mean'] - system_data['beta_expected'])
        beta_diff_pct = 100 * beta_diff / system_data['beta_expected']

        bootstrap_stats['beta_diff_from_expected'] = float(beta_diff)
        bootstrap_stats['beta_diff_pct'] = float(beta_diff_pct)

        # Check if expected β is within 95% CI
        in_ci = (system_data['beta_expected'] >= bootstrap_stats['beta_ci_lower'] and
                 system_data['beta_expected'] <= bootstrap_stats['beta_ci_upper'])
        bootstrap_stats['expected_within_ci'] = in_ci

        results[system_id] = bootstrap_stats

        # Print results
        print(f"  ✓ β_mean: {bootstrap_stats['beta_mean']:.2f}")
        print(f"  ✓ β_95%CI: [{bootstrap_stats['beta_ci_lower']:.2f}, {bootstrap_stats['beta_ci_upper']:.2f}]")
        print(f"  ✓ CI width: {bootstrap_stats['beta_ci_width']:.2f} ({bootstrap_stats['beta_ci_width_relative']*100:.1f}% relative)")
        print(f"  ✓ Convergence: {bootstrap_stats['convergence_rate']*100:.1f}%")
        print(f"  ✓ Diff from expected: {beta_diff:.2f} ({beta_diff_pct:.1f}%)")
        print(f"  ✓ Expected in CI: {'YES ✅' if in_ci else 'NO ❌'}")
        print()

    # Global summary
    all_betas = [r['beta_mean'] for r in results.values()]
    all_cis_lower = [r['beta_ci_lower'] for r in results.values()]
    all_cis_upper = [r['beta_ci_upper'] for r in results.values()]

    global_summary = {
        'n_systems': len(results),
        'n_bootstrap': n_bootstrap,
        'beta_range': [min(all_betas), max(all_betas)],
        'beta_mean_across_systems': float(np.mean(all_betas)),
        'beta_std_across_systems': float(np.std(all_betas)),
        'all_expected_within_ci': all([r['expected_within_ci'] for r in results.values()]),
        'convergence_rate_min': min([r['convergence_rate'] for r in results.values()]),
        'convergence_rate_mean': float(np.mean([r['convergence_rate'] for r in results.values()]))
    }

    print(f"╔══════════════════════════════════════════════════════════╗")
    print(f"║  GLOBAL SUMMARY                                          ║")
    print(f"╚══════════════════════════════════════════════════════════╝")
    print(f"  Systems analyzed: {global_summary['n_systems']}")
    print(f"  β-range: {global_summary['beta_range'][0]:.2f} → {global_summary['beta_range'][1]:.2f}")
    print(f"  Mean β across systems: {global_summary['beta_mean_across_systems']:.2f} ± {global_summary['beta_std_across_systems']:.2f}")
    print(f"  All expected β within CIs: {'YES ✅' if global_summary['all_expected_within_ci'] else 'NO ❌'}")
    print(f"  Bootstrap convergence: {global_summary['convergence_rate_mean']*100:.1f}%")
    print()

    # Compile final output
    output = {
        'meta': {
            'version': '1.0.0',
            'date': '2025-11-15',
            'n_bootstrap': n_bootstrap,
            'method': 'Bootstrap resampling with UTAC logistic fit',
            'author': 'Claude Code (Anthropic)',
            'note': 'MOCK DATA - Replace with real GRACE, RAPID, OISST, WHO, etc.'
        },
        'global_summary': global_summary,
        'systems': results
    }

    # Save to file if specified
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"✓ Results saved to: {output_file}")

    return output


# ═══════════════════════════════════════════════════════════════════
# CLI Interface
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Bootstrap confidence intervals for UTAC V3 β-parameters',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (n=1000)
  python bootstrap_beta_v3.py

  # Custom output file and iterations
  python bootstrap_beta_v3.py --output results/bootstrap.json --n-bootstrap 5000

  # Quick test run (n=100)
  python bootstrap_beta_v3.py --n-bootstrap 100 --output test.json
        """
    )

    parser.add_argument('--output', '-o',
                        type=Path,
                        default=Path('beta_fits_v3_bootstrap.json'),
                        help='Output JSON file path (default: beta_fits_v3_bootstrap.json)')

    parser.add_argument('--n-bootstrap', '-n',
                        type=int,
                        default=1000,
                        help='Number of bootstrap iterations (default: 1000)')

    parser.add_argument('--verbose', '-v',
                        action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    # Run bootstrap
    try:
        results = run_bootstrap_v3(
            n_bootstrap=args.n_bootstrap,
            output_file=args.output
        )

        print("\n✅ Bootstrap analysis complete!")
        print(f"📊 Results: {args.output}")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
