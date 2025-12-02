"""
Quick v_RIG test with reduced resolution for faster validation.
"""

import sys
sys.path.insert(0, '/home/user/Feldtheorie')

from simulation.v_rig_renderer import VRigRealityRenderer, plot_coherence_scan, N_OPTIMAL
import numpy as np

print("=" * 70)
print("v_RIG Quick Test (Reduced Resolution)")
print("=" * 70)
print(f"Testing hypothesis: Peak at N ≈ {N_OPTIMAL:.2f}")
print()

# Initialize with lower resolution for speed
renderer = VRigRealityRenderer(slice_resolution=50, seed=42)

# Quick scan with fewer slices
print("Generating 100 slices...")
n_slices = 100

# Coarse scan
print("Scanning N = 10 to 300 (step=10)...")
N_coarse, coherence_coarse = renderer.scan_window_sizes(
    N_range=(10, 300),
    n_slices=n_slices,
    step=10
)

# Find peak
peak_idx = np.argmax(coherence_coarse)
N_peak = N_coarse[peak_idx]
coherence_peak = coherence_coarse[peak_idx]

print("\n" + "=" * 70)
print("QUICK TEST RESULTS")
print("=" * 70)
print(f"Theoretical prediction: N = {N_OPTIMAL:.2f}")
print(f"Empirical peak:         N = {N_peak}")
print(f"Peak coherence:         {coherence_peak:.6f}")
print(f"Deviation:              {abs(N_peak - N_OPTIMAL):.2f} " +
      f"({abs(N_peak - N_OPTIMAL) / N_OPTIMAL * 100:.1f}%)")
print("=" * 70)

# Plot results
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

plot_coherence_scan(N_coarse, coherence_coarse,
                   save_path='results/v_rig_quick_test.png')

print("\nQuick test complete! ✓")
print(f"Results saved to results/v_rig_quick_test.png")

if abs(N_peak - N_OPTIMAL) / N_OPTIMAL < 0.15:  # Within 15%
    print("\n✓ HYPOTHESIS SUPPORTED (quick test)")
else:
    print("\n⚠ Inconclusive - run full simulation for definitive results")
