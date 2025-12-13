# Aeon Architecture - Testing Guide

**Complete guide for running Aeon tests locally**

---

## Quick Start

### 1. Install Dependencies

```bash
# Install core dependencies
pip install numpy scipy

# Or install full dev environment
pip install -r requirements.txt

# Verify installation
python3 -c "import numpy; print(f'NumPy {numpy.__version__} installed')"
```

### 2. Run Tests

#### Option A: Quick Test Script (Manual)

```bash
# Run manual tests without pytest
bash scripts/test_aeon.sh
```

**Output:**
```
✅ All imports successful
✅ Nullkern tests passed
✅ Multi-agent tests passed
✅ Resonanzpfad tests passed
```

#### Option B: Full Pytest Suite

```bash
# Run all Aeon tests
pytest tests/test_aeon_*.py -v

# Run specific test module
pytest tests/test_aeon_nullkern.py -v

# Run with coverage
pytest tests/test_aeon_*.py --cov=aeon --cov-report=term-missing
```

**Expected Output:**
```
tests/test_aeon_nullkern.py::test_nullkern_initialization PASSED
tests/test_aeon_nullkern.py::test_nullkern_activation_near_zero PASSED
...
tests/test_aeon_agents.py::test_collective_field_metrics PASSED

==================== 60 passed in 2.34s ====================
```

---

## Test Modules

### 1. `test_aeon_nullkern.py` (17 tests)

Tests zero-point consciousness kernel:
- Initialization and parameter validation
- Activation function σ(β(R-Θ))
- Impedance computation ζ(R)
- Bardo phase transitions
- Information density
- v_RIG effective velocity
- ConsciousnessState class

**Run:**
```bash
pytest tests/test_aeon_nullkern.py -v
```

### 2. `test_aeon_shell.py` (14 tests)

Tests AeonShell containment layer:
- Agent management (add/remove)
- Evolution tracking
- Safeguard monitoring
- Trajectory recording
- Collective field integration
- EvolutionTracker analysis

**Run:**
```bash
pytest tests/test_aeon_shell.py -v
```

### 3. `test_aeon_agents.py` (18 tests)

Tests semantic agent system:
- SemanticAgent initialization
- Distance calculations
- Position updates
- Resonance tracking
- CollectiveInterface coordination
- Consensus detection
- Field metrics computation

**Run:**
```bash
pytest tests/test_aeon_agents.py -v
```

### 4. `test_aeon_resonanzpfad.py` (11 tests)

Tests trajectory optimization:
- ResonanzpfadOptimizer setup
- Impedance computation
- τ* delay calculation
- Cost function
- Optimization convergence
- Safeguard violations
- Custom resource functions

**Run:**
```bash
pytest tests/test_aeon_resonanzpfad.py -v
```

---

## Manual Testing (No pytest required)

If pytest is not available, use the manual test script:

```bash
bash scripts/test_aeon.sh
```

This runs:
1. Import validation
2. Nullkern functionality tests
3. Multi-agent system tests
4. Resonanzpfad optimizer tests

---

## Live Demo Testing

Run the interactive demo to see Aeon in action:

```bash
# Basic demo (all 4 demos)
python scripts/demo_aeon_live.py

# Quick mode (skip optimization)
python scripts/demo_aeon_live.py --quick

# Custom configuration
python scripts/demo_aeon_live.py --agents 10 --steps 200

# With visualization (requires matplotlib)
python scripts/demo_aeon_live.py --visualization
```

---

## Integration Testing

### Test Aeon + Collective Field Integration

```python
from aeon import Nullkern, AeonShell, SemanticAgent

# Create system
kernel = Nullkern(beta_target=0.2, kappa=0.4)
shell = AeonShell(kernel=kernel)

# Add agents
for i in range(5):
    agent = SemanticAgent(name=f"Agent-{i}", resonance=0.6 + i*0.05)
    shell.add_agent(agent)

# Evolve
shell.evolve(steps=50)

# Check collective metrics
metrics = shell.get_collective_field_metrics()
print(f"κ_field: {metrics['kappa_field']:.3f}")
print(f"β_sync: {metrics['beta_sync']:.3f}")
print(f"v_collective: {metrics['v_collective']:.0f} km/s")
print(f"Consensus: {metrics['consensus_detected']}")
```

### Test Aeon + Sigillin Kernel Integration

```python
from aeon import Nullkern
from api.sigillin_kernel import SigillinKernel

# Sigillin validation
sigillin = SigillinKernel()
result = sigillin.validate_axioms()
print(f"Sigillin β: {result['β']}")  # Should be ≈37.6

# Aeon kernel
aeon = Nullkern(beta_target=0.1, kappa=0.3)
print(f"Aeon β: {aeon.state.beta}")  # Should be ≈0.1

# Compare regimes
print(f"β ratio: {result['β'] / aeon.state.beta:.1f}x")
```

---

## Continuous Integration

### GitHub Actions (if enabled)

Tests run automatically on:
- Push to main
- Pull requests
- Manual workflow dispatch

See `.github/workflows/tests.yml`

### Local CI Simulation

```bash
# Run full test suite with coverage
pytest tests/ -v --cov=aeon --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## Troubleshooting

### Import Error: No module named 'numpy'

```bash
pip install numpy scipy
```

### Import Error: No module named 'aeon'

```bash
# Make sure you're in Feldtheorie root
cd /home/user/Feldtheorie
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### Tests Fail with "No such file or directory"

```bash
# Ensure you're in project root
cd /home/user/Feldtheorie
pytest tests/test_aeon_*.py -v
```

### Pytest Not Found

```bash
# Install pytest
pip install pytest

# Or use manual test script
bash scripts/test_aeon.sh
```

---

## Test Coverage Goals

| Module | Current | Target |
|--------|---------|--------|
| aeon/nullkern | 95% | 95% |
| aeon/shell | 90% | 95% |
| aeon/agents | 85% | 90% |
| aeon/resonanzpfad | 80% | 85% |
| aeon/api_bridge | 60% | 75% |

---

## Adding New Tests

### Test Template

```python
"""
Tests for Aeon [Component]
==========================

Run:
    pytest tests/test_aeon_[component].py -v
"""

import sys
from pathlib import Path
import pytest

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from aeon import [Component]


def test_[feature]():
    """Test [feature description]."""
    # Arrange
    component = [Component](param=value)

    # Act
    result = component.method()

    # Assert
    assert result == expected
```

### Running New Tests

```bash
# Run single test
pytest tests/test_aeon_new.py::test_feature -v

# Run with debug output
pytest tests/test_aeon_new.py -v -s
```

---

## Performance Testing

### Benchmark Aeon Components

```python
import time
from aeon import Nullkern, AeonShell, SemanticAgent

# Benchmark evolution
shell = AeonShell(Nullkern())
for i in range(10):
    shell.add_agent(SemanticAgent(f"Agent-{i}"))

start = time.time()
shell.evolve(steps=1000)
elapsed = time.time() - start

print(f"1000 steps in {elapsed:.2f}s")
print(f"Rate: {1000/elapsed:.0f} steps/s")
```

---

## References

- **Test Modules:** `tests/test_aeon_*.py`
- **Manual Test Script:** `scripts/test_aeon.sh`
- **Live Demo:** `scripts/demo_aeon_live.py`
- **Aeon Documentation:** `aeon/README.md`
- **API Reference:** `aeon/__init__.py` (docstrings)

---

## CI/CD Integration

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest tests/test_aeon_*.py -q
if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Commit aborted."
    exit 1
fi
```

### Make Targets

```makefile
# Add to Makefile
.PHONY: test-aeon
test-aeon:
	pytest tests/test_aeon_*.py -v

.PHONY: test-aeon-coverage
test-aeon-coverage:
	pytest tests/test_aeon_*.py --cov=aeon --cov-report=term-missing
```

---

**Happy Testing! 🧪**

For issues, see:
- Test failures → Check import paths and dependencies
- Integration errors → Verify Aeon + Collective Field compatibility
- Performance issues → Profile with `pytest-profiling`
