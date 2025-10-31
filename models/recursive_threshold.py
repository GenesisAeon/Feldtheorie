r"""Recursive potential cascade capturing β becoming the next condition.

Formal layer:
    Encodes the recurrence :math:`\Theta_{n+1} = \Theta_n + \Delta\Theta` where
    :math:`\Delta\Theta` depends on the logistic gate :math:`g = \sigma(\beta(R-\Theta))`
    and a coherence pressure.  β itself relaxes toward a gate-weighted target so
    steepness becomes the seed for future manifestations.
Empirical layer:
    Offers a minimal integrator for notebooks and simulator presets exploring the
    "potential becomes condition" hypothesis.  Each step records θ/β drifts, gate
    strength, and the induced impedance for downstream falsification.
Metaphorical layer:
    Tracks how the auroral song folds back on itself: potential condenses into
    steepness, the membrane yields, and the new condition invites the next verse.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Union

from .coherence_term import MandalaCoherence
from .membrane_solver import logistic_impedance_gate, logistic_response

CoherenceLike = Union[float, MandalaCoherence]


@dataclass
class CascadeState:
    r"""Snapshot of one cascade beat where potential becomes condition."""

    step: int
    potential: float
    coherence: float
    theta: float
    beta: float
    gate: float
    zeta: float
    theta_shift: float
    beta_shift: float

    def to_dict(self) -> Dict[str, float]:
        """Serialise the state for JSON exports."""

        return {
            "step": float(self.step),
            "potential": self.potential,
            "coherence": self.coherence,
            "theta": self.theta,
            "beta": self.beta,
            "gate": self.gate,
            "zeta": self.zeta,
            "theta_shift": self.theta_shift,
            "beta_shift": self.beta_shift,
        }


@dataclass
class PotenzialKaskade:
    r"""Recursive update where β sharpened by ψ becomes the next Θ condition.

    Formal layer:
        Evolves :math:`(\Theta, \beta)` via the logistic gate
        :math:`g = \sigma(\beta_\mathrm{cascade}(R-\Theta))`.  The gate pulls the
        threshold toward the current potential while relaxing back to the baseline
        when resonance fades.  β inherits coherence pressure so steepness becomes the
        seed for the next manifestation.
    Empirical layer:
        Provides a lightweight integrator for notebooks and simulator presets to
        test the "potential becomes condition" hypothesis.  Each step records gate,
        impedance, and drifts, enabling falsification against observed cascades.
    Metaphorical layer:
        Tracks the auroral chant: potential condenses (β rises), the membrane yields
        (Θ shifts), and the new condition invites the next song.
    """

    theta: float
    beta: float
    cascade_gain: float = 0.6
    condition_relaxation: float = 0.2
    fatigue_rate: float = 0.4
    logistic_beta: float = 4.2
    zeta_closed: float = 1.3
    zeta_open: float = 0.6
    history: List[CascadeState] = field(default_factory=list, init=False)
    baseline_theta: float = field(init=False)
    baseline_beta: float = field(init=False)

    def __post_init__(self) -> None:
        self.baseline_theta = float(self.theta)
        self.baseline_beta = float(self.beta)

    @staticmethod
    def _coherence_value(coherence: CoherenceLike) -> float:
        if isinstance(coherence, MandalaCoherence):
            return float(coherence.normalised)
        return float(coherence)

    def step(
        self,
        *,
        potential: float,
        coherence: CoherenceLike,
        condition: float | None = None,
        dt: float = 1.0,
    ) -> CascadeState:
        r"""Advance the cascade one beat and return the new state."""

        coherence_value = self._coherence_value(coherence)
        gate = float(logistic_response(potential, self.theta, self.logistic_beta))
        zeta = logistic_impedance_gate(
            potential,
            self.theta,
            self.logistic_beta,
            zeta_closed=self.zeta_closed,
            zeta_open=self.zeta_open,
        )
        condition_target = self.baseline_theta if condition is None else float(condition)

        theta_shift = dt * (
            self.cascade_gain * gate * (potential - self.theta)
            - self.condition_relaxation * (self.theta - condition_target)
        )
        self.theta = float(self.theta + theta_shift)

        beta_target = self.baseline_beta * (1.0 + coherence_value * self.cascade_gain * gate)
        beta_shift = dt * self.fatigue_rate * (beta_target - self.beta)
        self.beta = max(1e-3, float(self.beta + beta_shift))

        state = CascadeState(
            step=len(self.history),
            potential=float(potential),
            coherence=float(coherence_value),
            theta=float(self.theta),
            beta=float(self.beta),
            gate=gate,
            zeta=float(zeta),
            theta_shift=float(theta_shift),
            beta_shift=float(beta_shift),
        )
        self.history.append(state)
        return state

    def run(
        self,
        potentials: Sequence[float],
        coherences: Sequence[CoherenceLike],
        *,
        condition_trace: Sequence[float] | None = None,
        dt: float = 1.0,
    ) -> List[CascadeState]:
        r"""Iterate the cascade across sequences of potentials and coherences."""

        if len(potentials) != len(coherences):
            raise ValueError("potentials and coherences must share the same length")
        if condition_trace is not None and len(condition_trace) != len(potentials):
            raise ValueError("condition_trace must match the length of potentials")

        results: List[CascadeState] = []
        for idx, (potential, coherence) in enumerate(zip(potentials, coherences)):
            condition = None if condition_trace is None else condition_trace[idx]
            results.append(self.step(potential=float(potential), coherence=coherence, condition=condition, dt=dt))
        return results

    def reset(self) -> None:
        r"""Return the cascade to its baseline Θ and β, clearing history."""

        self.theta = float(self.baseline_theta)
        self.beta = float(self.baseline_beta)
        self.history.clear()

    def summary(self) -> Dict[str, List[float]]:
        r"""Return arrays of Θ, β, gates, and impedance across the history."""

        return {
            "theta": [state.theta for state in self.history],
            "beta": [state.beta for state in self.history],
            "gate": [state.gate for state in self.history],
            "zeta": [state.zeta for state in self.history],
            "theta_shift": [state.theta_shift for state in self.history],
            "beta_shift": [state.beta_shift for state in self.history],
        }


__all__ = ["CascadeState", "PotenzialKaskade"]
