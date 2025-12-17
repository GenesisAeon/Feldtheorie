"""Early warning analytics for critical slowing down in the Lantern-Net.

Tracks Φ (integrated information proxy) and R (coherence) to surface rising
lag-1 autocorrelation and variance—signatures that σ(β(R-Θ)) is flattening
before collapse. Designed for Phase VI "Pre-Cognition Engine" experiments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np


@dataclass
class EarlyWarningSystem:
    """Rolling estimator for critical slowing down signals on Φ."""

    window: int = 50
    alert_threshold: float = 0.8
    phi_history: List[float] = field(default_factory=list)
    coherence_history: List[float] = field(default_factory=list)
    alert_step: Optional[int] = None

    def update(self, phi: float, coherence: float) -> Dict[str, float]:
        """Record latest Φ/R values and update diagnostics."""
        self.phi_history.append(float(phi))
        self.coherence_history.append(float(coherence))
        metrics = self.compute_metrics()
        if self.alert_step is None and metrics["lag1_autocorr_phi"] >= self.alert_threshold:
            self.alert_step = len(self.phi_history) - 1
        return metrics

    def compute_metrics(self) -> Dict[str, float]:
        """Return rolling lag-1 autocorrelation and variance for Φ."""
        phi_window = self._windowed_phi()
        lag1 = self._lag1_autocorr(phi_window)
        variance = float(np.var(phi_window)) if phi_window.size else 0.0
        return {
            "lag1_autocorr_phi": lag1,
            "variance_phi": variance,
            "latest_phi": float(phi_window[-1]) if phi_window.size else 0.0,
        }

    def _windowed_phi(self) -> np.ndarray:
        if self.window <= 0:
            return np.array(self.phi_history, dtype=float)
        return np.array(self.phi_history[-self.window :], dtype=float)

    @staticmethod
    def _lag1_autocorr(series: np.ndarray) -> float:
        if series.size < 2:
            return 0.0
        series_centered = series - np.mean(series)
        variance = np.var(series_centered)
        if variance < 1e-12:
            return 0.0
        numerator = np.dot(series_centered[:-1], series_centered[1:]) / (series_centered.size - 1)
        return float(numerator / variance)

    def reset(self) -> None:
        """Clear stored histories and alert state."""
        self.phi_history.clear()
        self.coherence_history.clear()
        self.alert_step = None


__all__ = ["EarlyWarningSystem"]
