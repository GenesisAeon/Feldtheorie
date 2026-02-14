"""Tests for the AFET Visual Profiling Hub (Quad-Layer 4)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from visuals.profiling import FieldMetrics, ProfilingGenerator, load_symbols


@pytest.fixture
def generator(tmp_path: Path) -> ProfilingGenerator:
    return ProfilingGenerator()


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


class TestFieldMetrics:
    def test_defaults(self):
        m = FieldMetrics()
        assert m.sigma_phi_deviation == 0.0
        assert m.s_crit_proximity == 0.0
        assert "info" in m.beta_values
        assert "axioms" in m.beta_values

    def test_custom_values(self):
        m = FieldMetrics(
            sigma_phi_deviation=0.5,
            beta_values={"neuro": 13.5},
            s_crit_proximity=0.8,
            label="test-v1",
        )
        assert m.sigma_phi_deviation == 0.5
        assert m.s_crit_proximity == 0.8
        assert m.label == "test-v1"
        assert list(m.beta_values.keys()) == ["neuro"]


class TestLoadSymbols:
    def test_loads_default_symbols(self):
        syms = load_symbols()
        assert "sigma_phi" in syms
        assert "beta_critical" in syms
        assert "domains" in syms
        assert "phi_scaling" in syms

    def test_symbol_types(self):
        syms = load_symbols()
        assert syms["sigma_phi"]["type"] == "halo"
        assert syms["beta_critical"]["type"] == "nucleus"
        assert syms["phi_scaling"]["type"] == "radial_lines"

    def test_domain_entries(self):
        syms = load_symbols()
        domains = syms["domains"]
        assert "info" in domains
        assert "bio" in domains
        assert "climate" in domains
        assert "neuro" in domains
        assert "axioms" in domains
        for name, d in domains.items():
            assert "beta" in d
            assert "color" in d


class TestProfilingGenerator:
    def test_generate_default_snapshot(self, generator: ProfilingGenerator, output_dir: Path):
        out = generator.generate_snapshot(output_path=output_dir / "default.png")
        assert out.exists()
        assert out.stat().st_size > 0

    def test_generate_custom_metrics(self, generator: ProfilingGenerator, output_dir: Path):
        metrics = FieldMetrics(
            sigma_phi_deviation=0.3,
            beta_values={"neuro": 13.5, "climate": 11.0, "info": 4.3},
            s_crit_proximity=0.5,
            entropy_density=8.0,
            label="DOI-v11",
        )
        out = generator.generate_snapshot(metrics=metrics, output_path=output_dir / "custom.png")
        assert out.exists()
        assert out.stat().st_size > 0

    def test_generate_near_collapse(self, generator: ProfilingGenerator, output_dir: Path):
        """Snapshot near frame-collapse should include warning ring."""
        metrics = FieldMetrics(
            sigma_phi_deviation=0.85,
            s_crit_proximity=0.9,
        )
        out = generator.generate_snapshot(metrics=metrics, output_path=output_dir / "collapse.png")
        assert out.exists()

    def test_generate_empty_domains(self, generator: ProfilingGenerator, output_dir: Path):
        metrics = FieldMetrics(beta_values={})
        out = generator.generate_snapshot(metrics=metrics, output_path=output_dir / "empty.png")
        assert out.exists()

    def test_get_field_snapshot_structure(self, generator: ProfilingGenerator):
        snapshot = generator.get_field_snapshot()
        assert snapshot["layer"] == "visual_profiling_hub"
        assert snapshot["quad_layer_index"] == 4
        assert "metastability" in snapshot
        assert "beta_analysis" in snapshot
        assert "metrics" in snapshot

    def test_get_field_snapshot_with_metrics(self, generator: ProfilingGenerator):
        metrics = FieldMetrics(
            entropy_density=10.0,
            beta_values={"neuro": 13.5},
        )
        snapshot = generator.get_field_snapshot(metrics=metrics)
        assert snapshot["metrics"]["entropy_density"] == 10.0
        assert "neuro" in snapshot["beta_analysis"]
        assert "peclet" in snapshot["beta_analysis"]["neuro"]

    def test_metastability_in_snapshot(self, generator: ProfilingGenerator):
        metrics = FieldMetrics(entropy_density=20.0)
        snapshot = generator.get_field_snapshot(metrics=metrics)
        # 1/sigma_phi = 16.0, so entropy_density=20 exceeds it
        assert snapshot["metastability"]["is_metastable"] is False

        metrics_safe = FieldMetrics(entropy_density=5.0)
        snapshot_safe = generator.get_field_snapshot(metrics=metrics_safe)
        assert snapshot_safe["metastability"]["is_metastable"] is True
