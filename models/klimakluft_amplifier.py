"""
Klimakluft Amplifier Module

Formal:
    Implements an inequality-aware emission redistribution where the effective
    steepness follows β_eff = β_base * (1 + Gini * Load). The logistic response
    σ(β(R-Θ)) tightens as inequality and load concentrate, mapping to amplified
    threshold sensitivity in downstream simulators.

Empirical:
    Designed for UTAC v3.0 experiments comparing null baselines (Gini≈0, Load≈0)
    against high-inequality scenarios. Calibration hooks allow sending β_eff to
    analysis pipelines for ΔAIC or R² tracking once empirical datasets land.

Poetic:
    The membrane feels the climate rift — as imbalance (Gini) and burden (Load)
    coil together, the β-slope steepens and σ(β(R-Θ)) leaps faster toward
    resonance.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass
class EmissionDistributor:
    """Distribute emissions under inequality-weighted β amplification.

    Parameters
    ----------
    beta_base:
        Baseline steepness controlling σ(β(R-Θ)) in the absence of inequality.
    gini:
        Gini coefficient (0–1) expressing inequality in the distribution.
    load:
        Load concentration (0–1) describing how emissions are clustered.
    """

    beta_base: float
    gini: float
    load: float

    def __post_init__(self) -> None:
        for name, value in ("beta_base", self.beta_base), ("gini", self.gini), ("load", self.load):
            if value < 0:
                raise ValueError(f"{name} must be non-negative, received {value}.")

    @property
    def beta_effective(self) -> float:
        """Compute β_eff = β_base * (1 + Gini * Load)."""

        return self.beta_base * (1 + self.gini * self.load)

    def amplify(self, emissions: Iterable[float]) -> list[float]:
        """Scale emissions by the effective β to mimic accelerated thresholding.

        Parameters
        ----------
        emissions:
            Sequence of emission values to be scaled.

        Returns
        -------
        List[float]
            Amplified emission values reflecting σ(β(R-Θ)) steepening.
        """

        beta_eff = self.beta_effective
        return [value * beta_eff for value in emissions]


if __name__ == "__main__":
    distributor = EmissionDistributor(beta_base=4.2, gini=0.35, load=0.8)
    baseline = [1.0, 1.5, 2.0]
    amplified = distributor.amplify(baseline)

    print("Baseline β:", distributor.beta_base)
    print("Effective β:", f"{distributor.beta_effective:.3f}")
    print("Input emissions:", baseline)
    print("Amplified emissions:", [f"{value:.3f}" for value in amplified])
