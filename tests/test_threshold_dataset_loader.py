from pathlib import Path

import numpy as np
import pytest

from analysis.threshold_dataset_loader import (
    evaluate_logistic_fit,
    guard_delta_aic,
    load_dataset,
    load_metadata,
    _coerce_simulation_hint,
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


def test_coerce_simulation_hint_with_none():
    """_coerce_simulation_hint should return None when given None."""
    result = _coerce_simulation_hint(None)
    assert result is None


def test_coerce_simulation_hint_with_empty_dict():
    """_coerce_simulation_hint treats empty dict as None (falsy)."""
    result = _coerce_simulation_hint({})
    # Empty dict is falsy, so None is returned
    assert result is None


def test_coerce_simulation_hint_with_custom_values():
    """_coerce_simulation_hint should use provided values."""
    hint = _coerce_simulation_hint({
        "control_min": 0.2,
        "control_max": 0.8,
        "n_points": 50,
        "noise_scale": 0.05
    })
    assert hint.control_min == 0.2
    assert hint.control_max == 0.8
    assert hint.n_points == 50
    assert hint.noise_scale == 0.05


def test_load_dataset_raises_when_missing_and_no_simulate():
    """load_dataset should raise FileNotFoundError when file missing and simulate_missing=False."""
    metadata_path = Path("data/climate/urban_heat_intensity.metadata.json")
    metadata = load_metadata(metadata_path)

    # Temporarily change path to nonexistent file
    original_path = metadata.path
    metadata.path = Path("/nonexistent/file.csv")

    with pytest.raises(FileNotFoundError, match="simulate_missing=True"):
        load_dataset(metadata, simulate_missing=False)

    metadata.path = original_path


def test_guard_delta_aic_passes_when_above_minimum():
    """guard_delta_aic should return True when delta_aic >= minimum."""
    from analysis.threshold_dataset_loader import FitResult

    # Create a minimal FitResult with sufficient delta_aic
    result = FitResult(
        dataset_id="test",
        dataset_name="test",
        domain="test",
        status="pending",
        metadata_path=Path("dummy"),
        data_path=Path("dummy"),
        data_origin="simulated",
        control_column="R",
        response_column="sigma",
        theta=0.5,
        theta_ci=(0.4, 0.6),
        beta=4.0,
        beta_ci=(3.5, 4.5),
        r_squared=0.95,
        aic=100.0,
        delta_aic_best=10.0,  # Above threshold
        null_models={},
        sample_size=100
    )

    assert guard_delta_aic(result, minimum=5.0) is True


def test_guard_delta_aic_fails_when_below_minimum():
    """guard_delta_aic should return False when delta_aic < minimum."""
    from analysis.threshold_dataset_loader import FitResult

    result = FitResult(
        dataset_id="test",
        dataset_name="test",
        domain="test",
        status="pending",
        metadata_path=Path("dummy"),
        data_path=Path("dummy"),
        data_origin="simulated",
        control_column="R",
        response_column="sigma",
        theta=0.5,
        theta_ci=(0.4, 0.6),
        beta=4.0,
        beta_ci=(3.5, 4.5),
        r_squared=0.95,
        aic=100.0,
        delta_aic_best=2.0,  # Below threshold
        null_models={},
        sample_size=100
    )

    assert guard_delta_aic(result, minimum=5.0) is False
