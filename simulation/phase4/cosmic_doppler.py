"""Cosmic Doppler abstraction around the Θ horizon using β_hex quantization.

The simulation imagines information packets approaching a Threshold Θ
(Ereignishorizont). When readiness R surpasses Θ, σ(β(R-Θ)) steepens and the
hexadecimal resonance β_hex determines how information density is quantized.

Telemetry reports the quantized density profile, ΔAIC against a softer null
(beta=1.2), and a horizon sharpness index to capture how abruptly the density
ramps once R>Θ.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, Sequence

import numpy as np
from models.unified_constants import HEX_RESONANCE_BETA


def _sigmoid_beta(r: np.ndarray, theta: float, beta: float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-beta * (r - theta)))


def _aic(observed: np.ndarray, predicted: np.ndarray, k: int = 2) -> float:
    residuals = observed - predicted
    n = residuals.size
    rss = np.sum(residuals**2)
    rss = max(rss, 1e-12)
    return float(n * np.log(rss / n) + 2 * k)


@dataclass
class CosmicDopplerConfig:
    """Configuration for the cosmic Doppler horizon experiment."""

    readiness: Sequence[float] | None = None
    theta: float = 0.72
    quantization_levels: int = 24
    beta: float = HEX_RESONANCE_BETA
    beta_null: float = 1.2
    damping: float = 0.018
    noise_modulation: float = 0.015


def simulate_cosmic_doppler(config: CosmicDopplerConfig | None = None) -> Dict[str, Any]:
    """Simulate information redshift around the Θ horizon using β_hex."""

    cfg = dataclasses.replace(config) if config else CosmicDopplerConfig()
    readiness = (
        np.asarray(cfg.readiness, dtype=float)
        if cfg.readiness is not None
        else np.linspace(0.1, 1.4, num=72)
    )

    sigma_hex = _sigmoid_beta(readiness, cfg.theta, cfg.beta)
    sigma_null = _sigmoid_beta(readiness, cfg.theta, cfg.beta_null)

    redshift_hex = np.exp(-cfg.beta * np.maximum(readiness - cfg.theta, 0.0))
    base_density = sigma_hex * (1.0 - cfg.damping) + cfg.damping * redshift_hex

    quantized = np.clip(
        np.round(base_density * cfg.quantization_levels) / cfg.quantization_levels,
        0.0,
        1.0,
    )
    null_quantized = np.clip(
        np.round(sigma_null * cfg.quantization_levels) / cfg.quantization_levels,
        0.0,
        1.0,
    )

    deterministic_noise = cfg.noise_modulation * np.cos(readiness * HEX_RESONANCE_BETA)
    observed_density = np.clip(quantized + deterministic_noise, 0.0, 1.0)

    aic_hex = _aic(observed_density, quantized)
    aic_null = _aic(observed_density, null_quantized)

    horizon_idx = int(np.argmax(readiness >= cfg.theta))
    gradient = np.gradient(quantized, readiness)
    horizon_sharpness = float(np.abs(gradient[horizon_idx])) if horizon_idx < gradient.size else 0.0

    telemetry: Dict[str, Any] = {
        "beta_hex": cfg.beta,
        "beta_null": cfg.beta_null,
        "sigma_profile": sigma_hex.tolist(),
        "sigma_null": sigma_null.tolist(),
        "quantized_density": quantized.tolist(),
        "quantized_density_null": null_quantized.tolist(),
        "observed_density": observed_density.tolist(),
        "delta_aic": float(aic_null - aic_hex),
        "horizon_sharpness": horizon_sharpness,
        "horizon_index": horizon_idx,
        "sigma_driver": {
            "R": readiness.tolist(),
            "Theta": cfg.theta,
            "beta": cfg.beta,
            "zeta": cfg.damping,
        },
    }

    return telemetry


__all__ = ["CosmicDopplerConfig", "simulate_cosmic_doppler"]
