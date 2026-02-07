from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping

from theory.afet import AFETFramework


def _default_evaluator(dataset: Mapping[str, object], beta: float, sigma_phi: float) -> dict[str, float | str]:
    framework = AFETFramework()
    dim = float(dataset.get("dimension", 0.0))
    predicted_beta = framework.predict_beta(dim)
    beta_error = abs(float(beta) - predicted_beta)
    sigma_error = abs(float(sigma_phi) - framework.constants.SIGMA_PHI)
    score = max(0.0, 1.0 - 0.02 * beta_error - 4.0 * sigma_error)
    return {
        "predicted_beta": predicted_beta,
        "beta_error": beta_error,
        "sigma_error": sigma_error,
        "fit_score": score,
    }


def run_scaling_validation(
    datasets: list[Mapping[str, object]],
    beta_values: list[float],
    sigma_phi_values: list[float],
    output_path: str | Path | None = None,
    max_workers: int = 1,
    evaluator: Callable[[Mapping[str, object], float, float], Mapping[str, object]] | None = None,
) -> list[dict[str, object]]:
    """Run AFET scaling sweeps over (dataset, β, σ_Φ) combinations."""
    eval_fn = evaluator or _default_evaluator
    tasks = [
        (dataset, float(beta), float(sigma_phi))
        for dataset in datasets
        for beta in beta_values
        for sigma_phi in sigma_phi_values
    ]

    def _run_single(task: tuple[Mapping[str, object], float, float]) -> dict[str, object]:
        dataset, beta, sigma_phi = task
        metrics = dict(eval_fn(dataset, beta, sigma_phi))
        return {
            "dataset_id": dataset.get("dataset_id", "unknown"),
            "domain": dataset.get("domain", "unknown"),
            "dimension": float(dataset.get("dimension", 0.0)),
            "beta": beta,
            "sigma_phi": sigma_phi,
            "metrics": metrics,
        }

    if max_workers > 1:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(_run_single, tasks))
    else:
        results = [_run_single(task) for task in tasks]

    if output_path is not None:
        output = {
            "created_at": datetime.now(tz=timezone.utc).isoformat(),
            "summary": {
                "num_runs": len(results),
                "num_datasets": len(datasets),
                "num_beta": len(beta_values),
                "num_sigma_phi": len(sigma_phi_values),
            },
            "results": results,
        }
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    return results
