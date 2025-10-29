"""Tests for the cohort resonance ledger threshold-crossing extensions."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from analysis.resonance_cohort_summary import parse_result, summarise_records


def _write_payload(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _base_payload() -> dict:
    return {
        "theta_estimate": {"value": 0.5, "ci95": [0.45, 0.55]},
        "beta_estimate": {"value": 5.0, "ci95": [4.5, 5.5]},
        "logistic_model": {"r2": 0.99, "aic": -120.0},
        "logistic_fit": {"sigma_hat": [0.25, 0.75]},
        "null_models": {
            "linear": {"r2": 0.8, "aic": -60.0}
        },
        "falsification": {
            "comparisons": {
                "linear": {"delta_aic": 60.0, "delta_r2": 0.19}
            }
        },
        "membrane": {"zeta_mean": 1.2},
    }


def test_parse_result_extracts_threshold_crossing(tmp_path: Path) -> None:
    payload = _base_payload()
    payload["threshold_crossing"] = {
        "crossed": True,
        "crossing_time": 2.0,
        "crossing_R": 0.52,
        "crossing_sigma": 0.61,
        "overshoot": 0.09,
        "zeta_at_crossing": 1.1,
    }
    target = tmp_path / "result.json"
    _write_payload(target, payload)

    record = parse_result(target)

    assert record.threshold_crossed is True
    assert pytest.approx(record.crossing_time, rel=1e-9) == 2.0
    assert pytest.approx(record.crossing_R, rel=1e-9) == 0.52
    assert pytest.approx(record.crossing_sigma, rel=1e-9) == 0.61
    assert pytest.approx(record.overshoot, rel=1e-9) == 0.09
    assert pytest.approx(record.zeta_at_crossing, rel=1e-9) == 1.1


def test_summarise_records_includes_crossing_stats(tmp_path: Path) -> None:
    first = _base_payload()
    first["threshold_crossing"] = {
        "crossed": True,
        "crossing_time": 2.0,
        "crossing_R": 0.52,
        "crossing_sigma": 0.61,
        "overshoot": 0.09,
    }
    first["logistic_fit"] = {
        "sigma_hat": [0.4, 0.6],
        "theta_drift_total": 0.1,
        "beta_drift_total": 0.3,
    }
    first["meta_gate"] = {
        "series": [0.4, 0.7],
        "fraction_above_half": 0.5,
        "stats": {"mean": 0.55},
    }
    second = _base_payload()
    second["threshold_crossing"] = {
        "crossed": False,
        "crossing_time": 4.0,
        "crossing_R": 0.7,
        "crossing_sigma": 0.85,
        "overshoot": 0.05,
    }
    second["logistic_fit"] = {
        "sigma_hat": [0.8, 0.9],
        "theta_drift_total": 0.2,
        "beta_drift_total": 0.5,
    }
    second["meta_gate"] = {
        "series": [0.6, 0.7],
        "stats": {"mean": 0.65},
    }

    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"
    _write_payload(first_path, first)
    _write_payload(second_path, second)

    records = [parse_result(first_path), parse_result(second_path)]
    summary = summarise_records(records)

    crossing = summary["aggregate"]["threshold_crossing"]
    assert crossing["reports"] == 2
    assert crossing["crossed_count"] == 1
    assert pytest.approx(crossing["crossed_fraction"], rel=1e-9) == 0.5

    time_stats = crossing["time"]
    assert time_stats is not None
    assert pytest.approx(time_stats["mean"], rel=1e-9) == 3.0
    assert time_stats["min"] == 2.0
    assert time_stats["max"] == 4.0

    overshoot_stats = crossing["overshoot"]
    assert overshoot_stats is not None
    assert pytest.approx(overshoot_stats["median"], rel=1e-9) == 0.07

    first_stats = summary["domains"][records[0].domain]["threshold_crossing"]
    assert first_stats["reports"] == 1
    assert first_stats["crossed_count"] == 1

    second_stats = summary["domains"][records[1].domain]["threshold_crossing"]
    assert second_stats["reports"] == 1
    assert second_stats["crossed_count"] == 0

    aggregate = summary["aggregate"]
    sigma_fraction = aggregate["sigma_fraction_above_half"]
    assert sigma_fraction is not None
    assert pytest.approx(sigma_fraction["mean"], rel=1e-9) == 0.75
    meta_fraction = aggregate["meta_gate_fraction_above_half"]
    assert meta_fraction is not None
    assert pytest.approx(meta_fraction["mean"], rel=1e-9) == 0.75
    meta_mean = aggregate["meta_gate_mean"]
    assert meta_mean is not None
    assert pytest.approx(meta_mean["mean"], rel=1e-9) == 0.6
    theta_drift = aggregate["theta_drift_total"]
    assert theta_drift is not None
    assert pytest.approx(theta_drift["mean"], rel=1e-9) == 0.15
    beta_drift = aggregate["beta_drift_total"]
    assert beta_drift is not None
    assert pytest.approx(beta_drift["mean"], rel=1e-9) == 0.4


def test_parse_result_computes_fraction_and_meta_gate(tmp_path: Path) -> None:
    payload = _base_payload()
    payload["logistic_fit"] = {
        "sigma_hat": [0.1, 0.5, 0.9],
        "theta_drift_total": 0.4,
        "beta_drift_total": 1.2,
    }
    payload["meta_gate"] = {
        "series": [0.4, 0.8, 0.9],
        "stats": {"mean": 0.7},
    }
    target = tmp_path / "meta.json"
    _write_payload(target, payload)

    record = parse_result(target)

    assert pytest.approx(record.sigma_fraction_above_half, rel=1e-9) == (2 / 3)
    assert pytest.approx(record.theta_drift_total, rel=1e-9) == 0.4
    assert pytest.approx(record.beta_drift_total, rel=1e-9) == 1.2
    assert pytest.approx(record.meta_gate_fraction_above_half, rel=1e-9) == (2 / 3)
    assert pytest.approx(record.meta_gate_mean, rel=1e-9) == 0.7
