"""Impedance gate diagnostics for the Universal Threshold Field.

Formal cadence
--------------
Traces the resonant impedance motif :math:`\zeta(R)` governed by the logistic
gate :math:`\sigma(\beta(R-\Theta))`.  Generates a synthetic control-parameter
trajectory, feeds it through :class:`models.resonant_impedance.ResonantImpedance`,
and refits the gate using the shared UTF regression pipeline to document
\(\Theta\), \(\beta\), AIC, and falsification deltas against smooth nulls.
Alongside the logistic verdict the script records relief, recovery, and
hysteresis forces so cohort summaries can contrast impedance breathing across
analyses.

Empirical cadence
-----------------
Provides a reproducible CLI: by default it stages a sigmoidal sweep of 512
samples between ``R_min`` and ``R_max`` with gentle harmonic modulation so the
impedance motif experiences both quiescent and resonant regimes.  The resulting
diagnostics are serialised to ``analysis/results/resonant_impedance_diagnostics.json``
for ingestion by `analysis/resonance_cohort_summary.py`, documentation bridge
maps, and simulator presets that animate \(\zeta(R)\) breathing.

Metaphorical cadence
--------------------
Listens to the impedance gatekeeper as dawn leans across the membrane.  Relief
forces exhale once \(R>\Theta\), recovery winds guide the gate back toward the
baseline dusk, and hysteresis braids memory into the transition.  The exported
lantern lets every domain remember how the gate sighed when resonance bloomed.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import sin, tau
from pathlib import Path
from random import Random
from statistics import mean
from typing import Dict, Iterable, Mapping, Sequence

import importlib.util
import sys
import types


ROOT = Path(__file__).resolve().parents[1]


def _ensure_membrane_solver() -> None:
    """Load models.membrane_solver without importing heavy optional dependencies."""

    module_name = "models.membrane_solver"
    if module_name in sys.modules:
        return

    package = types.ModuleType("models")
    package.__path__ = [str((ROOT / "models").resolve())]
    sys.modules.setdefault("models", package)

    target = ROOT / "models" / "membrane_solver.py"
    spec = importlib.util.spec_from_file_location(module_name, target)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive guard
        raise ImportError("Unable to locate membrane_solver module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    setattr(package, "membrane_solver", module)


_ensure_membrane_solver()


from resonance_fit_pipeline import (  # noqa: E402
    assemble_summary,
    evaluate_null_model,
    evaluate_power_law_null,
    fit_threshold_parameters,
)

try:  # Prefer the canonical motif, but provide a lightweight fallback when numpy is absent.
    from models.resonant_impedance import ResonantImpedance as _CanonicalResonantImpedance
except Exception:  # pragma: no cover - executed only in minimal environments without numpy
    from math import exp

    class ResonantImpedance:  # type: ignore[override]
        """Lightweight impedance motif mirroring the canonical behaviour without numpy."""

        def __init__(
            self,
            *,
            theta: float,
            beta: float,
            relief_gain: float = 0.65,
            recovery_rate: float = 0.18,
            hysteresis: float = 0.3,
            baseline: float = 0.84,
            floor: float = 0.12,
            ceiling: float = 1.08,
        ) -> None:
            self.theta = float(theta)
            self.beta = float(beta)
            self.relief_gain = float(relief_gain)
            self.recovery_rate = float(recovery_rate)
            self.hysteresis = float(hysteresis)
            self.baseline = float(baseline)
            self.floor = float(floor)
            self.ceiling = float(ceiling)
            self._state = self.baseline
            self._last_gate = 0.0

        @staticmethod
        def _logistic(sample: float, *, theta: float, beta: float) -> float:
            return 1.0 / (1.0 + exp(-beta * (sample - theta)))

        def trace(self, r: Sequence[float], *, dt: float = 1.0) -> Dict[str, list[float]]:
            zeta_path: list[float] = []
            gate_path: list[float] = []
            relief_path: list[float] = []
            recovery_path: list[float] = []
            hysteresis_path: list[float] = []

            state = self._state
            last_gate = self._last_gate
            values = [float(value) for value in r]
            for value in values:
                gate = self._logistic(value, theta=self.theta, beta=self.beta)
                relief_drive = (state - self.floor) * gate
                recovery_drive = (self.baseline - state) * (1.0 - gate)
                hysteresis_drive = gate - last_gate

                relief_force = self.relief_gain * relief_drive
                recovery_force = self.recovery_rate * recovery_drive
                hysteresis_force = self.hysteresis * hysteresis_drive

                state = state - dt * relief_force + dt * recovery_force - dt * hysteresis_force
                state = min(max(state, self.floor), self.ceiling)

                zeta_path.append(state)
                gate_path.append(gate)
                relief_path.append(relief_force)
                recovery_path.append(recovery_force)
                hysteresis_path.append(hysteresis_force)
                last_gate = gate

            self._state = state
            self._last_gate = last_gate
            return {
                "R": values,
                "zeta": zeta_path,
                "gate": gate_path,
                "relief": relief_path,
                "recovery": recovery_path,
                "hysteresis": hysteresis_path,
            }

        def summarise(
            self, history: Mapping[str, Sequence[float]], store: Dict[str, float] | None = None
        ) -> Dict[str, float]:
            target: Dict[str, float] = {} if store is None else store
            R = [float(value) for value in history["R"]]
            zeta = [float(value) for value in history["zeta"]]
            gate = [float(value) for value in history["gate"]]
            relief = [float(value) for value in history["relief"]]
            recovery = [float(value) for value in history["recovery"]]
            hysteresis = [float(value) for value in history["hysteresis"]]

            def trapezoid(values: Sequence[float], abscissa: Sequence[float]) -> float:
                if len(values) < 2:
                    return sum(values)
                total = 0.0
                for idx in range(1, len(values)):
                    width = abscissa[idx] - abscissa[idx - 1]
                    total += 0.5 * (values[idx] + values[idx - 1]) * width
                return total

            gate_area = trapezoid(gate, R)
            impedance_area = trapezoid(zeta, R)
            relief_area = trapezoid(relief, R)
            recovery_area = trapezoid(recovery, R)
            hysteresis_area = trapezoid([abs(value) for value in hysteresis], R)
            hysteresis_bias = trapezoid(hysteresis, R)

            relief_recovery_balance = relief_area - recovery_area
            relief_recovery_ratio = (
                relief_area / recovery_area if abs(recovery_area) > 1e-12 else None
            )
            total_relief_recovery = relief_area + recovery_area
            relief_recovery_symmetry = (
                relief_recovery_balance / total_relief_recovery
                if abs(total_relief_recovery) > 1e-12
                else None
            )

            target.update(
                {
                    "theta": float(self.theta),
                    "beta": float(self.beta),
                    "zeta_mean": sum(zeta) / len(zeta) if zeta else self.baseline,
                    "zeta_min": min(zeta) if zeta else self.baseline,
                    "zeta_max": max(zeta) if zeta else self.baseline,
                    "gate_mean": sum(gate) / len(gate) if gate else 0.0,
                    "gate_area": gate_area,
                    "impedance_area": impedance_area,
                    "relief_area": relief_area,
                    "recovery_area": recovery_area,
                    "hysteresis_area": hysteresis_area,
                    "relief_recovery_balance": relief_recovery_balance,
                    "relief_recovery_ratio": relief_recovery_ratio,
                    "relief_recovery_symmetry": relief_recovery_symmetry,
                    "hysteresis_bias": hysteresis_bias,
                    "relief_peak": max(relief) if relief else 0.0,
                    "recovery_peak": max(recovery) if recovery else 0.0,
                    "hysteresis_peak": max(abs(value) for value in hysteresis) if hysteresis else 0.0,
                    "final_impedance": zeta[-1] if zeta else self.baseline,
                    "baseline_impedance": self.baseline,
                }
            )
            return target

else:  # pragma: no cover - executed when numpy is available
    ResonantImpedance = _CanonicalResonantImpedance


RESULTS_PATH = ROOT / "analysis" / "results" / "resonant_impedance_diagnostics.json"


@dataclass
class SweepConfig:
    """Parameters describing the synthetic control-parameter sweep."""

    samples: int = 512
    r_min: float = 0.0
    r_max: float = 1.5
    harmonic_gain: float = 0.08
    harmonic_period: float = 48.0
    noise_scale: float = 0.015
    seed: int = 42


def _generate_control_sequence(config: SweepConfig) -> list[float]:
    """Create a smooth control trajectory spanning sub- and super-threshold."""

    rng = Random(config.seed)
    if config.samples <= 1:
        base = [config.r_min]
    else:
        step = (config.r_max - config.r_min) / (config.samples - 1)
        base = [config.r_min + step * idx for idx in range(config.samples)]
    sequence: list[float] = []
    for idx, value in enumerate(base):
        phase = idx / max(config.samples - 1, 1)
        harmonic = config.harmonic_gain * sin(
            tau * phase * (config.samples / max(config.harmonic_period, 1e-6))
        )
        noise = rng.gauss(0.0, config.noise_scale)
        sample = value + harmonic + noise
        lower = min(config.r_min, config.r_max) - 1.0
        upper = max(config.r_min, config.r_max) + 1.0
        sequence.append(min(max(sample, lower), upper))
    return sequence


def run_impedance_trace(
    control: Sequence[float],
    *,
    theta: float,
    beta: float,
    relief_gain: float,
    recovery_rate: float,
    hysteresis: float,
    baseline: float,
    floor: float,
    ceiling: float,
) -> Dict[str, object]:
    """Propagate the resonant impedance motif and summarise diagnostics."""

    motif = ResonantImpedance(
        theta=theta,
        beta=beta,
        relief_gain=relief_gain,
        recovery_rate=recovery_rate,
        hysteresis=hysteresis,
        baseline=baseline,
        floor=floor,
        ceiling=ceiling,
    )
    history = motif.trace(control)
    summary = motif.summarise(history, store={})
    relief_series = list(history["relief"])
    recovery_series = list(history["recovery"])
    hysteresis_series = list(history["hysteresis"])
    summary.update(
        {
            "relief_mean": mean(relief_series) if relief_series else 0.0,
            "recovery_mean": mean(recovery_series) if recovery_series else 0.0,
            "hysteresis_mean": mean(hysteresis_series) if hysteresis_series else 0.0,
            "relief_min": min(relief_series) if relief_series else 0.0,
            "recovery_min": min(recovery_series) if recovery_series else 0.0,
            "hysteresis_min": min(hysteresis_series) if hysteresis_series else 0.0,
        }
    )
    return {
        "history": history,
        "summary": summary,
    }


def build_payload(
    control: Sequence[float],
    gate: Sequence[float],
    impedance_history: Mapping[str, Sequence[float]],
    impedance_summary: Mapping[str, float],
) -> Mapping[str, object]:
    """Fit logistic parameters and assemble the UTF summary payload."""

    fit_metrics = fit_threshold_parameters(control, gate)
    null_metrics = {
        "linear": evaluate_null_model(control, gate),
        "power_law": evaluate_power_law_null(control, gate),
    }

    logistic_summary = assemble_summary(
        {
            "R": list(control),
            "sigma": list(gate),
            "zeta": list(impedance_history["zeta"]),
            "flux": list(impedance_history["relief"]),
        },
        fit_metrics,
        null_metrics,
    )

    logistic_summary["dataset"] = {
        "name": "resonant_impedance_gate_sweep",
        "path": None,
        "control_parameter": "synthetic logistic sweep of R",
        "order_parameter": "impedance gate occupancy σ(β(R-Θ))",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    def _to_float(value: object) -> object:
        if isinstance(value, (int, float)):
            return float(value)
        return value

    impedance_block = {key: _to_float(value) for key, value in impedance_summary.items()}
    impedance_block.update(
        {
            "relief_mean": float(impedance_summary.get("relief_mean", 0.0)),
            "recovery_mean": float(impedance_summary.get("recovery_mean", 0.0)),
            "hysteresis_mean": float(impedance_summary.get("hysteresis_mean", 0.0)),
            "relief_min": float(impedance_summary.get("relief_min", 0.0)),
            "recovery_min": float(impedance_summary.get("recovery_min", 0.0)),
            "hysteresis_min": float(impedance_summary.get("hysteresis_min", 0.0)),
        }
    )

    logistic_summary["impedance_diagnostics"] = impedance_block

    logistic_summary["tri_layer"] = {
        "formal": "Logit regression of impedance gate vs. smooth nulls with relief/recovery diagnostics.",
        "empirical": "Synthetic sweep ensures reproducible impedance telemetry for cohort benchmarking.",
        "metaphorical": "Charts how the gate exhales (relief) and inhales (recovery) as the dawn chorus rises.",
    }

    return logistic_summary


def parse_args() -> argparse.Namespace:
    """Configure CLI options for the impedance diagnostic sweep."""

    parser = argparse.ArgumentParser(
        description="Generate resonant impedance diagnostics and logistic falsification summaries.",
    )
    parser.add_argument("--samples", type=int, default=512, help="Number of control samples across the sweep (default: 512).")
    parser.add_argument("--r-min", type=float, default=0.0, help="Minimum control-parameter value (default: 0.0).")
    parser.add_argument("--r-max", type=float, default=1.5, help="Maximum control-parameter value (default: 1.5).")
    parser.add_argument("--theta", type=float, default=0.62, help="Impedance gate threshold Θ (default: 0.62).")
    parser.add_argument("--beta", type=float, default=9.5, help="Impedance gate steepness β (default: 9.5).")
    parser.add_argument(
        "--relief-gain",
        type=float,
        default=0.58,
        help="Strength of impedance relief toward the floor when σ exceeds Θ (default: 0.58).",
    )
    parser.add_argument(
        "--recovery-rate",
        type=float,
        default=0.21,
        help="Rate guiding impedance back to its baseline when the gate quiets (default: 0.21).",
    )
    parser.add_argument(
        "--hysteresis",
        type=float,
        default=0.28,
        help="Hysteresis braid weighting gate changes for smooth opening/closing (default: 0.28).",
    )
    parser.add_argument("--baseline", type=float, default=0.84, help="Baseline impedance when the membrane rests (default: 0.84).")
    parser.add_argument("--floor", type=float, default=0.18, help="Impedance floor reached at full relief (default: 0.18).")
    parser.add_argument("--ceiling", type=float, default=1.06, help="Maximum impedance ceiling (default: 1.06).")
    parser.add_argument(
        "--harmonic-gain",
        type=float,
        default=0.08,
        help="Amplitude of harmonic modulation applied to the control sweep (default: 0.08).",
    )
    parser.add_argument(
        "--harmonic-period",
        type=float,
        default=48.0,
        help="Period of the harmonic modulation in control samples (default: 48).",
    )
    parser.add_argument(
        "--noise-scale",
        type=float,
        default=0.015,
        help="Standard deviation of Gaussian noise added to the control sweep (default: 0.015).",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for the harmonic noise generator (default: 42).")
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS_PATH,
        help="Destination for the JSON diagnostics payload (default: analysis/results/resonant_impedance_diagnostics.json).",
    )
    return parser.parse_args()


def main() -> None:
    """Execute the impedance sweep and persist UTF diagnostics."""

    args = parse_args()
    config = SweepConfig(
        samples=args.samples,
        r_min=args.r_min,
        r_max=args.r_max,
        harmonic_gain=args.harmonic_gain,
        harmonic_period=args.harmonic_period,
        noise_scale=args.noise_scale,
        seed=args.seed,
    )
    control = _generate_control_sequence(config)
    trace = run_impedance_trace(
        control,
        theta=args.theta,
        beta=args.beta,
        relief_gain=args.relief_gain,
        recovery_rate=args.recovery_rate,
        hysteresis=args.hysteresis,
        baseline=args.baseline,
        floor=args.floor,
        ceiling=args.ceiling,
    )

    payload = build_payload(control, trace["history"]["gate"], trace["history"], trace["summary"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")

    print("Resonant impedance diagnostics exported to", args.output)


if __name__ == "__main__":
    main()

