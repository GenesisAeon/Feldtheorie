"""Tests for experiments.week2.clip_validation — CLIP σ_Φ validation."""

from __future__ import annotations

import json

import numpy as np
import pytest
from experiments.week2.clip_validation import (
    WEEK1_BASELINE_SIGMA_PHI,
    CLIPSample,
    run_clip_validation,
    run_clip_validation_experiment,
    sigma_phi_from_logits,
)

# ---------------------------------------------------------------------------
# test_clip_loading (numpy fallback — validates pipeline works)
# ---------------------------------------------------------------------------


def test_clip_loading_fallback() -> None:
    """Pipeline runs with numpy fallback when CLIP is not installed."""
    samples, report = run_clip_validation(n_samples=10, force_numpy=True)
    assert len(samples) == 10
    assert report.backend == "numpy"


# ---------------------------------------------------------------------------
# test_sigma_phi_consistency
# ---------------------------------------------------------------------------


def test_sigma_phi_consistency_across_runs() -> None:
    """Same seed produces identical σ_Φ values."""
    s1, r1 = run_clip_validation(n_samples=50, force_numpy=True, seed=99)
    s2, r2 = run_clip_validation(n_samples=50, force_numpy=True, seed=99)
    for a, b in zip(s1, s2, strict=True):
        assert a.sigma_phi == b.sigma_phi


def test_sigma_phi_positive() -> None:
    logits = np.array([1.0, 2.0, 3.0, 4.0])
    assert sigma_phi_from_logits(logits) > 0.0


def test_sigma_phi_zero_for_constant() -> None:
    logits = np.array([5.0, 5.0, 5.0])
    assert sigma_phi_from_logits(logits) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Validation report structure
# ---------------------------------------------------------------------------


def test_report_has_required_fields() -> None:
    _, report = run_clip_validation(n_samples=20, force_numpy=True)
    assert report.n_samples == 20
    assert 0.0 <= report.pct_stable <= 100.0
    assert 0.0 <= report.pct_warning <= 100.0
    assert 0.0 <= report.pct_critical <= 100.0
    assert pytest.approx(report.pct_stable + report.pct_warning + report.pct_critical) == 100.0


def test_report_category_means_present() -> None:
    _, report = run_clip_validation(n_samples=50, force_numpy=True)
    assert len(report.category_means) > 0
    for v in report.category_means.values():
        assert v > 0.0


def test_report_baseline_comparison() -> None:
    _, report = run_clip_validation(n_samples=100, force_numpy=True)
    assert report.week1_baseline_sigma_phi == WEEK1_BASELINE_SIGMA_PHI


# ---------------------------------------------------------------------------
# Sample data model
# ---------------------------------------------------------------------------


def test_samples_are_clip_sample_type() -> None:
    samples, _ = run_clip_validation(n_samples=5, force_numpy=True)
    assert all(isinstance(s, CLIPSample) for s in samples)


def test_sample_safety_states_valid() -> None:
    samples, _ = run_clip_validation(n_samples=50, force_numpy=True)
    valid_states = {"stable", "warning", "critical"}
    for s in samples:
        assert s.safety_state in valid_states


# ---------------------------------------------------------------------------
# Integration: file output
# ---------------------------------------------------------------------------


def test_experiment_writes_json(tmp_path) -> None:
    run_clip_validation_experiment(
        output_dir=tmp_path,
        n_samples=20,
        force_numpy=True,
    )
    json_path = tmp_path / "clip_validation.json"
    assert json_path.exists()
    data = json.loads(json_path.read_text())
    assert data["report"]["backend"] == "numpy"
    assert data["sample_count"] == 20


def test_experiment_payload_structure() -> None:
    payload = run_clip_validation_experiment(n_samples=10, force_numpy=True)
    assert "report" in payload
    assert "elapsed_seconds" in payload
    assert "samples" in payload


# ---------------------------------------------------------------------------
# Performance benchmarks
# ---------------------------------------------------------------------------


def test_performance_1000_samples() -> None:
    """1000 samples should complete without error (numpy fallback)."""
    samples, report = run_clip_validation(n_samples=1000, force_numpy=True)
    assert len(samples) == 1000
    assert report.sigma_phi_mean > 0.0
