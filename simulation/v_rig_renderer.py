"""
v_RIG Reality Renderer Simulation
==================================

Tests the hypothesis that consciousness integration achieves maximum 3D coherence
when buffer size N ≈ α⁻¹·Φ ≈ 221.74

The simulation:
1. Generates holographic 2D slices with interference patterns
2. Integrates them into 3D volume using ring buffer
3. Measures structural coherence (lower entropy = higher coherence)
4. Scans buffer sizes N = 1 to 500 to find coherence peak

Expected result: Peak coherence at N ≈ 137.036 × 1.618 ≈ 221.74

Author: J.B. Römer
Date: 2025-11-26
License: MIT
"""

import warnings

import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.stats import entropy

warnings.filterwarnings('ignore')

# Physical constants
ALPHA_INV = 137.036  # Fine-structure constant inverse
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio ≈ 1.618
C_LIGHT = 299792.458  # Speed of light (km/s)
V_RIG = C_LIGHT / (ALPHA_INV * PHI)  # ≈ 1351.8 km/s

# Expected peak
N_OPTIMAL = ALPHA_INV * PHI  # ≈ 221.74


class VRigRealityRenderer:
    """
    Simulates consciousness as a reality renderer that integrates 2D holographic
    slices into 3D volumetric perception.
    """

    def __init__(self,
                 slice_resolution: int = 100,
                 slice_spacing_phi: float = PHI,
                 seed: int = 42):
        """
        Initialize the v_RIG renderer.

        Args:
            slice_resolution: Pixel resolution for 2D slices (default: 100×100)
            slice_spacing_phi: Spatial spacing between slices in Φ units
            seed: Random seed for reproducibility
        """
        self.resolution = slice_resolution
        self.slice_spacing = slice_spacing_phi
        self.rng = np.random.RandomState(seed)

        # Storage for ring buffer
        self.buffer = []
        self.max_buffer_size = 500

    def generate_holographic_stream(self, n_slices: int = 100) -> list[np.ndarray]:
        """
        Generate a stream of 2D holographic slices with interference patterns.

        Simulates photon propagation through spacetime as 2D information surfaces
        with phase-shifted interference patterns.

        Args:
            n_slices: Number of slices to generate

        Returns:
            List of 2D numpy arrays (complex-valued interference patterns)
        """
        slices = []

        # Create coordinate grid
        x = np.linspace(-5, 5, self.resolution)
        y = np.linspace(-5, 5, self.resolution)
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X**2 + Y**2)

        for i in range(n_slices):
            # Phase shift per slice (creates temporal evolution)
            phase = 2 * np.pi * i / ALPHA_INV

            # Multiple interference sources (simulates holographic encoding)
            interference = np.zeros_like(X, dtype=complex)

            # Create Φ-spiral interference sources (golden angle = 2π/Φ²)
            golden_angle = 2 * np.pi / (PHI ** 2)
            n_sources = 8

            for j in range(n_sources):
                angle = j * golden_angle
                source_x = 3 * np.cos(angle)
                source_y = 3 * np.sin(angle)

                # Distance from source
                r_source = np.sqrt((X - source_x)**2 + (Y - source_y)**2)

                # Wave contribution (complex amplitude)
                k = 2 * np.pi / PHI  # Wave vector
                wave = np.exp(1j * (k * r_source + phase))

                # Amplitude decay (inverse square law)
                amplitude = 1 / (1 + r_source)

                interference += amplitude * wave

            # Add slice-specific modulation (depth encoding)
            depth_modulation = np.exp(-R**2 / (2 * PHI**2))
            slice_pattern = interference * depth_modulation

            # Extract intensity (|ψ|²) with phase information preserved
            slices.append(slice_pattern)

        return slices

    def integrate_buffer(self, slices: list[np.ndarray], N: int) -> np.ndarray:
        """
        Integrate N consecutive slices into a 3D volume using ring buffer.

        Implements the consciousness integration hypothesis: 2D→3D reconstruction
        with Φ-based parallax spacing.

        Args:
            slices: List of 2D holographic slices
            N: Buffer size (number of slices to integrate)

        Returns:
            3D numpy array (reconstructed volume)
        """
        if N < 1:
            N = 1
        if N > len(slices):
            N = len(slices)

        # Take last N slices (ring buffer behavior)
        buffer_slices = slices[-N:]

        # Stack into 3D volume with Φ-weighted depth spacing
        volume = np.zeros((N, self.resolution, self.resolution), dtype=complex)

        for i, slice_2d in enumerate(buffer_slices):
            # Apply Φ-based parallax shift (simulates stereo vision)
            # Shift increases with depth index, scaled by golden ratio
            shift_x = int((i - N/2) * self.slice_spacing / PHI)
            shift_y = int((i - N/2) * self.slice_spacing / PHI**2)

            # Apply shift via roll (periodic boundary conditions)
            shifted = np.roll(slice_2d, shift=(shift_y, shift_x), axis=(0, 1))

            volume[i] = shifted

        return volume

    def measure_coherence(self, volume: np.ndarray) -> float:
        """
        Measure 3D structural coherence of integrated volume.

        Coherence metric: Lower entropy = higher coherence (sharper 3D structure)

        Method:
        1. Extract intensity |ψ|²
        2. Apply 3D edge detection (gradient magnitude)
        3. Compute entropy of edge distribution
        4. Lower entropy → edges concentrated → high coherence

        Args:
            volume: 3D complex array

        Returns:
            Coherence score (normalized, higher = better)
        """
        # Handle edge case: volume too small for 3D gradient
        if volume.shape[0] < 3:
            # For very small volumes, return low coherence score
            # (cannot properly measure 3D structure with <3 slices)
            return 0.01  # Baseline low score

        # Extract intensity
        intensity = np.abs(volume) ** 2

        # Normalize
        intensity = intensity / (np.max(intensity) + 1e-10)

        # Apply Gaussian smoothing (simulates optical PSF)
        smoothed = gaussian_filter(intensity, sigma=1.0)

        # Compute 3D gradient magnitude (edge strength)
        grad_z, grad_y, grad_x = np.gradient(smoothed)
        grad_magnitude = np.sqrt(grad_x**2 + grad_y**2 + grad_z**2)

        # Normalize gradient to probability distribution
        grad_flat = grad_magnitude.flatten()
        grad_flat = grad_flat / (np.sum(grad_flat) + 1e-10)

        # Compute entropy (lower = more structured)
        H = entropy(grad_flat + 1e-10)

        # Convert to coherence score (invert so higher = better)
        # Normalize to [0, 1] range approximately
        max_entropy = np.log(grad_flat.size)  # Maximum possible entropy
        coherence = 1 - (H / max_entropy)

        return coherence

    def scan_window_sizes(self,
                          N_range: tuple[int, int] = (1, 500),
                          n_slices: int = 500,
                          step: int = 1) -> tuple[np.ndarray, np.ndarray]:
        """
        Scan buffer sizes from N_min to N_max and measure coherence at each.

        This is the key experiment: find the buffer size N that maximizes
        3D structural coherence.

        Hypothesis: Peak at N ≈ α⁻¹·Φ ≈ 221.74

        Args:
            N_range: (N_min, N_max) tuple
            n_slices: Total number of slices to generate
            step: Step size for scanning

        Returns:
            (N_values, coherence_scores) tuple
        """
        print(f"Generating {n_slices} holographic slices...")
        slices = self.generate_holographic_stream(n_slices)

        N_min, N_max = N_range
        N_values = np.arange(N_min, N_max + 1, step)
        coherence_scores = []

        print(f"Scanning buffer sizes N = {N_min} to {N_max} (step={step})...")
        for i, N in enumerate(N_values):
            # Integrate slices with buffer size N
            volume = self.integrate_buffer(slices, N)

            # Measure coherence
            coherence = self.measure_coherence(volume)
            coherence_scores.append(coherence)

            # Progress indicator
            if (i + 1) % 50 == 0 or N in [int(N_OPTIMAL), N_min, N_max]:
                print(f"  N = {N:3d}: coherence = {coherence:.6f}")

        return N_values, np.array(coherence_scores)

    def visualize_reconstruction(self,
                                 slices: list[np.ndarray],
                                 N_values: list[int] = None,
                                 save_path: str = None):
        """
        Visualize 3D reconstruction at different buffer sizes.

        Args:
            slices: Pre-generated holographic slices
            N_values: List of N values to visualize (default: [50, 222, 400])
            save_path: Path to save figure (optional)
        """
        if N_values is None:
            N_values = [50, int(N_OPTIMAL), 400]

        fig, axes = plt.subplots(2, len(N_values), figsize=(5*len(N_values), 10))

        for i, N in enumerate(N_values):
            volume = self.integrate_buffer(slices, N)
            coherence = self.measure_coherence(volume)

            # Top row: Mid-plane slice (XY at Z=N/2)
            mid_z = volume.shape[0] // 2
            intensity = np.abs(volume[mid_z]) ** 2

            axes[0, i].imshow(intensity, cmap='viridis', origin='lower')
            axes[0, i].set_title(f'N = {N}\nMid-Plane (Z={mid_z})')
            axes[0, i].axis('off')

            # Bottom row: Maximum intensity projection (collapse Z axis)
            mip = np.max(np.abs(volume) ** 2, axis=0)

            axes[1, i].imshow(mip, cmap='hot', origin='lower')
            axes[1, i].set_title(f'Max Projection\nCoherence = {coherence:.4f}')
            axes[1, i].axis('off')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved visualization to {save_path}")

        plt.show()


def plot_coherence_scan(N_values: np.ndarray,
                        coherence: np.ndarray,
                        save_path: str = None):
    """
    Plot coherence vs. buffer size N with theoretical prediction.

    Args:
        N_values: Buffer sizes
        coherence: Coherence scores
        save_path: Path to save figure (optional)
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot coherence curve
    ax.plot(N_values, coherence, 'b-', linewidth=2, label='Measured Coherence')

    # Mark theoretical optimum
    ax.axvline(N_OPTIMAL, color='red', linestyle='--', linewidth=2,
               label=f'Predicted: N = α⁻¹·Φ ≈ {N_OPTIMAL:.1f}')

    # Find empirical peak
    peak_idx = np.argmax(coherence)
    N_peak = N_values[peak_idx]
    coherence_peak = coherence[peak_idx]

    ax.plot(N_peak, coherence_peak, 'go', markersize=12,
            label=f'Empirical Peak: N = {N_peak}')

    # Formatting
    ax.set_xlabel('Buffer Size N (number of slices)', fontsize=12)
    ax.set_ylabel('3D Structural Coherence', fontsize=12)
    ax.set_title('v_RIG Reality Renderer: Coherence vs. Buffer Size\n' +
                 'Hypothesis: Maximum coherence at N ≈ α⁻¹·Φ ≈ 221.74',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(alpha=0.3)

    # Add statistics box
    deviation = abs(N_peak - N_OPTIMAL) / N_OPTIMAL * 100
    textstr = f'Peak Deviation: {deviation:.1f}%\n'
    textstr += f'α⁻¹ = {ALPHA_INV:.3f}\n'
    textstr += f'Φ = {PHI:.6f}\n'
    textstr += f'v_RIG = {V_RIG:.1f} km/s'

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved coherence plot to {save_path}")

    plt.show()


def main():
    """
    Run the v_RIG Reality Renderer simulation.
    """
    print("=" * 70)
    print("v_RIG Reality Renderer Simulation")
    print("=" * 70)
    print(f"Testing hypothesis: Maximum 3D coherence at N ≈ α⁻¹·Φ ≈ {N_OPTIMAL:.2f}")
    print("Physical constants:")
    print(f"  α⁻¹ = {ALPHA_INV:.6f} (fine-structure constant inverse)")
    print(f"  Φ   = {PHI:.6f} (golden ratio)")
    print(f"  c   = {C_LIGHT:.3f} km/s")
    print(f"  v_RIG = c/(α⁻¹·Φ) = {V_RIG:.2f} km/s")
    print("=" * 70)
    print()

    # Initialize renderer
    renderer = VRigRealityRenderer(slice_resolution=100, seed=42)

    # Scan buffer sizes (coarse scan first)
    print("Phase 1: Coarse scan (step=5)")
    N_coarse, coherence_coarse = renderer.scan_window_sizes(
        N_range=(1, 500),
        n_slices=500,
        step=5
    )

    # Find coarse peak
    peak_idx = np.argmax(coherence_coarse)
    N_peak_coarse = N_coarse[peak_idx]
    print(f"\nCoarse peak found at N = {N_peak_coarse}")

    # Fine scan around peak
    print(f"\nPhase 2: Fine scan around N = {N_peak_coarse} (step=1)")
    N_fine_min = max(1, N_peak_coarse - 30)
    N_fine_max = min(500, N_peak_coarse + 30)
    N_fine, coherence_fine = renderer.scan_window_sizes(
        N_range=(N_fine_min, N_fine_max),
        n_slices=500,
        step=1
    )

    # Find final peak
    peak_idx_fine = np.argmax(coherence_fine)
    N_peak_fine = N_fine[peak_idx_fine]
    coherence_max = coherence_fine[peak_idx_fine]

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Theoretical prediction: N = {N_OPTIMAL:.2f}")
    print(f"Empirical peak:         N = {N_peak_fine}")
    print(f"Peak coherence:         {coherence_max:.6f}")
    print(f"Deviation:              {abs(N_peak_fine - N_OPTIMAL):.2f} " +
          f"({abs(N_peak_fine - N_OPTIMAL) / N_OPTIMAL * 100:.1f}%)")
    print("=" * 70)

    # Visualization
    print("\nGenerating visualizations...")
    slices = renderer.generate_holographic_stream(n_slices=500)

    # Plot coherence scan
    plot_coherence_scan(N_fine, coherence_fine,
                       save_path='results/v_rig_coherence_scan.png')

    # Visualize reconstructions
    renderer.visualize_reconstruction(
        slices,
        N_values=[50, int(N_OPTIMAL), N_peak_fine, 400],
        save_path='results/v_rig_3d_reconstruction.png'
    )

    print("\nSimulation complete!")
    print("\nInterpretation:")
    if abs(N_peak_fine - N_OPTIMAL) / N_OPTIMAL < 0.1:  # Within 10%
        print("✓ HYPOTHESIS SUPPORTED: Peak coherence occurs near N ≈ α⁻¹·Φ")
        print("  This suggests consciousness integration may follow v_RIG scaling.")
    else:
        print("✗ HYPOTHESIS CHALLENGED: Peak deviates significantly from prediction")
        print("  This requires revision of the v_RIG framework.")


if __name__ == '__main__':
    # Create results directory if needed
    import os
    os.makedirs('results', exist_ok=True)

    main()
