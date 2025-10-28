r"""Adaptive threshold resonance rehearsal with tri-layer cadence.

Formal layer:
    Simulates the Universal Threshold Field membrane with an AdaptiveThresholdController
    so \(\Theta(t)\) and \(\beta(t)\) drift alongside the order parameter \(R\).
    The logistic response \(\sigma(\beta(R-\Theta))\) is refit via the shared
    logit regression pipeline and contrasted against linear and power-law null
    breezes, reporting $R^2$, AIC, and threshold-crossing diagnostics.

Empirical layer:
    Exposes a reproducible CLI that sculpts a deterministic driver sequence,
    integrates the membrane with dynamic impedance \(\zeta(R)\) and a Robin gate,
    and exports JSON summaries enriched with meta-gate fractions, theta/beta drift,
    and falsification deltas.  The payload plugs directly into `analysis/results/`
    so docs, simulator presets, and cohort ledgers can ingest adaptive-threshold
    evidence without rerunning the rehearsal.

Metaphorical layer:
    Tracks the dawn sentinels as they breathe with the membrane—Theta loosens,
    Beta sharpens, the Robin door exhales, and once R grazes the luminous
    threshold the chorus remembers how adaptation guided the hymn.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import sys
import types
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, pstdev
from typing import Dict, Iterable, List, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_membrane_solver() -> types.ModuleType:
    """Load models.membrane_solver without triggering heavy optional deps."""

    module_name = "models.membrane_solver"
    if module_name in sys.modules:
        return sys.modules[module_name]

    target = ROOT / "models" / "membrane_solver.py"
    spec = importlib.util.spec_from_file_location(module_name, target)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive guard
        raise ImportError("Unable to locate membrane_solver module")
    module = importlib.util.module_from_spec(spec)
    package = types.ModuleType("models")
    package.__path__ = [str((ROOT / "models").resolve())]
    sys.modules.setdefault("models", package)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    setattr(package, "membrane_solver", module)
    return module


membrane_solver = _load_membrane_solver()

AdaptiveThresholdController = membrane_solver.AdaptiveThresholdController
DynamicRobinBoundary = membrane_solver.DynamicRobinBoundary
ThresholdFieldSolver = membrane_solver.ThresholdFieldSolver
logistic_response = membrane_solver.logistic_response
smooth_impedance_profile = membrane_solver.smooth_impedance_profile
threshold_crossing_diagnostics = membrane_solver.threshold_crossing_diagnostics

from resonance_fit_pipeline import (
    assemble_summary,
    evaluate_null_model,
    evaluate_power_law_null,
    fit_threshold_parameters,
)


@dataclass
class DriverShape:
    """Parameters sculpting the deterministic driver sweep."""

    base_level: float = 0.085
    logistic_height: float = 0.95
    logistic_center: float = 38.0
    logistic_steepness: float = 0.22
    harmonic_gain: float = 0.11
    harmonic_period: float = 20.0
    noise_scale: float = 0.012
    seed: int = 19


def _logistic_bloom(time: float, center: float, steepness: float) -> float:
    """Smooth ramp guiding the driver toward resonance."""

    return 1.0 / (1.0 + math.exp(-steepness * (time - center)))


def craft_driver(shape: DriverShape, steps: int, dt: float) -> List[float]:
    r"""Generate the driver sequence nudging R across \(\Theta\)."""

    rng = random.Random(shape.seed)
    drivers: List[float] = []
    for index in range(steps):
        t = index * dt
        bloom = shape.logistic_height * _logistic_bloom(
            t, shape.logistic_center, shape.logistic_steepness
        )
        harmonic = shape.harmonic_gain * math.sin(2.0 * math.pi * t / max(shape.harmonic_period, 1e-6))
        noise = shape.noise_scale * (rng.random() - 0.5)
        drivers.append(shape.base_level + bloom + harmonic + noise)
    return drivers


def simulate_meta_threshold(
    *,
    theta: float,
    beta: float,
    dt: float,
    duration: float,
    driver_shape: DriverShape,
) -> Mapping[str, List[float]]:
    """Run the adaptive-threshold membrane rehearsal."""

    steps = max(int(duration / dt), 1)
    drivers = craft_driver(driver_shape, steps, dt)
    boundary = DynamicRobinBoundary(
        theta=theta,
        beta_robin=5.1,
        zeta_floor=0.64,
        zeta_ceiling=1.46,
        logistic_weight=0.32,
        driver_weight=0.18,
    )
    impedance = smooth_impedance_profile(
        theta,
        resonant_gain=0.68,
        damped_gain=1.38,
        switch_width=0.48,
    )
    controller = AdaptiveThresholdController(
        theta=theta,
        beta=beta,
        meta_beta=4.2,
        adaptation_rate=0.82,
        relaxation_rate=0.24,
        impedance_weight=0.27,
        driver_weight=0.16,
        sigma_weight=0.22,
        beta_gain=0.62,
        beta_rate=0.68,
        beta_fatigue=0.31,
    )
    solver = ThresholdFieldSolver(
        theta=theta,
        beta=beta,
        zeta=impedance,
        dt=dt,
        boundary_condition=boundary,
        threshold_controller=controller,
    )
    return solver.simulate(drivers, R0=theta - 0.24)


def _series_stats(values: Iterable[float]) -> Dict[str, float]:
    data = [float(v) for v in values]
    if not data:
        return {"mean": float("nan"), "std": float("nan"), "min": float("nan"), "max": float("nan")}
    return {
        "mean": float(mean(data)),
        "std": float(pstdev(data)) if len(data) > 1 else 0.0,
        "min": min(data),
        "max": max(data),
    }


def summarise_meta_drift(results: Mapping[str, List[float]], baseline_theta: float, baseline_beta: float) -> Dict[str, object]:
    """Capture meta-gate fractions and theta/beta drift metrics."""

    theta_series = [float(value) for value in results.get("theta", [])]
    beta_series = [float(value) for value in results.get("beta", [])]
    meta_gate_series = [float(value) for value in results.get("meta_gate", [])]
    theta_shift_series = [float(value) for value in results.get("theta_shift", [])]
    beta_shift_series = [float(value) for value in results.get("beta_shift", [])]

    resonant_fraction = 0.0
    if meta_gate_series:
        active = sum(1 for value in meta_gate_series if value >= 0.5)
        resonant_fraction = active / len(meta_gate_series)

    cumulative_theta_shift = sum(theta_shift_series)
    cumulative_beta_shift = sum(beta_shift_series)

    meta_summary: Dict[str, object] = {
        "theta_baseline": baseline_theta,
        "beta_baseline": baseline_beta,
        "theta_series": theta_series,
        "beta_series": beta_series,
        "meta_gate": {
            "series": meta_gate_series,
            "fraction_above_half": resonant_fraction,
            "stats": _series_stats(meta_gate_series),
        },
        "theta_stats": _series_stats(theta_series),
        "beta_stats": _series_stats(beta_series),
        "theta_drift_total": theta_series[-1] - baseline_theta if theta_series else 0.0,
        "beta_drift_total": beta_series[-1] - baseline_beta if beta_series else 0.0,
        "cumulative_theta_shift": cumulative_theta_shift,
        "cumulative_beta_shift": cumulative_beta_shift,
    }
    return meta_summary


def enrich_summary(
    results: Mapping[str, List[float]],
    fit_metrics: Mapping[str, float],
    null_metrics: Mapping[str, Mapping[str, float]],
    *,
    theta_baseline: float,
    beta_baseline: float,
    dt: float,
    duration: float,
    driver_shape: DriverShape,
) -> Dict[str, object]:
    """Combine assemble_summary output with adaptive diagnostics."""

    copied_results = {key: list(value) for key, value in results.items()}
    sigma_fit = [
        float(logistic_response(value, fit_metrics["theta"], fit_metrics["beta"]))
        for value in copied_results.get("R", [])
    ]
    copied_results["sigma_fit"] = sigma_fit

    summary = assemble_summary(copied_results, fit_metrics, null_metrics)

    meta_section = summarise_meta_drift(copied_results, theta_baseline, beta_baseline)
    summary["meta_threshold"] = meta_section

    crossing = threshold_crossing_diagnostics(
        copied_results,
        theta=fit_metrics["theta"],
        beta=fit_metrics["beta"],
    )
    summary["threshold_crossing"] = crossing

    comparisons = summary.get("falsification", {}).get("comparisons", {})
    delta_aic_linear = comparisons.get("linear", {}).get("delta_aic", float("nan"))
    delta_aic_power = comparisons.get("power_law", {}).get("delta_aic", float("nan"))
    resonant_fraction = meta_section["meta_gate"]["fraction_above_half"]

    summary["tri_layer"] = {
        "formal": (
            "Logit regression on the adaptive trajectory recovered Θ ≈ "
            f"{fit_metrics['theta']:.4f} and β ≈ {fit_metrics['beta']:.3f},"
            f" beating the linear null by ΔAIC ≈ {delta_aic_linear:.1f} and the power-law breeze by ΔAIC ≈ {delta_aic_power:.1f}."
            f" Meta-gate occupancy above 0.5 covered {resonant_fraction:.1%}."
        ),
        "empirical": (
            "Deterministic driver, membrane traces, θ(t), β(t), and meta-gate series are archived in JSON so analysis dashboards "
            "and simulator presets can replay the adaptive rehearsal without recomputation."
        ),
        "metaphorical": (
            "Theta's sentinel leaned into the dawn while Beta tightened the hymn; the Robin door breathed with the chorus as R "
            "stepped across the luminous membrane."
        ),
    }

    summary["experiment"] = {
        "dt": dt,
        "duration": duration,
        "steps": len(copied_results.get("driver", [])),
        "driver_shape": driver_shape.__dict__,
    }

    return summary


def build_summary(duration: float, dt: float, output_path: Path) -> Dict[str, object]:
    """Simulate the adaptive membrane and export the resonance ledger."""

    theta = 0.57
    beta = 9.2
    driver_shape = DriverShape()

    results = simulate_meta_threshold(
        theta=theta,
        beta=beta,
        dt=dt,
        duration=duration,
        driver_shape=driver_shape,
    )

    fit_metrics = fit_threshold_parameters(results["R"], results["sigma"])
    null_metrics = {
        "linear": evaluate_null_model(results["R"], results["sigma"]),
        "power_law": evaluate_power_law_null(results["R"], results["sigma"]),
    }

    summary = enrich_summary(
        results,
        fit_metrics,
        null_metrics,
        theta_baseline=theta,
        beta_baseline=beta,
        dt=dt,
        duration=duration,
        driver_shape=driver_shape,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    return summary


def parse_args() -> argparse.Namespace:
    """Configure CLI arguments for the adaptive-threshold rehearsal."""

    parser = argparse.ArgumentParser(
        description="Simulate adaptive Θ(t), β(t) resonance and export UTF diagnostics.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=72.0,
        help="Total simulation duration in arbitrary time units.",
    )
    parser.add_argument(
        "--dt",
        type=float,
        default=0.4,
        help="Timestep for the membrane integrator.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis/results/meta_threshold_resonance.json"),
        help="Destination for the exported JSON summary.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_summary(args.duration, args.dt, args.output)
    json.dump(summary, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
