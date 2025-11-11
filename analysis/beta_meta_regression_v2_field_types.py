"""Enhanced meta-regression for UTAC v2.0 with Field Type Classification.

This module extends beta_meta_regression_v2.py by incorporating Field Type
classification as a categorical predictor. This addresses the heterogeneity
problem (R²=0.43) by recognizing that β-variance reflects fundamental
architectural differences between system types.

Key Innovation:
    • Field Types as categorical predictors (one-hot encoding)
    • Feature selection via Random Forest importance
    • Parsimonious model: Field Types + top continuous covariates
    • Goal: R² ≥ 0.70 (adjusted)

Field Types (from docs/field_type_classification_v1.1.md):
    I.   Strongly Coupled (β: 3.5-5.0)
    II.  High-Dimensional (β: 3.0-4.5)
    III. Weakly Coupled (β: 2.0-3.5)
    IV.  Physically Constrained (β: 4.5-6.0+)
    V.   Meta-Adaptive (β: 3.0-10.0+, variable)

Usage
-----
python analysis/beta_meta_regression_v2_field_types.py \
    --beta-csv data/derived/beta_estimates.csv \
    --covariates-csv data/derived/domain_covariates.csv \
    --output-dir analysis/results
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
    """Summary metrics for Field Type enhanced regression."""

    timestamp: str
    model_type: str
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
    field_type_anova_eta_squared: Optional[float]
    field_type_anova_p_value: Optional[float]
    top_features: List[str]

    def to_dict(self) -> Dict[str, object]:
        payload = asdict(self)
        payload["canonical_band"] = list(self.canonical_band)
        payload["bootstrap_r2_interval"] = list(self.bootstrap_r2_interval)
        return payload


def load_and_prepare(beta_path: Path, covar_path: Path) -> pd.DataFrame:
    """Load β estimates and enrich with Field Type dummies."""

    betas = pd.read_csv(beta_path)
    covars = pd.read_csv(covar_path)

    df = betas.merge(covars, on="domain", how="inner", validate="one_to_one")
    if df.empty:
        raise ValueError("No overlapping domains between beta and covariate tables")

    # Ensure field_type column exists
    if "field_type" not in df.columns:
        raise ValueError(
            "field_type column missing! Run with updated domain_covariates.csv"
        )

    # Create Field Type dummies (one-hot encoding)
    field_type_dummies = pd.get_dummies(df["field_type"], prefix="FT", drop_first=False)
    df = pd.concat([df, field_type_dummies], axis=1)

    # Derived features
    df["domain_family"] = df["domain"].str.split("_").str[0]
    df["beta_band_distance"] = df["beta"] - CANONICAL_BETA
    df["within_canonical_band"] = (
        (df["beta"] >= CANONICAL_BAND[0]) & (df["beta"] <= CANONICAL_BAND[1])
    )
    df["delta_aic_guard"] = df.get("delta_aic", np.nan)
    df["log_theta"] = np.log1p(df["theta"].clip(lower=1e-9))

    # Non-linear expansions
    df["coupling_sq"] = df["C_eff"] ** 2
    df["coupling_memory"] = df["C_eff"] * df["Memory"]

    return df


def field_type_anova(df: pd.DataFrame) -> Tuple[float, float]:
    """Compute one-way ANOVA for Field Type effect on β."""
    from scipy import stats

    field_types = df["field_type"].unique()
    groups = [df[df["field_type"] == ft]["beta"].values for ft in field_types]

    # One-way ANOVA
    F, p = stats.f_oneway(*groups)

    # Effect size (eta-squared)
    grand_mean = df["beta"].mean()
    ss_between = sum(
        len(df[df["field_type"] == ft]) * (df[df["field_type"] == ft]["beta"].mean() - grand_mean) ** 2
        for ft in field_types
    )
    ss_total = sum((df["beta"] - grand_mean) ** 2)
    eta_squared = ss_between / ss_total if ss_total > 0 else 0.0

    return eta_squared, p


def select_top_features(
    X: pd.DataFrame,
    y: pd.Series,
    weights: pd.Series,
    n_estimators: int,
    top_k: int,
    seed: Optional[int] = None,
) -> List[str]:
    """Use Random Forest to select top-k most important continuous features."""

    if X.empty:
        return []

    rf = RandomForestRegressor(
        n_estimators=n_estimators,
        random_state=seed,
        oob_score=True,
        bootstrap=True,
        n_jobs=-1,
    )
    rf.fit(X, y, sample_weight=weights)

    importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(
        ascending=False
    )

    return importances.head(top_k).index.tolist()


def build_design_matrix(
    df: pd.DataFrame,
    selected_continuous: List[str],
) -> Tuple[pd.Series, pd.DataFrame, pd.Series]:
    """Construct design matrix with Field Type dummies + selected continuous features."""

    y = df["beta"].astype(float)

    # Field Type dummies (all 5 types, drop_first=True for one reference category)
    field_type_cols = [col for col in df.columns if col.startswith("FT_")]

    # Use all field types except one as reference (drop first)
    if len(field_type_cols) > 1:
        field_type_cols = field_type_cols[1:]  # Drop first category as reference

    # Combine Field Types + selected continuous features
    feature_cols = field_type_cols + selected_continuous

    X = df[feature_cols].copy()

    # Ensure all columns are numeric
    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce")

    X = X.fillna(0.0).astype(float)

    # Weights
    weights = pd.Series(np.ones(len(df)), index=df.index, dtype=float)
    if "beta_ci_width" in df.columns:
        safe_width = df["beta_ci_width"].replace({0.0: np.nan})
        inv_var = 1.0 / (safe_width ** 2)
        inv_var.replace([np.inf, -np.inf], np.nan, inplace=True)
        if inv_var.notna().any():
            weights = inv_var.fillna(inv_var.median())

    weights = weights.astype(float)

    X_design = sm.add_constant(X, has_constant="add")

    return y, X_design, weights


def run_wls(
    y: pd.Series, X_design: pd.DataFrame, weights: pd.Series
) -> sm.regression.linear_model.RegressionResultsWrapper:
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
    """Bootstrap R² envelopes for the WLS model."""

    rng = default_rng(seed)
    r2_samples: List[float] = []

    for _ in range(n_bootstrap):
        indices = rng.integers(0, len(y), len(y))
        X_sample = X_design.iloc[indices]
        y_sample = y.iloc[indices]
        w_sample = weights.iloc[indices]
        result = sm.WLS(y_sample, X_sample, weights=w_sample).fit()
        r2_samples.append(float(result.rsquared))

    r2_series = pd.Series(r2_samples)
    r2_summary = {
        "mean": float(r2_series.mean()),
        "median": float(r2_series.median()),
        "p05": float(r2_series.quantile(0.05)),
        "p95": float(r2_series.quantile(0.95)),
        "std": float(r2_series.std(ddof=1)),
    }

    return {}, r2_summary  # No coefficient bootstrap for now


def random_forest_diagnostics(
    X: pd.DataFrame,
    y: pd.Series,
    weights: pd.Series,
    n_estimators: int,
    seed: Optional[int] = None,
) -> Tuple[Optional[float], Dict[str, float]]:
    """Train a Random Forest regressor for feature importance."""

    if X.empty:
        return None, {}

    rf = RandomForestRegressor(
        n_estimators=n_estimators,
        random_state=seed,
        oob_score=True,
        bootstrap=True,
        n_jobs=-1,
    )
    rf.fit(X, y, sample_weight=weights)
    oob_r2 = float(rf.oob_score_) if rf.oob_score else None

    feature_importances = {
        feature: float(importance)
        for feature, importance in zip(X.columns, rf.feature_importances_)
    }

    return oob_r2, feature_importances


def build_coefficient_table(
    result: sm.regression.linear_model.RegressionResultsWrapper,
) -> pd.DataFrame:
    """Format coefficients with confidence intervals."""

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
    df["significant"] = df["p_value"] < 0.05
    return df


def run_pipeline(
    beta_csv: Path,
    covariates_csv: Path,
    output_dir: Path,
    n_bootstrap: int,
    rf_trees: int,
    top_features: int,
    seed: Optional[int],
) -> None:
    """Execute Field Type enhanced meta-regression workflow."""

    df = load_and_prepare(beta_csv, covariates_csv)

    # Field Type ANOVA
    eta_squared, anova_p = field_type_anova(df)
    print(f"✅ Field Type ANOVA: η²={eta_squared:.3f}, p={anova_p:.4f}")

    # Feature selection on continuous features only
    continuous_features = ["C_eff", "D_eff", "SNR", "Memory", "Theta_dot", "log_theta", "coupling_sq", "coupling_memory"]
    X_continuous = df[continuous_features].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    y = df["beta"]
    weights = pd.Series(np.ones(len(df)), index=df.index, dtype=float)

    selected_features = select_top_features(
        X_continuous, y, weights, n_estimators=rf_trees, top_k=top_features, seed=seed
    )
    print(f"✅ Top-{top_features} features selected: {selected_features}")

    # Build design matrix with Field Types + selected features
    y, X_design, weights = build_design_matrix(df, selected_features)

    # WLS regression
    result = run_wls(y, X_design, weights)
    print(f"✅ WLS R²={result.rsquared:.3f}, adj. R²={result.rsquared_adj:.3f}")

    # Bootstrap
    _, r2_summary = bootstrap_wls(y, X_design, weights, n_bootstrap=n_bootstrap, seed=seed)

    # Random Forest on full feature set (Field Types + continuous)
    X_full = X_design.drop(columns=["const"])
    rf_oob, rf_importances = random_forest_diagnostics(X_full, y, weights, n_estimators=rf_trees, seed=seed)
    if rf_oob:
        print(f"✅ Random Forest OOB R²={rf_oob:.3f}")

    # Coefficient table
    coefficient_table = build_coefficient_table(result)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    summary = RegressionSummary(
        timestamp=timestamp,
        model_type="WLS_with_FieldTypes",
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
        field_type_anova_eta_squared=float(eta_squared),
        field_type_anova_p_value=float(anova_p),
        top_features=selected_features,
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    # Write outputs
    summary_path = output_dir / f"beta_meta_regression_v2_latest.json"
    summary_path.write_text(
        json.dumps(summary.to_dict(), indent=2) + "\n", encoding="utf-8"
    )

    coeff_path = output_dir / f"beta_meta_regression_v2_coefficients_{timestamp}.csv"
    coeff_path.write_text(coefficient_table.to_csv(index=False), encoding="utf-8")

    diagnostics_path = output_dir / f"beta_meta_regression_v2_diagnostics_{timestamp}.json"
    diagnostics_payload = {
        "field_type_anova": {
            "eta_squared": float(eta_squared),
            "p_value": float(anova_p),
        },
        "feature_importances": rf_importances,
        "selected_features": selected_features,
    }
    diagnostics_path.write_text(
        json.dumps(diagnostics_payload, indent=2) + "\n", encoding="utf-8"
    )

    print(f"\n✅ Meta-regression v2 (Field Types) completed!")
    print(f"   Model: Field Types + Top-{top_features} continuous features")
    print(f"   WLS R² = {result.rsquared:.3f}, adj. R² = {result.rsquared_adj:.3f}")
    print(f"   Field Type ANOVA: η²={eta_squared:.3f}, p={anova_p:.4f}")
    if rf_oob is not None:
        print(f"   Random Forest OOB R² = {rf_oob:.3f}")
    print(f"   Outputs: {output_dir}")
    print(f"   Summary: {summary_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="UTAC meta-regression v2 with Field Types"
    )
    parser.add_argument(
        "--beta-csv", type=Path, default=Path("data/derived/beta_estimates.csv")
    )
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
        help="Number of bootstrap samples",
    )
    parser.add_argument(
        "--rf-trees",
        type=int,
        default=192,
        help="Number of trees for Random Forest",
    )
    parser.add_argument(
        "--top-features",
        type=int,
        default=3,
        help="Number of top continuous features to select",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed",
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
        top_features=args.top_features,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
