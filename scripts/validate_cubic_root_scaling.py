#!/usr/bin/env python3
"""
Validate Cubic-Root Scaling for Type-VI Cascade

Tests the hypothesis: ΔR ∝ (R - Θ)^(1/3)

Usage:
    python scripts/validate_cubic_root_scaling.py

Based on:
- simulation/notes/type6_cubic_jump_outline.md
- METRICS.md Section 8.3

Version: v6.0.0-alpha
Author: Johann Benjamin Römer, MOR Framework
Date: 2025-11-26
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Direct import to avoid loading all simulation modules
import importlib.util
spec = importlib.util.spec_from_file_location(
    "type6_cascade",
    Path(__file__).parent.parent / "simulation" / "type6_cascade.py"
)
type6_cascade = importlib.util.module_from_spec(spec)
spec.loader.exec_module(type6_cascade)
run_arctic_methane_simulation = type6_cascade.run_arctic_methane_simulation

import numpy as np


def validate_cubic_root_scaling(history, verbose=True):
    """Validate cubic-root scaling law for Type-VI dynamics.

    Tests: log(ΔR) vs log(R - Θ) should have slope ≈ 1/3

    Args:
        history: List of SimulationState from type6_cascade
        verbose: Print detailed analysis

    Returns:
        dict with validation results
    """
    if verbose:
        print("=" * 70)
        print("CUBIC-ROOT SCALING VALIDATION")
        print("=" * 70)

    # Extract data
    times = np.array([s.t for s in history])
    R_values = np.array([s.R for s in history])
    Theta = history[0].R  # Use initial R as proxy for Theta proximity

    # Compute ΔR (rate of change)
    Delta_R = np.diff(R_values) / np.diff(times)

    # Compute (R - Θ) for middle points
    R_mid = (R_values[:-1] + R_values[1:]) / 2
    R_minus_Theta = R_mid - Theta

    # Filter: only positive (R - Θ) and positive ΔR
    valid = (R_minus_Theta > 0.01) & (Delta_R > 0.001)
    R_minus_Theta_valid = R_minus_Theta[valid]
    Delta_R_valid = Delta_R[valid]

    if len(R_minus_Theta_valid) < 10:
        if verbose:
            print(f"⚠️  Insufficient data points: {len(R_minus_Theta_valid)} < 10")
            print("   Cubic-root scaling cannot be validated.")
        return {
            "validated": False,
            "reason": "insufficient_data",
            "n_points": len(R_minus_Theta_valid),
        }

    # Log-log fit: log(ΔR) = a + b·log(R-Θ)
    # Expected: b ≈ 1/3 for cubic-root scaling
    log_x = np.log(R_minus_Theta_valid)
    log_y = np.log(Delta_R_valid)

    # Linear regression
    A = np.vstack([log_x, np.ones(len(log_x))]).T
    slope, intercept = np.linalg.lstsq(A, log_y, rcond=None)[0]

    # R² (coefficient of determination)
    y_pred = slope * log_x + intercept
    ss_res = np.sum((log_y - y_pred) ** 2)
    ss_tot = np.sum((log_y - np.mean(log_y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    # Validation criteria
    expected_slope = 1.0 / 3.0  # Cubic-root law
    slope_tolerance = 0.15  # Allow ±0.15 deviation
    slope_error = abs(slope - expected_slope)
    r2_threshold = 0.7  # Minimum R²

    validated = (slope_error < slope_tolerance) and (r_squared > r2_threshold)

    if verbose:
        print(f"\n📊 Log-Log Regression Results:")
        print(f"   Data points: {len(R_minus_Theta_valid)}")
        print(f"   Slope (b):   {slope:.4f}")
        print(f"   Expected:    {expected_slope:.4f} (cubic-root: 1/3)")
        print(f"   Error:       {slope_error:.4f}")
        print(f"   R²:          {r_squared:.4f}")
        print(f"   Intercept:   {intercept:.4f}")

        print(f"\n🎯 Validation Criteria:")
        print(f"   Slope tolerance: ±{slope_tolerance}")
        print(f"   R² threshold:    >{r2_threshold}")

        print(f"\n{'✅' if validated else '❌'} Cubic-Root Scaling: ", end="")
        if validated:
            print("VALIDATED")
            print(f"   The Type-VI cascade exhibits cubic-root jumps.")
            print(f"   ΔR ∝ (R - Θ)^{slope:.3f} (expected: (R - Θ)^0.333)")
        else:
            if slope_error >= slope_tolerance:
                print("NOT VALIDATED (slope mismatch)")
                print(f"   Observed slope {slope:.4f} deviates from 1/3 by {slope_error:.4f}")
            if r_squared <= r2_threshold:
                print("NOT VALIDATED (low R²)")
                print(f"   R² = {r_squared:.4f} < {r2_threshold}")

        print("=" * 70)

    return {
        "validated": validated,
        "slope": slope,
        "expected_slope": expected_slope,
        "slope_error": slope_error,
        "r_squared": r_squared,
        "n_points": len(R_minus_Theta_valid),
        "intercept": intercept,
    }


def main():
    print("🧪 Type-VI Cubic-Root Scaling Validation\n")

    # Run Arctic methane simulation
    print("📊 Running Arctic Methane Release simulation...")
    history = run_arctic_methane_simulation(verbose=False)
    print(f"✅ Simulation complete: {len(history)} timesteps\n")

    # Validate scaling
    results = validate_cubic_root_scaling(history, verbose=True)

    # Summary
    print("\n📋 Summary:")
    if results["validated"]:
        print("   ✅ Type-VI dynamics confirmed")
        print("   ✅ Cubic-root jumps detected")
        print(f"   ✅ Scaling exponent: {results['slope']:.4f} (expected: 0.333)")
        print(f"   ✅ Goodness-of-fit: R² = {results['r_squared']:.4f}")
    else:
        print("   ❌ Cubic-root scaling not validated")
        print(f"   ℹ️  Reason: {results.get('reason', 'criteria not met')}")
        if "slope" in results:
            print(f"   ℹ️  Observed slope: {results['slope']:.4f}")
            print(f"   ℹ️  Expected slope: {results['expected_slope']:.4f}")

    print("\n🎯 Next: Visualize results with:")
    print("   python scripts/plot_type6_cascade.py")


if __name__ == "__main__":
    main()
