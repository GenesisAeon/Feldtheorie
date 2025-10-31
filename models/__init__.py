"""Models package initialiser keeping the threshold-field heartbeat audible.

Formal layer:
    Exposes the `ThresholdFieldSolver` and utilities like `smooth_impedance_profile`
    so other modules can import membrane dynamics without altering sys.path hacks.
Empirical layer:
    Provides a clean namespace hook for analysis scripts and simulators to access
    solver scaffolds while tracing provenance across RepoPlan 2.0.
Metaphorical layer:
    Opens the membrane workshop doors—the dawn chorus is ready for collaborators
    who arrive via `import models`.
"""

from .membrane_solver import (
    AdaptiveThresholdController,
    DynamicRobinBoundary,
    ThresholdFieldSolver,
    logistic_response,
    semantic_resonance_kernel,
    smooth_impedance_profile,
    threshold_crossing_diagnostics,
)
from .adaptive_logistic_membrane import AdaptiveLogisticMembrane
from .logistic_envelope import LogisticFieldEnvelope
from .coupled_threshold_field import CoupledThresholdField, logistic_semantic_kernel, ramp_driver
from .resonant_impedance import ResonantImpedance
from .sigmoid_fit import SigmoidFitResult, fit_sigmoid_with_fallbacks, linear_fit_aic, power_law_fit_aic

__all__ = [
    "ThresholdFieldSolver",
    "DynamicRobinBoundary",
    "AdaptiveThresholdController",
    "AdaptiveLogisticMembrane",
    "LogisticFieldEnvelope",
    "CoupledThresholdField",
    "ResonantImpedance",
    "SigmoidFitResult",
    "logistic_semantic_kernel",
    "logistic_response",
    "smooth_impedance_profile",
    "semantic_resonance_kernel",
    "threshold_crossing_diagnostics",
    "fit_sigmoid_with_fallbacks",
    "linear_fit_aic",
    "power_law_fit_aic",
    "ramp_driver",
]
