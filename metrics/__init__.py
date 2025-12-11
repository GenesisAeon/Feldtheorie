"""V6 Telemetry & Metrics Module

Tracks β-drift, τ* safety delays, and ζ-risk for Type-6 implosive field dynamics.

Usage:
    from metrics import log_telemetry, plot_beta_drift

    # Log simulation state
    log_telemetry(domain="test", beta=4.8, R=0.3, Theta=0.5)

    # Generate dashboard
    plot_beta_drift()
"""

from .telemetry_dashboard import (
    generate_summary_report,
    load_telemetry,
    log_telemetry,
    plot_beta_drift,
)

__all__ = [
    "log_telemetry",
    "load_telemetry",
    "plot_beta_drift",
    "generate_summary_report",
]

__version__ = "0.1.0"
