"""Simulation suite for UTAC threshold-field dynamics."""

from .genesis_loader import (
    DEFAULT_BETA_ESTIMATES,
    GenesisPreset,
    index_presets,
    load_beta_presets,
    resolve_preset,
)
from .implosive_genesis_sim import inverted_sigmoid, phase_space_trajectory
from .safety_delay_field import (
    SafetyDelayResult,
    control_centrality,
    crep_resonance,
    estimate_logistic_parameters,
    logistic_response,
    meta_resonance_analysis,
    simulate_safety_delay_field,
)

__all__ = [
    "SafetyDelayResult",
    "simulate_safety_delay_field",
    "logistic_response",
    "estimate_logistic_parameters",
    "control_centrality",
    "crep_resonance",
    "meta_resonance_analysis",
    "inverted_sigmoid",
    "phase_space_trajectory",
    "DEFAULT_BETA_ESTIMATES",
    "GenesisPreset",
    "index_presets",
    "load_beta_presets",
    "resolve_preset",
]

__version__ = "1.2.0"
