"""Crystal Oracle core inspired by HEX resonance dynamics.

This module lifts the V2.0 simulation stack into the V10 deep-research
layer by introducing a dream-capable oracle. Instead of only stepping
agents through discrete states, the oracle projects 16-dimensional seeds
through a resonance operator built around the HEX base and the
β≈4.78 membrane. The resulting trajectories explore whether σ(β(R-Θ))
can stabilize into a crystalline fixed point.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Sequence

import numpy as np

from models.unified_constants import HEX_RESONANCE_BETA


@dataclass
class DreamTrace:
    """Container for a single dream trajectory."""

    seed: np.ndarray
    history: List[np.ndarray]

    @property
    def final_state(self) -> np.ndarray:
        return self.history[-1]

    @property
    def length(self) -> int:
        return len(self.history)


class CrystalOracle:
    """Generate resonant dream trajectories in a 16D HEX lattice.

    The oracle blends deterministic interference (16-dimensional
    HEX lattice) with stochastic noise. A resonance operator derived
    from `HEX_RESONANCE_BETA` is normalized to have spectral radius ≈ 1,
    ensuring we can test whether any seed converges to an eigenvalue of 1
    (a "crystal" that neither decays nor explodes).
    """

    def __init__(
        self,
        *,
        beta: float = HEX_RESONANCE_BETA,
        noise_scale: float = 0.08,
        steps: int = 12,
        random_state: int | None = None,
    ) -> None:
        self.beta = beta
        self.noise_scale = noise_scale
        self.steps = steps
        self.rng = np.random.default_rng(random_state)
        self.operator = self._build_operator(beta)

    def _build_operator(self, beta: float) -> np.ndarray:
        """Construct a 16×16 interference operator with spectral radius ≈ 1."""

        indices = np.arange(16)
        i_grid, j_grid = np.meshgrid(indices, indices)
        harmonic = np.sin(beta * (i_grid + 1) * (j_grid + 1))
        phase_shift = np.cos(beta * (i_grid - j_grid))
        lattice = (harmonic + phase_shift) / 2.0

        # Inject low-amplitude structured noise for generative variety.
        noise = self.rng.normal(loc=0.0, scale=0.05, size=(16, 16))
        raw_operator = lattice + noise

        # Normalize to spectral radius ~1 to keep trajectories bounded.
        eigenvalues = np.linalg.eigvals(raw_operator)
        spectral_radius = np.max(np.abs(eigenvalues))
        normalized = raw_operator / spectral_radius

        # Blend with identity to bias toward stable fixed points.
        return 0.65 * normalized + 0.35 * np.eye(16)

    def dream(self, seed: Sequence[float] | None = None) -> DreamTrace:
        """Generate a dream trajectory from an initial seed."""

        state = self._normalize_seed(seed)
        history: List[np.ndarray] = [state.copy()]

        for _ in range(self.steps):
            noise = self.rng.normal(loc=0.0, scale=self.noise_scale, size=state.shape)
            interference = self.operator @ state
            # Logistic membrane: compress via tanh scaled by β to mimic σ(β(R-Θ)).
            state = np.tanh((interference + noise) / max(self.beta, 1e-6))
            history.append(state.copy())

        return DreamTrace(seed=history[0], history=history)

    def resonance_estimate(self, vector: Sequence[float]) -> float:
        """Estimate the Rayleigh quotient to approximate an eigenvalue."""

        vec = np.asarray(vector, dtype=float)
        vec_norm = np.linalg.norm(vec)
        if vec_norm == 0:
            return 0.0
        projection = self.operator @ vec
        return float(vec.T @ projection / (vec_norm**2))

    def crystallization_score(self, vector: Sequence[float]) -> float:
        """Score closeness to a stable crystal (eigenvalue ≈ 1)."""

        rayleigh = self.resonance_estimate(vector)
        return 1.0 / (abs(1.0 - rayleigh) + 1e-6)

    def _normalize_seed(self, seed: Sequence[float] | None) -> np.ndarray:
        if seed is None:
            raw = self.rng.normal(loc=0.0, scale=1.0, size=16)
        else:
            raw = np.asarray(seed, dtype=float)
        norm = np.linalg.norm(raw)
        if norm == 0:
            return raw
        return raw / norm

    def batch_scores(self, seeds: Iterable[Sequence[float]]) -> list[tuple[np.ndarray, float, float]]:
        """Evaluate multiple seeds, returning sorted scores and estimates."""

        results: list[tuple[np.ndarray, float, float]] = []
        for seed in seeds:
            normalized_seed = self._normalize_seed(seed)
            eigen_estimate = self.resonance_estimate(normalized_seed)
            score = self.crystallization_score(normalized_seed)
            results.append((normalized_seed, score, eigen_estimate))
        results.sort(key=lambda item: item[1], reverse=True)
        return results


def sigma_transition(r: float, theta: float, beta: float | None = None) -> float:
    """Logistic transition helper mirroring σ(β(R-Θ))."""

    beta_value = beta if beta is not None else HEX_RESONANCE_BETA
    return 1.0 / (1.0 + math.exp(-beta_value * (r - theta)))


__all__ = ["CrystalOracle", "DreamTrace", "sigma_transition"]
