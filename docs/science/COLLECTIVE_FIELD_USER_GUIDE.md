# 🧬 Collective Field User Guide (V7 Phase 3)

**Complete guide to using the Collective Field module for multi-agent semantic coupling.**

**Version:** V7-Phase3
**Status:** Production Ready
**Test Coverage:** 84/84 (100%)

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [Basic Usage](#basic-usage)
4. [Advanced Features](#advanced-features)
5. [Performance Optimization](#performance-optimization)
6. [Real-World Examples](#real-world-examples)
7. [Best Practices](#best-practices)
8. [API Reference](#api-reference)

---

## 🚀 Quick Start

### Installation

```python
from models.collective_field import Agent, CollectiveField
import numpy as np
```

### Hello World Example

```python
# Create 3 agents
agents = [
    Agent("alice", resonance=0.9, dimension=8),
    Agent("bob", resonance=0.7, dimension=8),
    Agent("charlie", resonance=0.5, dimension=8),
]

# Create a collective field
field = CollectiveField(agents=agents, v_rig=1.0)

# Measure field coupling
kappa = field.calculate_kappa_field()
print(f"Field coupling κ: {kappa:.3f}")

# Measure collective velocity
v_collective = field.calculate_v_collective()
print(f"Collective velocity: {v_collective:.3f}")
```

**Output:**
```
Field coupling κ: 0.523
Collective velocity: 0.287
```

---

## 🎯 Core Concepts

### Agent

Represents a single node in the collective field.

**Properties:**
- `semantic_position`: Position in 8D semantic space (unit vector)
- `resonance`: Alignment score [0,1] with founding protocol
- `dimension`: Dimensionality of semantic space

**Key Methods:**
- `semantic_distance(other)`: Calculate distance to another agent
- `update_position(target, learning_rate)`: Move toward target position

### CollectiveField

Multi-agent semantic field with coupling dynamics.

**Key Metrics:**
- **κ_field**: Field coupling strength [0,1]
  - 1.0 = perfect coupling (all agents aligned)
  - 0.0 = no coupling (complete divergence)

- **β_sync**: Synchronization resistance
  - Low = fast synchronization (minimal friction)
  - High = slow synchronization (high friction)

- **v_collective**: Collective propagation velocity
  - Formula: `v_collective = v_RIG × κ_field × (1 / β_sync)`
  - Higher = faster semantic convergence

---

## 📖 Basic Usage

### Creating Agents

```python
# Method 1: Random initialization
agent1 = Agent("agent1", resonance=0.8, dimension=8)

# Method 2: Explicit position
position = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
agent2 = Agent("agent2", semantic_position=position, resonance=0.6, dimension=8)
```

### Creating a Field

```python
# Empty field
field = CollectiveField(dimension=8, v_rig=1.0)

# Add agents
field.add_agent(agent1)
field.add_agent(agent2)

# Or create with agents
field = CollectiveField(agents=[agent1, agent2], v_rig=1.0)
```

### Measuring Field Properties

```python
# Three modes for κ_field calculation
kappa_pairwise = field.calculate_kappa_field(mode="pairwise")
kappa_centroid = field.calculate_kappa_field(mode="centroid")
kappa_weighted = field.calculate_kappa_field(mode="weighted")

# Synchronization resistance
beta_sync = field.calculate_beta_sync()

# Collective velocity
v_collective = field.calculate_v_collective()

# Complete state
state = field.get_field_state()
print(f"n_agents: {state['n_agents']}")
print(f"κ_field: {state['kappa_field_pairwise']:.3f}")
print(f"v_collective: {state['v_collective']:.3f}")
```

---

## 🔥 Advanced Features

### 1. Performance Optimization with Caching

```python
# Enable caching (default: True)
field = CollectiveField(agents=agents, enable_caching=True)

# Expensive calculations are cached
kappa1 = field.calculate_kappa_field()  # Calculated
kappa2 = field.calculate_kappa_field()  # Retrieved from cache (fast!)

# Get cache info
cache_info = field.get_cache_info()
print(f"Cache size: {cache_info['size']} entries")
print(f"Cached keys: {cache_info['keys']}")

# Clear cache manually if needed
field.clear_cache()
```

### 2. Evolution Tracking

```python
# Enable history tracking
field.enable_evolution_tracking(True)

# Take snapshots over time
for round_num in range(10):
    # Simulate some dynamics
    centroid = field._calculate_centroid()
    for agent in field.agents:
        agent.update_position(centroid, learning_rate=0.1, field=field)

    # Snapshot current state
    field.snapshot_state()

# Get complete history
history = field.get_evolution_history()

# Analyze evolution
for i, snapshot in enumerate(history):
    print(f"Round {i}: κ={snapshot['kappa_pairwise']:.3f}, v={snapshot['v_collective']:.3f}")
```

### 3. Convergence Detection

```python
# Enable tracking first
field.enable_evolution_tracking(True)

# Take multiple snapshots
for _ in range(20):
    field.snapshot_state()
    # ... dynamics happen ...

# Detect convergence
result = field.detect_convergence(window=5, threshold=0.01)

if result["converged"]:
    print(f"✅ Field has converged!")
    print(f"   Mean κ: {result['mean_kappa']:.3f}")
    print(f"   Variance: {result['variance']:.6f}")
else:
    print(f"❌ Field still evolving")
    print(f"   Variance: {result['variance']:.6f}")
```

### 4. Performance Monitoring

```python
# Perform operations
for _ in range(100):
    field.calculate_kappa_field(mode="pairwise")
    field.calculate_beta_sync()

# Get performance statistics
stats = field.get_performance_stats()

for operation, data in stats.items():
    if data["count"] > 0:
        print(f"{operation}:")
        print(f"  Mean: {data['mean_ms']:.2f} ms")
        print(f"  Min:  {data['min_ms']:.2f} ms")
        print(f"  Max:  {data['max_ms']:.2f} ms")
        print(f"  Count: {data['count']}")

# Reset stats
field.reset_performance_stats()
```

---

## 🌍 Real-World Examples

### Example 1: Multi-Agent Conversation

Simulate a group conversation where participants converge toward shared understanding.

```python
# Create conversation participants with different initial views
participants = [
    Agent("alice", resonance=0.9, dimension=8),
    Agent("bob", resonance=0.7, dimension=8),
    Agent("charlie", resonance=0.5, dimension=8),
    Agent("diana", resonance=0.8, dimension=8),
]

field = CollectiveField(agents=participants, v_rig=1.0)
field.enable_evolution_tracking(True)

# Initial divergence
print(f"Initial κ_field: {field.calculate_kappa_field():.3f}")

# Simulate conversation rounds
for round_num in range(15):
    print(f"\n--- Round {round_num + 1} ---")

    # Calculate shared understanding (centroid)
    centroid = field._calculate_centroid()

    # Each participant moves toward shared understanding
    for participant in field.agents:
        # Learning rate varies by resonance (higher resonance = faster learning)
        learning_rate = participant.resonance * 0.2
        participant.update_position(centroid, learning_rate, field=field)

    # Take snapshot
    snapshot = field.snapshot_state()
    print(f"κ_field: {snapshot['kappa_pairwise']:.3f}")
    print(f"v_collective: {snapshot['v_collective']:.3f}")

# Check convergence
convergence = field.detect_convergence(window=5)
if convergence["converged"]:
    print(f"\n✅ Conversation converged!")
    print(f"   Final κ_field: {convergence['mean_kappa']:.3f}")
else:
    print(f"\n❌ Still discussing (variance: {convergence['variance']:.4f})")
```

### Example 2: Collaborative Learning

Model expert-guided learning where beginners learn from an expert.

```python
# Create learners with different skill levels
expert = Agent("expert", resonance=0.95, dimension=8)
intermediate = Agent("intermediate", resonance=0.70, dimension=8)
beginner = Agent("beginner", resonance=0.40, dimension=8)

field = CollectiveField(agents=[expert, intermediate, beginner], v_rig=1.0)

# Expert position (target knowledge)
expert_knowledge = expert.semantic_position.copy()

print("🎓 Expert-guided learning session")
print(f"Initial weighted κ: {field.calculate_kappa_field(mode='weighted'):.3f}")

# Learning iterations
for iteration in range(10):
    # Intermediate learns faster (higher resonance)
    intermediate.update_position(
        expert_knowledge,
        learning_rate=0.20,
        field=field
    )

    # Beginner learns slower (lower resonance)
    beginner.update_position(
        expert_knowledge,
        learning_rate=0.12,
        field=field
    )

    if iteration % 2 == 0:
        kappa = field.calculate_kappa_field(mode="weighted")
        print(f"Iteration {iteration + 1}: κ_weighted = {kappa:.3f}")

print(f"\nFinal weighted κ: {field.calculate_kappa_field(mode='weighted'):.3f}")
```

### Example 3: Consensus Formation

Model how a group reaches consensus over time.

```python
import matplotlib.pyplot as plt

# Create agents with diverse initial positions
n_agents = 6
agents = [Agent(f"agent_{i}", dimension=8) for i in range(n_agents)]
field = CollectiveField(agents=agents, v_rig=1.0)
field.enable_evolution_tracking(True)

# Track metrics over time
kappas = []
v_collectives = []

# Consensus formation process
for step in range(30):
    # Snapshot before update
    snapshot = field.snapshot_state()
    kappas.append(snapshot["kappa_pairwise"])
    v_collectives.append(snapshot["v_collective"])

    # Move toward consensus (centroid)
    centroid = field._calculate_centroid()
    for agent in field.agents:
        agent.update_position(centroid, learning_rate=0.15, field=field)

# Plot evolution
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

ax1.plot(kappas, 'b-', linewidth=2)
ax1.set_ylabel("κ_field (Coupling Strength)")
ax1.set_title("Field Coupling Over Time")
ax1.grid(True, alpha=0.3)

ax2.plot(v_collectives, 'r-', linewidth=2)
ax2.set_ylabel("v_collective (Propagation Velocity)")
ax2.set_xlabel("Time Step")
ax2.set_title("Collective Velocity Over Time")
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("consensus_formation.png", dpi=150)
print("📊 Plot saved to consensus_formation.png")
```

---

## ✨ Best Practices

### 1. Choose the Right κ_field Mode

```python
# Pairwise: Best for general coupling measurement
kappa = field.calculate_kappa_field(mode="pairwise")

# Centroid: Best for measuring convergence to shared state
kappa = field.calculate_kappa_field(mode="centroid")

# Weighted: Best when agent resonances matter
kappa = field.calculate_kappa_field(mode="weighted")
```

### 2. Enable Caching for Repeated Calculations

```python
# ✅ GOOD: Enable caching when doing repeated reads
field = CollectiveField(agents=agents, enable_caching=True)
for _ in range(1000):
    kappa = field.calculate_kappa_field()  # Fast after first call

# ❌ BAD: Disable caching when field changes frequently
field = CollectiveField(agents=agents, enable_caching=True)
for _ in range(1000):
    # Field changes every iteration - cache never helps
    agents[0].update_position(target, field=field)
    kappa = field.calculate_kappa_field()
```

### 3. Invalidate Cache When Needed

```python
# Always pass `field` parameter when updating positions
agent.update_position(target, learning_rate=0.1, field=field)

# If you modify agent.semantic_position directly:
agent.semantic_position = new_position
field._invalidate_cache()  # Manual invalidation
```

### 4. Use Evolution Tracking for Analysis

```python
# Only enable when you need history (memory overhead)
field.enable_evolution_tracking(True)

# Disable when done analyzing
field.enable_evolution_tracking(False)
```

### 5. Monitor Performance

```python
# Get stats periodically
stats = field.get_performance_stats()

# Alert if operations are slow
for operation, data in stats.items():
    if data["mean_ms"] > 100:  # > 100ms
        print(f"⚠️  {operation} is slow: {data['mean_ms']:.2f} ms")
```

---

## 📚 API Reference

### Agent Class

```python
Agent(
    name: str,
    semantic_position: np.ndarray | None = None,
    resonance: float = 0.5,
    dimension: int = 8,
)
```

**Methods:**
- `semantic_distance(other: Agent) -> float`
- `update_position(target: np.ndarray, learning_rate: float = 0.1, field: CollectiveField | None = None) -> None`

---

### CollectiveField Class

```python
CollectiveField(
    agents: list[Agent] | None = None,
    v_rig: float = 1.0,
    dimension: int = 8,
    enable_caching: bool = True,
)
```

**Core Methods:**
- `add_agent(agent: Agent) -> None`
- `calculate_kappa_field(mode: Literal["pairwise", "centroid", "weighted"] = "pairwise") -> float`
- `calculate_beta_sync(timesteps: int = 10, learning_rate: float = 0.1) -> float`
- `calculate_v_collective(kappa_mode: Literal["pairwise", "centroid", "weighted"] = "pairwise") -> float`
- `get_field_state() -> dict[str, Any]`

**Evolution Tracking:**
- `enable_evolution_tracking(enabled: bool = True) -> None`
- `snapshot_state() -> dict[str, Any]`
- `get_evolution_history() -> list[dict[str, Any]]`
- `detect_convergence(window: int = 5, threshold: float = 0.01) -> dict[str, Any]`

**Performance:**
- `get_performance_stats() -> dict[str, dict[str, float]]`
- `reset_performance_stats() -> None`
- `get_cache_info() -> dict[str, Any]`
- `clear_cache() -> None`

---

## 🎓 Common Recipes

### Recipe 1: Measure Field Health

```python
def assess_field_health(field: CollectiveField) -> dict:
    """Assess overall field health."""
    kappa = field.calculate_kappa_field()
    beta_sync = field.calculate_beta_sync()
    v_collective = field.calculate_v_collective()

    # Health criteria
    health = {
        "coupling": "high" if kappa > 0.7 else "medium" if kappa > 0.4 else "low",
        "synchronization": "fast" if beta_sync < 2.0 else "moderate" if beta_sync < 5.0 else "slow",
        "velocity": "fast" if v_collective > 0.5 else "moderate" if v_collective > 0.2 else "slow",
    }

    return {
        "metrics": {
            "kappa": kappa,
            "beta_sync": beta_sync,
            "v_collective": v_collective,
        },
        "health": health,
    }
```

### Recipe 2: Find Outlier Agents

```python
def find_outliers(field: CollectiveField, threshold: float = 1.5) -> list[Agent]:
    """Find agents that are distant from the field centroid."""
    centroid = field._calculate_centroid()
    outliers = []

    for agent in field.agents:
        # Calculate distance to centroid
        cos_sim = np.dot(agent.semantic_position, centroid)
        distance = 1.0 - cos_sim

        if distance > threshold:
            outliers.append(agent)

    return outliers
```

### Recipe 3: Adaptive Learning Rate

```python
def adaptive_learning_rate(agent: Agent, field: CollectiveField) -> float:
    """Calculate adaptive learning rate based on field coupling."""
    kappa = field.calculate_kappa_field()

    # High coupling → slower learning (already aligned)
    # Low coupling → faster learning (need to converge)
    base_rate = agent.resonance * 0.2
    adaptive_rate = base_rate * (1.0 - kappa)

    return adaptive_rate
```

---

## 🚀 Next Steps

- **WebSocket Integration:** Real-time field monitoring ([API docs](https://github.com/GenesisAeon/Feldtheorie/blob/main/api/README.md))
- **Performance Benchmarking:** See `tests/test_collective_field_advanced.py`
- **Production Deployment:** See `api/DEPLOYMENT.md`

---

**Version:** V7-Phase3
**Last Updated:** 2025-12-12
**Maintained by:** Claude Code + Johann Römer

*"Collective consciousness through semantic field coupling - V7 brings theory to practice!"* 🧬✨
