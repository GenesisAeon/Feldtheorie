"""
Implosive Genesis Engine — inverted sigmoid rollout for Type-6 TAC dynamics.

This module simulates a high-density start (R ≫ Θ) that unfolds through an
inverted sigmoid S(R) = 1 / (1 + exp(+β(R - Θ))). The curve captures the
implosive-to-expansive transition as the membrane relaxes and σ(β(R-Θ)) shifts
from compression to resonance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def inverted_sigmoid(R: np.ndarray, beta: float, theta: float) -> np.ndarray:
    """Compute the inverted sigmoid S(R) = 1 / (1 + exp(+β(R - Θ)))."""

    return 1.0 / (1.0 + np.exp(beta * (R - theta)))


@dataclass
class ImplosiveGenesisResult:
    R: np.ndarray
    S: np.ndarray
    phases: np.ndarray

    def to_frame(self) -> pd.DataFrame:
        """Return the simulation as a tidy DataFrame."""

        return pd.DataFrame({"R": self.R, "S": self.S, "phase": self.phases})


def simulate_implosive_genesis(
    beta: float = 6.5,
    theta: float = 0.35,
    start: float = 1.2,
    end: float = -0.1,
    steps: int = 400,
) -> ImplosiveGenesisResult:
    """Run an implosive genesis sweep for TAC Type-6 dynamics.

    Parameters
    ----------
    beta:
        Steepness of the inverted sigmoid gate.
    theta:
        Threshold where compression flips to expansion.
    start, end:
        Bounds for the order parameter R; start>Θ models the compressed state.
    steps:
        Number of samples across the sweep.
    """

    R = np.linspace(start, end, steps)
    S = inverted_sigmoid(R, beta=beta, theta=theta)

    phases = np.where(
        R > theta,
        "compressed",
        np.where(R > theta - 0.1, "transition", "expanded"),
    )

    return ImplosiveGenesisResult(R=R, S=S, phases=phases)


def plot_implosive_genesis(
    beta: float = 6.5,
    theta: float = 0.35,
    start: float = 1.2,
    end: float = -0.1,
    steps: int = 400,
    ax: plt.Axes | None = None,
) -> Tuple[ImplosiveGenesisResult, plt.Axes]:
    """Simulate and plot the implosive → expansive transition."""

    result = simulate_implosive_genesis(beta=beta, theta=theta, start=start, end=end, steps=steps)
    working_ax = ax or plt.subplots(figsize=(7, 4))[1]
    frame = result.to_frame()
    working_ax.plot(frame["R"], frame["S"], label="S(R) inverted")
    working_ax.axvline(theta, color="red", linestyle="--", label="Θ (phase gate)")
    working_ax.set_xlabel("R (density → expansion)")
    working_ax.set_ylabel("S(R)")
    working_ax.set_title("Implosive Genesis: inverted sigmoid unfolding")
    working_ax.legend()
    working_ax.grid(alpha=0.3)
    return result, working_ax
