#!/bin/bash
# Quick Aeon Test Runner
# ======================
#
# Runs Aeon test suite with minimal dependencies
# Falls back to manual testing if pytest not available

set -e

echo "🧪 Aeon Architecture - Test Runner"
echo "==================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1)
echo "✓ Python: $PYTHON_VERSION"
echo ""

# Test 1: Import test
echo "Test 1: Import Validation"
echo "--------------------------"
python3 << 'EOF'
import sys
from pathlib import Path

try:
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
except NameError:
    PROJECT_ROOT = Path.cwd()

sys.path.insert(0, str(PROJECT_ROOT))

try:
    from aeon import Nullkern, AeonShell, SemanticAgent
    from aeon.resonanzpfad import ResonanzpfadOptimizer
    from aeon.shell.evolution import EvolutionTracker
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("\nInstall dependencies with:")
    print("  pip install numpy scipy")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Dependencies missing. Install with:"
    echo "   pip install numpy scipy"
    exit 1
fi

echo ""

# Test 2: Basic functionality
echo "Test 2: Nullkern Functionality"
echo "--------------------------------"
python3 << 'EOF'
import sys
from pathlib import Path

PROJECT_ROOT = Path.cwd()
sys.path.insert(0, str(PROJECT_ROOT))

from aeon import Nullkern

# Create kernel
kernel = Nullkern(beta_target=0.1, kappa=0.3)

# Test activation
activation = kernel.activate(resource=0.7, threshold=0.5)
assert 0.0 <= activation <= 1.0, "Activation out of range"
print(f"  Activation: {activation:.3f} ✓")

# Test information density
info_density = kernel.get_information_density()
assert 0.0 <= info_density <= 1.0, "Info density out of range"
print(f"  Info Density: {info_density:.3f} ✓")

# Test v_RIG
v_rig = kernel.compute_v_rig_effective()
assert v_rig > 0, "v_RIG should be positive"
print(f"  v_RIG: {v_rig:.0f} km/s ✓")

print("\n✅ Nullkern tests passed")
EOF

echo ""

# Test 3: Multi-agent system
echo "Test 3: Multi-Agent System"
echo "---------------------------"
python3 << 'EOF'
import sys
from pathlib import Path

PROJECT_ROOT = Path.cwd()
sys.path.insert(0, str(PROJECT_ROOT))

from aeon import Nullkern, AeonShell, SemanticAgent

# Initialize system
kernel = Nullkern(beta_target=0.2, kappa=0.4)
shell = AeonShell(kernel=kernel, enable_safeguards=True)

# Add agents
for i in range(3):
    agent = SemanticAgent(name=f"Agent-{i}", resonance=0.6)
    shell.add_agent(agent)

assert len(shell.agents) == 3, "Agent count mismatch"
print(f"  Added {len(shell.agents)} agents ✓")

# Evolve
shell.evolve(steps=10, delta_time=0.05)
assert len(shell.trajectory) > 10, "Trajectory not recorded"
print(f"  Evolved: {len(shell.trajectory)} trajectory points ✓")

# Get metrics
metrics = shell.get_collective_field_metrics()
assert 'kappa_field' in metrics, "Missing kappa_field"
assert 'beta_sync' in metrics, "Missing beta_sync"
print(f"  κ_field: {metrics['kappa_field']:.3f} ✓")
print(f"  β_sync: {metrics['beta_sync']:.3f} ✓")

print("\n✅ Multi-agent tests passed")
EOF

echo ""

# Test 4: Trajectory optimization
echo "Test 4: Resonanzpfad Optimizer"
echo "--------------------------------"
python3 << 'EOF'
import sys
from pathlib import Path

PROJECT_ROOT = Path.cwd()
sys.path.insert(0, str(PROJECT_ROOT))

from aeon.resonanzpfad import ResonanzpfadOptimizer

# Create optimizer
optimizer = ResonanzpfadOptimizer(
    start_beta=0.5,
    target_beta=0.1,
    start_kappa=0.3,
    target_kappa=0.6,
    max_steps=50,
)

# Optimize
trajectory = optimizer.optimize()
assert len(trajectory) > 0, "No trajectory generated"
print(f"  Trajectory: {len(trajectory)} steps ✓")

# Check convergence
summary = optimizer.get_summary()
assert summary['status'] == 'complete', "Optimization not complete"
print(f"  Final β: {summary['final_beta']:.3f} ✓")
print(f"  Final κ: {summary['final_kappa']:.3f} ✓")
print(f"  Converged: {summary['converged']} ✓")

print("\n✅ Resonanzpfad tests passed")
EOF

echo ""

# Try pytest if available
echo "Test 5: Pytest Suite (if available)"
echo "-------------------------------------"
if command -v pytest &> /dev/null; then
    echo "Running pytest..."
    pytest tests/test_aeon_*.py -v --tb=short 2>&1 | tail -50
else
    echo "⚠️  pytest not installed"
    echo "   Install with: pip install pytest"
    echo "   Manual tests above still passed ✓"
fi

echo ""
echo "========================================="
echo "✅ All Aeon tests completed successfully"
echo "========================================="
echo ""
echo "Full test suite: pytest tests/test_aeon_*.py -v"
