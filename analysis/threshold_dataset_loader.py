r"""Shared loaders for UTAC threshold datasets and logistic fits.

Formal stratum:
    Parses metadata scrolls so that every dataset entering the analysis bay
    declares its logistic response \(\sigma(\beta(R-\Theta))\), impedance notes
    \(\zeta(R)\), and falsification guards.  Provides helpers that feed raw or
    simulated samples into the canonical fitting pipeline.

Empirical stratum:
    Normalises paths, hydrates CSV/NetCDF payloads, and when data are pending
    generates synthetic rehearsals from the annotated \(\Theta\) and \(\beta\)
    estimates.  The loaders return tidy `pandas.DataFrame` objects ready for
    `resonance_fit_pipeline` comparisons against linear and power-law nulls.

Metaphorical stratum:
    Ensures every staging lantern still hums.  Even when the raw field samples
    are en route, these utilities let the membrane breathe simulated dawn light
    so codex entries, manifests, and tests keep resonance with the plan.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from .resonance_fit_pipeline import (
    evaluate_null_model,
    evaluate_power_law_null,
    fit_threshold_parameters,
)
from models.membrane_solver import logistic_response


@dataclass
class SimulationHint:
    """Describe how to synthesise a surrogate dataset when raw files are pending."""

    control_min: float
    control_max: float
    n_points: int
    noise_scale: float


@dataclass
class DatasetMetadata:
    """Structured view over a dataset's tri-layer metadata scroll."""

    dataset_name: str
    domain: str
    path: Path
    status: str
    description: str
    control_column: str
    response_column: str
    data_format: str
    theta: Optional[float]
    beta: Optional[float]
    zeta_notes: Optional[str]
    delta_aic_guard: Optional[float]
    null_models: List[str]
    preprocessing_steps: List[str]
    provenance: Dict[str, Any]
    temporal: Dict[str, Any]
    simulation_hint: Optional[SimulationHint]
    metadata_path: Path


@dataclass
class FitResult:
    """Logistic fit diagnostics aligned with manifest expectations."""

    dataset_id: str
    dataset_name: str
    domain: str
    status: str
    metadata_path: Path
    data_path: Path
    data_origin: str
    control_column: str
    response_column: str
    theta: float
    theta_ci: Tuple[float, float]
    beta: float
    beta_ci: Tuple[float, float]
    r_squared: float
    aic: float
    delta_aic_best: float
    null_models: Dict[str, Dict[str, Any]]
    sample_size: int

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "dataset_id": self.dataset_id,
            "dataset_name": self.dataset_name,
            "domain": self.domain,
            "status": self.status,
            "metadata_path": str(self.metadata_path),
            "data_path": str(self.data_path),
            "data_origin": self.data_origin,
            "control_column": self.control_column,
            "response_column": self.response_column,
            "theta": self.theta,
            "theta_ci": list(self.theta_ci),
            "beta": self.beta,
            "beta_ci": list(self.beta_ci),
            "r_squared": self.r_squared,
            "aic": self.aic,
            "delta_aic_best": self.delta_aic_best,
            "null_models": self.null_models,
            "sample_size": self.sample_size,
        }
        return payload


def _normalise_null_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Cast numeric entries to floats while preserving descriptive fields."""

    normalised: Dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, (int, float)):
            normalised[key] = float(value)
            continue
        try:
            normalised[key] = float(value)
        except (TypeError, ValueError):
            normalised[key] = value
    return normalised


def _coerce_simulation_hint(raw: Optional[Dict[str, Any]]) -> Optional[SimulationHint]:
    if not raw:
        return None
    return SimulationHint(
        control_min=float(raw.get("control_min", 0.0)),
        control_max=float(raw.get("control_max", 1.0)),
        n_points=int(raw.get("n_points", 200)),
        noise_scale=float(raw.get("noise_scale", 0.01)),
    )


def load_metadata(metadata_path: Path) -> DatasetMetadata:
    """Parse a `.metadata.json` file into a structured dataclass."""

    with metadata_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    root = metadata_path.parents[1]
    dataset_path = Path(payload["path"]) if "path" in payload else None
    if dataset_path is None:
        raise ValueError(f"metadata at {metadata_path} lacks a 'path' entry")
    if not dataset_path.is_absolute():
        dataset_path = (root / dataset_path).resolve()

    simulation_hint = _coerce_simulation_hint(payload.get("simulation_hint"))

    return DatasetMetadata(
        dataset_name=payload["dataset_name"],
        domain=payload["domain"],
        path=dataset_path,
        status=payload.get("status", "staging"),
        description=payload.get("description", ""),
        control_column=payload["control_parameter_R"]["column"],
        response_column=payload["response_sigma"]["column"],
        data_format=payload.get("data_format", "csv"),
        theta=payload.get("threshold_estimates", {}).get("theta"),
        beta=payload.get("threshold_estimates", {}).get("beta"),
        zeta_notes=payload.get("threshold_estimates", {}).get("zeta_R"),
        delta_aic_guard=payload.get("threshold_estimates", {}).get("delta_aic_guard"),
        null_models=payload.get("null_models_tested", []),
        preprocessing_steps=payload.get("preprocessing_steps", []),
        provenance=payload.get("provenance", {}),
        temporal=payload.get("temporal", {}),
        simulation_hint=simulation_hint,
        metadata_path=metadata_path.resolve(),
    )


def load_dataset(
    metadata: DatasetMetadata,
    simulate_missing: bool = False,
    seed: Optional[int] = None,
) -> Tuple[pd.DataFrame, str]:
    """Load a dataset as a DataFrame, optionally simulating values if absent."""

    if metadata.path.exists():
        if metadata.data_format.lower() in {"csv", "tsv"}:
            frame = pd.read_csv(metadata.path)
        elif metadata.data_format.lower() in {"netcdf", "nc"}:
            try:
                import xarray as xr
            except ImportError as exc:  # pragma: no cover - import guard
                raise RuntimeError(
                    "xarray is required to read NetCDF datasets; install optional dependency"
                ) from exc
            dataset = xr.open_dataset(metadata.path)
            control_values = dataset[metadata.control_column].values.ravel()
            response_values = dataset[metadata.response_column].values.ravel()
            frame = pd.DataFrame(
                {
                    metadata.control_column: control_values,
                    metadata.response_column: response_values,
                }
            )
        else:
            raise ValueError(
                f"Unsupported data_format '{metadata.data_format}' in {metadata.metadata_path}"
            )
        frame = frame[[metadata.control_column, metadata.response_column]].dropna()
        return frame, "observed"

    if not simulate_missing:
        raise FileNotFoundError(
            f"Dataset {metadata.dataset_name} missing at {metadata.path}; rerun with simulate_missing=True"
        )

    if metadata.simulation_hint is None:
        raise ValueError(
            f"No simulation_hint provided in {metadata.metadata_path}, cannot synthesise placeholder"
        )

    rng = np.random.default_rng(seed)
    hint = metadata.simulation_hint
    span_min = hint.control_min
    span_max = hint.control_max
    if metadata.theta is not None and metadata.beta not in (None, 0):
        span_left = max(metadata.theta - hint.control_min, 0.0)
        span_right = max(hint.control_max - metadata.theta, 0.0)
        if span_left > 0 and span_right > 0:
            logistic_window = 6.0 / abs(metadata.beta)
            effective_half_range = min(span_left, span_right, logistic_window)
            span_min = max(metadata.theta - effective_half_range, hint.control_min)
            span_max = min(metadata.theta + effective_half_range, hint.control_max)

    control_values = np.linspace(span_min, span_max, hint.n_points)

    theta = metadata.theta if metadata.theta is not None else np.median(control_values)
    beta = metadata.beta if metadata.beta is not None else 4.2

    logistic_values = np.array(
        [logistic_response(value, theta, beta) for value in control_values],
        dtype=float,
    )
    logistic_values = np.clip(logistic_values, 1e-12, 1.0 - 1e-12)

    if hint.noise_scale > 0:
        logits = np.log(logistic_values / (1.0 - logistic_values))
        jitter = rng.normal(loc=0.0, scale=hint.noise_scale, size=len(control_values))
        sigma_values = 1.0 / (1.0 + np.exp(-(logits + jitter)))
    else:
        sigma_values = logistic_values

    frame = pd.DataFrame(
        {
            metadata.control_column: control_values,
            metadata.response_column: sigma_values,
        }
    )
    return frame, "simulated"


def evaluate_logistic_fit(
    dataset_id: str,
    metadata: DatasetMetadata,
    frame: pd.DataFrame,
    data_origin: str,
) -> FitResult:
    """Run the canonical logistic fit and null comparisons."""

    control = frame[metadata.control_column].astype(float).to_numpy()
    response = frame[metadata.response_column].astype(float).to_numpy()

    metrics = fit_threshold_parameters(control, response)
    linear_null = evaluate_null_model(control, response)
    power_null = evaluate_power_law_null(control, response)

    null_models_raw = {
        "linear": linear_null,
        "power_law": power_null,
    }

    best_null_aic = min(
        value.get("aic", float("inf")) for value in null_models_raw.values()
    )
    delta_aic_best = best_null_aic - metrics.get("aic", float("nan"))

    return FitResult(
        dataset_id=dataset_id,
        dataset_name=metadata.dataset_name,
        domain=metadata.domain,
        status=metadata.status,
        metadata_path=metadata.metadata_path,
        data_path=metadata.path,
        data_origin=data_origin,
        control_column=metadata.control_column,
        response_column=metadata.response_column,
        theta=float(metrics["theta"]),
        theta_ci=(float(metrics["theta_ci_lower"]), float(metrics["theta_ci_upper"])),
        beta=float(metrics["beta"]),
        beta_ci=(float(metrics["beta_ci_lower"]), float(metrics["beta_ci_upper"])),
        r_squared=float(metrics["r2"]),
        aic=float(metrics["aic"]),
        delta_aic_best=float(delta_aic_best),
        null_models={key: _normalise_null_payload(value) for key, value in null_models_raw.items()},
        sample_size=len(frame),
    )


def guard_delta_aic(result: FitResult, minimum: float = 10.0) -> bool:
    """Return True when the fit clears the ΔAIC guardrail."""

    if np.isnan(result.delta_aic_best):
        return False
    return result.delta_aic_best >= minimum


def describe_result(result: FitResult) -> str:
    """Craft a concise textual summary for logs or reports."""

    origin = "observed" if result.data_origin == "observed" else "simulated"
    return (
        f"{result.dataset_id} | {result.dataset_name} | β={result.beta:.2f} "
        f"Θ={result.theta:.2f} | ΔAIC={result.delta_aic_best:.2f} | origin={origin}"
    )


__all__ = [
    "DatasetMetadata",
    "SimulationHint",
    "FitResult",
    "describe_result",
    "evaluate_logistic_fit",
    "guard_delta_aic",
    "load_dataset",
    "load_metadata",
]
