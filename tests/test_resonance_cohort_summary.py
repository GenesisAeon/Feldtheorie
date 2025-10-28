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
    second = _base_payload()
    second["threshold_crossing"] = {
        "crossed": False,
        "crossing_time": 4.0,
        "crossing_R": 0.7,
        "crossing_sigma": 0.85,
        "overshoot": 0.05,
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
