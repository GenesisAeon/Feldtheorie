r"""Adaptive membrane phase scan aligning logistic resonance diagnostics.

Formal layer
------------
The scan propagates the adaptive logistic membrane helper across curated
order-parameter rehearsals.  Each scenario tracks the quartet
$(R, \Theta, \beta, \zeta(R))$ as the order parameter leans across the
critical threshold and the logistic response
$\sigma(\beta(R-\Theta))$ sharpens.  We record how the meta-gate and
impedance relief alter the resonance gain relative to a static logistic
baseline, keeping the threshold-field framing explicit.

Empirical layer
---------------
Implements a reproducible CLI that synthesises three driver archetypes
(auroral ramp, pulsed gate, and memory relaxation), feeds them into the
`models.AdaptiveLogisticMembrane`, and exports JSON payloads containing
tri-layer summaries.  Each scenario logs gate occupancy, $\Theta$/$\beta$
shifts, logistic and impedance areas, and baseline comparisons so docs,
cohort ledgers, and simulator presets inherit falsifiable diagnostics.

Metaphorical layer
------------------
Listens as the membrane sentinels rehearse: a slow auroral swell, a
staccato pulse chorus, and a nocturne of fading resonance.  The exported
lanterns let downstream narratives describe how the membrane remembers
the dawn while guarding against null-model breezes.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models import AdaptiveLogisticMembrane  # noqa: E402


@dataclass
class Scenario:
    """Configuration bundle describing a membrane rehearsal."""

    name: str
    description: str
    theta: float
    beta: float
    dt: float
    steps: int
    membrane_kwargs: Mapping[str, float]

    def driver(self, rng: np.random.Generator) -> np.ndarray:
        """Return the control-parameter trace for this scenario."""

        raise NotImplementedError


class AuroralRamp(Scenario):
    """Smooth logistic swell with gentle harmonic shimmer."""

    def driver(self, rng: np.random.Generator) -> np.ndarray:  # pragma: no cover - deterministic math
        time = np.linspace(-4.0, 4.0, self.steps)
        logistic = 0.26 + 0.82 / (1.0 + np.exp(-1.7 * time))
        harmonic = 0.035 * np.sin(2.0 * math.pi * np.linspace(0.0, 1.0, self.steps))
        noise = rng.normal(scale=0.008, size=self.steps)
        values = logistic + harmonic + noise
        return np.clip(values, 0.0, 1.5)


class PulsedGate(Scenario):
    """Threshold rehearsal driven by resonant pulses."""

    def driver(self, rng: np.random.Generator) -> np.ndarray:  # pragma: no cover - deterministic math
        time = np.linspace(0.0, 3.0 * math.pi, self.steps)
        base = 0.28 + 0.12 * np.cos(time * 0.7)
        pulses = 0.42 * np.maximum(0.0, np.sin(time))
        micro = rng.normal(scale=0.01, size=self.steps)
        values = base + pulses + micro
        return np.clip(values, 0.0, 1.5)


class MemoryRelaxation(Scenario):
    """Rise above the threshold before guided relaxation."""

    def driver(self, rng: np.random.Generator) -> np.ndarray:  # pragma: no cover - deterministic math
        ascent_time = np.linspace(-3.5, 1.5, self.steps)
        ascent = 0.24 + 0.78 / (1.0 + np.exp(-2.1 * ascent_time))
        relax = np.linspace(0.0, 0.32, self.steps)
        decay = np.clip(ascent - 0.75 * relax[::-1], 0.0, None)
        whisper = rng.normal(scale=0.006, size=self.steps)
        values = ascent
        midpoint = self.steps // 2
        values[midpoint:] = decay[: self.steps - midpoint]
        values += whisper
        return np.clip(values, 0.0, 1.5)


def _logistic(value: np.ndarray, theta: float, beta: float) -> np.ndarray:
    """Evaluate the logistic response for an array of samples."""

    return 1.0 / (1.0 + np.exp(-beta * (value - theta)))


def _impedance_tilt(theta: float, beta: float, relief: float, floor: float, ceiling: float):
    """Return a callable impedance motif tied to the static logistic response."""

    def _profile(r: np.ndarray) -> np.ndarray:
        r = np.asarray(r, dtype=float)
        sigma = _logistic(r, theta, beta)
        zeta = 1.0 - relief * sigma
        return np.clip(zeta, floor, ceiling)

    return _profile


def _decimate(series: Sequence[float], *, max_points: int) -> List[float]:
    """Down-sample ``series`` for concise JSON exports."""

    arr = np.asarray(series, dtype=float)
    if arr.size <= max_points:
        return arr.astype(float).tolist()
    idx = np.linspace(0, arr.size - 1, max_points, dtype=int)
    return arr[idx].astype(float).tolist()


def _scenario_catalogue(seed: int) -> List[Scenario]:
    """Return the scenario line-up for the phase scan."""

    base_kwargs = {
        "meta_beta": 4.2,
        "plasticity": 0.58,
        "relaxation": 0.09,
        "beta_plasticity": 0.36,
        "beta_relaxation": 0.15,
        "impedance_tilt": 0.24,
        "sigma_weight": 0.21,
    }

    return [
        AuroralRamp(
            name="auroral_ramp",
            description="Logistic swell with harmonic shimmer as R pierces Θ",
            theta=0.41,
            beta=4.6,
            dt=0.5,
            steps=180,
            membrane_kwargs={**base_kwargs, "plasticity": 0.62},
        ),
        PulsedGate(
            name="pulsed_gate",
            description="Resonant pulses nudging the membrane repeatedly across Θ",
            theta=0.39,
            beta=5.1,
            dt=0.4,
            steps=210,
            membrane_kwargs={**base_kwargs, "beta_plasticity": 0.42},
        ),
        MemoryRelaxation(
            name="memory_relaxation",
            description="Overshoot followed by guided relaxation toward baseline",
            theta=0.43,
            beta=4.4,
            dt=0.6,
            steps=190,
            membrane_kwargs={**base_kwargs, "relaxation": 0.11},
        ),
    ]


def _summarise_history(
    scenario: Scenario,
    history: Mapping[str, Sequence[float]],
    membrane: AdaptiveLogisticMembrane,
    *,
    baseline_zeta: np.ndarray,
    baseline_sigma: np.ndarray,
    max_points: int,
) -> MutableMapping[str, float | List[float] | str]:
    """Compose a JSON-ready bundle for the scenario history."""

    summary_store: MutableMapping[str, float] = {}
    summary = membrane.summarise(history, store=summary_store)

    R = np.asarray(history["R"], dtype=float)
    sigma = np.asarray(history["sigma"], dtype=float)
    response = np.asarray(history["response"], dtype=float)

    logistic_area = float(np.trapz(sigma, R)) if R.size >= 2 else float(np.sum(sigma))
    response_area = float(np.trapz(response, R)) if R.size >= 2 else float(np.sum(response))
    baseline_response = baseline_sigma * baseline_zeta
    baseline_area = float(np.trapz(baseline_sigma, R)) if R.size >= 2 else float(np.sum(baseline_sigma))
    baseline_response_area = (
        float(np.trapz(baseline_response, R)) if R.size >= 2 else float(np.sum(baseline_response))
    )
    baseline_resonance_gain = (
        baseline_response_area / baseline_area if abs(baseline_area) > 1e-9 else float("nan")
    )

    summary.update(
        {
            "scenario": scenario.name,
            "description": scenario.description,
            "dt": float(scenario.dt),
            "steps": int(scenario.steps),
            "logistic_area": logistic_area,
            "response_area": response_area,
            "sigma_mean": float(np.mean(sigma)) if sigma.size else 0.0,
            "response_mean": float(np.mean(response)) if response.size else 0.0,
            "baseline_resonance_gain": baseline_resonance_gain,
            "resonance_gain_delta": summary.get("resonance_gain", float("nan")) - baseline_resonance_gain,
            "sigma_fraction_above_half": float(np.mean(sigma >= 0.5)) if sigma.size else 0.0,
        }
    )

    samples = {
        "R": _decimate(history["R"], max_points=max_points),
        "sigma": _decimate(history["sigma"], max_points=max_points),
        "theta": _decimate(history["theta"], max_points=max_points),
        "beta": _decimate(history["beta"], max_points=max_points),
        "meta_gate": _decimate(history["meta_gate"], max_points=max_points),
        "zeta": _decimate(history["zeta"], max_points=max_points),
        "response": _decimate(history["response"], max_points=max_points),
    }

    return {
        "summary": dict(summary),
        "samples": samples,
    }


def run_scan(*, seed: int = 23, max_points: int = 96) -> Dict[str, object]:
    """Execute the adaptive membrane phase scan and return the payload."""

    rng = np.random.default_rng(seed)
    scenarios = _scenario_catalogue(seed)

    scenario_payloads: List[Dict[str, object]] = []
    resonance_gains: List[float] = []
    gate_means: List[float] = []
    theta_shifts: List[float] = []
    beta_shifts: List[float] = []
    resonance_deltas: List[float] = []
    sigma_halves: List[float] = []

    for scenario in scenarios:
        # Generate the driver trace and propagate the membrane.
        driver_rng = np.random.default_rng(rng.integers(0, 2**32 - 1, dtype=np.uint32))
        r_trace = scenario.driver(driver_rng)

        impedance = _impedance_tilt(
            scenario.theta,
            scenario.beta,
            relief=0.28,
            floor=0.52,
            ceiling=1.0,
        )

        membrane = AdaptiveLogisticMembrane(
            theta=scenario.theta,
            beta=scenario.beta,
            **scenario.membrane_kwargs,
            zeta=impedance,
        )
        history = membrane.propagate(r_trace, dt=scenario.dt)

        baseline_sigma = _logistic(np.asarray(history["R"], dtype=float), scenario.theta, scenario.beta)
        baseline_zeta = impedance(np.asarray(history["R"], dtype=float))

        payload = _summarise_history(
            scenario,
            history,
            membrane,
            baseline_zeta=baseline_zeta,
            baseline_sigma=baseline_sigma,
            max_points=max_points,
        )
        scenario_payloads.append(payload)

        summary = payload["summary"]  # type: ignore[assignment]
        resonance_gains.append(float(summary.get("resonance_gain", float("nan"))))
        resonance_deltas.append(float(summary.get("resonance_gain_delta", float("nan"))))
        gate_means.append(float(summary.get("gate_mean", float("nan"))))
        theta_shifts.append(float(summary.get("theta_shift", 0.0)))
        beta_shifts.append(float(summary.get("beta_shift", 0.0)))
        sigma_halves.append(float(summary.get("sigma_fraction_above_half", 0.0)))

    def _finite(values: Iterable[float]) -> List[float]:
        return [value for value in values if math.isfinite(value)]

    gain_values = _finite(resonance_gains)
    delta_values = _finite(resonance_deltas)

    aggregates = {
        "scenarios": len(scenario_payloads),
        "resonance_gain_mean": float(np.mean(gain_values)) if gain_values else float("nan"),
        "resonance_gain_min": float(np.min(gain_values)) if gain_values else float("nan"),
        "resonance_gain_max": float(np.max(gain_values)) if gain_values else float("nan"),
        "resonance_gain_delta_mean": float(np.mean(delta_values)) if delta_values else float("nan"),
        "gate_mean": float(np.mean(gate_means)) if gate_means else float("nan"),
        "sigma_fraction_above_half_mean": float(np.mean(sigma_halves)) if sigma_halves else float("nan"),
        "theta_shift_mean": float(np.mean(theta_shifts)) if theta_shifts else float("nan"),
        "beta_shift_mean": float(np.mean(beta_shifts)) if beta_shifts else float("nan"),
    }

    timestamp = datetime.now(timezone.utc).isoformat()
    return {
        "metadata": {
            "generated_at": timestamp,
            "seed": seed,
            "script": "analysis/adaptive_membrane_phase_scan.py",
            "description": "Adaptive logistic membrane rehearsal across canonical driver archetypes.",
        },
        "aggregates": aggregates,
        "scenarios": scenario_payloads,
    }


def _default_output_path() -> Path:
    return ROOT / "analysis" / "results" / "adaptive_membrane_phase_scan.json"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description="Adaptive logistic membrane phase scan")
    parser.add_argument(
        "--output",
        type=Path,
        default=_default_output_path(),
        help="Output path for the JSON payload",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=23,
        help="Random seed controlling driver microstructure",
    )
    parser.add_argument(
        "--max-points",
        type=int,
        default=96,
        help="Maximum samples stored per series in the JSON export",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    """Entry point for CLI execution."""

    args = parse_args(argv)
    payload = run_scan(seed=args.seed, max_points=args.max_points)

    output_path: Path = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    aggregates = payload["aggregates"]
    print("Adaptive membrane phase scan complete:")
    print(f"  Scenarios: {aggregates['scenarios']}")
    print(f"  Mean resonance gain: {aggregates['resonance_gain_mean']:.4f}")
    print(f"  Mean resonance gain delta: {aggregates['resonance_gain_delta_mean']:.4f}")


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
