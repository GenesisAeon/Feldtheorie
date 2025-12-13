"""
Tests for Aeon Shell Module
============================

Tests the AeonShell containment and evolution layer.

Run:
    pytest tests/test_aeon_shell.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from aeon import AeonShell, Nullkern, SemanticAgent
from aeon.shell.evolution import EvolutionTracker


# ============================================================================
# AeonShell Tests
# ============================================================================


def test_shell_initialization():
    """Test AeonShell initialization."""
    kernel = Nullkern()
    shell = AeonShell(kernel=kernel)

    assert shell.kernel == kernel
    assert shell.safeguards_active is True
    assert len(shell.agents) == 0
    assert len(shell.trajectory) > 0  # Initial state recorded


def test_shell_add_agent():
    """Test adding agents to shell."""
    kernel = Nullkern()
    shell = AeonShell(kernel=kernel)

    agent = SemanticAgent(name="Agent-1")
    shell.add_agent(agent)

    assert len(shell.agents) == 1
    assert shell.agents[0] == agent


def test_shell_remove_agent():
    """Test removing agents from shell."""
    kernel = Nullkern()
    shell = AeonShell(kernel=kernel)

    agent = SemanticAgent(name="Agent-1")
    shell.add_agent(agent)
    removed = shell.remove_agent(agent)

    assert removed is True
    assert len(shell.agents) == 0


def test_shell_max_agents():
    """Test max_agents limit."""
    kernel = Nullkern()
    shell = AeonShell(kernel=kernel, max_agents=2)

    shell.add_agent(SemanticAgent(name="Agent-1"))
    shell.add_agent(SemanticAgent(name="Agent-2"))

    with pytest.raises(ValueError):
        shell.add_agent(SemanticAgent(name="Agent-3"))


def test_shell_evolve():
    """Test shell evolution."""
    kernel = Nullkern()
    shell = AeonShell(kernel=kernel)

    initial_length = len(shell.trajectory)
    shell.evolve(steps=5, delta_time=0.01)

    # Trajectory should have grown
    assert len(shell.trajectory) > initial_length


def test_shell_safeguards():
    """Test safeguard monitoring."""
    kernel = Nullkern(beta_target=0.8, kappa=0.1)  # High β, low κ → negative ζ
    shell = AeonShell(kernel=kernel, enable_safeguards=True)

    # Evolve with low resource (triggers negative ζ)
    for _ in range(10):
        shell.evolve(steps=1)
        if len(shell.safeguard_violations) > 0:
            break

    # Should have some violations
    assert len(shell.safeguard_violations) > 0


def test_shell_trajectory():
    """Test trajectory tracking."""
    kernel = Nullkern()
    shell = AeonShell(kernel=kernel)

    shell.evolve(steps=10)
    trajectory = shell.get_trajectory()

    assert len(trajectory) >= 10
    assert all("beta" in p for p in trajectory)
    assert all("kappa" in p for p in trajectory)


def test_shell_collective_metrics():
    """Test collective field metrics."""
    kernel = Nullkern()
    shell = AeonShell(kernel=kernel)

    # Add agents
    for i in range(3):
        shell.add_agent(SemanticAgent(name=f"Agent-{i}"))

    metrics = shell.get_collective_field_metrics()

    assert "kappa_field" in metrics
    assert "beta_sync" in metrics
    assert "num_agents" in metrics
    assert metrics["num_agents"] == 3


def test_shell_summary():
    """Test shell summary."""
    kernel = Nullkern()
    shell = AeonShell(kernel=kernel)
    shell.add_agent(SemanticAgent(name="Agent-1"))

    summary = shell.get_shell_summary()

    assert "kernel_state" in summary
    assert "num_agents" in summary
    assert summary["num_agents"] == 1
    assert "trajectory_length" in summary
    assert "safeguards_active" in summary


# ============================================================================
# EvolutionTracker Tests
# ============================================================================


def test_evolution_tracker_initialization():
    """Test EvolutionTracker initialization."""
    trajectory = [
        {"beta": 0.5, "kappa": 0.5, "resonance": 0.5, "phase": "none", "timestamp": 0.0}
    ]
    tracker = EvolutionTracker(trajectory)

    assert len(tracker.trajectory) == 1


def test_evolution_tracker_beta_evolution():
    """Test β-evolution extraction."""
    trajectory = [
        {"beta": 0.1, "kappa": 0.5, "resonance": 0.5, "phase": "none", "timestamp": 0.0},
        {"beta": 0.2, "kappa": 0.5, "resonance": 0.5, "phase": "none", "timestamp": 1.0},
        {"beta": 0.3, "kappa": 0.5, "resonance": 0.5, "phase": "none", "timestamp": 2.0},
    ]
    tracker = EvolutionTracker(trajectory)

    betas = tracker.get_beta_evolution()

    assert len(betas) == 3
    assert np.allclose(betas, [0.1, 0.2, 0.3])


def test_evolution_tracker_phase_transitions():
    """Test phase transition detection."""
    trajectory = [
        {"beta": 0.5, "kappa": 0.5, "resonance": 0.5, "phase": "none", "timestamp": 0.0},
        {"beta": 0.1, "kappa": 0.1, "resonance": 0.5, "phase": "dharmakaya", "timestamp": 1.0},
        {"beta": 0.2, "kappa": 0.2, "resonance": 0.5, "phase": "becoming", "timestamp": 2.0},
    ]
    tracker = EvolutionTracker(trajectory)

    transitions = tracker.get_phase_transitions()

    assert len(transitions) == 2
    assert transitions[0]["from_phase"] == "none"
    assert transitions[0]["to_phase"] == "dharmakaya"


def test_evolution_tracker_critical_events():
    """Test critical event detection."""
    trajectory = [
        {"beta": 0.5, "kappa": 0.5, "resonance": 0.5, "phase": "none", "timestamp": 0.0},
        {"beta": 0.05, "kappa": 0.5, "resonance": 0.5, "phase": "none", "timestamp": 1.0},
        {"beta": 0.5, "kappa": 0.05, "resonance": 0.5, "phase": "none", "timestamp": 2.0},
    ]
    tracker = EvolutionTracker(trajectory)

    events = tracker.get_critical_events()

    assert len(events) >= 2  # Low β and low κ


def test_evolution_tracker_statistics():
    """Test trajectory statistics."""
    trajectory = [
        {"beta": 0.1, "kappa": 0.5, "resonance": 0.5, "phase": "none", "timestamp": 0.0},
        {"beta": 0.2, "kappa": 0.5, "resonance": 0.5, "phase": "none", "timestamp": 1.0},
        {"beta": 0.3, "kappa": 0.5, "resonance": 0.5, "phase": "none", "timestamp": 2.0},
    ]
    tracker = EvolutionTracker(trajectory)

    stats = tracker.get_statistics()

    assert stats["length"] == 3
    assert stats["beta_mean"] == pytest.approx(0.2, abs=1e-6)
    assert stats["beta_min"] == 0.1
    assert stats["beta_max"] == 0.3


def test_evolution_tracker_export():
    """Test export for visualization."""
    trajectory = [
        {
            "beta": 0.5,
            "kappa": 0.5,
            "resonance": 0.5,
            "phase": "none",
            "timestamp": 0.0,
            "information_density": 0.5,
            "v_rig_effective": 1352.0,
        }
    ]
    tracker = EvolutionTracker(trajectory)

    data = tracker.export_for_visualization()

    assert "time" in data
    assert "beta" in data
    assert "kappa" in data
    assert "phase_transitions" in data
    assert "critical_events" in data
    assert "statistics" in data
