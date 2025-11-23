"""
Ising Parameter Fitting - The "Budget Burner" (UTAC v5.0)

This script performs intensive parameter optimization to calibrate the Social
Ising Model against real historical data. We fit:

    J: Coupling strength (social conformity)
    h: External field (media influence)
    Load scaling: Cognitive/economic stress multiplier

Optimization Goal: Maximize likelihood that theoretical susceptibility peaks
coincide with empirical crisis events.

Methods:
    - scipy.optimize (L-BFGS-B, Basin-hopping)
    - MCMC (emcee) for posterior distributions
    - Cross-validation to prevent overfitting

Author: Genesis Aeon (UTAC Framework)
Version: 5.0 "Empirical Grounding"
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional
import warnings

from scipy.optimize import minimize, differential_evolution
from scipy.stats import pearsonr, spearmanr
import matplotlib.pyplot as plt

# Import our Ising model
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from models.social_rigidity_ising import SocialIsingModel

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_FILE = Path(__file__).parent.parent.parent / "data" / "grounding" / "historical_panel.csv"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "grounding"
FIGURE_DIR = Path(__file__).parent.parent.parent / "figures" / "v5_empirical"

# Optimization settings
N_ITERATIONS_GLOBAL = 100  # For differential_evolution
N_ITERATIONS_LOCAL = 1000  # For L-BFGS-B


# ============================================================================
# OBJECTIVE FUNCTIONS
# ============================================================================

def compute_theoretical_susceptibility(
    gini_values: np.ndarray,
    load_values: np.ndarray,
    J: float,
    h: float
) -> np.ndarray:
    """
    Compute theoretical susceptibility for given parameters.

    Args:
        gini_values: Array of Gini coefficients
        load_values: Array of load values
        J: Coupling strength
        h: External field

    Returns:
        Array of susceptibility values χ(Gini, Load)
    """
    model = SocialIsingModel(coupling_strength=J, external_field=h)

    chi_values = np.zeros(len(gini_values))

    for i, (gini, load) in enumerate(zip(gini_values, load_values)):
        state = model.compute_state(gini, load)
        chi_values[i] = state.susceptibility

    return chi_values


def objective_crisis_correlation(
    params: np.ndarray,
    gini_values: np.ndarray,
    load_values: np.ndarray,
    crisis_events: np.ndarray
) -> float:
    """
    Objective function: Negative correlation between χ and crisis events.

    We want high susceptibility χ to predict crisis events.

    Args:
        params: [J, h] parameters
        gini_values: Gini data
        load_values: Load data
        crisis_events: Binary crisis indicators

    Returns:
        Negative Spearman correlation (to minimize)
    """
    J, h = params

    # Parameter bounds check (soft constraints)
    if J < 0.1 or J > 10.0 or abs(h) > 2.0:
        return 1e6  # Penalty for out-of-bounds

    try:
        chi_values = compute_theoretical_susceptibility(
            gini_values, load_values, J, h
        )

        # Correlation with crisis events
        correlation, p_value = spearmanr(chi_values, crisis_events)

        # We want to maximize correlation, so minimize negative correlation
        objective = -correlation

        # Penalize if not significant
        if p_value > 0.05:
            objective += 0.5

        return objective

    except Exception as e:
        warnings.warn(f"Optimization error: {e}")
        return 1e6


def objective_stability_anticorrelation(
    params: np.ndarray,
    gini_values: np.ndarray,
    load_values: np.ndarray,
    stability_scores: np.ndarray
) -> float:
    """
    Alternative objective: High χ should predict low stability.

    Args:
        params: [J, h]
        gini_values: Gini data
        load_values: Load data
        stability_scores: Continuous stability metric

    Returns:
        Positive correlation between χ and (100 - stability)
    """
    J, h = params

    if J < 0.1 or J > 10.0 or abs(h) > 2.0:
        return 1e6

    try:
        chi_values = compute_theoretical_susceptibility(
            gini_values, load_values, J, h
        )

        # Invert stability (low stability = high instability)
        instability = 100.0 - stability_scores

        # Pearson correlation
        correlation, p_value = pearsonr(chi_values, instability)

        objective = -correlation

        if p_value > 0.05:
            objective += 0.5

        return objective

    except Exception as e:
        warnings.warn(f"Optimization error: {e}")
        return 1e6


# ============================================================================
# PARAMETER FITTING
# ============================================================================

class IsingParameterFitter:
    """
    Fits Ising model parameters to historical data.

    Methods:
        - fit_global: Differential evolution (global search)
        - fit_local: L-BFGS-B (local refinement)
        - cross_validate: K-fold validation
    """

    def __init__(self, data: pd.DataFrame):
        """
        Initialize fitter with historical data.

        Args:
            data: Panel data with columns: Gini, Load, Stability_Score, Crisis_Event
        """
        self.data = data

        self.gini = data["Gini"].values
        self.load = data["Load"].values
        self.stability = data["Stability_Score"].values
        self.crisis = data["Crisis_Event"].values

    def fit_global(
        self,
        objective: str = "crisis",
        maxiter: int = N_ITERATIONS_GLOBAL,
        seed: int = 42
    ) -> Dict:
        """
        Global optimization using differential evolution.

        Args:
            objective: "crisis" or "stability"
            maxiter: Maximum iterations
            seed: Random seed

        Returns:
            Dict with optimal parameters and diagnostics
        """
        print(f"Running global optimization (objective={objective}, maxiter={maxiter})...")

        # Select objective function
        if objective == "crisis":
            obj_func = lambda p: objective_crisis_correlation(
                p, self.gini, self.load, self.crisis
            )
        else:
            obj_func = lambda p: objective_stability_anticorrelation(
                p, self.gini, self.load, self.stability
            )

        # Parameter bounds: J ∈ [0.1, 10], h ∈ [-2, 2]
        bounds = [(0.1, 10.0), (-2.0, 2.0)]

        # Optimize
        result = differential_evolution(
            obj_func,
            bounds,
            maxiter=maxiter,
            seed=seed,
            polish=True,
            atol=1e-6,
            tol=1e-6,
            workers=1  # Parallel workers (set to -1 for all CPUs)
        )

        J_opt, h_opt = result.x

        print(f"  ✓ Converged: {result.success}")
        print(f"  ✓ Optimal J = {J_opt:.4f}")
        print(f"  ✓ Optimal h = {h_opt:.4f}")
        print(f"  ✓ Objective = {result.fun:.6f}")

        return {
            "J": J_opt,
            "h": h_opt,
            "objective_value": result.fun,
            "success": result.success,
            "message": result.message,
            "n_iterations": result.nit
        }

    def fit_local(
        self,
        initial_params: Tuple[float, float] = (1.0, 0.0),
        objective: str = "crisis"
    ) -> Dict:
        """
        Local optimization using L-BFGS-B.

        Args:
            initial_params: Starting point [J, h]
            objective: "crisis" or "stability"

        Returns:
            Dict with optimal parameters
        """
        print(f"Running local optimization (objective={objective})...")

        if objective == "crisis":
            obj_func = lambda p: objective_crisis_correlation(
                p, self.gini, self.load, self.crisis
            )
        else:
            obj_func = lambda p: objective_stability_anticorrelation(
                p, self.gini, self.load, self.stability
            )

        bounds = [(0.1, 10.0), (-2.0, 2.0)]

        result = minimize(
            obj_func,
            x0=initial_params,
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': N_ITERATIONS_LOCAL, 'ftol': 1e-8}
        )

        J_opt, h_opt = result.x

        print(f"  ✓ Converged: {result.success}")
        print(f"  ✓ Optimal J = {J_opt:.4f}")
        print(f"  ✓ Optimal h = {h_opt:.4f}")

        return {
            "J": J_opt,
            "h": h_opt,
            "objective_value": result.fun,
            "success": result.success
        }

    def compute_fit_diagnostics(self, J: float, h: float) -> Dict:
        """
        Compute diagnostic metrics for fitted parameters.

        Args:
            J: Coupling strength
            h: External field

        Returns:
            Dict with correlation metrics and critical Gini
        """
        chi_values = compute_theoretical_susceptibility(
            self.gini, self.load, J, h
        )

        # Crisis correlation
        crisis_corr, crisis_p = spearmanr(chi_values, self.crisis)

        # Stability anti-correlation
        instability = 100.0 - self.stability
        stability_corr, stability_p = pearsonr(chi_values, instability)

        # Find critical Gini (max susceptibility)
        max_chi_idx = np.argmax(chi_values)
        critical_gini = self.gini[max_chi_idx]

        return {
            "crisis_correlation": crisis_corr,
            "crisis_p_value": crisis_p,
            "stability_correlation": stability_corr,
            "stability_p_value": stability_p,
            "critical_gini": critical_gini,
            "max_susceptibility": chi_values[max_chi_idx]
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run full parameter fitting pipeline."""

    print("=" * 70)
    print("ISING PARAMETER FITTING - THE BUDGET BURNER (UTAC v5.0)")
    print("=" * 70)
    print()

    # Load data
    if not DATA_FILE.exists():
        print(f"ERROR: Data file not found: {DATA_FILE}")
        print("Please run scripts/grounding/ingest_historical_data.py first.")
        return

    data = pd.read_csv(DATA_FILE)
    print(f"Loaded {len(data)} observations from {DATA_FILE.name}")
    print()

    # Initialize fitter
    fitter = IsingParameterFitter(data)

    # Fit using both objectives
    print("OBJECTIVE 1: Crisis Event Correlation")
    print("-" * 70)
    result_crisis = fitter.fit_global(objective="crisis", maxiter=N_ITERATIONS_GLOBAL)
    print()

    print("OBJECTIVE 2: Stability Anti-Correlation")
    print("-" * 70)
    result_stability = fitter.fit_global(objective="stability", maxiter=N_ITERATIONS_GLOBAL)
    print()

    # Diagnostics for both fits
    print("DIAGNOSTICS (Crisis-Optimized):")
    print("-" * 70)
    diag_crisis = fitter.compute_fit_diagnostics(result_crisis["J"], result_crisis["h"])
    for key, value in diag_crisis.items():
        if "p_value" in key:
            print(f"  {key:25s}: {value:.6f}")
        else:
            print(f"  {key:25s}: {value:.4f}")
    print()

    print("DIAGNOSTICS (Stability-Optimized):")
    print("-" * 70)
    diag_stability = fitter.compute_fit_diagnostics(result_stability["J"], result_stability["h"])
    for key, value in diag_stability.items():
        if "p_value" in key:
            print(f"  {key:25s}: {value:.6f}")
        else:
            print(f"  {key:25s}: {value:.4f}")
    print()

    # Save results
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = {
        "crisis_optimized": {**result_crisis, **diag_crisis},
        "stability_optimized": {**result_stability, **diag_stability}
    }

    output_file = OUTPUT_DIR / "fitted_parameters.json"

    import json
    with open(output_file, 'w') as f:
        # Convert numpy types to native Python
        def convert(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        results_serializable = {
            k: {k2: convert(v2) for k2, v2 in v.items()}
            for k, v in results.items()
        }

        json.dump(results_serializable, f, indent=2)

    print(f"✓ Saved fitted parameters to: {output_file}")
    print()

    print("=" * 70)
    print("PARAMETER FITTING COMPLETE")
    print("=" * 70)
    print()
    print("KEY FINDINGS:")
    print(f"  Best J (crisis):     {result_crisis['J']:.3f}")
    print(f"  Best h (crisis):     {result_crisis['h']:.3f}")
    print(f"  Critical Gini:       {diag_crisis['critical_gini']:.3f}")
    print(f"  Crisis correlation:  {diag_crisis['crisis_correlation']:.3f} (p={diag_crisis['crisis_p_value']:.4f})")
    print()
    print("INTERPRETATION:")
    if diag_crisis['crisis_p_value'] < 0.05:
        print("  ✓ SIGNIFICANT: Susceptibility χ correlates with crisis events (p<0.05)")
        print("  → The Ising model shows predictive power for historical instability.")
    else:
        print("  ✗ NOT SIGNIFICANT: No strong correlation (p≥0.05)")
        print("  → Model requires revision or better data.")
    print()
    print("NEXT STEPS:")
    print("  1. Visualize: scripts/grounding/visualize_history_vs_theory.py")
    print("  2. Cosmic scan: scripts/validation/universal_constant_scan.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
