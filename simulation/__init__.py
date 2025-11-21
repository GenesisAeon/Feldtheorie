"""Simulation suite for UTAC threshold-field dynamics."""

from .safety_delay_field import (
    SafetyDelayResult,
    control_centrality,
    crep_resonance,
    estimate_logistic_parameters,
    logistic_response,
    meta_resonance_analysis,
    simulate_safety_delay_field,
)
from .implosive_genesis_sim import (
    ImplosiveGenesisResult,
    inverted_sigmoid,
    plot_implosive_genesis,
    simulate_implosive_genesis,
)

__all__ = [
    "SafetyDelayResult",
    "simulate_safety_delay_field",
    "logistic_response",
    "estimate_logistic_parameters",
    "control_centrality",
    "crep_resonance",
    "meta_resonance_analysis",
    "ImplosiveGenesisResult",
    "inverted_sigmoid",
    "plot_implosive_genesis",
    "simulate_implosive_genesis",
]

__version__ = "1.2.0"
