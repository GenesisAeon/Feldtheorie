"""Tests for the Attraktor-Mapping tool."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from analysis.attraktor_mapping import (
    AFET_TERMS,
    build_cooccurrence_graph,
    compute_graph_metrics,
    extract_terms_from_text,
    scan_files,
)


@pytest.fixture()
def sample_texts(tmp_path: Path) -> Path:
    """Create sample files with known AFET terms for extraction."""
    doc = tmp_path / "sample.md"
    doc.write_text(
        "The UTAC framework defines β as critical threshold.\n"
        "CREP validation ensures σ_Φ stability.\n"
        "The Bardo-Phase transition leverages v_RIG for integration.\n"
        "Diamond Architecture provides the structural backbone for UTAC.\n",
        encoding="utf-8",
    )
    code = tmp_path / "sample.py"
    code.write_text(
        '# AFET constants: β, σ_Φ\n'
        'BETA_CRITICAL = 37.6  # β threshold\n'
        'SIGMA_PHI = 0.0625  # σ_Φ boundary\n',
        encoding="utf-8",
    )
    return tmp_path


class TestTermExtraction:
    def test_known_terms_detected(self) -> None:
        text = "UTAC defines β and σ_Φ with CREP validation in Diamond Architecture"
        found = extract_terms_from_text(text)
        assert "UTAC" in found
        assert "β" in found
        assert "σ_Φ" in found
        assert "CREP" in found
        assert "Diamond Architecture" in found

    def test_empty_text_yields_empty(self) -> None:
        assert extract_terms_from_text("") == []

    def test_no_duplicates(self) -> None:
        text = "UTAC and UTAC again, UTAC once more"
        found = extract_terms_from_text(text)
        assert found.count("UTAC") == 1

    def test_all_canonical_terms_recognizable(self) -> None:
        """Every term in AFET_TERMS should be extractable from its own name."""
        for term in AFET_TERMS:
            found = extract_terms_from_text(f"context {term} context")
            assert term in found, f"Term '{term}' not found in extraction"


class TestFileScan:
    def test_scan_finds_terms_across_files(self, sample_texts: Path) -> None:
        results = scan_files([sample_texts])
        # Should find terms from both .md and .py files
        all_terms = set()
        for entry in results:
            all_terms.update(entry["terms"])
        assert "UTAC" in all_terms
        assert "β" in all_terms
        assert "σ_Φ" in all_terms

    def test_scan_returns_file_paths(self, sample_texts: Path) -> None:
        results = scan_files([sample_texts])
        paths = {entry["file"] for entry in results}
        assert any("sample.md" in p for p in paths)
        assert any("sample.py" in p for p in paths)


class TestGraphConstruction:
    def test_graph_has_expected_nodes(self, sample_texts: Path) -> None:
        results = scan_files([sample_texts])
        graph = build_cooccurrence_graph(results)
        assert graph.number_of_nodes() >= 3

    def test_cooccurring_terms_share_edge(self) -> None:
        results = [{"file": "a.md", "terms": ["UTAC", "β", "CREP"]}]
        graph = build_cooccurrence_graph(results)
        assert graph.has_edge("UTAC", "β")
        assert graph.has_edge("UTAC", "CREP")
        assert graph.has_edge("β", "CREP")

    def test_single_term_no_edges(self) -> None:
        results = [{"file": "a.md", "terms": ["UTAC"]}]
        graph = build_cooccurrence_graph(results)
        assert graph.number_of_edges() == 0


class TestMetrics:
    def test_metrics_contain_expected_keys(self) -> None:
        results = [
            {"file": "a.md", "terms": ["UTAC", "β", "CREP"]},
            {"file": "b.md", "terms": ["UTAC", "σ_Φ"]},
        ]
        graph = build_cooccurrence_graph(results)
        metrics = compute_graph_metrics(graph)
        assert "UTAC" in metrics
        assert "degree" in metrics["UTAC"]
        assert "betweenness" in metrics["UTAC"]
        assert "pagerank" in metrics["UTAC"]

    def test_hub_node_has_highest_degree(self) -> None:
        """UTAC appears in all docs -> should have highest degree."""
        results = [
            {"file": "a.md", "terms": ["UTAC", "β"]},
            {"file": "b.md", "terms": ["UTAC", "CREP"]},
            {"file": "c.md", "terms": ["UTAC", "v_RIG"]},
        ]
        graph = build_cooccurrence_graph(results)
        metrics = compute_graph_metrics(graph)
        utac_degree = metrics["UTAC"]["degree"]
        for node, m in metrics.items():
            if node != "UTAC":
                assert utac_degree >= m["degree"]
