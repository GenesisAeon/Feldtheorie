from __future__ import annotations

import json

from analysis.xai_scaling_pilot import run_scaling_validation


def test_scaling_pilot_runs_all_parameter_pairs_and_persists(tmp_path) -> None:
    datasets = [
        {"dataset_id": "d1", "domain": "ai", "dimension": 0},
        {"dataset_id": "d2", "domain": "climate", "dimension": 2},
    ]
    betas = [4.2, 8.0]
    sigmas = [0.055, 0.0625, 0.07]
    output_path = tmp_path / "scaling_results.json"

    results = run_scaling_validation(
        datasets=datasets,
        beta_values=betas,
        sigma_phi_values=sigmas,
        output_path=output_path,
        max_workers=2,
    )

    assert len(results) == len(datasets) * len(betas) * len(sigmas)
    assert output_path.exists()

    persisted = json.loads(output_path.read_text(encoding="utf-8"))
    assert persisted["summary"]["num_runs"] == len(results)
    assert len(persisted["results"]) == len(results)
