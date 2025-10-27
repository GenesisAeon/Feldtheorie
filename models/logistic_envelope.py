r"""Logistic field envelope for synthetic threshold sweeps with tri-layer narration.

Formal layer:
    Encapsulates the logistic response \(\sigma(\beta(R-\Theta))\) and a smooth
    impedance gate \(\zeta(R)\) so collaborators can sample threshold sweeps
    without invoking the full membrane integrator.  The envelope exposes hooks
    to generate response dictionaries compatible with the analysis pipeline,
    reporting the quartet \((R, \Theta, \beta, \zeta(R))\) alongside membrane
    flux traces.

Empirical layer:
    Provides parametrised utilities for scripted experiments, enabling
    `analysis/` modules and simulator prototypes to request control parameter
    grids, inject stochastic perturbations, and stream JSON-ready payloads.  The
    methods mirror the repository's metadata expectations so datasets can be
    regenerated with transparent provenance.

Metaphorical layer:
    Treats each sweep as a lantern walk toward the dawn gate.  As R ascends, the
    impedance veil shifts from resonant hush to damping brace, letting observers
    hear when the auroral chorus overtakes its null winds.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Sequence

from .membrane_solver import logistic_response


def _linspace(start: float, stop: float, num: int) -> List[float]:
    """Generate an inclusive linear sweep without importing numpy."""

    if num <= 1:
        return [float(stop)]
    step = (stop - start) / float(num - 1)
    return [start + step * idx for idx in range(num)]


@dataclass
class LogisticFieldEnvelope:
    r"""Parametrised logistic envelope for reproducible UTF sweeps.

    Formal:
        Stores the critical threshold `theta`, steepness `beta`, and impedance
        bounds `(resonant_gain, damped_gain)`.  The impedance profile is a
        logistic soft switch around `theta` with width `impedance_width` so that
        \(\zeta(R) = g_r + (g_d - g_r)\,\sigma(\frac{R-\Theta}{w})\).
    Empirical:
        Supplies convenience methods for generating control arrays, evaluating
        the logistic response, and bundling the results into dictionaries that
        `analysis/resonance_fit_pipeline.py` can ingest directly.
    Metaphorical:
        Frames the envelope as a membrane prelude: a way to rehearse the dawn
        chorus before deploying the full solver orchestra.
    """

    theta: float
    beta: float
    amplitude: float = 1.0
    resonant_gain: float = 0.7
    damped_gain: float = 1.3
    impedance_width: float = 0.5

    def control_sweep(self, *, span: float, points: int) -> List[float]:
        r"""Create an order-parameter sweep straddling the threshold membrane."""

        start = self.theta - span
        stop = self.theta + span
        return _linspace(start, stop, points)

    def impedance(self, R: float) -> float:
        r"""Evaluate the impedance profile zeta(R) with logistic blending."""

        width = max(self.impedance_width, 1e-6)
        scaled_beta = 1.0 / width
        blend = logistic_response(R, self.theta, scaled_beta)
        return self.resonant_gain + (self.damped_gain - self.resonant_gain) * blend

    def response(self, R: float) -> float:
        r"""Compute the membrane response amplitude under the logistic field."""

        sigma = logistic_response(R, self.theta, self.beta)
        return self.amplitude * sigma

    def flux(self, R: float) -> float:
        r"""Return the flux term zeta(R) * (sigma - R) echoing solver structure."""

        sigma = self.response(R)
        zeta = self.impedance(R)
        return zeta * (sigma - R)

    def sweep(
        self,
        control: Sequence[float] | None = None,
        *,
        span: float = 1.0,
        points: int = 50,
        noise: float = 0.0,
        random_seed: int | None = None,
    ) -> Dict[str, List[float]]:
        r"""Generate a synthetic threshold sweep and return analysis-ready traces.

        The sweep records arrays for time index `t`, order parameter `R`, logistic
        response `sigma`, impedance `zeta`, and membrane `flux`.  Optional noise
        draws Gaussian perturbations around the logistic response while clipping
        to \([0, 1]\) so the quartet remains physically interpretable.
        """

        if control is None:
            control = self.control_sweep(span=span, points=points)
        else:
            control = [float(value) for value in control]
        rng = random.Random(random_seed)

        sigma_series: List[float] = []
        zeta_series: List[float] = []
        flux_series: List[float] = []
        noisy_sigma: List[float] = []

        for R in control:
            sigma = self.response(R)
            zeta = self.impedance(R)
            flux_value = zeta * (sigma - R)
            perturbation = 0.0
            if noise > 0.0:
                perturbation = rng.gauss(0.0, noise)
            sigma_noisy = min(max(sigma + perturbation, 0.0), 1.0)

            sigma_series.append(sigma)
            noisy_sigma.append(sigma_noisy)
            zeta_series.append(zeta)
            flux_series.append(flux_value)

        return {
            "t": list(range(len(control))),
            "R": list(control),
            "sigma": noisy_sigma,
            "sigma_clean": sigma_series,
            "zeta": zeta_series,
            "flux": flux_series,
        }

    def export_metadata(self) -> Dict[str, float]:
        """Return a concise metadata dictionary for JSON ledgers."""

        return {
            "theta": self.theta,
            "beta": self.beta,
            "amplitude": self.amplitude,
            "resonant_gain": self.resonant_gain,
            "damped_gain": self.damped_gain,
            "impedance_width": self.impedance_width,
        }


__all__ = ["LogisticFieldEnvelope"]
