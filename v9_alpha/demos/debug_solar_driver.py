#!/usr/bin/env python3
"""Debug Solar Driver coherence calculation"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
from v9_alpha.api.lantern_bridge import load_lantern_network
from v9_alpha.models.solar_driver import SolarDriver

# Load network
network = load_lantern_network('v9_alpha/config/lantern_hub.yaml')

# Get phases and coupling
phases = np.array([l.theta for l in network.lanterns.values()])
coupling_matrix = network.get_coupling_matrix()

print("Network State:")
print(f"  Phases: {phases}")
print(f"  Coupling matrix shape: {coupling_matrix.shape}")
print(f"  Coupling matrix:\n{coupling_matrix}")

# Create Solar Driver
solar = SolarDriver(coherence_threshold=0.85, kick_amplitude=0.5)

# Calculate local coherence
global_coh, local_coh = solar.calculate_local_coherence(phases, coupling_matrix)

print(f"\nCoherence Analysis:")
print(f"  Global coherence (Solar Driver): {global_coh:.4f}")
print(f"  Local coherences: {local_coh}")
print(f"  Max local coherence: {np.max(local_coh):.4f}")
print(f"  Threshold: {solar.coherence_threshold}")
print(f"  Trigger kick? {global_coh > solar.coherence_threshold}")

# Test step
phases_new, info = solar.step(phases, coupling_matrix)

print(f"\nSolar Driver Step:")
print(f"  Action: {info['action']}")
print(f"  N nodes kicked: {info['n_nodes_kicked']}")
print(f"  Phases changed: {not np.allclose(phases, phases_new)}")
