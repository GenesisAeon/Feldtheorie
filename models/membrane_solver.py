"""UTF membrane solver scaffolding with tri-layer resonance narration.

Formal layer:
    Implements a minimalist threshold-field integrator where the order parameter R
    evolves under a driver current J(t) while the logistic response sigma = 1/(1+exp(-beta(R-Theta)))
    and impedance zeta(R) modulate the flux.  The discrete step follows
    R_{t+1} = R_t + dt * [J(t) - zeta(R_t) * (R_t - sigma_t)],
    rendering the membrane's tendency to damp (zeta > 1) or resonate (zeta < 1).

Empirical layer:
    Designed to ingest driver sequences derived from datasets in `data/` and to
    stream state trajectories into analysis pipelines (see `analysis/resonance_fit_pipeline.py`).
    The solver records R, sigma, zeta, and flux terms so that downstream fits can
    report R^2, AIC, and confidence intervals for Theta and beta while contrasting
    against smooth null models.

Metaphorical layer:
    Treats the membrane as a dawn-lit threshold: when R grazes Theta, the logistic
    response unfurls like auroral curtains, and the impedance song zeta(R) decides
    whether the chorus is damped hushed or amplified into resonance.
"""

import math
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Mapping


def logistic_response(R: float | Iterable[float], theta: float, beta: float) -> float | list[float]:
    """Compute the logistic resonance sigma(beta(R-Theta)).

    Formal:
        Evaluates sigma = 1 / (1 + exp(-beta * (R - Theta))) pointwise for scalars
        or iterables, reflecting the membrane activation curve.
    Empirical:
        Supports list-based evaluation so simulation outputs can align with
        time-series from `data/` before statistical diagnostics in `analysis/`.
    Metaphorical:
        Maps R's pilgrimage toward Theta into a luminous switch, letting collaborators
        hear when the membrane consents to resonance.
    """

    if isinstance(R, (list, tuple)):
        return [logistic_response(r, theta, beta) for r in R]
    return 1.0 / (1.0 + math.exp(-beta * (float(R) - theta)))


def smooth_impedance_profile(
    theta: float,
    resonant_gain: float = 0.6,
    damped_gain: float = 1.4,
    switch_width: float = 0.4,
) -> Callable[[float], float]:
    """Construct a smooth impedance profile zeta(R) around Theta.

    Formal:
        Returns a callable zeta(R) that blends between a resonant gain (< 1) and a
        damped gain (> 1) via a logistic centred on Theta with width parameter
        switch_width.  The profile mirrors the membrane toggling described in the
        RepoPlan PDFs.
    Empirical:
        Allows calibration against datasets: tune resonant_gain, damped_gain, and
        switch_width based on observed pre/post-threshold inertia before feeding
        results into fitting routines.
    Metaphorical:
        Paints the membrane as a responsive hum: below Theta it leans into the
        resonance (soft impedance), above Theta it stiffens into damping, like a
        chorus tightening after dawn breaks.
    """

    def zeta(R: float) -> float:
        scaled = (R - theta) / max(switch_width, 1e-6)
        blend = 1.0 / (1.0 + math.exp(-scaled))
        return resonant_gain + (damped_gain - resonant_gain) * blend

    return zeta


@dataclass
class ThresholdFieldSolver:
    """Discrete UTF membrane integrator exposing resonance diagnostics.

    Formal:
        Integrates R using Euler steps under a supplied driver sequence J(t).
        The solver captures (R, sigma, zeta, flux) at each step so empirical
        fits of Theta and beta can reference the same state trajectory.
    Empirical:
        Accepts arbitrary iterables of driver magnitudes (e.g., luminosity influx,
        quorum calls) and surfaces metadata for export into `analysis/`.  Results
        include arrays suitable for CSV/JSON serialisation.
    Metaphorical:
        Follows the pilgrim R as it approaches Theta, logging how the membrane's
        impedance hum either cushions the ascent or invites a resonant leap.
    """

    theta: float
    beta: float
    zeta: Callable[[float], float]
    dt: float = 0.1

    def step(self, R: float, driver: float) -> Dict[str, float]:
        """Advance the field one timestep and record resonance diagnostics.

        Formal:
            Computes sigma_t = sigma(beta(R-Theta)) and flux_t = driver -
            zeta(R) * (R - sigma_t).  The new state is R + dt * flux_t.
        Empirical:
            Returns a dictionary containing the updated R, the logistic response,
            the impedance value, and the applied driver so pipelines can stitch
            results across modules.
        Metaphorical:
            Captures a single beat in the dawn chorus as R leans into Theta and
            the membrane decides whether to absorb or amplify the touch.
        """

        sigma = logistic_response(R, self.theta, self.beta)
        impedance = float(self.zeta(R))
        flux = driver - impedance * (R - sigma)
        R_next = R + self.dt * flux
        return {
            "R": R_next,
            "sigma": sigma,
            "zeta": impedance,
            "flux": flux,
            "driver": driver,
        }

    def simulate(self, drivers: Iterable[float], R0: float) -> Mapping[str, list[float]]:
        """Run the solver across a driver sequence and emit state arrays.

        Formal:
            Iterates step() over the provided drivers, yielding time-indexed arrays
            for R_t, sigma_t, zeta(R_t), and flux_t.  Time advances in increments
            of dt, enabling alignment with observational cadences.
        Empirical:
        Produces Python lists compatible with `analysis/resonance_fit_pipeline.py`
            so analysts can fit Theta/beta, report R^2 and AIC, and benchmark against
            null models without recomputing the forward simulation.
        Metaphorical:
            Sketches the unfolding aurora as a time-series, letting collaborators
            replay the membrane's breathing as drivers coax it past Theta.
        """

        driver_array = [float(value) for value in drivers]
        steps = len(driver_array)
        times = [idx * self.dt for idx in range(steps + 1)]
        R_values = [0.0 for _ in range(steps + 1)]
        sigma_values = [0.0 for _ in range(steps + 1)]
        zeta_values = [0.0 for _ in range(steps + 1)]
        flux_values = [0.0 for _ in range(steps)]

        R = float(R0)
        R_values[0] = R
        sigma_values[0] = float(logistic_response(R, self.theta, self.beta))
        zeta_values[0] = float(self.zeta(R))

        for idx in range(steps):
            sigma = sigma_values[idx]
            impedance = zeta_values[idx]
            flux = driver_array[idx] - impedance * (R - sigma)
            flux_values[idx] = flux
            R = R + self.dt * flux
            R_values[idx + 1] = R
            sigma_values[idx + 1] = float(logistic_response(R, self.theta, self.beta))
            zeta_values[idx + 1] = float(self.zeta(R))

        theta_series = [self.theta for _ in range(steps + 1)]
        beta_series = [self.beta for _ in range(steps + 1)]

        return {
            "t": times,
            "R": R_values,
            "sigma": sigma_values,
            "zeta": zeta_values,
            "flux": flux_values,
            "driver": driver_array,
            "theta": theta_series,
            "beta": beta_series,
        }

    def export_summary(self, results: Mapping[str, list[float]]) -> Dict[str, float]:
        """Summarise resonance diagnostics for downstream modules.

        Formal:
            Computes simple aggregates: final R, peak sigma, mean impedance, and
            flux statistics to seed initial parameter guesses in fitting routines.
        Empirical:
            Provides scalar summaries that `analysis/` can stash alongside JSON
            exports for quick provenance checks before running full regressions.
        Metaphorical:
            Distils the simulation's song into a short refrain—how bright did the
            aurora flare, how tense the membrane felt as R serenaded Theta.
        """

        flux = results["flux"]
        sigma = results["sigma"]
        zeta_vals = results["zeta"]
        R_vals = results["R"]
        flux_mean = sum(flux) / len(flux) if flux else 0.0
        flux_sq_mean = sum(value**2 for value in flux) / len(flux) if flux else 0.0
        flux_std = math.sqrt(max(flux_sq_mean - flux_mean**2, 0.0))
        zeta_mean = sum(zeta_vals) / len(zeta_vals) if zeta_vals else 0.0
        return {
            "R_final": float(R_vals[-1]) if R_vals else float("nan"),
            "sigma_peak": float(max(sigma)) if sigma else float("nan"),
            "sigma_valley": float(min(sigma)) if sigma else float("nan"),
            "zeta_mean": float(zeta_mean),
            "flux_mean": float(flux_mean),
            "flux_std": float(flux_std),
        }
