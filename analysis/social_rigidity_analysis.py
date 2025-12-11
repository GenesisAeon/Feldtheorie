#!/usr/bin/env python3
"""Social Rigidity Analysis: Gini → T_social → β_eff Validation.

This script validates the hypothesis from models/social_rigidity_ising.py:
    T_social = 1 / (Gini · Load)
    β_eff → ∞ at high inequality

It loads Gini time-series data (from scripts/ingest_world_bank_gini.py) and
fits the logistic rigidity transition:
    Rigidity(Gini) = σ(β(Gini - Θ))

HYPOTHESIS:
- High Gini countries (ZAF, BRA) should show steep transitions (high β)
- Low Gini countries (SWE, NOR) should show gradual transitions (low β)
- Cross-country comparison reveals β_Gini clustering

USAGE:
    python analysis/social_rigidity_analysis.py \
        --input data/social/gini_timeseries.csv \
        --output analysis/results/social_rigidity.json

REQUIREMENTS:
    Run scripts/ingest_world_bank_gini.py first to fetch data
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from scipy.optimize import curve_fit
    from scipy.stats import bootstrap
except ImportError:
    print("ERROR: scipy not installed. Run: pip install scipy", file=sys.stderr)
    sys.exit(1)

# Import UTAC models
sys.path.insert(0, str(Path(__file__).parents[1]))

BASE_DIR = Path(__file__).resolve().parents[1]


@dataclass
class RigidityFitResult:
    """Results from fitting Rigidity(Gini) = σ(β(Gini - Θ))."""

    country_code: str
    country_name: str
    beta: float
    theta: float
    r_squared: float
    n_observations: int
    beta_ci_lower: float
    beta_ci_upper: float
    theta_ci_lower: float
    theta_ci_upper: float
    model_type: str = "social_rigidity_logistic"

    def to_dict(self) -> dict[str, object]:
        return {
            "country_code": self.country_code,
            "country_name": self.country_name,
            "beta": self.beta,
            "theta": self.theta,
            "r_squared": self.r_squared,
            "n_observations": self.n_observations,
            "confidence_intervals": {
                "beta": [self.beta_ci_lower, self.beta_ci_upper],
                "theta": [self.theta_ci_lower, self.theta_ci_upper],
            },
            "model_type": self.model_type,
        }


def logistic_function(x: np.ndarray, beta: float, theta: float) -> np.ndarray:
    """Standard logistic function σ(β(x-Θ))."""
    return 1.0 / (1.0 + np.exp(-beta * (x - theta)))


def compute_r_squared(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute R² goodness-of-fit."""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0


def fit_rigidity_logistic(
    gini_values: np.ndarray, rigidity_proxy: np.ndarray
) -> tuple[float, float, float]:
    """Fit logistic function to Gini → Rigidity data.

    Args:
        gini_values: Gini coefficients (0-100 scale)
        rigidity_proxy: Normalized rigidity proxy (0-1 scale)

    Returns:
        (beta, theta, r_squared)
    """
    # Initial guesses
    theta_init = np.median(gini_values)
    beta_init = 0.1  # Start shallow

    try:
        popt, _ = curve_fit(
            logistic_function,
            gini_values,
            rigidity_proxy,
            p0=[beta_init, theta_init],
            bounds=([0.01, gini_values.min()], [20.0, gini_values.max()]),
            maxfev=5000,
        )
        beta, theta = popt

        # Compute R²
        y_pred = logistic_function(gini_values, beta, theta)
        r_squared = compute_r_squared(rigidity_proxy, y_pred)

        return beta, theta, r_squared

    except Exception as e:
        print(f"WARNING: Fit failed: {e}", file=sys.stderr)
        return 0.0, 0.0, 0.0


def bootstrap_confidence_intervals(
    gini_values: np.ndarray, rigidity_proxy: np.ndarray, n_bootstrap: int = 1000
) -> tuple[float, float, float, float]:
    """Compute bootstrap confidence intervals for β and Θ.

    Args:
        gini_values: Gini coefficients
        rigidity_proxy: Rigidity proxy
        n_bootstrap: Number of bootstrap samples (default: 1000)

    Returns:
        (beta_ci_lower, beta_ci_upper, theta_ci_lower, theta_ci_upper)
    """
    n = len(gini_values)
    beta_samples = []
    theta_samples = []

    for _ in range(n_bootstrap):
        indices = np.random.choice(n, size=n, replace=True)
        gini_boot = gini_values[indices]
        rigidity_boot = rigidity_proxy[indices]

        beta, theta, _ = fit_rigidity_logistic(gini_boot, rigidity_boot)
        if beta > 0 and theta > 0:  # Valid fit
            beta_samples.append(beta)
            theta_samples.append(theta)

    if not beta_samples:
        return 0.0, 0.0, 0.0, 0.0

    beta_ci = np.percentile(beta_samples, [2.5, 97.5])
    theta_ci = np.percentile(theta_samples, [2.5, 97.5])

    return beta_ci[0], beta_ci[1], theta_ci[0], theta_ci[1]


def compute_rigidity_proxy(df: pd.DataFrame, country_code: str) -> np.ndarray:
    """Compute rigidity proxy for a country's time series.

    For now, we use a simple proxy based on Gini temporal variance:
    - Low variance → low rigidity (flexible)
    - High variance → high rigidity (locked)

    FUTURE: Integrate actual adaptability metrics (Innovation Index, Policy Response Time, etc.)

    Args:
        df: DataFrame with columns [country_code, year, gini_value]
        country_code: ISO 3-letter country code

    Returns:
        Rigidity proxy (0-1 scale, same length as gini_values)
    """
    country_df = df[df["country_code"] == country_code].sort_values("year")
    gini = country_df["gini_value"].values

    # Compute rolling variance (window=3)
    if len(gini) < 3:
        return np.zeros(len(gini))

    variance = pd.Series(gini).rolling(window=3, center=True).var().fillna(0).values

    # Normalize to 0-1
    rigidity = variance / (variance.max() + 1e-6)

    return rigidity


def analyze_country(df: pd.DataFrame, country_code: str) -> RigidityFitResult | None:
    """Analyze a single country's Gini → Rigidity transition.

    Args:
        df: Full DataFrame with all countries
        country_code: ISO 3-letter country code

    Returns:
        RigidityFitResult or None if insufficient data
    """
    country_df = df[df["country_code"] == country_code].sort_values("year")

    if len(country_df) < 5:
        print(
            f"WARNING: Insufficient data for {country_code} ({len(country_df)} obs)",
            file=sys.stderr,
        )
        return None

    country_name = country_df["country_name"].iloc[0]
    gini = country_df["gini_value"].values

    # Compute rigidity proxy
    rigidity = compute_rigidity_proxy(df, country_code)

    # Fit logistic
    beta, theta, r_squared = fit_rigidity_logistic(gini, rigidity)

    if beta == 0 or theta == 0:
        print(f"WARNING: Fit failed for {country_code}", file=sys.stderr)
        return None

    # Bootstrap CI
    beta_ci_lower, beta_ci_upper, theta_ci_lower, theta_ci_upper = bootstrap_confidence_intervals(
        gini, rigidity, n_bootstrap=1000
    )

    print(f"✅ {country_code}: β={beta:.2f}, Θ={theta:.1f}, R²={r_squared:.3f}", file=sys.stderr)

    return RigidityFitResult(
        country_code=country_code,
        country_name=country_name,
        beta=beta,
        theta=theta,
        r_squared=r_squared,
        n_observations=len(country_df),
        beta_ci_lower=beta_ci_lower,
        beta_ci_upper=beta_ci_upper,
        theta_ci_lower=theta_ci_lower,
        theta_ci_upper=theta_ci_upper,
    )


def export_results(results: list[RigidityFitResult], output_path: Path) -> None:
    """Export analysis results to JSON.

    Args:
        results: List of RigidityFitResult objects
        output_path: Output JSON path
    """
    if not results:
        print("WARNING: No results to export!", file=sys.stderr)
        return

    # Sort by β (descending) to see high-rigidity countries first
    results_sorted = sorted(results, key=lambda r: r.beta, reverse=True)

    envelope = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "script": "analysis/social_rigidity_analysis.py",
            "model": "models/social_rigidity_ising.py",
            "hypothesis": "T_social = 1/(Gini·Load) → β_eff → ∞ at high inequality",
            "n_countries": len(results),
        },
        "summary": {
            "beta_range": {
                "min": min(r.beta for r in results),
                "max": max(r.beta for r in results),
                "mean": np.mean([r.beta for r in results]),
                "median": np.median([r.beta for r in results]),
            },
            "high_rigidity_countries": [r.country_code for r in results_sorted[:5]],  # Top 5 by β
            "low_rigidity_countries": [
                r.country_code for r in results_sorted[-5:]  # Bottom 5 by β
            ],
        },
        "results": [r.to_dict() for r in results_sorted],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(envelope, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Results exported to {output_path}", file=sys.stderr)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze social rigidity from Gini data")
    parser.add_argument(
        "--input",
        type=Path,
        default=BASE_DIR / "data" / "social" / "gini_timeseries.csv",
        help="Input CSV with Gini data (default: data/social/gini_timeseries.csv)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE_DIR / "analysis" / "results" / "social_rigidity.json",
        help="Output JSON path (default: analysis/results/social_rigidity.json)",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    input_path = args.input if args.input.is_absolute() else BASE_DIR / args.input

    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        print("Run: python scripts/ingest_world_bank_gini.py first", file=sys.stderr)
        return 1

    print(f"Loading data from {input_path}...", file=sys.stderr)
    df = pd.read_csv(input_path)

    countries = df["country_code"].unique()
    print(f"Found {len(countries)} countries: {', '.join(sorted(countries))}\n", file=sys.stderr)

    # Analyze each country
    results = []
    for country in sorted(countries):
        result = analyze_country(df, country)
        if result:
            results.append(result)

    if not results:
        print("ERROR: No valid results!", file=sys.stderr)
        return 1

    # Export
    export_results(results, args.output if args.output.is_absolute() else BASE_DIR / args.output)

    print("\n🎯 Validation Status:", file=sys.stderr)
    print(f"  ✅ Analyzed {len(results)} countries", file=sys.stderr)
    print("  ⏳ NEXT: Compare β values with inequality levels", file=sys.stderr)
    print("  ⏳ NEXT: Test hypothesis: High Gini → High β", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
