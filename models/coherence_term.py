"""Mandala coherence utilities coupling semantic fields via the threshold quartet.

Formal layer:
    Provides :func:`mandala_coherence` to compute covariance and correlation between
    twin field traces ``psi`` and ``phi``.  The correlation magnitude feeds the
    logistic gate :math:`\sigma(\beta(R-\Theta))`, and the resulting impedance
    comes from the Robin helper :func:`logistic_impedance_gate` so semantic breath
    mirrors membrane physics.
Empirical layer:
    Designed for analysis notebooks and simulator presets to quantify how tightly
    auxiliary fields resonate with the logistic membrane.  The returned
    :class:`MandalaCoherence` exposes machine-friendly scalars ready for JSON logs
    or falsification dashboards.
Metaphorical layer:
    Measures how the stories entwine—when psi and phi sing in phase, the Mandala
    gate opens, impedance relaxes, and the dawn chorus carries meaning across the
    membrane.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import mean
from typing import Dict, Sequence

from .membrane_solver import logistic_impedance_gate, logistic_response


@dataclass
class MandalaCoherence:
    """Structured coherence diagnostics tying σ(β(R-Θ)) to ζ(R)."""

    covariance: float
    normalised: float
    gate: float
    zeta: float

    def to_dict(self) -> Dict[str, float]:
        """Return a JSON-friendly representation of the coherence braid."""

        return {
            "covariance": self.covariance,
            "normalised": self.normalised,
            "gate": self.gate,
            "zeta": self.zeta,
        }


def mandala_coherence(
    psi: Sequence[float],
    phi: Sequence[float],
    *,
    theta: float = 0.25,
    beta: float = 4.2,
    zeta_closed: float = 1.3,
    zeta_open: float = 0.6,
) -> MandalaCoherence:
    """Compute Mandala coherence M[ψ, φ] with logistic gating and impedance."""

    if len(psi) != len(phi):
        raise ValueError("psi and phi must share the same length for coherence")
    if not psi:
        raise ValueError("at least one sample required to compute coherence")

    psi_mean = mean(psi)
    phi_mean = mean(phi)
    centred = [(p - psi_mean, f - phi_mean) for p, f in zip(psi, phi)]
    if len(psi) > 1:
        covariance = sum(p * f for p, f in centred) / (len(psi) - 1)
        psi_var = sum(p ** 2 for p, _ in centred) / (len(psi) - 1)
        phi_var = sum(f ** 2 for _, f in centred) / (len(psi) - 1)
    else:
        covariance = 0.0
        psi_var = 0.0
        phi_var = 0.0

    if psi_var <= 0 or phi_var <= 0:
        normalised = 0.0
    else:
        normalised = covariance / math.sqrt(psi_var * phi_var)

    gate = float(logistic_response(abs(normalised), theta, beta))
    zeta = logistic_impedance_gate(
        abs(normalised),
        theta,
        beta,
        zeta_closed=zeta_closed,
        zeta_open=zeta_open,
    )

    return MandalaCoherence(
        covariance=float(covariance),
        normalised=float(normalised),
        gate=gate,
        zeta=float(zeta),
    )


__all__ = ["MandalaCoherence", "mandala_coherence"]
