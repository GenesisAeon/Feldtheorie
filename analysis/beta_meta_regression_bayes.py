"""Hierarchical Bayesian meta-regression for β-heterogeneity across domains.

This module implements a Bayesian hierarchical model to explain how logistic
steepness (β) varies across domains (biology, climate, cognition, AI) through
domain-level random effects and information borrowing.

Theoretical Framework:
    • Bio domain: β ≈ 7.4 (body-coupled, metabolic)
    • Climate domain: β ≈ 11.0 (surface-bound, holographic)
    • Cognition domain: β ≈ 4.5 (volume-integrated)
    • AI/Symbolic domain: β ≈ 1.0 (decoupled, abstract)

Hierarchical Structure:
    • Level 1: β_ij ~ Normal(μ_j + X_ij·γ, σ_ε²)
        Individual observations within domain j
    • Level 2: μ_j ~ Normal(μ_global, σ_μ²)
        Domain-level means with random effects
    • Level 3: μ_global ~ Normal(Φ³, σ_global²)
        Global mean centered on golden ratio Φ³ ≈ 4.236

Information Borrowing:
    Domains with few observations "borrow" information from the global
    distribution and other domains through hierarchical shrinkage.

References:
    - V6ToDorefresh.md Priority 11 (Beta-Bayes)
    - FinalyzeVorschlägeGemini.txt:36-39 (Bayes spec)
    - activation_gaps_tau_star.md (τ*-integration)
    - Gelman & Hill (2007): Data Analysis Using Regression and Multilevel Models

Usage:
    python analysis/beta_meta_regression_bayes.py \\
        --beta-csv data/derived/beta_estimates.csv \\
        --covariates-csv data/derived/domain_covariates.csv \\
        --output-dir analysis/results/bayes \\
        --n-samples 2000 \\
        --n-tune 1000
"""

from __future__ import annotations

import argparse
import json
import warnings
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Try PyMC import with fallback
try:
    import arviz as az
    import pymc as pm

    PYMC_AVAILABLE = True
except ImportError:
    PYMC_AVAILABLE = False
    warnings.warn("PyMC not available. Install with: pip install pymc arviz")

# Type-6 constants
try:
    from models.utac_type6_implosive import BETA_FIXPOINT_PHI3, PHI

    CANONICAL_BETA = float(BETA_FIXPOINT_PHI3)  # Φ³ ≈ 4.236
except ImportError:
    PHI = 1.618034
    CANONICAL_BETA = 4.236

# Domain expected values (empirical priors)
DOMAIN_PRIORS = {
    "biology": {"mean": 7.4, "sd": 1.5},
    "climate": {"mean": 11.0, "sd": 2.0},
    "cognition": {"mean": 4.5, "sd": 1.0},
    "ai_symbolic": {"mean": 1.0, "sd": 0.5},
    "default": {"mean": CANONICAL_BETA, "sd": 3.0},
}


@dataclass
class BayesianResults:
    """Container for Bayesian hierarchical model results."""

    timestamp: str
    n_samples: int
    n_tune: int
    n_chains: int

    # Global parameters
    mu_global_mean: float
    mu_global_hdi_low: float
    mu_global_hdi_high: float
    sigma_global: float

    # Domain-level random effects
    domain_effects: dict[str, dict[str, float]]

    # Covariate effects (if any)
    covariate_effects: dict[str, dict[str, float]]

    # Model diagnostics
    r_hat_max: float
    ess_bulk_min: float
    ess_tail_min: float
    divergences: int

    # Posterior predictive checks
    ppc_p_value: float
    ppc_rmse: float

    # Information borrowing metrics
    shrinkage_factors: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_data(beta_csv: Path, covariates_csv: Path) -> pd.DataFrame:
    """Load and merge β estimates with covariates."""
    betas = pd.read_csv(beta_csv)

    if covariates_csv.exists():
        covariates = pd.read_csv(covariates_csv)
        df = betas.merge(covariates, on="domain", how="left")
    else:
        df = betas.copy()

    # Ensure required columns
    if "domain" not in df.columns:
        raise ValueError("beta_csv must contain 'domain' column")
    if "beta" not in df.columns and "beta_estimate" not in df.columns:
        raise ValueError("beta_csv must contain 'beta' or 'beta_estimate' column")

    # Standardize column names
    if "beta_estimate" in df.columns and "beta" not in df.columns:
        df["beta"] = df["beta_estimate"]

    # Map domains to categories
    df["domain_category"] = df["domain"].apply(categorize_domain)

    return df


def categorize_domain(domain: str) -> str:
    """Categorize domain into broad categories for hierarchical effects."""
    domain_lower = str(domain).lower()

    if any(kw in domain_lower for kw in ["bio", "metabol", "kleiber", "allometr"]):
        return "biology"
    elif any(kw in domain_lower for kw in ["climat", "cosmic", "astroph", "geo"]):
        return "climate"
    elif any(kw in domain_lower for kw in ["cognit", "conscious", "neural", "brain"]):
        return "cognition"
    elif any(kw in domain_lower for kw in ["ai", "llm", "gpt", "symbolic", "algorithm"]):
        return "ai_symbolic"
    else:
        return "default"


def compute_vif(X: pd.DataFrame) -> pd.DataFrame:
    """Compute Variance Inflation Factors for multicollinearity detection."""
    from sklearn.linear_model import LinearRegression

    vif_data = pd.DataFrame()
    vif_data["feature"] = X.columns
    vif_values = []

    for i, col in enumerate(X.columns):
        # Regress column i on all other columns
        X_others = X.drop(columns=[col])
        y = X[col]

        if X_others.shape[1] == 0:
            vif_values.append(1.0)
            continue

        lr = LinearRegression()
        lr.fit(X_others, y)
        r_squared = lr.score(X_others, y)

        # VIF = 1 / (1 - R²)
        vif = 1 / (1 - r_squared) if r_squared < 0.9999 else np.inf
        vif_values.append(vif)

    vif_data["VIF"] = vif_values
    return vif_data


def build_pymc_model(
    df: pd.DataFrame, covariates: list[str] | None = None
) -> tuple[pm.Model, dict[str, Any]]:
    """Build hierarchical Bayesian model with PyMC."""
    if not PYMC_AVAILABLE:
        raise ImportError("PyMC is required. Install with: pip install pymc")

    # Prepare data
    domains = df["domain_category"].unique()
    domain_idx = pd.Categorical(df["domain_category"]).codes
    n_domains = len(domains)

    y = df["beta"].values
    n_obs = len(y)

    # Prepare covariates if provided
    if covariates:
        X = df[covariates].values
        n_covariates = X.shape[1]
    else:
        X = None
        n_covariates = 0

    with pm.Model() as model:
        # === Level 3: Global hyperpriors ===
        # Global mean centered on Φ³ ≈ 4.236
        mu_global = pm.Normal("mu_global", mu=CANONICAL_BETA, sigma=3.0)

        # Global heterogeneity
        sigma_global = pm.HalfNormal("sigma_global", sigma=2.0)

        # === Level 2: Domain-level random effects ===
        # Domain means drawn from global distribution
        mu_domain_raw = pm.Normal("mu_domain_raw", mu=0, sigma=1, shape=n_domains)
        mu_domain = pm.Deterministic("mu_domain", mu_global + sigma_global * mu_domain_raw)

        # Domain-specific variance
        sigma_domain = pm.HalfNormal("sigma_domain", sigma=1.5, shape=n_domains)

        # === Covariate effects (if any) ===
        if X is not None:
            gamma = pm.Normal("gamma", mu=0, sigma=2.0, shape=n_covariates)
            X_effect = pm.math.dot(X, gamma)
        else:
            X_effect = 0

        # === Level 1: Observations ===
        # Individual β values within domains
        beta_expected = mu_domain[domain_idx] + X_effect

        # Observation noise
        sigma_obs = pm.HalfNormal("sigma_obs", sigma=1.0)

        # Likelihood
        beta_obs = pm.Normal("beta_obs", mu=beta_expected, sigma=sigma_obs, observed=y)

        # === Posterior predictive ===
        beta_pred = pm.Normal("beta_pred", mu=beta_expected, sigma=sigma_obs, shape=n_obs)

    data_dict = {
        "domains": domains,
        "domain_idx": domain_idx,
        "y": y,
        "X": X,
        "covariates": covariates,
    }

    return model, data_dict


def run_mcmc_sampling(
    model: pm.Model,
    n_samples: int = 2000,
    n_tune: int = 1000,
    n_chains: int = 4,
    random_seed: int = 42,
) -> az.InferenceData:
    """Run MCMC sampling with NUTS."""
    if not PYMC_AVAILABLE:
        raise ImportError("PyMC is required")

    with model:
        # Sample using NUTS (No U-Turn Sampler)
        trace = pm.sample(
            draws=n_samples,
            tune=n_tune,
            chains=n_chains,
            random_seed=random_seed,
            target_accept=0.95,
            return_inferencedata=True,
        )

        # Sample posterior predictive
        ppc = pm.sample_posterior_predictive(trace, random_seed=random_seed)

        # Combine traces
        trace.extend(ppc)

    return trace


def compute_diagnostics(trace: az.InferenceData) -> dict[str, float]:
    """Compute MCMC diagnostics (R-hat, ESS)."""
    summary = az.summary(trace, kind="diagnostics")

    diagnostics = {
        "r_hat_max": float(summary["r_hat"].max()),
        "ess_bulk_min": float(summary["ess_bulk"].min()),
        "ess_tail_min": float(summary["ess_tail"].min()),
    }

    # Check for divergences
    divergences = int(trace.sample_stats["diverging"].sum())
    diagnostics["divergences"] = divergences

    return diagnostics


def posterior_predictive_checks(trace: az.InferenceData, y_obs: np.ndarray) -> dict[str, float]:
    """Run posterior predictive checks."""
    # Extract posterior predictive samples
    y_pred = trace.posterior_predictive["beta_pred"].values.reshape(-1, len(y_obs))

    # Compute predictive p-value
    # P(T(y_rep) >= T(y_obs))
    obs_mean = np.mean(y_obs)
    pred_means = np.mean(y_pred, axis=1)
    p_value = float(np.mean(pred_means >= obs_mean))

    # RMSE between observed and posterior mean
    posterior_mean = np.mean(y_pred, axis=0)
    rmse = float(np.sqrt(np.mean((y_obs - posterior_mean) ** 2)))

    return {"ppc_p_value": p_value, "ppc_rmse": rmse}


def compute_shrinkage(
    trace: az.InferenceData, df: pd.DataFrame, data_dict: dict[str, Any]
) -> dict[str, float]:
    """Compute shrinkage factors (information borrowing strength)."""
    # Extract domain effects
    mu_domain = trace.posterior["mu_domain"].values.mean(axis=(0, 1))
    mu_global = float(trace.posterior["mu_global"].values.mean())

    domains = data_dict["domains"]
    domain_idx = data_dict["domain_idx"]

    shrinkage = {}
    for i, domain in enumerate(domains):
        # Observed domain mean (no pooling)
        mask = domain_idx == i
        if not mask.any():
            continue
        obs_mean = df.loc[mask, "beta"].mean()

        # Hierarchical estimate (partial pooling)
        hier_mean = mu_domain[i]

        # Shrinkage toward global mean
        if abs(obs_mean - mu_global) > 1e-6:
            shrink = abs(hier_mean - obs_mean) / abs(obs_mean - mu_global)
        else:
            shrink = 0.0

        shrinkage[str(domain)] = float(np.clip(shrink, 0, 1))

    return shrinkage


def extract_results(
    trace: az.InferenceData,
    data_dict: dict[str, Any],
    df: pd.DataFrame,
    n_samples: int,
    n_tune: int,
    n_chains: int,
) -> BayesianResults:
    """Extract and summarize Bayesian results."""
    summary = az.summary(trace, hdi_prob=0.94)

    # Global parameters
    mu_global_stats = summary.loc["mu_global"]
    mu_global_mean = float(mu_global_stats["mean"])
    mu_global_hdi = az.hdi(trace, hdi_prob=0.94)["mu_global"].values
    mu_global_hdi_low = float(mu_global_hdi[0])
    mu_global_hdi_high = float(mu_global_hdi[1])

    sigma_global = float(summary.loc["sigma_global", "mean"])

    # Domain effects
    domains = data_dict["domains"]
    domain_effects = {}
    for i, domain in enumerate(domains):
        mu_domain_stats = summary.loc[f"mu_domain[{i}]"]
        mu_domain_hdi = az.hdi(trace, hdi_prob=0.94)["mu_domain"].values[i]

        domain_effects[str(domain)] = {
            "mean": float(mu_domain_stats["mean"]),
            "sd": float(mu_domain_stats["sd"]),
            "hdi_low": float(mu_domain_hdi[0]),
            "hdi_high": float(mu_domain_hdi[1]),
        }

    # Covariate effects
    covariate_effects = {}
    if data_dict["covariates"]:
        for i, cov in enumerate(data_dict["covariates"]):
            gamma_stats = summary.loc[f"gamma[{i}]"]
            covariate_effects[cov] = {
                "mean": float(gamma_stats["mean"]),
                "sd": float(gamma_stats["sd"]),
            }

    # Diagnostics
    diagnostics = compute_diagnostics(trace)

    # Posterior predictive checks
    ppc = posterior_predictive_checks(trace, data_dict["y"])

    # Shrinkage
    shrinkage = compute_shrinkage(trace, df, data_dict)

    return BayesianResults(
        timestamp=datetime.now(timezone.utc).isoformat(),
        n_samples=n_samples,
        n_tune=n_tune,
        n_chains=n_chains,
        mu_global_mean=mu_global_mean,
        mu_global_hdi_low=mu_global_hdi_low,
        mu_global_hdi_high=mu_global_hdi_high,
        sigma_global=sigma_global,
        domain_effects=domain_effects,
        covariate_effects=covariate_effects,
        r_hat_max=diagnostics["r_hat_max"],
        ess_bulk_min=diagnostics["ess_bulk_min"],
        ess_tail_min=diagnostics["ess_tail_min"],
        divergences=diagnostics["divergences"],
        ppc_p_value=ppc["ppc_p_value"],
        ppc_rmse=ppc["ppc_rmse"],
        shrinkage_factors=shrinkage,
    )


def create_visualizations(
    trace: az.InferenceData, results: BayesianResults, output_dir: Path
) -> None:
    """Create diagnostic and summary visualizations."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Trace plots
    fig, axes = plt.subplots(3, 2, figsize=(12, 10))
    az.plot_trace(
        trace, var_names=["mu_global", "sigma_global", "mu_domain"], compact=False, axes=axes
    )
    plt.tight_layout()
    plt.savefig(output_dir / "trace_plots.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Forest plot (domain effects)
    fig, ax = plt.subplots(figsize=(10, 6))
    az.plot_forest(trace, var_names=["mu_domain"], combined=True, hdi_prob=0.94, ax=ax)
    ax.set_title("Domain-Level β Estimates (94% HDI)")
    ax.set_xlabel("β (Logistic Steepness)")
    plt.tight_layout()
    plt.savefig(output_dir / "forest_plot_domains.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Posterior predictive check
    fig, ax = plt.subplots(figsize=(8, 6))
    az.plot_ppc(trace, ax=ax)
    ax.set_title("Posterior Predictive Check")
    ax.set_xlabel("β (Observed vs Predicted)")
    plt.tight_layout()
    plt.savefig(output_dir / "ppc_plot.png", dpi=150, bbox_inches="tight")
    plt.close()

    print(f"📊 Visualizations saved to {output_dir}/")


def run_pipeline(
    beta_csv: Path,
    covariates_csv: Path,
    output_dir: Path,
    n_samples: int = 2000,
    n_tune: int = 1000,
    n_chains: int = 4,
    covariates: list[str] | None = None,
    random_seed: int = 42,
) -> None:
    """Run full Bayesian hierarchical analysis pipeline."""
    if not PYMC_AVAILABLE:
        print("❌ PyMC not available. Install with: pip install pymc arviz")
        return

    print("🎲 Starting Bayesian Hierarchical Meta-Regression")
    print(f"   β-data: {beta_csv}")
    print(f"   Covariates: {covariates_csv}")
    print(f"   Output: {output_dir}")
    print()

    # Load data
    print("📊 Loading data...")
    df = load_data(beta_csv, covariates_csv)
    print(f"   {len(df)} observations across {df['domain_category'].nunique()} domain categories")
    print()

    # VIF check if covariates provided
    if covariates:
        print("🔍 Checking multicollinearity (VIF)...")
        vif_df = compute_vif(df[covariates])
        print(vif_df)
        if (vif_df["VIF"] > 10).any():
            warnings.warn("High VIF detected (>10). Consider removing collinear covariates.")
        print()

    # Build model
    print("🏗️  Building hierarchical model...")
    model, data_dict = build_pymc_model(df, covariates)
    print(model)
    print()

    # Sample
    print(f"🎯 Running MCMC (chains={n_chains}, samples={n_samples}, tune={n_tune})...")
    trace = run_mcmc_sampling(
        model, n_samples=n_samples, n_tune=n_tune, n_chains=n_chains, random_seed=random_seed
    )
    print("✅ Sampling complete")
    print()

    # Extract results
    print("📈 Extracting results...")
    results = extract_results(trace, data_dict, df, n_samples, n_tune, n_chains)
    print()

    # Diagnostics
    print("🔬 Diagnostics:")
    print(f"   R-hat max: {results.r_hat_max:.4f} (should be < 1.01)")
    print(f"   ESS bulk min: {results.ess_bulk_min:.0f} (should be > 400)")
    print(f"   ESS tail min: {results.ess_tail_min:.0f} (should be > 400)")
    print(f"   Divergences: {results.divergences} (should be 0)")
    print()

    # Results summary
    print("📊 Results Summary:")
    print(
        f"   μ_global: {results.mu_global_mean:.3f} [{results.mu_global_hdi_low:.3f}, {results.mu_global_hdi_high:.3f}]"
    )
    print(f"   σ_global: {results.sigma_global:.3f}")
    print()
    print("   Domain Effects:")
    for domain, effects in results.domain_effects.items():
        print(
            f"      {domain:12s}: {effects['mean']:.3f} [{effects['hdi_low']:.3f}, {effects['hdi_high']:.3f}]"
        )
    print()

    if results.shrinkage_factors:
        print("   Information Borrowing (Shrinkage):")
        for domain, shrink in results.shrinkage_factors.items():
            print(f"      {domain:12s}: {shrink:.1%}")
        print()

    print(f"   PPC RMSE: {results.ppc_rmse:.3f}")
    print(f"   PPC p-value: {results.ppc_p_value:.3f}")
    print()

    # Save results
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results_path = output_dir / f"bayes_results_{timestamp}.json"
    with results_path.open("w") as f:
        json.dump(results.to_dict(), f, indent=2)
    print(f"💾 Results saved: {results_path}")

    # Save trace
    trace_path = output_dir / f"bayes_trace_{timestamp}.nc"
    trace.to_netcdf(trace_path)
    print(f"💾 Trace saved: {trace_path}")

    # Create visualizations
    print("🎨 Creating visualizations...")
    create_visualizations(trace, results, output_dir)
    print()

    print("✅ Bayesian analysis complete!")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Hierarchical Bayesian β meta-regression with PyMC"
    )
    parser.add_argument(
        "--beta-csv",
        type=Path,
        default=Path("data/derived/beta_estimates.csv"),
        help='CSV with β estimates (must have "domain" and "beta" columns)',
    )
    parser.add_argument(
        "--covariates-csv",
        type=Path,
        default=Path("data/derived/domain_covariates.csv"),
        help="CSV with domain covariates",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("analysis/results/bayes"),
        help="Output directory for results and plots",
    )
    parser.add_argument(
        "--n-samples", type=int, default=2000, help="Number of MCMC samples per chain"
    )
    parser.add_argument("--n-tune", type=int, default=1000, help="Number of tuning/burn-in samples")
    parser.add_argument("--n-chains", type=int, default=4, help="Number of MCMC chains")
    parser.add_argument("--covariates", nargs="*", help="List of covariate column names to include")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not PYMC_AVAILABLE:
        print("❌ PyMC is not installed.")
        print("   Install with: pip install pymc arviz")
        print("   Or: conda install -c conda-forge pymc")
        return

    run_pipeline(
        beta_csv=args.beta_csv,
        covariates_csv=args.covariates_csv,
        output_dir=args.output_dir,
        n_samples=args.n_samples,
        n_tune=args.n_tune,
        n_chains=args.n_chains,
        covariates=args.covariates,
        random_seed=args.seed,
    )


if __name__ == "__main__":
    main()
