"""Per-layer σ_Φ monitoring for Grok's transformer architecture.

Provides hooks that attach to any ``torch.nn.Module`` layer and track
the coefficient of variation (σ_Φ proxy) of activations during the
forward pass.  When torch is unavailable, a numpy-based simulation
provides equivalent functionality for testing and development.

Usage:
    monitor = GrokLayerMonitor()
    monitor.attach_to_layer("encoder.layer.0", model)
    outputs = model(inputs)
    readings = monitor.get_readings()
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from theory.afet import AFETConstants

EPSILON = 1e-12


@dataclass(frozen=True)
class LayerReading:
    """Single σ_Φ reading from one layer at one forward pass."""

    layer_name: str
    sigma_phi: float
    mean_activation: float
    std_activation: float
    timestamp: float
    shape: tuple[int, ...]


@dataclass
class GrokLayerMonitor:
    """Per-layer σ_Φ tracker for transformer models.

    Attaches forward hooks to named layers and records activation
    statistics on every forward pass.  Provides real-time σ_Φ readings
    and historical tracking for drift analysis.
    """

    sigma_phi_threshold: float = AFETConstants.SIGMA_PHI
    critical_threshold: float = 0.055
    max_history: int = 10000
    _readings: list[LayerReading] = field(default_factory=list)
    _hooks: dict[str, Any] = field(default_factory=dict)
    _attached_layers: list[str] = field(default_factory=list)

    def _make_hook(self, layer_name: str):
        """Create a forward hook closure for the given layer name."""

        def hook_fn(module, input, output):
            arr = output
            # Convert torch tensor to numpy if needed
            if hasattr(arr, "detach"):
                arr = arr.detach().cpu().numpy()
            arr = np.asarray(arr, dtype=np.float64).flatten()

            mean_val = float(np.mean(arr))
            std_val = float(np.std(arr, ddof=0))
            sigma = std_val / max(abs(mean_val), EPSILON)

            reading = LayerReading(
                layer_name=layer_name,
                sigma_phi=sigma,
                mean_activation=mean_val,
                std_activation=std_val,
                timestamp=time.time(),
                shape=tuple(arr.shape),
            )
            self._readings.append(reading)

            # Enforce history limit
            if len(self._readings) > self.max_history:
                self._readings = self._readings[-self.max_history :]

        return hook_fn

    def attach_to_layer(self, layer_name: str, model: Any) -> bool:
        """Attach a forward hook to a named layer in the model.

        Parameters
        ----------
        layer_name : str
            Dot-separated path to the layer (e.g., ``encoder.layer.0``).
        model : torch.nn.Module or Any
            The model instance.

        Returns
        -------
        bool
            True if the hook was attached successfully.
        """
        target = model
        for part in layer_name.split("."):
            if hasattr(target, part):
                target = getattr(target, part)
            elif hasattr(target, "_modules") and part in target._modules:
                target = target._modules[part]
            else:
                return False

        if hasattr(target, "register_forward_hook"):
            handle = target.register_forward_hook(self._make_hook(layer_name))
            self._hooks[layer_name] = handle
            self._attached_layers.append(layer_name)
            return True
        return False

    def record_reading(
        self,
        layer_name: str,
        activations: np.ndarray,
    ) -> LayerReading:
        """Manually record a reading (useful for numpy-only testing).

        Parameters
        ----------
        layer_name : str
            Name of the layer.
        activations : np.ndarray
            Activation tensor to measure.
        """
        arr = np.asarray(activations, dtype=np.float64).flatten()
        mean_val = float(np.mean(arr))
        std_val = float(np.std(arr, ddof=0))
        sigma = std_val / max(abs(mean_val), EPSILON)

        reading = LayerReading(
            layer_name=layer_name,
            sigma_phi=sigma,
            mean_activation=mean_val,
            std_activation=std_val,
            timestamp=time.time(),
            shape=tuple(arr.shape),
        )
        self._readings.append(reading)

        # Enforce history limit
        if len(self._readings) > self.max_history:
            self._readings = self._readings[-self.max_history :]

        return reading

    def get_readings(self, layer_name: str | None = None) -> list[LayerReading]:
        """Return recorded readings, optionally filtered by layer."""
        if layer_name is None:
            return list(self._readings)
        return [r for r in self._readings if r.layer_name == layer_name]

    def get_latest(self, layer_name: str) -> LayerReading | None:
        """Return the most recent reading for a given layer."""
        for r in reversed(self._readings):
            if r.layer_name == layer_name:
                return r
        return None

    def get_sigma_phi_series(self, layer_name: str) -> list[float]:
        """Return time series of σ_Φ values for a given layer."""
        return [r.sigma_phi for r in self._readings if r.layer_name == layer_name]

    def get_drift_report(self, layer_name: str) -> dict[str, float]:
        """Compute drift statistics for a layer's σ_Φ history."""
        series = self.get_sigma_phi_series(layer_name)
        if not series:
            return {"n_readings": 0, "mean": 0.0, "std": 0.0, "drift": 0.0}

        arr = np.array(series)
        return {
            "n_readings": len(series),
            "mean": round(float(np.mean(arr)), 6),
            "std": round(float(np.std(arr)), 6),
            "min": round(float(np.min(arr)), 6),
            "max": round(float(np.max(arr)), 6),
            "drift": round(float(np.max(arr) - np.min(arr)), 6),
            "latest": round(series[-1], 6),
        }

    def detach_all(self) -> int:
        """Remove all forward hooks. Returns the number of hooks removed."""
        count = 0
        for name, handle in self._hooks.items():
            if hasattr(handle, "remove"):
                handle.remove()
            count += 1
        self._hooks.clear()
        return count

    def clear_history(self) -> None:
        """Clear all recorded readings."""
        self._readings.clear()

    @property
    def attached_layers(self) -> list[str]:
        return list(self._attached_layers)
