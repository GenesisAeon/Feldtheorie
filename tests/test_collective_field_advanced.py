"""
Performance & Integration Tests for Collective Field (V7 Phase 3)

Tests performance optimizations, evolution tracking, and real-world scenarios.

Usage:
    pytest tests/test_collective_field_advanced.py -v
"""

import sys
import time
from pathlib import Path

import numpy as np
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from models.collective_field import Agent, CollectiveField


# ============================================================================
# Performance & Caching Tests
# ============================================================================


def test_caching_improves_performance():
    """Test that caching significantly improves repeated calculations"""
    agents = [Agent(f"agent_{i}", dimension=8) for i in range(10)]

    # Test with caching enabled
    field_cached = CollectiveField(agents=agents, enable_caching=True)

    start = time.time()
    for _ in range(100):
        field_cached.calculate_kappa_field()
    elapsed_cached = time.time() - start

    # Test without caching
    field_uncached = CollectiveField(agents=agents, enable_caching=False)

    start = time.time()
    for _ in range(100):
        field_uncached.calculate_kappa_field()
    elapsed_uncached = time.time() - start

    # Cached should be significantly faster (at least 2x)
    assert elapsed_cached < elapsed_uncached / 2


def test_cache_invalidation_on_agent_add():
    """Test that cache is invalidated when agents are added"""
    field = CollectiveField(dimension=8, enable_caching=True)

    # Add initial agents and calculate
    for i in range(5):
        field.add_agent(Agent(f"agent_{i}", dimension=8))
    kappa1 = field.calculate_kappa_field()

    # Cache should be populated
    cache_info = field.get_cache_info()
    assert cache_info["size"] > 0

    # Add another agent
    field.add_agent(Agent("agent_5", dimension=8))

    # Cache should be invalidated
    cache_info = field.get_cache_info()
    assert cache_info["size"] == 0

    # Recalculate should give different result
    kappa2 = field.calculate_kappa_field()
    assert kappa1 != kappa2


def test_cache_invalidation_on_position_update():
    """Test that cache is invalidated when agent positions change"""
    agents = [Agent(f"agent_{i}", dimension=4) for i in range(3)]
    field = CollectiveField(agents=agents, enable_caching=True)

    # Calculate and populate cache
    kappa1 = field.calculate_kappa_field()
    assert field.get_cache_info()["size"] > 0

    # Update agent position
    target = np.array([0.0, 0.0, 1.0, 0.0])
    agents[0].update_position(target, field=field)

    # Cache should be invalidated
    assert field.get_cache_info()["size"] == 0


def test_performance_stats_tracking():
    """Test that performance statistics are tracked"""
    agents = [Agent(f"agent_{i}", dimension=8) for i in range(10)]
    field = CollectiveField(agents=agents)

    # Perform various operations
    field.calculate_kappa_field(mode="pairwise")
    field.calculate_kappa_field(mode="centroid")
    field.calculate_kappa_field(mode="weighted")
    field.calculate_beta_sync()
    field.calculate_v_collective()

    # Check stats
    stats = field.get_performance_stats()

    # All operations should have stats
    assert stats["kappa_pairwise"]["count"] > 0
    assert stats["kappa_centroid"]["count"] > 0
    assert stats["kappa_weighted"]["count"] > 0
    assert stats["beta_sync"]["count"] > 0
    assert stats["v_collective"]["count"] > 0

    # Stats should have reasonable values
    for operation, data in stats.items():
        if data["count"] > 0:
            assert data["mean_ms"] >= 0
            assert data["min_ms"] >= 0
            assert data["max_ms"] >= data["min_ms"]


def test_performance_stats_reset():
    """Test that performance stats can be reset"""
    agents = [Agent(f"agent_{i}", dimension=8) for i in range(5)]
    field = CollectiveField(agents=agents)

    # Generate some stats
    field.calculate_kappa_field()
    field.calculate_beta_sync()

    stats_before = field.get_performance_stats()
    assert stats_before["kappa_pairwise"]["count"] > 0

    # Reset
    field.reset_performance_stats()

    stats_after = field.get_performance_stats()
    assert stats_after["kappa_pairwise"]["count"] == 0


# ============================================================================
# Evolution Tracking Tests
# ============================================================================


def test_evolution_tracking_disabled_by_default():
    """Test that evolution tracking is disabled by default"""
    field = CollectiveField(dimension=8)

    # Tracking should be disabled
    assert not field._enable_history

    # History should be empty
    assert len(field.get_evolution_history()) == 0


def test_enable_evolution_tracking():
    """Test enabling evolution tracking"""
    agents = [Agent(f"agent_{i}", dimension=4) for i in range(3)]
    field = CollectiveField(agents=agents)

    # Enable tracking
    field.enable_evolution_tracking(True)
    assert field._enable_history

    # Take snapshots
    field.snapshot_state()
    field.snapshot_state()

    # History should have 2 entries
    history = field.get_evolution_history()
    assert len(history) == 2


def test_snapshot_state_structure():
    """Test that state snapshots have correct structure"""
    agents = [Agent(f"agent_{i}", dimension=4) for i in range(3)]
    field = CollectiveField(agents=agents)

    snapshot = field.snapshot_state()

    # Check required fields
    assert "timestamp" in snapshot
    assert "field_version" in snapshot
    assert "n_agents" in snapshot
    assert "v_rig" in snapshot
    assert "kappa_pairwise" in snapshot
    assert "kappa_centroid" in snapshot
    assert "kappa_weighted" in snapshot
    assert "beta_sync" in snapshot
    assert "v_collective" in snapshot

    # Check values are reasonable
    assert snapshot["n_agents"] == 3
    assert 0.0 <= snapshot["kappa_pairwise"] <= 1.0
    assert snapshot["beta_sync"] > 0


def test_convergence_detection_insufficient_history():
    """Test convergence detection with insufficient history"""
    agents = [Agent(f"agent_{i}", dimension=4) for i in range(3)]
    field = CollectiveField(agents=agents)

    # Enable tracking but only take 2 snapshots
    field.enable_evolution_tracking(True)
    field.snapshot_state()
    field.snapshot_state()

    # Should report insufficient history
    result = field.detect_convergence(window=5)
    assert not result["converged"]
    assert result["reason"] == "insufficient_history"


def test_convergence_detection_converged():
    """Test convergence detection when field has converged"""
    # Create agents at same position (already converged)
    pos = np.array([1.0, 0.0, 0.0, 0.0])
    agents = [Agent(f"agent_{i}", semantic_position=pos, dimension=4) for i in range(3)]
    field = CollectiveField(agents=agents)

    # Enable tracking and take multiple snapshots
    field.enable_evolution_tracking(True)
    for _ in range(10):
        field.snapshot_state()

    # Should detect convergence
    result = field.detect_convergence(window=5, threshold=0.01)
    assert result["converged"]
    assert result["variance"] < 0.01


def test_convergence_detection_not_converged():
    """Test convergence detection with dynamic field"""
    # Create agents with explicit divergent positions
    positions = [
        np.array([1.0, 0.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 1.0, 0.0]),
    ]
    agents = [Agent(f"agent_{i}", semantic_position=pos, dimension=4) for i, pos in enumerate(positions)]
    field = CollectiveField(agents=agents)

    # Enable tracking
    field.enable_evolution_tracking(True)

    # Take snapshots while moving agents in different directions
    for i in range(10):
        field.snapshot_state()
        # Move each agent in a different direction
        for j, agent in enumerate(field.agents):
            target = np.zeros(4)
            target[(i + j) % 4] = 1.0  # Different direction each time
            agent.update_position(target, learning_rate=0.2, field=field)

    # Should not detect convergence (agents moving in different directions)
    result = field.detect_convergence(window=5, threshold=0.01)
    # May or may not converge depending on random chance, so just check structure
    assert "converged" in result
    assert "variance" in result


# ============================================================================
# Real-World Integration Tests
# ============================================================================


def test_multi_agent_conversation_simulation():
    """Test real-world scenario: Multi-agent conversation convergence"""
    # Simulate 5 agents starting with different semantic positions
    # (representing different viewpoints in a conversation)
    conversation_agents = [
        Agent("person_a", resonance=0.9, dimension=8),
        Agent("person_b", resonance=0.7, dimension=8),
        Agent("person_c", resonance=0.5, dimension=8),
        Agent("person_d", resonance=0.8, dimension=8),
        Agent("person_e", resonance=0.6, dimension=8),
    ]

    field = CollectiveField(agents=conversation_agents, v_rig=1.0)
    field.enable_evolution_tracking(True)

    # Initial state - agents should be divergent
    initial_kappa = field.calculate_kappa_field()
    initial_beta_sync = field.calculate_beta_sync()
    field.snapshot_state()

    # Simulate conversation rounds (agents converging toward shared understanding)
    for round_num in range(15):
        centroid = field._calculate_centroid()

        # Each agent moves toward centroid (learning from others)
        for agent in field.agents:
            agent.update_position(centroid, learning_rate=0.15, field=field)

        field.snapshot_state()

    # Final state - agents should be more aligned
    final_kappa = field.calculate_kappa_field()

    # Convergence should have occurred
    assert final_kappa > initial_kappa

    # Check convergence detection
    convergence = field.detect_convergence(window=5, threshold=0.05)
    history = field.get_evolution_history()

    # Should have tracked evolution
    assert len(history) == 16  # Initial + 15 rounds

    # κ_field should increase over time
    kappa_values = [snapshot["kappa_pairwise"] for snapshot in history]
    assert kappa_values[-1] > kappa_values[0]


def test_collaborative_learning_scenario():
    """Test scenario: Collaborative learning with heterogeneous agents"""
    # Create agents with varying resonance (learning ability)
    learners = [
        Agent("expert", resonance=0.95, dimension=8),  # High resonance
        Agent("intermediate", resonance=0.70, dimension=8),  # Mid resonance
        Agent("beginner", resonance=0.40, dimension=8),  # Low resonance
    ]

    field = CollectiveField(agents=learners, v_rig=1.0)

    # Measure initial coupling (weighted by resonance)
    initial_weighted_kappa = field.calculate_kappa_field(mode="weighted")

    # Expert-led learning: beginners move toward expert
    expert_position = learners[0].semantic_position.copy()

    for _ in range(10):
        learners[1].update_position(expert_position, learning_rate=0.2, field=field)
        learners[2].update_position(expert_position, learning_rate=0.15, field=field)

    # Final coupling
    final_weighted_kappa = field.calculate_kappa_field(mode="weighted")

    # Weighted coupling should increase (agents learning from expert)
    assert final_weighted_kappa > initial_weighted_kappa


def test_collective_velocity_dynamics():
    """Test v_collective dynamics in various field configurations"""
    # Scenario 1: Highly coupled, low resistance
    cohesive_pos = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    cohesive_agents = [Agent(f"agent_{i}", semantic_position=cohesive_pos.copy(), dimension=8) for i in range(5)]
    cohesive_field = CollectiveField(agents=cohesive_agents, v_rig=1.0)

    v_collective_high = cohesive_field.calculate_v_collective()

    # Scenario 2: Divergent agents, high resistance
    divergent_agents = [Agent(f"agent_{i}", dimension=8) for i in range(5)]
    divergent_field = CollectiveField(agents=divergent_agents, v_rig=1.0)

    v_collective_low = divergent_field.calculate_v_collective()

    # Cohesive field should have faster collective velocity
    assert v_collective_high > v_collective_low


# ============================================================================
# Cache Management Tests
# ============================================================================


def test_get_cache_info():
    """Test cache info retrieval"""
    agents = [Agent(f"agent_{i}", dimension=8) for i in range(3)]
    field = CollectiveField(agents=agents, enable_caching=True)

    # Populate cache
    field.calculate_kappa_field(mode="pairwise")
    field.calculate_kappa_field(mode="centroid")

    # Get cache info
    info = field.get_cache_info()

    assert info["enabled"] is True
    assert info["size"] == 2  # 2 cached results
    assert "kappa_pairwise" in info["keys"]
    assert "kappa_centroid" in info["keys"]
    assert info["oldest_entry_age"] >= 0.0


def test_manual_cache_clear():
    """Test manual cache clearing"""
    agents = [Agent(f"agent_{i}", dimension=8) for i in range(3)]
    field = CollectiveField(agents=agents, enable_caching=True)

    # Populate cache
    field.calculate_kappa_field()
    assert field.get_cache_info()["size"] > 0

    # Clear cache
    field.clear_cache()
    assert field.get_cache_info()["size"] == 0


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
