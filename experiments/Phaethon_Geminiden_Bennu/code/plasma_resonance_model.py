"""
Plasma Resonance Model for Phaethon Dust Emission
===================================================

Models the coupling between solar wind plasma waves (Alfvén modes) and
regolith acoustic resonances on asteroid (3200) Phaethon.

Based on:
  - Parker Solar Probe plasma wave measurements (< 0.2 AU)
  - Dusty plasma soliton theory (KdV equation)
  - Phaethon's extreme perihelion environment (0.14 AU, ~750°C)

Key Hypothesis:
  Alfvén waves in solar wind drive acoustic resonances in porous regolith,
  triggering dust emission via "acoustic fluidization" mechanism.

Author: Johann Benjamin Römer
Framework: GenesisAeon v10.2 / UTAC Case Study
Date: 2025-12-29
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.fft import fft, fftfreq
from dataclasses import dataclass
from typing import Tuple, Dict, List

@dataclass
class PhaethonParameters:
    """Physical parameters for Phaethon near perihelion"""

    # Orbital
    perihelion_distance: float = 0.14  # AU
    orbital_velocity: float = 106e3    # m/s at perihelion
    rotation_period: float = 3.6       # hours

    # Surface properties
    max_temperature: float = 750       # K (dayside at perihelion)
    albedo: float = 0.11               # Very dark surface
    radius: float = 2.7e3              # meters (mean radius ~2.7 km)

    # Regolith properties
    porosity: float = 0.60             # Highly porous (assumed)
    grain_size: float = 1e-4           # meters (100 microns typical)
    sound_speed: float = 100           # m/s (acoustic in porous regolith)
    quality_factor: float = 10         # Q-factor (damping)

    # Electrostatic (intense near Sun)
    surface_potential: float = 20      # Volts (photoelectric effect)
    plasma_density: float = 1e8        # m^-3 (solar wind at 0.14 AU)


@dataclass
class SolarWindParameters:
    """Solar wind plasma properties at 0.14 AU (Parker Solar Probe regime)"""

    # Plasma properties
    electron_density: float = 1e8      # m^-3 (100 cm^-3)
    ion_density: float = 1e8           # m^-3 (quasi-neutral)
    electron_temp: float = 1e5         # K
    ion_temp: float = 1e5              # K

    # Magnetic field
    B_field: float = 200e-9            # Tesla (200 nT at 0.14 AU)

    # Wave properties
    alfven_speed: float = 500e3        # m/s (typical at this distance)

    # Frequency ranges (from PSP observations)
    freq_alfven_low: float = 0.1       # Hz
    freq_alfven_high: float = 10       # Hz
    freq_acoustic_low: float = 100     # Hz
    freq_acoustic_high: float = 10e3   # Hz (kHz range)


class PlasmaResonanceModel:
    """
    Models Alfvén wave - regolith acoustic coupling.

    Three-stage process:
      1. Alfvén wave impinges on surface
      2. Converts to acoustic wave in porous medium
      3. Acoustic resonance triggers dust ejection
    """

    def __init__(self, phaethon: PhaethonParameters, solar_wind: SolarWindParameters):
        self.phaethon = phaethon
        self.sw = solar_wind

        # Physical constants
        self.mu_0 = 4 * np.pi * 1e-7   # Permeability
        self.k_B = 1.38e-23             # Boltzmann constant
        self.m_proton = 1.67e-27        # Proton mass
        self.m_electron = 9.11e-31      # Electron mass

    def alfven_velocity(self) -> float:
        """
        Calculate Alfvén speed in solar wind.

        v_A = B / sqrt(μ_0 * ρ)

        Returns:
            Alfvén velocity in m/s
        """
        # Mass density (mostly protons)
        rho = self.sw.ion_density * self.m_proton

        v_A = self.sw.B_field / np.sqrt(self.mu_0 * rho)
        return v_A

    def plasma_beta(self) -> float:
        """
        Calculate plasma beta (thermal/magnetic pressure ratio).

        β = (n k_B T) / (B^2 / 2μ_0)

        Returns:
            Dimensionless plasma beta
        """
        thermal_pressure = self.sw.ion_density * self.k_B * self.sw.ion_temp
        magnetic_pressure = self.sw.B_field**2 / (2 * self.mu_0)

        return thermal_pressure / magnetic_pressure

    def regolith_resonance_frequencies(self, n_modes: int = 10) -> np.ndarray:
        """
        Calculate acoustic resonance frequencies in porous regolith layer.

        For a layer of thickness L, resonant frequencies:
        f_n = n * c_s / (2L)

        where n = 1, 2, 3, ... (harmonics)

        Parameters:
            n_modes : number of resonant modes to calculate

        Returns:
            Array of resonant frequencies in Hz
        """
        # Assume regolith layer depth
        layer_depth = 10  # meters (estimated loose regolith)

        c_s = self.phaethon.sound_speed

        # Harmonic series
        modes = np.arange(1, n_modes + 1)
        frequencies = modes * c_s / (2 * layer_depth)

        return frequencies

    def alfven_frequency_spectrum(self, frequencies: np.ndarray) -> np.ndarray:
        """
        Model Alfvén wave power spectrum at Phaethon's location.

        Based on Parker Solar Probe observations:
          - Power-law spectrum: P(f) ~ f^(-α)
          - α ≈ -1.5 (typical turbulent cascade)

        Parameters:
            frequencies : array of frequencies to evaluate (Hz)

        Returns:
            Power spectral density (arbitrary units)
        """
        # Power law index
        alpha = -1.5

        # Reference power at 1 Hz
        P_0 = 1.0

        # Power law with cutoffs
        power = P_0 * frequencies**alpha

        # Apply low and high frequency cutoffs
        power[frequencies < self.sw.freq_alfven_low] = 0
        power[frequencies > self.sw.freq_alfven_high] = 0

        return power

    def coupling_efficiency(self, f_plasma: float, f_acoustic: float,
                           width: float = 0.5) -> float:
        """
        Calculate coupling efficiency between plasma and acoustic modes.

        Uses Lorentzian resonance profile:
        η(f) = 1 / (1 + ((f_p - f_a) / Γ)^2)

        Parameters:
            f_plasma : plasma wave frequency (Hz)
            f_acoustic : acoustic resonance frequency (Hz)
            width : resonance width (Hz)

        Returns:
            Coupling efficiency in [0, 1]
        """
        delta_f = f_plasma - f_acoustic
        efficiency = 1 / (1 + (delta_f / width)**2)

        return efficiency

    def dust_emission_rate(self, coupling: float, temperature: float) -> float:
        """
        Estimate dust emission rate from acoustic fluidization.

        Combines:
          - Resonant coupling strength
          - Thermal activation (higher T → more emission)
          - Threshold behavior (UTAC-style)

        Parameters:
            coupling : coupling efficiency [0, 1]
            temperature : surface temperature (K)

        Returns:
            Emission rate (particles/s/m^2) - relative scale
        """
        # Thermal factor (Arrhenius-like)
        T_ref = 400  # Reference temperature (K)
        thermal_factor = np.exp((temperature - T_ref) / T_ref)

        # Threshold coupling (beta-parameter style)
        beta = 5.0  # Steepness
        threshold = 0.3

        activation = 1 / (1 + np.exp(-beta * (coupling - threshold)))

        # Combined rate (relative units)
        rate = thermal_factor * activation * coupling

        return rate

    def resonance_map(self, freq_range: Tuple[float, float] = (0.1, 100),
                     n_points: int = 1000) -> Dict:
        """
        Generate full resonance coupling map.

        Scans through frequency space to find resonant coupling peaks.

        Parameters:
            freq_range : (f_min, f_max) in Hz
            n_points : number of frequency points

        Returns:
            Dictionary with frequencies, coupling, and emission data
        """
        # Frequency grid
        frequencies = np.logspace(np.log10(freq_range[0]),
                                 np.log10(freq_range[1]),
                                 n_points)

        # Get regolith resonances
        resonances = self.regolith_resonance_frequencies(n_modes=20)

        # Calculate Alfvén power at each frequency
        alfven_power = self.alfven_frequency_spectrum(frequencies)

        # Calculate total coupling
        total_coupling = np.zeros_like(frequencies)

        for f_res in resonances:
            coupling = np.array([self.coupling_efficiency(f, f_res)
                               for f in frequencies])
            total_coupling += coupling * alfven_power

        # Normalize
        if np.max(total_coupling) > 0:
            total_coupling /= np.max(total_coupling)

        # Dust emission at peak temperature
        T_peak = self.phaethon.max_temperature
        emission = np.array([self.dust_emission_rate(c, T_peak)
                           for c in total_coupling])

        return {
            'frequencies': frequencies,
            'alfven_power': alfven_power,
            'coupling': total_coupling,
            'emission_rate': emission,
            'resonances': resonances
        }

    def plot_resonance_map(self, resonance_data: Dict):
        """Create diagnostic plots for resonance analysis"""

        fig, axes = plt.subplots(3, 1, figsize=(12, 10))

        freq = resonance_data['frequencies']

        # Plot 1: Alfvén Power Spectrum
        ax = axes[0]
        ax.loglog(freq, resonance_data['alfven_power'], 'b-', linewidth=2,
                 label='Alfvén Wave Power')
        ax.set_ylabel('Power (a.u.)')
        ax.set_xlabel('Frequency (Hz)')
        ax.legend()
        ax.grid(True, alpha=0.3, which='both')
        ax.set_title('Solar Wind Alfvén Wave Spectrum (0.14 AU)')

        # Plot 2: Coupling Efficiency
        ax = axes[1]
        ax.semilogx(freq, resonance_data['coupling'], 'r-', linewidth=2,
                   label='Total Coupling')

        # Mark resonances
        for f_res in resonance_data['resonances']:
            if f_res < freq[-1]:
                ax.axvline(f_res, color='gray', linestyle='--', alpha=0.5)

        ax.set_ylabel('Coupling Efficiency')
        ax.set_xlabel('Frequency (Hz)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_title('Plasma-Acoustic Coupling')

        # Plot 3: Dust Emission Rate
        ax = axes[2]
        ax.semilogx(freq, resonance_data['emission_rate'], 'g-', linewidth=2,
                   label='Emission Rate')
        ax.set_ylabel('Emission Rate (relative)')
        ax.set_xlabel('Frequency (Hz)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_title(f'Predicted Dust Emission (T={self.phaethon.max_temperature}K)')

        plt.tight_layout()
        return fig

    def generate_report(self) -> str:
        """Generate analysis report"""

        v_A = self.alfven_velocity()
        beta = self.plasma_beta()
        resonances = self.regolith_resonance_frequencies(n_modes=5)

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║     PHAETHON PLASMA RESONANCE ANALYSIS REPORT               ║
╚══════════════════════════════════════════════════════════════╝

SOLAR WIND CONDITIONS (0.14 AU)
─────────────────────────────────
  Magnetic Field:      {self.sw.B_field*1e9:.1f} nT
  Plasma Density:      {self.sw.ion_density:.2e} m⁻³
  Alfvén Velocity:     {v_A/1e3:.1f} km/s
  Plasma Beta:         {beta:.2f}

PHAETHON SURFACE CONDITIONS
─────────────────────────────────
  Temperature (max):   {self.phaethon.max_temperature} K
  Regolith Porosity:   {self.phaethon.porosity*100:.0f}%
  Sound Speed:         {self.phaethon.sound_speed} m/s
  Surface Potential:   {self.phaethon.surface_potential} V

ACOUSTIC RESONANCES (first 5 modes)
─────────────────────────────────
"""
        for i, f in enumerate(resonances, 1):
            report += f"  Mode {i}: {f:.2f} Hz\n"

        report += f"""
INTERPRETATION
─────────────────────────────────
{'✓' if beta < 1 else '✗'} Magnetic pressure dominant (β < 1): {beta < 1}
{'✓' if v_A > 100e3 else '✗'} Strong Alfvén waves (v_A > 100 km/s): {v_A > 100e3}
{'✓' if resonances[0] < 100 else '✗'} Low-frequency resonances accessible: {resonances[0] < 100}

PREDICTION
─────────────────────────────────
Alfvén-acoustic coupling is {'PLAUSIBLE' if beta < 2 and v_A > 100e3 else 'UNCERTAIN'}
at Phaethon's perihelion conditions.

Recommended for DESTINY+ mission:
  1. Measure plasma wave spectrum (0.1-100 Hz)
  2. Detect dust emission timing vs. wave activity
  3. Correlate with magnetic field variations

═══════════════════════════════════════════════════════════════
"""
        return report


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("Plasma Resonance Model for Phaethon")
    print("=" * 70)

    # Initialize parameters
    phaethon = PhaethonParameters()
    solar_wind = SolarWindParameters()

    # Create model
    model = PlasmaResonanceModel(phaethon, solar_wind)

    # Generate report
    print(model.generate_report())

    # Calculate resonance map
    print("\nGenerating resonance coupling map...")
    resonance_data = model.resonance_map(freq_range=(0.01, 1000), n_points=2000)

    # Find peak coupling
    peak_idx = np.argmax(resonance_data['coupling'])
    peak_freq = resonance_data['frequencies'][peak_idx]
    peak_coupling = resonance_data['coupling'][peak_idx]

    print(f"Peak coupling at {peak_freq:.2f} Hz (efficiency: {peak_coupling:.3f})")

    # Plot results
    print("\nGenerating diagnostic plots...")
    fig = model.plot_resonance_map(resonance_data)

    output_path = '/home/user/Feldtheorie/experiments/Phaethon_Geminiden_Bennu/figures/phaethon_plasma_resonance.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved to: {output_path}")

    print("\n✓ Analysis complete!")
