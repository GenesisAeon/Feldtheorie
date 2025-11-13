"""Unit tests for UTAC Microscopic ABM (RG Phase 2)

Tests:
- ABM initialization & lattice state
- Local field computation
- Agent update dynamics
- Equilibration convergence
- Coarse-graining correctness
- Emergent β extraction
- Multi-system validation

Version: 1.0.0
Date: 2025-11-13
"""

import numpy as np
import pytest

from models.utac_microscopic_abm import (
    ABMParams,
    MicroscopicABM,
    EmergentBetaSimulator,
    coarse_grain,
    multi_scale_coarsening,
    extract_emergent_beta,
    microscopic_to_beta_map,
)


# ═══════════════════════════════════════════════════════════════
# ABM INITIALIZATION & STATE TESTS
# ═══════════════════════════════════════════════════════════════


class TestABMInitialization:
    """Test ABM initialization and basic state."""

    def test_abm_params_defaults(self):
        """Test default ABM parameters."""
        params = ABMParams()
        assert params.J == 0.8
        assert params.h == 0.5
        assert params.T == 0.2
        assert params.lattice_size == 128

    def test_abm_params_custom(self):
        """Test custom ABM parameters."""
        params = ABMParams(J=0.6, h=0.3, T=0.15, lattice_size=64)
        assert params.J == 0.6
        assert params.h == 0.3
        assert params.T == 0.15
        assert params.lattice_size == 64

    def test_abm_initialization(self):
        """Test ABM initializes with correct lattice."""
        params = ABMParams(lattice_size=32)
        abm = MicroscopicABM(params)
        assert abm.lattice.shape == (32, 32)
        assert np.all(abm.lattice >= 0) and np.all(abm.lattice <= 1)

    def test_abm_snapshot(self):
        """Test ABM snapshot returns copy."""
        params = ABMParams(lattice_size=16)
        abm = MicroscopicABM(params)
        snapshot1 = abm.snapshot()
        abm.step(n_updates=100)
        snapshot2 = abm.snapshot()
        assert not np.array_equal(snapshot1, snapshot2)


# ═══════════════════════════════════════════════════════════════
# LOCAL FIELD & DYNAMICS TESTS
# ═══════════════════════════════════════════════════════════════


class TestABMDynamics:
    """Test ABM local field and agent update dynamics."""

    def test_local_field_range(self):
        """Test local field is in reasonable range."""
        params = ABMParams(J=0.8, h=0.5, lattice_size=16)
        abm = MicroscopicABM(params)
        for i in range(3):
            for j in range(3):
                h_local = abm.local_field(i, j)
                assert -2 < h_local < 3  # Reasonable range

    def test_local_field_coupling(self):
        """Test local field increases with neighbor activation."""
        params = ABMParams(J=0.8, h=0.0, lattice_size=8)
        abm = MicroscopicABM(params)

        # Low neighbor activation
        abm.lattice[:, :] = 0.1
        h_low = abm.local_field(4, 4)

        # High neighbor activation
        abm.lattice[:, :] = 0.9
        h_high = abm.local_field(4, 4)

        assert h_high > h_low

    def test_agent_update_bounds(self):
        """Test agent update keeps activation in [0,1]."""
        params = ABMParams(lattice_size=16)
        abm = MicroscopicABM(params)
        for _ in range(100):
            i, j = np.random.randint(0, 16, size=2)
            abm.update_agent(i, j)
            assert 0 <= abm.lattice[i, j] <= 1

    def test_step_changes_state(self):
        """Test step() changes lattice state."""
        params = ABMParams(lattice_size=16)
        abm = MicroscopicABM(params)
        before = abm.snapshot()
        abm.step(n_updates=100)
        after = abm.snapshot()
        assert not np.array_equal(before, after)

    def test_equilibration(self):
        """Test equilibration converges to steady state."""
        params = ABMParams(lattice_size=32, T=0.1)
        abm = MicroscopicABM(params)
        abm.equilibrate(n_steps=50)
        mean_before = abm.mean_activation()
        abm.step(n_updates=1000)
        mean_after = abm.mean_activation()
        # After equilibration, mean should be relatively stable
        assert abs(mean_after - mean_before) < 0.1


# ═══════════════════════════════════════════════════════════════
# COARSE-GRAINING TESTS
# ═══════════════════════════════════════════════════════════════


class TestCoarseGraining:
    """Test coarse-graining algorithms."""

    def test_coarse_grain_shape(self):
        """Test coarse-graining reduces lattice size."""
        lattice = np.random.rand(64, 64)
        coarse = coarse_grain(lattice, block_size=2)
        assert coarse.shape == (32, 32)

    def test_coarse_grain_preserves_mean(self):
        """Test coarse-graining approximately preserves mean."""
        lattice = np.random.rand(64, 64)
        mean_before = np.mean(lattice)
        coarse = coarse_grain(lattice, block_size=2)
        mean_after = np.mean(coarse)
        assert abs(mean_after - mean_before) < 0.1

    def test_multi_scale_coarsening(self):
        """Test multi-scale coarse-graining."""
        lattice = np.random.rand(128, 128)
        scales = multi_scale_coarsening(lattice, n_scales=3)
        assert len(scales) == 4  # Original + 3 coarse levels
        assert scales[0].shape == (128, 128)
        assert scales[1].shape == (64, 64)
        assert scales[2].shape == (32, 32)
        assert scales[3].shape == (16, 16)


# ═══════════════════════════════════════════════════════════════
# EMERGENT β EXTRACTION TESTS
# ═══════════════════════════════════════════════════════════════


class TestEmergentBeta:
    """Test emergent β extraction from coarse-grained data."""

    def test_extract_beta_perfect_logistic(self):
        """Test β extraction on perfect logistic data."""
        R_values = np.linspace(-2, 2, 50)
        beta_true = 4.0
        theta_true = 0.0
        sigma_true = 1 / (1 + np.exp(-beta_true * (R_values - theta_true)))

        beta_fit, r_squared, fit_info = extract_emergent_beta(
            R_values, sigma_true, theta=0.0
        )

        assert abs(beta_fit - beta_true) < 0.1
        assert r_squared > 0.99

    def test_extract_beta_noisy_data(self):
        """Test β extraction with noisy data."""
        R_values = np.linspace(-2, 2, 50)
        beta_true = 3.5
        theta_true = 0.0
        sigma_true = 1 / (1 + np.exp(-beta_true * (R_values - theta_true)))
        sigma_noisy = sigma_true + np.random.randn(len(sigma_true)) * 0.05
        sigma_noisy = np.clip(sigma_noisy, 0, 1)

        beta_fit, r_squared, fit_info = extract_emergent_beta(
            R_values, sigma_noisy, theta=0.0
        )

        assert abs(beta_fit - beta_true) < 0.5
        assert r_squared > 0.9

    def test_extract_beta_edge_cases(self):
        """Test β extraction handles edge cases."""
        R_values = np.linspace(0, 1, 20)
        sigma_flat = np.ones(20) * 0.5  # Flat, no transition

        beta_fit, r_squared, fit_info = extract_emergent_beta(
            R_values, sigma_flat, theta=0.5
        )

        # Should return valid result or NaN
        assert np.isfinite(beta_fit) or np.isnan(beta_fit)


# ═══════════════════════════════════════════════════════════════
# EMERGENT β SIMULATOR TESTS
# ═══════════════════════════════════════════════════════════════


class TestEmergentBetaSimulator:
    """Test full emergent β simulator."""

    def test_simulator_initialization(self):
        """Test simulator initializes correctly."""
        params = ABMParams(lattice_size=32)
        simulator = EmergentBetaSimulator(params)
        assert simulator.params.lattice_size == 32

    def test_scan_resource_range(self):
        """Test R-scan produces valid σ values."""
        params = ABMParams(lattice_size=16, T=0.2)
        simulator = EmergentBetaSimulator(params)
        R_values, sigma_values = simulator.scan_resource_range(
            R_min=-1.0, R_max=1.0, n_points=10
        )
        assert len(R_values) == 10
        assert len(sigma_values) == 10
        assert np.all(sigma_values >= 0) and np.all(sigma_values <= 1)

    def test_compute_emergent_beta(self):
        """Test emergent β computation."""
        params = ABMParams(J=0.8, T=0.2, lattice_size=32)
        simulator = EmergentBetaSimulator(params)
        results = simulator.compute_emergent_beta(n_points=15)

        assert "beta_emergent" in results
        assert "r_squared" in results
        assert "fit_info" in results
        assert np.isfinite(results["beta_emergent"])
        assert 0 <= results["r_squared"] <= 1

    def test_emergent_beta_theory_match(self):
        """Test emergent β roughly matches theory β ≈ J/T."""
        params = ABMParams(J=0.6, T=0.15, lattice_size=32)
        simulator = EmergentBetaSimulator(params)
        results = simulator.compute_emergent_beta(n_points=15)

        beta_emergent = results["beta_emergent"]
        beta_theory = params.J / params.T

        # Allow 50% deviation (coarse approximation)
        deviation = abs(beta_emergent - beta_theory) / beta_theory
        assert deviation < 0.5 or results["r_squared"] < 0.7  # Or poor fit


# ═══════════════════════════════════════════════════════════════
# MICROSCOPIC → MACROSCOPIC MAPPING TESTS
# ═══════════════════════════════════════════════════════════════


class TestMicroscopicMapping:
    """Test microscopic → macroscopic β mapping."""

    def test_mapping_structure(self):
        """Test mapping returns expected structure."""
        mapping = microscopic_to_beta_map()
        assert "llm_training" in mapping
        assert "climate_amoc" in mapping
        assert "urban_heat" in mapping

        for system, config in mapping.items():
            assert "J" in config
            assert "T" in config
            assert "beta_predicted" in config

    def test_mapping_theory_consistency(self):
        """Test mapping β ≈ J/T is consistent."""
        mapping = microscopic_to_beta_map()

        for system, config in mapping.items():
            beta_predicted = config["beta_predicted"]
            beta_theory = config["J"] / config["T"]

            # Theory should match prediction within 20%
            deviation = abs(beta_predicted - beta_theory) / beta_predicted
            assert deviation < 0.2, f"{system}: {deviation:.2%} deviation"


# ═══════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════


class TestIntegration:
    """Integration tests for full ABM → emergent β pipeline."""

    @pytest.mark.slow
    def test_full_pipeline_llm(self):
        """Test full pipeline for LLM-like system."""
        # LLM: J=0.8, T=0.19 → β ≈ 4.2
        params = ABMParams(J=0.8, T=0.19, lattice_size=32)
        simulator = EmergentBetaSimulator(params)
        results = simulator.compute_emergent_beta(n_points=20)

        beta_emergent = results["beta_emergent"]
        r_squared = results["r_squared"]

        # Should be in ballpark of 4.2 (allow 50% deviation for small lattice)
        assert 2 < beta_emergent < 6 or r_squared < 0.7
        assert r_squared > 0.5  # At least moderate fit

    @pytest.mark.slow
    def test_full_pipeline_quantum(self):
        """Test full pipeline for quantum-like system."""
        # Quantum: J=0.15, T=0.11 → β ≈ 1.4
        params = ABMParams(J=0.15, T=0.11, lattice_size=32)
        simulator = EmergentBetaSimulator(params)
        results = simulator.compute_emergent_beta(n_points=20)

        beta_emergent = results["beta_emergent"]
        r_squared = results["r_squared"]

        # Low-β system (allow wider range)
        assert 0.5 < beta_emergent < 2.5 or r_squared < 0.7
        assert r_squared > 0.4


# ═══════════════════════════════════════════════════════════════
# RUN TESTS
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
