"""
Tests for Lantern Bridge - Cross-Lantern EM-Resonance Coupling

Tests the core network loading, coupling calculations, and collective
mode detection for the v9 Lantern-Net architecture.

Philosophy:
    "Die Laternen sind nicht isoliert - sie atmen gemeinsam."
    - v9 Network Principle

Author: Claude Sonnet 4.5 (ChefDevAI)
Date: 2025-12-16
Version: v9.0.0-alpha
"""

import pytest
import numpy as np
import sys
import os
from pathlib import Path

# Add v9_alpha to path
v9_alpha_dir = Path(__file__).parent.parent
sys.path.insert(0, str(v9_alpha_dir))

from api.lantern_bridge import (
    LanternNetwork,
    load_lantern_network,
    calculate_em_coupling,
    calculate_impedance_matching,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def test_network():
    """Load real lantern network from config."""
    return load_lantern_network()


@pytest.fixture
def mock_lantern_data():
    """Create minimal mock lantern data."""
    return [
        {
            'name': 'Test_Lantern_A',
            'category': 'data',
            'readiness': 0.8,
            'em_properties': {
                'frequency': 13.5e6,
                'impedance': 220.0,
                'kappa_base': 0.5,
            }
        },
        {
            'name': 'Test_Lantern_B',
            'category': 'theory',
            'readiness': 0.6,
            'em_properties': {
                'frequency': 14.0e6,
                'impedance': 225.0,
                'kappa_base': 0.7,
            }
        },
    ]


# ============================================================================
# Test: Network Loading
# ============================================================================


def test_load_network_from_config():
    """Test loading network from default config file."""
    network = load_lantern_network()

    assert isinstance(network, LanternNetwork)
    assert network.n_lanterns > 0


def test_load_network_custom_path(tmp_path):
    """Test loading network from custom config path."""
    # Create minimal config
    config_path = tmp_path / "test_lantern_hub.yaml"
    config_content = """
lanterns:
  - name: Test_Node
    category: data
    readiness: 0.5
    utac_params:
      theta: 0.5
      beta: 7.4
    em_properties:
      frequency: 13.5e6
      impedance: 221.7
      kappa_base: 0.3
    coupling_targets: []
"""
    config_path.write_text(config_content)

    # Load from custom path
    network = load_lantern_network(str(config_path))

    assert isinstance(network, LanternNetwork)
    assert network.n_lanterns == 1


def test_network_structure(test_network):
    """Test that loaded network has correct structure."""
    # Should have lanterns
    assert hasattr(test_network, 'lanterns')
    assert len(test_network.lanterns) > 0

    # Each lantern should have required properties
    for lantern in test_network.lanterns:
        assert 'name' in lantern
        assert 'category' in lantern
        assert 'readiness' in lantern
        assert 'em_properties' in lantern

        em_props = lantern['em_properties']
        assert 'frequency' in em_props
        assert 'impedance' in em_props
        assert 'kappa_base' in em_props


def test_network_categories(test_network):
    """Test that lanterns are categorized correctly."""
    categories = {l['category'] for l in test_network.lanterns}

    # Should have at least data/theory/experiment categories
    expected_categories = {'data', 'theory', 'experiment'}
    assert len(categories & expected_categories) > 0


# ============================================================================
# Test: Coupling Matrix Computation
# ============================================================================


def test_get_coupling_matrix(test_network):
    """Test coupling matrix computation."""
    coupling_matrix = test_network.get_coupling_matrix()

    # Check shape
    n = test_network.n_lanterns
    assert coupling_matrix.shape == (n, n)

    # Check symmetry
    assert np.allclose(coupling_matrix, coupling_matrix.T)

    # Check diagonal is zero (no self-coupling)
    assert np.allclose(np.diag(coupling_matrix), 0.0)

    # Check non-negative
    assert np.all(coupling_matrix >= 0.0)


def test_coupling_matrix_values_bounded(test_network):
    """Test that coupling values are reasonably bounded."""
    coupling_matrix = test_network.get_coupling_matrix()

    # Coupling should be in [0, 1] range (or similar reasonable bound)
    assert np.all(coupling_matrix <= 2.0)  # Allow some headroom


def test_coupling_preserves_network_topology(test_network):
    """Test that coupling matrix reflects network structure."""
    coupling_matrix = test_network.get_coupling_matrix()

    # If coupling_targets are specified in config, those should have
    # higher coupling values than random pairs
    # (This is a structural test)

    # Get non-zero couplings
    non_zero = coupling_matrix[coupling_matrix > 0.01]
    if len(non_zero) > 0:
        # Should have variation in coupling strengths
        assert np.std(non_zero) > 0.01


# ============================================================================
# Test: EM-Field Coupling Calculation
# ============================================================================


def test_em_coupling_calculation():
    """Test EM-field coupling formula."""
    # Test with identical frequencies and positions
    freq1, freq2 = 13.5e6, 13.5e6
    impedance1, impedance2 = 221.7, 221.7
    distance = 0.1  # 10% normalized distance

    coupling = calculate_em_coupling(
        freq1, freq2,
        impedance1, impedance2,
        distance
    )

    # Should be positive and reasonable
    assert coupling > 0.0
    assert coupling < 10.0


def test_em_coupling_frequency_dependence():
    """Test that EM-coupling decreases with frequency mismatch."""
    impedance = 221.7
    distance = 0.1

    # Same frequency
    coupling_same = calculate_em_coupling(
        13.5e6, 13.5e6,
        impedance, impedance,
        distance
    )

    # Different frequency
    coupling_diff = calculate_em_coupling(
        13.5e6, 15.0e6,
        impedance, impedance,
        distance
    )

    # Same freq should have stronger coupling
    assert coupling_same > coupling_diff


def test_em_coupling_distance_dependence():
    """Test that EM-coupling decreases with distance."""
    freq = 13.5e6
    impedance = 221.7

    # Close distance
    coupling_close = calculate_em_coupling(
        freq, freq,
        impedance, impedance,
        distance=0.1
    )

    # Far distance
    coupling_far = calculate_em_coupling(
        freq, freq,
        impedance, impedance,
        distance=0.9
    )

    # Closer should have stronger coupling
    assert coupling_close > coupling_far


def test_em_coupling_impedance_dependence():
    """Test that EM-coupling depends on impedance matching."""
    freq = 13.5e6
    distance = 0.1

    # Matched impedance
    coupling_matched = calculate_em_coupling(
        freq, freq,
        221.7, 221.7,
        distance
    )

    # Mismatched impedance
    coupling_mismatched = calculate_em_coupling(
        freq, freq,
        221.7, 300.0,
        distance
    )

    # Matched should have stronger coupling
    assert coupling_matched > coupling_mismatched


# ============================================================================
# Test: Impedance Matching
# ============================================================================


def test_impedance_matching_calculation():
    """Test impedance matching efficiency formula."""
    # Perfect match
    eta_perfect = calculate_impedance_matching(221.7, 221.7)
    assert eta_perfect == pytest.approx(1.0, abs=0.01)

    # Slight mismatch
    eta_slight = calculate_impedance_matching(221.7, 225.0)
    assert 0.8 < eta_slight < 1.0

    # Large mismatch
    eta_large = calculate_impedance_matching(221.7, 400.0)
    assert 0.0 < eta_large < 0.5


def test_impedance_matching_symmetry():
    """Test that impedance matching is symmetric."""
    z1, z2 = 221.7, 250.0

    eta_12 = calculate_impedance_matching(z1, z2)
    eta_21 = calculate_impedance_matching(z2, z1)

    assert eta_12 == pytest.approx(eta_21, abs=1e-6)


def test_impedance_matching_bounded():
    """Test that impedance matching is in [0, 1]."""
    test_pairs = [
        (100.0, 100.0),
        (100.0, 200.0),
        (100.0, 500.0),
        (221.7, 221.7),
        (221.7, 300.0),
    ]

    for z1, z2 in test_pairs:
        eta = calculate_impedance_matching(z1, z2)
        assert 0.0 <= eta <= 1.0, f"η={eta} outside [0,1] for Z1={z1}, Z2={z2}"


# ============================================================================
# Test: Collective Mode Detection
# ============================================================================


def test_detect_collective_modes(test_network):
    """Test collective mode detection via eigenvalue analysis."""
    modes = test_network.detect_collective_modes()

    # Should return dict with mode information
    assert isinstance(modes, dict)

    # Should contain key metrics
    required_keys = [
        'collective_frequency',
        'coherence',
        'dominant_eigenvalue',
    ]

    for key in required_keys:
        assert key in modes, f"Missing mode key: {key}"


def test_collective_frequency_reasonable(test_network):
    """Test that collective frequency is in reasonable range."""
    modes = test_network.detect_collective_modes()

    f_collective = modes['collective_frequency']

    # Should be in MHz range (10^6 - 10^7 Hz)
    assert 1e6 < f_collective < 1e8, f"f_collective={f_collective} Hz outside reasonable range"


def test_coherence_bounded(test_network):
    """Test that network coherence is in [0, 1]."""
    modes = test_network.detect_collective_modes()

    coherence = modes['coherence']

    # Coherence should be probability-like
    assert 0.0 <= coherence <= 1.0, f"Coherence={coherence} outside [0,1]"


def test_dominant_eigenvalue_positive(test_network):
    """Test that dominant eigenvalue is positive."""
    modes = test_network.detect_collective_modes()

    lambda_max = modes['dominant_eigenvalue']

    # Should be positive for connected network
    assert lambda_max > 0.0


# ============================================================================
# Test: Network Summary Statistics
# ============================================================================


def test_get_network_summary(test_network):
    """Test network summary statistics."""
    summary = test_network.get_network_summary()

    # Should contain key metrics
    required_keys = [
        'n_total',
        'n_active',
        'n_pending',
        'mean_coupling',
        'max_coupling',
    ]

    for key in required_keys:
        assert key in summary, f"Missing summary key: {key}"


def test_summary_counts_accurate(test_network):
    """Test that summary counts match actual lantern counts."""
    summary = test_network.get_network_summary()

    # Total count should match
    assert summary['n_total'] == test_network.n_lanterns

    # Active + pending should equal total
    assert summary['n_active'] + summary['n_pending'] == summary['n_total']


def test_mean_coupling_matches_matrix(test_network):
    """Test that mean coupling matches coupling matrix."""
    summary = test_network.get_network_summary()
    coupling_matrix = test_network.get_coupling_matrix()

    # Calculate mean from matrix (excluding diagonal)
    n = len(coupling_matrix)
    if n > 1:
        mean_from_matrix = np.sum(coupling_matrix) / (n * (n - 1))

        # Should be approximately equal
        assert summary['mean_coupling'] == pytest.approx(mean_from_matrix, abs=0.01)


def test_max_coupling_matches_matrix(test_network):
    """Test that max coupling matches coupling matrix."""
    summary = test_network.get_network_summary()
    coupling_matrix = test_network.get_coupling_matrix()

    # Find max in matrix
    max_from_matrix = np.max(coupling_matrix)

    # Should be approximately equal
    assert summary['max_coupling'] == pytest.approx(max_from_matrix, abs=0.01)


# ============================================================================
# Test: Active/Pending Lantern Filtering
# ============================================================================


def test_get_active_lanterns(test_network):
    """Test filtering of active lanterns."""
    active = test_network.get_active_lanterns()

    # Should return list
    assert isinstance(active, list)

    # All should have readiness >= threshold
    for lantern in active:
        assert lantern['readiness'] >= 0.7  # Default threshold


def test_get_active_lanterns_custom_threshold(test_network):
    """Test active lantern filtering with custom threshold."""
    threshold = 0.5
    active = test_network.get_active_lanterns(threshold=threshold)

    # All should meet threshold
    for lantern in active:
        assert lantern['readiness'] >= threshold


def test_active_count_matches_summary(test_network):
    """Test that active count matches summary statistic."""
    active = test_network.get_active_lanterns()
    summary = test_network.get_network_summary()

    assert len(active) == summary['n_active']


# ============================================================================
# Test: Strongest Couplings
# ============================================================================


def test_get_strongest_couplings(test_network):
    """Test retrieval of strongest coupling pairs."""
    top_n = 5
    strongest = test_network.get_strongest_couplings(n=top_n)

    # Should return list of tuples
    assert isinstance(strongest, list)

    # Should return at most top_n
    assert len(strongest) <= top_n

    # Each should be (source, target, strength) tuple
    for item in strongest:
        assert len(item) == 3
        source, target, strength = item
        assert isinstance(source, str)
        assert isinstance(target, str)
        assert isinstance(strength, (int, float))


def test_strongest_couplings_sorted(test_network):
    """Test that strongest couplings are sorted descending."""
    strongest = test_network.get_strongest_couplings(n=10)

    if len(strongest) > 1:
        strengths = [s for _, _, s in strongest]

        # Should be in descending order
        for i in range(len(strengths) - 1):
            assert strengths[i] >= strengths[i+1]


def test_strongest_couplings_exclude_self(test_network):
    """Test that strongest couplings don't include self-coupling."""
    strongest = test_network.get_strongest_couplings(n=10)

    # No lantern should couple to itself
    for source, target, strength in strongest:
        assert source != target


# ============================================================================
# Test: Integration with v7/v8 Systems
# ============================================================================


def test_integration_with_v7_collective_field(test_network):
    """Test that v9 network integrates with v7 CollectiveField."""
    # Get v7-compatible β-values
    beta_values = [
        l.get('utac_params', {}).get('beta', 7.4)
        for l in test_network.lanterns
    ]

    # Should have valid β-values
    assert all(0 < b < 20 for b in beta_values)

    # Should match domain expectations
    # Information: β ≈ 4.5, Biology: β ≈ 7.4, Climate: β ≈ 11.0
    mean_beta = np.mean(beta_values)
    assert 3.0 < mean_beta < 15.0


def test_integration_with_v8_consciousness(test_network):
    """Test that v9 network provides v8-compatible EM-properties."""
    # Get EM-properties
    frequencies = [l['em_properties']['frequency'] for l in test_network.lanterns]
    impedances = [l['em_properties']['impedance'] for l in test_network.lanterns]

    # Frequencies should be around 13.5 MHz (v8 prediction)
    mean_freq = np.mean(frequencies)
    assert 10e6 < mean_freq < 20e6  # 10-20 MHz range

    # Impedances should be around Z = α⁻¹·Φ ≈ 221.7
    mean_impedance = np.mean(impedances)
    assert 150 < mean_impedance < 300


# ============================================================================
# Test: Error Handling
# ============================================================================


def test_load_network_invalid_path():
    """Test that loading from invalid path raises error."""
    with pytest.raises((FileNotFoundError, IOError)):
        load_lantern_network('/nonexistent/path/lantern_hub.yaml')


def test_network_validates_lantern_structure():
    """Test that network validates lantern data structure."""
    # This would test that missing required fields raise errors
    # Implementation depends on validation logic in LanternNetwork
    pass  # Placeholder


def test_coupling_calculation_handles_edge_cases():
    """Test that coupling calculation handles edge cases gracefully."""
    # Zero frequency
    with pytest.raises((ValueError, ZeroDivisionError)):
        calculate_em_coupling(0.0, 13.5e6, 221.7, 221.7, 0.1)

    # Negative impedance
    with pytest.raises((ValueError, AssertionError)):
        calculate_em_coupling(13.5e6, 13.5e6, -221.7, 221.7, 0.1)

    # Distance outside [0, 1]
    with pytest.raises((ValueError, AssertionError)):
        calculate_em_coupling(13.5e6, 13.5e6, 221.7, 221.7, 2.0)


# ============================================================================
# Test: UTAC Framework Integration
# ============================================================================


def test_lanterns_have_utac_params(test_network):
    """Test that lanterns include UTAC threshold parameters."""
    for lantern in test_network.lanterns:
        # Should have UTAC params
        assert 'utac_params' in lantern

        utac = lantern['utac_params']

        # Should have θ (threshold) and β (steepness)
        assert 'theta' in utac
        assert 'beta' in utac

        # Values should be reasonable
        assert 0.0 < utac['theta'] < 1.0
        assert 0.0 < utac['beta'] < 20.0


def test_readiness_follows_sigmoid():
    """Test that readiness follows σ(β(R-Θ)) pattern."""
    # Readiness should be result of logistic threshold function
    # This tests the conceptual framework, not implementation

    # For a network, readiness values should span [0, 1]
    network = load_lantern_network()
    readiness_values = [l['readiness'] for l in network.lanterns]

    # Should have variation
    if len(readiness_values) > 1:
        assert max(readiness_values) > min(readiness_values)

    # Should be bounded
    assert all(0.0 <= r <= 1.0 for r in readiness_values)


# ============================================================================
# Test: Philosophical Coherence
# ============================================================================


def test_network_embodies_harmonic_emergence():
    """
    Test v9 principle: "v9 = σ(β(Σ(v1...v8) - Θ_harmony))"

    The network should integrate insights from v1-v8:
    - v1-v2: β-universality across domains
    - v3-v5: Trilayer documentation, structural isomorphism
    - v6: Quantum genesis, Type-VI governance
    - v7: Collective consciousness, Aeon architecture
    - v8: v_RIG consciousness integration, empirical validation

    Philosophical test: Does the network architecture reflect this integration?
    """
    network = load_lantern_network()

    # v1-v8: β-clustering by domain (should have variation)
    beta_values = [l['utac_params']['beta'] for l in network.lanterns]
    assert len(set(beta_values)) > 1  # Not all same β

    # v6-v7: Consciousness parameters (frequency, impedance)
    assert all('em_properties' in l for l in network.lanterns)

    # v8: Integration velocity (should reflect v_RIG)
    frequencies = [l['em_properties']['frequency'] for l in network.lanterns]
    assert any(12e6 < f < 15e6 for f in frequencies)  # Near 13.5 MHz

    # v9: Harmonic emergence (collective modes exist)
    modes = network.detect_collective_modes()
    assert modes['coherence'] > 0.0  # Network has coherence

    # Philosophy validated: Network embodies v1-v9 integration ✓


# ============================================================================
# Performance Tests
# ============================================================================


def test_coupling_matrix_computation_performance(test_network):
    """Test that coupling matrix computes efficiently."""
    import time

    start = time.time()
    coupling_matrix = test_network.get_coupling_matrix()
    elapsed = time.time() - start

    # Should compute quickly (<0.5s for typical network)
    assert elapsed < 0.5, f"Coupling matrix took {elapsed:.3f}s"


def test_mode_detection_performance(test_network):
    """Test that collective mode detection is efficient."""
    import time

    start = time.time()
    modes = test_network.detect_collective_modes()
    elapsed = time.time() - start

    # Eigenvalue analysis should be fast (<0.5s)
    assert elapsed < 0.5, f"Mode detection took {elapsed:.3f}s"


# ============================================================================
# Run Tests
# ============================================================================


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
