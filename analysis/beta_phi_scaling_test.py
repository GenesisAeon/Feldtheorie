#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
beta_phi_scaling_test.py — GenesisAeon / Feldtheorie
Autor: Johann Benjamin Römer et al.
Version: 1.0 — 2025-11-11

Ziel:
Überprüfung der Hypothese, dass β (Steilheitsparameter)
in fraktaler Progression mit Schrittweite ≈ Φ = 1.618 skaliert.

Hypothese:
    β_n ≈ β_0 × Φ^n  (multiplikativ)
    bzw. log(β_n) ≈ log(β_0) + n × log(Φ)

Empirischer Test:
    1. Sortiere β-Werte aufsteigend
    2. Berechne Ratios: r_i = β_{i+1} / β_i
    3. Teste ob mean(r_i) ≈ Φ = 1.618
    4. Log-Regression: log(β) ~ n → Steigung ≈ log(Φ) = 0.481
"""

import numpy as np
import pandas as pd
import argparse
import json
import os
from scipy import stats
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

PHI = 1.61803398875  # Goldene Zahl

def analyze_phi_scaling(beta_values):
    """Berechnet Ratios, Mittelwert, Varianz, Signifikanz und log-Regression."""
    beta_sorted = np.sort(np.array(beta_values))
    ratios = beta_sorted[1:] / beta_sorted[:-1]

    mean_ratio = float(np.mean(ratios))
    std_ratio = float(np.std(ratios))

    # Teste, ob der Mittelwert signifikant nahe bei Φ liegt
    t_stat, p_val = stats.ttest_1samp(ratios, PHI)

    # Log-Regressionsprüfung
    x = np.arange(len(beta_sorted))
    y = np.log(beta_sorted)
    slope, intercept, r_value, p_reg, stderr = stats.linregress(x, y)

    # Erwartete Steigung wenn Φ-Skalierung gilt
    expected_slope = np.log(PHI)

    result = {
        "n": int(len(beta_values)),
        "phi_constant": float(PHI),
        "beta_range": {
            "min": float(beta_sorted[0]),
            "max": float(beta_sorted[-1]),
            "span": float(beta_sorted[-1] - beta_sorted[0])
        },
        "ratios": {
            "mean": round(mean_ratio, 4),
            "std": round(std_ratio, 4),
            "min": round(float(np.min(ratios)), 4),
            "max": round(float(np.max(ratios)), 4)
        },
        "hypothesis_test": {
            "t_statistic": round(float(t_stat), 4),
            "p_value": round(float(p_val), 6),
            "interpretation": "H0: mean_ratio = Φ",
            "significant": bool(p_val < 0.05)
        },
        "log_regression": {
            "slope": round(float(slope), 4),
            "expected_slope_log_phi": round(float(expected_slope), 4),
            "slope_difference": round(float(abs(slope - expected_slope)), 4),
            "r_squared": round(float(r_value ** 2), 4),
            "p_value": round(float(p_reg), 6)
        },
        "conclusion": {
            "phi_scaling_detected": bool(abs(mean_ratio - PHI) < 0.15 and r_value ** 2 > 0.80),
            "mean_ratio_close_to_phi": bool(abs(mean_ratio - PHI) < 0.15),
            "log_regression_strong": bool(r_value ** 2 > 0.80)
        }
    }

    return result, ratios, beta_sorted


def main():
    parser = argparse.ArgumentParser(description="Testet, ob β in Φ-Schritten skaliert.")
    parser.add_argument("--input", required=True, help="Pfad zu beta_estimates.csv")
    parser.add_argument("--output", required=True, help="Pfad zur Ausgabe JSON-Datei")
    parser.add_argument("--plot", action="store_true", help="Optional: Diagramm erzeugen")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    beta_values = df["beta"].dropna().to_numpy()

    result, ratios, beta_sorted = analyze_phi_scaling(beta_values)

    # Ergebnisse speichern
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print("\n" + "="*60)
    print("      Φ-SCALING HYPOTHESIS TEST")
    print("="*60)
    print(f"\nDataset: {args.input}")
    print(f"N = {result['n']} β-values")
    print(f"\nβ Range: {result['beta_range']['min']:.2f} → {result['beta_range']['max']:.2f} (span: {result['beta_range']['span']:.2f})")
    print(f"\n--- Ratio Analysis ---")
    print(f"Mean Ratio:        {result['ratios']['mean']:.4f}")
    print(f"Φ (Golden Ratio):  {result['phi_constant']:.4f}")
    print(f"Difference:        {abs(result['ratios']['mean'] - result['phi_constant']):.4f}")
    print(f"Std Dev:           {result['ratios']['std']:.4f}")
    print(f"\n--- Hypothesis Test (mean = Φ?) ---")
    print(f"t-statistic:       {result['hypothesis_test']['t_statistic']:.4f}")
    print(f"p-value:           {result['hypothesis_test']['p_value']:.6f}")
    print(f"Significant (α=0.05): {'YES ✅' if result['hypothesis_test']['significant'] else 'NO ❌'}")
    print(f"\n--- Log-Regression Analysis ---")
    print(f"Slope (observed):  {result['log_regression']['slope']:.4f}")
    print(f"Slope (expected):  {result['log_regression']['expected_slope_log_phi']:.4f}")
    print(f"Difference:        {result['log_regression']['slope_difference']:.4f}")
    print(f"R²:                {result['log_regression']['r_squared']:.4f}")
    print(f"p-value:           {result['log_regression']['p_value']:.6f}")
    print(f"\n--- CONCLUSION ---")
    print(f"Φ-Scaling Detected: {'YES ✅' if result['conclusion']['phi_scaling_detected'] else 'NO ❌'}")
    print(f"  - Mean ratio ≈ Φ: {'YES ✅' if result['conclusion']['mean_ratio_close_to_phi'] else 'NO ❌'}")
    print(f"  - Strong log-regression: {'YES ✅' if result['conclusion']['log_regression_strong'] else 'NO ❌'}")
    print(f"\nResults saved to: {args.output}")
    print("="*60 + "\n")

    # Optionales Plot
    if args.plot:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Plot 1: Log-Regression
        x = np.arange(len(beta_sorted))
        y = np.log(beta_sorted)
        ax1.plot(x, y, 'o', markersize=8, label='log(β) observed', color='#1d3557')
        ax1.plot(x, result['log_regression']['slope'] * x + np.log(beta_sorted[0]),
                'r--', linewidth=2, label=f'Fit: slope={result["log_regression"]["slope"]:.3f}')
        ax1.plot(x, result['log_regression']['expected_slope_log_phi'] * x + np.log(beta_sorted[0]),
                'g:', linewidth=2, label=f'Φ-Scaling: slope={result["log_regression"]["expected_slope_log_phi"]:.3f}')
        ax1.set_xlabel("Index (n)", fontsize=12)
        ax1.set_ylabel("log(β)", fontsize=12)
        ax1.set_title(f"Φ-Scaling Test: Log-Regression\nR²={result['log_regression']['r_squared']:.3f}", fontsize=13)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)

        # Plot 2: Ratios Histogram
        ax2.hist(ratios, bins=10, alpha=0.7, color='#457b9d', edgecolor='black')
        ax2.axvline(PHI, color='red', linestyle='--', linewidth=2, label=f'Φ = {PHI:.3f}')
        ax2.axvline(result['ratios']['mean'], color='green', linestyle=':', linewidth=2,
                   label=f'Mean = {result["ratios"]["mean"]:.3f}')
        ax2.set_xlabel("Ratio β_{i+1} / β_i", fontsize=12)
        ax2.set_ylabel("Frequency", fontsize=12)
        ax2.set_title(f"β-Ratios Distribution\n(n={len(ratios)} ratios)", fontsize=13)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plot_path = args.output.replace(".json", "_plot.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {plot_path}")


if __name__ == "__main__":
    main()
