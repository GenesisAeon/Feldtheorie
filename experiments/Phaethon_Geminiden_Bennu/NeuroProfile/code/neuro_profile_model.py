"""
NeuroProfile Model
=================

Verknüpft β-Schätzung, σΦ-Proxy und Resonanzvergleich.
R, Θ, β und ζ(R) werden im Modellkontext explizit benannt,
σ(β(R-Θ)) bleibt als Kontrollfunktion präsent.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .beta_extractor_neuro import BetaEstimate, estimate_beta_from_series
from .microtubule_resonance import ResonanceProxyResult, estimate_resonance_proxy


@dataclass
class NeuroProfileConfig:
    sampling_rate: float = 256.0
    sigma_phi_target: float = 0.0625
    logistic_R: float = 0.42
    logistic_Theta: float = 0.68
    logistic_beta: float = 4.8
    zeta_R: float = 0.18


@dataclass
class NeuroProfileResult:
    beta_estimate: BetaEstimate
    sigma_phi_proxy: float
    resonance_proxy: ResonanceProxyResult


class NeuroProfileModel:
    def __init__(self, config: NeuroProfileConfig | None = None) -> None:
        self.config = config or NeuroProfileConfig()

    def preprocess(self, series: Sequence[float]) -> np.ndarray:
        data = np.asarray(series, dtype=float)
        if data.size == 0:
            return data
        return (data - np.mean(data)) / (np.std(data) + 1e-9)

    def estimate_sigma_phi_proxy(self, series: np.ndarray) -> float:
        # Proxy: normalized spectral entropy
        spectrum = np.abs(np.fft.rfft(series)) ** 2
        if spectrum.size == 0:
            return 0.0
        spectrum = spectrum / (np.sum(spectrum) + 1e-9)
        entropy = -np.sum(spectrum * np.log(spectrum + 1e-9))
        entropy_norm = entropy / np.log(spectrum.size + 1e-9)
        return float(entropy_norm)

    def analyze(self, series: Sequence[float]) -> NeuroProfileResult:
        prepared = self.preprocess(series)
        beta_estimate = estimate_beta_from_series(prepared)
        sigma_phi_proxy = self.estimate_sigma_phi_proxy(prepared)
        resonance_proxy = estimate_resonance_proxy(prepared, self.config.sampling_rate)
        return NeuroProfileResult(
            beta_estimate=beta_estimate,
            sigma_phi_proxy=sigma_phi_proxy,
            resonance_proxy=resonance_proxy,
        )


def run_demo() -> NeuroProfileResult:
    rng = np.random.default_rng(42)
    synthetic = rng.normal(0.0, 1.0, 2048)
    model = NeuroProfileModel()
    return model.analyze(synthetic)


if __name__ == "__main__":
    result = run_demo()
    print(result)
