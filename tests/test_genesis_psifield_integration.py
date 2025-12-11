"""
Integration Tests for GenesisCube ↔ PsiFieldPipeline

Tests the V6 integration between:
- genesis_cube.py: Geometric tesseract slicing (block universe)
- psi_field.py: Entropische Wellenfunktion ψ_genesis

References:
- V6_Wellenfunktions_Integrationsplan.md
- simulation/genesis_cube.py (compute_psifield_analysis, hybrid_evolution)
"""

from __future__ import annotations

import numpy as np
import pytest
from simulation.genesis_cube import PSIFIELD_AVAILABLE, GenesisCube, GenesisCubeConfig


class TestGenesisPsiFieldIntegration:
    """Test suite for GenesisCube + PsiFieldPipeline integration."""

    def test_psifield_pipeline_import_available(self):
        """PsiFieldPipeline should be importable."""
        assert PSIFIELD_AVAILABLE, "PsiFieldPipeline import failed"

    def test_genesis_cube_with_psifield_disabled(self):
        """GenesisCube should work without PsiFieldPipeline."""
        config = GenesisCubeConfig(use_psifield_pipeline=False)
        cube = GenesisCube(config)

        assert cube.psi_pipeline is None

    def test_genesis_cube_with_psifield_enabled(self):
        """GenesisCube should initialize PsiFieldPipeline when enabled."""
        if not PSIFIELD_AVAILABLE:
            pytest.skip("PsiFieldPipeline not available")

        config = GenesisCubeConfig(use_psifield_pipeline=True)
        cube = GenesisCube(config)

        assert cube.psi_pipeline is not None

    def test_compute_psifield_analysis_returns_dict(self):
        """compute_psifield_analysis() should return complete results."""
        if not PSIFIELD_AVAILABLE:
            pytest.skip("PsiFieldPipeline not available")

        config = GenesisCubeConfig(use_psifield_pipeline=True)
        cube = GenesisCube(config)

        results = cube.compute_psifield_analysis(r_max=5.0, n_points=20, theta_phi_res=10, t=0.0)

        assert results is not None
        assert "r_grid" in results
        assert "psi" in results
        assert "entropy" in results
        assert "utac_coupling" in results

    def test_compute_psifield_analysis_utac_coupling(self):
        """UTAC coupling should be computed and included."""
        if not PSIFIELD_AVAILABLE:
            pytest.skip("PsiFieldPipeline not available")

        config = GenesisCubeConfig(
            use_psifield_pipeline=True,
            beta=4.8,
            theta=0.5,
        )
        cube = GenesisCube(config)

        results = cube.compute_psifield_analysis(r_max=5.0, n_points=20)

        utac = results["utac_coupling"]
        assert "R" in utac
        assert "sigma" in utac
        assert "beta" in utac
        assert utac["beta"] == 4.8
        assert utac["theta"] == 0.5

    def test_compute_psifield_analysis_without_pipeline(self):
        """Should return None and warn when pipeline not available."""
        config = GenesisCubeConfig(use_psifield_pipeline=False)
        cube = GenesisCube(config)

        results = cube.compute_psifield_analysis()

        assert results is None

    def test_hybrid_evolution_returns_dict(self):
        """hybrid_evolution() should return combined geometric + quantum results."""
        config = GenesisCubeConfig(use_psifield_pipeline=True)
        cube = GenesisCube(config)

        results = cube.hybrid_evolution(r_max=5.0, n_points=30)

        assert "geometric" in results
        assert "quantum" in results
        assert "integration" in results

    def test_hybrid_evolution_geometric_component(self):
        """Geometric component should contain block universe slices."""
        config = GenesisCubeConfig(use_psifield_pipeline=True)
        cube = GenesisCube(config)

        results = cube.hybrid_evolution(r_max=5.0, n_points=30)

        geometric = results["geometric"]
        assert "slices" in geometric
        assert "slice_count" in geometric
        assert len(geometric["slices"]) > 0

    def test_hybrid_evolution_quantum_component(self):
        """Quantum component should contain wavefunction results (if enabled)."""
        if not PSIFIELD_AVAILABLE:
            pytest.skip("PsiFieldPipeline not available")

        config = GenesisCubeConfig(use_psifield_pipeline=True)
        cube = GenesisCube(config)

        results = cube.hybrid_evolution(r_max=5.0, n_points=20)

        quantum = results["quantum"]
        if quantum is not None:
            assert "psi" in quantum
            assert "entropy" in quantum
            assert "mean_r" in quantum

    def test_hybrid_evolution_without_psifield(self):
        """Hybrid evolution should work even without PsiFieldPipeline."""
        config = GenesisCubeConfig(use_psifield_pipeline=False)
        cube = GenesisCube(config)

        results = cube.hybrid_evolution(r_max=5.0, n_points=20)

        assert results["quantum"] is None
        assert results["integration"]["psifield_enabled"] is False
        # But geometric should still work
        assert len(results["geometric"]["slices"]) > 0

    def test_integration_preserves_genesis_cube_functionality(self):
        """Integration should not break existing GenesisCube methods."""
        config = GenesisCubeConfig(use_psifield_pipeline=True)
        cube = GenesisCube(config)

        # Test existing methods still work
        vectors = cube.seed_vectors()
        assert len(vectors) == 3

        cube_vertices = cube.cube_vertices(scale=1.0)
        assert len(cube_vertices) == 8

        hexagon = cube.project_hexagon()
        assert len(hexagon) == 6

        slices = cube.block_universe_slices()
        assert len(slices) > 0

    def test_psifield_analysis_entropy_computation(self):
        """Entropy should be computed via PsiFieldPipeline."""
        if not PSIFIELD_AVAILABLE:
            pytest.skip("PsiFieldPipeline not available")

        config = GenesisCubeConfig(use_psifield_pipeline=True)
        cube = GenesisCube(config)

        results = cube.compute_psifield_analysis(r_max=5.0, n_points=30)

        entropy = results["entropy"]
        assert entropy >= 0
        assert np.isfinite(entropy)

    def test_psifield_analysis_radial_statistics(self):
        """Radial statistics (mean_r, delta_r) should be computed."""
        if not PSIFIELD_AVAILABLE:
            pytest.skip("PsiFieldPipeline not available")

        config = GenesisCubeConfig(use_psifield_pipeline=True)
        cube = GenesisCube(config)

        results = cube.compute_psifield_analysis(r_max=10.0, n_points=50)

        assert "mean_r" in results
        assert "delta_r" in results
        assert results["mean_r"] >= 0
        assert results["delta_r"] >= 0


class TestV6IntegrationPhilosophy:
    """Tests for V6 conceptual integration (Tesseract + Ψ-field)."""

    def test_v6_integration_description(self):
        """Hybrid evolution should describe V6 philosophy."""
        config = GenesisCubeConfig(use_psifield_pipeline=True)
        cube = GenesisCube(config)

        results = cube.hybrid_evolution()

        integration = results["integration"]
        assert "V6" in integration["description"]
        assert "Tesseract" in integration["description"]
        assert "ψ_genesis" in integration["description"]

    def test_quantum_classical_bridge(self):
        """Integration should bridge quantum (Planck scale) and classical (UTAC)."""
        if not PSIFIELD_AVAILABLE:
            pytest.skip("PsiFieldPipeline not available")

        config = GenesisCubeConfig(
            use_psifield_pipeline=True,
            beta=4.8,
            theta=0.0,
        )
        cube = GenesisCube(config)

        results = cube.compute_psifield_analysis(r_max=5.0)

        utac = results["utac_coupling"]
        # Planck scale → UTAC R mapping
        assert "mean_r_planck" in utac  # Quantum (Planck lengths)
        assert "R" in utac  # Classical (UTAC parameter)
        assert "sigma" in utac  # UTAC coupling strength


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
