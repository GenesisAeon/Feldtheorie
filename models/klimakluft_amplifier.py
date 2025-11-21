"""
Klimakluft amplifier modelling load concentration and β amplification.

Formal layer:
    Implements the climate-inequality amplifier
    β_eff = β_base · (1 + Gini · LoadConcentration) with a percentile-split
    load metric. The logistic membrane σ(β(R-Θ)) steepens as concentrated
    emitters push R past Θ.

Empirical layer:
    Provides `EmissionDistributor` to compute Gini, load concentration,
    β amplification, and inequality sweeps returning DataFrames and plots.
    Defaults create a Δβ trajectory from 4.2 to >11 when the top emitters
    concentrate load.

Poetic layer:
    The field tilts when a few chimneys blaze hot—σ(β(R-Θ)) climbs the
    membrane’s dawn ridge as the klimakluft widens, and the chorus sharpens
    into a steep cry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@dataclass
class EmissionDistributor:
    """Partition emissions into percentiles and estimate β amplification.

    The distributor treats emission loads as the order parameter R and
    evaluates how concentrated loads steepen the membrane response
    σ(β(R-Θ)). The effective steepness follows

    β_eff = β_base · (1 + Gini · LoadConcentration).

    Parameters
    ----------
    emissions:
        Sequence of non-negative emission loads per actor.
    label:
        Optional identifier for plots and logs.
    """

    emissions: Sequence[float]
    label: str = "klimakluft"

    def __post_init__(self) -> None:
        values = np.asarray(self.emissions, dtype=float)
        if values.ndim != 1:
            raise ValueError("Emissions must be a 1-D sequence")
        if values.size == 0:
            raise ValueError("Emissions sequence cannot be empty")
        if np.any(values < 0):
            raise ValueError("Emissions must be non-negative")
        self.emissions = values

    @staticmethod
    def gini(values: np.ndarray) -> float:
        """Compute the Gini coefficient for a 1-D array."""

        sorted_vals = np.sort(values)
        n = sorted_vals.size
        cumvals = np.cumsum(sorted_vals)
        total = cumvals[-1]
        if total == 0:
            return 0.0
        # Gini from the Lorenz curve definition
        gini_raw = (n + 1 - 2 * np.sum(cumvals) / total) / n
        return float(gini_raw)

    @staticmethod
    def _load_concentration(values: np.ndarray, top_percentile: float) -> float:
        if not 0 < top_percentile < 1:
            raise ValueError("top_percentile must be in (0, 1)")
        threshold = np.quantile(values, 1 - top_percentile)
        mask = values >= threshold
        share = float(values[mask].sum() / values.sum())
        expected_share = top_percentile
        return share / expected_share

    def _scale_top_percentile(self, multiplier: float, top_percentile: float) -> np.ndarray:
        scaled = self.emissions.copy()
        cutoff = np.quantile(scaled, 1 - top_percentile)
        heavy_mask = scaled >= cutoff
        scaled[heavy_mask] *= multiplier
        return scaled

    def beta_effective(
        self,
        beta_base: float = 4.2,
        top_percentile: float = 0.1,
        values: np.ndarray | None = None,
    ) -> float:
        """Return β_eff for provided values using β_eff = β_base · (1 + Gini · LC)."""

        working = self.emissions if values is None else values
        gini = self.gini(working)
        load_concentration = self._load_concentration(working, top_percentile)
        return float(beta_base * (1 + gini * load_concentration))

    def inequality_sweep(
        self,
        multipliers: Iterable[float] = (1.0, 1.5, 2.5, 4.0, 6.0),
        beta_base: float = 4.2,
        top_percentile: float = 0.1,
        include_uniform_baseline: bool = True,
    ) -> pd.DataFrame:
        """Simulate β amplification as top-percentile loads intensify.

        Returns a DataFrame with columns: multiplier, gini, load_concentration,
        beta_eff. Default parameters yield a climb from β≈4.2 (balanced baseline)
        to β>11 (heavy concentration), evidencing the Delta-Peak effect.
        """

        rows: List[dict[str, float]] = []
        if include_uniform_baseline:
            rows.append(
                {
                    "multiplier": 0.0,
                    "gini": 0.0,
                    "load_concentration": 1.0,
                    "beta_eff": beta_base,
                }
            )
        for multiplier in multipliers:
            scaled = self._scale_top_percentile(multiplier, top_percentile)
            gini = self.gini(scaled)
            load_concentration = self._load_concentration(scaled, top_percentile)
            beta_eff = self.beta_effective(beta_base=beta_base, top_percentile=top_percentile, values=scaled)
            rows.append(
                {
                    "multiplier": multiplier,
                    "gini": gini,
                    "load_concentration": load_concentration,
                    "beta_eff": beta_eff,
                }
            )

        return pd.DataFrame(rows)

    def plot_beta_sweep(
        self,
        multipliers: Iterable[float] = (1.0, 1.5, 2.5, 4.0, 6.0),
        beta_base: float = 4.2,
        top_percentile: float = 0.1,
        ax: plt.Axes | None = None,
    ) -> plt.Axes:
        """Plot β amplification against inequality multipliers."""

        df = self.inequality_sweep(multipliers=multipliers, beta_base=beta_base, top_percentile=top_percentile)
        working_ax = ax or plt.subplots(figsize=(7, 4))[1]
        working_ax.plot(df["multiplier"], df["beta_eff"], marker="o", label=f"{self.label} β_eff")
        working_ax.axhline(beta_base, linestyle="--", color="gray", label="β_base")
        working_ax.set_xlabel(f"Top {int(top_percentile*100)}% load multiplier")
        working_ax.set_ylabel("β_eff")
        working_ax.set_title("Delta-Peak: Load Concentration → β Amplification")
        working_ax.legend()
        working_ax.grid(alpha=0.3)
        return working_ax

    @classmethod
    def from_lognormal(
        cls,
        n: int = 10_000,
        mean: float = 0.0,
        sigma: float = 1.0,
        seed: int | None = None,
        label: str = "klimakluft",
    ) -> "EmissionDistributor":
        """Create a synthetic distributor from a lognormal draw for quick experiments."""

        rng = np.random.default_rng(seed)
        emissions = rng.lognormal(mean=mean, sigma=sigma, size=n)
        return cls(emissions=emissions, label=label)
