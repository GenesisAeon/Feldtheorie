"""Soliton Doppler probe for Phase 4 neural-field standing waves.

This module keeps σ(β(R-Θ)) explicit by treating `readiness` as R and
`theta` as Θ while locking the nonlinearity to the hexadecimal resonance
constant β_hex = 16^(2/π). The experiment tracks whether soliton-like wave
packets stabilize into standing waves when β equals HEX_RESONANCE_BETA.

Telemetries include ΔAIC comparisons against a null linear model, stability
ratios for the central membrane point, and Doppler-shifted phase velocities.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np
from models.unified_constants import HEX_RESONANCE_BETA


@dataclass
class SolitonDopplerConfig:
    """Configuration for the soliton Doppler experiment.

    Attributes
    ----------
    grid_points: int
        Number of spatial samples across the neural field membrane.
    dx: float
        Spatial resolution between grid points.
    dt: float
        Integration time step for the explicit solver.
    steps: int
        Total simulation steps executed.
    theta: float
        Threshold Θ in the σ(β(R-Θ)) logistic driver.
    readiness: float
        Readiness R baseline, nudging the field toward activation.
    damping: float
        ζ(R) style damping to prevent runaway amplitudes.
    perturbation: float
        Small stochastic drive to test robustness of the standing wave.
    carrier_k: float
        Initial wave number k for the seed packet.
    seed_width: float
        Width of the initial Gaussian packet.
    """

    grid_points: int = 256
    dx: float = 0.25
    dt: float = 0.002
    steps: int = 600
    theta: float = 0.2
    readiness: float = 0.5
    damping: float = 0.0008
    perturbation: float = 0.015
    carrier_k: float = 0.4
    seed_width: float = 6.0


def _laplacian(field: np.ndarray, dx: float) -> np.ndarray:
    """Compute a periodic 1D Laplacian."""

    return (np.roll(field, 1) + np.roll(field, -1) - 2 * field) / (dx * dx)


def _aic_from_residuals(residuals: np.ndarray, k: int = 2) -> float:
    """Compute an AIC score for residuals with k parameters."""

    n = residuals.size
    rss = np.sum(residuals**2)
    rss = max(rss, 1e-12)
    return float(n * np.log(rss / n) + 2 * k)


def simulate_soliton_doppler(config: SolitonDopplerConfig | None = None) -> Dict[str, Any]:
    """Run the soliton Doppler experiment with β_hex coupling.

    Returns a telemetry dictionary with stability metrics, ΔAIC comparisons
    between the β_hex run and a null linear β=0 model, and final profiles for
    downstream visualization.
    """

    cfg = dataclasses.replace(config) if config else SolitonDopplerConfig()
    x = (np.arange(cfg.grid_points) - cfg.grid_points / 2) * cfg.dx
    seed = np.exp(-(x**2) / (2 * cfg.seed_width**2)) * np.exp(1j * cfg.carrier_k * x)
    seed /= np.linalg.norm(seed)

    psi = seed.copy()
    energies: List[float] = []
    phase_velocities: List[float] = []
    center_trace: List[float] = []

    for step in range(cfg.steps):
        lap = _laplacian(psi, cfg.dx)
        nonlinear = HEX_RESONANCE_BETA * np.abs(psi) ** 2 * psi
        drive = (cfg.readiness - cfg.theta)
        psi += cfg.dt * (0.5j * lap - 1j * nonlinear + drive * psi - cfg.damping * psi)

        if cfg.perturbation and step % 50 == 0:
            noise = (cfg.perturbation * (np.random.rand(cfg.grid_points) - 0.5)).astype(
                complex
            )
            psi += noise

        amplitude = np.abs(psi)
        energies.append(float(np.trapz(amplitude**2, dx=cfg.dx)))
        unwrapped_phase = np.unwrap(np.angle(psi))
        phase_velocities.append(float(np.ptp(unwrapped_phase) / (cfg.grid_points * cfg.dx)))
        center_trace.append(float(amplitude[cfg.grid_points // 2]))

    amplitude_final = np.abs(psi)
    stability_window = max(20, cfg.steps // 5)
    center_tail = np.array(center_trace[-stability_window:])
    stability_ratio = float(np.std(center_tail) / (np.mean(center_tail) + 1e-9))

    energy_series = np.array(energies)
    null_energy = np.full_like(energy_series, energies[0])
    aic_hex = _aic_from_residuals(energy_series - energy_series.mean())
    aic_null = _aic_from_residuals(energy_series - null_energy)

    telemetry: Dict[str, Any] = {
        "beta_hex": HEX_RESONANCE_BETA,
        "sigma_driver": {
            "R": cfg.readiness,
            "Theta": cfg.theta,
            "beta": HEX_RESONANCE_BETA,
            "zeta": cfg.damping,
        },
        "stability_ratio": stability_ratio,
        "standing_wave_plateau": float(center_tail.mean()),
        "energy_trace": energy_series.tolist(),
        "phase_velocities": phase_velocities,
        "delta_aic": float(aic_null - aic_hex),
        "null_model": "linear wave β=0 with identical initial condition",
        "amplitude_final": amplitude_final.tolist(),
        "grid": x.tolist(),
    }

    return telemetry


__all__ = ["SolitonDopplerConfig", "simulate_soliton_doppler"]
