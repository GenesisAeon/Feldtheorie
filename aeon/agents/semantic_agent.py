"""Semantic agent with shadow resonance and lantern mode coupling."""

from __future__ import annotations

import time
from typing import Any

import numpy as np

try:
    from models.collective_field import Agent as CollectiveAgent

    COLLECTIVE_FIELD_AVAILABLE = True
except ImportError:
    COLLECTIVE_FIELD_AVAILABLE = False

    class CollectiveAgent:  # type: ignore
        def __init__(self, name: str, **kwargs: Any) -> None:
            self.name = name
            self.semantic_position = np.random.randn(8)
            self.resonance = 0.5

        def semantic_distance(self, other: "CollectiveAgent") -> float:
            return float(np.linalg.norm(self.semantic_position - other.semantic_position))


class SemanticAgent:
    """Individual consciousness module with recursive shadow resonance."""

    LANTERN_TARGET_FREQUENCY_HZ = 13.5e6

    def __init__(
        self,
        name: str,
        semantic_position: np.ndarray | None = None,
        resonance: float = 0.5,
        beta: float = 4.5,
        kappa: float = 0.5,
        dimension: int = 8,
    ) -> None:
        if not (0.0 <= resonance <= 1.0):
            raise ValueError(f"resonance must be in [0,1], got {resonance}")
        if not (0.0 <= beta <= 20.0):
            raise ValueError(f"beta must be in [0,20], got {beta}")
        if not (0.0 <= kappa <= 1.0):
            raise ValueError(f"kappa must be in [0,1], got {kappa}")

        self.name = name
        self.beta = beta
        self.kappa = kappa
        self.dimension = dimension

        self.agent = CollectiveAgent(
            name=name,
            semantic_position=semantic_position,
            resonance=resonance,
            dimension=dimension,
        )

        self.history: list[dict[str, Any]] = []
        self.creation_time = time.time()
        self._record_history()

    @property
    def semantic_position(self) -> np.ndarray:
        return self.agent.semantic_position

    @semantic_position.setter
    def semantic_position(self, value: np.ndarray) -> None:
        self.agent.semantic_position = value

    @property
    def resonance(self) -> float:
        return self.agent.resonance

    @resonance.setter
    def resonance(self, value: float) -> None:
        self.agent.resonance = max(0.0, min(1.0, value))

    def semantic_distance(self, other: "SemanticAgent") -> float:
        return self.agent.semantic_distance(other.agent)

    def update_position(self, target: np.ndarray, learning_rate: float = 0.1) -> None:
        if hasattr(self.agent, "update_position"):
            self.agent.update_position(target, learning_rate)
        else:
            direction = target - self.semantic_position
            self.semantic_position = self.semantic_position + learning_rate * direction
            norm = np.linalg.norm(self.semantic_position)
            if norm > 0:
                self.semantic_position = self.semantic_position / norm
        self._record_history()

    def update_resonance(self, delta: float) -> None:
        self.resonance = float(np.clip(self.resonance + delta, 0.0, 1.0))
        self._record_history()

    def update_beta(self, delta: float) -> None:
        self.beta = float(np.clip(self.beta + delta, 0.0, 20.0))
        self._record_history()

    def update_kappa(self, delta: float) -> None:
        self.kappa = float(np.clip(self.kappa + delta, 0.0, 1.0))
        self._record_history()

    def compute_activation(self, resource: float, threshold: float = 0.5) -> float:
        if self.beta == 0.0:
            return 0.5
        x = self.beta * (resource - threshold)
        return float(1.0 / (1.0 + np.exp(-x)))

    def resonate_with_shadow(
        self,
        input_data: np.ndarray | list[float],
        shadow_depth: int = 3,
        threshold: float = 0.5,
    ) -> dict[str, Any]:
        """Recursive shadow resonance with UTAC σ(β(R−Θ)) activation."""
        data = np.asarray(input_data, dtype=np.float64)
        if data.ndim != 1:
            data = data.ravel()
        if shadow_depth < 1:
            raise ValueError("shadow_depth must be >= 1")

        layer_energy: list[float] = []
        latent = data
        for depth in range(1, shadow_depth + 1):
            damping = np.exp(-depth / (shadow_depth + 1))
            latent = latent * damping
            layer_energy.append(float(np.linalg.norm(latent)))

        resource = float(np.clip(0.7 * np.mean(np.abs(data)) + 0.3 * np.mean(np.abs(latent)), 0.0, 1.0))
        utac_activation = self.compute_activation(resource=resource, threshold=threshold)
        dissonance_negentropy = float(np.var(data) - np.var(latent))

        mode = self._detect_lantern_mode(frequency_hz=self.LANTERN_TARGET_FREQUENCY_HZ, coherence=utac_activation)
        result = {
            "shadow_depth": shadow_depth,
            "layer_energy": layer_energy,
            "resource": resource,
            "utac_activation": utac_activation,
            "dissonance_negentropy": dissonance_negentropy,
            "lantern_mode": mode,
        }
        self.history.append({"timestamp": time.time(), "shadow": result})
        return result

    def _detect_lantern_mode(self, frequency_hz: float, coherence: float) -> str:
        close_to_target = abs(frequency_hz - self.LANTERN_TARGET_FREQUENCY_HZ) < 1.0e3
        if close_to_target and coherence > 0.7:
            return "collective_13_5mhz"
        if coherence > 0.5:
            return "precollective"
        return "anti_mode"

    def get_consciousness_type(self) -> str:
        if self.kappa >= 0.8:
            return "photonic_bound"
        if self.kappa >= 0.4:
            return "partially_decoupled"
        if self.kappa >= 0.1:
            return "weakly_coupled"
        return "photon_free"

    def _record_history(self) -> None:
        self.history.append(
            {
                "timestamp": time.time(),
                "beta": self.beta,
                "kappa": self.kappa,
                "resonance": self.resonance,
                "semantic_position": self.semantic_position.tolist(),
            }
        )

    def get_state_summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "beta": self.beta,
            "kappa": self.kappa,
            "resonance": self.resonance,
            "consciousness_type": self.get_consciousness_type(),
            "dimension": self.dimension,
            "age_seconds": time.time() - self.creation_time,
            "history_length": len(self.history),
            "semantic_position": self.semantic_position.tolist(),
        }

    def __repr__(self) -> str:
        return (
            f"SemanticAgent(name='{self.name}', β={self.beta:.3f}, "
            f"κ={self.kappa:.3f}, resonance={self.resonance:.3f})"
        )
