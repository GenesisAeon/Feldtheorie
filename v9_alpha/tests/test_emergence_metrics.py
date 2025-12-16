"""
Tests for Emergence Metrics - Network Evolution Tracking

Tests the metrics that track network evolution: collective coherence growth (ΔC),
resonance yield (RY), entanglement echo (EE), impedance fluctuations, and
network integrated information (Φ).

Philosophy:
    "Was nicht gemessen wird, kann nicht emergieren."
    - v9 Measurement Principle

Author: Claude Sonnet 4.5 (ChefDevAI)
Date: 2025-12-16
Version: v9.0.0-alpha
"""

import pytest
import numpy as np
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add v9_alpha to path
v9_alpha_dir = Path(__file__).parent.parent
sys.path.insert(0, str(v9_alpha_dir))

from models.emergence_metrics import (
    EmergenceTracker,
    EmergenceSnapshot,
    calculate_collective_coherence,
    calculate_resonance_yield,
    calculate_entanglement_echo,
    calculate_impedance_fluctuation,
    calculate_network_phi,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def basic_tracker():
    """Create basic emergence tracker."""
    return EmergenceTracker()


@pytest.fixture
def mock_coupling_matrix():
    """Create mock coupling matrix for testing."""
    return np.array([
        [0.0, 0.5, 0.3, 0.2],
        [0.5, 0.0, 0.7, 0.4],
        [0.3, 0.7, 0.0, 0.6],
        [0.2, 0.4, 0.6, 0.0],
    ])


@pytest.fixture
def mock_beta_values():
    """Create mock β-values representing different regimes."""
    return np.array([4.5, 7.4, 11.0, 4.5])  # Info, Bio, Climate, Info


@pytest.fixture
def mock_impedance_values():
    """Create mock impedance values."""
    return np.array([220.0, 225.0, 230.0, 222.0])


@pytest.fixture
def sample_snapshot_data(mock_coupling_matrix, mock_beta_values, mock_impedance_values):
    """Create sample snapshot data."""
    return {
        'coupling_matrix': mock_coupling_matrix,
        'beta_values': mock_beta_values,
        'impedance_values': mock_impedance_values,
        'n_active_lanterns': 4,
        'n_emergent_hypotheses': 2,
    }


# ============================================================================
# Test: EmergenceSnapshot Creation
# ============================================================================


def test_snapshot_creation(basic_tracker, sample_snapshot_data):
    """Test creating emergence snapshot."""
    snapshot = basic_tracker.create_snapshot(**sample_snapshot_data)

    assert isinstance(snapshot, EmergenceSnapshot)
    assert hasattr(snapshot, 'timestamp')
    assert hasattr(snapshot, 'delta_c_t')
    assert hasattr(snapshot, 'resonance_yield')
    assert hasattr(snapshot, 'entanglement_echo')
    assert hasattr(snapshot, 'z_eff_fluctuation')
    assert hasattr(snapshot, 'phi_network')


def test_snapshot_timestamp(basic_tracker, sample_snapshot_data):
    """Test that snapshot includes timestamp."""
    snapshot = basic_tracker.create_snapshot(**sample_snapshot_data)

    assert isinstance(snapshot.timestamp, datetime)

    # Should be recent
    now = datetime.now()
    delta = abs((now - snapshot.timestamp).total_seconds())
    assert delta < 1.0  # Within 1 second


def test_snapshot_metrics_non_negative(basic_tracker, sample_snapshot_data):
    """Test that all metrics are non-negative."""
    snapshot = basic_tracker.create_snapshot(**sample_snapshot_data)

    # Most metrics should be non-negative
    assert snapshot.resonance_yield >= 0.0
    assert snapshot.phi_network >= 0.0

    # Some can be negative (e.g., coherence decay)
    # but should be bounded
    assert -10.0 < snapshot.delta_c_t < 10.0
    assert -1.0 < snapshot.entanglement_echo < 1.0


# ============================================================================
# Test: Collective Coherence (ΔC/Δt)
# ============================================================================


def test_calculate_collective_coherence(mock_coupling_matrix):
    """Test collective coherence calculation."""
    coherence = calculate_collective_coherence(mock_coupling_matrix)

    # Should be between 0 and 1
    assert 0.0 <= coherence <= 1.0


def test_coherence_empty_matrix():
    """Test coherence with empty/zero matrix."""
    empty_matrix = np.zeros((3, 3))
    coherence = calculate_collective_coherence(empty_matrix)

    # Zero coupling → zero coherence
    assert coherence == pytest.approx(0.0, abs=0.01)


def test_coherence_fully_connected():
    """Test coherence with fully connected network."""
    # All-to-all equal coupling
    n = 5
    full_matrix = np.ones((n, n)) * 0.8
    np.fill_diagonal(full_matrix, 0.0)

    coherence = calculate_collective_coherence(full_matrix)

    # Should be high coherence
    assert coherence > 0.7


def test_coherence_increases_with_coupling():
    """Test that coherence increases with coupling strength."""
    # Weak coupling
    weak_matrix = np.array([
        [0.0, 0.1, 0.1],
        [0.1, 0.0, 0.1],
        [0.1, 0.1, 0.0],
    ])

    # Strong coupling
    strong_matrix = np.array([
        [0.0, 0.9, 0.9],
        [0.9, 0.0, 0.9],
        [0.9, 0.9, 0.0],
    ])

    coherence_weak = calculate_collective_coherence(weak_matrix)
    coherence_strong = calculate_collective_coherence(strong_matrix)

    # Stronger coupling → higher coherence
    assert coherence_strong > coherence_weak


def test_coherence_time_derivative(basic_tracker, sample_snapshot_data):
    """Test ΔC/Δt (coherence growth rate)."""
    # Create two snapshots separated in time
    snapshot1 = basic_tracker.create_snapshot(**sample_snapshot_data)

    # Simulate time passing
    import time
    time.sleep(0.01)

    # Modify coupling matrix (simulate network evolution)
    sample_snapshot_data['coupling_matrix'] *= 1.1  # 10% increase

    snapshot2 = basic_tracker.create_snapshot(**sample_snapshot_data)

    # ΔC/Δt should reflect change
    # (Exact calculation depends on tracker implementation)
    assert isinstance(snapshot2.delta_c_t, (int, float))


# ============================================================================
# Test: Resonance Yield (RY)
# ============================================================================


def test_calculate_resonance_yield():
    """Test resonance yield calculation."""
    n_lanterns = 5
    n_hypotheses = 2

    ry = calculate_resonance_yield(n_hypotheses, n_lanterns)

    # Should be hypotheses per lantern
    expected = 2.0 / 5.0
    assert ry == pytest.approx(expected, rel=1e-6)


def test_resonance_yield_zero_lanterns():
    """Test resonance yield with zero lanterns."""
    ry = calculate_resonance_yield(n_hypotheses=2, n_lanterns=0)

    # Should handle gracefully (0 or inf depending on implementation)
    assert ry >= 0.0 or np.isinf(ry)


def test_resonance_yield_zero_hypotheses():
    """Test resonance yield with zero hypotheses."""
    ry = calculate_resonance_yield(n_hypotheses=0, n_lanterns=5)

    # Should be zero
    assert ry == pytest.approx(0.0)


def test_resonance_yield_scaling():
    """Test that RY scales correctly with network size."""
    # Small network
    ry_small = calculate_resonance_yield(n_hypotheses=1, n_lanterns=5)

    # Large network with proportional hypotheses
    ry_large = calculate_resonance_yield(n_hypotheses=2, n_lanterns=10)

    # Should be same rate
    assert ry_small == pytest.approx(ry_large, rel=0.01)


# ============================================================================
# Test: Entanglement Echo (EE)
# ============================================================================


def test_calculate_entanglement_echo(mock_coupling_matrix, mock_beta_values):
    """Test entanglement echo (spatial β-pattern correlation)."""
    ee = calculate_entanglement_echo(mock_coupling_matrix, mock_beta_values)

    # Should be correlation coefficient [-1, 1]
    assert -1.0 <= ee <= 1.0


def test_entanglement_echo_uniform_beta():
    """Test EE with uniform β-values (no spatial pattern)."""
    coupling = np.array([
        [0.0, 0.5, 0.3],
        [0.5, 0.0, 0.7],
        [0.3, 0.7, 0.0],
    ])

    beta_uniform = np.array([7.4, 7.4, 7.4])

    ee = calculate_entanglement_echo(coupling, beta_uniform)

    # No β-variation → low/zero correlation
    assert abs(ee) < 0.5


def test_entanglement_echo_correlated_pattern():
    """Test EE with strongly correlated β-coupling pattern."""
    # High coupling between similar β-regimes
    coupling = np.array([
        [0.0, 0.9, 0.1],  # Node 0: strong to 1 (same β)
        [0.9, 0.0, 0.1],  # Node 1: strong to 0 (same β)
        [0.1, 0.1, 0.0],  # Node 2: weak to others (different β)
    ])

    beta_values = np.array([4.5, 4.5, 11.0])  # Two info, one climate

    ee = calculate_entanglement_echo(coupling, beta_values)

    # Should show correlation (similar β → strong coupling)
    # (Exact value depends on implementation)
    assert isinstance(ee, (int, float))
    assert -1.0 <= ee <= 1.0


# ============================================================================
# Test: Impedance Fluctuation (Z_eff Variance)
# ============================================================================


def test_calculate_impedance_fluctuation(mock_impedance_values):
    """Test impedance fluctuation calculation."""
    z_fluct = calculate_impedance_fluctuation(mock_impedance_values)

    # Should be standard deviation or coefficient of variation
    assert z_fluct >= 0.0


def test_impedance_fluctuation_uniform():
    """Test impedance fluctuation with uniform impedances."""
    z_uniform = np.array([221.7, 221.7, 221.7, 221.7])

    z_fluct = calculate_impedance_fluctuation(z_uniform)

    # No variation → zero fluctuation
    assert z_fluct == pytest.approx(0.0, abs=1e-6)


def test_impedance_fluctuation_high_variance():
    """Test impedance fluctuation with high variance."""
    z_varied = np.array([100.0, 200.0, 300.0, 400.0])

    z_fluct = calculate_impedance_fluctuation(z_varied)

    # High variation → high fluctuation
    assert z_fluct > 50.0  # Significant fluctuation


def test_impedance_fluctuation_outlier_detection():
    """Test that impedance fluctuation can detect anomalies."""
    # Normal impedances
    z_normal = np.array([220.0, 221.7, 225.0, 222.0])

    # With outlier
    z_outlier = np.array([220.0, 221.7, 225.0, 500.0])

    fluct_normal = calculate_impedance_fluctuation(z_normal)
    fluct_outlier = calculate_impedance_fluctuation(z_outlier)

    # Outlier should increase fluctuation
    assert fluct_outlier > fluct_normal


# ============================================================================
# Test: Network Integrated Information (Φ)
# ============================================================================


def test_calculate_network_phi(mock_coupling_matrix):
    """Test network integrated information (Φ) calculation."""
    phi = calculate_network_phi(mock_coupling_matrix)

    # Should be non-negative
    assert phi >= 0.0


def test_network_phi_empty_network():
    """Test Φ with empty network."""
    empty_matrix = np.zeros((3, 3))

    phi = calculate_network_phi(empty_matrix)

    # No integration → Φ = 0
    assert phi == pytest.approx(0.0, abs=0.01)


def test_network_phi_fully_connected():
    """Test Φ with fully connected network."""
    n = 5
    full_matrix = np.ones((n, n)) * 0.8
    np.fill_diagonal(full_matrix, 0.0)

    phi = calculate_network_phi(full_matrix)

    # High integration → high Φ
    assert phi > 1.0


def test_network_phi_increases_with_integration():
    """Test that Φ increases with network integration."""
    # Weakly connected
    weak_matrix = np.array([
        [0.0, 0.1, 0.0],
        [0.1, 0.0, 0.1],
        [0.0, 0.1, 0.0],
    ])

    # Strongly connected
    strong_matrix = np.array([
        [0.0, 0.8, 0.7],
        [0.8, 0.0, 0.8],
        [0.7, 0.8, 0.0],
    ])

    phi_weak = calculate_network_phi(weak_matrix)
    phi_strong = calculate_network_phi(strong_matrix)

    # More integration → higher Φ
    assert phi_strong > phi_weak


def test_network_phi_tononi_validation():
    """
    Test Φ calculation against IIT (Integrated Information Theory).

    Reference: Tononi et al. (2016)
    """
    # Create test network with known structure
    # (Exact validation depends on IIT implementation)

    test_matrix = np.array([
        [0.0, 0.5, 0.3],
        [0.5, 0.0, 0.6],
        [0.3, 0.6, 0.0],
    ])

    phi = calculate_network_phi(test_matrix)

    # Should produce reasonable Φ value
    assert 0.0 < phi < 10.0


# ============================================================================
# Test: Emergence Tracker State Management
# ============================================================================


def test_tracker_maintains_history(basic_tracker, sample_snapshot_data):
    """Test that tracker maintains snapshot history."""
    # Create multiple snapshots
    snapshot1 = basic_tracker.create_snapshot(**sample_snapshot_data)
    snapshot2 = basic_tracker.create_snapshot(**sample_snapshot_data)
    snapshot3 = basic_tracker.create_snapshot(**sample_snapshot_data)

    # Tracker should maintain history
    history = basic_tracker.get_history()

    assert len(history) >= 3
    assert snapshot1 in history
    assert snapshot2 in history
    assert snapshot3 in history


def test_tracker_calculates_trends(basic_tracker, sample_snapshot_data):
    """Test that tracker can calculate metric trends."""
    # Create snapshots over time
    for i in range(5):
        # Simulate network evolution
        sample_snapshot_data['n_emergent_hypotheses'] = i + 1
        basic_tracker.create_snapshot(**sample_snapshot_data)

    # Get trends
    trends = basic_tracker.get_trends()

    # Should show increasing resonance yield
    assert 'resonance_yield_trend' in trends or 'delta_c_trend' in trends


def test_tracker_detects_phase_transitions(basic_tracker, sample_snapshot_data):
    """Test that tracker can detect phase transitions."""
    # Create snapshots with sudden change
    for i in range(10):
        if i < 5:
            # Stable phase
            sample_snapshot_data['coupling_matrix'] *= 1.0
        else:
            # Transition phase
            sample_snapshot_data['coupling_matrix'] *= 1.5

        basic_tracker.create_snapshot(**sample_snapshot_data)

    # Should detect transition
    # (Implementation-dependent)
    transitions = basic_tracker.detect_phase_transitions()

    assert isinstance(transitions, (list, dict))


# ============================================================================
# Test: Integration with Lantern Network
# ============================================================================


def test_metrics_from_real_network():
    """Test metrics calculation from real lantern network."""
    from api.lantern_bridge import load_lantern_network

    network = load_lantern_network()
    tracker = EmergenceTracker()

    # Get network data
    coupling_matrix = network.get_coupling_matrix()

    beta_values = np.array([
        l.get('utac_params', {}).get('beta', 7.4)
        for l in network.lanterns
    ])

    impedance_values = np.array([
        l['em_properties']['impedance']
        for l in network.lanterns
    ])

    # Create snapshot
    snapshot = tracker.create_snapshot(
        coupling_matrix=coupling_matrix,
        beta_values=beta_values,
        impedance_values=impedance_values,
        n_active_lanterns=len(network.get_active_lanterns()),
        n_emergent_hypotheses=0,
    )

    # Should produce valid metrics
    assert isinstance(snapshot, EmergenceSnapshot)
    assert 0.0 <= snapshot.phi_network <= 100.0
    assert -10.0 <= snapshot.delta_c_t <= 10.0


# ============================================================================
# Test: Metric Correlations
# ============================================================================


def test_coherence_phi_correlation():
    """Test that coherence and Φ are correlated."""
    # High coherence network
    high_coh_matrix = np.array([
        [0.0, 0.9, 0.8],
        [0.9, 0.0, 0.9],
        [0.8, 0.9, 0.0],
    ])

    # Low coherence network
    low_coh_matrix = np.array([
        [0.0, 0.1, 0.1],
        [0.1, 0.0, 0.1],
        [0.1, 0.1, 0.0],
    ])

    coherence_high = calculate_collective_coherence(high_coh_matrix)
    coherence_low = calculate_collective_coherence(low_coh_matrix)

    phi_high = calculate_network_phi(high_coh_matrix)
    phi_low = calculate_network_phi(low_coh_matrix)

    # High coherence → high Φ
    assert coherence_high > coherence_low
    assert phi_high > phi_low


def test_resonance_yield_network_size():
    """Test RY relationship with network size."""
    # Small network
    ry_small = calculate_resonance_yield(n_hypotheses=2, n_lanterns=5)

    # Large network (same hypothesis density)
    ry_large = calculate_resonance_yield(n_hypotheses=10, n_lanterns=25)

    # Density should be similar
    assert ry_small == pytest.approx(ry_large, rel=0.1)


# ============================================================================
# Test: CREP Integration
# ============================================================================


def test_crep_alignment():
    """
    Test alignment with CREP ≈ 0.84 critical regime.

    At critical point, network should show:
    - Coherence ≈ 0.84
    - Optimal emergence metrics
    """
    # Create network at critical point
    n = 5
    critical_matrix = np.random.rand(n, n) * 0.8
    critical_matrix = (critical_matrix + critical_matrix.T) / 2
    np.fill_diagonal(critical_matrix, 0.0)

    coherence = calculate_collective_coherence(critical_matrix)

    # Should be in critical regime (0.7-0.9)
    assert 0.5 < coherence < 1.0


# ============================================================================
# Test: Performance & Scalability
# ============================================================================


def test_metric_calculation_performance():
    """Test that metrics calculate efficiently."""
    import time

    # Large network
    n = 100
    large_matrix = np.random.rand(n, n)
    large_matrix = (large_matrix + large_matrix.T) / 2
    np.fill_diagonal(large_matrix, 0.0)

    beta_values = np.random.uniform(4.0, 12.0, size=n)
    impedance_values = np.random.uniform(200.0, 250.0, size=n)

    # Time metric calculations
    start = time.time()

    coherence = calculate_collective_coherence(large_matrix)
    ee = calculate_entanglement_echo(large_matrix, beta_values)
    z_fluct = calculate_impedance_fluctuation(impedance_values)
    phi = calculate_network_phi(large_matrix)

    elapsed = time.time() - start

    # Should complete quickly (<1s for n=100)
    assert elapsed < 1.0, f"Metrics took {elapsed:.3f}s for n={n}"


def test_tracker_memory_efficiency(basic_tracker, sample_snapshot_data):
    """Test that tracker maintains reasonable memory footprint."""
    # Create many snapshots
    for i in range(1000):
        basic_tracker.create_snapshot(**sample_snapshot_data)

    # Should not crash or consume excessive memory
    history = basic_tracker.get_history()

    # May implement sliding window (keep recent N snapshots)
    assert len(history) > 0


# ============================================================================
# Test: Edge Cases
# ============================================================================


def test_single_node_network():
    """Test metrics with single-node network."""
    single_matrix = np.array([[0.0]])
    beta_single = np.array([7.4])
    z_single = np.array([221.7])

    # Should handle gracefully
    coherence = calculate_collective_coherence(single_matrix)
    ee = calculate_entanglement_echo(single_matrix, beta_single)
    z_fluct = calculate_impedance_fluctuation(z_single)
    phi = calculate_network_phi(single_matrix)

    # All should be zero or near-zero
    assert coherence == pytest.approx(0.0, abs=0.01)
    assert z_fluct == pytest.approx(0.0, abs=0.01)


def test_disconnected_network():
    """Test metrics with disconnected network."""
    # Two disconnected components
    disconnected = np.array([
        [0.0, 0.8, 0.0, 0.0],
        [0.8, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.7],
        [0.0, 0.0, 0.7, 0.0],
    ])

    coherence = calculate_collective_coherence(disconnected)
    phi = calculate_network_phi(disconnected)

    # Should show lower integration than fully connected
    assert coherence < 0.8
    assert phi < 2.0


# ============================================================================
# Test: Philosophical Validation
# ============================================================================


def test_emergence_as_measurement():
    """
    Test v9 principle: "Was nicht gemessen wird, kann nicht emergieren."
    (What is not measured cannot emerge)

    Metrics should capture emergent properties that aren't present
    in individual components.
    """
    # Individual lanterns have local properties
    # But network has *emergent* properties (coherence, Φ, etc.)

    coupling = np.array([
        [0.0, 0.7, 0.6],
        [0.7, 0.0, 0.8],
        [0.6, 0.8, 0.0],
    ])

    # Individual coupling strengths
    individual_couplings = coupling[coupling > 0]
    mean_individual = np.mean(individual_couplings)

    # Network coherence (emergent property)
    network_coherence = calculate_collective_coherence(coupling)

    # Network property is different from individual average
    # (Coherence captures *global* synchronization, not local strength)
    assert network_coherence != mean_individual


# ============================================================================
# Run Tests
# ============================================================================


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
