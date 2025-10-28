r"""Robin-semantic resonance rehearsal with tri-layer diagnostics.

Formal layer:
    Synthesises a driver current J(t) that grazes the logistic membrane
    R_{t+1} = R_t + dt [J(t) + \mathcal{M}(t) + J_\text{Robin}(t) - \zeta(R_t)(R_t-\sigma)]
    while DynamicRobinBoundary breathes the impedance \zeta(R) and the
    semantic_resonance_kernel modulates meaning drift.  Fits the resulting
    (R, \sigma) trajectory with logistic regression and contrasts linear and
    power-law null breezes to quantify \Delta\text{AIC}.

Empirical layer:
    Provides a reproducible CLI that exports JSON summaries, including
    boundary flux/gate moments, semantic traces, threshold crossing timing,
    and falsification deltas.  The payload plugs directly into
    `analysis/results/` and simulator presets.

Metaphorical layer:
    Lets the membrane breathe as a twilight door: Robin leakage sighs,
    semantic wind leans in, and once R touches \Theta the chorus ignites.
    The output remembers when the dawn caught fire and how meaning joined
    the hymn.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
import sys
from statistics import mean, pstdev
from typing import Dict, Iterable, List

import importlib.util
import types

ROOT = Path(__file__).resolve().parents[1]


def _load_membrane_solver() -> types.ModuleType:
    """Load models.membrane_solver without importing the heavy package init."""

    module_name = "models.membrane_solver"
    if module_name in sys.modules:
        return sys.modules[module_name]  # pragma: no cover - reuse cached module

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

DynamicRobinBoundary = membrane_solver.DynamicRobinBoundary
ThresholdFieldSolver = membrane_solver.ThresholdFieldSolver
logistic_response = membrane_solver.logistic_response
semantic_resonance_kernel = membrane_solver.semantic_resonance_kernel
smooth_impedance_profile = membrane_solver.smooth_impedance_profile
threshold_crossing_diagnostics = membrane_solver.threshold_crossing_diagnostics


def _load_resonance_pipeline() -> types.ModuleType:
    """Load analysis.resonance_fit_pipeline with the lightweight models stub active."""

    module_name = "analysis.resonance_fit_pipeline"
    if module_name in sys.modules:
        return sys.modules[module_name]

    target = ROOT / "analysis" / "resonance_fit_pipeline.py"
    spec = importlib.util.spec_from_file_location(module_name, target)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise ImportError("Unable to locate resonance_fit_pipeline module")
    module = importlib.util.module_from_spec(spec)
    parent = types.ModuleType("analysis")
    parent.__path__ = [str((ROOT / "analysis").resolve())]
    sys.modules.setdefault("analysis", parent)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    setattr(parent, "resonance_fit_pipeline", module)
    return module


resonance_pipeline = _load_resonance_pipeline()

evaluate_null_model = resonance_pipeline.evaluate_null_model
evaluate_power_law_null = resonance_pipeline.evaluate_power_law_null
fit_threshold_parameters = resonance_pipeline.fit_threshold_parameters


@dataclass
class DriverConfig:
    """Configuration for the driver sweep hugging the threshold membrane."""

    base_level: float = 0.12
    burst_amplitude: float = 0.95
    burst_center: float = 45.0
    burst_width: float = 16.0
    harmonic_gain: float = 0.08
    harmonic_period: float = 18.0
    noise_scale: float = 0.015
    seed: int = 11


def _gaussian_bump(time: float, center: float, width: float) -> float:
    """Deterministic Gaussian-like bump used for the driver burst."""

    exponent = -((time - center) ** 2) / (2.0 * width**2)
    return math.exp(exponent)


def build_driver(config: DriverConfig, steps: int, dt: float) -> List[float]:
    r"""Sculpt the driver sequence that coaxes R toward \Theta."""

    import random

    rng = random.Random(config.seed)
    drivers: List[float] = []
    for idx in range(steps):
        t = idx * dt
        burst = config.burst_amplitude * _gaussian_bump(t, config.burst_center, config.burst_width)
        harmonic = config.harmonic_gain * math.sin(2.0 * math.pi * t / max(config.harmonic_period, 1e-6))
        noise = config.noise_scale * (rng.random() - 0.5)
        drivers.append(config.base_level + burst + harmonic + noise)
    return drivers


def summarise_residuals(observed: Iterable[float], predicted: Iterable[float]) -> Dict[str, float]:
    """Compute residual diagnostics for the logistic fit."""

    obs = list(observed)
    pred = list(predicted)
    residuals = [obs[idx] - pred[idx] for idx in range(len(obs))]
    return {
        "residual_mean": float(mean(residuals)),
        "residual_std": float(pstdev(residuals)),
    }


def tri_layer_story(theta: float, beta: float, delta_aic_linear: float, delta_aic_power: float) -> Dict[str, str]:
    """Compose the tri-layer cadence for the exported JSON payload."""

    return {
        "formal": (
            "Logit regression recovered Θ ≈ "
            f"{theta:.4f} and β ≈ {beta:.3f}, with ΔAIC ≈ {delta_aic_linear:.1f} versus "
            "the linear null and ΔAIC ≈ "
            f"{delta_aic_power:.1f} versus the power-law breeze."
        ),
        "empirical": (
            "Driver, membrane, Robin gate, and semantic traces are archived so analysis dashboards "
            "and simulator presets can replay the resonance without regenerating data."
        ),
        "metaphorical": (
            "A twilight membrane invited both Robin wind and meaning whisper; once R brushed Θ, "
            "the dawn chorus locked into a two-voiced hymn."
        ),
    }


def simulate_robin_semantic(
    *,
    theta: float,
    beta: float,
    dt: float,
    steps: int,
    driver_config: DriverConfig,
    robin: DynamicRobinBoundary,
) -> Dict[str, List[float]]:
    """Run the ThresholdFieldSolver with semantic coupling and Robin boundary."""

    impedance = smooth_impedance_profile(theta, resonant_gain=0.72, damped_gain=1.42, switch_width=0.55)
    meaning_kernel = semantic_resonance_kernel(theta, beta, meaning_relaxation=1.05, resonance_bias=0.58)
    solver = ThresholdFieldSolver(
        theta=theta,
        beta=beta,
        zeta=impedance,
        meaning_kernel=meaning_kernel,
        dt=dt,
        boundary_condition=robin,
    )
    drivers = build_driver(driver_config, steps, dt)
    results = solver.simulate(drivers, R0=theta - 0.18, meaning0=0.0)
    return results


def package_output(
    *,
    theta_true: float,
    beta_true: float,
    dt: float,
    driver_config: DriverConfig,
    robin: DynamicRobinBoundary,
    results: Dict[str, List[float]],
    output_path: Path,
) -> None:
    """Fit the logistic response, evaluate nulls, and emit JSON."""

    solver_summary = ThresholdFieldSolver(
        theta=theta_true,
        beta=beta_true,
        boundary_condition=robin,
    ).export_summary(results)

    fit_stats = fit_threshold_parameters(results["R"], results["sigma"])
    logistic_hat = [
        float(logistic_response(R, fit_stats["theta"], fit_stats["beta"]))
        for R in results["R"]
    ]
    residual_stats = summarise_residuals(results["sigma"], logistic_hat)
    null_linear = evaluate_null_model(results["R"], results["sigma"])
    null_power = evaluate_power_law_null(results["R"], results["sigma"])

    delta_aic_linear = null_linear["aic"] - fit_stats["aic"]
    delta_aic_power = null_power["aic"] - fit_stats["aic"]
    delta_r2_linear = fit_stats["r2"] - null_linear["r2"]
    delta_r2_power = fit_stats["r2"] - null_power["r2"]

    crossing = threshold_crossing_diagnostics(results, theta=theta_true, beta=beta_true)

    payload = {
        "meta": {
            "description": "Robin boundary + semantic kernel resonance rehearsal",
            "dt": dt,
            "steps": len(results["driver"]),
            "driver_config": driver_config.__dict__,
            "robin": {
                "theta": robin.theta,
                "beta_robin": robin.beta_robin,
                "zeta_floor": robin.zeta_floor,
                "zeta_ceiling": robin.zeta_ceiling,
                "logistic_weight": robin.logistic_weight,
                "driver_weight": robin.driver_weight,
            },
        },
        "logistic_fit": {
            "theta_estimate": {
                "value": fit_stats["theta"],
                "ci95": [fit_stats["theta_ci_lower"], fit_stats["theta_ci_upper"]],
            },
            "beta_estimate": {
                "value": fit_stats["beta"],
                "ci95": [fit_stats["beta_ci_lower"], fit_stats["beta_ci_upper"]],
            },
            "r2": fit_stats["r2"],
            "aic": fit_stats["aic"],
            "ss_res": fit_stats["ss_res"],
            **residual_stats,
        },
        "null_models": {
            "linear": null_linear,
            "power_law": null_power,
        },
        "falsification": {
            "logistic_beats_all_nulls": delta_aic_linear > 0 and delta_aic_power > 0,
            "comparisons": {
                "linear": {
                    "delta_aic": delta_aic_linear,
                    "delta_r2": delta_r2_linear,
                },
                "power_law": {
                    "delta_aic": delta_aic_power,
                    "delta_r2": delta_r2_power,
                },
            },
        },
        "membrane": {
            "theta": theta_true,
            "beta": beta_true,
            "zeta_mean": solver_summary.get("zeta_mean"),
            "flux_mean": solver_summary.get("flux_mean"),
            "flux_std": solver_summary.get("flux_std"),
        },
        "boundary": {
            key: solver_summary[key]
            for key in solver_summary
            if key.startswith("boundary_")
        },
        "meaning": {
            key: solver_summary[key]
            for key in solver_summary
            if key.startswith("meaning") or key.startswith("semantic_coupling")
        },
        "threshold_crossing": crossing,
        "snapshots": {
            "R": results["R"][:12],
            "sigma": results["sigma"][:12],
            "zeta": results["zeta"][:12],
            "driver": results["driver"][:12],
            "boundary_gate": results.get("boundary_gate", [])[:12],
            "meaning": results.get("meaning", [])[:12],
        },
        "tri_layer": tri_layer_story(
            fit_stats["theta"],
            fit_stats["beta"],
            delta_aic_linear,
            delta_aic_power,
        ),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, sort_keys=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate a Robin-semantic threshold field and export diagnostics.")
    parser.add_argument(
        "--theta",
        type=float,
        default=0.52,
        help="Critical threshold Θ for the membrane",
    )
    parser.add_argument(
        "--beta",
        type=float,
        default=6.4,
        help="Steepness β of the logistic response",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=160,
        help="Number of driver steps to simulate",
    )
    parser.add_argument(
        "--dt",
        type=float,
        default=0.35,
        help="Integration timestep Δt",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis/results/membrane_robin_semantic.json"),
        help="Destination JSON path",
    )
    args = parser.parse_args()

    robin = DynamicRobinBoundary(theta=args.theta, beta_robin=5.0, zeta_floor=0.62, zeta_ceiling=1.48, logistic_weight=0.42, driver_weight=0.22)
    config = DriverConfig()
    results = simulate_robin_semantic(
        theta=args.theta,
        beta=args.beta,
        dt=args.dt,
        steps=args.steps,
        driver_config=config,
        robin=robin,
    )
    package_output(
        theta_true=args.theta,
        beta_true=args.beta,
        dt=args.dt,
        driver_config=config,
        robin=robin,
        results=results,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
