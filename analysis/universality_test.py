"""Statistical test for β universality hypothesis across domains.

This module implements rigorous hypothesis testing to evaluate whether
the steepness parameter β can be considered universal across domains.

Hypothesis:
    H0: All β values come from the same distribution centered at β₀ = 4.2
    H1: β values show significant heterogeneity incompatible with universality

Methods:
    - Weighted chi-square test using inverse variance weights from CIs
    - Cochran's Q test for homogeneity
    - Effect size estimation (I² statistic)
    - Meta-analytic random-effects model
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy import stats

RESULTS_DIR = Path("analysis/results")
OUTPUT_PATH = Path("analysis/results/universality_test.json")


@dataclass
class BetaEstimate:
    """Container for a single domain's β estimate."""

    domain: str
    dataset: str
    beta: float
    ci_lower: float
    ci_upper: float
    n_obs: int

    @property
    def se(self) -> float:
        """Standard error estimated from 95% CI."""
        # 95% CI ≈ β ± 1.96*SE
        return (self.ci_upper - self.ci_lower) / 3.92

    @property
    def variance(self) -> float:
        """Variance of β estimate."""
        return self.se ** 2

    @property
    def weight(self) -> float:
        """Inverse-variance weight for meta-analysis."""
        return 1.0 / self.variance


def weighted_chi_square_test(
    estimates: List[BetaEstimate],
    null_beta: float = 4.2
) -> Tuple[float, float, int]:
    """Perform weighted chi-square test for homogeneity.

    Tests whether all β estimates are consistent with a common value β₀.

    Parameters
    ----------
    estimates : List[BetaEstimate]
        β estimates from different domains
    null_beta : float, default=4.2
        Hypothesized universal β value

    Returns
    -------
    chi2_stat : float
        Chi-square test statistic
    p_value : float
        Two-tailed p-value
    df : int
        Degrees of freedom
    """
    betas = np.array([e.beta for e in estimates])
    weights = np.array([e.weight for e in estimates])

    # Weighted sum of squared deviations
    chi2_stat = np.sum(weights * (betas - null_beta) ** 2)
    df = len(estimates) - 1
    p_value = 1 - stats.chi2.cdf(chi2_stat, df)

    return float(chi2_stat), float(p_value), df


def cochran_q_test(estimates: List[BetaEstimate]) -> Tuple[float, float, int]:
    """Cochran's Q test for heterogeneity in β estimates.

    Tests whether β values are more variable than expected by chance.

    Returns
    -------
    Q : float
        Cochran's Q statistic
    p_value : float
        P-value from chi-square distribution
    df : int
        Degrees of freedom
    """
    betas = np.array([e.beta for e in estimates])
    weights = np.array([e.weight for e in estimates])

    # Weighted mean
    weighted_mean = np.sum(weights * betas) / np.sum(weights)

    # Q statistic
    Q = np.sum(weights * (betas - weighted_mean) ** 2)
    df = len(estimates) - 1
    p_value = 1 - stats.chi2.cdf(Q, df)

    return float(Q), float(p_value), df


def i_squared_statistic(Q: float, df: int) -> float:
    """Calculate I² heterogeneity statistic.

    I² estimates the proportion of total variance due to true heterogeneity
    rather than sampling error.

    Returns
    -------
    i_squared : float
        Percentage of heterogeneity (0-100%)
        < 25%: low heterogeneity
        25-50%: moderate heterogeneity
        > 50%: substantial heterogeneity
    """
    if Q <= df:
        return 0.0
    return 100 * (Q - df) / Q


def random_effects_meta_analysis(
    estimates: List[BetaEstimate]
) -> Tuple[float, float, float, float]:
    """DerSimonian-Laird random-effects meta-analysis.

    Estimates a common β while accounting for between-domain heterogeneity.

    Returns
    -------
    pooled_beta : float
        Pooled β estimate
    pooled_se : float
        Standard error of pooled estimate
    tau_squared : float
        Between-domain variance estimate
    prediction_interval : Tuple[float, float]
        95% prediction interval for a new domain
    """
    betas = np.array([e.beta for e in estimates])
    variances = np.array([e.variance for e in estimates])
    weights = 1.0 / variances

    # Weighted mean (fixed-effects)
    weighted_mean = np.sum(weights * betas) / np.sum(weights)

    # Q statistic
    Q = np.sum(weights * (betas - weighted_mean) ** 2)
    df = len(estimates) - 1

    # Between-domain variance (tau²)
    C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
    tau_squared = max(0.0, (Q - df) / C)

    # Random-effects weights
    re_weights = 1.0 / (variances + tau_squared)

    # Random-effects pooled estimate
    pooled_beta = np.sum(re_weights * betas) / np.sum(re_weights)
    pooled_se = np.sqrt(1.0 / np.sum(re_weights))

    # 95% prediction interval
    pred_se = np.sqrt(pooled_se ** 2 + tau_squared)
    pred_lower = pooled_beta - 1.96 * pred_se
    pred_upper = pooled_beta + 1.96 * pred_se

    return (
        float(pooled_beta),
        float(pooled_se),
        float(tau_squared),
        (float(pred_lower), float(pred_upper)),
    )


def load_estimates_from_cohort_summary() -> List[BetaEstimate]:
    """Load β estimates from resonance cohort summary."""
    cohort_path = RESULTS_DIR / "resonance_cohort_summary_validated.json"

    if not cohort_path.exists():
        cohort_path = RESULTS_DIR / "resonance_cohort_summary.json"

    with open(cohort_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    estimates = []
    for entry in data.get("cohort", []):
        # Extract β and CI
        beta = entry.get("beta")
        ci = entry.get("beta_ci", [])

        if beta is None or len(ci) != 2:
            continue

        estimates.append(
            BetaEstimate(
                domain=entry.get("domain", "unknown"),
                dataset=entry.get("dataset", "unknown"),
                beta=float(beta),
                ci_lower=float(ci[0]),
                ci_upper=float(ci[1]),
                n_obs=entry.get("n_observations", 0),
            )
        )

    return estimates


def interpret_results(
    chi2_stat: float,
    chi2_p: float,
    Q: float,
    Q_p: float,
    i_squared: float,
    pooled_beta: float,
    pooled_se: float,
    tau_squared: float,
) -> str:
    """Generate interpretation of universality test results."""

    lines = []
    lines.append("INTERPRETATION OF UNIVERSALITY TEST")
    lines.append("=" * 50)
    lines.append("")

    # Chi-square test interpretation
    if chi2_p < 0.001:
        lines.append(
            f"Chi-square test: REJECT universality (p < 0.001, χ² = {chi2_stat:.2f})"
        )
        lines.append(
            "  β values deviate significantly from hypothesized universal β = 4.2"
        )
    elif chi2_p < 0.05:
        lines.append(
            f"Chi-square test: REJECT universality (p = {chi2_p:.4f}, χ² = {chi2_stat:.2f})"
        )
        lines.append("  β values show significant heterogeneity")
    else:
        lines.append(
            f"Chi-square test: Fail to reject (p = {chi2_p:.4f}, χ² = {chi2_stat:.2f})"
        )
        lines.append("  β values consistent with universal value")

    lines.append("")

    # Cochran's Q interpretation
    if Q_p < 0.05:
        lines.append(f"Cochran's Q: Significant heterogeneity (Q = {Q:.2f}, p = {Q_p:.4f})")
    else:
        lines.append(f"Cochran's Q: No significant heterogeneity (Q = {Q:.2f}, p = {Q_p:.4f})")

    lines.append("")

    # I² interpretation
    if i_squared < 25:
        heterogeneity = "LOW"
    elif i_squared < 50:
        heterogeneity = "MODERATE"
    else:
        heterogeneity = "SUBSTANTIAL"

    lines.append(f"I² statistic: {i_squared:.1f}% ({heterogeneity} heterogeneity)")
    lines.append("")

    # Meta-analysis summary
    lines.append(f"Pooled β estimate: {pooled_beta:.2f} ± {pooled_se:.2f}")
    lines.append(f"Between-domain variance (τ²): {tau_squared:.3f}")
    lines.append("")

    # Overall conclusion
    lines.append("CONCLUSION:")
    if chi2_p < 0.05 or i_squared > 50:
        lines.append(
            "  Data are INCONSISTENT with strict universality of β = 4.2."
        )
        lines.append(
            "  Observed β heterogeneity suggests domain-specific mechanisms."
        )
        lines.append(
            f"  Recommend reporting β clustering around {pooled_beta:.2f} rather than"
        )
        lines.append("  claiming a universal constant.")
    else:
        lines.append(
            "  Data are CONSISTENT with a common β value across domains."
        )
        lines.append(
            "  However, limited sample sizes warrant cautious interpretation."
        )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Test β universality hypothesis across domains"
    )
    parser.add_argument(
        "--null-beta",
        type=float,
        default=4.2,
        help="Hypothesized universal β value (default: 4.2)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="Output JSON path",
    )
    args = parser.parse_args()

    # Load estimates
    estimates = load_estimates_from_cohort_summary()

    if len(estimates) < 3:
        print(f"ERROR: Need at least 3 estimates for universality test, found {len(estimates)}")
        return 1

    print(f"Loaded {len(estimates)} β estimates from cohort summary")
    print(f"Testing universality with null hypothesis: β₀ = {args.null_beta}")
    print("")

    # Run tests
    chi2_stat, chi2_p, chi2_df = weighted_chi_square_test(estimates, args.null_beta)
    Q, Q_p, Q_df = cochran_q_test(estimates)
    i_squared = i_squared_statistic(Q, Q_df)
    pooled_beta, pooled_se, tau_squared, pred_interval = random_effects_meta_analysis(
        estimates
    )

    # Build output
    output = {
        "test_name": "β_universality_test",
        "null_hypothesis": f"β = {args.null_beta} across all domains",
        "n_domains": len(estimates),
        "chi_square_test": {
            "statistic": chi2_stat,
            "df": chi2_df,
            "p_value": chi2_p,
            "significant": chi2_p < 0.05,
        },
        "cochran_q_test": {
            "Q": Q,
            "df": Q_df,
            "p_value": Q_p,
            "significant": Q_p < 0.05,
        },
        "i_squared": {
            "value": i_squared,
            "interpretation": (
                "low" if i_squared < 25 else "moderate" if i_squared < 50 else "substantial"
            ),
        },
        "random_effects_meta_analysis": {
            "pooled_beta": pooled_beta,
            "pooled_se": pooled_se,
            "ci_lower": pooled_beta - 1.96 * pooled_se,
            "ci_upper": pooled_beta + 1.96 * pooled_se,
            "tau_squared": tau_squared,
            "prediction_interval": pred_interval,
        },
        "estimates": [
            {
                "domain": e.domain,
                "dataset": e.dataset,
                "beta": e.beta,
                "ci": [e.ci_lower, e.ci_upper],
                "se": e.se,
                "weight": e.weight,
            }
            for e in estimates
        ],
    }

    # Generate interpretation
    interpretation = interpret_results(
        chi2_stat, chi2_p, Q, Q_p, i_squared, pooled_beta, pooled_se, tau_squared
    )
    output["interpretation"] = interpretation

    # Save
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(interpretation)
    print("")
    print(f"Results saved to: {args.output}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
