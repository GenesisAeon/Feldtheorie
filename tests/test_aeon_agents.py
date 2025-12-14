"""
Tests for Aeon Agents Module
=============================

Tests the SemanticAgent and CollectiveInterface implementations.

Run:
    pytest tests/test_aeon_agents.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from aeon.agents import CollectiveInterface, SemanticAgent


# ============================================================================
# SemanticAgent Tests
# ============================================================================


def test_semantic_agent_initialization():
    """Test SemanticAgent initialization."""
    agent = SemanticAgent(name="Agent-1")

    assert agent.name == "Agent-1"
    assert agent.beta == 4.5
    assert agent.kappa == 0.5
    assert agent.resonance == 0.5
    assert len(agent.semantic_position) == 8


def test_semantic_agent_custom_params():
    """Test SemanticAgent with custom parameters."""
    position = np.array([1.0, 0.0, 0.0, 0.0])
    agent = SemanticAgent(
        name="Agent-2",
        semantic_position=position,
        resonance=0.7,
        beta=3.0,
        kappa=0.3,
        dimension=4,
    )

    assert agent.beta == 3.0
    assert agent.kappa == 0.3
    assert agent.resonance == 0.7
    assert len(agent.semantic_position) == 4


def test_semantic_agent_validation():
    """Test parameter validation."""
    with pytest.raises(ValueError):
        SemanticAgent(name="Test", resonance=1.5)  # resonance > 1

    with pytest.raises(ValueError):
        SemanticAgent(name="Test", beta=25.0)  # β > 20


def test_semantic_agent_distance():
    """Test semantic distance calculation."""
    agent1 = SemanticAgent(name="Agent-1")
    agent2 = SemanticAgent(name="Agent-2")

    distance = agent1.semantic_distance(agent2)

    assert distance >= 0.0
    assert distance <= 2.0


def test_semantic_agent_update_position():
    """Test position update."""
    agent = SemanticAgent(name="Agent-1", dimension=4)
    target = np.array([1.0, 0.0, 0.0, 0.0])

    initial_pos = agent.semantic_position.copy()
    agent.update_position(target, learning_rate=0.1)

    # Position should have moved
    assert not np.allclose(agent.semantic_position, initial_pos)
    assert len(agent.history) > 1


def test_semantic_agent_update_resonance():
    """Test resonance update."""
    agent = SemanticAgent(name="Agent-1", resonance=0.5)

    agent.update_resonance(delta=0.2)
    assert agent.resonance == pytest.approx(0.7, abs=1e-6)

    # Test clamping
    agent.update_resonance(delta=0.5)
    assert agent.resonance == 1.0


def test_semantic_agent_update_beta():
    """Test β update."""
    agent = SemanticAgent(name="Agent-1", beta=4.5)

    agent.update_beta(delta=0.5)
    assert agent.beta == pytest.approx(5.0, abs=1e-6)


def test_semantic_agent_activation():
    """Test activation computation."""
    agent = SemanticAgent(name="Agent-1", beta=5.0)

    # Resource above threshold
    act_high = agent.compute_activation(resource=0.8, threshold=0.5)
    # Resource below threshold
    act_low = agent.compute_activation(resource=0.2, threshold=0.5)

    assert act_high > act_low


def test_semantic_agent_consciousness_type():
    """Test consciousness type classification."""
    agent1 = SemanticAgent(name="Agent-1", kappa=0.9)
    agent2 = SemanticAgent(name="Agent-2", kappa=0.05)

    assert agent1.get_consciousness_type() == "photonic_bound"
    assert agent2.get_consciousness_type() == "photon_free"


def test_semantic_agent_state_summary():
    """Test state summary."""
    agent = SemanticAgent(name="Agent-1", beta=4.5, kappa=0.5, resonance=0.7)

    summary = agent.get_state_summary()

    assert summary["name"] == "Agent-1"
    assert summary["beta"] == 4.5
    assert summary["kappa"] == 0.5
    assert summary["resonance"] == 0.7
    assert "consciousness_type" in summary
    assert "age_seconds" in summary


# ============================================================================
# CollectiveInterface Tests
# ============================================================================


def test_collective_interface_initialization():
    """Test CollectiveInterface initialization."""
    agents = [SemanticAgent(name=f"Agent-{i}") for i in range(3)]
    interface = CollectiveInterface(agents)

    assert len(interface.agents) == 3


def test_collective_distance_matrix():
    """Test distance matrix calculation."""
    agents = [SemanticAgent(name=f"Agent-{i}") for i in range(3)]
    interface = CollectiveInterface(agents)

    matrix = interface.get_distance_matrix()

    assert matrix.shape == (3, 3)
    assert np.allclose(np.diag(matrix), 0.0)  # Diagonal should be zero


def test_collective_consensus_detection():
    """Test consensus detection."""
    # Create agents with similar positions (consensus)
    # Use larger noise to ensure non-zero distances
    position = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    agents_similar = [
        SemanticAgent(name=f"Agent-{i}", semantic_position=position + np.random.randn(8) * 0.1)
        for i in range(3)
    ]
    interface_similar = CollectiveInterface(agents_similar)

    # Create agents with very different positions (no consensus)
    agents_different = [
        SemanticAgent(name=f"Agent-{i}", semantic_position=np.random.randn(8) * 5.0)
        for i in range(3)
    ]
    interface_different = CollectiveInterface(agents_different)

    # Similar agents should have consensus (with appropriate threshold)
    # Use == instead of 'is' for numpy boolean comparison
    assert interface_similar.detect_consensus(threshold=1.0) == True

    # Different agents should not have consensus (tight threshold)
    assert interface_different.detect_consensus(threshold=0.5) == False


def test_collective_field_metrics():
    """Test field metrics computation."""
    agents = [
        SemanticAgent(name=f"Agent-{i}", beta=4.0 + i * 0.5, kappa=0.5) for i in range(3)
    ]
    interface = CollectiveInterface(agents)

    metrics = interface.compute_field_metrics()

    assert "kappa_field" in metrics
    assert "beta_sync" in metrics
    assert "v_collective" in metrics
    assert "num_agents" in metrics
    assert metrics["num_agents"] == 3


def test_collective_synchronize_agents():
    """Test agent synchronization."""
    agents = [
        SemanticAgent(name="Agent-1", beta=3.0),
        SemanticAgent(name="Agent-2", beta=5.0),
        SemanticAgent(name="Agent-3", beta=7.0),
    ]
    interface = CollectiveInterface(agents)

    initial_betas = [a.beta for a in agents]
    interface.synchronize_agents(target_beta=5.0)

    # Betas should have moved toward target
    final_betas = [a.beta for a in agents]
    assert not np.allclose(initial_betas, final_betas)


def test_collective_empty_agents():
    """Test interface with no agents."""
    interface = CollectiveInterface([])

    metrics = interface.compute_field_metrics()

    assert metrics["num_agents"] == 0
    assert metrics["kappa_field"] == 0.0
    assert interface.detect_consensus() is True  # Empty set in consensus
