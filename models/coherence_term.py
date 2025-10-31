r"""Mandala coherence utilities coupling semantic fields via the threshold quartet.

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

import numpy as np
from numpy.typing import ArrayLike, NDArray



@dataclass
class MandalaCoherence:
    r"""Structured coherence diagnostics tying σ(β(R-Θ)) to ζ(R)."""

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
    r"""Compute Mandala coherence M[ψ, φ] with logistic gating and impedance."""

    from .membrane_solver import logistic_impedance_gate, logistic_response

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


def _broadcast_fields(
    psi: ArrayLike, phi: ArrayLike
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Return float arrays for ``psi`` and ``phi`` with matching shapes."""

    psi_array = np.asarray(psi, dtype=float)
    phi_array = np.asarray(phi, dtype=float)
    if psi_array.shape == phi_array.shape:
        return psi_array.astype(float), phi_array.astype(float)

    if phi_array.size == 1:
        broadcast_phi = np.full_like(psi_array, float(phi_array))
        return psi_array.astype(float), broadcast_phi.astype(float)

    try:
        broadcast_phi = np.broadcast_to(phi_array, psi_array.shape)
    except ValueError as exc:
        raise ValueError("psi and phi must be broadcastable to a common shape") from exc
    return psi_array.astype(float), np.asarray(broadcast_phi, dtype=float)


def semantic_coupling_term(
    psi: ArrayLike,
    phi: ArrayLike,
    *,
    lambda_coupling: float = 0.1,
    phi_exponent: float = 2.0,
    theta: float = 0.0,
    beta: float = 4.2,
) -> NDArray[np.float64]:
    r"""Compute the semantic coupling term :math:`\mathcal{M}[\psi, \phi]`.

    Formal layer:
        Implements the non-linear braid :math:`\mathcal{M} = \lambda \psi \vert\phi\vert^{n}`
        gated by the logistic resonance :math:`\sigma(\beta(\psi-\Theta))`.  The coupling
        translates semantic density ``phi`` into a modulation of the physical field ``psi``.
    Empirical layer:
        Accepts scalars or arrays (NumPy broadcast rules apply) so notebooks and simulator
        presets can inject semantic pressure directly into the membrane equations documented
        in ``analysis/``.  The return value mirrors the shape of ``psi`` for JSON exports or
        solver integrations.
    Metaphorical layer:
        Measures how meaning leans on matter: once ``psi`` approaches \(\Theta\), the logistic
        gate opens and semantic light (``phi``) pours into the membrane, coaxing a brighter
        dawn chorus.

    Args:
        psi: Physical field samples (e.g., order parameter \(R\) or membrane voltage).
        phi: Semantic field samples (e.g., Mandala meaning trace).
        lambda_coupling: Coupling strength :math:`\lambda`.
        phi_exponent: Exponent applied to the semantic field to emphasise non-linearity.
        theta: Threshold \(\Theta\) governing the logistic gate.
        beta: Steepness \(\beta\) of the logistic gate.

    Returns:
        A NumPy array containing :math:`\mathcal{M}[\psi, \phi]` for each sample.
    """

    psi_array, phi_array = _broadcast_fields(psi, phi)
    gate = 1.0 / (1.0 + np.exp(-beta * (psi_array - theta)))
    semantic_strength = np.power(np.abs(phi_array), phi_exponent)
    semantic_strength *= np.sign(phi_array)
    modulation = lambda_coupling * psi_array * semantic_strength
    return modulation * gate


__all__ = ["MandalaCoherence", "mandala_coherence", "semantic_coupling_term"]
