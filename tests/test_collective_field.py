"""
Comprehensive tests for Collective Field Module (V7 Phase 2)

Tests the multi-agent semantic field coupling implementation including:
- Agent class (semantic positioning, distance calculations)
- CollectiveField class (κ_field, β_sync, v_collective)
- Distance matrix calculations
- Consensus detection

Usage:
    pytest tests/test_collective_field.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from models.collective_field import (  # noqa: E402
    Agent,
    CollectiveField,
    calculate_semantic_distance_matrix,
    detect_consensus,
)

# ============================================================================
# Agent Class Tests
# ============================================================================


def test_agent_initialization_default():
    """Test agent initialization with default parameters"""
    agent = Agent("test_agent")

    assert agent.name == "test_agent"
    assert agent.resonance == 0.5
    assert agent.dimension == 8
    assert len(agent.semantic_position) == 8
    assert np.isclose(np.linalg.norm(agent.semantic_position), 1.0)


def test_agent_initialization_custom():
    """Test agent initialization with custom parameters"""
    position = np.array([1.0, 0.0, 0.0, 0.0])
    agent = Agent(
        "custom_agent",
        semantic_position=position,
        resonance=0.8,
        dimension=4,
    )

    assert agent.name == "custom_agent"
    assert agent.resonance == 0.8
    assert agent.dimension == 4
    assert np.array_equal(agent.semantic_position, position)


def test_agent_resonance_clamping():
    """Test that resonance is clamped to [0, 1]"""
    agent1 = Agent("agent1", resonance=-0.5)
    assert agent1.resonance == 0.0

    agent2 = Agent("agent2", resonance=1.5)
    assert agent2.resonance == 1.0


def test_agent_position_dimension_mismatch():
    """Test error when position dimension doesn't match"""
    position = np.array([1.0, 0.0])
    with pytest.raises(ValueError, match="semantic_position must have dimension"):
        Agent("agent", semantic_position=position, dimension=4)


def test_agent_semantic_distance():
    """Test semantic distance calculation between agents"""
    # Identical positions
    pos = np.array([1.0, 0.0, 0.0, 0.0])
    agent1 = Agent("a1", semantic_position=pos, dimension=4)
    agent2 = Agent("a2", semantic_position=pos, dimension=4)
    assert np.isclose(agent1.semantic_distance(agent2), 0.0)

    # Opposite positions
    pos1 = np.array([1.0, 0.0, 0.0, 0.0])
    pos2 = np.array([-1.0, 0.0, 0.0, 0.0])
    agent1 = Agent("a1", semantic_position=pos1, dimension=4)
    agent2 = Agent("a2", semantic_position=pos2, dimension=4)
    assert np.isclose(agent1.semantic_distance(agent2), 2.0)

    # Orthogonal positions
    pos1 = np.array([1.0, 0.0, 0.0, 0.0])
    pos2 = np.array([0.0, 1.0, 0.0, 0.0])
    agent1 = Agent("a1", semantic_position=pos1, dimension=4)
    agent2 = Agent("a2", semantic_position=pos2, dimension=4)
    assert np.isclose(agent1.semantic_distance(agent2), 1.0)


def test_agent_semantic_distance_dimension_mismatch():
    """Test error when calculating distance between agents with different dimensions"""
    agent1 = Agent("a1", dimension=4)
    agent2 = Agent("a2", dimension=8)

    with pytest.raises(ValueError, match="Agents must have same semantic dimension"):
        agent1.semantic_distance(agent2)


def test_agent_update_position():
    """Test agent position update toward target"""
    pos = np.array([1.0, 0.0, 0.0, 0.0])
    target = np.array([0.0, 1.0, 0.0, 0.0])
    agent = Agent("agent", semantic_position=pos, dimension=4)

    initial_distance = np.linalg.norm(pos - target)
    agent.update_position(target, learning_rate=0.5)

    # Should move toward target
    new_distance = np.linalg.norm(agent.semantic_position - target)
    assert new_distance < initial_distance

    # Should remain on unit sphere
    assert np.isclose(np.linalg.norm(agent.semantic_position), 1.0)


def test_agent_repr():
    """Test agent string representation"""
    agent = Agent("test", resonance=0.75)
    repr_str = repr(agent)

    assert "Agent" in repr_str
    assert "test" in repr_str
    assert "0.75" in repr_str


# ============================================================================
# CollectiveField Class Tests
# ============================================================================


def test_collective_field_initialization_empty():
    """Test collective field initialization without agents"""
    field = CollectiveField(v_rig=1.5, dimension=4)

    assert len(field.agents) == 0
    assert field.v_rig == 1.5
    assert field.dimension == 4


def test_collective_field_initialization_with_agents():
    """Test collective field initialization with agents"""
    agents = [Agent(f"agent_{i}", dimension=4) for i in range(3)]
    field = CollectiveField(agents=agents, dimension=4)

    assert len(field.agents) == 3
    assert field.dimension == 4


def test_collective_field_add_agent():
    """Test adding agent to field"""
    field = CollectiveField(dimension=4)
    agent = Agent("agent1", dimension=4)

    field.add_agent(agent)
    assert len(field.agents) == 1
    assert field.agents[0] == agent


def test_collective_field_add_agent_dimension_mismatch():
    """Test error when adding agent with wrong dimension"""
    field = CollectiveField(dimension=4)
    agent = Agent("agent", dimension=8)

    with pytest.raises(ValueError, match="dimension.*does not match"):
        field.add_agent(agent)


def test_collective_field_kappa_pairwise_identical():
    """Test κ_field calculation for identical agents (perfect coupling)"""
    pos = np.array([1.0, 0.0, 0.0, 0.0])
    agents = [Agent(f"a{i}", semantic_position=pos, dimension=4) for i in range(3)]
    field = CollectiveField(agents=agents, dimension=4)

    kappa = field.calculate_kappa_field(mode="pairwise")
    assert np.isclose(kappa, 1.0)


def test_collective_field_kappa_pairwise_diverse():
    """Test κ_field calculation for diverse agents"""
    positions = [
        np.array([1.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 1.0, 0.0]),
    ]
    agents = [Agent(f"a{i}", semantic_position=pos, dimension=4) for i, pos in enumerate(positions)]
    field = CollectiveField(agents=agents, dimension=4)

    kappa = field.calculate_kappa_field(mode="pairwise")
    # Orthogonal agents should have moderate coupling
    assert 0.0 < kappa < 1.0


def test_collective_field_kappa_centroid():
    """Test κ_field calculation using centroid method"""
    positions = [
        np.array([1.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0, 0.0]),
    ]
    agents = [Agent(f"a{i}", semantic_position=pos, dimension=4) for i, pos in enumerate(positions)]
    field = CollectiveField(agents=agents, dimension=4)

    kappa = field.calculate_kappa_field(mode="centroid")
    assert 0.0 <= kappa <= 1.0


def test_collective_field_kappa_weighted():
    """Test κ_field calculation using weighted method"""
    positions = [
        np.array([1.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0, 0.0]),
    ]
    agents = [
        Agent("a1", semantic_position=positions[0], resonance=0.9, dimension=4),
        Agent("a2", semantic_position=positions[1], resonance=0.1, dimension=4),
    ]
    field = CollectiveField(agents=agents, dimension=4)

    kappa = field.calculate_kappa_field(mode="weighted")
    assert 0.0 <= kappa <= 1.0


def test_collective_field_kappa_single_agent():
    """Test κ_field for single agent (trivially coupled)"""
    agent = Agent("agent", dimension=4)
    field = CollectiveField(agents=[agent], dimension=4)

    kappa = field.calculate_kappa_field()
    assert kappa == 1.0


def test_collective_field_kappa_empty():
    """Test κ_field for empty field"""
    field = CollectiveField(dimension=4)

    kappa = field.calculate_kappa_field()
    assert kappa == 1.0


def test_collective_field_kappa_invalid_mode():
    """Test error for invalid κ_field mode"""
    agents = [Agent(f"agent_{i}", dimension=4) for i in range(2)]
    field = CollectiveField(agents=agents, dimension=4)

    with pytest.raises(ValueError, match="Unknown mode"):
        field.calculate_kappa_field(mode="invalid")


def test_collective_field_beta_sync():
    """Test β_sync calculation"""
    positions = [
        np.array([1.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 1.0, 0.0]),
    ]
    agents = [Agent(f"a{i}", semantic_position=pos, dimension=4) for i, pos in enumerate(positions)]
    field = CollectiveField(agents=agents, dimension=4)

    beta_sync = field.calculate_beta_sync(timesteps=5, learning_rate=0.2)

    # Should be positive
    assert beta_sync > 0.0
    # Should be in reasonable range
    assert 0.1 <= beta_sync <= 10.0


def test_collective_field_beta_sync_converged():
    """Test β_sync for already converged agents"""
    pos = np.array([1.0, 0.0, 0.0, 0.0])
    agents = [Agent(f"a{i}", semantic_position=pos, dimension=4) for i in range(3)]
    field = CollectiveField(agents=agents, dimension=4)

    beta_sync = field.calculate_beta_sync()
    # Already converged -> minimal resistance
    assert beta_sync == 0.1


def test_collective_field_beta_sync_single_agent():
    """Test β_sync for single agent"""
    agent = Agent("agent", dimension=4)
    field = CollectiveField(agents=[agent], dimension=4)

    beta_sync = field.calculate_beta_sync()
    assert beta_sync == 0.1


def test_collective_field_v_collective():
    """Test v_collective calculation"""
    positions = [
        np.array([1.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0, 0.0]),
    ]
    agents = [Agent(f"a{i}", semantic_position=pos, dimension=4) for i, pos in enumerate(positions)]
    field = CollectiveField(agents=agents, v_rig=1.0, dimension=4)

    v_collective = field.calculate_v_collective()

    # Should be positive
    assert v_collective > 0.0
    # Formula: v_RIG × κ × (1 / β_sync)
    # With v_RIG=1.0, result should be reasonable
    assert 0.0 < v_collective < 100.0


def test_collective_field_v_collective_perfect_coupling():
    """Test v_collective for perfectly coupled agents"""
    pos = np.array([1.0, 0.0, 0.0, 0.0])
    agents = [Agent(f"a{i}", semantic_position=pos, dimension=4) for i in range(3)]
    field = CollectiveField(agents=agents, v_rig=1.0, dimension=4)

    v_collective = field.calculate_v_collective()

    # Perfect coupling (κ=1) + minimal β_sync (0.1) -> high velocity
    assert v_collective >= 1.0


def test_collective_field_get_state():
    """Test comprehensive field state retrieval"""
    agents = [Agent(f"agent_{i}", dimension=4) for i in range(3)]
    field = CollectiveField(agents=agents, v_rig=1.5, dimension=4)

    state = field.get_field_state()

    # Check required fields
    assert "n_agents" in state
    assert state["n_agents"] == 3

    assert "v_rig" in state
    assert state["v_rig"] == 1.5

    assert "kappa_field_pairwise" in state
    assert "kappa_field_centroid" in state
    assert "kappa_field_weighted" in state
    assert "beta_sync" in state
    assert "v_collective" in state

    assert "agents" in state
    assert len(state["agents"]) == 3

    # Check agent data structure
    agent_data = state["agents"][0]
    assert "name" in agent_data
    assert "resonance" in agent_data
    assert "semantic_position" in agent_data
    assert isinstance(agent_data["semantic_position"], list)


def test_collective_field_repr():
    """Test field string representation"""
    agents = [Agent(f"agent_{i}", dimension=4) for i in range(3)]
    field = CollectiveField(agents=agents, v_rig=1.5, dimension=4)

    repr_str = repr(field)

    assert "CollectiveField" in repr_str
    assert "n_agents=3" in repr_str
    assert "1.5" in repr_str


# ============================================================================
# Utility Function Tests
# ============================================================================


def test_distance_matrix_calculation():
    """Test pairwise semantic distance matrix"""
    positions = [
        np.array([1.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 1.0, 0.0]),
    ]
    agents = [Agent(f"a{i}", semantic_position=pos, dimension=4) for i, pos in enumerate(positions)]

    matrix = calculate_semantic_distance_matrix(agents)

    # Check shape
    assert matrix.shape == (3, 3)

    # Check symmetry
    assert np.allclose(matrix, matrix.T)

    # Check diagonal is zero
    assert np.allclose(np.diag(matrix), 0.0)

    # Check orthogonal distances
    # Orthogonal unit vectors have cosine similarity 0, distance = 1
    assert np.isclose(matrix[0, 1], 1.0)
    assert np.isclose(matrix[0, 2], 1.0)
    assert np.isclose(matrix[1, 2], 1.0)


def test_detect_consensus_achieved():
    """Test consensus detection when agents are close"""
    pos = np.array([1.0, 0.0, 0.0, 0.0])
    agents = [Agent(f"a{i}", semantic_position=pos, dimension=4) for i in range(3)]

    has_consensus, max_dist = detect_consensus(agents, threshold=0.2)

    assert has_consensus is True
    assert np.isclose(max_dist, 0.0)


def test_detect_consensus_not_achieved():
    """Test consensus detection when agents are far apart"""
    positions = [
        np.array([1.0, 0.0, 0.0, 0.0]),
        np.array([-1.0, 0.0, 0.0, 0.0]),
    ]
    agents = [Agent(f"a{i}", semantic_position=pos, dimension=4) for i, pos in enumerate(positions)]

    has_consensus, max_dist = detect_consensus(agents, threshold=0.2)

    assert not has_consensus  # Use not instead of is False for numpy bool
    assert np.isclose(max_dist, 2.0)


def test_detect_consensus_single_agent():
    """Test consensus with single agent (trivially true)"""
    agent = Agent("agent", dimension=4)

    has_consensus, max_dist = detect_consensus([agent])

    assert has_consensus is True
    assert max_dist == 0.0


def test_detect_consensus_empty():
    """Test consensus with no agents"""
    has_consensus, max_dist = detect_consensus([])

    assert has_consensus is True
    assert max_dist == 0.0


# ============================================================================
# Integration Tests
# ============================================================================


def test_field_convergence_integration():
    """Test full convergence workflow"""
    # Create divergent agents
    positions = [
        np.array([1.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 1.0, 0.0]),
    ]
    agents = [Agent(f"a{i}", semantic_position=pos, dimension=4) for i, pos in enumerate(positions)]
    field = CollectiveField(agents=agents, dimension=4)

    # Initial state
    initial_kappa = field.calculate_kappa_field()
    assert initial_kappa < 1.0

    # Simulate convergence
    for _ in range(10):
        centroid = field._calculate_centroid()
        for agent in field.agents:
            agent.update_position(centroid, learning_rate=0.1, field=field)

    # Final state
    final_kappa = field.calculate_kappa_field()
    assert final_kappa > initial_kappa


def test_multi_agent_semantic_coupling():
    """Test complex multi-agent coupling scenario"""
    # Create 5 agents with varying resonances
    agents = [
        Agent("a1", resonance=0.9, dimension=8),
        Agent("a2", resonance=0.7, dimension=8),
        Agent("a3", resonance=0.5, dimension=8),
        Agent("a4", resonance=0.3, dimension=8),
        Agent("a5", resonance=0.1, dimension=8),
    ]
    field = CollectiveField(agents=agents, v_rig=1.0, dimension=8)

    # Calculate all coupling measures
    kappa_pairwise = field.calculate_kappa_field(mode="pairwise")
    kappa_centroid = field.calculate_kappa_field(mode="centroid")
    kappa_weighted = field.calculate_kappa_field(mode="weighted")
    beta_sync = field.calculate_beta_sync()
    v_collective = field.calculate_v_collective()

    # All measures should be in valid ranges
    assert 0.0 <= kappa_pairwise <= 1.0
    assert 0.0 <= kappa_centroid <= 1.0
    assert 0.0 <= kappa_weighted <= 1.0
    assert beta_sync > 0.0
    assert v_collective > 0.0

    # Weighted coupling should differ from unweighted
    # (since resonances vary)
    assert kappa_weighted != kappa_pairwise


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
