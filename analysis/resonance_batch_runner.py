r"""Batch orchestration for UTF resonance fits with tri-layer cadence.

Formal layer:
    Automates multiple invocations of the logistic resonance pipeline by reading a
    JSON configuration that specifies the threshold quartet parameters \((R, \Theta,
    \beta, \zeta(R))\).  Each run may simulate a membrane via
    :func:`analysis.resonance_fit_pipeline.simulate_series` or ingest recorded
    measurements before refitting \(\sigma(\beta(R-\Theta))\), benchmarking the
    logistic curve against smooth null models, and exporting structured summaries.

Empirical layer:
    Provides a CLI that batches analyses for reproducibility audits.  The runner
    accepts configuration defaults, writes summaries to per-run destinations, and
    echoes compact console diagnostics (\(R^2\), \(\Delta\mathrm{AIC}\)) so
    collaborators can stage cohort updates without hand-triggering each script.

Metaphorical layer:
    Conducts a caravan of dawn choruses—each run is a lantern lighting when the
    membrane consents to resonance.  By braiding simulations and archival data in
    one cadence, the batch runner keeps the threshold field humming across domains.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.resonance_fit_pipeline import (  # noqa: E402
    assemble_summary,
    evaluate_null_model,
    evaluate_power_law_null,
    export_summary,
    fit_threshold_parameters,
    logistic_response,
    simulate_series,
)


DEFAULT_CONFIG = ROOT / "analysis" / "batch_configs" / "resonance_runs.json"


class ConfigurationError(RuntimeError):
    """Raised when the batch configuration cannot be interpreted."""


def _as_float_list(values: Iterable[Any]) -> List[float]:
    """Convert *values* into a list of floats, skipping ``None`` entries."""

    floats: List[float] = []
    for value in values:
        if value is None:
            continue
        try:
            floats.append(float(value))
        except (TypeError, ValueError):
            raise ConfigurationError(f"Value {value!r} cannot be converted to float") from None
    return floats


def _load_json(path: Path) -> MutableMapping[str, Any]:
    """Load a JSON file and ensure the payload is mapping-like."""

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, MutableMapping):
        raise ConfigurationError(f"Configuration file {path} must contain a JSON object")
    return payload


def resolve_path(candidate: Path) -> Path:
    """Resolve *candidate* relative to the repository root when necessary."""

    if candidate.is_absolute():
        return candidate
    return (ROOT / candidate).resolve()


@dataclass
class BatchRun:
    """Configuration for a single batch execution."""

    identifier: str
    mode: str
    output: Path
    simulation_params: Mapping[str, Any]
    input_path: Optional[Path] = None
    metadata: Optional[Mapping[str, Any]] = None
    notes: Optional[Mapping[str, Any]] = None


def parse_configuration(path: Path) -> Tuple[Mapping[str, Any], List[BatchRun]]:
    """Parse the batch configuration at *path* into defaults and runs."""

    payload = _load_json(path)
    defaults = payload.get("defaults", {})
    if not isinstance(defaults, Mapping):
        raise ConfigurationError("defaults entry must be an object")
    default_mode = str(defaults.get("mode", "simulate")).lower()
    default_output_dir = defaults.get("output_dir", "analysis/batch_runs")
    default_output_dir_path = resolve_path(Path(str(default_output_dir)))

    simulation_defaults = defaults.get("simulation", {})
    if not isinstance(simulation_defaults, Mapping):
        raise ConfigurationError("defaults.simulation must be an object when provided")

    runs_payload = payload.get("runs")
    if not isinstance(runs_payload, list) or not runs_payload:
        raise ConfigurationError("Configuration must include a non-empty 'runs' array")

    runs: List[BatchRun] = []
    for entry in runs_payload:
        if not isinstance(entry, Mapping):
            raise ConfigurationError("Each run entry must be an object")
        identifier = entry.get("id") or entry.get("identifier")
        if not isinstance(identifier, str) or not identifier.strip():
            raise ConfigurationError("Run entries require a non-empty 'id'")
        mode = str(entry.get("mode", default_mode)).lower()
        if mode not in {"simulate", "ingest"}:
            raise ConfigurationError(f"Run {identifier!r} uses unsupported mode {mode!r}")

        output_value = entry.get("output")
        if output_value is None:
            output_path = default_output_dir_path / f"{identifier}.json"
        else:
            output_path = resolve_path(Path(str(output_value)))

        simulation_params: Dict[str, Any] = dict(simulation_defaults)
        entry_params = entry.get("params") or entry.get("simulation")
        if entry_params is not None:
            if not isinstance(entry_params, Mapping):
                raise ConfigurationError(f"Run {identifier!r} parameters must be an object")
            simulation_params.update(entry_params)

        input_value = entry.get("input") or entry.get("source")
        input_path = resolve_path(Path(str(input_value))) if input_value else None

        metadata = entry.get("metadata") or entry.get("dataset")
        if metadata is not None and not isinstance(metadata, Mapping):
            raise ConfigurationError(f"Run {identifier!r} metadata must be an object when provided")

        notes = entry.get("notes")
        if notes is not None and not isinstance(notes, Mapping):
            raise ConfigurationError(f"Run {identifier!r} notes must be an object when provided")

        runs.append(
            BatchRun(
                identifier=identifier,
                mode=mode,
                output=output_path,
                simulation_params=simulation_params,
                input_path=input_path,
                metadata=metadata,
                notes=notes,
            )
        )

    return defaults, runs


def _ingest_series(path: Path) -> Tuple[Dict[str, List[float]], Dict[str, Any]]:
    """Load measurement series suitable for fitting from *path*."""

    payload = _load_json(path)
    series: Dict[str, List[float]] = {}
    metadata: Dict[str, Any] = {}

    for key in (
        "R",
        "sigma",
        "driver",
        "zeta",
        "flux",
        "boundary_flux",
        "boundary_gate",
        "theta",
        "beta",
        "meaning",
        "semantic_coupling",
    ):
        value = payload.get(key)
        if isinstance(value, list):
            series[key] = _as_float_list(value)

    if "R" not in series or "sigma" not in series:
        dataset = payload.get("dataset")
        if isinstance(dataset, Mapping):
            metadata.setdefault("dataset", dataset)
            measurements = dataset.get("measurements")
            if isinstance(measurements, list):
                R_values: List[float] = []
                sigma_values: List[float] = []
                for item in measurements:
                    if not isinstance(item, Mapping):
                        continue
                    if "R" in item and "sigma" in item:
                        try:
                            R_values.append(float(item["R"]))
                            sigma_values.append(float(item["sigma"]))
                        except (TypeError, ValueError):
                            raise ConfigurationError(
                                f"Measurement {item!r} in {path} must expose numeric R and sigma"
                            ) from None
                if R_values and sigma_values:
                    series["R"] = R_values
                    series["sigma"] = sigma_values

    if "R" not in series or "sigma" not in series:
        raise ConfigurationError(
            f"File {path} lacks 'R'/'sigma' arrays or dataset.measurements for ingestion"
        )

    # Carry additional context forward for the summary if present.
    if "membrane" in payload and isinstance(payload["membrane"], Mapping):
        metadata.setdefault("membrane", payload["membrane"])
    if "falsification" in payload and isinstance(payload["falsification"], Mapping):
        metadata.setdefault("falsification", payload["falsification"])

    return series, metadata


def _sigma_fit(R: Iterable[float], theta: float, beta: float) -> List[float]:
    """Return the logistic fit values for *R* given ``theta`` and ``beta``."""

    return [float(logistic_response(value, theta, beta)) for value in R]


def execute_run(run: BatchRun, *, dry_run: bool, config_path: Path) -> Optional[Dict[str, Any]]:
    """Execute a configured batch run and return the summary when written."""

    if run.mode == "simulate":
        required = {"theta", "beta", "steps", "dt", "driver", "R0"}
        missing = [name for name in required if name not in run.simulation_params]
        if missing:
            raise ConfigurationError(
                f"Run {run.identifier!r} is missing required simulation parameters: {', '.join(missing)}"
            )
        results = simulate_series(
            theta=float(run.simulation_params["theta"]),
            beta=float(run.simulation_params["beta"]),
            steps=int(run.simulation_params["steps"]),
            dt=float(run.simulation_params["dt"]),
            driver=float(run.simulation_params["driver"]),
            R0=float(run.simulation_params["R0"]),
            resonant_gain=float(run.simulation_params.get("resonant_gain", 0.6)),
            damped_gain=float(run.simulation_params.get("damped_gain", 1.4)),
            switch_width=float(run.simulation_params.get("switch_width", 0.35)),
            dynamic_robin=bool(run.simulation_params.get("dynamic_robin", False)),
            beta_robin=float(run.simulation_params.get("beta_robin", 4.8)),
            boundary_logistic_weight=float(run.simulation_params.get("boundary_logistic_weight", 0.35)),
            boundary_driver_weight=float(run.simulation_params.get("boundary_driver_weight", 0.15)),
        )
        metadata: Dict[str, Any] = {}
    else:
        if run.input_path is None:
            raise ConfigurationError(f"Run {run.identifier!r} requires an input file in ingest mode")
        series, extra_metadata = _ingest_series(run.input_path)
        results = series
        metadata = dict(extra_metadata)

    fit_metrics = fit_threshold_parameters(results["R"], results["sigma"])
    results["sigma_fit"] = _sigma_fit(results["R"], fit_metrics["theta"], fit_metrics["beta"])

    null_metrics = {
        "linear": evaluate_null_model(results["R"], results["sigma"]),
        "power_law": evaluate_power_law_null(results["R"], results["sigma"]),
    }

    summary = assemble_summary(results, fit_metrics, null_metrics)

    dataset_block: Dict[str, Any] = {}
    if run.metadata:
        dataset_block.update(run.metadata)
    if metadata.get("dataset") and "dataset" not in dataset_block:
        dataset_block["dataset"] = metadata["dataset"]
    if dataset_block:
        summary.setdefault("dataset", dataset_block)

    if run.mode == "ingest":
        summary.setdefault("source", {})
        summary["source"].update({"mode": "ingest", "input": str(run.input_path)})
    else:
        summary.setdefault("source", {})
        summary["source"].update({
            "mode": "simulate",
            "simulation": {
                key: (float(value) if isinstance(value, (int, float)) else value)
                for key, value in run.simulation_params.items()
            },
        })

    summary.setdefault("source", {})
    summary["source"].update(
        {
            "batch_run_id": run.identifier,
            "config": str(config_path),
        }
    )

    if run.notes:
        summary.setdefault("notes", run.notes)

    delta_aic_linear = null_metrics["linear"].get("aic", float("nan")) - summary["logistic_model"]["aic"]
    delta_aic_power = null_metrics["power_law"].get("aic", float("nan")) - summary["logistic_model"]["aic"]
    print(
        f"[batch:{run.identifier}] mode={run.mode} R²={summary['logistic_model']['r2']:.6f} "
        f"ΔAIC(linear)={delta_aic_linear:.2f} ΔAIC(power)={delta_aic_power:.2f}"
    )

    if dry_run:
        print(f"  ↳ dry-run enabled; skipping write to {run.output}")
        return None

    run.output.parent.mkdir(parents=True, exist_ok=True)
    export_summary(summary, run.output)
    return summary


def parse_arguments(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Configure CLI arguments."""

    parser = argparse.ArgumentParser(
        description="Batch logistic resonance runs spanning simulations and ingests."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to the JSON batch configuration (default: analysis/batch_configs/resonance_runs.json).",
    )
    parser.add_argument(
        "--run",
        dest="run_ids",
        action="append",
        help="Execute only the specified run id (can be repeated).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available runs without executing them.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration and show diagnostics without writing outputs.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry point."""

    args = parse_arguments(argv)
    config_path = resolve_path(args.config)

    try:
        defaults, runs = parse_configuration(config_path)
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    if args.list:
        print("Available batch runs:")
        for run in runs:
            print(f"  • {run.identifier} (mode={run.mode}, output={run.output})")
        return 0

    selected_ids = set(args.run_ids) if args.run_ids else None
    for run in runs:
        if selected_ids and run.identifier not in selected_ids:
            continue
        try:
            execute_run(run, dry_run=args.dry_run, config_path=config_path)
        except ConfigurationError as exc:
            print(f"Run {run.identifier} failed: {exc}", file=sys.stderr)
            return 3

    if defaults.get("notes") and not args.dry_run:
        print("Batch defaults notes:")
        for key, value in defaults["notes"].items():
            print(f"  {key}: {value}")

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI execution
    raise SystemExit(main())
