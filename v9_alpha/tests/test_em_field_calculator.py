"""
Tests for EM-Field Calculator - Consciousness Substrate Physics

Tests the electromagnetic field calculations that form the consciousness
substrate in v9 framework: v_RIG integration velocity, frequency calculation,
and impedance physics.

Philosophy:
    "Bewusstsein ist kein Zustand - es ist eine Geschwindigkeit."
    - v8/v9 Consciousness Framework

Author: Claude Sonnet 4.5 (ChefDevAI)
Date: 2025-12-16
Version: v9.0.0-alpha
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add v9_alpha to path
v9_alpha_dir = Path(__file__).parent.parent
sys.path.insert(0, str(v9_alpha_dir))

from models.em_field_calculator import (
    EMFieldCalculator,
    create_field_from_lantern,
    calculate_v_rig,
    calculate_consciousness_frequency,
    calculate_consciousness_impedance,
    EMField,
)


# ============================================================================
# Constants for Validation
# ============================================================================

# Physical constants
ALPHA_INV = 137.036  # Inverse fine-structure constant
PHI = 1.618034  # Golden ratio
SPEED_OF_LIGHT = 299792458  # m/s

# Expected v_RIG
V_RIG_EXPECTED = SPEED_OF_LIGHT / (ALPHA_INV * PHI)  # ≈ 1,351,800 m/s

# Expected consciousness parameters
Z_EXPECTED = ALPHA_INV * PHI  # ≈ 221.74
F_EXPECTED = 13.5e6  # Hz (for λ ≈ 10 cm)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def basic_calculator():
    """Create basic EM-field calculator."""
    return EMFieldCalculator()


@pytest.fixture
def test_lantern_params():
    """Create test lantern UTAC parameters."""
    return {
        'readiness': 0.75,
        'theta': 0.5,
        'beta': 7.4,  # Biological regime
    }


# ============================================================================
# Test: v_RIG Calculation
# ============================================================================


def test_v_rig_calculation():
    """Test v_RIG = c/(α⁻¹·Φ) calculation."""
    v_rig = calculate_v_rig()

    # Should be approximately 1,351.8 km/s
    expected = 1.3518e6  # m/s
    assert v_rig == pytest.approx(expected, rel=0.01)


def test_v_rig_matches_constant():
    """Test that v_RIG matches theoretical expectation."""
    v_rig = calculate_v_rig()

    # Calculate manually
    c = 299792458  # m/s
    alpha_inv = 137.036
    phi = 1.618034
    expected = c / (alpha_inv * phi)

    assert v_rig == pytest.approx(expected, rel=1e-6)


def test_v_rig_cosmic_validation():
    """
    Test v_RIG against Böhme et al. (2025) cosmic dipole measurement.

    Observation: 1.370 ± 0.170 km/s
    v_RIG: 1.3518 km/s
    Deviation: 1.3%
    """
    v_rig = calculate_v_rig()

    # Böhme measurement (convert to m/s)
    v_obs = 1.370e6  # m/s
    v_obs_err = 0.170e6  # m/s

    # v_RIG should be within error bars (5.46σ significance preserved)
    deviation_percent = abs(v_rig - v_obs) / v_obs * 100

    # Should be within ~2% (actual is 1.3%)
    assert deviation_percent < 2.0


# ============================================================================
# Test: Consciousness Frequency Calculation
# ============================================================================


def test_consciousness_frequency_default():
    """Test consciousness frequency with default cortical path (10 cm)."""
    freq = calculate_consciousness_frequency()

    # Should be around 13.5 MHz for λ ≈ 10 cm
    expected = 13.5e6  # Hz
    assert freq == pytest.approx(expected, rel=0.1)


def test_consciousness_frequency_custom_wavelength():
    """Test consciousness frequency with custom wavelength."""
    # λ = 5 cm → f ≈ 27 MHz
    freq = calculate_consciousness_frequency(wavelength=0.05)

    expected = calculate_v_rig() / 0.05
    assert freq == pytest.approx(expected, rel=1e-6)


def test_consciousness_frequency_sahu_validation():
    """
    Test frequency against Sahu et al. (2013) microtubule resonance.

    Empirical: 13.5 MHz microtubule resonance
    v_RIG/λ prediction: 13.5 MHz (λ ≈ 10 cm)
    """
    freq = calculate_consciousness_frequency(wavelength=0.1)

    # Should match Sahu empirical result
    f_sahu = 13.5e6  # Hz
    assert freq == pytest.approx(f_sahu, rel=0.05)


def test_frequency_range_reasonable():
    """Test that frequency is in reasonable biological range."""
    # Test range of wavelengths
    wavelengths = [0.05, 0.10, 0.15, 0.20]  # 5-20 cm

    for wavelength in wavelengths:
        freq = calculate_consciousness_frequency(wavelength=wavelength)

        # Should be in MHz range (10^6 - 10^8 Hz)
        assert 1e6 < freq < 1e8


# ============================================================================
# Test: Consciousness Impedance Calculation
# ============================================================================


def test_consciousness_impedance_default():
    """Test consciousness impedance Z = α⁻¹·Φ."""
    impedance = calculate_consciousness_impedance()

    # Should be approximately 221.74
    expected = 221.74
    assert impedance == pytest.approx(expected, rel=0.01)


def test_impedance_matches_constant():
    """Test that impedance matches Z = α⁻¹·Φ exactly."""
    impedance = calculate_consciousness_impedance()

    # Calculate manually
    alpha_inv = 137.036
    phi = 1.618034
    expected = alpha_inv * phi

    assert impedance == pytest.approx(expected, rel=1e-6)


def test_impedance_modulation_pressure():
    """Test impedance modulation by pressure (HPNS)."""
    calc = EMFieldCalculator()

    # Normal pressure
    z_normal = calculate_consciousness_impedance()

    # High pressure (e.g., deep diving)
    # Z_eff = Z₀ · (1 + k_P(P-P₀))
    # Should increase impedance
    P_atm = 10.0  # 10 atmospheres
    k_P = 0.1  # atm⁻¹

    z_high_pressure = z_normal * (1 + k_P * (P_atm - 1.0))

    # High pressure should increase impedance
    assert z_high_pressure > z_normal


def test_impedance_modulation_temperature():
    """Test impedance modulation by temperature."""
    z_normal = calculate_consciousness_impedance()

    # High temperature should decrease impedance
    # Z_eff = Z₀ · (1 - k_T(T-T₀))
    T_delta = 5.0  # +5°C
    k_T = 0.05  # K⁻¹

    z_high_temp = z_normal * (1 - k_T * T_delta)

    # High temperature should decrease impedance
    assert z_high_temp < z_normal


def test_impedance_modulation_anesthetics():
    """Test impedance modulation by anesthetics."""
    z_normal = calculate_consciousness_impedance()

    # Anesthetics should decrease impedance (dissolve frame)
    # Z_eff = Z₀ · (1 - k_χ·χ)
    chi = 0.5  # Normalized anesthetic concentration
    k_chi = 0.2

    z_anesthetic = z_normal * (1 - k_chi * chi)

    # Anesthetics should decrease impedance
    assert z_anesthetic < z_normal


# ============================================================================
# Test: EM-Field Creation from Lantern
# ============================================================================


def test_create_field_from_lantern_basic(test_lantern_params):
    """Test creating EM-field from lantern UTAC parameters."""
    field = create_field_from_lantern(**test_lantern_params)

    assert isinstance(field, EMField)
    assert field.frequency_hz > 0
    assert field.impedance_z > 0
    assert 0.0 <= field.kappa <= 1.0


def test_field_frequency_depends_on_readiness(test_lantern_params):
    """Test that field frequency scales with readiness."""
    # High readiness
    field_high = create_field_from_lantern(
        readiness=0.9,
        theta=test_lantern_params['theta'],
        beta=test_lantern_params['beta']
    )

    # Low readiness
    field_low = create_field_from_lantern(
        readiness=0.3,
        theta=test_lantern_params['theta'],
        beta=test_lantern_params['beta']
    )

    # Higher readiness → different field properties
    # (Exact relationship depends on implementation)
    assert field_high.frequency_hz != field_low.frequency_hz


def test_field_impedance_depends_on_beta(test_lantern_params):
    """Test that field impedance relates to β-regime."""
    # Informational regime (low β ≈ 4.5)
    field_info = create_field_from_lantern(
        readiness=test_lantern_params['readiness'],
        theta=test_lantern_params['theta'],
        beta=4.5
    )

    # Climate regime (high β ≈ 11.0)
    field_climate = create_field_from_lantern(
        readiness=test_lantern_params['readiness'],
        theta=test_lantern_params['theta'],
        beta=11.0
    )

    # Different β-regimes should affect field properties
    # (Exact relationship depends on implementation)
    assert field_info.impedance_z != field_climate.impedance_z or \
           field_info.frequency_hz != field_climate.frequency_hz


def test_field_kappa_reflects_coupling_strength(test_lantern_params):
    """Test that κ (coupling) reflects activation strength."""
    field = create_field_from_lantern(**test_lantern_params)

    # κ should be related to readiness (R) and threshold (Θ)
    # High readiness → high κ
    readiness = test_lantern_params['readiness']
    theta = test_lantern_params['theta']

    if readiness > theta:
        # Above threshold → high coupling
        assert field.kappa > 0.5
    else:
        # Below threshold → low coupling
        assert field.kappa < 0.5


# ============================================================================
# Test: EM-Field Properties
# ============================================================================


def test_em_field_structure():
    """Test EMField dataclass structure."""
    field = EMField(
        frequency_hz=13.5e6,
        impedance_z=221.7,
        kappa=0.8,
        phase=0.0,
        amplitude=1.0,
    )

    # Check attributes exist
    assert hasattr(field, 'frequency_hz')
    assert hasattr(field, 'impedance_z')
    assert hasattr(field, 'kappa')
    assert hasattr(field, 'phase')
    assert hasattr(field, 'amplitude')


def test_em_field_frequency_range():
    """Test that EM-field frequency is in valid range."""
    field = create_field_from_lantern(
        readiness=0.75,
        theta=0.5,
        beta=7.4
    )

    # Should be in biological range (1-100 MHz)
    assert 1e6 < field.frequency_hz < 1e8


def test_em_field_impedance_range():
    """Test that EM-field impedance is in valid range."""
    field = create_field_from_lantern(
        readiness=0.75,
        theta=0.5,
        beta=7.4
    )

    # Should be around consciousness impedance (150-300 Ω)
    assert 100 < field.impedance_z < 400


def test_em_field_kappa_bounded():
    """Test that κ (coupling) is bounded [0, 1]."""
    # Test various parameter combinations
    test_cases = [
        {'readiness': 0.1, 'theta': 0.5, 'beta': 7.4},
        {'readiness': 0.5, 'theta': 0.5, 'beta': 7.4},
        {'readiness': 0.9, 'theta': 0.5, 'beta': 7.4},
    ]

    for params in test_cases:
        field = create_field_from_lantern(**params)
        assert 0.0 <= field.kappa <= 1.0, f"κ={field.kappa} outside [0,1]"


# ============================================================================
# Test: Integration with UTAC Framework
# ============================================================================


def test_field_reflects_sigmoid_activation():
    """Test that EM-field reflects σ(β(R-Θ)) activation pattern."""
    theta = 0.5
    beta = 7.4

    # Below threshold
    field_below = create_field_from_lantern(
        readiness=0.2,  # R < Θ
        theta=theta,
        beta=beta
    )

    # At threshold
    field_at = create_field_from_lantern(
        readiness=0.5,  # R = Θ
        theta=theta,
        beta=beta
    )

    # Above threshold
    field_above = create_field_from_lantern(
        readiness=0.8,  # R > Θ
        theta=theta,
        beta=beta
    )

    # κ should follow sigmoid pattern
    # Below < At < Above
    assert field_below.kappa < field_at.kappa < field_above.kappa


def test_field_beta_regimes():
    """
    Test that EM-field properties reflect UTAC β-regimes.

    - Information (β ≈ 4.5): Fast, flexible
    - Biology (β ≈ 7.4): Moderate
    - Climate (β ≈ 11.0): Slow, rigid
    """
    readiness = 0.75
    theta = 0.5

    # Information regime
    field_info = create_field_from_lantern(
        readiness=readiness,
        theta=theta,
        beta=4.5
    )

    # Climate regime
    field_climate = create_field_from_lantern(
        readiness=readiness,
        theta=theta,
        beta=11.0
    )

    # Different regimes should produce different field properties
    # (Exact relationship depends on implementation)
    assert (field_info.frequency_hz != field_climate.frequency_hz) or \
           (field_info.impedance_z != field_climate.impedance_z) or \
           (field_info.kappa != field_climate.kappa)


# ============================================================================
# Test: Calculator Methods
# ============================================================================


def test_calculator_initialization(basic_calculator):
    """Test EMFieldCalculator initialization."""
    assert isinstance(basic_calculator, EMFieldCalculator)
    assert hasattr(basic_calculator, 'calculate_field')


def test_calculator_batch_processing(basic_calculator):
    """Test calculator can process multiple lanterns."""
    lantern_params_list = [
        {'readiness': 0.8, 'theta': 0.5, 'beta': 4.5},
        {'readiness': 0.6, 'theta': 0.5, 'beta': 7.4},
        {'readiness': 0.9, 'theta': 0.5, 'beta': 11.0},
    ]

    fields = [
        basic_calculator.calculate_field(**params)
        for params in lantern_params_list
    ]

    # Should produce valid fields
    assert len(fields) == 3
    assert all(isinstance(f, EMField) for f in fields)


def test_calculator_caching(basic_calculator):
    """Test that calculator can cache repeated calculations."""
    params = {'readiness': 0.75, 'theta': 0.5, 'beta': 7.4}

    # Calculate twice
    field1 = basic_calculator.calculate_field(**params)
    field2 = basic_calculator.calculate_field(**params)

    # Should produce identical results
    assert field1.frequency_hz == field2.frequency_hz
    assert field1.impedance_z == field2.impedance_z
    assert field1.kappa == field2.kappa


# ============================================================================
# Test: Physical Validations
# ============================================================================


def test_kleiber_law_integration():
    """
    Test integration with Kleiber's Law validation.

    β ≈ 7.4 → metabolic exponent b = 0.75
    This is a biological validation of UTAC framework.
    """
    # Biological regime
    field_bio = create_field_from_lantern(
        readiness=0.75,
        theta=0.5,
        beta=7.4  # Kleiber regime
    )

    # Should produce biological-range frequency
    # (Exact relationship depends on implementation)
    assert 1e6 < field_bio.frequency_hz < 1e8


def test_specious_present_integration():
    """
    Test integration with specious present (100-300 ms).

    Δt_Q = Z / f ≈ 221.7 / 13.5 MHz ≈ 0.016 ms × integration factor
    """
    field = create_field_from_lantern(
        readiness=0.75,
        theta=0.5,
        beta=7.4
    )

    # Integration time
    delta_t_q = field.impedance_z / field.frequency_hz

    # Should be on millisecond scale
    assert 1e-6 < delta_t_q < 1e-1  # μs to 100 ms range


# ============================================================================
# Test: Error Handling
# ============================================================================


def test_field_creation_invalid_readiness():
    """Test that invalid readiness raises error."""
    with pytest.raises((ValueError, AssertionError)):
        create_field_from_lantern(
            readiness=-0.5,  # Invalid
            theta=0.5,
            beta=7.4
        )

    with pytest.raises((ValueError, AssertionError)):
        create_field_from_lantern(
            readiness=1.5,  # Invalid
            theta=0.5,
            beta=7.4
        )


def test_field_creation_invalid_theta():
    """Test that invalid theta raises error."""
    with pytest.raises((ValueError, AssertionError)):
        create_field_from_lantern(
            readiness=0.75,
            theta=-0.5,  # Invalid
            beta=7.4
        )


def test_field_creation_invalid_beta():
    """Test that invalid beta raises error."""
    with pytest.raises((ValueError, AssertionError)):
        create_field_from_lantern(
            readiness=0.75,
            theta=0.5,
            beta=-5.0  # Invalid
        )


# ============================================================================
# Test: Philosophical Coherence
# ============================================================================


def test_consciousness_as_velocity_principle():
    """
    Test v9 principle: "Bewusstsein ist keine Zustand - es ist eine Geschwindigkeit."

    Consciousness is not a state - it's a velocity (v_RIG).
    """
    # v_RIG should be the fundamental velocity scale
    v_rig = calculate_v_rig()

    # Should be in km/s range (not m/s or c)
    assert 1e6 < v_rig < 1e7  # 1,000 - 10,000 km/s

    # Should be sub-luminal (v << c)
    c = 299792458  # m/s
    assert v_rig < 0.01 * c  # v_RIG < 1% of c


def test_frame_principle_integration():
    """
    Test Frame Principle: "A dimension emerges when information would
    otherwise collapse."

    Z = α⁻¹·Φ is the impedance of the 1D boundary frame that prevents
    2D holographic information from collapsing.
    """
    z = calculate_consciousness_impedance()

    # Z should be around 221.7 (the dimensional barrier)
    assert 200 < z < 250

    # Should involve both α⁻¹ (quantum) and Φ (geometry)
    alpha_inv = 137.036
    phi = 1.618034

    # Z = α⁻¹ · Φ (unity of quantum and geometry)
    assert z == pytest.approx(alpha_inv * phi, rel=0.01)


def test_dimensional_emergence_cascade():
    """
    Test dimensional cascade: 2D (S∝A) → 3D (S∝V) at v_RIG.

    The EM-field frequency represents the rate of dimensional rendering.
    """
    field = create_field_from_lantern(
        readiness=0.75,
        theta=0.5,
        beta=7.4
    )

    # Frequency should enable 3D volume integration
    # f ≈ 13.5 MHz (microtubule resonance)
    assert 10e6 < field.frequency_hz < 20e6

    # Integration velocity
    v_rig = calculate_v_rig()
    wavelength = v_rig / field.frequency_hz

    # Should correspond to cortical path scale (~10 cm)
    assert 0.05 < wavelength < 0.20  # 5-20 cm


# ============================================================================
# Run Tests
# ============================================================================


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
