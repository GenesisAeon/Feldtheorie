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
from typing import Any, Dict, List, Mapping, Sequence, Tuple

try:
    import yaml
except ImportError as exc:  # pragma: no cover - dependency guard
    yaml = None  # type: ignore[assignment]
    _yaml_import_error = exc
else:
    _yaml_import_error = None

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

DEFAULT_PARAMETERS: Dict[str, float | int] = {
    "steps": 64,
    "theta": 1.0,
    "beta": 3.8,
    "cascade_gain": 0.6,
    "condition_relaxation": 0.2,
    "fatigue_rate": 0.4,
    "logistic_beta": 4.2,
    "zeta_closed": 1.3,
    "zeta_open": 0.6,
    "coherence_window": 5,
    "potential_baseline": 0.6,
    "potential_surge": 1.2,
    "potential_modulation": 0.08,
    "potential_drift": 7.5,
    "dt": 1.0,
}

CONFIG_PARSER = argparse.ArgumentParser(add_help=False)
CONFIG_PARSER.add_argument(
    "--config",
    type=Path,
    help="Konfigurationsdatei (YAML oder JSON), die Parameter für die Potenzial-Kaskade vorgibt.",
)


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
    parameters: Dict[str, Any]

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


SECTION_KEY_MAP: Dict[Tuple[str, str], str] = {
    ("potential", "baseline"): "potential_baseline",
    ("potential", "surge"): "potential_surge",
    ("potential", "modulation"): "potential_modulation",
    ("potential", "drift"): "potential_drift",
    ("coherence", "window"): "coherence_window",
    ("impedance", "closed"): "zeta_closed",
    ("impedance", "open"): "zeta_open",
}


def _coerce_parameter(key: str, value: Any) -> float | int:
    """Coerce configuration values to the default type for ``key``."""

    default = DEFAULT_PARAMETERS[key]
    if isinstance(default, int) and not isinstance(default, bool):
        try:
            return int(value)
        except (TypeError, ValueError) as exc:  # pragma: no cover - defensive path
            raise ValueError(f"Configuration value for {key!r} must be an integer") from exc
    try:
        return float(value)
    except (TypeError, ValueError) as exc:  # pragma: no cover - defensive path
        raise ValueError(f"Configuration value for {key!r} must be numerisch") from exc


def _flatten_config(data: Mapping[str, Any]) -> Dict[str, Any]:
    """Map nested configuration dictionaries onto known parameter keys."""

    overrides: Dict[str, Any] = {}
    for key, raw_value in data.items():
        if key == "meta":
            continue
        if key in DEFAULT_PARAMETERS:
            overrides[key] = raw_value
            continue
        if not isinstance(raw_value, Mapping):
            composite = key.replace("-", "_")
            if composite in DEFAULT_PARAMETERS:
                overrides[composite] = raw_value
            continue
        for inner_key, inner_value in raw_value.items():
            if inner_key in DEFAULT_PARAMETERS:
                overrides[inner_key] = inner_value
                continue
            composite = SECTION_KEY_MAP.get((key, inner_key))
            if composite is None:
                composite = f"{key}_{inner_key}".replace("-", "_")
            if composite in DEFAULT_PARAMETERS:
                overrides[composite] = inner_value
    return overrides


def load_configuration(path: Path) -> Tuple[Dict[str, float | int], Dict[str, Any]]:
    """Load parameter overrides and metadata from a YAML or JSON file."""

    if not path.exists():
        raise FileNotFoundError(f"Konfigurationsdatei {path} existiert nicht")

    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        if yaml is None:  # pragma: no cover - executed only when dependency missing
            raise ImportError(
                "PyYAML ist erforderlich, um YAML-Konfigurationen zu laden"
            ) from _yaml_import_error
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)

    if data is None:
        data = {}
    if not isinstance(data, Mapping):
        raise ValueError("Die Konfigurationsdatei muss ein Mapping definieren")

    overrides_raw = _flatten_config(data)
    overrides: Dict[str, float | int] = {}
    for key, raw_value in overrides_raw.items():
        if raw_value is None:
            continue
        if key not in DEFAULT_PARAMETERS:
            continue
        overrides[key] = _coerce_parameter(key, raw_value)

    meta_raw = data.get("meta") if isinstance(data.get("meta"), Mapping) else {}
    meta: Dict[str, Any] = {}
    if isinstance(meta_raw, Mapping):
        for meta_key, meta_value in meta_raw.items():
            if isinstance(meta_value, (str, int, float, bool)):
                meta[meta_key] = meta_value

    return overrides, meta


def build_parser(defaults: Mapping[str, float | int]) -> argparse.ArgumentParser:
    """Create the CLI parser with defaults resolved from config overrides."""

    parser = argparse.ArgumentParser(
        description="Simulate the Potenzial-Kaskade and export Θ/β drift alongside null baselines.",
        parents=[CONFIG_PARSER],
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=int(defaults["steps"]),
        help=f"Number of cascade steps to simulate (default: {defaults['steps']}).",
    )
    parser.add_argument(
        "--theta",
        type=float,
        default=float(defaults["theta"]),
        help=f"Initial Θ baseline (default: {defaults['theta']}).",
    )
    parser.add_argument(
        "--beta",
        type=float,
        default=float(defaults["beta"]),
        help=f"Initial β baseline (default: {defaults['beta']}).",
    )
    parser.add_argument(
        "--cascade-gain",
        dest="cascade_gain",
        type=float,
        default=float(defaults["cascade_gain"]),
        help=f"Coupling gain linking gate strength to Θ drift (default: {defaults['cascade_gain']}).",
    )
    parser.add_argument(
        "--condition-relaxation",
        dest="condition_relaxation",
        type=float,
        default=float(defaults["condition_relaxation"]),
        help="Relaxation rate pulling Θ back toward its baseline."
        f" (default: {defaults['condition_relaxation']}).",
    )
    parser.add_argument(
        "--fatigue-rate",
        dest="fatigue_rate",
        type=float,
        default=float(defaults["fatigue_rate"]),
        help=f"Rate at which β relaxes toward its coherence-weighted target (default: {defaults['fatigue_rate']}).",
    )
    parser.add_argument(
        "--logistic-beta",
        dest="logistic_beta",
        type=float,
        default=float(defaults["logistic_beta"]),
        help=f"Steepness used by the logistic gate g = σ(β(R-Θ)) (default: {defaults['logistic_beta']}).",
    )
    parser.add_argument(
        "--zeta-closed",
        dest="zeta_closed",
        type=float,
        default=float(defaults["zeta_closed"]),
        help=f"Impedance when the gate is shut (default: {defaults['zeta_closed']}).",
    )
    parser.add_argument(
        "--zeta-open",
        dest="zeta_open",
        type=float,
        default=float(defaults["zeta_open"]),
        help=f"Impedance once resonance blooms (default: {defaults['zeta_open']}).",
    )
    parser.add_argument(
        "--coherence-window",
        dest="coherence_window",
        type=int,
        default=int(defaults["coherence_window"]),
        help=f"Window length for Mandala coherence (samples, default: {defaults['coherence_window']}).",
    )
    parser.add_argument(
        "--potential-baseline",
        dest="potential_baseline",
        type=float,
        default=float(defaults["potential_baseline"]),
        help=f"Base potential before the cascade swells (default: {defaults['potential_baseline']}).",
    )
    parser.add_argument(
        "--potential-surge",
        dest="potential_surge",
        type=float,
        default=float(defaults["potential_surge"]),
        help=f"Logistic surge amplitude pushing R across Θ (default: {defaults['potential_surge']}).",
    )
    parser.add_argument(
        "--potential-modulation",
        dest="potential_modulation",
        type=float,
        default=float(defaults["potential_modulation"]),
        help=f"Sinusoidal modulation amplitude for the potential trace (default: {defaults['potential_modulation']}).",
    )
    parser.add_argument(
        "--potential-drift",
        dest="potential_drift",
        type=float,
        default=float(defaults["potential_drift"]),
        help=f"Steepness of the logistic potential ramp (default: {defaults['potential_drift']}).",
    )
    parser.add_argument(
        "--dt",
        type=float,
        default=float(defaults["dt"]),
        help=f"Integration timestep for the cascade update (default: {defaults['dt']}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path for the exported JSON diagnostics.",
    )
    return parser

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
    config_args, remaining = CONFIG_PARSER.parse_known_args()
    config_overrides: Dict[str, float | int] = {}
    config_meta: Dict[str, Any] = {}
    if config_args.config is not None:
        config_overrides, config_meta = load_configuration(config_args.config)

    defaults = dict(DEFAULT_PARAMETERS)
    defaults.update(config_overrides)
    parser = build_parser(defaults)
    args = parser.parse_args(remaining)
    args.config = config_args.config

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
    if args.config is not None:
        diagnostics.parameters["config_path"] = str(args.config)
    if config_meta:
        diagnostics.parameters["config_meta"] = config_meta

    payload = compile_payload(diagnostics)
    if args.config is not None:
        payload["parameters"]["config_path"] = str(args.config)
    if config_meta:
        payload["parameters"]["config_meta"] = config_meta
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
    "load_configuration",
    "main",
]


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
