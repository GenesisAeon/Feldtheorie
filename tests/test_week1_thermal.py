"""Tests for experiments.week1.thermal — HfO2 thermal simulation."""

from __future__ import annotations

import json

import pytest
from experiments.week1.thermal import (
    NOMINAL_SIGMA_PHI,
    NOMINAL_TEMP_C,
    THERMAL_COEFF,
    ThermalSample,
    classify_temperature,
    find_boundary_temperature,
    run_thermal_simulation,
    sigma_phi_at_temperature,
    sweep_temperatures,
)

# ---------------------------------------------------------------------------
# sigma_phi_at_temperature
# ---------------------------------------------------------------------------


def test_nominal_temperature_returns_nominal_sigma() -> None:
    assert sigma_phi_at_temperature(NOMINAL_TEMP_C) == pytest.approx(NOMINAL_SIGMA_PHI)


def test_higher_temperature_lowers_sigma_phi() -> None:
    hot = sigma_phi_at_temperature(60.0)
    assert hot < NOMINAL_SIGMA_PHI


def test_lower_temperature_raises_sigma_phi() -> None:
    cold = sigma_phi_at_temperature(0.0)
    assert cold > NOMINAL_SIGMA_PHI


def test_sigma_phi_never_negative() -> None:
    """Even at absurd temperatures, sigma_Phi is clamped to >= 0."""
    assert sigma_phi_at_temperature(500.0) == 0.0


def test_thermal_linearity() -> None:
    """Verify the linear model: delta_sigma = coeff * delta_T."""
    t1, t2 = 30.0, 50.0
    s1, s2 = sigma_phi_at_temperature(t1), sigma_phi_at_temperature(t2)
    expected_delta = THERMAL_COEFF * (t2 - t1)
    assert (s2 - s1) == pytest.approx(expected_delta)


# ---------------------------------------------------------------------------
# classify_temperature
# ---------------------------------------------------------------------------


def test_classify_nominal_is_stable() -> None:
    sample = classify_temperature(NOMINAL_TEMP_C)
    assert sample.safety_state == "stable"
    assert not sample.should_shutdown


def test_classify_high_temp_is_warning_or_critical() -> None:
    sample = classify_temperature(55.0)
    assert sample.safety_state in ("warning", "critical")


def test_classify_returns_thermal_sample() -> None:
    sample = classify_temperature(40.0)
    assert isinstance(sample, ThermalSample)
    assert sample.temperature_c == 40.0


# ---------------------------------------------------------------------------
# find_boundary_temperature
# ---------------------------------------------------------------------------


def test_warning_boundary_round_trip() -> None:
    """The temperature that yields sigma_Phi = 0.0625 should be 25 C."""
    boundary = find_boundary_temperature(NOMINAL_SIGMA_PHI)
    assert boundary == pytest.approx(NOMINAL_TEMP_C, abs=0.1)


def test_critical_boundary_above_nominal() -> None:
    """Critical threshold is lower sigma -> needs higher temperature."""
    boundary = find_boundary_temperature(0.055)
    assert boundary > NOMINAL_TEMP_C


# ---------------------------------------------------------------------------
# sweep_temperatures
# ---------------------------------------------------------------------------


def test_sweep_covers_full_range() -> None:
    samples = sweep_temperatures(start_c=0.0, stop_c=100.0, step_c=10.0)
    temps = [s.temperature_c for s in samples]
    assert min(temps) == pytest.approx(0.0)
    assert max(temps) == pytest.approx(100.0)


def test_sweep_all_entries_are_thermal_samples() -> None:
    samples = sweep_temperatures(start_c=20.0, stop_c=30.0, step_c=5.0)
    assert all(isinstance(s, ThermalSample) for s in samples)


# ---------------------------------------------------------------------------
# run_thermal_simulation (integration)
# ---------------------------------------------------------------------------


def test_simulation_writes_json(tmp_path) -> None:
    run_thermal_simulation(output_dir=tmp_path, make_plot=False)
    json_path = tmp_path / "week1_thermal.json"
    assert json_path.exists()
    data = json.loads(json_path.read_text())
    assert "boundaries" in data
    assert "sweep" in data
    assert len(data["sweep"]) > 0


def test_simulation_result_structure() -> None:
    result = run_thermal_simulation(make_plot=False)
    assert "model" in result
    assert "boundaries" in result
    assert "thresholds" in result
    assert result["boundaries"]["warning_temp_c"] < result["boundaries"]["critical_temp_c"]
