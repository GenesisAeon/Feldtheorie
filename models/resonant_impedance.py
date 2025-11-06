r"""Resonant impedance motif that lets the membrane breathe with the control field.

Formal stratum
---------------
Implements a logistic gate \(\sigma(\beta(R-\Theta))\) that sculpts the impedance
profile \(\zeta(R)\).  When the order parameter \(R\) crosses \(\Theta\) the gate
opens, relaxing the impedance toward a low-relief floor; when the membrane quiets
the impedance recovers toward a remembered baseline.  A hysteresis braid keeps
the transition smooth so downstream solvers can toggle resonant versus damped
runs reproducibly.

Empirical stratum
-----------------
Provides a callable class that accepts control traces and returns impedance
samples alongside diagnostic paths (gate occupancy, relief, recovery, hysteresis
forces).  Analysis pipelines can stream these arrays to quantify how
\(\zeta(R)\) co-varies with threshold crossings, while simulator presets can feed
back the traces to animate membrane openness.

Metaphorical stratum
--------------------
Treats the impedance as a dawn-lit gatekeeper: when the chorus of \(R\) swells,
the gate relaxes to let resonance sing; when night returns, it gently closes,
remembering the home frequency yet welcoming the next auroral surge.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, MutableMapping

import numpy as np

ArrayLike = Iterable[float] | np.ndarray


def _logistic(sample: float, *, theta: float, beta: float) -> float:
    """Evaluate the logistic response for a scalar sample."""

    return float(1.0 / (1.0 + np.exp(-beta * (sample - theta))))


@dataclass
class ResonantImpedance:
    r"""Adaptive impedance motif aligned with the Universal Threshold Field quartet.

    Parameters
    ----------
    theta:
        Critical threshold \(\Theta\) controlling when the impedance loosens.
    beta:
        Steepness \(\beta\) of the impedance gate.  Higher values sharpen the
        relief transition once \(R\) leans past \(\Theta\).
    relief_gain:
        Strength of the downward drift toward the impedance floor when the gate
        is open.
    recovery_rate:
        Pulling rate that guides impedance back to its baseline when the gate is
        quiet.
    hysteresis:
        Coupling that reacts to changes in the gate value so opening and closing
        sweeps remain smooth.
    baseline:
        Remembered impedance level when the membrane rests.
    floor:
        Minimum impedance value once the membrane fully relaxes.
    ceiling:
        Upper bound that prevents runaway impedance amplification.
    """

    theta: float
    beta: float
    relief_gain: float = 0.65
    recovery_rate: float = 0.18
    hysteresis: float = 0.3
    baseline: float = 0.84
    floor: float = 0.12
    ceiling: float = 1.08
    _state: float = field(init=False)
    _last_gate: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:
        baseline = float(np.clip(self.baseline, self.floor, self.ceiling))
        self.baseline = baseline
        self._state = baseline

    @property
    def current_impedance(self) -> float:
        """Return the latest impedance value maintained by the motif."""

        return float(self._state)

    def reset(self) -> None:
        """Restore impedance and gate memories to the baseline."""

        self._state = float(self.baseline)
        self._last_gate = 0.0

    def trace(self, r: ArrayLike, *, dt: float = 1.0) -> Mapping[str, np.ndarray]:
        r"""Propagate impedance dynamics across a control-parameter trace.

        Parameters
        ----------
        r:
            Iterable of control parameter samples representing \(R\).
        dt:
            Integration step for the first-order impedance updates.

        Returns
        -------
        Mapping[str, numpy.ndarray]
            Contains the input control values, impedance samples, gate occupancy,
            and the relief/recovery/hysteresis forces accumulated at each step.
        """

        r_arr = np.asarray(list(r), dtype=float)
        zeta_path = np.zeros_like(r_arr)
        gate_path = np.zeros_like(r_arr)
        relief_path = np.zeros_like(r_arr)
        recovery_path = np.zeros_like(r_arr)
        hysteresis_path = np.zeros_like(r_arr)

        state = float(self._state)
        last_gate = float(self._last_gate)

        for idx, value in enumerate(r_arr):
            gate = _logistic(value, theta=self.theta, beta=self.beta)
            relief_drive = (state - self.floor) * gate
            recovery_drive = (self.baseline - state) * (1.0 - gate)
            hysteresis_drive = gate - last_gate

            relief_force = self.relief_gain * relief_drive
            recovery_force = self.recovery_rate * recovery_drive
            hysteresis_force = self.hysteresis * hysteresis_drive

            state = state - dt * relief_force + dt * recovery_force - dt * hysteresis_force
            state = float(np.clip(state, self.floor, self.ceiling))

            zeta_path[idx] = state
            gate_path[idx] = gate
            relief_path[idx] = relief_force
            recovery_path[idx] = recovery_force
            hysteresis_path[idx] = hysteresis_force

            last_gate = gate

        self._state = state
        self._last_gate = last_gate

        return {
            "R": r_arr,
            "zeta": zeta_path,
            "gate": gate_path,
            "relief": relief_path,
            "recovery": recovery_path,
            "hysteresis": hysteresis_path,
        }

    def __call__(self, r: ArrayLike) -> np.ndarray:
        """Return only the impedance samples for compatibility with solvers."""

        history = self.trace(r)
        return history["zeta"]

    def summarise(
        self,
        history: Mapping[str, ArrayLike],
        store: MutableMapping[str, float] | None = None,
    ) -> MutableMapping[str, float]:
        r"""Summarise an impedance trace with resonance diagnostics."""

        target = store if store is not None else {}

        r_arr = np.asarray(history["R"], dtype=float)
        zeta = np.asarray(history["zeta"], dtype=float)
        gate = np.asarray(history["gate"], dtype=float)
        relief = np.asarray(history["relief"], dtype=float)
        recovery = np.asarray(history["recovery"], dtype=float)
        hysteresis = np.asarray(history["hysteresis"], dtype=float)

        if r_arr.size >= 2:
            gate_area = float(np.trapz(gate, r_arr))
            impedance_area = float(np.trapz(zeta, r_arr))
            relief_area = float(np.trapz(relief, r_arr))
            recovery_area = float(np.trapz(recovery, r_arr))
            hysteresis_area = float(np.trapz(np.abs(hysteresis), r_arr))
            hysteresis_bias = float(np.trapz(hysteresis, r_arr))
        else:
            gate_area = float(np.sum(gate))
            impedance_area = float(np.sum(zeta))
            relief_area = float(np.sum(relief))
            recovery_area = float(np.sum(recovery))
            hysteresis_area = float(np.sum(np.abs(hysteresis)))
            hysteresis_bias = float(np.sum(hysteresis))

        relief_recovery_balance = relief_area - recovery_area
        if abs(recovery_area) > 1e-12:
            relief_recovery_ratio = float(relief_area / recovery_area)
        else:
            relief_recovery_ratio = None
        total_relief_recovery = relief_area + recovery_area
        if abs(total_relief_recovery) > 1e-12:
            relief_recovery_symmetry = float(relief_recovery_balance / total_relief_recovery)
        else:
            relief_recovery_symmetry = None

        target.update(
            {
                "theta": float(self.theta),
                "beta": float(self.beta),
                "zeta_mean": float(np.mean(zeta)) if zeta.size else self.baseline,
                "zeta_min": float(np.min(zeta)) if zeta.size else self.baseline,
                "zeta_max": float(np.max(zeta)) if zeta.size else self.baseline,
                "gate_mean": float(np.mean(gate)) if gate.size else 0.0,
                "gate_area": gate_area,
                "impedance_area": impedance_area,
                "relief_area": relief_area,
                "recovery_area": recovery_area,
                "hysteresis_area": hysteresis_area,
                "relief_recovery_balance": relief_recovery_balance,
                "relief_recovery_ratio": relief_recovery_ratio,
                "relief_recovery_symmetry": relief_recovery_symmetry,
                "hysteresis_bias": hysteresis_bias,
                "relief_peak": float(np.max(relief)) if relief.size else 0.0,
                "recovery_peak": float(np.max(recovery)) if recovery.size else 0.0,
                "hysteresis_peak": float(np.max(np.abs(hysteresis))) if hysteresis.size else 0.0,
                "final_impedance": float(zeta[-1]) if zeta.size else self.baseline,
                "baseline_impedance": float(self.baseline),
            }
        )
        return target


if __name__ == "__main__":
    # Demonstrate a simple impedance sweep for quick validation from the CLI.
    control = np.linspace(0.0, 1.0, 100)
    motif = ResonantImpedance(theta=0.42, beta=9.5, baseline=0.88, floor=0.18)
    history = motif.trace(control)
    summary = motif.summarise(history)
    print("ResonantImpedance quick-look summary:")
    for key, value in summary.items():
        print(f"  {key}: {value:.4f}")
