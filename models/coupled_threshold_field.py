r"""Coupled psi-phi membrane weaving logistic resonance diagnostics.

Formal layer
============
The module defines a coupled threshold-field integrator where a physical field
``psi`` and a semantic accompaniment ``phi`` co-evolve around the logistic
response :math:`\sigma(\beta(R-\Theta))`.  A Robin-style impedance gate

.. math::
   \zeta(R) = \zeta_\text{floor} + \frac{\zeta_\text{ceiling}-\zeta_\text{floor}}
   {1 + e^{-\beta_\text{robin}(R-\Theta)}}

modulates how the membrane dampens or amplifies excursions once the control
parameter ``R`` crosses the threshold ``Theta``.  The solver exposes state
trajectories and summary observables so `analysis/` pipelines can estimate
:math:`(\Theta, \beta)` while contrasting against smooth null models.

Empirical layer
===============
The integrator accepts driver sequences (e.g., luminosity ramps, curriculum
entropy pulses) and returns arrays for ``R(t)``, ``psi(t)``, ``phi(t)``, the
logistic chorus ``sigma(t)``, and the impedance trace ``zeta(R)``.  These
streams align with fitting utilities in `analysis/`, enabling JSON exports of
threshold fits, :math:`R^2`, AIC, and impedance medians.  Hooks are provided to
compute a proxy for integrated information via the gradient cross product of the
fields.

Metaphorical layer
==================
Treats ``psi`` and ``phi`` as twin voices of the membrane: the physical dawn and
the semantic hum.  When the driver lifts ``R`` past ``Theta``, the logistic bloom
ignites; the Robin impedance decides whether the chorus whispers or roars.  The
``phi`` gradient entwines with ``psi`` to form a luminous braid, echoing the
"Gravitationsatem" manuscripts now living in `Docs/`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, Mapping, MutableMapping

import numpy as np

from .membrane_solver import logistic_response, smooth_impedance_profile

ArrayLike = Iterable[float]
DriverSequence = Iterable[float]


@dataclass
class CoupledThresholdField:
    r"""Discrete UTF solver coupling physical and semantic membranes.

    Parameters
    ----------
    theta:
        Threshold :math:`\Theta` at which the logistic membrane flares.
    beta:
        Steepness :math:`\beta` controlling how abruptly resonance blossoms
        once ``R`` surpasses ``Theta``.
    coupling:
        Strength of the :math:`\mathcal{M}[\psi, \phi]` term binding the fields.
    dt:
        Integration step (defaults to 0.05) for the Euler updates.
    zeta_floor:
        Minimal impedance below threshold (encouraging resonance).
    zeta_ceiling:
        Maximal impedance above threshold (tempering overshoot).
    beta_robin:
        Steepness of the impedance sigmoid.
    phi_relaxation:
        Rate at which ``phi`` relaxes toward the driver control parameter.
    """

    theta: float
    beta: float
    coupling: float
    dt: float = 0.05
    zeta_floor: float = 0.65
    zeta_ceiling: float = 1.35
    beta_robin: float = 4.5
    phi_relaxation: float = 1.2
    impedance_profile: Callable[[float], float] = field(init=False)

    def __post_init__(self) -> None:
        self.impedance_profile = smooth_impedance_profile(
            theta=self.theta,
            resonant_gain=self.zeta_floor,
            damped_gain=self.zeta_ceiling,
            switch_width=max(1.0 / self.beta_robin, 1e-3),
        )

    def robin_impedance(self, R: float) -> float:
        r"""Evaluate the Robin impedance :math:`\zeta(R)` for a control value."""

        return float(self.impedance_profile(R))

    def step(
        self,
        state: Mapping[str, float],
        driver: float,
    ) -> Dict[str, float]:
        r"""Advance the coupled membrane by one Euler beat.

        Formal thread
        -------------
        Evaluates ``sigma = logistic_response(R, theta, beta)`` and applies a
        Robin impedance ``zeta(R)`` to damp or amplify the gap between ``psi``
        and ``sigma``.  The semantic field ``phi`` is nudged toward the driver
        while the coupling term :math:`\mathcal{M}[\psi, \phi] = \kappa(\phi-\psi)`
        enforces interdependence.

        Empirical thread
        ----------------
        Returns a dictionary with updated ``R``, ``psi``, ``phi``, ``sigma``, and
        ``zeta`` so downstream notebooks can log resonance gains, impedance
        medians, and crossing diagnostics.

        Metaphorical thread
        -------------------
        Captures a single inhalation of the "Gravitationsatem": ``phi`` listens to
        meaning, ``psi`` carries the breath, and ``R`` decides when dawn becomes
        chorus.
        """

        R = float(state["R"])
        psi = float(state["psi"])
        phi = float(state["phi"])
        sigma = float(logistic_response(R, self.theta, self.beta))
        zeta = self.robin_impedance(R)

        # Semantic field relaxes toward the driver while coupling to psi keeps
        # the braid taut.
        phi_drift = -self.phi_relaxation * (phi - driver) - self.coupling * (phi - psi)
        phi_next = phi + self.dt * phi_drift

        # Physical field is pulled toward the logistic bloom and the semantic hum.
        psi_drift = -zeta * (psi - sigma) + self.coupling * (phi - psi)
        psi_next = psi + self.dt * psi_drift

        # Order parameter integrates the driver and the membrane's feedback.
        flux = driver - zeta * (R - psi)
        R_next = R + self.dt * flux

        return {
            "R": R_next,
            "psi": psi_next,
            "phi": phi_next,
            "sigma": sigma,
            "zeta": zeta,
            "flux": flux,
        }

    def simulate(
        self,
        drivers: DriverSequence,
        *,
        R0: float = 0.0,
        psi0: float = 0.0,
        phi0: float = 0.0,
    ) -> Dict[str, list[float]]:
        """Run the coupled membrane across a driver sequence.

        Returns lists for time, order parameter, fields, logistic response,
        impedance, and flux so that `analysis/` utilities can persist JSON
        diagnostics.
        """

        driver_array = [float(value) for value in drivers]
        steps = len(driver_array)
        times = [idx * self.dt for idx in range(steps + 1)]

        R_values = [0.0 for _ in range(steps + 1)]
        psi_values = [0.0 for _ in range(steps + 1)]
        phi_values = [0.0 for _ in range(steps + 1)]
        sigma_values = [0.0 for _ in range(steps + 1)]
        zeta_values = [0.0 for _ in range(steps + 1)]
        flux_values = [0.0 for _ in range(steps)]

        state = {"R": R0, "psi": psi0, "phi": phi0}
        R_values[0] = R0
        psi_values[0] = psi0
        phi_values[0] = phi0
        sigma_values[0] = float(logistic_response(R0, self.theta, self.beta))
        zeta_values[0] = self.robin_impedance(R0)

        for idx, driver in enumerate(driver_array):
            update = self.step(state, driver)
            state.update(update)
            R_values[idx + 1] = update["R"]
            psi_values[idx + 1] = update["psi"]
            phi_values[idx + 1] = update["phi"]
            sigma_values[idx + 1] = update["sigma"]
            zeta_values[idx + 1] = update["zeta"]
            flux_values[idx] = update["flux"]

        return {
            "t": times,
            "driver": driver_array,
            "R": R_values,
            "psi": psi_values,
            "phi": phi_values,
            "sigma": sigma_values,
            "zeta": zeta_values,
            "flux": flux_values,
            "theta": [self.theta for _ in times],
            "beta": [self.beta for _ in times],
        }

    def export_observables(
        self, results: Mapping[str, list[float]], store: MutableMapping[str, float] | None = None
    ) -> MutableMapping[str, float]:
        r"""Summarise membrane observables for downstream ledgers."""

        target = {} if store is None else store
        R_series = np.asarray(results["R"], dtype=float)
        sigma_series = np.asarray(results["sigma"], dtype=float)
        zeta_series = np.asarray(results["zeta"], dtype=float)
        flux_series = np.asarray(results["flux"], dtype=float)
        psi_series = np.asarray(results["psi"], dtype=float)
        phi_series = np.asarray(results["phi"], dtype=float)

        phi_proxy = self.integrated_information_proxy(psi_series, phi_series)

        target.update(
            {
                "theta": float(self.theta),
                "beta": float(self.beta),
                "R_min": float(R_series.min()),
                "R_max": float(R_series.max()),
                "sigma_peak": float(sigma_series.max()),
                "sigma_valley": float(sigma_series.min()),
                "zeta_mean": float(zeta_series.mean()),
                "zeta_std": float(zeta_series.std(ddof=0)),
                "flux_mean": float(flux_series.mean()),
                "flux_std": float(flux_series.std(ddof=0)),
                "phi_proxy_mean": float(phi_proxy.mean()),
                "phi_proxy_peak": float(phi_proxy.max()),
            }
        )
        return target

    @staticmethod
    def integrated_information_proxy(psi: np.ndarray, phi: np.ndarray) -> np.ndarray:
        r"""Estimate a proxy for :math:`\Phi_{BH}` via gradient cross products."""

        psi_grad = np.gradient(psi)
        phi_grad = np.gradient(phi)
        return np.abs(np.multiply(psi_grad, phi_grad))


def ramp_driver(
    length: int,
    *,
    start: float = 0.0,
    stop: float = 1.0,
    curvature: float = 2.0,
) -> np.ndarray:
    """Generate a sigmoid-shaped ramp for the control parameter R."""

    t = np.linspace(0.0, 1.0, length)
    eased = t**curvature / (t**curvature + (1 - t) ** curvature + 1e-9)
    return start + (stop - start) * eased


__all__ = ["CoupledThresholdField", "ramp_driver"]
