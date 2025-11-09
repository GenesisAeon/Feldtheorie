from pathlib import Path

import numpy as np

from analysis.threshold_dataset_loader import (
    evaluate_logistic_fit,
    guard_delta_aic,
    load_dataset,
    load_metadata,
)


def test_load_metadata_and_simulated_fit():
    metadata_path = Path("data/climate/urban_heat_intensity.metadata.json")
    metadata = load_metadata(metadata_path)

    frame, origin = load_dataset(metadata, simulate_missing=True, seed=42)
    assert origin in {"observed", "simulated"}
    assert metadata.control_column in frame.columns
    assert metadata.response_column in frame.columns
    if origin == "simulated":
        assert len(frame) == metadata.simulation_hint.n_points
    else:
        assert len(frame) > 0

    result = evaluate_logistic_fit("utac-test", metadata, frame, origin)
    assert guard_delta_aic(result, minimum=5.0)
    assert np.isfinite(result.beta)
    assert abs(result.beta - metadata.beta) < 1.5
    assert abs(result.theta - metadata.theta) < 1.0
