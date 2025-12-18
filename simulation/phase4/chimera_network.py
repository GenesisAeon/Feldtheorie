"""Kuramoto chimera explorer locked to the HEX_RESONANCE_BETA coupling.

We evolve a two-community Kuramoto network and measure whether the chimera
transition (coexistence of synchrony and drift) sharpens at β_hex. The σ(β(R-Θ))
driver uses readiness R to bias intrinsic frequencies while Θ sets the
synchronization threshold. Telemetries report order parameters, ΔAIC scores
against a weaker null coupling, and the chimera contrast between communities.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, Tuple

import numpy as np
from models.unified_constants import HEX_RESONANCE_BETA


@dataclass
class ChimeraNetworkConfig:
    """Configuration for the chimera Kuramoto simulation."""

    oscillators: int = 48
    coherent_block: int = 24
    dt: float = 0.02
    steps: int = 1200
    readiness: float = 0.65
    theta: float = 0.12
    coupling: float = HEX_RESONANCE_BETA
    null_coupling: float = 2.4
    noise: float = 0.03
    seed: int | None = 42


def _order_parameters(phases: np.ndarray, coherent_block: int) -> Tuple[float, float, float]:
    """Compute global and community order parameters."""

    global_r = np.abs(np.mean(np.exp(1j * phases)))
    r_coherent = np.abs(np.mean(np.exp(1j * phases[:coherent_block])))
    r_incoherent = np.abs(np.mean(np.exp(1j * phases[coherent_block:])))
    return float(global_r), float(r_coherent), float(r_incoherent)


def _simulate(config: ChimeraNetworkConfig, coupling_strength: float) -> Dict[str, Any]:
    """Integrate Kuramoto equations for a given coupling strength."""

    rng = np.random.default_rng(config.seed)
    phases = rng.uniform(-np.pi, np.pi, size=config.oscillators)
    intrinsic = rng.normal(loc=config.readiness, scale=0.15 + config.theta, size=config.oscillators)
    sigma_drive = 1.0 / (1.0 + np.exp(-HEX_RESONANCE_BETA * (config.readiness - config.theta)))

    within_strength = coupling_strength * np.concatenate(
        [np.full(config.coherent_block, 1.0), np.full(config.oscillators - config.coherent_block, 0.35)]
    )
    cross_strength = coupling_strength * 0.18

    global_trace: list[float] = []
    coherent_trace: list[float] = []
    incoherent_trace: list[float] = []

    for _ in range(config.steps):
        phase_diff = phases[:, None] - phases[None, :]
        sin_diff = np.sin(-phase_diff)

        # Coupling matrix: stronger within first community, weaker elsewhere.
        strength_matrix = np.full((config.oscillators, config.oscillators), cross_strength)
        strength_matrix[: config.coherent_block, : config.coherent_block] = within_strength[: config.coherent_block]
        strength_matrix[config.coherent_block :, config.coherent_block :] = within_strength[
            config.coherent_block :
        ][:, None]

        coupling_term = (strength_matrix * sin_diff).sum(axis=1) / config.oscillators
        noise = rng.normal(scale=config.noise, size=config.oscillators)

        phases = phases + config.dt * (intrinsic * sigma_drive + coupling_term + noise)
        phases = (phases + np.pi) % (2 * np.pi) - np.pi

        global_r, r_coherent, r_incoherent = _order_parameters(phases, config.coherent_block)
        global_trace.append(global_r)
        coherent_trace.append(r_coherent)
        incoherent_trace.append(r_incoherent)

    chimera_contrast = np.mean(coherent_trace[-200:]) - np.mean(incoherent_trace[-200:])

    return {
        "global": global_trace,
        "coherent": coherent_trace,
        "incoherent": incoherent_trace,
        "chimera_contrast": float(chimera_contrast),
    }


def simulate_chimera_network(config: ChimeraNetworkConfig | None = None) -> Dict[str, Any]:
    """Run the chimera network at β_hex and compare against a null coupling."""

    cfg = dataclasses.replace(config) if config else ChimeraNetworkConfig()

    beta_trace = _simulate(cfg, coupling_strength=cfg.coupling)
    null_trace = _simulate(cfg, coupling_strength=cfg.null_coupling)

    global_r = np.array(beta_trace["global"])
    null_global = np.array(null_trace["global"])

    target_profile = np.linspace(0.6, 0.9, num=global_r.size)
    residual_hex = global_r - target_profile
    residual_null = null_global - target_profile

    n = target_profile.size
    rss_hex = np.sum(residual_hex**2)
    rss_null = np.sum(residual_null**2)
    rss_hex = max(rss_hex, 1e-12)
    rss_null = max(rss_null, 1e-12)

    aic_hex = float(n * np.log(rss_hex / n) + 2)
    aic_null = float(n * np.log(rss_null / n) + 2)

    telemetry: Dict[str, Any] = {
        "beta_hex": HEX_RESONANCE_BETA,
        "sigma_driver": {
            "R": cfg.readiness,
            "Theta": cfg.theta,
            "beta": HEX_RESONANCE_BETA,
            "zeta": cfg.noise,
        },
        "chimera_contrast_beta": beta_trace["chimera_contrast"],
        "chimera_contrast_null": null_trace["chimera_contrast"],
        "delta_aic": float(aic_null - aic_hex),
        "global_order_beta": beta_trace["global"],
        "global_order_null": null_trace["global"],
        "coherent_beta": beta_trace["coherent"],
        "incoherent_beta": beta_trace["incoherent"],
        "null_model": "Kuramoto network with weaker non-hex coupling",
    }

    return telemetry


__all__ = ["ChimeraNetworkConfig", "simulate_chimera_network"]
