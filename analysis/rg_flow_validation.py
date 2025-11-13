#!/usr/bin/env python3
"""RG Flow Validation Against LLM β-Trajectories

Validates RG flow simulator against empirical β evolution from LLM training.
Tests all 5 flow variants and identifies best-fit model.

Usage:
    python analysis/rg_flow_validation.py
    python analysis/rg_flow_validation.py --variant linear_phi --save-plots

Input:
    data/implosion/llm_runs_beta.csv (61 epochs, 6 models)

Output:
    analysis/results/rg_flow_validation.json (metrics)
    analysis/results/rg_flow_validation_{variant}.png (plots)

Metrics:
    - R² (fit quality)
    - RMSE (trajectory error)
    - Φ³ convergence score
    - Fixed point analysis

Author: Claude Code + Johann B. Römer
Date: 2025-11-12
Version: 1.0.0
"""

import argparse
import json
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr

# Import RG simulator
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.rg_flow_simulator import (
    FlowVariant,
    RGFlowConfig,
    RGFlowSimulator,
    compare_to_phi_ladder,
    phi_convergence_score,
)
from models.utac_type6_implosive import PHI, BETA_FIXPOINT_PHI3, BETA_STEPS


# ═══════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════


def load_llm_trajectories() -> dict[str, pd.DataFrame]:
    """Load LLM β-trajectories from CSV.

    Returns
    -------
    data : dict[str, DataFrame]
        Keys: model names, Values: DataFrames with columns [epoch, beta]
    """
    data_path = Path("data/implosion/llm_runs_beta.csv")

    if not data_path.exists():
        raise FileNotFoundError(f"LLM data not found: {data_path}")

    df = pd.read_csv(data_path)

    # Check columns - adjust for actual CSV format
    if "run_id" in df.columns and "training_step" in df.columns and "beta_estimate" in df.columns:
        # Rename to expected format
        df = df.rename(columns={
            "run_id": "model",
            "training_step": "epoch",
            "beta_estimate": "beta",
        })
    elif not all(col in df.columns for col in ["model", "epoch", "beta"]):
        raise ValueError(f"Expected columns: model, epoch, beta (or run_id, training_step, beta_estimate). Got: {df.columns}")

    # Split by model
    trajectories = {}
    for model_name in df["model"].unique():
        model_df = df[df["model"] == model_name].copy()
        model_df = model_df.sort_values("epoch")
        # Reset epoch to start from 0
        model_df["epoch"] = range(len(model_df))
        trajectories[model_name] = model_df

    return trajectories


# ═══════════════════════════════════════════════════════════════
# RG FLOW FITTING
# ═══════════════════════════════════════════════════════════════


def fit_rg_flow(
    empirical_beta: np.ndarray,
    empirical_epochs: np.ndarray,
    variant: FlowVariant,
    config_overrides: Optional[dict] = None,
) -> dict:
    """Fit RG flow to empirical β trajectory.

    Parameters
    ----------
    empirical_beta : ndarray
        Observed β values
    empirical_epochs : ndarray
        Epoch indices (proxy for scale λ)
    variant : FlowVariant
        RG flow variant to test
    config_overrides : dict, optional
        Override default config parameters

    Returns
    -------
    results : dict
        Keys: simulated_beta, r_squared, rmse, phi_convergence, config
    """
    beta_initial = float(empirical_beta[0])
    beta_final_empirical = float(empirical_beta[-1])

    # Map epochs to log-scale (epochs = proxy for coarse-graining scale)
    # λ = epoch + 1 (avoid log(0))
    lambda_values = empirical_epochs + 1.0
    lambda_range = (float(lambda_values[0]), float(lambda_values[-1]))

    # Create config
    config = RGFlowConfig(variant=variant)
    if config_overrides:
        for key, value in config_overrides.items():
            setattr(config, key, value)

    # Simulate
    simulator = RGFlowSimulator(config)
    ln_lambda_sim, beta_sim = simulator.simulate(
        beta_initial=beta_initial,
        lambda_range=lambda_range,
        n_points=len(empirical_beta),
        method="RK45",
    )

    # Interpolate simulated β to match empirical epochs
    lambda_sim = np.exp(ln_lambda_sim)
    beta_sim_interp = np.interp(lambda_values, lambda_sim, beta_sim)

    # Compute metrics
    residuals = empirical_beta - beta_sim_interp
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((empirical_beta - np.mean(empirical_beta)) ** 2)
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    rmse = np.sqrt(np.mean(residuals**2))

    phi_score = phi_convergence_score(beta_sim_interp)

    # Compare to Φ³
    phi_comparison = compare_to_phi_ladder(beta_sim_interp, ln_lambda_sim)

    return {
        "simulated_beta": beta_sim_interp.tolist(),
        "r_squared": float(r_squared),
        "rmse": float(rmse),
        "phi_convergence_score": float(phi_score),
        "phi_comparison": phi_comparison,
        "config": {
            "variant": variant.value,
            "alpha": config.alpha,
            "gamma": config.gamma,
            "exponent": config.exponent,
            "k_cubic": config.k_cubic,
        },
    }


# ═══════════════════════════════════════════════════════════════
# VALIDATION ACROSS ALL VARIANTS
# ═══════════════════════════════════════════════════════════════


def validate_all_variants(
    trajectories: dict[str, pd.DataFrame],
) -> dict:
    """Validate all RG flow variants against all LLM trajectories.

    Parameters
    ----------
    trajectories : dict[str, DataFrame]
        LLM trajectories

    Returns
    -------
    results : dict
        Nested: results[model][variant] = metrics
    """
    all_results = {}

    variants = list(FlowVariant)

    for model_name, df in trajectories.items():
        print(f"\n{'=' * 60}")
        print(f"Model: {model_name}")
        print(f"{'=' * 60}")

        empirical_beta = df["beta"].values
        empirical_epochs = df["epoch"].values

        model_results = {}

        for variant in variants:
            print(f"  Testing {variant.value}...", end=" ")

            try:
                result = fit_rg_flow(
                    empirical_beta,
                    empirical_epochs,
                    variant,
                )

                model_results[variant.value] = result

                print(
                    f"R²={result['r_squared']:.3f}, "
                    f"RMSE={result['rmse']:.3f}, "
                    f"Φ³-score={result['phi_convergence_score']:.3f}"
                )

            except Exception as e:
                print(f"FAILED: {e}")
                model_results[variant.value] = {
                    "error": str(e),
                    "r_squared": 0.0,
                    "rmse": 999.0,
                }

        all_results[model_name] = model_results

    return all_results


# ═══════════════════════════════════════════════════════════════
# VISUALIZATION
# ═══════════════════════════════════════════════════════════════


def plot_variant_comparison(
    trajectories: dict[str, pd.DataFrame],
    results: dict,
    variant: FlowVariant,
    output_path: Optional[Path] = None,
):
    """Plot RG flow vs. empirical trajectories for given variant.

    Parameters
    ----------
    trajectories : dict
        LLM trajectories
    results : dict
        Validation results
    variant : FlowVariant
        Which variant to plot
    output_path : Path, optional
        Save path (default: analysis/results/)
    """
    n_models = len(trajectories)
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for idx, (model_name, df) in enumerate(trajectories.items()):
        ax = axes[idx]

        empirical_beta = df["beta"].values
        empirical_epochs = df["epoch"].values

        # Get simulated data
        model_result = results[model_name].get(variant.value, {})
        simulated_beta = model_result.get("simulated_beta", [])

        # Plot
        ax.plot(
            empirical_epochs,
            empirical_beta,
            "o-",
            label="Empirical",
            color="black",
            linewidth=2,
            markersize=4,
        )

        if simulated_beta:
            ax.plot(
                empirical_epochs,
                simulated_beta,
                "--",
                label="RG Flow",
                color="red",
                linewidth=2,
            )

        # Φ³ reference line
        ax.axhline(
            BETA_FIXPOINT_PHI3,
            linestyle=":",
            color="gold",
            linewidth=1.5,
            label=f"Φ³≈{BETA_FIXPOINT_PHI3:.3f}",
        )

        # Metrics
        r2 = model_result.get("r_squared", 0.0)
        rmse = model_result.get("rmse", 0.0)

        ax.set_title(
            f"{model_name}\nR²={r2:.3f}, RMSE={rmse:.3f}",
            fontsize=10,
        )
        ax.set_xlabel("Epoch")
        ax.set_ylabel("β")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)

    # Overall title
    fig.suptitle(
        f"RG Flow Validation: {variant.value.upper()}",
        fontsize=14,
        fontweight="bold",
    )

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"  → Plot saved: {output_path}")
    else:
        plt.show()

    plt.close()


def plot_summary_metrics(
    results: dict,
    output_path: Optional[Path] = None,
):
    """Plot summary metrics across all variants.

    Parameters
    ----------
    results : dict
        Validation results
    output_path : Path, optional
        Save path
    """
    # Extract R² and RMSE per variant
    variants = [v.value for v in FlowVariant]

    r2_per_variant = {v: [] for v in variants}
    rmse_per_variant = {v: [] for v in variants}

    for model_name, model_results in results.items():
        for variant in variants:
            result = model_results.get(variant, {})
            r2_per_variant[variant].append(result.get("r_squared", 0.0))
            rmse_per_variant[variant].append(result.get("rmse", 999.0))

    # Compute means
    r2_means = {v: np.mean(r2_per_variant[v]) for v in variants}
    rmse_means = {v: np.mean(rmse_per_variant[v]) for v in variants}

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # R² barplot
    ax1 = axes[0]
    ax1.bar(range(len(variants)), [r2_means[v] for v in variants], color="steelblue")
    ax1.set_xticks(range(len(variants)))
    ax1.set_xticklabels([v.replace("_", "\n") for v in variants], fontsize=9)
    ax1.set_ylabel("Mean R²", fontsize=12)
    ax1.set_title("R² by RG Flow Variant", fontsize=12, fontweight="bold")
    ax1.grid(axis="y", alpha=0.3)
    ax1.axhline(0.7, linestyle="--", color="red", linewidth=1.5, label="Target 0.70")
    ax1.legend()

    # RMSE barplot
    ax2 = axes[1]
    ax2.bar(range(len(variants)), [rmse_means[v] for v in variants], color="coral")
    ax2.set_xticks(range(len(variants)))
    ax2.set_xticklabels([v.replace("_", "\n") for v in variants], fontsize=9)
    ax2.set_ylabel("Mean RMSE", fontsize=12)
    ax2.set_title("RMSE by RG Flow Variant", fontsize=12, fontweight="bold")
    ax2.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"  → Summary plot saved: {output_path}")
    else:
        plt.show()

    plt.close()


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="RG Flow Validation")
    parser.add_argument(
        "--variant",
        type=str,
        default="all",
        choices=["all"] + [v.value for v in FlowVariant],
        help="RG flow variant to test (default: all)",
    )
    parser.add_argument(
        "--save-plots",
        action="store_true",
        help="Save plots to analysis/results/",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("RG FLOW VALIDATION - LLM β-Trajectories")
    print("=" * 60)

    # Load data
    print("\n[1] Loading LLM trajectories...")
    trajectories = load_llm_trajectories()
    print(f"  → Loaded {len(trajectories)} models")

    # Validate
    print("\n[2] Running RG flow validation...")
    results = validate_all_variants(trajectories)

    # Save results
    output_dir = Path("analysis/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    results_path = output_dir / "rg_flow_validation.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n  → Results saved: {results_path}")

    # Visualize
    if args.save_plots:
        print("\n[3] Generating plots...")

        # Plot each variant
        if args.variant == "all":
            for variant in FlowVariant:
                plot_path = output_dir / f"rg_flow_validation_{variant.value}.png"
                plot_variant_comparison(
                    trajectories,
                    results,
                    variant,
                    output_path=plot_path,
                )
        else:
            variant = FlowVariant(args.variant)
            plot_path = output_dir / f"rg_flow_validation_{variant.value}.png"
            plot_variant_comparison(
                trajectories,
                results,
                variant,
                output_path=plot_path,
            )

        # Summary plot
        summary_path = output_dir / "rg_flow_validation_summary.png"
        plot_summary_metrics(results, output_path=summary_path)

    # Report best variant
    print("\n" + "=" * 60)
    print("BEST VARIANT PER MODEL")
    print("=" * 60)

    for model_name, model_results in results.items():
        best_variant = max(
            model_results.items(),
            key=lambda x: x[1].get("r_squared", 0.0),
        )
        variant_name = best_variant[0]
        r2 = best_variant[1].get("r_squared", 0.0)
        print(f"{model_name:20s} → {variant_name:20s} (R²={r2:.3f})")

    # Overall best
    print("\n" + "=" * 60)
    print("OVERALL BEST VARIANT (Mean R²)")
    print("=" * 60)

    variant_r2_means = {}
    for variant in FlowVariant:
        r2_values = [
            results[model][variant.value].get("r_squared", 0.0)
            for model in results
            if variant.value in results[model]
        ]
        variant_r2_means[variant.value] = np.mean(r2_values) if r2_values else 0.0

    best_overall = max(variant_r2_means.items(), key=lambda x: x[1])
    print(f"  → {best_overall[0]:20s} (Mean R²={best_overall[1]:.3f})")

    print("\n✅ Validation complete!")


if __name__ == "__main__":
    main()
