"""
Microtubule Resonance Model (Proxy)
==================================

Legt eine Proxy-Kopplung zwischen Gamma/Beta-Bändern und einer
konzeptuellen 13.5 MHz Resonanz an. Direkte Messungen bleiben
v10.x+ und benötigen Hochfrequenzsensorik.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass
class ResonanceProxyResult:
    gamma_beta_coupling: float
    proxy_alignment: float


def _bandpower(series: np.ndarray, low: float, high: float, fs: float) -> float:
    freqs = np.fft.rfftfreq(series.size, d=1.0 / fs)
    spectrum = np.abs(np.fft.rfft(series)) ** 2
    mask = (freqs >= low) & (freqs <= high)
    if not np.any(mask):
        return 0.0
    return float(np.mean(spectrum[mask]))


def estimate_resonance_proxy(series: Sequence[float], fs: float) -> ResonanceProxyResult:
    data = np.asarray(series, dtype=float)
    if data.size < 10:
        return ResonanceProxyResult(gamma_beta_coupling=0.0, proxy_alignment=0.0)

    gamma_power = _bandpower(data, 30.0, 100.0, fs)
    beta_power = _bandpower(data, 13.0, 30.0, fs)

    coupling = float(np.tanh(gamma_power / (beta_power + 1e-9)))
    alignment = float(1.0 - abs(gamma_power - beta_power) / (gamma_power + beta_power + 1e-9))

    return ResonanceProxyResult(gamma_beta_coupling=coupling, proxy_alignment=alignment)
