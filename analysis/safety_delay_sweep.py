r"""Safety-Delay sweep orchestrator for UTAC logistic membranes.

This script fans out simulations from :mod:`simulation.safety_delay_field`
to map how the adaptive controller stretches the window between the
logistic breaking point (\(\tau_{\text{break}}\)) and the actual escape
(\(\tau_{\text{escape}}\)). Each run preserves the quartet
\((R, \Theta, \beta, \zeta(R))\), contrasts \(\sigma(\beta(R-\Theta))\)
against smooth null models, and exports ΔAIC diagnostics for the
Metaquest bridge.

Usage
-----
.. code-block:: bash

    python -m analysis.safety_delay_sweep --control-strengths 0.25 0.4 \
        --drift-rates 0.008 0.012 --beta-gains 0.9 1.2 \
        --output analysis/results/safety_delay_sweep_custom.json

The default invocation produces a timestamped JSON artefact inside
``analysis/results/`` so the Tri-Layer indices can surface the newest
Safety-Delay evidence.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import numpy as np

from simulation.safety_delay_field import (
    SafetyDelayResult,
    logistic_response,
    meta_resonance_analysis,
    simulate_safety_delay_field,
)


# ---------------------------------------------------------------------------
# Configuration dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SweepConfig:
    """Configuration for the Safety-Delay parameter sweep."""

    t_max: float = 120.0
    dt: float = 0.05
    mu0: float = 0.9
    theta: float = 0.0
    noise_std: float = 0.01
    initial_state: float | None = None
    base_seed: int = 1337
    replicates: int = 1
    control_strengths: Sequence[float] = (0.25, 0.35, 0.45)
    drift_rates: Sequence[float] = (0.008, 0.010, 0.012)
    beta_gains: Sequence[float] = (0.8, 1.0, 1.2)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _ensure_positive(value: float, floor: float = 1e-12) -> float:
    return float(value if value > floor else floor)


def _aic_from_rss(rss: float, n: int, k: int) -> float:
    rss = _ensure_positive(rss)
    return float(n * np.log(rss / max(n, 1)) + 2 * k)


def _linear_null_fit(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, float]:
    coeffs = np.polyfit(x, y, deg=1)
    fitted = np.polyval(coeffs, x)
    rss = float(np.sum((y - fitted) ** 2))
    return fitted, rss


def _constant_null_fit(y: np.ndarray) -> Tuple[np.ndarray, float]:
    mean_val = float(np.mean(y))
    fitted = np.full_like(y, mean_val)
    rss = float(np.sum((y - fitted) ** 2))
    return fitted, rss


def _build_adjacency(control_strength: float, beta_gain: float) -> np.ndarray:
    weight = float(max(control_strength, 1e-3))
    modulation = float(beta_gain)
    adjacency = np.array(
        [
            [0.0, weight, 0.5 * modulation * weight],
            [weight, 0.0, modulation * weight],
            [0.5 * modulation * weight, modulation * weight, 0.0],
        ]
    )
    return adjacency


def _summarise_runs(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not runs:
        return {
            "count": 0,
            "tau_delay_mean": float("nan"),
            "tau_delay_median": float("nan"),
            "delta_aic_linear_min": float("nan"),
            "delta_aic_linear_median": float("nan"),
            "r_squared_mean": float("nan"),
            "control_energy_mean": float("nan"),
            "resonance_signal_mean": float("nan"),
            "delta_aic_linear_gt10_ratio": float("nan"),
            "theta_mean": float("nan"),
            "theta_ci95": None,
            "beta_mean": float("nan"),
            "beta_ci95": None,
            "r_squared_ci95": None,
            "delta_aic_constant_median": float("nan"),
            "delta_r2_linear_median": float("nan"),
            "delta_r2_constant_median": float("nan"),
            "logistic_aic_median": float("nan"),
            "logistic_rss_median": float("nan"),
            "null_comparisons": {},
            "best_null_model": None,
            "delta_aic_best_null": float("nan"),
            "delta_r2_best_null": float("nan"),
        }

    def _collect(name: str) -> np.ndarray:
        values = [run[name] for run in runs if not np.isnan(run.get(name, np.nan))]
        return np.asarray(values, dtype=float)

    def _nan_stat(arr: np.ndarray, fn) -> float:
        return float(fn(arr)) if arr.size else float("nan")

    def _ci95(arr: np.ndarray) -> List[float] | None:
        if not arr.size:
            return None
        lower, upper = np.nanpercentile(arr, [2.5, 97.5])
        return [float(lower), float(upper)]

    tau_delay = _collect("tau_delay")
    delta_linear = _collect("delta_aic_linear")
    delta_constant = _collect("delta_aic_constant")
    r_squared = _collect("r_squared")
    control_energy = _collect("control_energy")
    resonance_signal = _collect("meta_resonance_combined")
    theta_values = _collect("theta_hat")
    beta_values = _collect("beta_hat")
    delta_r2_linear = _collect("delta_r2_linear")
    delta_r2_constant = _collect("delta_r2_constant")
    logistic_aic = _collect("aic_logistic")
    logistic_rss = _collect("rss_logistic")

    null_comparisons = {
        "linear": {
            "delta_aic": _nan_stat(delta_linear, np.nanmedian),
            "delta_r2": _nan_stat(delta_r2_linear, np.nanmedian),
        },
        "constant": {
            "delta_aic": _nan_stat(delta_constant, np.nanmedian),
            "delta_r2": _nan_stat(delta_r2_constant, np.nanmedian),
        },
    }

    finite_comparisons = {
        name: metrics
        for name, metrics in null_comparisons.items()
        if np.isfinite(metrics["delta_aic"])
    }
    if finite_comparisons:
        best_null_name, best_metrics = max(
            finite_comparisons.items(), key=lambda item: item[1]["delta_aic"]
        )
        best_delta_aic = best_metrics["delta_aic"]
        best_delta_r2 = best_metrics["delta_r2"]
    else:
        best_null_name = None
        best_delta_aic = float("nan")
        best_delta_r2 = float("nan")

    return {
        "count": len(runs),
        "tau_delay_mean": _nan_stat(tau_delay, np.nanmean),
        "tau_delay_median": _nan_stat(tau_delay, np.nanmedian),
        "delta_aic_linear_min": _nan_stat(delta_linear, np.nanmin),
        "delta_aic_linear_median": _nan_stat(delta_linear, np.nanmedian),
        "r_squared_mean": _nan_stat(r_squared, np.nanmean),
        "control_energy_mean": _nan_stat(control_energy, np.nanmean),
        "resonance_signal_mean": _nan_stat(resonance_signal, np.nanmean),
        "delta_aic_linear_gt10_ratio": (
            float(np.mean(delta_linear > 10.0)) if delta_linear.size else float("nan")
        ),
        "theta_mean": _nan_stat(theta_values, np.nanmean),
        "theta_ci95": _ci95(theta_values),
        "beta_mean": _nan_stat(beta_values, np.nanmean),
        "beta_ci95": _ci95(beta_values),
        "r_squared_ci95": _ci95(r_squared),
        "delta_aic_constant_median": _nan_stat(delta_constant, np.nanmedian),
        "delta_r2_linear_median": _nan_stat(delta_r2_linear, np.nanmedian),
        "delta_r2_constant_median": _nan_stat(delta_r2_constant, np.nanmedian),
        "logistic_aic_median": _nan_stat(logistic_aic, np.nanmedian),
        "logistic_rss_median": _nan_stat(logistic_rss, np.nanmedian),
        "null_comparisons": null_comparisons,
        "best_null_model": best_null_name,
        "delta_aic_best_null": best_delta_aic,
        "delta_r2_best_null": best_delta_r2,
    }


# ---------------------------------------------------------------------------
# Core sweep logic
# ---------------------------------------------------------------------------


def _run_single(
    control_strength: float,
    drift_rate: float,
    beta_gain: float,
    config: SweepConfig,
    seed: int,
    replicate_index: int,
) -> Dict[str, Any]:
    rng = np.random.default_rng(seed)
    result: SafetyDelayResult = simulate_safety_delay_field(
        t_max=config.t_max,
        dt=config.dt,
        mu0=config.mu0,
        drift_rate=drift_rate,
        control_strength=control_strength,
        beta_gain=beta_gain,
        theta=config.theta,
        noise_std=config.noise_std,
        initial_state=config.initial_state,
        random_state=rng,
    )

    n = result.field_response.size
    logistic_fit = logistic_response(
        result.control_parameter, result.beta_hat, result.theta_hat
    )
    rss_logistic = float(np.sum((result.field_response - logistic_fit) ** 2))
    aic_logistic = _aic_from_rss(rss_logistic, n=n, k=2)

    _, rss_linear = _linear_null_fit(result.control_parameter, result.field_response)
    aic_linear = _aic_from_rss(rss_linear, n=n, k=2)

    _, rss_constant = _constant_null_fit(result.field_response)
    aic_constant = _aic_from_rss(rss_constant, n=n, k=1)

    mean_response = float(np.mean(result.field_response))
    ss_tot = float(np.sum((result.field_response - mean_response) ** 2))
    if ss_tot > 0:
        r2_linear = 1.0 - (rss_linear / ss_tot)
        r2_constant = 1.0 - (rss_constant / ss_tot)
    else:
        r2_linear = float("nan")
        r2_constant = float("nan")
    delta_r2_linear = (
        float(result.r_squared - r2_linear) if np.isfinite(r2_linear) else float("nan")
    )
    delta_r2_constant = (
        float(result.r_squared - r2_constant) if np.isfinite(r2_constant) else float("nan")
    )

    adjacency = _build_adjacency(control_strength, beta_gain)
    meta_diag = meta_resonance_analysis(adjacency, result.field_response)

    return {
        "control_strength": float(control_strength),
        "drift_rate": float(drift_rate),
        "beta_gain": float(beta_gain),
        "beta_hat": float(result.beta_hat),
        "theta_hat": float(result.theta_hat),
        "r_squared": float(result.r_squared),
        "tau_break": float(result.tau_break),
        "tau_delay": float(result.tau_delay),
        "control_energy": float(result.control_energy),
        "beta_shift": float(result.beta_shift),
        "aic_logistic": float(aic_logistic),
        "aic_linear": float(aic_linear),
        "aic_constant": float(aic_constant),
        "delta_aic_linear": float(aic_linear - aic_logistic),
        "delta_aic_constant": float(aic_constant - aic_logistic),
        "rss_logistic": float(rss_logistic),
        "rss_linear": float(rss_linear),
        "rss_constant": float(rss_constant),
        "ss_tot": float(ss_tot),
        "r2_linear": float(r2_linear),
        "r2_constant": float(r2_constant),
        "delta_r2_linear": delta_r2_linear,
        "delta_r2_constant": delta_r2_constant,
        "meta_resonance_control_centrality": float(meta_diag["control_centrality"]),
        "meta_resonance_crep": float(meta_diag["crep_resonance"]),
        "meta_resonance_combined": float(meta_diag["combined_signal"]),
        "seed": int(seed),
        "replicate": int(replicate_index),
        "sigma_notation": "sigma(beta*(R-Theta))",
    }


def run_sweep(config: SweepConfig) -> Dict[str, Any]:
    runs: List[Dict[str, Any]] = []
    seed_offset = 0
    for c_strength in config.control_strengths:
        for drift in config.drift_rates:
            for beta_gain in config.beta_gains:
                for replicate_index in range(max(config.replicates, 1)):
                    seed = int(config.base_seed + seed_offset)
                    run = _run_single(
                        c_strength,
                        drift,
                        beta_gain,
                        config,
                        seed,
                        replicate_index,
                    )
                    runs.append(run)
                    seed_offset += 1

    summary = _summarise_runs(runs)
    timestamp = datetime.now(timezone.utc).isoformat()

    def _clean_float(value: Any) -> Any:
        if isinstance(value, float) and not np.isfinite(value):
            return None
        return value

    comparisons_payload = {
        name: {metric: _clean_float(val) for metric, val in metrics.items()}
        for name, metrics in summary["null_comparisons"].items()
    }

    theta_estimate = {
        "value": _clean_float(summary["theta_mean"]),
        "ci95": summary["theta_ci95"],
    }
    beta_estimate = {
        "value": _clean_float(summary["beta_mean"]),
        "ci95": summary["beta_ci95"],
    }

    logistic_model_meta = {
        "parameters": 2,
        "description": "σ(β(R-Θ)) fit using non-linear least squares",
        "r2": _clean_float(summary["r_squared_mean"]),
        "r2_ci95": summary["r_squared_ci95"],
        "aic_median": _clean_float(summary["logistic_aic_median"]),
        "rss_median": _clean_float(summary["logistic_rss_median"]),
    }

    aggregate_block = {
        "theta": _clean_float(summary["theta_mean"]),
        "theta_ci95": summary["theta_ci95"],
        "beta": _clean_float(summary["beta_mean"]),
        "beta_ci95": summary["beta_ci95"],
        "r2": _clean_float(summary["r_squared_mean"]),
        "r2_ci95": summary["r_squared_ci95"],
        "null_models": comparisons_payload,
    }

    falsification_block = {
        "logistic_beats_all_nulls": all(
            (val.get("delta_aic") or 0.0) > 0 for val in comparisons_payload.values()
        ),
        "comparisons": comparisons_payload,
        "best_null_model": summary["best_null_model"],
        "best_delta_aic": _clean_float(summary["delta_aic_best_null"]),
        "best_delta_r2": _clean_float(summary["delta_r2_best_null"]),
    }

    payload: Dict[str, Any] = {
        "metadata": {
            "generated_at": timestamp,
            "module": "analysis.safety_delay_sweep",
            "description": (
                "Safety-Delay τ* sweep for UTAC σ(β(R-Θ)) controller with ΔAIC"
                " diagnostics against linear and constant null models."
            ),
            "theta": config.theta,
            "noise_std": config.noise_std,
        },
        "config": {
            **asdict(config),
            "control_strengths": [float(x) for x in config.control_strengths],
            "drift_rates": [float(x) for x in config.drift_rates],
            "beta_gains": [float(x) for x in config.beta_gains],
        },
        "summary": summary,
        "theta_estimate": theta_estimate,
        "beta_estimate": beta_estimate,
        "runs": runs,
        "null_models": {
            "linear": {
                "parameters": 2,
                "description": "Linear regression of field response on R",
            },
            "constant": {
                "parameters": 1,
                "description": "Constant mean response",
            },
        },
        "logistic_model": logistic_model_meta,
        "aggregate": aggregate_block,
        "falsification": falsification_block,
    }
    return payload


# ---------------------------------------------------------------------------
# CLI interface
# ---------------------------------------------------------------------------


def _parse_float_list(values: Iterable[str] | None, default: Sequence[float]) -> List[float]:
    if values is None:
        return [float(v) for v in default]
    return [float(v) for v in values]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Safety-Delay τ* sweeps and export ΔAIC diagnostics."
    )
    parser.add_argument(
        "--control-strengths",
        nargs="*",
        type=float,
        default=None,
        help="Control amplitudes applied to μ(t). Default: 0.25 0.35 0.45",
    )
    parser.add_argument(
        "--drift-rates",
        nargs="*",
        type=float,
        default=None,
        help="Drift rates that push R toward Θ. Default: 0.008 0.01 0.012",
    )
    parser.add_argument(
        "--beta-gains",
        nargs="*",
        type=float,
        default=None,
        help="Multipliers for β dynamics. Default: 0.8 1.0 1.2",
    )
    parser.add_argument(
        "--theta",
        type=float,
        default=0.0,
        help="Threshold Θ used in σ(β(R-Θ)).",
    )
    parser.add_argument(
        "--noise-std",
        type=float,
        default=0.01,
        help="Standard deviation of stochastic forcing in the state dynamics.",
    )
    parser.add_argument(
        "--t-max",
        type=float,
        default=120.0,
        help="Maximum simulation time horizon.",
    )
    parser.add_argument(
        "--dt",
        type=float,
        default=0.05,
        help="Integration step size for Euler-Maruyama integration.",
    )
    parser.add_argument(
        "--mu0",
        type=float,
        default=0.9,
        help="Initial distance to the bifurcation (μ₀).",
    )
    parser.add_argument(
        "--base-seed",
        type=int,
        default=1337,
        help="Base random seed; each run increments this offset.",
    )
    parser.add_argument(
        "--replicates",
        type=int,
        default=1,
        help="Number of stochastic replicates per parameter combination.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path for the JSON export. Defaults to analysis/results/ with timestamp.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> Path:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    config = SweepConfig(
        t_max=args.t_max,
        dt=args.dt,
        mu0=args.mu0,
        theta=args.theta,
        noise_std=args.noise_std,
        base_seed=args.base_seed,
        replicates=max(1, int(args.replicates)),
        control_strengths=_parse_float_list(args.control_strengths, SweepConfig.control_strengths),
        drift_rates=_parse_float_list(args.drift_rates, SweepConfig.drift_rates),
        beta_gains=_parse_float_list(args.beta_gains, SweepConfig.beta_gains),
    )

    payload = run_sweep(config)

    if args.output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_path = Path("analysis/results") / f"safety_delay_sweep_{stamp}.json"
    else:
        output_path = args.output

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)

    return output_path


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    path = main()
    print(path)
