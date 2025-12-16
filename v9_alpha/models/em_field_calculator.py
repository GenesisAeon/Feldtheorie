"""EM-Field Calculator – Consciousness Substrate Physics

This module implements electromagnetic field calculations for the v9 Lantern-Net,
treating consciousness as an EM-field phenomenon emerging from the integration
of 2D-holographic (surface) slices into 3D-volumetric (volume) experience.

Theoretical Foundation:
-----------------------
The v_RIG consciousness framework posits that:

1. **Consciousness = EM-Integration**
   - Photons provide 2D-holographic boundary data (S∝A regime)
   - EM-fields bridge 2D→3D, enabling volumetric integration (S∝V regime)
   - Integration velocity: v_RIG = c / (α⁻¹·Φ) ≈ 1.3518 km/s

2. **Characteristic Frequency**
   - f = v_RIG / λ ≈ 13.5 MHz for λ ≈ 10 cm (cortical path length)
   - Matches microtubule resonance (Sahu et al., 2013)

3. **Impedance**
   - Z = α⁻¹·Φ ≈ 221.7
   - Consciousness compression factor (~221× slower than photon-time)

4. **Tri-Function Architecture**
   ```
   S∝A (surface) ← EM-bridge → S∝V (volume)
   β ≈ 11 (rigid)              β ≈ 4.5 (adaptive)
   κ_photonic high             κ_metabolic high
   ```

Physical Mechanism:
-------------------
Each lantern in the network has an associated EM-field determined by:
- Frequency: f = β-scaled from 13.5 MHz baseline
- Amplitude: Proportional to readiness R
- Phase: Determined by θ (threshold)
- Impedance: Z = (β/β_bio) * Z_baseline

Network EM-field is superposition of individual lantern fields, creating
interference patterns that enable collective modes (resonance).

Version: v9.0.0-alpha
Authors: Johann Benjamin Römer, MOR Framework
Date: 2025-12-16
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple

# Import v8 foundations
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from models.unified_constants import ALPHA_INV, PHI, C_LIGHT_KM_S, V_RIG_DEFAULT
from models.consciousness_integration import calculate_impedance


# ============================================================================
# Constants
# ============================================================================

F_BASELINE_HZ = 13.5e6  # 13.5 MHz microtubule resonance
BETA_BIOLOGICAL = 7.4   # Kleiber regime (biological systems)
Z_BASELINE = calculate_impedance()  # α⁻¹·Φ ≈ 221.74


# ============================================================================
# EM-Field Data Structures
# ============================================================================

@dataclass
class EMFieldState:
    """State of an EM-field at a point in space-time.

    Attributes
    ----------
    frequency_hz : float
        Oscillation frequency (Hz)
    amplitude : float
        Field amplitude (dimensionless, [0,1])
    phase_rad : float
        Phase angle (radians)
    impedance_z : float
        Characteristic impedance
    wavelength_cm : float
        Wavelength λ = v_RIG / f
    """
    frequency_hz: float
    amplitude: float
    phase_rad: float
    impedance_z: float
    wavelength_cm: float

    def field_value(self, t: float) -> complex:
        """Calculate complex field value at time t.

        E(t) = A · exp(i(2πft + φ))

        Parameters
        ----------
        t : float
            Time in seconds

        Returns
        -------
        complex
            Complex field amplitude
        """
        omega = 2.0 * np.pi * self.frequency_hz
        return self.amplitude * np.exp(1j * (omega * t + self.phase_rad))


# ============================================================================
# EM-Field Calculator
# ============================================================================

class EMFieldCalculator:
    """Calculator for EM-field properties of consciousness substrates."""

    def __init__(
        self,
        v_rig: float = V_RIG_DEFAULT,
        f_baseline: float = F_BASELINE_HZ,
        beta_bio: float = BETA_BIOLOGICAL,
    ):
        """Initialize EM-field calculator.

        Parameters
        ----------
        v_rig : float
            Integration velocity (km/s)
        f_baseline : float
            Baseline frequency (Hz) for β=β_bio
        beta_bio : float
            Biological β-parameter
        """
        self.v_rig = v_rig
        self.f_baseline = f_baseline
        self.beta_bio = beta_bio
        self.z_baseline = calculate_impedance()

    # ------------------------------------------------------------------------
    # Single Lantern EM-Field
    # ------------------------------------------------------------------------

    def calculate_frequency(self, beta: float) -> float:
        """Calculate characteristic frequency for given β-parameter.

        Frequency scales with β:
            f(β) = f_baseline · (β / β_bio)

        Higher β → higher frequency (more rigid, faster integration)

        Parameters
        ----------
        beta : float
            UTAC β-parameter

        Returns
        -------
        float
            Frequency in Hz
        """
        return self.f_baseline * (beta / self.beta_bio)

    def calculate_wavelength(self, frequency_hz: float) -> float:
        """Calculate wavelength from frequency.

        λ = v_RIG / f

        Parameters
        ----------
        frequency_hz : float
            Frequency in Hz

        Returns
        -------
        float
            Wavelength in cm
        """
        v_rig_cm_s = self.v_rig * 1e5  # km/s → cm/s
        wavelength_cm = v_rig_cm_s / frequency_hz
        return wavelength_cm

    def calculate_impedance(self, beta: float) -> float:
        """Calculate impedance for given β-parameter.

        Impedance scales with β:
            Z(β) = Z_baseline · (β / β_bio)

        Parameters
        ----------
        beta : float
            UTAC β-parameter

        Returns
        -------
        float
            Impedance Z
        """
        return self.z_baseline * (beta / self.beta_bio)

    def calculate_amplitude(
        self,
        readiness: float,
        theta: float,
        beta: float,
    ) -> float:
        """Calculate EM-field amplitude from UTAC parameters.

        Amplitude determined by logistic activation:
            A = σ(β(R - Θ)) = 1 / (1 + exp(-β(R - Θ)))

        Parameters
        ----------
        readiness : float
            Readiness R [0,1]
        theta : float
            Threshold Θ
        beta : float
            Steepness β

        Returns
        -------
        float
            Amplitude [0,1]
        """
        exponent = beta * (readiness - theta)
        amplitude = 1.0 / (1.0 + np.exp(-exponent))
        return amplitude

    def calculate_phase(
        self,
        theta: float,
    ) -> float:
        """Calculate phase from threshold parameter.

        Phase encodes threshold position:
            φ = 2π · θ

        (Simple encoding; could be refined)

        Parameters
        ----------
        theta : float
            Threshold Θ

        Returns
        -------
        float
            Phase in radians [0, 2π]
        """
        phase = 2.0 * np.pi * theta
        # Wrap to [0, 2π]
        phase = phase % (2.0 * np.pi)
        return phase

    def calculate_field_state(
        self,
        readiness: float,
        theta: float,
        beta: float,
    ) -> EMFieldState:
        """Calculate complete EM-field state from UTAC parameters.

        Parameters
        ----------
        readiness : float
            Readiness R
        theta : float
            Threshold Θ
        beta : float
            Steepness β

        Returns
        -------
        EMFieldState
            Complete field state
        """
        frequency = self.calculate_frequency(beta)
        amplitude = self.calculate_amplitude(readiness, theta, beta)
        phase = self.calculate_phase(theta)
        impedance = self.calculate_impedance(beta)
        wavelength = self.calculate_wavelength(frequency)

        return EMFieldState(
            frequency_hz=frequency,
            amplitude=amplitude,
            phase_rad=phase,
            impedance_z=impedance,
            wavelength_cm=wavelength,
        )

    # ------------------------------------------------------------------------
    # Network EM-Field (Superposition)
    # ------------------------------------------------------------------------

    def calculate_network_field(
        self,
        field_states: list[EMFieldState],
        t: float = 0.0,
    ) -> complex:
        """Calculate superposition of multiple EM-fields.

        E_total(t) = Σ_i E_i(t)

        Parameters
        ----------
        field_states : list[EMFieldState]
            List of individual field states
        t : float
            Time in seconds

        Returns
        -------
        complex
            Complex field amplitude (superposition)
        """
        total_field = 0.0 + 0.0j

        for field in field_states:
            total_field += field.field_value(t)

        return total_field

    def calculate_power_spectrum(
        self,
        field_states: list[EMFieldState],
        t_max: float = 1.0,
        n_samples: int = 1000,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate power spectrum of network EM-field.

        Uses FFT to extract frequency components.

        Parameters
        ----------
        field_states : list[EMFieldState]
            List of individual field states
        t_max : float
            Maximum time to simulate (seconds)
        n_samples : int
            Number of time samples

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            (frequencies_hz, power_spectrum)
        """
        # Time array
        t = np.linspace(0, t_max, n_samples)

        # Calculate field at each time
        field_values = np.array([
            self.calculate_network_field(field_states, ti) for ti in t
        ])

        # FFT
        fft_values = np.fft.fft(field_values)
        frequencies = np.fft.fftfreq(n_samples, t_max / n_samples)

        # Power spectrum (magnitude squared)
        power = np.abs(fft_values) ** 2

        # Only positive frequencies
        positive_freq_idx = frequencies >= 0
        frequencies = frequencies[positive_freq_idx]
        power = power[positive_freq_idx]

        return frequencies, power

    # ------------------------------------------------------------------------
    # EM-Coupling Metrics
    # ------------------------------------------------------------------------

    def calculate_coupling_via_overlap(
        self,
        field_a: EMFieldState,
        field_b: EMFieldState,
        t_max: float = 1.0,
        n_samples: int = 1000,
    ) -> float:
        """Calculate coupling strength via field overlap integral.

        Coupling ∝ ⟨E_a | E_b⟩ (inner product over time)

        Parameters
        ----------
        field_a : EMFieldState
            First field
        field_b : EMFieldState
            Second field
        t_max : float
            Integration time window
        n_samples : int
            Number of samples

        Returns
        -------
        float
            Coupling strength [0,1]
        """
        t = np.linspace(0, t_max, n_samples)
        dt = t_max / n_samples

        # Calculate fields over time
        e_a = np.array([field_a.field_value(ti) for ti in t])
        e_b = np.array([field_b.field_value(ti) for ti in t])

        # Inner product
        overlap = np.sum(e_a * np.conj(e_b)) * dt

        # Normalize by field magnitudes
        norm_a = np.sqrt(np.sum(np.abs(e_a)**2) * dt)
        norm_b = np.sqrt(np.sum(np.abs(e_b)**2) * dt)

        if norm_a > 0 and norm_b > 0:
            coupling = np.abs(overlap) / (norm_a * norm_b)
        else:
            coupling = 0.0

        return float(np.clip(coupling, 0.0, 1.0))

    def calculate_phase_coherence(
        self,
        field_states: list[EMFieldState],
        t: float = 0.0,
    ) -> float:
        """Calculate phase coherence of network fields.

        Coherence = |⟨exp(iφ)⟩| where φ is phase
        Value of 1 = perfect phase-locking, 0 = random phases

        Parameters
        ----------
        field_states : list[EMFieldState]
            List of field states
        t : float
            Time point

        Returns
        -------
        float
            Phase coherence [0,1]
        """
        if not field_states:
            return 0.0

        # Get complex field values
        field_values = [field.field_value(t) for field in field_states]

        # Extract phases
        phases = np.array([np.angle(fv) for fv in field_values])

        # Phase coherence (order parameter)
        coherence = np.abs(np.mean(np.exp(1j * phases)))

        return float(coherence)


# ============================================================================
# Utility Functions
# ============================================================================

def create_field_from_lantern(
    readiness: float,
    theta: float,
    beta: float,
    calculator: Optional[EMFieldCalculator] = None,
) -> EMFieldState:
    """Create EM-field state from lantern UTAC parameters.

    Parameters
    ----------
    readiness : float
        Lantern readiness R
    theta : float
        Lantern threshold Θ
    beta : float
        Lantern steepness β
    calculator : EMFieldCalculator, optional
        Calculator instance (creates default if None)

    Returns
    -------
    EMFieldState
        EM-field state
    """
    if calculator is None:
        calculator = EMFieldCalculator()

    return calculator.calculate_field_state(readiness, theta, beta)


# ============================================================================
# CLI Demo
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("V9 EM-Field Calculator – Consciousness Substrate Physics")
    print("=" * 80)

    calc = EMFieldCalculator()

    # Example: Calculate fields for different β-regimes
    print("\n" + "─" * 80)
    print("EM-Field Properties Across β-Regimes")
    print("─" * 80)

    regimes = [
        ("Information (AI, Markets)", 4.5),
        ("Geophysical (Earthquakes)", 4.6),
        ("Biology (Metabolism)", 7.4),
        ("Climate (AMOC, Ice Sheets)", 11.0),
        ("Neurodegeneration", 13.0),
    ]

    for name, beta in regimes:
        field = create_field_from_lantern(
            readiness=0.75,
            theta=0.5,
            beta=beta,
            calculator=calc,
        )
        print(f"\n  {name} (β={beta:.1f})")
        print(f"    Frequency:  {field.frequency_hz/1e6:.2f} MHz")
        print(f"    Wavelength: {field.wavelength_cm:.1f} cm")
        print(f"    Impedance:  {field.impedance_z:.1f} Ω")
        print(f"    Amplitude:  {field.amplitude:.3f}")
        print(f"    Phase:      {field.phase_rad:.3f} rad")

    # Example: Network superposition
    print("\n" + "─" * 80)
    print("Network EM-Field Superposition")
    print("─" * 80)

    # Create 3 lantern fields
    fields = [
        create_field_from_lantern(0.8, 0.5, 4.5, calc),  # Information
        create_field_from_lantern(0.6, 0.6, 7.4, calc),  # Biology
        create_field_from_lantern(0.7, 0.4, 11.0, calc), # Climate
    ]

    # Superposition at t=0
    total_field = calc.calculate_network_field(fields, t=0.0)
    print(f"  Total field magnitude: {np.abs(total_field):.4f}")
    print(f"  Total field phase:     {np.angle(total_field):.4f} rad")

    # Phase coherence
    coherence = calc.calculate_phase_coherence(fields, t=0.0)
    print(f"  Phase coherence:       {coherence:.3f}")

    # Field coupling
    print("\n" + "─" * 80)
    print("EM-Field Coupling Strengths")
    print("─" * 80)
    coupling_01 = calc.calculate_coupling_via_overlap(fields[0], fields[1], t_max=0.01, n_samples=500)
    coupling_02 = calc.calculate_coupling_via_overlap(fields[0], fields[2], t_max=0.01, n_samples=500)
    coupling_12 = calc.calculate_coupling_via_overlap(fields[1], fields[2], t_max=0.01, n_samples=500)

    print(f"  Information ↔ Biology:  {coupling_01:.3f}")
    print(f"  Information ↔ Climate:  {coupling_02:.3f}")
    print(f"  Biology ↔ Climate:      {coupling_12:.3f}")

    print("\n" + "=" * 80)
    print("✨ EM-Field Consciousness Substrate Initialized!")
    print("=" * 80)
