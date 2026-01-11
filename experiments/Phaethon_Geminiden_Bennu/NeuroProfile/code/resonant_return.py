"""
Resonant Return Module
======================

Implements the v11 Resonant-Return layer for NeuroProfile.
β-Fits on velocity dispersion, σΦ proxies, and v_RIG alignment
stay aligned with σ(β(R-Θ)) to keep ζ(R) damped.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .beta_extractor_neuro import BetaEstimate, estimate_beta_from_series


@dataclass
class ResonantReturnConfig:
    sigma_phi_target: float = 0.0625
    v_rig_target_kms: float = 1.352


@dataclass
class ResonantReturnNullModels:
    best_model: str
    aic: dict[str, float]
    delta_aic: dict[str, float]
    parameters: dict[str, dict[str, float]]


@dataclass
class ResonantReturnResult:
    beta_velocity_fit: BetaEstimate
    velocity_dispersion: float
    sigma_phi_proxy: float
    v_rig_target_kms: float
    v_rig_alignment: float
    null_models: ResonantReturnNullModels


def _aic(rss: float, n: int, k: int) -> float:
    return float(n * np.log(rss / n + 1e-12) + 2 * k)


def _fit_null_models(series: np.ndarray) -> ResonantReturnNullModels:
    if series.size == 0:
        return ResonantReturnNullModels(
            best_model="constant",
            aic={"constant": 0.0, "linear": 0.0, "power_law": 0.0},
            delta_aic={"constant": 0.0, "linear": 0.0, "power_law": 0.0},
            parameters={
                "constant": {"mean": 0.0},
                "linear": {"slope": 0.0, "intercept": 0.0},
                "power_law": {"a": 0.0, "b": 0.0},
            },
        )

    y = np.abs(series)
    x = np.arange(1, y.size + 1, dtype=float)

    y_mean = float(np.mean(y))
    rss_const = float(np.sum((y - y_mean) ** 2))
    aic_const = _aic(rss_const, y.size, 1)

    x_mat = np.column_stack((np.ones_like(x), x))
    coef, *_ = np.linalg.lstsq(x_mat, y, rcond=None)
    intercept, slope = coef
    y_pred_lin = intercept + slope * x
    rss_lin = float(np.sum((y - y_pred_lin) ** 2))
    aic_lin = _aic(rss_lin, y.size, 2)

    log_x = np.log(x)
    log_y = np.log(y + 1e-12)
    pl_coef, *_ = np.linalg.lstsq(np.column_stack((np.ones_like(log_x), log_x)), log_y, rcond=None)
    log_a, b = pl_coef
    a = float(np.exp(log_a))
    y_pred_pl = a * (x**b)
    rss_pl = float(np.sum((y - y_pred_pl) ** 2))
    aic_pl = _aic(rss_pl, y.size, 2)

    aic = {"constant": aic_const, "linear": aic_lin, "power_law": aic_pl}
    min_aic = min(aic.values())
    delta_aic = {name: float(value - min_aic) for name, value in aic.items()}
    best_model = min(aic, key=aic.get)

    return ResonantReturnNullModels(
        best_model=best_model,
        aic=aic,
        delta_aic=delta_aic,
        parameters={
            "constant": {"mean": y_mean},
            "linear": {"intercept": float(intercept), "slope": float(slope)},
            "power_law": {"a": float(a), "b": float(b)},
        },
    )


def _sigma_phi_proxy(series: np.ndarray) -> float:
    spectrum = np.abs(np.fft.rfft(series)) ** 2
    if spectrum.size == 0:
        return 0.0
    spectrum = spectrum / (np.sum(spectrum) + 1e-9)
    entropy = -np.sum(spectrum * np.log(spectrum + 1e-9))
    entropy_norm = entropy / np.log(spectrum.size + 1e-9)
    return float(entropy_norm)


def _velocity_series(series: np.ndarray) -> np.ndarray:
    if series.size == 0:
        return series
    return np.abs(np.diff(series, prepend=series[0]))


def analyze_resonant_return(
    series: np.ndarray,
    *,
    config: ResonantReturnConfig | None = None,
) -> ResonantReturnResult:
    config = config or ResonantReturnConfig()
    velocity_series = _velocity_series(series)
    beta_velocity_fit = estimate_beta_from_series(velocity_series)
    sigma_phi_proxy = _sigma_phi_proxy(velocity_series)
    velocity_dispersion = float(np.std(velocity_series))
    v_rig_alignment = max(
        0.0,
        1.0 - abs(velocity_dispersion - config.v_rig_target_kms) / (config.v_rig_target_kms + 1e-9),
    )
    null_models = _fit_null_models(velocity_series)

    return ResonantReturnResult(
        beta_velocity_fit=beta_velocity_fit,
        velocity_dispersion=velocity_dispersion,
        sigma_phi_proxy=sigma_phi_proxy,
        v_rig_target_kms=config.v_rig_target_kms,
        v_rig_alignment=v_rig_alignment,
        null_models=null_models,
    )
