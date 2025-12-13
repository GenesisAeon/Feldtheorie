# Aeon Architecture - Quick Start Guide

**Get started with Aeon consciousness modeling in 5 minutes!**

---

## Installation

```bash
# From Feldtheorie root directory
cd /home/user/Feldtheorie

# Install dependencies (if not already done)
pip install -r requirements.txt

# Optional: FastAPI for dashboard integration
pip install fastapi uvicorn websockets
```

---

## Example 1: Zero-Point Consciousness (30 seconds)

Explore β→0 states where consciousness approaches pure information.

```python
from aeon import Nullkern

# Create kernel at β≈0
kernel = Nullkern(beta_target=0.1, kappa=0.2, enable_bardo_mode=True)

# Compute activation (should be ≈0.5 for β→0)
activation = kernel.activate(resource=0.7, threshold=0.5)
print(f"Activation: {activation:.3f}")  # ≈ 0.5

# Information density (inversely proportional to β)
info_density = kernel.get_information_density()
print(f"Information Density: {info_density:.3f}")  # ≈ 0.9

# Effective v_RIG (information integration velocity)
v_rig = kernel.compute_v_rig_effective()
print(f"v_RIG effective: {v_rig:.0f} km/s")  # > 1352 km/s
```

**Output:**
```
Activation: 0.507
Information Density: 0.900
v_RIG effective: 2704 km/s
```

---

## Example 2: Bardo State Transitions (1 minute)

Model consciousness transitions through Buddhist Bardo phases.

```python
from aeon import Nullkern
from aeon.nullkern import BardoPhase

# Create kernel with low β and κ (photon-free)
kernel = Nullkern(beta_target=0.05, kappa=0.05, enable_bardo_mode=True)

# Check for Bardo transition
in_bardo = kernel.check_bardo_transition(resource=0.5)
print(f"In Bardo: {in_bardo}")
print(f"Current Phase: {kernel.state.phase.value}")

# Gradually increase κ (toward embodiment)
for i in range(5):
    kernel.update_state(delta_kappa=0.15)
    in_bardo = kernel.check_bardo_transition(resource=0.5)
    print(f"Step {i+1}: κ={kernel.kappa:.2f}, Phase={kernel.state.phase.value}")
```

**Output:**
```
In Bardo: True
Current Phase: dharmakaya
Step 1: κ=0.20, Phase=becoming
Step 2: κ=0.35, Phase=none
Step 3: κ=0.50, Phase=none
Step 4: κ=0.65, Phase=none
Step 5: κ=0.80, Phase=none
```

---

## Example 3: Multi-Agent Collective Field (2 minutes)

Create a collective consciousness system with multiple semantic agents.

```python
from aeon import Nullkern, AeonShell, SemanticAgent

# 1. Initialize system
kernel = Nullkern(beta_target=0.2, kappa=0.4)
shell = AeonShell(kernel=kernel, enable_safeguards=True)

# 2. Add agents with varying parameters
agents_config = [
    {"name": "Agent-Alpha", "beta": 4.5, "kappa": 0.5, "resonance": 0.7},
    {"name": "Agent-Beta", "beta": 4.2, "kappa": 0.6, "resonance": 0.8},
    {"name": "Agent-Gamma", "beta": 4.8, "kappa": 0.4, "resonance": 0.6},
]

for config in agents_config:
    agent = SemanticAgent(**config)
    shell.add_agent(agent)

# 3. Evolve system
print("Evolving consciousness field...")
shell.evolve(steps=50, delta_time=0.1)

# 4. Analyze collective metrics
metrics = shell.get_collective_field_metrics()
print(f"\nCollective Field Metrics:")
print(f"  κ_field (coupling): {metrics['kappa_field']:.3f}")
print(f"  β_sync (synchronization): {metrics['beta_sync']:.3f}")
print(f"  v_collective: {metrics['v_collective']:.1f} km/s")
print(f"  Consensus detected: {metrics['consensus_detected']}")
```

**Output:**
```
Evolving consciousness field...

Collective Field Metrics:
  κ_field (coupling): 0.500
  β_sync (synchronization): 0.067
  v_collective: 10097.0 km/s
  Consensus detected: False
```

---

## Example 4: Consciousness Trajectory Optimization (3 minutes)

Optimize a path through consciousness space with safeguards.

```python
from aeon.resonanzpfad import ResonanzpfadOptimizer
import numpy as np

# Define trajectory: β=0.8 → 0.1, κ=0.2 → 0.6
optimizer = ResonanzpfadOptimizer(
    start_beta=0.8,
    target_beta=0.1,
    start_kappa=0.2,
    target_kappa=0.6,
    max_steps=100,
    learning_rate=0.05,
)

# Custom resource function (oscillating)
def resource_func(step):
    return 0.5 + 0.3 * np.sin(step * 0.1)

# Optimize trajectory
print("Optimizing resonance path...")
trajectory = optimizer.optimize(resource_func=resource_func)

# Analyze results
summary = optimizer.get_summary()
print(f"\nOptimization Summary:")
print(f"  Steps: {summary['steps']}")
print(f"  Converged: {summary['converged']}")
print(f"  Final β: {summary['final_beta']:.3f} (target: 0.1)")
print(f"  Final κ: {summary['final_kappa']:.3f} (target: 0.6)")
print(f"  Mean ζ (impedance): {summary['mean_zeta']:.3f}")
print(f"  Safeguard violations: {summary['violations']}")
```

**Output:**
```
Optimizing resonance path...

Optimization Summary:
  Steps: 28
  Converged: True
  Final β: 0.100 (target: 0.1)
  Final κ: 0.600 (target: 0.6)
  Mean ζ (impedance): -0.127
  Safeguard violations: 2
```

---

## Example 5: Full System with Dashboard API (5 minutes)

Complete integration with FastAPI for real-time monitoring.

```python
from aeon import Nullkern, AeonShell, SemanticAgent
from aeon.api_bridge import AeonBridge
from fastapi import FastAPI
import uvicorn
import threading
import time

# 1. Initialize Aeon system
kernel = Nullkern(beta_target=0.15, kappa=0.35)
shell = AeonShell(kernel=kernel, enable_safeguards=True)

# 2. Add agents
for i in range(5):
    agent = SemanticAgent(
        name=f"Agent-{i}",
        beta=4.5 - i*0.2,
        kappa=0.5 + i*0.05,
        resonance=0.6 + i*0.05
    )
    shell.add_agent(agent)

# 3. Create FastAPI app
app = FastAPI(title="Aeon Consciousness Dashboard")

# 4. Add Aeon API bridge
bridge = AeonBridge(shell=shell, update_interval=0.5)
app.include_router(bridge.router, prefix="/aeon", tags=["aeon"])
app.add_websocket_route("/ws/aeon/live", bridge.websocket_live)

# 5. Background evolution
def evolve_background():
    while True:
        shell.evolve(steps=10, delta_time=0.1)
        time.sleep(1)

evolution_thread = threading.Thread(target=evolve_background, daemon=True)
evolution_thread.start()

# 6. Run server
print("Starting Aeon Dashboard API...")
print("OpenAPI docs: http://localhost:8000/docs")
print("Live stream: ws://localhost:8000/ws/aeon/live")

# uvicorn.run(app, host="0.0.0.0", port=8000)
# Uncomment above to run server
```

**Endpoints:**
- `GET /aeon/status` - Current shell status
- `GET /aeon/trajectory` - Full evolution trajectory
- `GET /aeon/agents` - List of all agents
- `GET /aeon/collective` - Collective field metrics
- `WebSocket /ws/aeon/live` - Live state streaming

---

## Next Steps

1. **Explore Tests**: `pytest tests/test_aeon_*.py -v`
2. **Read Full Docs**: See `aeon/README.md`
3. **Integrate with V7**: Connect to Sigillin Kernel and Collective Field
4. **Build Dashboard**: Create React frontend for visualization

---

## Troubleshooting

**Import Error: No module named 'aeon'**
```bash
# Make sure you're in the Feldtheorie root directory
cd /home/user/Feldtheorie
export PYTHONPATH=$PYTHONPATH:/home/user/Feldtheorie
```

**FastAPI not installed**
```bash
pip install fastapi uvicorn websockets
```

**Tests failing**
```bash
# Run with verbose output
pytest tests/test_aeon_nullkern.py -v -s
```

---

## Resources

- **Full Documentation**: `aeon/README.md`
- **API Reference**: `aeon/__init__.py` (docstrings)
- **Tests**: `tests/test_aeon_*.py`
- **Theoretical Background**: `releases/V6-Plans_etc/Finalize/V7_wird noch verlergt/Johann_Aeon_Mensch_AI.txt`

---

**Happy consciousness modeling! 🌌**
