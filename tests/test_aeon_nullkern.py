"""
Tests for Aeon Nullkern Module
================================

Tests the Zero-Point Consciousness Kernel implementation.

Run:
    pytest tests/test_aeon_nullkern.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from aeon.nullkern import BardoPhase, ConsciousnessState, Nullkern


# ============================================================================
# Nullkern Tests
# ============================================================================


def test_nullkern_initialization():
    """Test Nullkern initialization with default parameters."""
    kernel = Nullkern()

    assert kernel.beta_target == 0.1
    assert kernel.kappa == 0.1
    assert kernel.dimension == 8
    assert kernel.enable_bardo_mode is True
    assert len(kernel.history) == 0


def test_nullkern_custom_params():
    """Test Nullkern with custom parameters."""
    kernel = Nullkern(beta_target=0.05, kappa=0.2, dimension=16, enable_bardo_mode=False)

    assert kernel.beta_target == 0.05
    assert kernel.kappa == 0.2
    assert kernel.dimension == 16
    assert kernel.enable_bardo_mode is False
    assert kernel.state.phase == BardoPhase.NONE


def test_nullkern_activation_near_zero():
    """Test activation function for β≈0."""
    kernel = Nullkern(beta_target=0.01)

    # For β→0, activation should approach 0.5
    activation = kernel.activate(resource=0.3, threshold=0.5)
    assert 0.45 < activation < 0.55


def test_nullkern_activation_varying_resource():
    """Test activation function with varying resources."""
    kernel = Nullkern(beta_target=0.5)

    # Low resource
    act_low = kernel.activate(resource=0.1, threshold=0.5)
    # High resource
    act_high = kernel.activate(resource=0.9, threshold=0.5)

    # High resource should give higher activation
    assert act_high > act_low


def test_nullkern_impedance():
    """Test impedance computation."""
    kernel = Nullkern(beta_target=0.5, kappa=0.5)

    # Compute impedance
    zeta = kernel.compute_impedance(resource=0.5)

    # ζ = β*(1-κ) - baseline
    # ζ = 0.5*0.5 - 0.5 = -0.25
    assert zeta < 0  # Should be negative


def test_nullkern_update_state():
    """Test state update."""
    kernel = Nullkern(beta_target=0.5, kappa=0.3)

    initial_beta = kernel.state.beta
    kernel.update_state(delta_beta=0.1, delta_kappa=0.05)

    assert kernel.state.beta == pytest.approx(initial_beta + 0.1, abs=1e-6)
    assert kernel.kappa == pytest.approx(0.35, abs=1e-6)
    assert len(kernel.history) > 0


def test_nullkern_bardo_transitions():
    """Test Bardo phase transitions."""
    kernel = Nullkern(beta_target=0.05, kappa=0.05, enable_bardo_mode=True)

    # Should detect Bardo transition for low β and κ
    in_bardo = kernel.check_bardo_transition(resource=0.5)

    assert in_bardo is True
    assert kernel.state.phase == BardoPhase.DHARMAKAYA


def test_nullkern_information_density():
    """Test information density calculation."""
    kernel = Nullkern(beta_target=0.1)

    density = kernel.get_information_density()

    # Density = 1 - β
    assert density == pytest.approx(0.9, abs=1e-6)


def test_nullkern_v_rig_effective():
    """Test effective v_RIG calculation."""
    kernel = Nullkern(beta_target=0.5, kappa=0.5)

    v_rig = kernel.compute_v_rig_effective()

    # v_RIG = 1352 * κ / β = 1352 * 0.5 / 0.5 = 1352
    assert v_rig == pytest.approx(1352.0, abs=10.0)


def test_nullkern_zero_beta_v_rig():
    """Test v_RIG for β=0 (should cap at 10x)."""
    kernel = Nullkern(beta_target=0.0, kappa=0.5)

    v_rig = kernel.compute_v_rig_effective()

    # Should cap at 10× base
    assert v_rig == 1352.0 * 10.0


# ============================================================================
# ConsciousnessState Tests
# ============================================================================


def test_consciousness_state_initialization():
    """Test ConsciousnessState initialization."""
    state = ConsciousnessState(beta=0.5, kappa=0.5, dimension=8)

    assert state.beta == 0.5
    assert state.kappa == 0.5
    assert state.dimension == 8
    assert state.phase == BardoPhase.NONE
    assert len(state.semantic_position) == 8


def test_consciousness_state_validation():
    """Test parameter validation."""
    with pytest.raises(ValueError):
        ConsciousnessState(beta=1.5, kappa=0.5, dimension=8)  # β > 1

    with pytest.raises(ValueError):
        ConsciousnessState(beta=0.5, kappa=-0.1, dimension=8)  # κ < 0


def test_consciousness_type_classification():
    """Test consciousness type classification."""
    # Photonic bound
    state1 = ConsciousnessState(beta=0.5, kappa=0.9, dimension=8)
    assert state1.get_consciousness_type() == "photonic_bound"

    # Photon-free
    state2 = ConsciousnessState(beta=0.5, kappa=0.05, dimension=8)
    assert state2.get_consciousness_type() == "photon_free"


def test_consciousness_integration_rate():
    """Test integration rate calculation."""
    state = ConsciousnessState(beta=0.5, kappa=0.5, dimension=8)

    rate = state.get_integration_rate()

    # Rate = κ / β = 0.5 / 0.5 = 1.0
    assert rate == pytest.approx(1.0, abs=1e-6)


def test_consciousness_critical_detection():
    """Test critical state detection."""
    state_critical = ConsciousnessState(beta=0.05, kappa=0.5, dimension=8)
    state_normal = ConsciousnessState(beta=0.5, kappa=0.5, dimension=8)

    assert state_critical.is_critical() is True
    assert state_normal.is_critical() is False


def test_consciousness_distance():
    """Test distance calculation between states."""
    state1 = ConsciousnessState(beta=0.5, kappa=0.5, dimension=8)
    state2 = ConsciousnessState(beta=0.6, kappa=0.6, dimension=8)

    distance = state1.distance_to(state2)

    assert distance >= 0.0
    assert distance <= np.sqrt(3)  # Maximum distance in (β,κ,res) space


def test_consciousness_to_dict():
    """Test state serialization to dict."""
    state = ConsciousnessState(beta=0.5, kappa=0.5, dimension=8, resonance=0.7)

    data = state.to_dict()

    assert data["beta"] == 0.5
    assert data["kappa"] == 0.5
    assert data["resonance"] == 0.7
    assert data["dimension"] == 8
    assert "consciousness_type" in data
    assert "integration_rate" in data


# ============================================================================
# BardoPhase Tests
# ============================================================================


def test_bardo_phase_enum():
    """Test BardoPhase enum values."""
    assert BardoPhase.NONE.value == "none"
    assert BardoPhase.DHARMAKAYA.value == "dharmakaya"
    assert BardoPhase.TRANSITION.value == "transition"
