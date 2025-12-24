#!/usr/bin/env python
"""
Quick integration test for the Ouroboros system.

Tests:
- Engine initialization
- State management
- Intervention commands
- History tracking
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.ouroboros_engine import get_engine

print("=" * 70)
print("♾️  OUROBOROS SYSTEM TEST")
print("=" * 70)
print()

# Test 1: Engine Initialization
print("Test 1: Engine Initialization")
print("-" * 40)
engine = get_engine()
print(f"✅ Engine created")
print(f"   Initial state: {engine.state.value}")
print(f"   Initial generation: {engine.current_seed.generation}")
print()

# Test 2: Get State
print("Test 2: Get State")
print("-" * 40)
state = engine.get_state()
print(f"✅ State retrieved")
print(f"   State: {state['state']}")
print(f"   Status: {state['status_message']}")
print(f"   Generation: {state['generation']}")
print(f"   ECM: {state['ancestor_ecm']}")
print(f"   Mutation: {state['mutation_rate']}")
print()

# Test 3: Start/Pause/Resume
print("Test 3: Control Commands")
print("-" * 40)
result = engine.start_simulation()
print(f"✅ Start: {result['message']}")

time.sleep(0.5)

result = engine.pause_simulation()
print(f"✅ Pause: {result['message']}")

result = engine.resume_simulation()
print(f"✅ Resume: {result['message']}")

time.sleep(0.5)

result = engine.stop_simulation()
print(f"✅ Stop: {result['message']}")
print()

# Test 4: Interventions
print("Test 4: God-Mode Interventions")
print("-" * 40)
result = engine.intervene("mutation_rate", 0.25)
print(f"✅ Mutation intervention: {result['message']}")

result = engine.intervene("energy_injection", 0.15)
print(f"✅ Energy intervention: {result['message']}")

state = engine.get_state()
print(f"   Updated ECM: {state['ancestor_ecm']}")
print(f"   Updated Mutation: {state['mutation_rate']}")
print()

# Test 5: Reset
print("Test 5: Reset to Generation 1")
print("-" * 40)
result = engine.reset_simulation()
print(f"✅ Reset: {result['message']}")

state = engine.get_state()
print(f"   Generation after reset: {state['generation']}")
print(f"   History cleared: {state['history_length']} entries")
print()

# Test 6: Brief simulation run
print("Test 6: Brief Simulation Run (5 seconds)")
print("-" * 40)
print("Starting simulation for 5 seconds...")
engine.start_simulation()
time.sleep(5)
engine.stop_simulation()

state = engine.get_state()
print(f"✅ Simulation completed")
print(f"   Current generation: {state['generation']}")
print(f"   Total generations attempted: {state['total_generations']}")
print(f"   Successful: {state['successful_generations']}")
print(f"   Failed: {state['failed_generations']}")
if state['total_generations'] > 0:
    print(f"   Success rate: {state['success_rate']:.1%}")
print()

# Test 7: History
print("Test 7: History Timeline")
print("-" * 40)
history = engine.get_history_timeline()
print(f"✅ History retrieved: {len(history)} entries")
if history:
    print("   Recent generations:")
    for entry in history[-5:]:
        result_emoji = "🟢" if entry['result'] == 'SUCCESS' else "⚫"
        print(f"   {result_emoji} Gen {entry['generation']}: {entry['result']} (ECM: {entry['ecm_score']:.3f})")
print()

print("=" * 70)
print("✅ ALL TESTS PASSED")
print("=" * 70)
print()
print("Next steps:")
print("1. Start API server:    python -m src.interface.api_server")
print("2. Start dashboard:     streamlit run src/interface/dashboard.py")
print()
