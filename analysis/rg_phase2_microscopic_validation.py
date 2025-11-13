"""RG Phase 2 - Microscopic ABM Validation

Validates emergent β against empirical β-values across multiple systems.

Tests hypothesis: β_emergent ≈ β_empirical (within ±15%)

Workflow:
1. For each system type (LLM, Climate, Urban Heat, etc.):
   - Set microscopic params (J, T) based on theory (β ≈ J/T)
   - Run ABM simulation
   - Extract emergent β via coarse-graining
   - Compare to empirical β

2. Validation criteria:
   - R² ≥ 0.85 (good logistic fit)
   - |β_emergent - β_empirical| / β_empirical ≤ 0.15 (±15% deviation)
   - At least 5/6 systems pass validation

Version: 1.0.0
Date: 2025-11-13
"""

import json
from pathlib import Path
from typing import Dict, List

import numpy as np

from models.utac_microscopic_abm import (
    ABMParams,
    EmergentBetaSimulator,
    microscopic_to_beta_map,
)


def validate_system(
    system_name: str,
    beta_empirical: float,
    J: float,
    T: float,
    lattice_size: int = 64,
    verbose: bool = True,
) -> Dict:
    """Validate emergent β for single system.

    Parameters
    ----------
    system_name : str
        System name (e.g., "llm_training")
    beta_empirical : float
        Empirical β from data
    J : float
        Microscopic coupling
    T : float
        Microscopic temperature
    lattice_size : int
        Lattice size (default: 64)
    verbose : bool
        Print progress (default: True)

    Returns
    -------
    dict
        Validation results
    """
    if verbose:
        print(f"\n🔬 {system_name}")
        print(f"   Empirical β: {beta_empirical:.2f}")
        print(f"   Microscopic: J={J:.2f}, T={T:.2f}")
        print(f"   Theory: β ≈ J/T = {J / T:.2f}")

    # Run ABM
    params = ABMParams(J=J, h=0.0, T=T, lattice_size=lattice_size)
    simulator = EmergentBetaSimulator(params)
    results = simulator.compute_emergent_beta(n_points=25)

    beta_emergent = results["beta_emergent"]
    r_squared = results["r_squared"]

    # Validation
    deviation_pct = abs(beta_emergent - beta_empirical) / beta_empirical * 100
    passed = (r_squared >= 0.85) and (deviation_pct <= 15.0)

    if verbose:
        print(f"   ✅ Emergent β: {beta_emergent:.2f} (R²={r_squared:.3f})")
        print(f"   Deviation: {deviation_pct:.1f}% {'✅ PASS' if passed else '❌ FAIL'}")

    return {
        "system": system_name,
        "beta_empirical": float(beta_empirical),
        "beta_emergent": float(beta_emergent),
        "beta_theory": float(J / T),
        "J": float(J),
        "T": float(T),
        "r_squared": float(r_squared),
        "deviation_pct": float(deviation_pct),
        "passed": passed,
    }


def run_full_validation() -> Dict:
    """Run validation across all system types.

    Returns
    -------
    dict
        Full validation results
    """
    print("🌀 RG Phase 2 - Microscopic ABM Validation")
    print("=" * 60)

    # System catalog (empirical β + microscopic params)
    systems = {
        "llm_training": {"beta": 4.2, "J": 0.80, "T": 0.19},
        "climate_amoc": {"beta": 4.0, "J": 0.60, "T": 0.15},
        "honeybees": {"beta": 4.1, "J": 0.70, "T": 0.17},
        "urban_heat_moderate": {"beta": 11.0, "J": 0.88, "T": 0.08},
        "quantum_vacuum": {"beta": 1.4, "J": 0.15, "T": 0.11},
        "systemic_debt": {"beta": 18.5, "J": 0.98, "T": 0.053},
    }

    results = []
    for name, config in systems.items():
        result = validate_system(
            system_name=name,
            beta_empirical=config["beta"],
            J=config["J"],
            T=config["T"],
            lattice_size=64,  # Smaller lattice for speed
        )
        results.append(result)

    # Summary
    n_total = len(results)
    n_passed = sum(1 for r in results if r["passed"])
    pass_rate = n_passed / n_total * 100

    print(f"\n{'=' * 60}")
    print(f"📊 Validation Summary")
    print(f"   Systems tested: {n_total}")
    print(f"   Passed: {n_passed}/{n_total} ({pass_rate:.0f}%)")
    print(f"   Criteria: R² ≥ 0.85, Deviation ≤ 15%")

    if pass_rate >= 80:
        print(f"\n✅ VALIDATION PASSED! ({pass_rate:.0f}% ≥ 80%)")
    else:
        print(f"\n⚠️  VALIDATION PARTIAL ({pass_rate:.0f}% < 80%)")

    return {
        "systems": results,
        "summary": {
            "n_total": n_total,
            "n_passed": n_passed,
            "pass_rate": pass_rate,
            "passed": pass_rate >= 80,
        },
    }


if __name__ == "__main__":
    results = run_full_validation()

    # Save results
    output_path = Path("analysis/results/rg_phase2_microscopic_validation.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved: {output_path}")
