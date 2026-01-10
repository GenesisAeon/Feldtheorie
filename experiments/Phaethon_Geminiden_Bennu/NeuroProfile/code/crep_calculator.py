"""
CREP Calculator
===============

Part of the GenesisAeon Feldtheorie project.
License: LGPL-3.0-or-later

Operationalisiert CREP (Coherence, Resonance, Emergence, Potential) als
gleichgewichtete Skala. R, Θ, β und ζ(R) werden in den Komponenten
protokollierbar gehalten, während σ(β(R-Θ)) durch klare Normierung
stabil bleibt.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .microtubule_resonance import estimate_resonance_proxy


@dataclass
class CrepResult:
    coherence: float
    resonance: float
    emergence: float
    potential: float
    aggregate: float


def _collapse_to_signal(data: np.ndarray) -> np.ndarray:
    if data.ndim == 1:
        return data
    if data.shape[0] > data.shape[1]:
        return np.mean(data, axis=1)
    return np.mean(data, axis=0)


def _coherence(eeg_data: np.ndarray) -> float:
    if eeg_data.ndim == 1:
        return 1.0 if eeg_data.size else 0.0
    if eeg_data.shape[0] > eeg_data.shape[1]:
        corr = np.corrcoef(eeg_data, rowvar=False)
    else:
        corr = np.corrcoef(eeg_data)
    if corr.size == 0 or corr.ndim != 2:
        return 0.0
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    values = np.abs(corr[mask])
    if values.size == 0:
        return 0.0
    return float(np.clip(values.mean(), 0.0, 1.0))


def compute_crep(
    beta: float,
    sigma_phi: float,
    eeg_data: Sequence[float] | np.ndarray,
    fs: float,
    *,
    sigma_phi_target: float = 0.0625,
    beta_baseline: float = 7.4,
) -> CrepResult:
    data = np.asarray(eeg_data, dtype=float)
    coherence = _coherence(data)
    signal = _collapse_to_signal(data)
    resonance_proxy = estimate_resonance_proxy(signal, fs)
    resonance = float(np.clip(resonance_proxy.gamma_beta_coupling, 0.0, 1.0))
    emergence = float(np.clip(min(1.0, beta / beta_baseline), 0.0, 1.0))
    potential = float(np.exp(-10.0 * abs(sigma_phi - sigma_phi_target)))
    aggregate = float(np.clip((coherence + resonance + emergence + potential) / 4.0, 0.0, 1.0))
    return CrepResult(
        coherence=coherence,
        resonance=resonance,
        emergence=emergence,
        potential=potential,
        aggregate=aggregate,
    )
