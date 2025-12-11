#!/usr/bin/env python3
"""
UTAC v5.0 AI Agent Interfaces

This module provides JSON-compatible interfaces for AI agents to interact
with the v5.0 models (Cosmic Quantization, Social Rigidity).

All functions return JSON-serializable dictionaries that can be consumed
by multi-agent orchestration systems (MOR).

Author: Genesis Aeon (UTAC Framework)
Version: 5.0 "Multi-Agent Ready"
"""

import json
import sys
from pathlib import Path

# Add models directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "models"))

from cosmic_alpha_phi import (
    BOEHME_UNCERTAINTY_KM_S,
    BOEHME_VELOCITY_KM_S,
    CosmicQuantization,
)
from social_rigidity_ising import SocialIsingModel

# ============================================================================
# COSMIC VELOCITY INTERFACE
# ============================================================================


def cosmic_velocity_predict(alpha: float | None = None, phi: float | None = None) -> dict:
    """
    AI Agent Interface: Predict cosmic velocity from fundamental constants.

    Args:
        alpha: Fine-structure constant (default: physical value)
        phi: Golden ratio parameter (default: mathematical value)

    Returns:
        JSON-serializable dict with prediction and comparison

    Example:
        >>> result = cosmic_velocity_predict()
        >>> print(result['prediction_km_s'])
        1352.07
    """
    if alpha is None and phi is None:
        model = CosmicQuantization()
    else:
        model = CosmicQuantization(
            alpha=alpha if alpha is not None else model.alpha,
            phi=phi if phi is not None else model.phi,
        )

    prediction = model.predict_velocity()
    comparison = model.compare_boehme()

    return {
        "prediction_km_s": prediction,
        "measured_km_s": BOEHME_VELOCITY_KM_S,
        "uncertainty_km_s": BOEHME_UNCERTAINTY_KM_S,
        "deviation_km_s": comparison.deviation,
        "relative_error": comparison.relative_error,
        "p_value": comparison.p_value,
        "z_score": comparison.z_score,
        "constants": {"alpha": model.alpha, "phi": model.phi, "alpha_inverse": 1.0 / model.alpha},
    }


def cosmic_null_hypothesis_test(
    n_trials: int = 10000,
    alpha_range: tuple[float, float] | None = None,
    phi_range: tuple[float, float] | None = None,
    seed: int = 42,
) -> dict:
    """
    AI Agent Interface: Test null hypothesis with random constants.

    Args:
        n_trials: Number of random constant pairs to test
        alpha_range: Range for random α values (default: [0.001, 0.02])
        phi_range: Range for random Φ values (default: [1.3, 2.0])
        seed: Random seed for reproducibility

    Returns:
        JSON-serializable dict with null hypothesis test results

    Example:
        >>> result = cosmic_null_hypothesis_test(n_trials=1000)
        >>> print(result['p_value_null'])
        0.011299
    """
    model = CosmicQuantization()

    if alpha_range is None:
        alpha_range = (0.001, 0.02)
    if phi_range is None:
        phi_range = (1.3, 2.0)

    null_test = model.null_hypothesis_test(
        n_random_trials=n_trials, alpha_range=alpha_range, phi_range=phi_range, seed=seed
    )

    return {
        "n_trials": n_trials,
        "p_value_null": null_test["p_value_null"],
        "our_deviation_km_s": null_test["our_deviation_km_s"],
        "mean_random_deviation_km_s": null_test["mean_random_deviation_km_s"],
        "std_random_deviation_km_s": null_test["std_random_deviation_km_s"],
        "improvement_factor": null_test["improvement_factor"],
        "n_random_better": null_test["n_random_better"],
        "ranges": {"alpha": list(alpha_range), "phi": list(phi_range)},
    }


# ============================================================================
# SOCIAL RIGIDITY INTERFACE
# ============================================================================


def social_rigidity_predict(gini: float, load: float = 1.0) -> dict:
    """
    AI Agent Interface: Predict social rigidity from inequality.

    Args:
        gini: Gini coefficient (0-1, where 1 = max inequality)
        load: Cognitive/economic load parameter (default: 1.0)

    Returns:
        JSON-serializable dict with social state prediction

    Example:
        >>> result = social_rigidity_predict(gini=0.73)  # US 2024
        >>> print(result['is_frozen'])
        False
    """
    model = SocialIsingModel(load_baseline=load)
    state = model.compute_state(gini, load)

    return {
        "gini": gini,
        "load": load,
        "temperature": state.temperature,
        "rigidity_beta": state.rigidity,
        "magnetization": state.magnetization,
        "susceptibility": state.susceptibility,
        "adaptability": state.adaptability,
        "is_frozen": state.is_frozen,
        "phase": "FROZEN (ferromagnetic)" if state.is_frozen else "FLUID (paramagnetic)",
    }


def social_phase_transition_scan(
    gini_min: float = 0.2, gini_max: float = 0.95, n_points: int = 100, load: float = 1.0
) -> dict:
    """
    AI Agent Interface: Scan for phase transitions across Gini range.

    Args:
        gini_min: Minimum Gini coefficient
        gini_max: Maximum Gini coefficient
        n_points: Number of points to sample
        load: Cognitive load parameter

    Returns:
        JSON-serializable dict with phase transition data

    Example:
        >>> result = social_phase_transition_scan(n_points=50)
        >>> print(result['critical_gini'])
        0.95
    """
    model = SocialIsingModel(load_baseline=load)
    transition = model.phase_transition_scan(gini_range=(gini_min, gini_max), n_points=n_points)

    return {
        "critical_gini": transition.critical_gini,
        "transition_width": transition.transition_sharpness,
        "gini_range": [gini_min, gini_max],
        "n_points": n_points,
        "load": load,
        "gini_values": transition.gini_values.tolist(),
        "temperatures": transition.temperatures.tolist(),
        "magnetizations": transition.magnetizations.tolist(),
        "susceptibilities": transition.susceptibilities.tolist(),
    }


# ============================================================================
# COMBINED ANALYSIS INTERFACE
# ============================================================================


def v5_full_analysis(
    cosmic_trials: int = 10000, social_gini: float = 0.73, social_load: float = 1.0
) -> dict:
    """
    AI Agent Interface: Run complete v5.0 analysis (both models).

    Args:
        cosmic_trials: Number of null hypothesis trials
        social_gini: Gini coefficient for social analysis
        social_load: Cognitive load parameter

    Returns:
        JSON-serializable dict with both analyses

    Example:
        >>> result = v5_full_analysis()
        >>> print(result['cosmic']['p_value_null'])
        >>> print(result['social']['is_frozen'])
    """
    # Cosmic analysis
    cosmic_prediction = cosmic_velocity_predict()
    cosmic_null = cosmic_null_hypothesis_test(n_trials=cosmic_trials)

    # Social analysis
    social_state = social_rigidity_predict(gini=social_gini, load=social_load)
    social_transition = social_phase_transition_scan(n_points=50, load=social_load)

    return {
        "version": "5.0",
        "timestamp": "2025-11-23",
        "cosmic": {"prediction": cosmic_prediction, "null_hypothesis": cosmic_null},
        "social": {"state": social_state, "transition": social_transition},
        "meta": {
            "hypothesis": "structural_isomorphism",
            "status": "empirical_testing",
            "limitations": [
                "Cosmic: n=1 system, post-hoc selection, no mechanism",
                "Social: theoretical model, empirical validation pending",
            ],
        },
    }


# ============================================================================
# BATCH PROCESSING INTERFACE (for MOR agents)
# ============================================================================


def batch_cosmic_predictions(parameter_sets: list[dict]) -> list[dict]:
    """
    AI Agent Interface: Batch process multiple cosmic predictions.

    Args:
        parameter_sets: List of dicts with 'alpha' and 'phi' keys

    Returns:
        List of JSON-serializable prediction dicts

    Example:
        >>> params = [
        ...     {'alpha': 0.00729, 'phi': 1.618},
        ...     {'alpha': 0.008, 'phi': 1.7}
        ... ]
        >>> results = batch_cosmic_predictions(params)
    """
    results = []
    for params in parameter_sets:
        result = cosmic_velocity_predict(alpha=params.get("alpha"), phi=params.get("phi"))
        result["input_params"] = params
        results.append(result)
    return results


def batch_social_predictions(gini_values: list[float], load: float = 1.0) -> list[dict]:
    """
    AI Agent Interface: Batch process multiple social predictions.

    Args:
        gini_values: List of Gini coefficients
        load: Cognitive load parameter

    Returns:
        List of JSON-serializable state dicts

    Example:
        >>> ginis = [0.3, 0.5, 0.7, 0.9]
        >>> results = batch_social_predictions(ginis)
    """
    results = []
    for gini in gini_values:
        result = social_rigidity_predict(gini=gini, load=load)
        results.append(result)
    return results


# ============================================================================
# JSON I/O UTILITIES
# ============================================================================


def save_analysis_json(analysis: dict, filepath: str) -> None:
    """
    Save analysis results to JSON file.

    Args:
        analysis: Result dict from any analysis function
        filepath: Output file path

    Example:
        >>> result = v5_full_analysis()
        >>> save_analysis_json(result, 'v5_analysis.json')
    """
    import numpy as np

    class NumpyEncoder(json.JSONEncoder):
        """Handle NumPy types for JSON serialization."""

        def default(self, obj):
            if isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    with open(filepath, "w") as f:
        json.dump(analysis, f, indent=2, cls=NumpyEncoder)
    print(f"✓ Analysis saved: {filepath}")


def load_analysis_json(filepath: str) -> dict:
    """
    Load analysis results from JSON file.

    Args:
        filepath: Input file path

    Returns:
        Analysis dict

    Example:
        >>> result = load_analysis_json('v5_analysis.json')
    """
    with open(filepath) as f:
        return json.load(f)


# ============================================================================
# MAIN EXECUTION (Demo)
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("UTAC v5.0 AI AGENT INTERFACES - DEMO")
    print("=" * 70)
    print()

    # Demo 1: Cosmic prediction
    print("1. COSMIC VELOCITY PREDICTION:")
    cosmic = cosmic_velocity_predict()
    print(json.dumps(cosmic, indent=2))
    print()

    # Demo 2: Social rigidity
    print("2. SOCIAL RIGIDITY PREDICTION (US 2024):")
    social = social_rigidity_predict(gini=0.73)
    print(json.dumps(social, indent=2))
    print()

    # Demo 3: Full analysis
    print("3. COMBINED V5.0 ANALYSIS:")
    full = v5_full_analysis(cosmic_trials=1000)  # Reduced for demo
    print(f"Cosmic p-value: {full['cosmic']['null_hypothesis']['p_value_null']:.6f}")
    print(f"Social is_frozen: {full['social']['state']['is_frozen']}")
    print()

    # Demo 4: Save to JSON
    output_path = Path(__file__).parent.parent / "data" / "derived" / "v5_demo_analysis.json"
    save_analysis_json(full, str(output_path))

    print("=" * 70)
    print("DEMO COMPLETE - AI Agents can now consume these interfaces!")
    print("=" * 70)
