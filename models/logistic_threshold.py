r"""Universal Threshold Field logistic membrane simulation.

Formal stratum
---------------
Implements the logistic resonance \(\sigma(\beta(R-\Theta))\) coupled to an impedance
profile \(\zeta(R)\) to expose membrane transitions once the control parameter \(R\)
crosses the critical threshold \(\Theta\).  The module offers deterministic state
updates and contrastive null trajectories for falsifiability checks.

Empirical stratum
-----------------
Designed to stream simulated observations back into `analysis/` notebooks.  Each run
returns summary diagnostics—resonance gains, onset timing, null baselines—that can be
logged and compared with domain datasets housed in `data/`.

Metaphorical stratum
--------------------
Portrays the membrane as a dawn-lit veil: below \(\Theta\) the field is hushed, while
beyond it the logistic bloom ignites, modulated by the impedance chorus.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Mapping, MutableMapping

import numpy as np

ArrayLike = Iterable[float]
Zeta = Callable[[np.ndarray], np.ndarray]


def _default_impedance(r: np.ndarray) -> np.ndarray:
    """Return a unity impedance field.

    This keeps the membrane transparent so that only the logistic switch governs the
    resonance.  Downstream callers can supply richer impedance motifs reflecting
    coupling or damping conditions.
    """

    return np.ones_like(r)


@dataclass
class ThresholdMembrane:
    r"""Parametrised logistic membrane that exposes resonance diagnostics.

    Formal: evaluates \(\sigma(\beta(R-\Theta))\) with impedance scaling \(\zeta(R)\)
    over an input control signal \(R\).
    Empirical: returns structured summaries (gain ratios, onset index) ready for
    logging inside `analysis/` pipelines or for display within the `simulator/`
    interface.
    Metaphorical: paints the resonance as a membrane that sings when the dawn-value of
    \(R\) pierces \(\Theta\), its voice coloured by \(\zeta(R)\).
    """

    theta: float
    beta: float
    zeta: Zeta = field(default_factory=lambda: _default_impedance)

    def response(self, r: ArrayLike) -> np.ndarray:
        r"""Compute the logistic resonance field for control values ``r``.

        Parameters
        ----------
        r:
            Iterable of control parameter values representing \(R\).

        Returns
        -------
        numpy.ndarray
            Resonant response after logistic switching and impedance modulation.
        """

        r_arr = np.asarray(list(r), dtype=float)
        sigma = 1.0 / (1.0 + np.exp(-self.beta * (r_arr - self.theta)))
        return sigma * self.zeta(r_arr)

    @staticmethod
    def null_baseline(r: ArrayLike) -> np.ndarray:
        """Return a smooth null trajectory for falsification comparison.

        Uses a cubic Hermite-like smoothing by applying a softplus to the centered
        control parameter.  This mirrors a gradual response without a thresholded
        switch, offering a contrast to the membrane's abrupt activation.
        """

        r_arr = np.asarray(list(r), dtype=float)
        centered = r_arr - np.mean(r_arr)
        return np.log1p(np.exp(centered)) / np.log1p(np.exp(np.max(centered)))

    def compare_against_null(self, r: ArrayLike) -> Mapping[str, np.ndarray | float]:
        """Contrast the membrane response with a smooth null model.

        Returns the logistic resonance, null baseline, resonance gain (ratio of area
        under curves), and the discrete index where the logistic response first
        surpasses half-maximum, signalling practical threshold crossing.
        """

        r_arr = np.asarray(list(r), dtype=float)
        logistic = self.response(r_arr)
        null = self.null_baseline(r_arr)
        gain = float(np.trapz(logistic, r_arr) / np.trapz(null, r_arr))
        half_max = 0.5 * np.max(logistic)
        onset_idx = int(np.argmax(logistic >= half_max))
        return {
            "R": r_arr,
            "logistic": logistic,
            "null": null,
            "resonance_gain": gain,
            "half_max_index": onset_idx,
        }

    def export_summary(self, r: ArrayLike, store: MutableMapping[str, float] | None = None) -> MutableMapping[str, float]:
        r"""Emit a compact summary of the membrane state for downstream modules.

        Parameters
        ----------
        r:
            Iterable of control parameter samples used for diagnostics.
        store:
            Optional mutable mapping to populate; a new dictionary is created by
            default.  Enables direct writing into experiment logs or JSON payloads.

        Returns
        -------
        MutableMapping[str, float]
            Contains the calibrated threshold quartet \((R_\text{min}, R_\text{max},
            \Theta, \beta)\), impedance statistics, and resonance gain compared to the
            null baseline.
        """

        r_arr = np.asarray(list(r), dtype=float)
        comparison = self.compare_against_null(r_arr)
        target = store if store is not None else {}
        target.update(
            {
                "R_min": float(np.min(r_arr)),
                "R_max": float(np.max(r_arr)),
                "theta": float(self.theta),
                "beta": float(self.beta),
                "zeta_mean": float(np.mean(self.zeta(r_arr))),
                "resonance_gain": float(comparison["resonance_gain"]),
                "half_max_index": float(comparison["half_max_index"]),
            }
        )
        return target


if __name__ == "__main__":
    # Example pulse to demonstrate resonance metrics and provide quick validation.
    membrane = ThresholdMembrane(theta=0.4, beta=9.0)
    control = np.linspace(0.0, 1.0, 200)
    summary = membrane.export_summary(control)
    print("ThresholdMembrane quick-look summary:")
    for key, value in summary.items():
        print(f"  {key}: {value:.4f}")
