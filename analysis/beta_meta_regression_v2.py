"""Advanced meta-regression for UTAC v1.2 logistic resonance.

This module refreshes the β meta-regression referenced in
`seed/NextStep.txt` and `seed/Manuskriptfinalisierung und Kampagnenstart.pdf`.
It quantifies how structural covariates (coupling efficiency, effective
dimensionality, memory, Θ drift, signal-to-noise) explain the heterogeneity of
logistic steepness across domains.

Tri-layer cadence:
    • Formal: Weighted least squares (WLS) with non-linear feature expansion
      keeps the logistic guard σ(β(R-Θ)) tethered to ΔAIC≥10 evidence.
    • Empirical: Bootstrap confidence intervals and random-forest diagnostics
      map cross-domain variance, reporting R² envelopes and feature importances.
    • Poetic: The membrane remembers where β departs from the canonical band,
      letting ζ(R) tune interventions in the resonance ledger.

Usage
-----
Run from the repository root:

```
python analysis/beta_meta_regression_v2.py \
    --beta-csv data/derived/beta_estimates.csv \
    --covariates-csv data/derived/domain_covariates.csv \
    --output-dir analysis/results
```

Outputs (timestamped in UTC):
    • `*_coefficients_YYYYMMDDTHHMMSSZ.csv` – coefficient table with Holm-corrected
      p-values.
    • `*_summary_YYYYMMDDTHHMMSSZ.json` – canonical resonance summary (R², ΔAIC guards,
      canonical β band coverage).
    • `*_diagnostics_YYYYMMDDTHHMMSSZ.json` – domain-level residuals, Cook’s distance,
      and impedance proxies.
    • `*_bootstrap_YYYYMMDDTHHMMSSZ.json` – WLS + Random Forest bootstrap envelopes.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm
from numpy.random import default_rng
from sklearn.ensemble import RandomForestRegressor
from statsmodels.stats.outliers_influence import OLSInfluence

CANONICAL_BETA = 4.2
CANONICAL_BAND = (3.6, 4.8)


@dataclass
class RegressionSummary:
    """Top-level resonance metrics for the refreshed regression."""

    timestamp: str
    r_squared: float
    adjusted_r_squared: float
    aic: float
    bic: float
    rmse: float
    canonical_beta: float
    canonical_band: Tuple[float, float]
    beta_mean: float
    beta_std: float
    beta_band_fraction: float
    delta_aic_guard_min: float
    bootstrap_r2_median: float
    bootstrap_r2_interval: Tuple[float, float]
    random_forest_oob_r2: Optional[float]
    random_forest_bootstrap_interval: Optional[Tuple[float, float]]

    def to_dict(self) -> Dict[str, object]:
        payload = asdict(self)
        payload["canonical_band"] = list(self.canonical_band)
        payload["bootstrap_r2_interval"] = list(self.bootstrap_r2_interval)
        if self.random_forest_bootstrap_interval is not None:
            payload["random_forest_bootstrap_interval"] = list(
                self.random_forest_bootstrap_interval
            )
        return payload


def load_and_prepare(beta_path: Path, covar_path: Path) -> pd.DataFrame:
    """Load β estimates and enrich with derived resonance features."""

    betas = pd.read_csv(beta_path)
    covars = pd.read_csv(covar_path)

    df = betas.merge(covars, on="domain", how="inner", validate="one_to_one")
    if df.empty:
        raise ValueError("No overlapping domains between beta and covariate tables")

    df["domain_family"] = df["domain"].str.split("_").str[0]
    df["beta_band_distance"] = df["beta"] - CANONICAL_BETA
    df["within_canonical_band"] = (
        (df["beta"] >= CANONICAL_BAND[0]) & (df["beta"] <= CANONICAL_BAND[1])
    )
    df["delta_aic_guard"] = df.get("delta_aic", np.nan)
    df["log_theta"] = np.log1p(df["theta"].clip(lower=1e-9))

    # Non-linear feature expansion inspired by seed/Sigillin_Neuro_Membran_Modell_Plan.txt
    df["coupling_sq"] = df["C_eff"] ** 2
    df["coupling_memory"] = df["C_eff"] * df["Memory"]
    df["zeta_proxy"] = df["C_eff"] / (1.0 + df["SNR"].replace(0, np.nan))
    df["zeta_proxy"] = df["zeta_proxy"].fillna(df["C_eff"] * 0.5)

    return df


def build_design_matrix(df: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame, pd.Series, pd.DataFrame]:
    """Construct dependent variable, design matrix, weights, and augmented table."""

    y = df["beta"]

    feature_cols = [
        "C_eff",
        "D_eff",
        "SNR",
        "Memory",
        "Theta_dot",
        "log_theta",
        "coupling_sq",
        "coupling_memory",
    ]

    X = df[feature_cols].apply(pd.to_numeric, errors="coerce")

    X.fillna(0.0, inplace=True)

    weights = pd.Series(np.ones(len(df)), index=df.index, dtype=float)
    if "beta_ci_width" in df.columns:
        safe_width = df["beta_ci_width"].replace({0.0: np.nan})
        inv_var = 1.0 / (safe_width ** 2)
        inv_var.replace([np.inf, -np.inf], np.nan, inplace=True)
        if inv_var.notna().any():
            weights = inv_var.fillna(inv_var.median())

    weights = weights.astype(float)

    X_design = sm.add_constant(X, has_constant="add")
    return y, X_design, weights, X


def run_wls(y: pd.Series, X_design: pd.DataFrame, weights: pd.Series) -> sm.regression.linear_model.RegressionResultsWrapper:
    """Fit weighted least squares meta-regression."""

    model = sm.WLS(y, X_design, weights=weights)
    return model.fit()


def bootstrap_wls(
    y: pd.Series,
    X_design: pd.DataFrame,
    weights: pd.Series,
    n_bootstrap: int,
    seed: Optional[int] = None,
) -> Tuple[Dict[str, Dict[str, float]], Dict[str, float]]:
    """Bootstrap coefficient and R² envelopes for the WLS model."""

    rng = default_rng(seed)
    params_samples: List[pd.Series] = []
    r2_samples: List[float] = []

    for _ in range(n_bootstrap):
        indices = rng.integers(0, len(y), len(y))
        X_sample = X_design.iloc[indices]
        y_sample = y.iloc[indices]
        w_sample = weights.iloc[indices]
        result = sm.WLS(y_sample, X_sample, weights=w_sample).fit()
        params_samples.append(result.params)
        r2_samples.append(float(result.rsquared))

    params_df = pd.DataFrame(params_samples)
    bootstrap_summary: Dict[str, Dict[str, float]] = {}
    for column in params_df.columns:
        series = params_df[column].dropna()
        bootstrap_summary[column] = {
            "median": float(series.median()),
            "p05": float(series.quantile(0.05)),
            "p95": float(series.quantile(0.95)),
            "std": float(series.std(ddof=1)),
        }

    r2_series = pd.Series(r2_samples)
    r2_summary = {
        "mean": float(r2_series.mean()),
        "median": float(r2_series.median()),
        "p05": float(r2_series.quantile(0.05)),
        "p95": float(r2_series.quantile(0.95)),
        "std": float(r2_series.std(ddof=1)),
    }

    return bootstrap_summary, r2_summary


def random_forest_diagnostics(
    X: pd.DataFrame,
    y: pd.Series,
    weights: pd.Series,
    n_estimators: int,
    n_bootstrap: int,
    seed: Optional[int] = None,
) -> Tuple[Optional[float], Dict[str, float], Dict[str, float]]:
    """Train a Random Forest regressor and derive bootstrap OOB envelopes."""

    if X.empty:
        return None, {}, {}

    base_model = RandomForestRegressor(
        n_estimators=n_estimators,
        random_state=seed,
        oob_score=True,
        bootstrap=True,
        n_jobs=-1,
    )
    base_model.fit(X, y, sample_weight=weights)
    oob_r2 = float(base_model.oob_score_) if base_model.oob_score else None

    feature_importances = {
        feature: float(importance)
        for feature, importance in zip(X.columns, base_model.feature_importances_)
    }

    rng = default_rng(seed)
    bootstrap_scores: List[float] = []
    for _ in range(max(0, n_bootstrap)):
        indices = rng.integers(0, len(y), len(y))
        X_sample = X.iloc[indices]
        y_sample = y.iloc[indices]
        w_sample = weights.iloc[indices]
        model = RandomForestRegressor(
            n_estimators=max(64, n_estimators // 2),
            random_state=int(rng.integers(0, 2**31 - 1)),
            oob_score=True,
            bootstrap=True,
            n_jobs=-1,
        )
        model.fit(X_sample, y_sample, sample_weight=w_sample)
        bootstrap_scores.append(float(model.oob_score_))

    if bootstrap_scores:
        score_series = pd.Series(bootstrap_scores)
        rf_interval = (float(score_series.quantile(0.05)), float(score_series.quantile(0.95)))
        rf_bootstrap = {
            "mean": float(score_series.mean()),
            "median": float(score_series.median()),
            "p05": rf_interval[0],
            "p95": rf_interval[1],
            "std": float(score_series.std(ddof=1)),
        }
    else:
        rf_interval = None
        rf_bootstrap = {}

    return oob_r2, feature_importances, rf_bootstrap


def domain_diagnostics(
    df: pd.DataFrame,
    y: pd.Series,
    predictions: np.ndarray,
    weights: pd.Series,
    result: sm.regression.linear_model.RegressionResultsWrapper,
) -> Dict[str, Dict[str, float]]:
    """Assemble per-domain diagnostics, including Cook's distance."""

    influence = OLSInfluence(result)
    cooks_d = influence.cooks_distance[0]
    pred_series = pd.Series(predictions, index=y.index)

    diagnostics: Dict[str, Dict[str, float]] = {}

    for idx, row in df.iterrows():
        diagnostics[row["domain"]] = {
            "beta_observed": float(y.loc[idx]),
            "beta_predicted": float(pred_series.loc[idx]),
            "residual": float(y.loc[idx] - pred_series.loc[idx]),
            "abs_residual": float(abs(y.loc[idx] - pred_series.loc[idx])),
            "weight": float(weights.loc[idx]),
            "delta_aic": float(row.get("delta_aic_guard", np.nan)),
            "within_canonical_band": bool(row["within_canonical_band"]),
            "cooks_distance": float(cooks_d[idx]),
        }

    return diagnostics


def holm_correction(p_values: pd.Series) -> pd.Series:
    """Holm-Bonferroni correction implemented manually to avoid scipy dependency."""

    ordered = p_values.sort_values()
    m = len(p_values)
    adjusted = pd.Series(np.zeros(m), index=ordered.index, dtype=float)
    for i, (idx, p_val) in enumerate(ordered.items(), start=1):
        adjusted[idx] = min((m - i + 1) * p_val, 1.0)
    # Reorder back to original index
    return adjusted.reindex(p_values.index)


def build_coefficient_table(
    result: sm.regression.linear_model.RegressionResultsWrapper,
) -> pd.DataFrame:
    """Format coefficients, intervals, and Holm-corrected p-values."""

    params = result.params
    bse = result.bse
    tvalues = result.tvalues
    pvalues = result.pvalues
    conf_int = result.conf_int()

    df = pd.DataFrame(
        {
            "variable": params.index,
            "coefficient": params.values,
            "std_error": bse.values,
            "t_statistic": tvalues.values,
            "p_value": pvalues.values,
            "ci_lower": conf_int[0].values,
            "ci_upper": conf_int[1].values,
        }
    )
    df["p_value_corrected"] = holm_correction(df["p_value"])
    df["significant"] = df["p_value_corrected"] < 0.05
    return df


def run_pipeline(
    beta_csv: Path,
    covariates_csv: Path,
    output_dir: Path,
    n_bootstrap: int,
    rf_trees: int,
    rf_bootstrap: int,
    seed: Optional[int],
) -> None:
    """Execute the refreshed meta-regression workflow and persist artefacts."""

    df = load_and_prepare(beta_csv, covariates_csv)
    y, X_design, weights, X_plain = build_design_matrix(df)

    result = run_wls(y, X_design, weights)
    predictions = result.predict(X_design)

    bootstrap_summary, r2_summary = bootstrap_wls(
        y, X_design, weights, n_bootstrap=n_bootstrap, seed=seed
    )

    rf_oob, rf_importances, rf_bootstrap_summary = random_forest_diagnostics(
        X_plain, y, weights, n_estimators=rf_trees, n_bootstrap=rf_bootstrap, seed=seed
    )

    diagnostics = domain_diagnostics(df, y, predictions, weights, result)

    coefficient_table = build_coefficient_table(result)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    summary = RegressionSummary(
        timestamp=timestamp,
        r_squared=float(result.rsquared),
        adjusted_r_squared=float(result.rsquared_adj),
        aic=float(result.aic),
        bic=float(result.bic),
        rmse=float(np.sqrt(result.scale)),
        canonical_beta=CANONICAL_BETA,
        canonical_band=CANONICAL_BAND,
        beta_mean=float(df["beta"].mean()),
        beta_std=float(df["beta"].std(ddof=1)),
        beta_band_fraction=float(df["within_canonical_band"].mean()),
        delta_aic_guard_min=float(df["delta_aic_guard"].min()),
        bootstrap_r2_median=float(r2_summary["median"]),
        bootstrap_r2_interval=(float(r2_summary["p05"]), float(r2_summary["p95"])),
        random_forest_oob_r2=rf_oob,
        random_forest_bootstrap_interval=(
            float(rf_bootstrap_summary["p05"]),
            float(rf_bootstrap_summary["p95"]),
        )
        if rf_bootstrap_summary
        else None,
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    coeff_path = output_dir / f"beta_meta_regression_v2_coefficients_{timestamp}.csv"
    coeff_path.write_text(coefficient_table.to_csv(index=False), encoding="utf-8")

    summary_path = output_dir / f"beta_meta_regression_v2_summary_{timestamp}.json"
    summary_path.write_text(
        json.dumps(summary.to_dict(), indent=2) + "\n", encoding="utf-8"
    )

    diagnostics_path = output_dir / f"beta_meta_regression_v2_diagnostics_{timestamp}.json"
    diagnostics_payload = {
        "domains": diagnostics,
        "feature_importances": rf_importances,
    }
    diagnostics_path.write_text(
        json.dumps(diagnostics_payload, indent=2) + "\n", encoding="utf-8"
    )

    bootstrap_path = output_dir / f"beta_meta_regression_v2_bootstrap_{timestamp}.json"
    bootstrap_payload = {
        "wls_coefficients": bootstrap_summary,
        "wls_r2": r2_summary,
        "random_forest": rf_bootstrap_summary,
        "settings": {
            "n_bootstrap": n_bootstrap,
            "rf_bootstrap": rf_bootstrap,
            "rf_trees": rf_trees,
            "seed": seed,
        },
    }
    bootstrap_path.write_text(
        json.dumps(bootstrap_payload, indent=2) + "\n", encoding="utf-8"
    )

    print("✅ Meta-regression v2 completed")
    print(f"   WLS R² = {result.rsquared:.3f}, adj. R² = {result.rsquared_adj:.3f}")
    if rf_oob is not None:
        print(f"   Random Forest OOB R² = {rf_oob:.3f}")
    print(f"   Outputs written to: {output_dir}")
    print(f"   Summary: {summary_path}")
    print(f"   Coefficients: {coeff_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="UTAC meta-regression v2 pipeline")
    parser.add_argument("--beta-csv", type=Path, default=Path("data/derived/beta_estimates.csv"))
    parser.add_argument(
        "--covariates-csv", type=Path, default=Path("data/derived/domain_covariates.csv")
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("analysis/results"), help="Output directory"
    )
    parser.add_argument(
        "--bootstrap",
        type=int,
        default=1024,
        help="Number of bootstrap samples for WLS coefficients",
    )
    parser.add_argument(
        "--rf-trees",
        type=int,
        default=192,
        help="Number of trees for the Random Forest diagnostics",
    )
    parser.add_argument(
        "--rf-bootstrap",
        type=int,
        default=48,
        help="Number of bootstrap refits for the Random Forest OOB envelope",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_pipeline(
        beta_csv=args.beta_csv,
        covariates_csv=args.covariates_csv,
        output_dir=args.output_dir,
        n_bootstrap=args.bootstrap,
        rf_trees=args.rf_trees,
        rf_bootstrap=args.rf_bootstrap,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
