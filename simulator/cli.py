"""Command-line interface for UTAC simulator logistics.

This CLI bridges the Safety-Delay field controller into the Sigillin-Netz
workflow. It orchestrates σ(β(R-Θ)) sweeps, records ΔAIC against smooth
null models, and exports resonance diagnostics into the `data/safety_delay/`
ledger so simulator presets and manuscripts can cite the same membrane pulse.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from analysis.safety_delay_sweep import SweepConfig, run_sweep


def _parse_float_list(values: Iterable[str] | None, default: Sequence[float]) -> List[float]:
    if values is None:
        return [float(v) for v in default]
    return [float(v) for v in values]


def _nanmean(values: Iterable[float]) -> float:
    clean = [float(v) for v in values if v is not None and not (isinstance(v, float) and v != v)]
    if not clean:
        return float("nan")
    return float(sum(clean) / len(clean))


def _write_csv(path: Path, runs: List[Dict[str, float]]) -> None:
    fieldnames = [
        "control_strength",
        "drift_rate",
        "beta_gain",
        "replicate",
        "seed",
        "beta_hat",
        "theta_hat",
        "r_squared",
        "tau_break",
        "tau_delay",
        "control_energy",
        "beta_shift",
        "delta_aic_linear",
        "delta_aic_constant",
        "meta_resonance_control_centrality",
        "meta_resonance_crep",
        "meta_resonance_combined",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for run in runs:
            row = {name: run.get(name, "") for name in fieldnames}
            writer.writerow(row)


def _build_metadata(
    dataset_path: Path,
    summary_path: Path,
    config: SweepConfig,
    runs: List[Dict[str, float]],
    summary: Dict[str, float],
    timestamp: str,
) -> Dict[str, object]:
    beta_values = [run.get("beta_hat") for run in runs]
    theta_values = [run.get("theta_hat") for run in runs]
    mean_beta = _nanmean(beta_values)
    mean_theta = _nanmean(theta_values)

    return {
        "title": "Safety-Delay ΔAIC ledger",
        "path": str(dataset_path.as_posix()),
        "category": "simulation-derived",
        "source": "simulation.safety_delay_field / simulator.cli",
        "description": (
            "ΔAIC sweep for the UTAC safety-delay controller. Each row captures σ(β(R-Θ)) "
            "fits, logistic vs null falsification, and resonance diagnostics."
        ),
        "threshold_parameters": {
            "R": "μ(t) control parameter",
            "Theta": mean_theta if mean_theta == mean_theta else config.theta,
            "beta": mean_beta,
            "zeta_R": "Safety-delay impedance via control schedule",
        },
        "preprocessing": [
            "Parameter sweep via simulator.cli safety-delay",
            "ΔAIC computed against linear and constant null models",
        ],
        "null_models_tested": ["linear", "constant"],
        "temporal": {
            "created": timestamp,
            "modified": timestamp,
            "version": "1.0.0",
            "change_count": 0,
        },
        "summary_reference": str(summary_path.as_posix()),
        "config": {
            "theta": config.theta,
            "noise_std": config.noise_std,
            "mu0": config.mu0,
            "replicates": config.replicates,
            "control_strengths": [float(x) for x in config.control_strengths],
            "drift_rates": [float(x) for x in config.drift_rates],
            "beta_gains": [float(x) for x in config.beta_gains],
        },
        "resonance_summary": summary,
    }


def run_safety_delay_command(args: argparse.Namespace) -> Dict[str, Path | None]:
    config = SweepConfig(
        t_max=args.t_max,
        dt=args.dt,
        mu0=args.mu0,
        theta=args.theta,
        noise_std=args.noise_std,
        initial_state=None,
        base_seed=args.base_seed,
        replicates=max(1, args.replicates),
        control_strengths=_parse_float_list(args.control_strengths, SweepConfig.control_strengths),
        drift_rates=_parse_float_list(args.drift_rates, SweepConfig.drift_rates),
        beta_gains=_parse_float_list(args.beta_gains, SweepConfig.beta_gains),
    )

    payload = run_sweep(config)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    dataset_path = data_dir / f"safety_delay_delta_aic_{stamp}.csv"
    summary_path = data_dir / f"safety_delay_delta_aic_{stamp}_summary.json"
    metadata_path = data_dir / f"safety_delay_delta_aic_{stamp}.metadata.json"

    _write_csv(dataset_path, payload["runs"])

    summary_payload = {
        "generated_at": stamp,
        "sigma_notation": "sigma(beta*(R-Theta))",
        "description": "Safety-delay resonance export for simulator pipelines",
        "config": {
            **asdict(config),
            "control_strengths": [float(x) for x in config.control_strengths],
            "drift_rates": [float(x) for x in config.drift_rates],
            "beta_gains": [float(x) for x in config.beta_gains],
        },
        "summary": payload["summary"],
        "logistic_model": payload["logistic_model"],
        "null_models": payload["null_models"],
    }

    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary_payload, handle, indent=2, ensure_ascii=False)

    metadata = _build_metadata(dataset_path, summary_path, config, payload["runs"], payload["summary"], stamp)
    with metadata_path.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, ensure_ascii=False)

    analysis_path: Path | None = None
    if args.emit_analysis:
        if args.analysis_output is None:
            analysis_path = Path("analysis/results") / f"safety_delay_sweep_{stamp}.json"
        else:
            analysis_path = Path(args.analysis_output)
        analysis_path.parent.mkdir(parents=True, exist_ok=True)
        with analysis_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)

    return {
        "dataset": dataset_path,
        "summary": summary_path,
        "metadata": metadata_path,
        "analysis": analysis_path,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "UTAC simulator CLI for safety-delay σ(β(R-Θ)) sweeps "
            "and ΔAIC resonance logging."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    safety_delay = subparsers.add_parser(
        "safety-delay",
        help="Run safety-delay τ* sweeps and export Sigillin-ready datasets.",
    )
    safety_delay.add_argument("--control-strengths", nargs="*", type=float, default=None)
    safety_delay.add_argument("--drift-rates", nargs="*", type=float, default=None)
    safety_delay.add_argument("--beta-gains", nargs="*", type=float, default=None)
    safety_delay.add_argument("--theta", type=float, default=0.0)
    safety_delay.add_argument("--noise-std", type=float, default=0.01)
    safety_delay.add_argument("--t-max", type=float, default=120.0)
    safety_delay.add_argument("--dt", type=float, default=0.05)
    safety_delay.add_argument("--mu0", type=float, default=0.9)
    safety_delay.add_argument("--base-seed", type=int, default=1337)
    safety_delay.add_argument("--replicates", type=int, default=1)
    safety_delay.add_argument(
        "--data-dir",
        type=str,
        default="data/safety_delay",
        help="Destination directory for ΔAIC ledger outputs.",
    )
    safety_delay.add_argument(
        "--emit-analysis",
        action="store_true",
        help="Also emit full sweep payload into analysis/results.",
    )
    safety_delay.add_argument(
        "--analysis-output",
        type=str,
        default=None,
        help="Optional override path for the analysis JSON export.",
    )
    safety_delay.set_defaults(func=run_safety_delay_command)

    return parser


def main(argv: Sequence[str] | None = None) -> Dict[str, Path | None]:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.error("No command provided. Use 'safety-delay'.")

    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    paths = main()
    for label, path in paths.items():
        if path is not None:
            print(f"{label}: {path}")
