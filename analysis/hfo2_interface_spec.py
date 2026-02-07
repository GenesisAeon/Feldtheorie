from __future__ import annotations

from typing import Any


def get_hfo2_interface_contract() -> dict[str, Any]:
    """High-level AFET contract for HfO₂ neuromorphic hardware integration."""
    return {
        "name": "AFET-HfO2-Neuromorphic-Interface-v0",
        "inputs": {
            "pulse_sequence": "list[dict] with keys {voltage_v, width_ns, channel_id}",
            "sensor_feedback": "optional dict containing current, resistance, temperature",
            "calibration_profile": "dict with sigma_phi_target and beta_profile",
        },
        "outputs": {
            "state_embedding": "list[float] latent state exported to AFET runtime",
            "sigma_phi_estimate": "float metastability estimator for safety monitor",
            "diagnostics": "dict with drift_score, retention_error, and device_flags",
        },
        "constraints": {
            "latency_ms": "<= 5ms per inference tick",
            "thermal_window_c": "0-85C nominal",
            "critical_sigma_phi": 0.055,
        },
        "notes": [
            "Placeholder contract pending co-design with hardware partner.",
            "Designed for compatibility with AFETSafetyMonitor and scaling pilot outputs.",
        ],
    }
