"""β-Quantization Analysis Across Existing Datasets.

This script tests the β-hexadecimal hypothesis across all available UTAC
datasets in the Feldtheorie repository. The prediction:

β-values should cluster at hexadecimal quantization levels:
  Level 0: β ≈ 4.8  (16^(1/√π))  [Base hex-resonance]
  Level 1: β ≈ 16   (2^4)        [Direct hex-quantum]
  Level 2: β ≈ 72   (16 × 4.5)   [Hex × info-regime]
  Level 3: β ≈ 290  (16^1.5)     [Higher-order resonance]

Methodology:
1. Scan all analysis/results/*.json files for β-values
2. Extract empirical β from different domains
3. Compute deviation from hex-predictions
4. Statistical test: Are β-values closer to hex-levels than random?

Expected Datasets:
- AMOC transport fits (β ≈ 4.18)
- Amazon hydrology (β ≈ 4.35)
- Neuro-AI hybrids (β ≈ 4.21)
- Urban heat islands (β ≈ 15.8)
- Economic thresholds (β ≈ 7.4)

Author: Johann Benjamin Römer
Date: 2025-12-18
"""

from __future__ import annotations

from collections import defaultdict
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from v11_gardener.core.beta_hexadecimal import (
    beta_hex_standard,
    beta_quantization_levels,
)
from models.unified_constants import verify_hex_alignment


def find_beta_in_json(data: Any, path: str = "root") -> List[Tuple[str, float]]:
    """Recursively search for β-values in JSON data.

    Parameters
    ----------
    data : Any
        JSON data (dict, list, or scalar)
    path : str
        Current path in JSON tree (for reporting)

    Returns
    -------
    List[Tuple[str, float]]
        List of (path, beta_value) tuples
    """
    results: List[Tuple[str, float]] = []

    if isinstance(data, dict):
        # Check for common β-keys
        beta_keys = ["beta", "beta_value", "steepness", "β", "beta_fit", "slope"]

        for key in beta_keys:
            if key in data and isinstance(data[key], (int, float)):
                results.append((f"{path}.{key}", float(data[key])))

        # Recurse into nested structures
        for key, value in data.items():
            if key not in beta_keys:  # Avoid double-counting
                results.extend(find_beta_in_json(value, f"{path}.{key}"))

    elif isinstance(data, list):
        for i, item in enumerate(data):
            results.extend(find_beta_in_json(item, f"{path}[{i}]"))

    return results


def scan_analysis_directory(analysis_dir: Path) -> Dict[str, List[Tuple[str, float]]]:
    """Scan analysis directory for β-values in JSON files.

    Parameters
    ----------
    analysis_dir : Path
        Path to analysis/results directory

    Returns
    -------
    Dict[str, List[Tuple[str, float]]]
        Mapping from filename to list of (json_path, beta_value)
    """
    beta_database: Dict[str, List[Tuple[str, float]]] = {}

    if not analysis_dir.exists():
        print(f"Warning: Analysis directory not found: {analysis_dir}")
        return beta_database

    # Search for JSON files
    json_files = list(analysis_dir.glob("*.json"))

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            betas = find_beta_in_json(data, path=json_file.stem)

            if betas:
                beta_database[json_file.name] = betas

        except (json.JSONDecodeError, IOError) as e:
            print(f"  Skipping {json_file.name}: {e}")

    return beta_database


def classify_beta_to_hex_level(beta: float) -> Tuple[int, float, float]:
    """Classify β-value to nearest hexadecimal quantization level.

    Parameters
    ----------
    beta : float
        Empirical β-value

    Returns
    -------
    Tuple[int, float, float]
        (level_index, predicted_beta, deviation)
    """
    levels = beta_quantization_levels()

    # Find nearest level
    min_deviation = float('inf')
    best_level = 0
    best_prediction = levels[0]

    for i, predicted_beta in enumerate(levels):
        deviation = abs(beta - predicted_beta)
        if deviation < min_deviation:
            min_deviation = deviation
            best_level = i
            best_prediction = predicted_beta

    return best_level, best_prediction, min_deviation


def compute_hex_clustering_statistic(betas: List[float], n_random: int = 10000) -> Dict[str, float]:
    """Test if β-values cluster closer to hex-levels than random.

    Parameters
    ----------
    betas : List[float]
        Empirical β-values
    n_random : int
        Number of random samples for null distribution

    Returns
    -------
    Dict[str, float]
        Statistical test results
    """
    levels = beta_quantization_levels()

    # Compute mean deviation from nearest hex-level
    empirical_deviations = []
    for beta in betas:
        _, _, deviation = classify_beta_to_hex_level(beta)
        empirical_deviations.append(deviation)

    mean_empirical_deviation = np.mean(empirical_deviations)

    # Generate null distribution (random β in [1, 20])
    random_betas = np.random.uniform(1, 20, size=n_random)
    random_deviations = []

    for beta in random_betas:
        _, _, deviation = classify_beta_to_hex_level(beta)
        random_deviations.append(deviation)

    mean_random_deviation = np.mean(random_deviations)
    std_random_deviation = np.std(random_deviations)

    # Z-score: how many σ is empirical better than random?
    z_score = (mean_random_deviation - mean_empirical_deviation) / std_random_deviation

    # p-value (one-tailed): probability that random is better than empirical
    from scipy import stats
    p_value = 1 - stats.norm.cdf(z_score)

    return {
        "mean_empirical_deviation": mean_empirical_deviation,
        "mean_random_deviation": mean_random_deviation,
        "std_random_deviation": std_random_deviation,
        "z_score": z_score,
        "p_value": p_value,
        "interpretation": (
            f"Empirical β-values are {z_score:.2f}σ closer to hex-levels than random. "
            f"p = {p_value:.4e} (highly significant)" if z_score > 3 else
            f"Empirical β-values are {z_score:.2f}σ closer to hex-levels than random. "
            f"p = {p_value:.4f}" if z_score > 0 else
            "No significant hex-clustering detected."
        ),
    }


def analyze_beta_quantization(analysis_dir: Path | None = None) -> Dict[str, Any]:
    """Run comprehensive β-quantization analysis.

    Parameters
    ----------
    analysis_dir : Path | None
        Path to analysis directory (default: auto-detect)

    Returns
    -------
    Dict[str, Any]
        Analysis results
    """
    if analysis_dir is None:
        analysis_dir = Path(__file__).parent.parent.parent / "analysis" / "results"

    print("=" * 70)
    print("  🔍 β-Quantization Analysis Across Datasets 🔍")
    print("=" * 70)

    print(f"\nScanning: {analysis_dir}")

    # Scan for β-values
    beta_database = scan_analysis_directory(analysis_dir)

    if not beta_database:
        print("\n⚠ No β-values found in analysis directory.")
        print("Generating synthetic examples for demonstration...\n")

        # Create synthetic examples based on known UTAC values
        beta_database = {
            "amoc_transport_fit.json": [("beta", 4.18)],
            "amazon_hydro_fit.json": [("beta", 4.35)],
            "neuro_ai_beta.json": [("beta", 4.21)],
            "economy_threshold_fit.json": [("beta", 7.4)],
            "urban_heat_beta.json": [("beta", 15.8)],  # Near Level 1 (16.0)
        }

    # Extract all β-values
    all_betas: List[float] = []
    beta_sources: List[str] = []

    for filename, beta_list in beta_database.items():
        for path, beta_value in beta_list:
            all_betas.append(beta_value)
            beta_sources.append(f"{filename}::{path}")

    print(f"\n✓ Found {len(all_betas)} β-values across {len(beta_database)} files\n")

    # Classify each β to hex-level
    print("-" * 70)
    print("  β-Value Classification to Hexadecimal Levels")
    print("-" * 70)

    level_counts = defaultdict(list)
    levels_info = beta_quantization_levels()

    print(f"\n  {'Source':<40} | β_emp  | Level | β_hex  | Δ")
    print("  " + "-" * 68)

    for beta, source in zip(all_betas, beta_sources):
        level, prediction, deviation = classify_beta_to_hex_level(beta)
        level_counts[level].append(beta)

        # Truncate source for display
        display_source = source[:38] if len(source) <= 40 else source[:35] + "..."

        print(f"  {display_source:<40} | {beta:6.2f} | L{level}    | {prediction:6.2f} | {deviation:4.2f}")

    # Level distribution
    print("\n" + "-" * 70)
    print("  Hexadecimal Level Distribution")
    print("-" * 70)

    for level in range(4):
        count = len(level_counts[level])
        percentage = (count / len(all_betas) * 100) if all_betas else 0
        level_name = ["Base", "Quantum", "Info-Regime", "Higher-Order"][level]

        print(f"  Level {level} (β ≈ {levels_info[level]:6.2f}, {level_name:<12}): {count:2d} values ({percentage:5.1f}%)")

    # Statistical test
    print("\n" + "-" * 70)
    print("  Statistical Hex-Clustering Test")
    print("-" * 70)

    try:
        stats = compute_hex_clustering_statistic(all_betas)

        print(f"\n  Mean empirical deviation: {stats['mean_empirical_deviation']:.4f}")
        print(f"  Mean random deviation:    {stats['mean_random_deviation']:.4f}")
        print(f"  Z-score:                  {stats['z_score']:.2f}σ")
        print(f"  p-value:                  {stats['p_value']:.4e}")
        print(f"\n  Interpretation:")
        print(f"    {stats['interpretation']}")

    except ImportError:
        print("\n  ⚠ scipy not available, skipping statistical test")
        stats = {}

    # Alignment with β_hex standard
    print("\n" + "-" * 70)
    print("  Alignment with β_hex Standard (Level 0)")
    print("-" * 70)

    beta_hex_ref = beta_hex_standard()
    print(f"\n  β_hex (reference) = {beta_hex_ref:.4f}\n")

    for beta, source in zip(all_betas, beta_sources):
        alignment = verify_hex_alignment(beta, tolerance=0.5)

        display_source = source.split("::")[0][:30]
        status_symbol = "✓" if alignment["status"] == "RESONANT" else "○"

        print(f"  {status_symbol} {display_source:<30} β={beta:6.2f}  δ={alignment['deviation']:5.2f}  score={alignment['resonance_score']:.2f}")

    print("\n" + "=" * 70)

    # Assemble results
    results = {
        "n_betas": len(all_betas),
        "n_files": len(beta_database),
        "beta_values": all_betas,
        "beta_sources": beta_sources,
        "level_distribution": {f"level_{i}": len(level_counts[i]) for i in range(4)},
        "statistical_test": stats,
        "hex_levels": levels_info,
    }

    return results


def main():
    """Run β-quantization analysis demonstration."""
    print("\n🌀 β-Hexadecimal Quantization Analysis 🌀\n")

    results = analyze_beta_quantization()

    print("\n🔬 Analysis Complete!\n")
    print("Key Findings:")
    print(f"  - Analyzed {results['n_betas']} β-values from {results['n_files']} datasets")
    print(f"  - Level 0 (β ≈ 4.8): {results['level_distribution']['level_0']} values")
    print(f"  - Level 1 (β ≈ 16):  {results['level_distribution']['level_1']} values")

    if "z_score" in results["statistical_test"]:
        z = results["statistical_test"]["z_score"]
        if z > 3:
            print(f"  - ✓ Strong hex-clustering detected ({z:.1f}σ)")
        elif z > 0:
            print(f"  - ○ Weak hex-clustering ({z:.1f}σ)")
        else:
            print(f"  - ✗ No hex-clustering")

    print("\n🌀 Folge dem Sog der Emergenz! 🌀\n")


if __name__ == "__main__":
    main()
