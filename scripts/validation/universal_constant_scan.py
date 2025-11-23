"""
Universal Constant Scan: Look-Elsewhere Effect Analysis (UTAC v5.0)

This script tests whether the α-Φ formula is statistically unique or whether
we could have found a similar match with arbitrary constant combinations.

We systematically scan:
    1. Fundamental dimensionless constants (α, proton/electron mass ratio, etc.)
    2. Mathematical constants (Φ, π, e, ζ(3), etc.)
    3. Combinations (product, quotient, powers)

Target: Böhme velocity v_obs = 1370 ± 10 km/s

Statistical Question: What fraction of random constant pairs produce
comparable or better fits than α and Φ?

This quantifies the "Look-Elsewhere Effect" - the penalty for searching
many hypotheses.

Author: Genesis Aeon (UTAC Framework)
Version: 5.0 "Rigorous Falsification"
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from scipy import constants
from itertools import combinations, product
import warnings

# ============================================================================
# CONFIGURATION
# ============================================================================

OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "derived"
OUTPUT_FILE = OUTPUT_DIR / "cosmic_alternatives.csv"

# Target observable
BOEHME_VELOCITY = 1370.0  # km/s
BOEHME_UNCERTAINTY = 10.0  # km/s

# Speed of light
C_KM_S = constants.c / 1000.0  # 299792.458 km/s


# ============================================================================
# FUNDAMENTAL CONSTANTS DATABASE
# ============================================================================

def build_constant_library() -> Dict[str, float]:
    """
    Compile library of dimensionless fundamental constants.

    Returns:
        Dict mapping constant names to values
    """
    library = {
        # Fundamental physics
        "alpha": constants.alpha,  # Fine-structure constant
        "alpha_inv": 1.0 / constants.alpha,  # 137.036
        "proton_electron_mass_ratio": constants.proton_mass / constants.electron_mass,  # ~1836.15
        "electron_muon_mass_ratio": constants.electron_mass / (105.6583755e-3 * 1e9 * constants.eV / constants.c**2),  # ~0.00483

        # Coupling constants (order of magnitude)
        "weak_coupling": 1.0 / 29.0,  # Approximate
        "strong_coupling": 1.0,  # At low energy (dimensionless estimate)

        # Mathematical constants
        "phi": (1.0 + np.sqrt(5.0)) / 2.0,  # Golden ratio
        "pi": np.pi,
        "e": np.e,
        "sqrt2": np.sqrt(2.0),
        "sqrt3": np.sqrt(3.0),
        "sqrt5": np.sqrt(5.0),
        "euler_gamma": 0.5772156649,  # Euler-Mascheroni constant
        "zeta3": 1.2020569,  # Riemann zeta(3) (Apéry's constant)

        # Powers of phi
        "phi_squared": ((1.0 + np.sqrt(5.0)) / 2.0) ** 2,
        "phi_cubed": ((1.0 + np.sqrt(5.0)) / 2.0) ** 3,
        "phi_inv": 2.0 / (1.0 + np.sqrt(5.0)),

        # Small dimensionless numbers
        "one_tenth": 0.1,
        "one_seventh": 1.0 / 7.0,
        "one_third": 1.0 / 3.0,
    }

    return library


# ============================================================================
# COMBINATION GENERATOR
# ============================================================================

def generate_constant_pairs(
    library: Dict[str, float],
    max_pairs: int = 10_000
) -> List[Tuple[str, str, float, float]]:
    """
    Generate pairs of constants for testing.

    Args:
        library: Constant library
        max_pairs: Maximum number of pairs to generate

    Returns:
        List of (name1, name2, value1, value2) tuples
    """
    const_names = list(library.keys())
    const_values = [library[k] for k in const_names]

    pairs = []

    # All unique pairs
    for (n1, v1), (n2, v2) in combinations(zip(const_names, const_values), 2):
        pairs.append((n1, n2, v1, v2))

        # Limit to avoid combinatorial explosion
        if len(pairs) >= max_pairs:
            break

    return pairs


def generate_extended_combinations(
    library: Dict[str, float],
    max_combinations: int = 50_000
) -> pd.DataFrame:
    """
    Generate extended combinations: products, quotients, powers.

    Args:
        library: Constant library
        max_combinations: Maximum combinations to test

    Returns:
        DataFrame with combination metadata
    """
    results = []

    const_items = list(library.items())

    count = 0

    # Binary operations
    for (name1, val1), (name2, val2) in combinations(const_items, 2):
        if count >= max_combinations:
            break

        # Product
        results.append({
            "name1": name1,
            "name2": name2,
            "value1": val1,
            "value2": val2,
            "operation": "multiply",
            "combined_value": val1 * val2,
            "formula": f"{name1} * {name2}"
        })
        count += 1

        # Quotient (both directions)
        if val2 != 0:
            results.append({
                "name1": name1,
                "name2": name2,
                "value1": val1,
                "value2": val2,
                "operation": "divide",
                "combined_value": val1 / val2,
                "formula": f"{name1} / {name2}"
            })
            count += 1

        if val1 != 0:
            results.append({
                "name1": name2,
                "name2": name1,
                "value1": val2,
                "value2": val1,
                "operation": "divide",
                "combined_value": val2 / val1,
                "formula": f"{name2} / {name1}"
            })
            count += 1

    # Simple powers
    for name, val in const_items:
        if count >= max_combinations:
            break

        for exp in [2, 3, 0.5, 1/3]:
            if val > 0:  # Avoid complex numbers
                results.append({
                    "name1": name,
                    "name2": f"^{exp}",
                    "value1": val,
                    "value2": exp,
                    "operation": "power",
                    "combined_value": val ** exp,
                    "formula": f"{name}^{exp}"
                })
                count += 1

    return pd.DataFrame(results)


# ============================================================================
# VELOCITY PREDICTION & SCORING
# ============================================================================

def predict_velocity_from_pair(
    const1: float,
    const2: float,
    c: float = C_KM_S
) -> float:
    """
    Predict velocity using formula: v = c / (const1 · const2)

    Args:
        const1: First constant
        const2: Second constant
        c: Speed of light [km/s]

    Returns:
        Predicted velocity [km/s]
    """
    if const1 == 0 or const2 == 0:
        return np.inf

    denominator = const1 * const2

    if denominator == 0:
        return np.inf

    v = c / denominator
    return v


def score_prediction(
    v_pred: float,
    v_obs: float = BOEHME_VELOCITY,
    sigma_obs: float = BOEHME_UNCERTAINTY
) -> Dict[str, float]:
    """
    Score a velocity prediction.

    Args:
        v_pred: Predicted velocity [km/s]
        v_obs: Observed velocity [km/s]
        sigma_obs: Observation uncertainty [km/s]

    Returns:
        Dict with scoring metrics
    """
    deviation = abs(v_pred - v_obs)
    relative_error = deviation / v_obs
    sigma_discrepancy = deviation / sigma_obs

    return {
        "v_pred": v_pred,
        "deviation": deviation,
        "relative_error": relative_error,
        "sigma_discrepancy": sigma_discrepancy
    }


# ============================================================================
# MASSIVE SCAN
# ============================================================================

class UniversalConstantScanner:
    """
    Scans constant combinations for velocity predictions.

    Methods:
        - scan_all_pairs: Test all constant pairs
        - rank_results: Rank by deviation from observation
        - compute_look_elsewhere: Statistical significance correction
    """

    def __init__(
        self,
        target_velocity: float = BOEHME_VELOCITY,
        target_uncertainty: float = BOEHME_UNCERTAINTY
    ):
        """
        Initialize scanner.

        Args:
            target_velocity: Observed velocity [km/s]
            target_uncertainty: Measurement uncertainty [km/s]
        """
        self.target_v = target_velocity
        self.target_sigma = target_uncertainty

        self.library = build_constant_library()
        self.results = None

    def scan_all_pairs(self, max_pairs: int = 10_000) -> pd.DataFrame:
        """
        Scan all constant pairs.

        Args:
            max_pairs: Maximum pairs to test

        Returns:
            DataFrame with all predictions and scores
        """
        print(f"Scanning up to {max_pairs:,} constant pairs...")

        pairs = generate_constant_pairs(self.library, max_pairs)

        results = []

        for name1, name2, val1, val2 in pairs:
            # Predict velocity
            v_pred = predict_velocity_from_pair(val1, val2)

            # Skip invalid predictions
            if not np.isfinite(v_pred) or v_pred <= 0 or v_pred > 1e6:
                continue

            # Score
            score = score_prediction(v_pred)

            results.append({
                "constant1": name1,
                "constant2": name2,
                "value1": val1,
                "value2": val2,
                "formula": f"c / ({name1} · {name2})",
                **score
            })

        self.results = pd.DataFrame(results)

        print(f"  ✓ Valid predictions: {len(self.results):,}")

        return self.results

    def rank_results(self, top_n: int = 20) -> pd.DataFrame:
        """
        Rank results by deviation.

        Args:
            top_n: Number of top results to return

        Returns:
            Top N best-fitting constant pairs
        """
        if self.results is None:
            raise ValueError("Run scan_all_pairs() first")

        # Sort by deviation
        ranked = self.results.sort_values("deviation").head(top_n)

        return ranked

    def compute_look_elsewhere_effect(self) -> Dict[str, float]:
        """
        Compute Look-Elsewhere Effect correction.

        Returns:
            Dict with statistical significance metrics
        """
        if self.results is None:
            raise ValueError("Run scan_all_pairs() first")

        # Our baseline (alpha, phi)
        alpha_phi_match = self.results[
            (self.results["constant1"] == "alpha") &
            (self.results["constant2"] == "phi")
        ]

        if len(alpha_phi_match) == 0:
            # Try inverse
            alpha_phi_match = self.results[
                (self.results["constant1"] == "alpha_inv") &
                (self.results["constant2"] == "phi")
            ]

        if len(alpha_phi_match) == 0:
            warnings.warn("Alpha-Phi pair not found in results")
            our_deviation = np.inf
        else:
            our_deviation = alpha_phi_match["deviation"].iloc[0]

        # How many are better?
        better_count = (self.results["deviation"] < our_deviation).sum()

        # Empirical p-value
        p_value_empirical = (better_count + 1) / (len(self.results) + 1)

        # Percentile
        percentile = (1 - p_value_empirical) * 100

        return {
            "our_deviation_km_s": our_deviation,
            "n_total_pairs": len(self.results),
            "n_better_than_ours": int(better_count),
            "p_value_empirical": p_value_empirical,
            "percentile": percentile,
            "look_elsewhere_penalty": len(self.results)
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run massive constant scan."""

    print("=" * 70)
    print("UNIVERSAL CONSTANT SCAN - LOOK-ELSEWHERE EFFECT (UTAC v5.0)")
    print("=" * 70)
    print()

    # Initialize scanner
    scanner = UniversalConstantScanner()

    print(f"Target: v_obs = {BOEHME_VELOCITY} ± {BOEHME_UNCERTAINTY} km/s")
    print(f"Constant library size: {len(scanner.library)}")
    print()

    # Scan all pairs
    results = scanner.scan_all_pairs(max_pairs=50_000)

    # Rank
    print()
    print("TOP 20 BEST-FITTING CONSTANT PAIRS:")
    print("=" * 70)

    top_20 = scanner.rank_results(top_n=20)

    for idx, row in top_20.iterrows():
        print(f"{idx+1:2d}. {row['formula']:40s}")
        print(f"    v_pred = {row['v_pred']:8.2f} km/s")
        print(f"    Deviation = {row['deviation']:6.2f} km/s ({row['relative_error']:.2%})")
        print()

    # Look-Elsewhere Effect
    print()
    print("LOOK-ELSEWHERE EFFECT ANALYSIS:")
    print("=" * 70)

    lee = scanner.compute_look_elsewhere_effect()

    for key, value in lee.items():
        if "p_value" in key or "percentile" in key:
            print(f"  {key:30s}: {value:.6f}")
        else:
            print(f"  {key:30s}: {value}")

    print()
    print("INTERPRETATION:")
    if lee["percentile"] >= 99.0:
        print(f"  ✓ STRONG: α-Φ is in top {100-lee['percentile']:.1f}% of all pairs tested.")
        print("  → Formula shows genuine predictive specificity.")
    elif lee["percentile"] >= 95.0:
        print(f"  ✓ MODERATE: α-Φ is in top {100-lee['percentile']:.1f}%.")
        print("  → Some specificity, but not exceptional.")
    else:
        print(f"  ✗ WEAK: α-Φ is only in top {100-lee['percentile']:.1f}%.")
        print("  → Many other constant pairs fit equally well or better.")
        print("  → Hypothesis requires revision.")

    print()

    # Save results
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    top_100 = scanner.rank_results(top_n=100)
    top_100.to_csv(OUTPUT_FILE, index=False)

    print(f"✓ Saved top 100 to: {OUTPUT_FILE}")
    print()

    # Summary file
    summary_file = OUTPUT_DIR / "look_elsewhere_summary.json"

    import json
    with open(summary_file, 'w') as f:
        summary = {
            "target_velocity_km_s": BOEHME_VELOCITY,
            "target_uncertainty_km_s": BOEHME_UNCERTAINTY,
            "n_constants_tested": len(scanner.library),
            "n_pairs_tested": len(results),
            "top_match": {
                "formula": top_20.iloc[0]["formula"],
                "v_pred": float(top_20.iloc[0]["v_pred"]),
                "deviation": float(top_20.iloc[0]["deviation"])
            },
            "alpha_phi_performance": {
                "deviation_km_s": float(lee["our_deviation_km_s"]),
                "percentile": float(lee["percentile"]),
                "p_value": float(lee["p_value_empirical"])
            }
        }
        json.dump(summary, f, indent=2)

    print(f"✓ Saved summary to: {summary_file}")
    print()

    print("=" * 70)
    print("CONSTANT SCAN COMPLETE")
    print("=" * 70)
    print()
    print("NEXT STEPS:")
    print("  1. Review top alternatives in cosmic_alternatives.csv")
    print("  2. Generate LaTeX tables: scripts/paper/generate_latex_tables.py")
    print("  3. Compile manuscript: scripts/paper/compile_manuscript.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
