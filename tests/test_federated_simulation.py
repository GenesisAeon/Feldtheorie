"""Tests for experiments.week3.federated_simulation."""

from __future__ import annotations

import json

import numpy as np
import pytest

from experiments.week3.federated_simulation import (
    CLIENT_PROFILES,
    ClientState,
    FederatedReport,
    FederatedRound,
    detect_outliers,
    run_federated_experiment,
    simulate_federation,
    weighted_median,
)


# ===========================================================================
# weighted_median
# ===========================================================================


class TestWeightedMedian:
    def test_equal_weights(self) -> None:
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        weights = [1.0, 1.0, 1.0, 1.0, 1.0]
        result = weighted_median(values, weights)
        assert result == 3.0

    def test_skewed_weights(self) -> None:
        values = [1.0, 100.0]
        weights = [10.0, 1.0]
        result = weighted_median(values, weights)
        assert result == 1.0  # heavy weight on 1.0

    def test_single_value(self) -> None:
        assert weighted_median([42.0], [1.0]) == 42.0


# ===========================================================================
# detect_outliers
# ===========================================================================


class TestDetectOutliers:
    def test_no_outliers_in_tight_cluster(self) -> None:
        betas = [37.0, 37.5, 38.0, 37.2, 37.8]
        flags = detect_outliers(betas, 37.5)
        assert not any(flags)

    def test_detects_extreme_outlier(self) -> None:
        betas = [37.0, 37.5, 38.0, 37.2, 100.0]
        flags = detect_outliers(betas, 37.5)
        assert flags[-1] is True

    def test_identical_values_no_outliers(self) -> None:
        betas = [37.0, 37.0, 37.0]
        flags = detect_outliers(betas, 37.0)
        assert not any(flags)


# ===========================================================================
# simulate_federation
# ===========================================================================


class TestSimulateFederation:
    def test_returns_correct_types(self) -> None:
        rounds, report = simulate_federation(n_rounds=5)
        assert len(rounds) == 5
        assert isinstance(report, FederatedReport)
        assert all(isinstance(r, FederatedRound) for r in rounds)

    def test_deterministic(self) -> None:
        r1, rep1 = simulate_federation(n_rounds=5, seed=42)
        r2, rep2 = simulate_federation(n_rounds=5, seed=42)
        for a, b in zip(r1, r2):
            assert a.beta_consensus == b.beta_consensus

    def test_correct_client_count(self) -> None:
        rounds, report = simulate_federation(n_rounds=3)
        assert report.n_clients == len(CLIENT_PROFILES)
        for r in rounds:
            assert len(r.client_states) == len(CLIENT_PROFILES)

    def test_consensus_in_reasonable_range(self) -> None:
        _, report = simulate_federation(n_rounds=10)
        # Consensus should be between min and max client betas
        min_beta = min(p["beta_c"] for p in CLIENT_PROFILES)
        max_beta = max(p["beta_c"] for p in CLIENT_PROFILES)
        assert min_beta - 5 <= report.final_consensus_beta <= max_beta + 5

    def test_sigma_phi_mean_positive(self) -> None:
        _, report = simulate_federation(n_rounds=10)
        assert report.sigma_phi_mean > 0.0

    def test_per_client_drift_present(self) -> None:
        _, report = simulate_federation(n_rounds=10)
        assert len(report.per_client_drift) == len(CLIENT_PROFILES)
        for name, drift in report.per_client_drift.items():
            assert drift >= 0.0


# ===========================================================================
# Integration: file output
# ===========================================================================


class TestFederatedExperiment:
    def test_writes_json(self, tmp_path) -> None:
        payload = run_federated_experiment(output_dir=tmp_path, n_rounds=5)
        json_path = tmp_path / "federated.json"
        assert json_path.exists()
        data = json.loads(json_path.read_text())
        assert data["report"]["n_rounds"] == 5

    def test_payload_structure(self) -> None:
        payload = run_federated_experiment(n_rounds=3)
        assert "report" in payload
        assert "rounds" in payload
        assert len(payload["rounds"]) == 3
