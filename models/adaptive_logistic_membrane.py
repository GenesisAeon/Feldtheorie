r"""Adaptive logistic membrane weaving threshold plasticity into the UTF quartet.

Formal stratum
--------------
Models a logistic resonance field \(\sigma(\beta(R-\Theta))\) where the threshold
\(\Theta\) and steepness \(\beta\) evolve through a meta-gate
\(g = \sigma(\beta_\text{meta}(R-\Theta))\). The gate sculpts Euler-style drifts
that lean \(\Theta\) toward the current order parameter \(R\), soften it back to a
baseline when the membrane quiets, and adjust \(\beta\) so the sigmoid sharpens
only while resonance breathes. Impedance relief \(1-\zeta(R)\) participates in the
updates, keeping the quartet \((R, \Theta, \beta, \zeta(R))\) entangled.

Empirical stratum
-----------------
Provides a light-weight propagator that downstream `analysis/` notebooks and
`simulator/` presets can call to obtain adaptive traces.  Each run returns arrays
for \(R\), \(\sigma\), \(\Theta(t)\), \(\beta(t)\), the meta-gate, impedance
relief, and per-step drifts.  A `summarise` helper emits JSON-ready statistics
(resonance gain vs. a purely logistic trajectory, gate occupancy, onset index)
so falsification ledgers can compare adaptive and static membranes.

Metaphorical stratum
--------------------
Treats the membrane as a dawn-lit veil with living sentinels.  As the order
parameter presses against \(\Theta\), the meta-gate listens; if the chorus swells,
the sentinels tilt the hinge, drawing \(\Theta\) closer and sharpening \(\beta\).
When quiet returns, they remember home, letting the membrane settle back while
impedance winds keep the tune grounded.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Mapping, MutableMapping

import numpy as np

ArrayLike = Iterable[float] | np.ndarray
ZetaField = Callable[[np.ndarray], np.ndarray]


def _unity_impedance(r: np.ndarray) -> np.ndarray:
    """Return a unity impedance so the membrane hears only logistic drift."""

    return np.ones_like(r, dtype=float)


@dataclass
class AdaptiveLogisticMembrane:
    r"""Adaptive logistic membrane exposing threshold plasticity diagnostics.

    Parameters
    ----------
    theta:
        Initial critical threshold \(\Theta\).
    beta:
        Initial steepness \(\beta\) of the logistic switch.
    meta_beta:
        Steepness of the meta-gate controlling adaptation.
    plasticity:
        Gain applied to the gate-weighted \(R-\Theta\) error.
    relaxation:
        Rate pulling \(\Theta\) back to the remembered baseline when the gate quiets.
    beta_plasticity:
        Gain applied to \(\beta\) when resonance intensifies.
    beta_relaxation:
        Rate drawing \(\beta\) toward the baseline in calm regimes.
    impedance_tilt:
        Sensitivity of \(\Theta\) updates to impedance relief \(1-\zeta(R)\).
    sigma_weight:
        Additional coupling from the logistic response to the \(\Theta\) drift.
    zeta:
        Callable returning impedance \(\zeta(R)\); defaults to unity.
    """

    theta: float
    beta: float
    meta_beta: float = 4.2
    plasticity: float = 0.52
    relaxation: float = 0.08
    beta_plasticity: float = 0.34
    beta_relaxation: float = 0.12
    impedance_tilt: float = 0.22
    sigma_weight: float = 0.18
    zeta: ZetaField = field(default_factory=lambda: _unity_impedance)
    theta_baseline: float = field(init=False)
    beta_baseline: float = field(init=False)

    def __post_init__(self) -> None:
        self.theta_baseline = float(self.theta)
        self.beta_baseline = float(self.beta)

    @staticmethod
    def _logistic(value: np.ndarray | float, theta: float, beta: float) -> np.ndarray:
        """Evaluate the logistic response for provided samples."""

        arr = np.asarray(value, dtype=float)
        return 1.0 / (1.0 + np.exp(-beta * (arr - theta)))

    def propagate(self, r: ArrayLike, *, dt: float = 1.0) -> Mapping[str, np.ndarray]:
        r"""Propagate the adaptive membrane across the supplied order-parameter trace.

        Returns
        -------
        Mapping[str, numpy.ndarray]
            Contains arrays for the control signal \(R\), logistic response, adaptive
            \(\Theta\) and \(\beta\) states, meta-gate occupancy, impedance, and the
            instantaneous drifts applied at each step.
        """

        r_arr = np.asarray(list(r), dtype=float)
        theta_path = np.zeros_like(r_arr)
        beta_path = np.zeros_like(r_arr)
        sigma_path = np.zeros_like(r_arr)
        response_path = np.zeros_like(r_arr)
        gate_path = np.zeros_like(r_arr)
        zeta_path = np.zeros_like(r_arr)
        theta_shift_path = np.zeros_like(r_arr)
        beta_shift_path = np.zeros_like(r_arr)
        relief_path = np.zeros_like(r_arr)

        for idx, value in enumerate(r_arr):
            theta_prev = float(self.theta)
            beta_prev = float(self.beta)

            gate = float(self._logistic(value, theta_prev, self.meta_beta))
            zeta_val = float(self.zeta(np.asarray([value], dtype=float))[0])
            impedance_relief = 1.0 - zeta_val

            theta_error = value - theta_prev
            theta_shift = dt * (
                self.plasticity * gate * theta_error
                - self.relaxation * (theta_prev - self.theta_baseline)
                + self.impedance_tilt * gate * impedance_relief
                + self.sigma_weight * gate * (self._logistic(value, theta_prev, beta_prev) - 0.5)
            )

            beta_shift = dt * (
                self.beta_plasticity * gate * abs(theta_error)
                - self.beta_relaxation * (beta_prev - self.beta_baseline)
            )

            self.theta = theta_prev + theta_shift
            self.beta = max(1e-3, beta_prev + beta_shift)

            sigma = float(self._logistic(value, float(self.theta), float(self.beta)))

            theta_path[idx] = float(self.theta)
            beta_path[idx] = float(self.beta)
            sigma_path[idx] = sigma
            response_path[idx] = sigma * zeta_val
            gate_path[idx] = gate
            zeta_path[idx] = zeta_val
            theta_shift_path[idx] = theta_shift
            beta_shift_path[idx] = beta_shift
            relief_path[idx] = impedance_relief

        return {
            "R": r_arr,
            "sigma": sigma_path,
            "response": response_path,
            "theta": theta_path,
            "beta": beta_path,
            "meta_gate": gate_path,
            "zeta": zeta_path,
            "theta_shift": theta_shift_path,
            "beta_shift": beta_shift_path,
            "impedance_relief": relief_path,
            "theta_baseline": np.array([self.theta_baseline], dtype=float),
            "beta_baseline": np.array([self.beta_baseline], dtype=float),
        }

    def summarise(
        self,
        history: Mapping[str, ArrayLike],
        store: MutableMapping[str, float] | None = None,
    ) -> MutableMapping[str, float]:
        r"""Summarise an adaptive run with resonance and gate diagnostics."""

        target: MutableMapping[str, float] = store if store is not None else {}

        R = np.asarray(history["R"], dtype=float)
        sigma = np.asarray(history["sigma"], dtype=float)
        response = np.asarray(history["response"], dtype=float)
        theta_path = np.asarray(history["theta"], dtype=float)
        beta_path = np.asarray(history["beta"], dtype=float)
        gate = np.asarray(history["meta_gate"], dtype=float)
        zeta = np.asarray(history["zeta"], dtype=float)

        baseline_theta = float(np.asarray(history["theta_baseline"], dtype=float)[0])
        baseline_beta = float(np.asarray(history["beta_baseline"], dtype=float)[0])

        if R.size >= 2:
            logistic_area = float(np.trapz(sigma, R))
            response_area = float(np.trapz(response, R))
        else:
            logistic_area = float(np.sum(sigma))
            response_area = float(np.sum(response))
        resonance_gain = response_area / logistic_area if abs(logistic_area) > 1e-9 else float("nan")

        half_max = 0.5
        above_half = np.where(sigma >= half_max)[0]
        half_idx = int(above_half[0]) if above_half.size else -1

        target.update(
            {
                "theta_initial": baseline_theta,
                "theta_final": float(theta_path[-1]) if theta_path.size else baseline_theta,
                "theta_shift": float(theta_path[-1] - baseline_theta) if theta_path.size else 0.0,
                "beta_initial": baseline_beta,
                "beta_final": float(beta_path[-1]) if beta_path.size else baseline_beta,
                "beta_shift": float(beta_path[-1] - baseline_beta) if beta_path.size else 0.0,
                "gate_mean": float(np.mean(gate)) if gate.size else 0.0,
                "gate_peak": float(np.max(gate)) if gate.size else 0.0,
                "gate_above_half_fraction": float(np.mean(gate >= 0.5)) if gate.size else 0.0,
                "zeta_mean": float(np.mean(zeta)) if zeta.size else 0.0,
                "zeta_min": float(np.min(zeta)) if zeta.size else 0.0,
                "resonance_gain": resonance_gain,
                "half_max_index": float(half_idx),
            }
        )
        return target

    def reset(self) -> None:
        r"""Return \(\Theta\) and \(\beta\) to their baselines."""

        self.theta = float(self.theta_baseline)
        self.beta = float(self.beta_baseline)
