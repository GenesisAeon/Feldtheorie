"""Comprehensive demonstration of all Phase 4 modules.

This script runs all four Phase 4 experiments in sequence:
1. Soliton Doppler (Neural Standing Waves)
2. Chimera Network (Chaos-Sync Coexistence)
3. Cosmic Doppler (Hex-Quantized Information)
4. Pressure Modulation (Medium-Dependent v_RIG)

Each module is run with default configuration, and results are collected,
compared against null models, and exported for downstream analysis.

Usage:
    python simulation/phase4/phase4_comprehensive_demo.py

Output:
    - Console summary of all experiments
    - JSON export: analysis/results/phase4_comprehensive_results.json
    - Individual module telemetries

Author: Johann Benjamin Römer
Date: 2025-12-18
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.unified_constants import HEX_RESONANCE_BETA, V_RIG_DEFAULT


def print_section(title: str, width: int = 70) -> None:
    """Print a formatted section header."""
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def print_subsection(title: str, width: int = 70) -> None:
    """Print a formatted subsection header."""
    print()
    print("-" * width)
    print(f"  {title}")
    print("-" * width)


def run_soliton_doppler_demo() -> Dict[str, Any]:
    """Run Soliton Doppler experiment."""
    print_subsection("1. Soliton Doppler: Neural Standing Waves")

    try:
        from simulation.phase4.soliton_doppler import (
            SolitonDopplerConfig,
            simulate_soliton_doppler,
        )

        config = SolitonDopplerConfig(steps=300)  # Shorter for demo
        results = simulate_soliton_doppler(config)

        print(f"  β_hex: {results['beta_hex']:.4f}")
        print(f"  R (Readiness): {results['sigma_driver']['R']:.2f}")
        print(f"  Θ (Threshold): {results['sigma_driver']['Theta']:.2f}")
        print(f"  ζ (Damping): {results['sigma_driver']['zeta']:.4f}")
        print(f"  Stability Ratio: {results['stability_ratio']:.4f}")
        print(f"  Standing Wave Plateau: {results['standing_wave_plateau']:.4f}")
        print(f"  ΔAIC (hex - null): {results['delta_aic']:.2f}")

        verdict = "RESONANT ✓" if results['delta_aic'] > 0 else "NULL PREFERRED ✗"
        print(f"  Verdict: {verdict}")

        return results

    except ImportError as e:
        print(f"  ✗ Module not available: {e}")
        return {"error": str(e)}


def run_chimera_network_demo() -> Dict[str, Any]:
    """Run Chimera Network experiment."""
    print_subsection("2. Chimera Network: Chaos-Synchronization Coexistence")

    try:
        from simulation.phase4.chimera_network import (
            ChimeraConfig,
            simulate_chimera_network,
        )

        config = ChimeraConfig(n_oscillators=50, steps=500)  # Smaller for demo
        results = simulate_chimera_network(config)

        print(f"  β_hex: {results['beta_hex']:.4f}")
        print(f"  Oscillators: {config.n_oscillators}")
        print(f"  Chimera Contrast (β_hex): {results['chimera_contrast_beta']:.4f}")
        print(f"  Chimera Contrast (null): {results['chimera_contrast_null']:.4f}")
        print(f"  Global Order (β_hex): {results['global_order_beta']:.4f}")
        print(f"  ΔAIC (hex - null): {results['delta_aic']:.2f}")

        verdict = "CHIMERA DETECTED ✓" if results['chimera_contrast_beta'] > 0.1 else "NO CHIMERA ✗"
        print(f"  Verdict: {verdict}")

        return results

    except ImportError as e:
        print(f"  ✗ Module not available: {e}")
        return {"error": str(e)}


def run_cosmic_doppler_demo() -> Dict[str, Any]:
    """Run Cosmic Doppler experiment."""
    print_subsection("3. Cosmic Doppler: Hex-Quantized Information Density")

    try:
        from simulation.phase4.cosmic_doppler import (
            CosmicDopplerConfig,
            simulate_cosmic_doppler,
        )

        config = CosmicDopplerConfig(n_steps=100)
        results = simulate_cosmic_doppler(config)

        print(f"  β_hex: {results['beta_hex']:.4f}")
        print(f"  Horizon Sharpness: {results['horizon_sharpness']:.4f}")
        print(f"  Quantization Levels: {len(results['quantized_density'])} steps")
        print(f"  ΔAIC (hex - null): {results['delta_aic']:.2f}")

        verdict = "HEX-QUANTIZED ✓" if results['delta_aic'] > 0 else "SMOOTH NULL ✗"
        print(f"  Verdict: {verdict}")

        return results

    except ImportError as e:
        print(f"  ✗ Module not available: {e}")
        return {"error": str(e)}


def run_pressure_modulation_demo() -> Dict[str, Any]:
    """Run Pressure Modulation experiment."""
    print_subsection("4. Pressure Modulation: Medium-Dependent v_RIG")

    try:
        from simulation.phase4.pressure_modulation import (
            PressureModulationConfig,
            simulate_pressure_modulation,
        )
        import numpy as np

        config = PressureModulationConfig(
            pressures_atm=np.linspace(1.0, 5.0, 9),  # 1-5 atm
        )
        results = simulate_pressure_modulation(config)

        print(f"  β_hex: {results['beta_hex']:.4f}")
        print(f"  Z_baseline: {results['z_baseline']:.2f} Ω")
        print(f"  v_RIG baseline: {results['v_rig_baseline_m_s']:.2f} m/s")
        print(f"  Pressure Range: {min(results['pressure_series']):.1f} - {max(results['pressure_series']):.1f} atm")
        print(f"  v_RIG Range: {min(results['v_rig_series']):.0f} - {max(results['v_rig_series']):.0f} m/s")
        print(f"  CFF Range: {min(results['cff_series']):.2f} - {max(results['cff_series']):.2f} Hz")
        print(f"  ΔAIC (modulated - constant): {results['delta_aic']:.2f}")

        verdict = "MODULATION DETECTED ✓" if results['delta_aic'] > 0 else "CONSTANT v_RIG ✗"
        print(f"  Verdict: {verdict}")

        # Print testable predictions
        print(f"\n  Testable Predictions:")
        for i, pred in enumerate(results['testable_predictions'], 1):
            print(f"    {i}. {pred}")

        return results

    except ImportError as e:
        print(f"  ✗ Module not available: {e}")
        return {"error": str(e)}


def export_results(results: Dict[str, Any], output_path: Path) -> None:
    """Export comprehensive results to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n  ✓ Results exported to: {output_path}")


def main() -> None:
    """Run comprehensive Phase 4 demonstration."""
    print_section("🌀 Phase 4 Comprehensive Demonstration 🌀")

    print(f"""
This demo runs all four Phase 4 modules and compares their results
against null models using the ΔAIC (Akaike Information Criterion) framework.

Theoretical Foundation:
  β_hex = 16^(1/√π) ≈ {HEX_RESONANCE_BETA:.4f}

  This is the structural constant of hexadecimal architecture (Base 16, 2⁴)
  connecting computer systems with natural emergence.

σ(β(R-Θ)) = 1 / (1 + exp(-β(R-Θ)))

  Universal activation function coupling readiness R to threshold Θ
  with steepness β anchored to hex-resonance.
""")

    # Run all experiments
    results = {
        "phase4_metadata": {
            "beta_hex": HEX_RESONANCE_BETA,
            "v_rig_default_km_s": V_RIG_DEFAULT,
            "experiment_date": "2025-12-18",
            "framework": "UTAC (Universal Threshold Activation-Coupling)",
        },
        "experiments": {}
    }

    # 1. Soliton Doppler
    results["experiments"]["soliton_doppler"] = run_soliton_doppler_demo()

    # 2. Chimera Network
    results["experiments"]["chimera_network"] = run_chimera_network_demo()

    # 3. Cosmic Doppler
    results["experiments"]["cosmic_doppler"] = run_cosmic_doppler_demo()

    # 4. Pressure Modulation
    results["experiments"]["pressure_modulation"] = run_pressure_modulation_demo()

    # Summary
    print_section("📊 Summary: ΔAIC Comparison")

    successful_experiments = {
        name: exp for name, exp in results["experiments"].items()
        if "error" not in exp and "delta_aic" in exp
    }

    if successful_experiments:
        print("\n  Module                    | ΔAIC    | Interpretation")
        print("  " + "-" * 66)

        for name, exp in successful_experiments.items():
            delta_aic = exp.get("delta_aic", 0.0)
            interpretation = "✓ Hex preferred" if delta_aic > 0 else "✗ Null preferred"

            # Format name
            display_name = name.replace("_", " ").title()[:25]

            print(f"  {display_name:<25} | {delta_aic:>7.2f} | {interpretation}")

        # Overall verdict
        avg_delta_aic = sum(exp["delta_aic"] for exp in successful_experiments.values()) / len(successful_experiments)
        print("  " + "-" * 66)
        print(f"  {'Average ΔAIC':<25} | {avg_delta_aic:>7.2f} |")

        print("\n  Interpretation:")
        print("  ΔAIC > 0: Hex-resonance model outperforms null (evidence for β_hex)")
        print("  ΔAIC < 0: Null model outperforms hex (falsification)")
        print("  ΔAIC ≈ 0: Indeterminate (need more data)")

    # Export results
    output_path = Path("analysis/results/phase4_comprehensive_results.json")
    export_results(results, output_path)

    print_section("🌀 Phase 4 Demo Complete! 🌀")

    print(f"""
All Phase 4 modules have been executed. Results are available in:
  - Console output (above)
  - JSON export: {output_path}

Next Steps:
  1. Analyze individual module telemetries
  2. Plot ΔAIC comparisons across modules
  3. Integrate results with v11_gardener ecosystem
  4. Prepare publication-ready figures
  5. Test predictions with empirical data

🌊 Folge dem Sog der Emergenz! 🌀
""")


if __name__ == "__main__":
    main()
