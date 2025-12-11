#!/usr/bin/env python3
"""Cosmic Quantization: Local Group Extension (n>1 Systems).

This script extends models/cosmic_alpha_phi.py to test the v = c/(α⁻¹·Φ)
hypothesis across multiple systems in the Local Group, addressing the
"n=1 limitation" critique.

HYPOTHESIS:
    v_test = c / (α⁻¹ · Φ) ≈ 1352 km/s

SYSTEMS TESTED:
    1. Solar System → CMB rest frame (Böhme et al. 2020): 1370 ± 10 km/s
    2. Andromeda (M31) → Milky Way: ~300 km/s (approaching)
    3. Triangulum (M33) → Milky Way: ~180 km/s (approaching)
    4. Local Group → CMB rest frame: ~600 km/s
    5. Virgo Cluster → CMB: ~1000 km/s (from cluster dynamics)

DATA SOURCES:
    - NASA/IPAC Extragalactic Database (NED): https://ned.ipac.caltech.edu/
    - CODATA 2018: Fine-structure constant
    - Böhme et al. (2020): Solar system velocity

FALSIFICATION CRITERION:
    If v_test systematically fails across multiple scales (|residual| > 3σ),
    reject hypothesis. If v_test works at 2+ scales → strengthen evidence.

USAGE:
    python analysis/cosmic_quantization_local_group.py \
        --output analysis/results/cosmic_quantization_local_group.json

REQUIREMENTS:
    pip install numpy scipy pandas
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import stats

# Import CosmicQuantization base class
sys.path.insert(0, str(Path(__file__).parents[1]))
from models.cosmic_alpha_phi import ALPHA, C_KM_S, PHI, CosmicQuantization

BASE_DIR = Path(__file__).resolve().parents[1]


# ============================================================================
# Local Group Observational Data
# ============================================================================


@dataclass
class VelocityObservation:
    """Single velocity measurement with metadata."""

    system_name: str
    description: str
    observed_velocity: float  # km/s
    uncertainty: float  # km/s
    reference: str
    scale: str  # 'solar_system', 'galactic', 'cluster'
    notes: str = ""

    def z_score(self, predicted_velocity: float) -> float:
        """Compute z-score: (observed - predicted) / uncertainty."""
        return (self.observed_velocity - predicted_velocity) / self.uncertainty

    def relative_error(self, predicted_velocity: float) -> float:
        """Compute relative error: |observed - predicted| / observed."""
        return abs(self.observed_velocity - predicted_velocity) / self.observed_velocity

    def to_dict(self) -> dict[str, object]:
        return {
            "system_name": self.system_name,
            "description": self.description,
            "observed_velocity": self.observed_velocity,
            "uncertainty": self.uncertainty,
            "reference": self.reference,
            "scale": self.scale,
            "notes": self.notes,
        }


# Data from literature
LOCAL_GROUP_VELOCITIES = [
    VelocityObservation(
        system_name="Solar System",
        description="Solar system velocity through CMB rest frame",
        observed_velocity=1370.0,
        uncertainty=10.0,
        reference="Böhme et al. (2020), A&A 633, A145",
        scale="solar_system",
        notes="Bielefeld measurement, UTAC v5.0 baseline",
    ),
    VelocityObservation(
        system_name="Andromeda (M31)",
        description="Radial velocity of M31 relative to Milky Way",
        observed_velocity=301.0,  # Approaching (negative → magnitude)
        uncertainty=1.0,
        reference="van der Marel et al. (2012), ApJ 753, 8",
        scale="galactic",
        notes="Most precise M31 proper motion measurement",
    ),
    VelocityObservation(
        system_name="Triangulum (M33)",
        description="Radial velocity of M33 relative to Milky Way",
        observed_velocity=179.0,
        uncertainty=3.0,
        reference="NED (NASA/IPAC Extragalactic Database)",
        scale="galactic",
        notes="Heliocentric velocity, corrected for Galactic rotation",
    ),
    VelocityObservation(
        system_name="Local Group Barycenter",
        description="Local Group center of mass velocity through CMB",
        observed_velocity=627.0,
        uncertainty=22.0,
        reference="Fixsen et al. (1996), ApJ 473, 576",
        scale="cluster",
        notes="CMB dipole measurement, ~50% of Solar System value",
    ),
    VelocityObservation(
        system_name="Virgo Cluster",
        description="Virgo Cluster peculiar velocity relative to CMB",
        observed_velocity=1035.0,
        uncertainty=50.0,
        reference="Karachentsev et al. (2009), MNRAS 393, 1265",
        scale="cluster",
        notes="Cluster-scale dynamics, ~75% of Solar System value",
    ),
]


# ============================================================================
# Multi-System Analysis
# ============================================================================


@dataclass
class MultiSystemResult:
    """Results from testing v_test across multiple systems."""

    predicted_velocity: float  # km/s (v_test = c/(α⁻¹·Φ))
    observations: list[VelocityObservation]
    deviations: list[float]  # observed - predicted (km/s)
    z_scores: list[float]
    relative_errors: list[float]
    chi_squared: float
    p_value_chi_squared: float
    mean_relative_error: float
    systems_within_3_sigma: int
    total_systems: int

    def to_dict(self) -> dict[str, object]:
        return {
            "predicted_velocity": self.predicted_velocity,
            "observations": [obs.to_dict() for obs in self.observations],
            "statistics": {
                "chi_squared": self.chi_squared,
                "p_value": self.p_value_chi_squared,
                "mean_relative_error": self.mean_relative_error,
                "systems_within_3_sigma": self.systems_within_3_sigma,
                "total_systems": self.total_systems,
                "fraction_within_3_sigma": self.systems_within_3_sigma / self.total_systems,
            },
            "deviations_km_s": self.deviations,
            "z_scores": self.z_scores,
            "relative_errors": self.relative_errors,
        }


def analyze_local_group(
    observations: list[VelocityObservation],
) -> MultiSystemResult:
    """Test v_test = c/(α⁻¹·Φ) across multiple Local Group systems.

    Args:
        observations: List of velocity measurements

    Returns:
        MultiSystemResult with statistical analysis
    """
    quant = CosmicQuantization(c=C_KM_S, alpha=ALPHA, phi=PHI)
    v_test = quant.predict_velocity()

    print(f"\n📐 Predicted velocity: v_test = {v_test:.2f} km/s", file=sys.stderr)
    print(
        f"   Formula: c / (α⁻¹ · Φ) = {C_KM_S:.3f} / ({1/ALPHA:.3f} × {PHI:.6f})\n", file=sys.stderr
    )

    deviations = []
    z_scores = []
    relative_errors = []
    chi_squared_terms = []
    systems_within_3_sigma = 0

    print("System-by-System Analysis:", file=sys.stderr)
    print("-" * 80, file=sys.stderr)

    for obs in observations:
        deviation = obs.observed_velocity - v_test
        z = obs.z_score(v_test)
        rel_error = obs.relative_error(v_test)

        deviations.append(deviation)
        z_scores.append(z)
        relative_errors.append(rel_error)

        # χ² term
        chi_squared_terms.append((deviation / obs.uncertainty) ** 2)

        if abs(z) <= 3.0:
            systems_within_3_sigma += 1
            status = "✅"
        else:
            status = "⚠️"

        print(
            f"{status} {obs.system_name:25s} | "
            f"v_obs = {obs.observed_velocity:7.1f} ± {obs.uncertainty:4.1f} km/s | "
            f"Δv = {deviation:+7.1f} km/s | "
            f"z = {z:+5.2f} | "
            f"ε = {rel_error:5.1%}",
            file=sys.stderr,
        )

    print("-" * 80, file=sys.stderr)

    # χ² statistic
    chi_squared = sum(chi_squared_terms)
    dof = len(observations) - 1  # Degrees of freedom
    p_value = 1.0 - stats.chi2.cdf(chi_squared, dof)

    mean_rel_error = np.mean(relative_errors)

    print("\n📊 Statistical Summary:", file=sys.stderr)
    print(f"   χ² = {chi_squared:.2f} (dof={dof})", file=sys.stderr)
    print(f"   p-value = {p_value:.4f}", file=sys.stderr)
    print(f"   Mean relative error = {mean_rel_error:.1%}", file=sys.stderr)
    print(f"   Systems within 3σ: {systems_within_3_sigma}/{len(observations)}", file=sys.stderr)

    return MultiSystemResult(
        predicted_velocity=v_test,
        observations=observations,
        deviations=deviations,
        z_scores=z_scores,
        relative_errors=relative_errors,
        chi_squared=chi_squared,
        p_value_chi_squared=p_value,
        mean_relative_error=mean_rel_error,
        systems_within_3_sigma=systems_within_3_sigma,
        total_systems=len(observations),
    )


def null_model_comparison(
    observations: list[VelocityObservation], n_trials: int = 10000
) -> tuple[float, float]:
    """Test whether α and Φ outperform random constants.

    Args:
        observations: List of velocity measurements
        n_trials: Number of random constant pairs to test

    Returns:
        (fraction_worse, p_value)
    """
    # Compute χ² for our model
    quant = CosmicQuantization()
    v_test = quant.predict_velocity()

    chi_squared_target = sum(
        ((obs.observed_velocity - v_test) / obs.uncertainty) ** 2 for obs in observations
    )

    print(f"\n🎲 Null Model Test (n={n_trials:,} random constant pairs):", file=sys.stderr)
    print(f"   Target χ² = {chi_squared_target:.2f} (α={ALPHA:.6f}, Φ={PHI:.6f})", file=sys.stderr)

    # Generate random constants
    np.random.seed(1337)  # Reproducibility
    random_alphas = np.random.uniform(0.001, 0.01, size=n_trials)  # ~1/100 to ~1/1000
    random_phis = np.random.uniform(1.0, 2.0, size=n_trials)  # Near golden ratio range

    worse_count = 0

    for i, (alpha_rand, phi_rand) in enumerate(zip(random_alphas, random_phis)):
        quant_rand = CosmicQuantization(alpha=alpha_rand, phi=phi_rand)
        v_rand = quant_rand.predict_velocity()

        chi_squared_rand = sum(
            ((obs.observed_velocity - v_rand) / obs.uncertainty) ** 2 for obs in observations
        )

        if chi_squared_rand > chi_squared_target:
            worse_count += 1

        if (i + 1) % 2000 == 0:
            print(f"   Progress: {i+1:,}/{n_trials:,}", file=sys.stderr)

    fraction_worse = worse_count / n_trials
    p_value = 1.0 - fraction_worse  # Probability that random is better

    print(f"\n   Result: {worse_count:,}/{n_trials:,} random pairs were WORSE", file=sys.stderr)
    print(f"   → α and Φ outperform {fraction_worse:.1%} of random constants", file=sys.stderr)
    print(f"   → p-value = {p_value:.4f}", file=sys.stderr)

    return fraction_worse, p_value


def export_results(result: MultiSystemResult, null_p_value: float, output_path: Path) -> None:
    """Export analysis results to JSON.

    Args:
        result: MultiSystemResult object
        null_p_value: p-value from null model test
        output_path: Output JSON path
    """
    envelope = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "script": "analysis/cosmic_quantization_local_group.py",
            "model": "models/cosmic_alpha_phi.py",
            "hypothesis": "v_test = c / (α⁻¹ · Φ) shows correlation across multiple scales",
            "version": "5.0.0",
        },
        "constants": {
            "c_km_s": C_KM_S,
            "alpha": ALPHA,
            "phi": PHI,
            "v_test_predicted": result.predicted_velocity,
        },
        "multi_system_analysis": result.to_dict(),
        "null_model_test": {
            "n_trials": 10000,
            "p_value": null_p_value,
            "interpretation": "Probability that random constants outperform α and Φ",
        },
        "validation_status": {
            "n_systems": result.total_systems,
            "chi_squared_p_value": result.p_value_chi_squared,
            "mean_relative_error": result.mean_relative_error,
            "systems_within_3_sigma": result.systems_within_3_sigma,
            "verdict": (
                "STRENGTHENED: Multiple scales support hypothesis"
                if result.systems_within_3_sigma >= result.total_systems * 0.6
                else "WEAKENED: Hypothesis fails at multiple scales"
            ),
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(envelope, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Results exported to {output_path}", file=sys.stderr)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test cosmic quantization hypothesis across Local Group systems"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE_DIR / "analysis" / "results" / "cosmic_quantization_local_group.json",
        help="Output JSON path",
    )
    parser.add_argument(
        "--null-trials",
        type=int,
        default=10000,
        help="Number of null model trials (default: 10000)",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    print("=" * 80, file=sys.stderr)
    print("COSMIC QUANTIZATION: LOCAL GROUP EXTENSION (n>1 Systems)", file=sys.stderr)
    print("=" * 80, file=sys.stderr)

    # Multi-system analysis
    result = analyze_local_group(LOCAL_GROUP_VELOCITIES)

    # Null model test
    _, null_p_value = null_model_comparison(LOCAL_GROUP_VELOCITIES, n_trials=args.null_trials)

    # Export
    export_results(
        result, null_p_value, args.output if args.output.is_absolute() else BASE_DIR / args.output
    )

    # Verdict
    print("\n" + "=" * 80, file=sys.stderr)
    print("🎯 VERDICT:", file=sys.stderr)
    print("=" * 80, file=sys.stderr)

    if result.mean_relative_error < 0.30 and result.systems_within_3_sigma >= 3:
        print("✅ HYPOTHESIS STRENGTHENED:", file=sys.stderr)
        print(
            f"   • {result.systems_within_3_sigma}/{result.total_systems} systems within 3σ",
            file=sys.stderr,
        )
        print(f"   • Mean relative error = {result.mean_relative_error:.1%}", file=sys.stderr)
        print(f"   • χ² p-value = {result.p_value_chi_squared:.4f}", file=sys.stderr)
        print("   • Extension to n>1 systems SUPPORTS hypothesis", file=sys.stderr)
    else:
        print("⚠️  HYPOTHESIS WEAKENED:", file=sys.stderr)
        print(
            f"   • Only {result.systems_within_3_sigma}/{result.total_systems} systems within 3σ",
            file=sys.stderr,
        )
        print(f"   • Mean relative error = {result.mean_relative_error:.1%}", file=sys.stderr)
        print("   • Extension to n>1 systems reveals limitations", file=sys.stderr)

    print("\n📖 NEXT STEPS:", file=sys.stderr)
    print("   1. Extend to galaxy cluster velocities (Virgo, Coma, Fornax)", file=sys.stderr)
    print("   2. Compare with cosmological simulations (ΛCDM predictions)", file=sys.stderr)
    print("   3. Seek theoretical mechanism for α-Φ coupling", file=sys.stderr)
    print("=" * 80, file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
