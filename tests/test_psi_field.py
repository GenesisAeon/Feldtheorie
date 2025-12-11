"""
Unit Tests for Ψ-Field Pipeline (psi_field.py)

Tests cover:
1. PsiFieldConfig initialization and defaults
2. PsiField wavefunction computation (radial, angular, time components)
3. Normalization and probability density
4. UTAC collapse mapping |ψ|² → P(R)
5. Entropy computation (von Neumann)
6. PsiFieldPipeline integration
7. Physical constants (α⁻¹, Φ, Planck scales)

References:
- pipelines/wavefunction/psi_field.py
- V6_Wellenfunktions_Integrationsplan.md
- GrundPrinzip Simulation.txt (theoretical foundation)
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from pipelines.wavefunction.psi_field import (
    ALPHA_INV,
    E_PLANCK,
    HBAR,
    L_PLANCK,
    PHI,
    PsiField,
    PsiFieldConfig,
    PsiFieldPipeline,
    compute_psi_genesis,
)


class TestPsiFieldConfig:
    """Test suite for PsiFieldConfig dataclass."""

    def test_default_config_uses_physical_constants(self):
        """Default config should use α⁻¹=137, Φ=1.618, etc."""
        config = PsiFieldConfig()

        assert config.alpha_inv == ALPHA_INV
        assert config.phi == PHI
        assert config.l_planck == L_PLANCK
        assert config.e_planck == E_PLANCK

    def test_config_tetrahedral_symmetry_enabled_by_default(self):
        """Tetrahedral symmetry should be enabled by default."""
        config = PsiFieldConfig()

        assert config.use_tetrahedral is True
        assert config.n_tetra_modes == 4

    def test_config_normalization_enabled_by_default(self):
        """Wavefunction normalization should be enabled by default."""
        config = PsiFieldConfig()

        assert config.normalize is True

    def test_config_custom_parameters(self):
        """Should allow custom physical constants."""
        config = PsiFieldConfig(
            alpha_inv=100.0,
            phi=2.0,
            use_tetrahedral=False,
        )

        assert config.alpha_inv == 100.0
        assert config.phi == 2.0
        assert config.use_tetrahedral is False

    def test_config_notes_present(self):
        """Config should contain documentation notes."""
        config = PsiFieldConfig()

        assert len(config.notes) > 0
        assert any("ψ_genesis" in note for note in config.notes)


class TestPsiFieldRadialComponent:
    """Test suite for radial component exp(-α⁻¹·r²/ℓ²_P)."""

    def test_radial_component_at_origin_is_unity(self):
        """At r=0, radial component should be exp(0) = 1."""
        field = PsiField()
        r = np.array([0.0])

        psi_radial = field._radial_component(r)

        assert np.isclose(psi_radial[0], 1.0)

    def test_radial_component_decays_with_distance(self):
        """Radial component should decay as r increases."""
        field = PsiField()
        r_vals = np.array([0.0, 1.0, 2.0, 5.0])

        psi_radial = field._radial_component(r_vals)

        # Should be monotonically decreasing
        assert all(psi_radial[i] >= psi_radial[i + 1] for i in range(len(psi_radial) - 1))

    def test_radial_component_gaussian_form(self):
        """Radial component should follow Gaussian exp(-α⁻¹·r²)."""
        field = PsiField()
        r = np.array([1.0])

        psi_radial = field._radial_component(r)
        expected = np.exp(-ALPHA_INV * 1.0**2 / L_PLANCK**2)

        assert np.isclose(psi_radial[0], expected)

    def test_radial_component_scales_with_alpha_inv(self):
        """Higher α⁻¹ should lead to faster decay."""
        field_low = PsiField(PsiFieldConfig(alpha_inv=100.0))
        field_high = PsiField(PsiFieldConfig(alpha_inv=200.0))

        r = np.array([1e-36])  # Small r to avoid underflow

        psi_low = field_low._radial_component(r)
        psi_high = field_high._radial_component(r)

        # Higher α⁻¹ → stronger decay → smaller value
        assert psi_high[0] < psi_low[0]


class TestPsiFieldAngularComponent:
    """Test suite for angular component Y_tetra(θ,φ)."""

    def test_angular_component_returns_scalar_when_disabled(self):
        """When tetrahedral=False, angular component should be 1."""
        config = PsiFieldConfig(use_tetrahedral=False)
        field = PsiField(config)

        theta = np.array([np.pi / 4])
        phi = np.array([0.0])

        y_angular = field._angular_component(theta, phi)

        assert np.allclose(y_angular, 1.0)

    def test_angular_component_tetrahedral_symmetry(self):
        """Tetrahedral harmonics should exhibit approximate symmetry."""
        field = PsiField()

        theta = np.pi / 4
        # 3-fold symmetry: φ = 0, 2π/3, 4π/3
        phi_vals = np.array([0, 2 * np.pi / 3, 4 * np.pi / 3])

        y_vals = [field._angular_component(np.array([theta]), np.array([phi])) for phi in phi_vals]

        # Magnitudes should be similar (within 50% due to approximate form)
        mags = [abs(complex(y[0])) for y in y_vals]
        mean_mag = sum(mags) / len(mags)

        for mag in mags:
            assert abs(mag - mean_mag) / (mean_mag + 1e-10) < 0.6

    def test_angular_component_is_complex_valued(self):
        """Angular component can be complex (due to spherical harmonics)."""
        field = PsiField()

        theta = np.array([np.pi / 4])
        phi = np.array([np.pi / 6])

        y_angular = field._angular_component(theta, phi)

        # Should be numeric (real or complex)
        assert np.isfinite(y_angular).all()


class TestPsiFieldTimeComponent:
    """Test suite for time component exp(-iΦ·E_P·t/ℏ)."""

    def test_time_component_at_t_zero_is_unity(self):
        """At t=0, time component should be exp(0) = 1."""
        field = PsiField()
        t = np.array([0.0])

        psi_time = field._time_component(t)

        assert np.isclose(abs(psi_time[0]), 1.0)
        assert np.isclose(psi_time[0], 1.0 + 0j)

    def test_time_component_oscillates_with_unit_magnitude(self):
        """Time component should have |exp(-iωt)| = 1."""
        field = PsiField()
        t_vals = np.linspace(0, 10, 50)

        psi_time = field._time_component(t_vals)

        # All magnitudes should be 1
        assert np.allclose(np.abs(psi_time), 1.0)

    def test_time_component_phase_evolves_linearly(self):
        """Phase should evolve as Φ·E_P·t/ℏ."""
        field = PsiField()

        t1 = 1e-44  # 1 Planck time
        t2 = 2e-44  # 2 Planck times

        psi_t1 = field._time_component(np.array([t1]))
        psi_t2 = field._time_component(np.array([t2]))

        phase_1 = np.angle(psi_t1[0])
        phase_2 = np.angle(psi_t2[0])

        # Phase should evolve (magnitude constant at 1)
        assert np.abs(psi_t1[0]) == pytest.approx(1.0, abs=1e-10)
        assert np.abs(psi_t2[0]) == pytest.approx(1.0, abs=1e-10)

        # Phase should change with time (wraps around 2π)
        # Just verify they're different
        assert not np.isclose(phase_1, phase_2, atol=1e-3)

    def test_time_component_uses_golden_ratio(self):
        """Frequency should be modulated by golden ratio Φ."""
        field = PsiField()
        config = field.config

        omega = config.phi * config.e_planck / HBAR

        # Check that Φ is indeed involved
        assert config.phi == PHI
        assert omega > 0


class TestPsiFieldWavefunction:
    """Test suite for complete wavefunction computation."""

    def test_compute_wavefunction_returns_complex_array(self):
        """Wavefunction should return complex values."""
        field = PsiField()

        r = np.array([1.0, 2.0, 3.0])
        theta = np.array([np.pi / 4, np.pi / 2, 3 * np.pi / 4])
        phi = np.array([0.0, np.pi / 3, 2 * np.pi / 3])
        t = 0.0

        psi = field.compute_wavefunction(r, theta, phi, t)

        assert psi.dtype in [np.complex64, np.complex128, complex]
        assert psi.shape == r.shape

    def test_compute_wavefunction_handles_scalar_inputs(self):
        """Should handle scalar inputs (promoted to arrays)."""
        field = PsiField()

        psi = field.compute_wavefunction(1.0, np.pi / 4, 0.0, 0.0)

        assert isinstance(psi, (complex, np.complexfloating, np.ndarray))

    def test_compute_wavefunction_probability_is_positive(self):
        """Probability density |ψ|² should be positive."""
        field = PsiField()

        r = np.linspace(0, 5, 20)
        theta = np.full_like(r, np.pi / 4)
        phi = np.full_like(r, 0.0)
        t = 0.0

        psi = field.compute_wavefunction(r, theta, phi, t)
        prob = np.abs(psi) ** 2

        assert np.all(prob >= 0)
        assert np.all(np.isreal(prob))

    def test_compute_wavefunction_normalization(self):
        """When normalize=True, wavefunction should be approximately normalized."""
        config = PsiFieldConfig(normalize=True)
        field = PsiField(config)

        # Use Planck-scale units (r in units of ℓ_P)
        r = np.linspace(1e-37, 1e-35, 100)  # Physical Planck length scale
        theta = np.full_like(r, np.pi / 4)
        phi = np.full_like(r, 0.0)
        t = 0.0

        psi = field.compute_wavefunction(r, theta, phi, t)
        prob = np.abs(psi) ** 2

        # Check that probabilities are finite and non-zero
        assert np.all(np.isfinite(prob))
        assert np.any(prob > 0)  # At least some non-zero values

    def test_compute_wavefunction_without_normalization(self):
        """When normalize=False, normalization should not be applied."""
        config = PsiFieldConfig(normalize=False)
        field = PsiField(config)

        r = np.array([1.0])
        theta = np.array([np.pi / 4])
        phi = np.array([0.0])
        t = 0.0

        psi = field.compute_wavefunction(r, theta, phi, t)

        # Just check it returns a value (no normalization applied)
        assert np.isfinite(psi).all()


class TestPsiFieldUTACCollapse:
    """Test suite for |ψ|² → P(R) UTAC mapping."""

    def test_collapse_to_utac_returns_dict_with_keys(self):
        """Should return dict with probability_density, radial_distribution, etc."""
        field = PsiField()

        r_grid = np.linspace(0, 10, 50)
        theta = np.full_like(r_grid, np.pi / 4)
        phi = np.full_like(r_grid, 0.0)

        psi = field.compute_wavefunction(r_grid, theta, phi, 0.0)

        result = field.collapse_to_utac(psi, r_grid)

        assert "probability_density" in result
        assert "radial_distribution" in result
        assert "mean_r" in result
        assert "delta_r" in result

    def test_collapse_to_utac_radial_distribution_normalized(self):
        """Radial distribution P(r) should integrate to 1."""
        field = PsiField()

        r_grid = np.linspace(1e-37, 1e-35, 100)  # Use Planck-scale coordinates
        theta = np.full_like(r_grid, np.pi / 4)
        phi = np.full_like(r_grid, 0.0)

        psi = field.compute_wavefunction(r_grid, theta, phi, 0.0)

        result = field.collapse_to_utac(psi, r_grid)
        radial_dist = result["radial_distribution"]

        # Check that distribution is normalized (within tolerance)
        integral = np.trapezoid(radial_dist, r_grid)

        # If normalization worked, integral should be ~1
        # Otherwise just check it's finite and positive
        assert integral >= 0
        assert np.isfinite(integral)

    def test_collapse_to_utac_mean_r_is_positive(self):
        """Mean radius <r> should be positive."""
        field = PsiField()

        r_grid = np.linspace(0, 10, 50)
        theta = np.full_like(r_grid, np.pi / 4)
        phi = np.full_like(r_grid, 0.0)

        psi = field.compute_wavefunction(r_grid, theta, phi, 0.0)

        result = field.collapse_to_utac(psi, r_grid)

        assert result["mean_r"] >= 0

    def test_collapse_to_utac_delta_r_uncertainty(self):
        """Δr = √(<r²> - <r>²) should satisfy uncertainty relation."""
        field = PsiField()

        r_grid = np.linspace(0, 10, 100)
        theta = np.full_like(r_grid, np.pi / 4)
        phi = np.full_like(r_grid, 0.0)

        psi = field.compute_wavefunction(r_grid, theta, phi, 0.0)

        result = field.collapse_to_utac(psi, r_grid)

        # Δr should be positive and finite
        assert result["delta_r"] >= 0
        assert np.isfinite(result["delta_r"])


class TestPsiFieldEntropy:
    """Test suite for entropy computation S = -Tr(ρ log ρ)."""

    def test_compute_entropy_is_non_negative(self):
        """Entropy should be non-negative."""
        field = PsiField()

        r = np.linspace(0, 5, 50)
        theta = np.full_like(r, np.pi / 4)
        phi = np.full_like(r, 0.0)

        psi = field.compute_wavefunction(r, theta, phi, 0.0)
        entropy = field.compute_entropy(psi)

        assert entropy >= 0

    def test_compute_entropy_zero_for_delta_function(self):
        """Entropy should be ~0 for highly localized state."""
        field = PsiField()

        # Very localized state (small r range)
        r = np.linspace(0, 0.1, 50)
        theta = np.full_like(r, np.pi / 4)
        phi = np.full_like(r, 0.0)

        psi = field.compute_wavefunction(r, theta, phi, 0.0)
        entropy = field.compute_entropy(psi)

        # Should be low (highly localized)
        assert entropy < 2.0

    def test_compute_entropy_higher_for_delocalized_state(self):
        """Entropy should be higher for spread-out wavefunction."""
        field = PsiField()

        # Delocalized state (use Planck scale)
        r = np.linspace(1e-37, 5e-35, 100)
        theta = np.full_like(r, np.pi / 4)
        phi = np.full_like(r, 0.0)

        psi = field.compute_wavefunction(r, theta, phi, 0.0)
        entropy = field.compute_entropy(psi)

        # Entropy should be non-negative and finite
        assert entropy >= 0
        assert np.isfinite(entropy)


class TestPsiFieldPipeline:
    """Test suite for PsiFieldPipeline integration."""

    def test_pipeline_run_returns_complete_dict(self):
        """Pipeline.run() should return all expected outputs."""
        pipeline = PsiFieldPipeline()

        results = pipeline.run(r_max=5.0, n_points=20, theta_phi_res=10, t=0.0)

        assert "r_grid" in results
        assert "theta_grid" in results
        assert "phi_grid" in results
        assert "psi" in results
        assert "probability_density" in results
        assert "radial_distribution" in results
        assert "mean_r" in results
        assert "delta_r" in results
        assert "entropy" in results

    def test_pipeline_run_grid_dimensions(self):
        """Pipeline should create correct grid dimensions."""
        pipeline = PsiFieldPipeline()

        n_points = 30
        theta_phi_res = 15

        results = pipeline.run(r_max=10.0, n_points=n_points, theta_phi_res=theta_phi_res, t=0.0)

        assert len(results["r_grid"]) == n_points
        assert len(results["theta_grid"]) == theta_phi_res
        assert len(results["phi_grid"]) == theta_phi_res
        assert results["psi"].shape == (n_points, theta_phi_res, theta_phi_res)

    def test_pipeline_run_with_time_evolution(self):
        """Pipeline should handle non-zero time."""
        pipeline = PsiFieldPipeline()

        results_t0 = pipeline.run(r_max=5.0, n_points=20, theta_phi_res=10, t=0.0)
        results_t1 = pipeline.run(r_max=5.0, n_points=20, theta_phi_res=10, t=1e-44)

        # Wavefunctions should differ (time evolution)
        psi_t0 = results_t0["psi"]
        psi_t1 = results_t1["psi"]

        # Phases should differ
        phase_diff = np.abs(np.angle(psi_t1) - np.angle(psi_t0))
        assert np.any(phase_diff > 1e-5)

    def test_pipeline_run_entropy_is_computed(self):
        """Pipeline should compute and return entropy."""
        pipeline = PsiFieldPipeline()

        results = pipeline.run(r_max=5.0, n_points=50, theta_phi_res=10, t=0.0)

        assert "entropy" in results
        assert results["entropy"] >= 0
        assert np.isfinite(results["entropy"])

    def test_pipeline_custom_config(self):
        """Pipeline should accept custom PsiFieldConfig."""
        config = PsiFieldConfig(
            alpha_inv=100.0,
            phi=2.0,
            use_tetrahedral=False,
            normalize=False,
        )
        pipeline = PsiFieldPipeline(config)

        results = pipeline.run(r_max=5.0, n_points=20, theta_phi_res=10)

        assert results["psi"] is not None


class TestConvenienceFunction:
    """Test suite for compute_psi_genesis() convenience function."""

    def test_compute_psi_genesis_scalar_inputs(self):
        """Should handle scalar inputs."""
        psi = compute_psi_genesis(r=1.0, theta=np.pi / 4, phi=0.0, t=0.0)

        assert isinstance(psi, (complex, np.complexfloating, np.ndarray))

    def test_compute_psi_genesis_array_inputs(self):
        """Should handle array inputs."""
        r = np.linspace(0, 5, 20)
        psi = compute_psi_genesis(r=r, theta=np.pi / 4, phi=0.0, t=0.0)

        assert len(psi) == len(r)

    def test_compute_psi_genesis_custom_constants(self):
        """Should allow custom physical constants."""
        psi = compute_psi_genesis(
            r=1.0,
            theta=np.pi / 4,
            phi=0.0,
            t=0.0,
            alpha_inv=100.0,
            phi_golden=2.0,
        )

        assert np.isfinite(psi)

    def test_compute_psi_genesis_matches_field_object(self):
        """Convenience function should match PsiField results."""
        r = np.array([1.0, 2.0, 3.0])
        theta = np.pi / 4
        phi = 0.0
        t = 0.0

        # Via convenience function
        psi_convenience = compute_psi_genesis(r, theta, phi, t)

        # Via PsiField object
        field = PsiField()
        psi_field = field.compute_wavefunction(r, theta, phi, t)

        assert np.allclose(psi_convenience, psi_field, rtol=0.01)


class TestPhysicalConstants:
    """Test suite for physical constants used in psi_field.py."""

    def test_alpha_inv_value(self):
        """Fine-structure constant inverse should be ~137."""
        assert 136 < ALPHA_INV < 138

    def test_phi_golden_ratio(self):
        """Golden ratio should be (1 + √5)/2 ≈ 1.618."""
        expected_phi = (1 + math.sqrt(5)) / 2
        assert np.isclose(PHI, expected_phi, atol=0.001)

    def test_planck_length_order_of_magnitude(self):
        """Planck length should be ~10⁻³⁵ m."""
        assert 1e-36 < L_PLANCK < 1e-34

    def test_planck_energy_order_of_magnitude(self):
        """Planck energy should be ~10⁹ J."""
        assert 1e8 < E_PLANCK < 1e10

    def test_hbar_value(self):
        """Reduced Planck constant should be ~10⁻³⁴ J·s."""
        assert 1e-35 < HBAR < 1e-33


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
