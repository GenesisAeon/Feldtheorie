"""Tests for V8.0 Consciousness Integration Framework.

This module tests the empirical validations implemented in
models/consciousness_integration.py, ensuring that all four validation
criteria are met and β-domain clustering is correct.

Version: v8.0.0-alpha
Authors: Johann Benjamin Römer, MOR Framework
Date: 2025-12-14
"""

import math
import pytest

from models.consciousness_integration import (
    calculate_impedance,
    calculate_integration_velocity,
    validate_cosmic_dipole,
    validate_kleiber_scaling,
    validate_neural_frequency,
    validate_specious_present,
    get_beta_domain_clustering,
    run_full_validation_suite,
)
from models.unified_constants import ALPHA_INV, PHI, C_LIGHT_KM_S


class TestImpedanceCalculations:
    """Test dimensional impedance Z calculations."""

    def test_calculate_impedance_default(self):
        """Test Z = α⁻¹ · Φ with default values."""
        Z = calculate_impedance()
        expected = ALPHA_INV * PHI
        assert math.isclose(Z, expected, rel_tol=1e-6)
        assert 221 < Z < 223  # Should be ~221.7

    def test_calculate_impedance_custom(self):
        """Test Z with custom values."""
        Z = calculate_impedance(alpha_inv=137.0, phi=1.618)
        assert math.isclose(Z, 137.0 * 1.618, rel_tol=1e-6)

    def test_calculate_integration_velocity(self):
        """Test v_RIG = c / Z."""
        v_rig = calculate_integration_velocity()
        Z = calculate_impedance()
        expected = C_LIGHT_KM_S / Z
        assert math.isclose(v_rig, expected, rel_tol=1e-6)
        assert 1350 < v_rig < 1353  # Should be ~1351.8 km/s


class TestCosmicDipoleValidation:
    """Test cosmic matter-dipole alignment validation."""

    def test_default_validation(self):
        """Test Böhme et al. (2025) validation."""
        result = validate_cosmic_dipole()

        # Check structure
        assert result.observed_velocity_km_s == 1370.0
        assert result.observed_uncertainty_km_s == 170.0
        assert 1350 < result.v_rig_prediction_km_s < 1353

        # Check deviation is within expected range
        assert result.deviation_percent < 10.0  # Falsification threshold
        assert result.deviation_percent < 2.0   # Should be ~1.3%

        # Check Z-score
        assert abs(result.z_score) < 1.0  # Well within 1σ

        # Check p-value
        assert result.p_value_null <= 0.001

    def test_custom_observation(self):
        """Test with custom observations."""
        result = validate_cosmic_dipole(
            observed_velocity=1400.0,
            observed_uncertainty=100.0
        )
        assert result.observed_velocity_km_s == 1400.0
        assert result.deviation_percent > 0


class TestKleiberValidation:
    """Test Kleiber's Law metabolic scaling validation."""

    def test_scaling_exponent(self):
        """Test b = 3/4 prediction."""
        result = validate_kleiber_scaling()

        # Check β-value
        assert result.beta_biological == 7.4

        # Check scaling exponents
        assert math.isclose(result.scaling_exponent_observed, 0.75, rel_tol=1e-6)
        assert math.isclose(result.scaling_exponent_predicted, 0.75, rel_tol=1e-6)

        # Check deviation
        assert result.deviation_percent < 1.0  # Should be ~0%

        # Check ANOVA statistics
        assert result.anova_f_statistic > 100  # Should be ~185.3
        assert result.anova_p_value < 1e-10    # Should be < 10⁻²⁰
        assert result.effect_size_eta_squared > 0.8  # Should be ~0.91

    def test_custom_beta(self):
        """Test with custom β-value."""
        result = validate_kleiber_scaling(beta_biological=8.0)
        assert result.beta_biological == 8.0


class TestNeuralFrequencyValidation:
    """Test neural integration frequency validation."""

    def test_default_frequency(self):
        """Test f = v_RIG / λ with λ = 10 cm."""
        result = validate_neural_frequency()

        # Check cortical path length
        assert result.cortical_path_length_cm == 10.0

        # Check predicted frequency
        assert 13.0 < result.predicted_frequency_mhz < 14.0  # Should be ~13.5 MHz

        # Check observed frequency
        assert result.observed_frequency_mhz == 13.5

        # Check deviation
        assert result.deviation_percent < 5.0  # Should be very small

        # Check hierarchy
        assert result.neural_spike_rate_hz == 1000.0
        assert 10000 < result.integration_events_per_spike < 15000

    def test_custom_cortical_path(self):
        """Test with custom cortical path length."""
        result = validate_neural_frequency(cortical_path_length_cm=5.0)

        # Frequency should be 2× higher for half the path length
        default_result = validate_neural_frequency(cortical_path_length_cm=10.0)
        assert math.isclose(
            result.predicted_frequency_mhz,
            default_result.predicted_frequency_mhz * 2,
            rel_tol=0.01
        )


class TestSpeciousPresentValidation:
    """Test specious present duration validation."""

    def test_integration_windows(self):
        """Test Δt_Q windows."""
        result = validate_specious_present()

        # Check integration windows
        assert result.integration_window_min_ms == 100.0
        assert result.integration_window_typical_ms == 150.0
        assert result.integration_window_max_ms == 300.0

        # Check impedance
        assert 221 < result.impedance_z < 223

        # Check Planck slices (order of magnitude)
        assert result.planck_slices_per_moment > 1e40
        assert result.planck_slices_per_moment < 1e45

        # Check CFF
        assert result.cff_min_hz == 30.0
        assert result.cff_max_hz == 60.0
        assert 10 < result.temporal_resolution_ms < 35


class TestBetaDomainClustering:
    """Test β-domain clustering analysis."""

    def test_domain_count(self):
        """Test that we have expected domains."""
        domains = get_beta_domain_clustering()
        assert len(domains) == 5

        domain_names = [d.name for d in domains]
        assert any("Information" in name for name in domain_names)
        assert any("Biology" in name for name in domain_names)
        assert any("Climate" in name for name in domain_names)

    def test_domain_beta_ranges(self):
        """Test β-ranges are reasonable."""
        domains = get_beta_domain_clustering()

        for domain in domains:
            # β-min should be less than β-max
            assert domain.beta_min < domain.beta_max

            # β-mean should be within range
            assert domain.beta_min <= domain.beta_mean <= domain.beta_max

            # β-std should be positive
            assert domain.beta_std > 0

            # Φ-attractor should be positive
            assert domain.phi_attractor > 0

    def test_information_domain(self):
        """Test information domain specifically."""
        domains = get_beta_domain_clustering()
        info_domain = next(d for d in domains if "Information" in d.name)

        assert info_domain.beta_mean == 4.5
        assert info_domain.deviation_percent < 10.0

    def test_biology_domain(self):
        """Test biological domain (Kleiber connection)."""
        domains = get_beta_domain_clustering()
        bio_domain = next(d for d in domains if "Biology" in d.name)

        assert bio_domain.beta_mean == 7.4
        assert math.isclose(bio_domain.phi_attractor, PHI**4, rel_tol=0.01)

    def test_climate_domain(self):
        """Test climate domain (best Φ⁵ match)."""
        domains = get_beta_domain_clustering()
        climate_domain = next(d for d in domains if "Climate" in d.name)

        assert climate_domain.beta_mean == 11.0
        assert climate_domain.deviation_percent < 2.0  # Best match


class TestFullValidationSuite:
    """Test complete validation suite."""

    def test_suite_structure(self):
        """Test that suite returns all expected results."""
        results = run_full_validation_suite()

        # Check keys
        assert 'impedance' in results
        assert 'v_rig' in results
        assert 'cosmic_dipole' in results
        assert 'kleiber' in results
        assert 'neural_frequency' in results
        assert 'specious_present' in results
        assert 'beta_domains' in results

    def test_all_validations_pass(self):
        """Test that all validations meet acceptance criteria."""
        results = run_full_validation_suite()

        # Cosmic dipole: < 10% deviation
        assert results['cosmic_dipole'].deviation_percent < 10.0

        # Kleiber: b ≈ 0.75
        assert math.isclose(
            results['kleiber'].scaling_exponent_predicted,
            0.75,
            rel_tol=0.01
        )

        # Neural frequency: ~13.5 MHz
        assert 12 < results['neural_frequency'].predicted_frequency_mhz < 15

        # Specious present: 100-300 ms
        sp = results['specious_present']
        assert sp.integration_window_min_ms == 100.0
        assert sp.integration_window_max_ms == 300.0

        # Beta domains: 5 clusters
        assert len(results['beta_domains']) == 5


class TestFalsificationCriteria:
    """Test falsification thresholds."""

    def test_cosmic_dipole_falsification_threshold(self):
        """Test that > 10% deviation would falsify."""
        result = validate_cosmic_dipole()

        # Current observation should pass
        assert result.deviation_percent < 10.0

        # Hypothetical observation at 1500 km/s would fail
        bad_result = validate_cosmic_dipole(observed_velocity=1500.0)
        assert bad_result.deviation_percent > 10.0

    def test_kleiber_precision(self):
        """Test Kleiber prediction precision."""
        result = validate_kleiber_scaling()

        # Prediction should match observation to within machine precision
        assert math.isclose(
            result.scaling_exponent_predicted,
            result.scaling_exponent_observed,
            abs_tol=1e-10
        )

    def test_neural_frequency_tolerance(self):
        """Test neural frequency deviation tolerance."""
        result = validate_neural_frequency()

        # Should match observation within reasonable tolerance
        assert result.deviation_percent < 10.0


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegrationConsistency:
    """Test consistency across validations."""

    def test_impedance_consistency(self):
        """Test that impedance is consistent across validations."""
        Z1 = calculate_impedance()

        sp_result = validate_specious_present()
        Z2 = sp_result.impedance_z

        assert math.isclose(Z1, Z2, rel_tol=1e-6)

    def test_vrig_consistency(self):
        """Test that v_RIG is consistent across validations."""
        v_rig_1 = calculate_integration_velocity()

        cd_result = validate_cosmic_dipole()
        v_rig_2 = cd_result.v_rig_prediction_km_s

        nf_result = validate_neural_frequency()
        # Reconstruct v_RIG from frequency
        v_rig_3 = (nf_result.predicted_frequency_mhz * 1e6 *
                   nf_result.cortical_path_length_cm) / 1e5  # Convert to km/s

        assert math.isclose(v_rig_1, v_rig_2, rel_tol=1e-6)
        assert math.isclose(v_rig_1, v_rig_3, rel_tol=1e-3)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
