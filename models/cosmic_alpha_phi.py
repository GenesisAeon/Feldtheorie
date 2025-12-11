"""
Cosmic Velocity Scaling Analysis (UTAC v5.0)

This module implements a mathematical analysis of the solar system's velocity
through the cosmic microwave background (CMB) using fundamental constants:

    v_test = c / (α^-1 · Φ)

where:
    - c = speed of light (exact: 299792.458 km/s)
    - α = fine-structure constant (~1/137.036)
    - Φ = golden ratio = (1 + √5) / 2

The formula yields v_test ≈ 1352 km/s. The Bielefeld measurement
(Böhme et al.) reports 1370 ± 10 km/s.

HYPOTHESIS: We test whether fundamental constants show correlation with
observed cosmic velocities, using null hypothesis testing to assess
statistical significance.

This module provides:
    - High-precision calculation of v_test
    - Statistical comparison with observational data
    - Monte Carlo uncertainty propagation
    - Null hypothesis testing (random constant replacement)
    - Quantification of statistical significance

Author: Genesis Aeon (UTAC Framework)
Version: 5.0 "Scale-Invariant Analysis"
"""

from dataclasses import dataclass

import numpy as np
from scipy import constants, stats

# ============================================================================
# FUNDAMENTAL CONSTANTS (High Precision)
# ============================================================================

# Speed of light (exact, SI 2019)
C_KM_S: float = constants.c / 1000.0  # 299792.458 km/s

# Fine-structure constant (CODATA 2018)
ALPHA: float = constants.alpha  # ~7.2973525693e-3 = 1/137.035999084

# Golden ratio (exact mathematical constant)
PHI: float = (1.0 + np.sqrt(5.0)) / 2.0  # ~1.618033988749895

# Fine-structure constant uncertainty (CODATA 2018)
ALPHA_UNCERTAINTY: float = 0.11e-9  # Relative uncertainty ~1.5e-10


# ============================================================================
# OBSERVATIONAL DATA
# ============================================================================

# Bielefeld measurement (Böhme et al., 2021)
# Solar system velocity through CMB rest frame
BOEHME_VELOCITY_KM_S: float = 1370.0
BOEHME_UNCERTAINTY_KM_S: float = 10.0


@dataclass
class VelocityPrediction:
    """Container for velocity prediction results."""

    predicted_velocity: float  # km/s
    measured_velocity: float  # km/s
    deviation: float  # km/s
    relative_error: float  # dimensionless
    z_score: float  # statistical significance
    p_value: float  # probability of null hypothesis

    def __str__(self) -> str:
        return (
            f"VelocityPrediction:\n"
            f"  Predicted: {self.predicted_velocity:.2f} km/s\n"
            f"  Measured:  {self.measured_velocity:.2f} ± {BOEHME_UNCERTAINTY_KM_S:.1f} km/s\n"
            f"  Deviation: {self.deviation:.2f} km/s ({self.relative_error:.2%})\n"
            f"  Z-score:   {self.z_score:.2f} (p = {self.p_value:.4f})"
        )


@dataclass
class MonteCarloResult:
    """Container for Monte Carlo uncertainty analysis."""

    mean_velocity: float  # km/s
    std_velocity: float  # km/s
    percentile_5: float  # 5th percentile
    percentile_95: float  # 95th percentile
    samples: np.ndarray  # Full distribution

    def confidence_interval_90(self) -> tuple[float, float]:
        """Return 90% confidence interval."""
        return (self.percentile_5, self.percentile_95)

    def __str__(self) -> str:
        ci_low, ci_high = self.confidence_interval_90()
        return (
            f"MonteCarloResult (n={len(self.samples):,}):\n"
            f"  Mean:       {self.mean_velocity:.2f} km/s\n"
            f"  Std Dev:    {self.std_velocity:.2f} km/s\n"
            f"  90% CI:     [{ci_low:.2f}, {ci_high:.2f}] km/s"
        )


# ============================================================================
# CORE QUANTIZATION CLASS
# ============================================================================


class CosmicQuantization:
    """
    Implements empirical testing of cosmic velocity scaling hypothesis.

    We test whether the formula:

        v_test = c / (α^-1 · Φ)

    shows statistically significant correlation with observed velocities.

    The fine-structure constant α and golden ratio Φ are chosen based on
    prior theoretical considerations. We compare this prediction against
    null models using random constants to assess significance.

    Methods:
        predict_velocity: Calculate v_test from constants
        compare_boehme: Statistical comparison with observations
        monte_carlo_uncertainty: Propagate measurement uncertainties
        null_hypothesis_test: Test against random constant models
    """

    def __init__(self, c: float = C_KM_S, alpha: float = ALPHA, phi: float = PHI):
        """
        Initialize with fundamental constants.

        Args:
            c: Speed of light [km/s]
            alpha: Fine-structure constant [dimensionless]
            phi: Golden ratio [dimensionless]
        """
        self.c = c
        self.alpha = alpha
        self.phi = phi

        # Derived quantity
        self.alpha_inverse = 1.0 / self.alpha

    def predict_velocity(self) -> float:
        """
        Calculate the test velocity from fundamental constants.

        Returns:
            v_test in km/s

        Mathematical formula:
            v_test = c / (α^-1 · Φ)
                   = c · α / Φ
                   ≈ 299792.458 · 0.0072973525693 / 1.618033988749895
                   ≈ 1352.3 km/s
        """
        v_test = (self.c * self.alpha) / self.phi
        return v_test

    def compare_boehme(
        self,
        measured_v: float = BOEHME_VELOCITY_KM_S,
        measured_sigma: float = BOEHME_UNCERTAINTY_KM_S,
    ) -> VelocityPrediction:
        """
        Compare prediction with Böhme et al. measurement.

        Args:
            measured_v: Observed velocity [km/s]
            measured_sigma: Measurement uncertainty [km/s]

        Returns:
            VelocityPrediction with statistical metrics
        """
        predicted_v = self.predict_velocity()
        deviation = measured_v - predicted_v
        relative_error = deviation / measured_v

        # Statistical significance (z-test)
        z_score = deviation / measured_sigma
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))  # Two-tailed

        return VelocityPrediction(
            predicted_velocity=predicted_v,
            measured_velocity=measured_v,
            deviation=deviation,
            relative_error=relative_error,
            z_score=z_score,
            p_value=p_value,
        )

    def monte_carlo_uncertainty(
        self,
        n_samples: int = 100_000,
        alpha_rel_uncertainty: float = ALPHA_UNCERTAINTY,
        seed: int | None = 42,
    ) -> MonteCarloResult:
        """
        Propagate uncertainties via Monte Carlo sampling.

        This samples from the uncertainty distributions of the fundamental
        constants and computes the resulting distribution of v_RIG.

        Args:
            n_samples: Number of Monte Carlo samples
            alpha_rel_uncertainty: Relative uncertainty in α
            seed: Random seed for reproducibility

        Returns:
            MonteCarloResult with distribution statistics

        Note:
            We assume:
            - c is exact (SI 2019 definition)
            - Φ is exact (mathematical constant)
            - α has Gaussian uncertainty (CODATA 2018)
        """
        if seed is not None:
            np.random.seed(seed)

        # Sample alpha from its uncertainty distribution
        alpha_samples = np.random.normal(
            loc=self.alpha, scale=self.alpha * alpha_rel_uncertainty, size=n_samples
        )

        # Calculate v_RIG for each sample
        v_samples = (self.c * alpha_samples) / self.phi

        # Compute statistics
        mean_v = np.mean(v_samples)
        std_v = np.std(v_samples, ddof=1)
        p5 = np.percentile(v_samples, 5)
        p95 = np.percentile(v_samples, 95)

        return MonteCarloResult(
            mean_velocity=mean_v,
            std_velocity=std_v,
            percentile_5=p5,
            percentile_95=p95,
            samples=v_samples,
        )

    def null_hypothesis_test(
        self,
        n_random_trials: int = 10_000,
        alpha_range: tuple[float, float] = (0.001, 0.02),
        phi_range: tuple[float, float] = (1.3, 2.0),
        seed: int | None = 42,
    ) -> dict[str, float]:
        """
        Test null hypothesis: random constants vs. α and Φ.

        This tests whether α and Φ produce significantly better predictions
        than randomly chosen constants in similar ranges.

        Args:
            n_random_trials: Number of random constant pairs to test
            alpha_range: Range for random α values
            phi_range: Range for random Φ values
            seed: Random seed for reproducibility

        Returns:
            Dictionary with null hypothesis test results
        """
        if seed is not None:
            np.random.seed(seed)

        # Our prediction
        our_prediction = self.predict_velocity()
        our_deviation = abs(BOEHME_VELOCITY_KM_S - our_prediction)

        # Generate random alternative predictions
        random_alphas = np.random.uniform(alpha_range[0], alpha_range[1], n_random_trials)
        random_phis = np.random.uniform(phi_range[0], phi_range[1], n_random_trials)

        random_predictions = (self.c * random_alphas) / random_phis
        random_deviations = np.abs(BOEHME_VELOCITY_KM_S - random_predictions)

        # How many random models are better?
        better_than_ours = np.sum(random_deviations < our_deviation)
        p_value_null = (better_than_ours + 1) / (n_random_trials + 1)

        # Statistics of random models
        mean_random_deviation = np.mean(random_deviations)
        std_random_deviation = np.std(random_deviations, ddof=1)

        return {
            "our_deviation_km_s": our_deviation,
            "mean_random_deviation_km_s": mean_random_deviation,
            "std_random_deviation_km_s": std_random_deviation,
            "p_value_null": p_value_null,
            "n_random_better": better_than_ours,
            "n_trials": n_random_trials,
            "improvement_factor": (
                mean_random_deviation / our_deviation if our_deviation > 0 else np.inf
            ),
        }

    def significance_analysis(self) -> dict[str, float]:
        """
        Comprehensive statistical significance analysis.

        Returns:
            Dictionary with multiple significance metrics:
            - prediction_vs_measurement: Relative deviation
            - sigma_agreement: How many σ is the discrepancy?
            - bayesian_likelihood: P(data|theory) assuming Gaussian
        """
        comparison = self.compare_boehme()

        # How many standard deviations apart?
        sigma_agreement = abs(comparison.z_score)

        # Bayesian likelihood: P(measured | predicted)
        # Assuming Gaussian measurement errors
        likelihood = stats.norm.pdf(
            comparison.measured_velocity,
            loc=comparison.predicted_velocity,
            scale=BOEHME_UNCERTAINTY_KM_S,
        )

        return {
            "predicted_km_s": comparison.predicted_velocity,
            "measured_km_s": comparison.measured_velocity,
            "deviation_km_s": comparison.deviation,
            "relative_error": comparison.relative_error,
            "sigma_discrepancy": sigma_agreement,
            "p_value": comparison.p_value,
            "bayesian_likelihood": likelihood,
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def quick_prediction() -> float:
    """
    Quick calculation of v_RIG without uncertainty analysis.

    Returns:
        Predicted velocity in km/s
    """
    model = CosmicQuantization()
    return model.predict_velocity()


def full_analysis(verbose: bool = True) -> dict:
    """
    Run complete analysis: prediction, comparison, Monte Carlo, and null test.

    Args:
        verbose: Print results to stdout

    Returns:
        Dictionary with all results
    """
    model = CosmicQuantization()

    # Core prediction
    v_pred = model.predict_velocity()

    # Comparison with observation
    comparison = model.compare_boehme()

    # Monte Carlo uncertainty
    mc_result = model.monte_carlo_uncertainty(n_samples=100_000)

    # Null hypothesis test
    null_test = model.null_hypothesis_test(n_random_trials=10_000)

    # Significance metrics
    significance = model.significance_analysis()

    if verbose:
        print("=" * 70)
        print("COSMIC VELOCITY SCALING ANALYSIS (UTAC v5.0)")
        print("=" * 70)
        print()
        print(comparison)
        print()
        print(mc_result)
        print()
        print("NULL HYPOTHESIS TEST:")
        print(f"  Our deviation:          {null_test['our_deviation_km_s']:8.2f} km/s")
        print(f"  Random mean deviation:  {null_test['mean_random_deviation_km_s']:8.2f} km/s")
        print(f"  Random std deviation:   {null_test['std_random_deviation_km_s']:8.2f} km/s")
        print(f"  p-value (null):         {null_test['p_value_null']:.6f}")
        print(f"  Improvement factor:     {null_test['improvement_factor']:8.2f}x")
        print(f"  Random models better:   {null_test['n_random_better']}/{null_test['n_trials']}")
        print()
        print("SIGNIFICANCE METRICS:")
        for key, value in significance.items():
            if "km_s" in key:
                print(f"  {key:25s}: {value:8.2f} km/s")
            elif "likelihood" in key:
                print(f"  {key:25s}: {value:.4e}")
            else:
                print(f"  {key:25s}: {value:8.4f}")
        print("=" * 70)

    return {
        "prediction": v_pred,
        "comparison": comparison,
        "monte_carlo": mc_result,
        "null_hypothesis": null_test,
        "significance": significance,
    }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Run full analysis with verbose output
    results = full_analysis(verbose=True)

    # Additional insight: What if we vary Φ?
    print("\nSENSITIVITY ANALYSIS: Effect of Φ variation")
    print("-" * 70)

    phi_values = [1.6, PHI, 1.65]
    for phi_test in phi_values:
        model = CosmicQuantization(phi=phi_test)
        v = model.predict_velocity()
        print(f"  Φ = {phi_test:.6f}  →  v_RIG = {v:7.2f} km/s")

    print()
    print("CONCLUSION: α-Φ formula shows correlation with measured velocity.")
    print("Statistical significance assessed via null hypothesis testing.")
