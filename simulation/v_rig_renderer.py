"""v_RIG Reality-Renderer Simulation.

Tests the hypothesis that coherent 3D reality emerges when holographic 2D slices
are integrated over a buffer window N ≈ α⁻¹·Φ ≈ 221.74.

Reference: releases/V6-Plans_etc/GrundPrinzip Simulation.txt:596-727
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Tuple


# Constants
ALPHA_INV = 137.036  # Fine structure constant inverse
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio ≈ 1.618
TARGET_N = ALPHA_INV * PHI  # ≈ 221.74


@dataclass
class VRigConfig:
    """Configuration for v_RIG reality renderer."""
    slice_size: int = 100  # 2D slice resolution (pixels)
    alpha_inv: float = ALPHA_INV
    phi: float = PHI
    parallax_shift: float = 0.1  # Φ-based parallax between slices


class VRigRealityRenderer:
    """Reality-Renderer implementing holographic slice integration.
    
    Core Hypothesis: Maximum 3D coherence at buffer size N ≈ α⁻¹·Φ ≈ 222.
    """

    def __init__(self, config: VRigConfig | None = None):
        self.config = config or VRigConfig()
        self.target_n = self.config.alpha_inv * self.config.phi

    def generate_holographic_slice(self, slice_index: int) -> np.ndarray:
        """Generate 2D holographic slice with interference patterns.
        
        Args:
            slice_index: Temporal index of slice
            
        Returns:
            2D array (slice_size × slice_size) with interference pattern
        """
        size = self.config.slice_size
        x = np.linspace(-1, 1, size)
        y = np.linspace(-1, 1, size)
        X, Y = np.meshgrid(x, y)
        
        # Interference pattern modulated by slice index
        freq = 2 * np.pi * (1 + slice_index * 0.01)
        pattern = np.sin(freq * X) * np.cos(freq * Y)
        
        # Add golden ratio phase shift
        pattern += 0.3 * np.sin(self.config.phi * freq * np.sqrt(X**2 + Y**2))
        
        return pattern

    def integrate_buffer(self, N: int) -> np.ndarray:
        """Integrate N holographic slices into 3D structure.
        
        Args:
            N: Buffer window size (number of slices to integrate)
            
        Returns:
            3D array (N × slice_size × slice_size) with integrated structure
        """
        size = self.config.slice_size
        buffer_3d = np.zeros((N, size, size))
        
        for i in range(N):
            # Generate slice
            slice_2d = self.generate_holographic_slice(i)
            
            # Add Φ-parallax shift (simulate binocular disparity)
            shift = int(self.config.parallax_shift * self.config.phi * i)
            slice_2d = np.roll(slice_2d, shift, axis=1)
            
            buffer_3d[i] = slice_2d
        
        return buffer_3d

    def measure_coherence(self, buffer_3d: np.ndarray) -> float:
        """Measure 3D structure coherence (low entropy = high coherence).
        
        Args:
            buffer_3d: Integrated 3D buffer
            
        Returns:
            Coherence score (0-1, higher = more coherent)
        """
        # Compute gradient magnitude as proxy for structure
        grad_x = np.gradient(buffer_3d, axis=0)
        grad_y = np.gradient(buffer_3d, axis=1)
        grad_z = np.gradient(buffer_3d, axis=2)
        
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2 + grad_z**2)
        
        # Coherence = inverse of gradient variance (low variance = coherent)
        variance = np.var(gradient_magnitude)
        coherence = 1.0 / (1.0 + variance)  # Normalize to 0-1
        
        return coherence

    def scan_window_sizes(
        self,
        N_min: int = 1,
        N_max: int = 500,
        N_step: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Scan buffer window sizes and measure coherence.
        
        Core Test: Does coherence peak at N ≈ α⁻¹·Φ ≈ 222?
        
        Args:
            N_min: Minimum buffer size
            N_max: Maximum buffer size
            N_step: Step size for scan
            
        Returns:
            Tuple of (N_values, coherence_values)
        """
        N_values = np.arange(N_min, N_max + 1, N_step)
        coherence_values = []
        
        for N in N_values:
            buffer_3d = self.integrate_buffer(N)
            coherence = self.measure_coherence(buffer_3d)
            coherence_values.append(coherence)
            
            # Log progress
            if N % 50 == 0:
                print(f"N={N:3d}: coherence={coherence:.4f}")
        
        return N_values, np.array(coherence_values)

    def find_coherence_peak(self) -> Tuple[int, float]:
        """Find buffer size N that maximizes coherence.
        
        Returns:
            Tuple of (optimal_N, peak_coherence)
        """
        N_values, coherence_values = self.scan_window_sizes(
            N_min=int(self.target_n * 0.5),
            N_max=int(self.target_n * 1.5),
            N_step=5
        )
        
        peak_idx = np.argmax(coherence_values)
        optimal_N = N_values[peak_idx]
        peak_coherence = coherence_values[peak_idx]
        
        print(f"\n✅ Peak coherence at N={optimal_N} (target: {self.target_n:.1f})")
        print(f"   Deviation: {abs(optimal_N - self.target_n):.1f} ({abs(optimal_N - self.target_n) / self.target_n * 100:.1f}%)")
        
        return optimal_N, peak_coherence


def run_vrig_validation() -> None:
    """Run v_RIG buffer validation experiment."""
    print("🔬 v_RIG Reality-Renderer Validation")
    print(f"Target buffer size: N = α⁻¹·Φ ≈ {TARGET_N:.2f}")
    print("Hypothesis: Coherence peaks at N ≈ 222\n")
    
    renderer = VRigRealityRenderer()
    optimal_N, peak_coherence = renderer.find_coherence_peak()
    
    # Validation
    deviation_pct = abs(optimal_N - TARGET_N) / TARGET_N * 100
    
    if deviation_pct < 5:
        print(f"\n✅ HYPOTHESIS SUPPORTED: {deviation_pct:.1f}% deviation")
    elif deviation_pct < 10:
        print(f"\n⚠️  HYPOTHESIS WEAK: {deviation_pct:.1f}% deviation")
    else:
        print(f"\n❌ HYPOTHESIS REJECTED: {deviation_pct:.1f}% deviation")


if __name__ == "__main__":
    run_vrig_validation()
