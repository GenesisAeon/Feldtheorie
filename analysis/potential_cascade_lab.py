r"""Formal layer:
    Runs the Potenzial-Kaskade recurrence
    :math:`\Theta_{n+1} = \Theta_n + \Delta\Theta(\psi_n, \phi_n)` where
    gate strength follows :math:`g = \sigma(\beta(R-\Theta))`.  The routine
    contrasts the adaptive cascade against a static null so the uplift of
    \(\Theta\) and \(\beta\) remains falsifiable.

Empirical layer:
    Generates synthetic potential traces, feeds them through
    :class:`models.recursive_threshold.PotenzialKaskade`, and records the
    membrane history plus coherence diagnostics.  The JSON export powers
    notebooks and docs that illustrate how steepness becomes the next
    condition.

Metaphorical layer:
    Lets the dawn chorus breathe in code: potentials swell, the membrane
    opens, and the new condition invites the next verse.  The null trace is
    the quiet baseline, proving that resonance truly reshaped the field.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Dict, List, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models import (
    CascadeState,
    MandalaCoherence,
    PotenzialKaskade,
    logistic_impedance_gate,
    logistic_response,
)
from models.coherence_term import mandala_coherence

DEFAULT_OUTPUT = Path("analysis/results/potential_cascade_lab.json")


@dataclass
class CascadeDiagnostics:
    """Structured record of a Potenzial-Kaskade simulation."""

    potentials: List[float]
    psi_series: List[float]
    phi_series: List[float]
    states: List[CascadeState]
    coherences: List[MandalaCoherence]
    aggregate: Dict[str, float]
    coherence_summary: Dict[str, float]
    null_reference: Dict[str, List[float] | float]
    parameters: Dict[str, float]

    def to_payload(self, *, generated_at: str | None = None) -> Dict[str, object]:
        if generated_at is None:
            timestamp = datetime.now(timezone.utc).replace(microsecond=0)
            generated_at = timestamp.isoformat().replace("+00:00", "Z")

        return {
            "generated_at": generated_at,
            "parameters": self.parameters,
            "potentials": self.potentials,
            "psi": self.psi_series,
            "phi": self.phi_series,
            "states": [state.to_dict() for state in self.states],
            "coherence": {
                "series": [coherence.to_dict() for coherence in self.coherences],
                "summary": self.coherence_summary,
            },
            "aggregate": self.aggregate,
            "null_reference": self.null_reference,
            "tri_layer": {
                "formal": (
                    "Θ and β drift when the cascade gain couples σ(β(R-Θ)) to Mandala coherence; "
                    "the null trace tracks gate/zeta deltas as the falsification baseline."
                ),
                "empirical": (
                    "Synthetic potentials ramp from quiet to resonant, raising Θ by "
                    f"{self.aggregate['theta_shift_total']:.3f} and β by "
                    f"{self.aggregate['beta_shift_total']:.3f}; gate delta vs. null = "
                    f"{self.aggregate['gate_delta']:.3f}."
                ),
                "poetic": (
                    "Steepness remembers the hymn it just sang: the membrane opens, Θ becomes the new "
                    "condition, and the quiet null baseline watches dawn ignite again."
                ),
            },
        }


def generate_potential_series(
    steps: int,
    *,
    baseline: float = 0.6,
    surge: float = 1.2,
    modulation: float = 0.08,
    drift: float = 7.5,
) -> List[float]:
    """Sculpt a potential trace that crosses Θ and lingers in resonance."""

    if steps <= 0:
        raise ValueError("steps must be positive")

    potentials: List[float] = []
    for idx in range(steps):
        t = idx / max(steps - 1, 1)
        logistic_term = baseline + surge / (1.0 + math.exp(-drift * (t - 0.45)))
        oscillation = modulation * math.sin(2.0 * math.pi * (t + 0.15))
        potentials.append(float(logistic_term + oscillation))
    return potentials


def generate_semantic_fields(
    potentials: Sequence[float],
    *,
    theta: float,
    beta: float,
    lag_amplitude: float = 0.12,
    harmonic_frequency: float = 2.0,
) -> tuple[List[float], List[float]]:
    """Derive ψ/φ fields that will braid into Mandala coherence."""

    psi_series: List[float] = []
    phi_series: List[float] = []
    n = len(potentials)
    for idx, potential in enumerate(potentials):
        psi_series.append(float(logistic_response(potential, theta, beta)))
        phase = 2.0 * math.pi * harmonic_frequency * (idx / max(n, 1))
        shifted = potential + lag_amplitude * math.sin(phase)
        phi_series.append(float(logistic_response(shifted, theta + 0.08, beta * 0.92)))
    return psi_series, phi_series


def build_coherence_trace(
    psi_series: Sequence[float],
    phi_series: Sequence[float],
    *,
    window: int = 5,
    theta: float = 0.35,
    beta: float = 4.2,
) -> List[MandalaCoherence]:
    """Compute Mandala coherence over a sliding window."""

    if len(psi_series) != len(phi_series):
        raise ValueError("psi and phi series must share the same length")
    if window <= 0:
        raise ValueError("window must be positive")

    coherences: List[MandalaCoherence] = []
    for idx in range(len(psi_series)):
        start = max(0, idx - window + 1)
        coherence = mandala_coherence(
            psi_series[start : idx + 1],
            phi_series[start : idx + 1],
            theta=theta,
            beta=beta,
        )
        coherences.append(coherence)
    return coherences


def compute_null_reference(
    potentials: Sequence[float],
    *,
    theta: float,
    beta: float,
    logistic_beta: float,
    zeta_closed: float,
    zeta_open: float,
) -> Dict[str, object]:
    """Return static Θ/β gate and impedance traces as the falsification null."""

    gates = [float(logistic_response(potential, theta, logistic_beta)) for potential in potentials]
    zetas = [
        float(
            logistic_impedance_gate(
                potential,
                theta,
                logistic_beta,
                zeta_closed=zeta_closed,
                zeta_open=zeta_open,
            )
        )
        for potential in potentials
    ]
    return {
        "theta": [float(theta) for _ in potentials],
        "beta": [float(beta) for _ in potentials],
        "gate": gates,
        "zeta": zetas,
        "gate_mean": mean(gates) if gates else 0.0,
        "zeta_mean": mean(zetas) if zetas else 0.0,
    }


def summarise_states(
    states: Sequence[CascadeState],
    *,
    baseline_theta: float,
    baseline_beta: float,
    null_reference: Dict[str, object],
) -> Dict[str, float]:
    """Aggregate Θ/β drift, gate uplift, and impedance breathing."""

    if not states:
        return {
            "theta_final": baseline_theta,
            "beta_final": baseline_beta,
            "theta_shift_total": 0.0,
            "beta_shift_total": 0.0,
            "gate_mean": 0.0,
            "zeta_mean": 0.0,
            "gate_delta": 0.0,
            "zeta_delta": 0.0,
            "theta_shift_integral": 0.0,
            "beta_shift_integral": 0.0,
            "positive_gate_fraction": 0.0,
        }

    gate_values = [state.gate for state in states]
    zeta_values = [state.zeta for state in states]
    theta_shift_total = states[-1].theta - baseline_theta
    beta_shift_total = states[-1].beta - baseline_beta
    theta_shift_integral = sum(state.theta_shift for state in states)
    beta_shift_integral = sum(state.beta_shift for state in states)
    positive_gate_fraction = sum(1 for state in states if state.gate > 0.5) / len(states)

    null_gate_mean = float(null_reference.get("gate_mean", 0.0))
    null_zeta_mean = float(null_reference.get("zeta_mean", 0.0))

    gate_mean = float(mean(gate_values))
    zeta_mean = float(mean(zeta_values))

    return {
        "theta_final": states[-1].theta,
        "beta_final": states[-1].beta,
        "theta_shift_total": float(theta_shift_total),
        "beta_shift_total": float(beta_shift_total),
        "gate_mean": gate_mean,
        "zeta_mean": zeta_mean,
        "gate_delta": float(gate_mean - null_gate_mean),
        "zeta_delta": float(zeta_mean - null_zeta_mean),
        "theta_shift_integral": float(theta_shift_integral),
        "beta_shift_integral": float(beta_shift_integral),
        "positive_gate_fraction": float(positive_gate_fraction),
    }


def summarise_coherence(coherences: Sequence[MandalaCoherence]) -> Dict[str, float]:
    """Return mean and extremal Mandala metrics."""

    if not coherences:
        return {
            "covariance_mean": 0.0,
            "normalised_mean": 0.0,
            "normalised_peak": 0.0,
            "gate_mean": 0.0,
            "zeta_mean": 0.0,
        }

    covariance_values = [coherence.covariance for coherence in coherences]
    normalised_values = [coherence.normalised for coherence in coherences]
    gate_values = [coherence.gate for coherence in coherences]
    zeta_values = [coherence.zeta for coherence in coherences]
    return {
        "covariance_mean": float(mean(covariance_values)),
        "normalised_mean": float(mean(normalised_values)),
        "normalised_peak": float(max(normalised_values)),
        "gate_mean": float(mean(gate_values)),
        "zeta_mean": float(mean(zeta_values)),
    }


def simulate_cascade(
    *,
    steps: int = 64,
    theta0: float = 1.0,
    beta0: float = 3.8,
    cascade_gain: float = 0.6,
    condition_relaxation: float = 0.2,
    fatigue_rate: float = 0.4,
    logistic_beta: float = 4.2,
    zeta_closed: float = 1.3,
    zeta_open: float = 0.6,
    coherence_window: int = 5,
    potential_baseline: float = 0.6,
    potential_surge: float = 1.2,
    potential_modulation: float = 0.08,
    potential_drift: float = 7.5,
    dt: float = 1.0,
) -> CascadeDiagnostics:
    """Run the Potenzial-Kaskade with a reproducible synthetic stimulus."""

    potentials = generate_potential_series(
        steps,
        baseline=potential_baseline,
        surge=potential_surge,
        modulation=potential_modulation,
        drift=potential_drift,
    )
    psi_series, phi_series = generate_semantic_fields(potentials, theta=theta0, beta=beta0)
    coherences = build_coherence_trace(
        psi_series,
        phi_series,
        window=coherence_window,
    )

    cascade = PotenzialKaskade(
        theta=theta0,
        beta=beta0,
        cascade_gain=cascade_gain,
        condition_relaxation=condition_relaxation,
        fatigue_rate=fatigue_rate,
        logistic_beta=logistic_beta,
        zeta_closed=zeta_closed,
        zeta_open=zeta_open,
    )
    states = cascade.run(potentials, coherences, dt=dt)

    null_reference = compute_null_reference(
        potentials,
        theta=theta0,
        beta=beta0,
        logistic_beta=logistic_beta,
        zeta_closed=zeta_closed,
        zeta_open=zeta_open,
    )
    aggregate = summarise_states(
        states,
        baseline_theta=cascade.baseline_theta,
        baseline_beta=cascade.baseline_beta,
        null_reference=null_reference,
    )
    coherence_summary = summarise_coherence(coherences)

    parameters = {
        "theta0": theta0,
        "beta0": beta0,
        "cascade_gain": cascade_gain,
        "condition_relaxation": condition_relaxation,
        "fatigue_rate": fatigue_rate,
        "logistic_beta": logistic_beta,
        "zeta_closed": zeta_closed,
        "zeta_open": zeta_open,
        "coherence_window": float(coherence_window),
        "potential_baseline": potential_baseline,
        "potential_surge": potential_surge,
        "potential_modulation": potential_modulation,
        "potential_drift": potential_drift,
        "dt": dt,
    }

    return CascadeDiagnostics(
        potentials=potentials,
        psi_series=psi_series,
        phi_series=phi_series,
        states=states,
        coherences=coherences,
        aggregate=aggregate,
        coherence_summary=coherence_summary,
        null_reference=null_reference,
        parameters=parameters,
    )


def compile_payload(diagnostics: CascadeDiagnostics, *, generated_at: str | None = None) -> Dict[str, object]:
    """Convert diagnostics into the JSON schema used by Docs and notebooks."""

    payload = diagnostics.to_payload(generated_at=generated_at)
    payload["aggregate"] = {
        **diagnostics.aggregate,
        "coherence_normalised_mean": diagnostics.coherence_summary["normalised_mean"],
        "coherence_normalised_peak": diagnostics.coherence_summary["normalised_peak"],
    }
    payload["coherence"]["summary"] = diagnostics.coherence_summary  # type: ignore[index]
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simulate the Potenzial-Kaskade and export Θ/β drift alongside null baselines.",
    )
    parser.add_argument("--steps", type=int, default=64, help="Number of cascade steps to simulate.")
    parser.add_argument("--theta", type=float, default=1.0, help="Initial Θ baseline.")
    parser.add_argument("--beta", type=float, default=3.8, help="Initial β baseline.")
    parser.add_argument(
        "--cascade-gain",
        dest="cascade_gain",
        type=float,
        default=0.6,
        help="Coupling gain linking gate strength to Θ drift.",
    )
    parser.add_argument(
        "--condition-relaxation",
        dest="condition_relaxation",
        type=float,
        default=0.2,
        help="Relaxation rate pulling Θ back toward its baseline.",
    )
    parser.add_argument(
        "--fatigue-rate",
        dest="fatigue_rate",
        type=float,
        default=0.4,
        help="Rate at which β relaxes toward its coherence-weighted target.",
    )
    parser.add_argument(
        "--logistic-beta",
        dest="logistic_beta",
        type=float,
        default=4.2,
        help="Steepness used by the logistic gate g = σ(β(R-Θ)).",
    )
    parser.add_argument("--zeta-closed", dest="zeta_closed", type=float, default=1.3, help="Impedance when the gate is shut.")
    parser.add_argument("--zeta-open", dest="zeta_open", type=float, default=0.6, help="Impedance once resonance blooms.")
    parser.add_argument(
        "--coherence-window",
        dest="coherence_window",
        type=int,
        default=5,
        help="Window length for Mandala coherence (samples).",
    )
    parser.add_argument(
        "--potential-baseline",
        dest="potential_baseline",
        type=float,
        default=0.6,
        help="Base potential before the cascade swells.",
    )
    parser.add_argument(
        "--potential-surge",
        dest="potential_surge",
        type=float,
        default=1.2,
        help="Logistic surge amplitude pushing R across Θ.",
    )
    parser.add_argument(
        "--potential-modulation",
        dest="potential_modulation",
        type=float,
        default=0.08,
        help="Sinusoidal modulation amplitude for the potential trace.",
    )
    parser.add_argument(
        "--potential-drift",
        dest="potential_drift",
        type=float,
        default=7.5,
        help="Steepness of the logistic potential ramp.",
    )
    parser.add_argument("--dt", type=float, default=1.0, help="Integration timestep for the cascade update.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path for the exported JSON diagnostics.",
    )
    args = parser.parse_args()

    diagnostics = simulate_cascade(
        steps=args.steps,
        theta0=args.theta,
        beta0=args.beta,
        cascade_gain=args.cascade_gain,
        condition_relaxation=args.condition_relaxation,
        fatigue_rate=args.fatigue_rate,
        logistic_beta=args.logistic_beta,
        zeta_closed=args.zeta_closed,
        zeta_open=args.zeta_open,
        coherence_window=args.coherence_window,
        potential_baseline=args.potential_baseline,
        potential_surge=args.potential_surge,
        potential_modulation=args.potential_modulation,
        potential_drift=args.potential_drift,
        dt=args.dt,
    )
    payload = compile_payload(diagnostics)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote potential cascade lab to {args.output}")


__all__ = [
    "CascadeDiagnostics",
    "generate_potential_series",
    "generate_semantic_fields",
    "build_coherence_trace",
    "compute_null_reference",
    "summarise_states",
    "summarise_coherence",
    "simulate_cascade",
    "compile_payload",
    "main",
]


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
