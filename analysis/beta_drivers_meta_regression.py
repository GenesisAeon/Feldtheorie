"""
Meta-regression analysis of β values across system domains.

This module performs weighted meta-regression to explain β heterogeneity
as a function of system properties: coupling strength (C_eff), dimensionality (D_eff),
signal-to-noise ratio (SNR), memory effects (M), and threshold dynamics (Theta_dot).

Author: Johann Römer et al.
License: MIT
DOI: 10.5281/zenodo.17472834
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from pathlib import Path
import json
import argparse
from typing import Tuple, Dict
import warnings


def load_data(
    beta_path: str = "data/derived/beta_estimates.csv",
    covar_path: str = "data/derived/domain_covariates.csv"
) -> pd.DataFrame:
    """
    Load β estimates and domain covariates.

    Parameters
    ----------
    beta_path : str
        Path to β estimates CSV file
    covar_path : str
        Path to domain covariates CSV file

    Returns
    -------
    DataFrame
        Merged data with β values and covariates
    """
    try:
        betas = pd.read_csv(beta_path)
        covars = pd.read_csv(covar_path)

        # Merge on domain
        df = betas.merge(covars, on="domain", how="inner")

        print(f"✅ Loaded {len(df)} domain records")
        print(f"   β range: [{df['beta'].min():.2f}, {df['beta'].max():.2f}]")

        return df

    except FileNotFoundError as e:
        print(f"❌ Data files not found: {e}")
        print("\nPlease ensure the following files exist:")
        print(f"  - {beta_path}")
        print(f"  - {covar_path}")
        print("\nSee data/derived/README.md for template generation.")
        raise


def prepare_regression_data(df: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame, pd.Series]:
    """
    Prepare data for weighted least squares regression.

    Parameters
    ----------
    df : DataFrame
        Merged β and covariate data

    Returns
    -------
    y : Series
        Dependent variable (β values)
    X : DataFrame
        Independent variables (covariates)
    weights : Series
        Regression weights (inverse variance)
    """
    # Dependent variable
    y = df["beta"]

    # Independent variables (covariates)
    covariate_cols = ["C_eff", "D_eff", "SNR", "Memory", "Theta_dot"]

    # Check which covariates are available
    available_covars = [col for col in covariate_cols if col in df.columns]
    missing_covars = [col for col in covariate_cols if col not in df.columns]

    if missing_covars:
        warnings.warn(
            f"Missing covariates: {missing_covars}. "
            f"Regression will use only: {available_covars}"
        )

    X = df[available_covars]

    # Calculate weights from confidence interval widths
    # If beta_ci_width is not available, use uniform weights
    if "beta_ci_width" in df.columns:
        # Weight by inverse variance (approximated from CI width)
        weights = 1 / df["beta_ci_width"].clip(lower=0.1)
    else:
        weights = pd.Series(np.ones(len(df)), index=df.index)
        warnings.warn("No beta_ci_width column found. Using uniform weights.")

    return y, X, weights


def meta_regression(
    y: pd.Series,
    X: pd.DataFrame,
    weights: pd.Series
) -> Tuple[pd.DataFrame, sm.regression.linear_model.RegressionResultsWrapper]:
    """
    Perform weighted least squares meta-regression.

    Parameters
    ----------
    y : Series
        Dependent variable (β)
    X : DataFrame
        Independent variables (covariates)
    weights : Series
        Regression weights

    Returns
    -------
    results_df : DataFrame
        Summary table with coefficients, p-values, and corrected p-values
    model : RegressionResultsWrapper
        Full statsmodels regression results
    """
    # Add constant term
    X_with_const = sm.add_constant(X)

    # Weighted least squares
    model = sm.WLS(y, X_with_const, weights=weights)
    result = model.fit()

    # Extract results
    df_results = pd.DataFrame({
        "variable": result.params.index,
        "coefficient": result.params.values,
        "std_error": result.bse.values,
        "t_statistic": result.tvalues.values,
        "p_value": result.pvalues.values,
        "ci_lower": result.conf_int()[0].values,
        "ci_upper": result.conf_int()[1].values
    })

    # Multiple testing correction (Holm-Bonferroni)
    _, p_corrected, _, _ = multipletests(
        df_results["p_value"].values,
        method="holm",
        alpha=0.05
    )
    df_results["p_value_corrected"] = p_corrected

    # Mark significance
    df_results["significant"] = df_results["p_value_corrected"] < 0.05

    return df_results, result


def generate_report(
    df_results: pd.DataFrame,
    model_result,
    output_dir: str = "analysis/results"
) -> Dict:
    """
    Generate comprehensive regression report.

    Parameters
    ----------
    df_results : DataFrame
        Regression results table
    model_result : RegressionResultsWrapper
        Full model results
    output_dir : str
        Output directory

    Returns
    -------
    Dict
        Summary statistics
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save detailed results
    results_csv = output_path / "beta_meta_regression_results.csv"
    df_results.to_csv(results_csv, index=False)
    print(f"✅ Regression results saved to {results_csv}")

    # Model summary
    summary_dict = {
        "model": "Weighted Least Squares Meta-Regression",
        "n_observations": int(model_result.nobs),
        "n_covariates": len(df_results) - 1,  # Exclude intercept
        "r_squared": float(model_result.rsquared),
        "adj_r_squared": float(model_result.rsquared_adj),
        "f_statistic": float(model_result.fvalue),
        "f_pvalue": float(model_result.f_pvalue),
        "aic": float(model_result.aic),
        "bic": float(model_result.bic),
        "significant_predictors": df_results[df_results["significant"]]["variable"].tolist()
    }

    # Save summary
    summary_json = output_path / "beta_meta_regression_summary.json"
    with open(summary_json, 'w') as f:
        json.dump(summary_dict, f, indent=2)
    print(f"✅ Summary saved to {summary_json}")

    # Save model object for later use
    model_pkl = output_path / "beta_meta_model.pkl"
    model_result.save(str(model_pkl))
    print(f"✅ Model object saved to {model_pkl}")

    return summary_dict


def print_results(df_results: pd.DataFrame, summary: Dict):
    """Print formatted results to console."""
    print("\n" + "="*70)
    print("META-REGRESSION RESULTS: β-DRIVER ANALYSIS")
    print("="*70)

    print(f"\nModel: {summary['model']}")
    print(f"Observations: {summary['n_observations']}")
    print(f"R²: {summary['r_squared']:.4f}")
    print(f"Adjusted R²: {summary['adj_r_squared']:.4f}")
    print(f"F-statistic: {summary['f_statistic']:.2f} (p={summary['f_pvalue']:.4e})")

    print("\n" + "-"*70)
    print("COEFFICIENT ESTIMATES")
    print("-"*70)

    for _, row in df_results.iterrows():
        sig_marker = "***" if row["significant"] else "   "
        print(f"{row['variable']:15s} {sig_marker} "
              f"β = {row['coefficient']:7.4f} ± {row['std_error']:.4f}  "
              f"[{row['ci_lower']:.4f}, {row['ci_upper']:.4f}]  "
              f"p = {row['p_value_corrected']:.4e}")

    print("\n*** = Significant after Holm-Bonferroni correction (α=0.05)")

    if summary['significant_predictors']:
        print(f"\n✅ Significant predictors: {', '.join(summary['significant_predictors'])}")
    else:
        print("\n⚠️  No significant predictors found at α=0.05")

    print("\n" + "="*70)


def main():
    """Command-line interface for β-driver meta-regression."""
    parser = argparse.ArgumentParser(
        description="Meta-regression analysis of β heterogeneity across domains"
    )
    parser.add_argument(
        '--beta-data',
        type=str,
        default='data/derived/beta_estimates.csv',
        help='Path to β estimates CSV'
    )
    parser.add_argument(
        '--covariate-data',
        type=str,
        default='data/derived/domain_covariates.csv',
        help='Path to domain covariates CSV'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='analysis/results',
        help='Output directory for results'
    )

    args = parser.parse_args()

    print("="*70)
    print("β-DRIVER META-REGRESSION ANALYSIS")
    print("="*70)

    # Load data
    df = load_data(args.beta_data, args.covariate_data)

    # Prepare regression data
    y, X, weights = prepare_regression_data(df)

    # Run meta-regression
    print(f"\nRunning weighted least squares regression...")
    print(f"  Predictors: {', '.join(X.columns)}")
    df_results, model_result = meta_regression(y, X, weights)

    # Generate report
    summary = generate_report(df_results, model_result, args.output)

    # Print results
    print_results(df_results, summary)

    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
