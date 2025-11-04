"""Multiple testing correction for cross-domain threshold analysis.

When fitting logistic models to multiple datasets across domains and comparing
against multiple null models, the cumulative false positive rate (Type I error)
inflates. This module implements standard corrections to maintain valid inference.

Problem:
    - 11 datasets × 3 null models = 33 statistical comparisons
    - At α = 0.05, expect ~1.65 false positives by chance alone
    - Standard ΔAIC = 10 threshold (p ≈ 0.007) still gives 23% familywise error

Solutions:
    1. Bonferroni correction (conservative)
    2. Benjamini-Hochberg FDR control (less conservative)
    3. Holm-Bonferroni step-down (balance)
    4. Adjusted ΔAIC thresholds for model selection
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
OUTPUT_PATH = Path("analysis/results/multiple_testing_correction.json")


@dataclass
class ModelComparison:
    """Single pairwise model comparison."""

    domain: str
    dataset: str
    null_model: str
    delta_aic: float
    p_value: float  # Approximate p-value from likelihood ratio test


def aic_to_likelihood_ratio_p(delta_aic: float) -> float:
    """Convert ΔAIC to approximate p-value.

    ΔAIC = 2 * log(L1/L0) where L1, L0 are likelihoods.
    Under nested models, 2*log(LR) ~ χ²(df), where df = difference in parameters.

    For logistic (4 params) vs linear/power-law (2 params), df = 2.

    Parameters
    ----------
    delta_aic : float
        AIC(null) - AIC(logistic). Positive favors logistic.

    Returns
    -------
    p_value : float
        Approximate two-tailed p-value.
    """
    if delta_aic <= 0:
        return 1.0  # Null is better or equal

    # ΔAIC = 2 * log(L_logistic / L_null)
    # Under H0 (null is true), this follows χ²(df=2)
    chi2_stat = delta_aic
    p_value = 1 - stats.chi2.cdf(chi2_stat, df=2)

    return float(p_value)


def bonferroni_correction(p_values: np.ndarray, alpha: float = 0.05) -> np.ndarray:
    """Bonferroni correction for multiple comparisons.

    Adjusts significance threshold to α/m where m is number of tests.

    Parameters
    ----------
    p_values : array_like
        Raw p-values
    alpha : float, default=0.05
        Familywise error rate

    Returns
    -------
    reject : np.ndarray
        Boolean array indicating which hypotheses to reject
    """
    m = len(p_values)
    alpha_corrected = alpha / m
    return p_values < alpha_corrected


def benjamini_hochberg_fdr(p_values: np.ndarray, q: float = 0.05) -> np.ndarray:
    """Benjamini-Hochberg FDR control procedure.

    Controls false discovery rate (expected proportion of false positives
    among rejections) at level q.

    Parameters
    ----------
    p_values : array_like
        Raw p-values
    q : float, default=0.05
        False discovery rate threshold

    Returns
    -------
    reject : np.ndarray
        Boolean array indicating which hypotheses to reject
    """
    m = len(p_values)
    sorted_indices = np.argsort(p_values)
    sorted_p = p_values[sorted_indices]

    # BH critical values: p(i) ≤ (i/m) * q
    critical_values = (np.arange(1, m + 1) / m) * q

    # Find largest i such that p(i) ≤ critical
    significant = sorted_p <= critical_values
    if not np.any(significant):
        return np.zeros(m, dtype=bool)

    k = np.where(significant)[0][-1]  # Largest significant index

    # Reject all hypotheses up to k
    reject = np.zeros(m, dtype=bool)
    reject[sorted_indices[: k + 1]] = True

    return reject


def holm_bonferroni(p_values: np.ndarray, alpha: float = 0.05) -> np.ndarray:
    """Holm-Bonferroni step-down procedure.

    More powerful than Bonferroni while controlling familywise error rate.

    Parameters
    ----------
    p_values : array_like
        Raw p-values
    alpha : float, default=0.05
        Familywise error rate

    Returns
    -------
    reject : np.ndarray
        Boolean array indicating which hypotheses to reject
    """
    m = len(p_values)
    sorted_indices = np.argsort(p_values)
    sorted_p = p_values[sorted_indices]

    # Holm critical values: p(i) ≤ α / (m - i + 1)
    critical_values = alpha / (m - np.arange(m))

    # Find first i where p(i) > critical (stop rejecting)
    reject_mask = sorted_p <= critical_values

    if not np.any(reject_mask):
        return np.zeros(m, dtype=bool)

    # Stop at first non-rejection
    first_accept = np.where(~reject_mask)[0]
    if len(first_accept) > 0:
        k = first_accept[0]
    else:
        k = m

    # Reject all hypotheses up to k-1
    reject = np.zeros(m, dtype=bool)
    reject[sorted_indices[:k]] = True

    return reject


def corrected_aic_threshold(
    n_comparisons: int,
    alpha: float = 0.05,
    correction: str = "bonferroni"
) -> float:
    """Compute ΔAIC threshold adjusted for multiple testing.

    Parameters
    ----------
    n_comparisons : int
        Total number of model comparisons
    alpha : float, default=0.05
        Desired error rate
    correction : str, default='bonferroni'
        Type of correction: 'bonferroni', 'holm', or 'fdr'

    Returns
    -------
    delta_aic_threshold : float
        Adjusted ΔAIC threshold
    """
    if correction == "bonferroni":
        alpha_corrected = alpha / n_comparisons
    elif correction == "holm":
        # Holm is adaptive; use most conservative (first comparison)
        alpha_corrected = alpha / n_comparisons
    elif correction == "fdr":
        # FDR at level q; use q as effective alpha
        alpha_corrected = alpha
    else:
        raise ValueError(f"Unknown correction: {correction}")

    # Convert α to ΔAIC threshold
    # p = α corresponds to χ²(df=2) critical value
    chi2_critical = stats.chi2.ppf(1 - alpha_corrected, df=2)
    delta_aic_threshold = chi2_critical

    return float(delta_aic_threshold)


def load_comparisons_from_cohort() -> List[ModelComparison]:
    """Load model comparisons from cohort summary."""
    cohort_path = RESULTS_DIR / "resonance_cohort_summary_validated.json"

    if not cohort_path.exists():
        cohort_path = RESULTS_DIR / "resonance_cohort_summary.json"

    with open(cohort_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    comparisons = []
    for entry in data.get("cohort", []):
        domain = entry.get("domain", "unknown")
        dataset = entry.get("dataset", "unknown")

        # Extract ΔAIC for each null model
        for null_model in ["linear", "power", "exponential"]:
            delta_aic_key = f"delta_aic_{null_model}"
            delta_aic = entry.get(delta_aic_key)

            if delta_aic is None:
                continue

            p_value = aic_to_likelihood_ratio_p(delta_aic)

            comparisons.append(
                ModelComparison(
                    domain=domain,
                    dataset=dataset,
                    null_model=null_model,
                    delta_aic=float(delta_aic),
                    p_value=p_value,
                )
            )

    return comparisons


def interpret_corrections(
    comparisons: List[ModelComparison],
    bonferroni_reject: np.ndarray,
    bh_reject: np.ndarray,
    holm_reject: np.ndarray,
    corrected_thresholds: Dict[str, float],
) -> str:
    """Generate interpretation of multiple testing corrections."""

    lines = []
    lines.append("MULTIPLE TESTING CORRECTION ANALYSIS")
    lines.append("=" * 60)
    lines.append("")

    lines.append(f"Total comparisons: {len(comparisons)}")
    lines.append(f"Uncorrected rejections (ΔAIC > 10): {sum(c.delta_aic > 10 for c in comparisons)}")
    lines.append("")

    lines.append("Corrected thresholds:")
    lines.append(f"  Bonferroni ΔAIC threshold: {corrected_thresholds['bonferroni']:.1f}")
    lines.append(f"  Holm ΔAIC threshold: {corrected_thresholds['holm']:.1f}")
    lines.append(f"  FDR (q=0.05) ΔAIC threshold: {corrected_thresholds['fdr']:.1f}")
    lines.append("")

    lines.append("Rejections after correction:")
    lines.append(f"  Bonferroni: {np.sum(bonferroni_reject)} / {len(comparisons)}")
    lines.append(f"  Holm: {np.sum(holm_reject)} / {len(comparisons)}")
    lines.append(f"  BH-FDR: {np.sum(bh_reject)} / {len(comparisons)}")
    lines.append("")

    lines.append("INTERPRETATION:")
    if np.sum(bh_reject) < len(comparisons) / 3:
        lines.append(
            "  After multiple testing correction, fewer than 1/3 of comparisons"
        )
        lines.append("  remain significant. This suggests:")
        lines.append("    - Some initial ΔAIC > 10 findings may be false positives")
        lines.append("    - Universality claims should be limited to corrected-significant datasets")
        lines.append("    - Recommend reporting FDR-adjusted results in manuscript")
    else:
        lines.append(
            "  Majority of comparisons remain significant after correction."
        )
        lines.append("  This supports robust model preference for logistic over null models.")

    lines.append("")
    lines.append("RECOMMENDATION:")
    lines.append("  Use Holm or BH-FDR correction (moderate conservativeness)")
    lines.append(f"  Report ΔAIC threshold as {corrected_thresholds['holm']:.1f} (Holm-adjusted)")
    lines.append("  Update manuscript to reflect corrected inference")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Apply multiple testing corrections to model comparisons"
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="Familywise error rate or FDR level (default: 0.05)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="Output JSON path",
    )
    args = parser.parse_args()

    # Load comparisons
    comparisons = load_comparisons_from_cohort()

    if len(comparisons) == 0:
        print("ERROR: No model comparisons found in cohort summary")
        return 1

    print(f"Loaded {len(comparisons)} model comparisons")
    print(f"Applying corrections with α = {args.alpha}")
    print("")

    # Extract p-values
    p_values = np.array([c.p_value for c in comparisons])

    # Apply corrections
    bonferroni_reject = bonferroni_correction(p_values, args.alpha)
    bh_reject = benjamini_hochberg_fdr(p_values, args.alpha)
    holm_reject = holm_bonferroni(p_values, args.alpha)

    # Compute corrected ΔAIC thresholds
    corrected_thresholds = {
        "bonferroni": corrected_aic_threshold(
            len(comparisons), args.alpha, "bonferroni"
        ),
        "holm": corrected_aic_threshold(len(comparisons), args.alpha, "holm"),
        "fdr": corrected_aic_threshold(len(comparisons), args.alpha, "fdr"),
    }

    # Build output
    output = {
        "n_comparisons": len(comparisons),
        "alpha": args.alpha,
        "uncorrected_rejections": int(sum(c.delta_aic > 10 for c in comparisons)),
        "corrected_thresholds": corrected_thresholds,
        "bonferroni": {
            "n_reject": int(np.sum(bonferroni_reject)),
            "rejected_comparisons": [
                {
                    "domain": comp.domain,
                    "dataset": comp.dataset,
                    "null_model": comp.null_model,
                    "delta_aic": comp.delta_aic,
                    "p_value": comp.p_value,
                }
                for i, comp in enumerate(comparisons)
                if bonferroni_reject[i]
            ],
        },
        "benjamini_hochberg": {
            "n_reject": int(np.sum(bh_reject)),
            "rejected_comparisons": [
                {
                    "domain": comp.domain,
                    "dataset": comp.dataset,
                    "null_model": comp.null_model,
                    "delta_aic": comp.delta_aic,
                    "p_value": comp.p_value,
                }
                for i, comp in enumerate(comparisons)
                if bh_reject[i]
            ],
        },
        "holm": {
            "n_reject": int(np.sum(holm_reject)),
            "rejected_comparisons": [
                {
                    "domain": comp.domain,
                    "dataset": comp.dataset,
                    "null_model": comp.null_model,
                    "delta_aic": comp.delta_aic,
                    "p_value": comp.p_value,
                }
                for i, comp in enumerate(comparisons)
                if holm_reject[i]
            ],
        },
        "all_comparisons": [
            {
                "domain": c.domain,
                "dataset": c.dataset,
                "null_model": c.null_model,
                "delta_aic": c.delta_aic,
                "p_value": c.p_value,
                "bonferroni_reject": bool(bonferroni_reject[i]),
                "bh_reject": bool(bh_reject[i]),
                "holm_reject": bool(holm_reject[i]),
            }
            for i, c in enumerate(comparisons)
        ],
    }

    # Generate interpretation
    interpretation = interpret_corrections(
        comparisons, bonferroni_reject, bh_reject, holm_reject, corrected_thresholds
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
