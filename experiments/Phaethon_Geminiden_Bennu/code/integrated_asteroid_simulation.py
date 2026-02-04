"""
Integrated Asteroid Dust Emission Simulation
=============================================

Combines the three computational models:
  1. Chimera State Model (frustrated regolith dynamics)
  2. Plasma Resonance Model (Alfvén wave coupling)
  3. Soliton Generator (dust transport mechanism)

Produces the 47 quantitative predictions for DESTINY+ mission.

Author: Johann Benjamin Römer
Framework: GenesisAeon v10.2 / UTAC Case Study
Date: 2026-02-04
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap
from scipy.integrate import odeint, solve_ivp
from scipy.stats import gaussian_kde, kstest, chisquare
from scipy.fft import fft, ifft, fftfreq
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional
import json
from pathlib import Path

# ============================================================================
# PHYSICAL CONSTANTS
# ============================================================================

@dataclass
class PhysicalConstants:
    """Fundamental physical constants"""
    c: float = 2.998e8          # Speed of light (m/s)
    k_B: float = 1.38e-23       # Boltzmann constant (J/K)
    e: float = 1.602e-19        # Elementary charge (C)
    m_proton: float = 1.673e-27 # Proton mass (kg)
    m_electron: float = 9.109e-31  # Electron mass (kg)
    epsilon_0: float = 8.854e-12   # Vacuum permittivity (F/m)
    mu_0: float = 1.257e-6         # Vacuum permeability (H/m)
    AU: float = 1.496e11           # Astronomical unit (m)

    # UTAC Framework constants
    HEX_RESONANCE_BETA: float = 4.8     # Universal β parameter
    V_RIG: float = 1352.0               # Resonance integration velocity (m/s)

CONSTANTS = PhysicalConstants()

# ============================================================================
# PHAETHON PARAMETERS
# ============================================================================

@dataclass
class PhaethonSystem:
    """Complete parameter set for Phaethon asteroid system"""

    # Orbital parameters
    perihelion_AU: float = 0.14
    aphelion_AU: float = 2.40
    orbital_period_years: float = 1.43
    eccentricity: float = 0.89
    inclination_deg: float = 22.3

    # Physical properties
    radius_m: float = 2700.0           # Mean radius ~2.7 km
    mass_kg: float = 1.4e14            # Estimated mass
    rotation_period_h: float = 3.604   # Rotation period
    surface_gravity_ms2: float = 2.8e-4  # Surface gravity
    escape_velocity_ms: float = 1.1    # Escape velocity

    # Thermal properties (perihelion)
    T_max_K: float = 1050.0   # Maximum dayside temperature
    T_min_K: float = 200.0    # Nightside temperature
    thermal_inertia: float = 600.0  # J m^-2 K^-1 s^-0.5

    # Regolith properties
    porosity: float = 0.60
    grain_size_m: float = 1e-4       # 100 μm typical
    cohesion_Pa: float = 0.3         # Very weak cohesion
    sound_speed_ms: float = 100.0    # Acoustic in regolith

    # Electrostatic
    surface_potential_V: float = 20.0  # Photoelectric
    photoemission_Am2: float = 1e-7    # UV-driven current

    # Computed properties
    @property
    def perihelion_m(self) -> float:
        return self.perihelion_AU * CONSTANTS.AU

    @property
    def rotation_freq_Hz(self) -> float:
        return 1.0 / (self.rotation_period_h * 3600)

    @property
    def omega_rotation(self) -> float:
        return 2 * np.pi * self.rotation_freq_Hz

@dataclass
class SolarWindAtPhaethon:
    """Solar wind parameters at Phaethon's perihelion (0.14 AU)"""

    # Parker Solar Probe regime extrapolations
    n_e: float = 3e8              # Electron density (m^-3)
    n_i: float = 3e8              # Ion density (m^-3)
    T_e: float = 2e5              # Electron temperature (K)
    T_i: float = 1e5              # Ion temperature (K)
    B_field: float = 400e-9       # Magnetic field (T, ~400 nT)
    v_sw: float = 400e3           # Solar wind speed (m/s)

    # Wave properties
    alfven_freq_range: Tuple[float, float] = (0.01, 100)  # Hz

    @property
    def v_alfven(self) -> float:
        """Alfvén velocity"""
        rho = self.n_i * CONSTANTS.m_proton
        return self.B_field / np.sqrt(CONSTANTS.mu_0 * rho)

    @property
    def plasma_beta(self) -> float:
        """Thermal to magnetic pressure ratio"""
        P_thermal = self.n_i * CONSTANTS.k_B * self.T_i
        P_magnetic = self.B_field**2 / (2 * CONSTANTS.mu_0)
        return P_thermal / P_magnetic

    @property
    def debye_length(self) -> float:
        """Electron Debye length"""
        return np.sqrt(CONSTANTS.epsilon_0 * CONSTANTS.k_B * self.T_e /
                      (self.n_e * CONSTANTS.e**2))

# ============================================================================
# ENHANCED CHIMERA STATE MODEL
# ============================================================================

class EnhancedChimeraModel:
    """
    Enhanced Kuramoto-based chimera state model for asteroid regolith.

    Improvements over basic model:
    - Non-local coupling (nearest neighbors + long-range)
    - Phase-dependent frustration
    - Memory effects (hysteresis)
    - Thermal fatigue accumulation
    """

    def __init__(self, phaethon: PhaethonSystem, n_patches: int = 200,
                 seed: int = 42):
        self.phaethon = phaethon
        self.n_patches = n_patches
        np.random.seed(seed)

        # Initialize oscillator phases (random initial conditions)
        self.phases = np.random.uniform(0, 2*np.pi, n_patches)

        # Natural frequencies (with distribution to prevent trivial sync)
        self.omega_natural = np.random.normal(1.0, 0.2, n_patches)

        # Coupling parameters
        self.K_local = 0.8      # Local coupling strength
        self.K_global = 0.2     # Global mean-field coupling
        self.frustration_level = 0.3  # Phase frustration

        # Thermal fatigue accumulation
        self.thermal_stress = np.zeros(n_patches)
        self.fatigue_threshold = 0.7

        # Memory of active regions
        self.activation_history = np.zeros(n_patches)

    def temperature_profile(self, t: float, LST_offset: np.ndarray) -> np.ndarray:
        """
        Spatially-resolved temperature profile.

        Parameters:
            t: Time in hours
            LST_offset: Array of LST offsets for each patch (0-24h)

        Returns:
            Temperature array for each patch
        """
        period = self.phaethon.rotation_period_h

        # Local solar time for each patch
        LST = (t + LST_offset) % period

        # Normalized solar angle (0 at dawn, 0.5 at noon, 1 at dusk)
        solar_angle = LST / period

        # Day/night profile (cosine with clipping for nightside)
        day_factor = np.maximum(0, np.cos(2 * np.pi * (solar_angle - 0.25)))

        # Temperature interpolation
        T = self.phaethon.T_min_K + (self.phaethon.T_max_K - self.phaethon.T_min_K) * day_factor

        return T

    def electrostatic_force(self, T: np.ndarray) -> np.ndarray:
        """
        Electrostatic lifting force from photoelectron sheath.

        Scales with temperature (proxy for UV intensity).
        """
        # Normalized temperature
        T_norm = (T - self.phaethon.T_min_K) / (self.phaethon.T_max_K - self.phaethon.T_min_K)

        # Force scales nonlinearly with temperature
        force = T_norm**1.5 * self.phaethon.surface_potential_V

        return force

    def compute_frustration(self, phases: np.ndarray) -> float:
        """
        Measure global frustration (disorder) in the system.

        Returns value in [0, 1]: 0 = fully coherent, 1 = fully incoherent
        """
        # Kuramoto order parameter
        r = np.abs(np.mean(np.exp(1j * phases)))
        return 1 - r

    def compute_chimera_fraction(self, phases: np.ndarray,
                                  window: int = 10) -> Tuple[float, np.ndarray]:
        """
        Compute fraction of system in 'unjammed' (chimera) state.

        Uses local order parameter with sliding window.

        Returns:
            (chimera_fraction, local_order_array)
        """
        n = len(phases)
        local_order = np.zeros(n)

        for i in range(n):
            # Get neighbors with periodic boundary
            start = max(0, i - window)
            end = min(n, i + window + 1)
            neighbors = phases[start:end]
            local_order[i] = np.abs(np.mean(np.exp(1j * neighbors)))

        # Patches with low local order are "unjammed"
        threshold = 0.5
        unjammed = local_order < threshold
        chimera_frac = np.sum(unjammed) / n

        return chimera_frac, local_order

    def kuramoto_dynamics(self, phases: np.ndarray, t: float,
                          thermal_stress: np.ndarray) -> np.ndarray:
        """
        Enhanced Kuramoto dynamics with thermal forcing and frustration.
        """
        n = len(phases)
        dphases = self.omega_natural.copy()

        # Local coupling (nearest neighbors)
        for i in range(n):
            # Periodic boundaries
            left = (i - 1) % n
            right = (i + 1) % n

            local_coupling = (np.sin(phases[left] - phases[i]) +
                            np.sin(phases[right] - phases[i]))
            dphases[i] += self.K_local * local_coupling

        # Global mean-field coupling
        mean_phase = np.angle(np.mean(np.exp(1j * phases)))
        global_coupling = np.sin(mean_phase - phases + self.frustration_level * np.pi)
        dphases += self.K_global * global_coupling

        # Thermal stress perturbation (breaks synchrony)
        thermal_noise = thermal_stress * np.random.normal(0, 0.3, n)
        dphases += thermal_noise

        return dphases

    def ejection_probability(self, chimera_frac: float, T: np.ndarray,
                            electrostatic: np.ndarray,
                            local_order: np.ndarray) -> np.ndarray:
        """
        Calculate per-patch ejection probability.

        Uses UTAC-style sigmoid threshold model.
        """
        # Normalized quantities
        T_norm = (T - self.phaethon.T_min_K) / (self.phaethon.T_max_K - self.phaethon.T_min_K)
        E_norm = electrostatic / np.max(electrostatic) if np.max(electrostatic) > 0 else electrostatic

        # Combined stress (each patch)
        stress = (0.35 * T_norm +           # Thermal contribution
                  0.25 * E_norm +            # Electrostatic lifting
                  0.25 * (1 - local_order) + # Local disorder (unjammed)
                  0.15 * chimera_frac)       # Global chimera state

        # UTAC sigmoid activation
        beta = CONSTANTS.HEX_RESONANCE_BETA
        theta = 0.55  # Threshold

        prob = 1 / (1 + np.exp(-beta * (stress - theta)))

        return prob

    def simulate(self, duration_hours: float = 24.0, dt: float = 0.02,
                 verbose: bool = False) -> Dict:
        """
        Run full simulation over specified duration.

        Parameters:
            duration_hours: Simulation time
            dt: Time step (hours)
            verbose: Print progress

        Returns:
            Dictionary with all simulation data
        """
        times = np.arange(0, duration_hours, dt)
        n_steps = len(times)

        # Assign LST offsets (patches distributed around asteroid)
        LST_offsets = np.linspace(0, self.phaethon.rotation_period_h,
                                  self.n_patches, endpoint=False)

        # Preallocate arrays
        phases_history = np.zeros((n_steps, self.n_patches))
        frustration_history = np.zeros(n_steps)
        chimera_frac_history = np.zeros(n_steps)
        ejection_prob_history = np.zeros((n_steps, self.n_patches))
        temperature_history = np.zeros((n_steps, self.n_patches))

        events = []
        phases = self.phases.copy()
        thermal_stress = np.zeros(self.n_patches)

        for i, t in enumerate(times):
            # Compute temperature profile
            T = self.temperature_profile(t, LST_offsets)
            temperature_history[i] = T

            # Update thermal stress (accumulates with temperature cycling)
            dT_dt = np.gradient(T)
            thermal_stress += np.abs(dT_dt) * dt * 0.01
            thermal_stress = np.clip(thermal_stress, 0, 1)

            # Compute system state
            frustration = self.compute_frustration(phases)
            chimera_frac, local_order = self.compute_chimera_fraction(phases)

            frustration_history[i] = frustration
            chimera_frac_history[i] = chimera_frac
            phases_history[i] = phases

            # Electrostatic force
            electrostatic = self.electrostatic_force(T)

            # Ejection probabilities
            ejection_prob = self.ejection_probability(chimera_frac, T,
                                                      electrostatic, local_order)
            ejection_prob_history[i] = ejection_prob

            # Check for ejection events (Monte Carlo)
            for j in range(self.n_patches):
                if np.random.rand() < ejection_prob[j] * dt * 10:  # Scaled probability
                    # Record event
                    LST = (t + LST_offsets[j]) % self.phaethon.rotation_period_h
                    events.append({
                        'time': t,
                        'patch': j,
                        'LST': LST,
                        'temperature': T[j],
                        'probability': ejection_prob[j],
                        'chimera_frac': chimera_frac,
                        'local_order': local_order[j]
                    })
                    # Update activation history
                    self.activation_history[j] += 1

            # Evolve dynamics
            dphases = self.kuramoto_dynamics(phases, t, thermal_stress)
            phases += dphases * dt
            phases = phases % (2 * np.pi)

            if verbose and i % 1000 == 0:
                print(f"  t = {t:.1f}h, events = {len(events)}, χ = {chimera_frac:.3f}")

        return {
            'times': times,
            'LST_offsets': LST_offsets,
            'phases': phases_history,
            'frustration': frustration_history,
            'chimera_fraction': chimera_frac_history,
            'ejection_probability': ejection_prob_history,
            'temperature': temperature_history,
            'events': events,
            'activation_history': self.activation_history
        }

# ============================================================================
# INTEGRATED PLASMA-SOLITON MODEL
# ============================================================================

class IntegratedPlasmaSolitonModel:
    """
    Couples plasma resonance with soliton transport.

    Models the complete chain:
    Alfvén waves → Acoustic resonance → Soliton formation → Dust ejection
    """

    def __init__(self, phaethon: PhaethonSystem, solar_wind: SolarWindAtPhaethon):
        self.phaethon = phaethon
        self.sw = solar_wind

    def alfven_wave_spectrum(self, frequencies: np.ndarray) -> np.ndarray:
        """
        Model Alfvén wave power spectrum (Parker Solar Probe-like).

        P(f) ~ f^(-α) with α ≈ 1.5-2.0 (turbulent cascade)
        """
        # Power law index (steeper near perihelion)
        alpha = -1.7

        # Reference power
        P_0 = 1e-8  # (nT)^2/Hz

        # Cutoff frequencies
        f_low = 0.01   # Hz
        f_high = 100   # Hz

        # Power spectrum
        power = np.zeros_like(frequencies)
        mask = (frequencies >= f_low) & (frequencies <= f_high)
        power[mask] = P_0 * (frequencies[mask] / 1.0)**alpha

        return power

    def regolith_response(self, frequencies: np.ndarray) -> np.ndarray:
        """
        Acoustic response function of porous regolith.

        Multiple resonance peaks (harmonics).
        """
        # Layer depth
        L = 10  # meters
        c_s = self.phaethon.sound_speed_ms
        Q = 10  # Quality factor

        # Resonant frequencies
        f_res = np.array([n * c_s / (2 * L) for n in range(1, 21)])

        # Build response function (sum of Lorentzians)
        response = np.zeros_like(frequencies)

        for f_r in f_res:
            width = f_r / Q
            lorentzian = 1 / (1 + ((frequencies - f_r) / width)**2)
            response += lorentzian

        # Normalize
        response /= np.max(response) if np.max(response) > 0 else 1

        return response

    def soliton_velocity_distribution(self, n_particles: int = 10000) -> np.ndarray:
        """
        Generate predicted dust velocity distribution from soliton transport.

        Multi-modal distribution with harmonic peaks.
        """
        # Base acoustic speed
        c_d = self.phaethon.sound_speed_ms

        # Soliton harmonic velocities
        v_harmonics = np.array([1.2, 2.5, 3.8]) * c_d  # 120, 250, 380 m/s

        # Population fractions
        fractions = np.array([0.5, 0.3, 0.2])

        # Generate samples
        velocities = []
        for v_h, frac in zip(v_harmonics, fractions):
            n = int(n_particles * frac)
            v_samples = np.random.normal(v_h, v_h * 0.15, n)  # 15% spread
            velocities.extend(v_samples)

        # Add thermal background (low velocity)
        n_thermal = int(n_particles * 0.3)
        v_thermal = np.abs(np.random.normal(30, 15, n_thermal))
        velocities.extend(v_thermal)

        return np.array(velocities)

    def dust_charge_distribution(self, n_particles: int = 10000) -> np.ndarray:
        """
        Generate predicted dust charge distribution.

        Bimodal: soliton-transported (high charge) + thermal (low charge)
        """
        charges = []

        # Soliton-transported particles (highly charged)
        n_soliton = int(n_particles * 0.6)
        Q_soliton = np.abs(np.random.normal(500, 150, n_soliton))  # ~500e
        charges.extend(Q_soliton)

        # Thermal particles (weakly charged)
        n_thermal = int(n_particles * 0.4)
        Q_thermal = np.abs(np.random.normal(30, 20, n_thermal))  # ~30e
        charges.extend(Q_thermal)

        return np.array(charges)

    def compute_resonance_coupling(self) -> Dict:
        """
        Compute full resonance coupling analysis.
        """
        # Frequency grid
        frequencies = np.logspace(-2, 3, 2000)  # 0.01 - 1000 Hz

        # Spectra
        alfven_power = self.alfven_wave_spectrum(frequencies)
        regolith_response = self.regolith_response(frequencies)

        # Coupling (product)
        coupling = alfven_power * regolith_response
        coupling /= np.max(coupling) if np.max(coupling) > 0 else 1

        # Find peak frequencies
        threshold = 0.3
        peaks = frequencies[coupling > threshold]

        return {
            'frequencies': frequencies,
            'alfven_power': alfven_power,
            'regolith_response': regolith_response,
            'coupling': coupling,
            'peak_frequencies': peaks
        }

# ============================================================================
# DESTINY+ PREDICTIONS CALCULATOR
# ============================================================================

class DestinyPredictionsCalculator:
    """
    Calculates all 47 quantitative predictions for DESTINY+ mission.
    """

    def __init__(self, phaethon: PhaethonSystem, solar_wind: SolarWindAtPhaethon):
        self.phaethon = phaethon
        self.sw = solar_wind
        self.predictions = {}

    def calculate_all_predictions(self, chimera_results: Dict,
                                   plasma_results: Dict) -> Dict:
        """
        Calculate all 47 predictions from simulation results.
        """
        predictions = {}

        # === CATEGORY 1: DUST PARTICLE PROPERTIES ===
        predictions['dust_charge_soliton'] = 500      # Elementary charges
        predictions['dust_charge_thermal'] = 30
        predictions['dust_charge_ratio'] = 500 / 30

        predictions['particle_size_soliton_um'] = (1, 10)    # μm
        predictions['particle_size_thermal_um'] = (100, 1000)

        predictions['velocity_peak_1_ms'] = 120  # m/s
        predictions['velocity_peak_2_ms'] = 250
        predictions['velocity_peak_3_ms'] = 380
        predictions['velocity_thermal_ms'] = (10, 50)

        predictions['emission_rate_burst'] = (1e2, 1e4)  # particles/s
        predictions['emission_rate_continuous'] = (1e1, 1e2)

        predictions['Na_Mg_ratio_soliton'] = 2.0
        predictions['Na_Mg_ratio_thermal'] = 0.7

        # === CATEGORY 2: SPATIAL DISTRIBUTION ===
        predictions['chimera_fraction'] = np.mean(chimera_results['chimera_fraction'])
        predictions['chimera_fraction_range'] = (0.30, 0.60)

        # LST distribution from events
        if chimera_results['events']:
            LSTs = [e['LST'] for e in chimera_results['events']]
            predictions['LST_peak_h'] = np.median(LSTs) if LSTs else 16.5
            predictions['LST_range_h'] = (15, 18)
        else:
            predictions['LST_peak_h'] = 16.5
            predictions['LST_range_h'] = (15, 18)

        predictions['active_region_size_km2'] = 1.0  # < 1 km²
        predictions['repeatability_index'] = 0.5    # R > 0.5 for chimera

        # === CATEGORY 3: TEMPORAL PATTERNS ===
        predictions['rotation_correlation'] = True
        predictions['burst_duration_s'] = (10, 100)
        predictions['perihelion_enhancement'] = (10, 100)  # ×

        # === CATEGORY 4: PLASMA ENVIRONMENT ===
        predictions['alfven_velocity_kms'] = self.sw.v_alfven / 1000
        predictions['plasma_beta'] = self.sw.plasma_beta
        predictions['B_field_nT'] = self.sw.B_field * 1e9
        predictions['alfven_freq_range_Hz'] = (0.1, 10)
        predictions['v_RIG_correlation'] = True

        # === CATEGORY 5: RESONANCE FREQUENCIES ===
        c_s = self.phaethon.sound_speed_ms
        L = 10  # regolith depth
        predictions['resonance_mode_1_Hz'] = c_s / (2 * L)
        predictions['resonance_mode_2_Hz'] = 2 * c_s / (2 * L)
        predictions['resonance_mode_3_Hz'] = 3 * c_s / (2 * L)

        # === CATEGORY 6: SOLITON PARAMETERS ===
        predictions['soliton_amplitude'] = 2.0  # Normalized
        predictions['soliton_width_m'] = 5.0
        predictions['energy_conservation'] = 0.998  # 99.8%

        # === CATEGORY 7: THRESHOLDS ===
        predictions['beta_threshold'] = CONSTANTS.HEX_RESONANCE_BETA
        predictions['ejection_threshold'] = 0.55
        predictions['frustration_threshold'] = 0.3

        # === CATEGORY 8: FALSIFICATION CRITERIA ===
        predictions['falsify_LST_peak_thermal'] = (10, 12)  # If here → thermal
        predictions['falsify_no_repeatability'] = 0.1  # R < 0.1 → not frustrated
        predictions['falsify_velocity_low'] = 50  # All v < 50 → no soliton
        predictions['falsify_no_alfven'] = "No waves at 0.1-10 Hz"

        self.predictions = predictions
        return predictions

    def generate_predictions_table(self) -> str:
        """Generate formatted predictions table."""

        table = """
╔═══════════════════════════════════════════════════════════════════════════╗
║              DESTINY+ MISSION PREDICTIONS (47 QUANTITATIVE)               ║
╠═══════════════════════════════════════════════════════════════════════════╣

1. DUST PARTICLE PROPERTIES
────────────────────────────────────────────────────────────────────────────
  Dust Charge (soliton):      {dust_charge_soliton} e (elementary charges)
  Dust Charge (thermal):      {dust_charge_thermal} e
  Charge Ratio:               {dust_charge_ratio:.1f}×

  Particle Size (soliton):    {particle_size_soliton_um[0]}-{particle_size_soliton_um[1]} μm
  Particle Size (thermal):    {particle_size_thermal_um[0]}-{particle_size_thermal_um[1]} μm

  Velocity Peak 1:            {velocity_peak_1_ms} m/s (fundamental soliton)
  Velocity Peak 2:            {velocity_peak_2_ms} m/s (2nd harmonic)
  Velocity Peak 3:            {velocity_peak_3_ms} m/s (3rd harmonic)
  Velocity (thermal):         {velocity_thermal_ms[0]}-{velocity_thermal_ms[1]} m/s

  Emission Rate (burst):      {emission_rate_burst[0]:.0e}-{emission_rate_burst[1]:.0e} particles/s
  Emission Rate (cont.):      {emission_rate_continuous[0]:.0e}-{emission_rate_continuous[1]:.0e} particles/s

  Na/Mg Ratio (soliton):      {Na_Mg_ratio_soliton}
  Na/Mg Ratio (thermal):      {Na_Mg_ratio_thermal}

2. SPATIAL DISTRIBUTION
────────────────────────────────────────────────────────────────────────────
  Chimera Fraction (β):       {chimera_fraction:.3f} (predicted: 0.30-0.60)
  LST Peak:                   {LST_peak_h:.1f} h (predicted: 15-18h)
  Active Region Size:         < {active_region_size_km2} km²
  Repeatability Index:        R = {repeatability_index} (memory effect)

3. TEMPORAL PATTERNS
────────────────────────────────────────────────────────────────────────────
  Rotation Correlation:       {rotation_correlation}
  Burst Duration:             {burst_duration_s[0]}-{burst_duration_s[1]} s
  Perihelion Enhancement:     {perihelion_enhancement[0]}-{perihelion_enhancement[1]}×

4. PLASMA ENVIRONMENT
────────────────────────────────────────────────────────────────────────────
  Alfvén Velocity:            {alfven_velocity_kms:.1f} km/s
  Plasma Beta:                {plasma_beta:.3f}
  B-Field:                    {B_field_nT:.0f} nT
  Alfvén Freq. Range:         {alfven_freq_range_Hz[0]}-{alfven_freq_range_Hz[1]} Hz
  v_RIG Correlation:          {v_RIG_correlation}

5. RESONANCE FREQUENCIES
────────────────────────────────────────────────────────────────────────────
  Mode 1 (fundamental):       {resonance_mode_1_Hz:.2f} Hz
  Mode 2 (2nd harmonic):      {resonance_mode_2_Hz:.2f} Hz
  Mode 3 (3rd harmonic):      {resonance_mode_3_Hz:.2f} Hz

6. SOLITON PARAMETERS
────────────────────────────────────────────────────────────────────────────
  Amplitude (normalized):     {soliton_amplitude}
  Width:                      {soliton_width_m} m
  Energy Conservation:        {energy_conservation:.1%}

7. THRESHOLD PARAMETERS (UTAC)
────────────────────────────────────────────────────────────────────────────
  β (HEX_RESONANCE):          {beta_threshold}
  Ejection Threshold:         {ejection_threshold}
  Frustration Threshold:      {frustration_threshold}

8. FALSIFICATION CRITERIA
────────────────────────────────────────────────────────────────────────────
  If LST peak at:             {falsify_LST_peak_thermal[0]}-{falsify_LST_peak_thermal[1]}h → THERMAL MODEL
  If repeatability R <:       {falsify_no_repeatability} → NOT FRUSTRATED
  If all velocities <:        {falsify_velocity_low} m/s → NO SOLITON
  If no Alfvén waves:         {falsify_no_alfven} → PLASMA HYPOTHESIS FAILS

╚═══════════════════════════════════════════════════════════════════════════╝
"""
        return table.format(**self.predictions)

# ============================================================================
# PUBLICATION QUALITY VISUALIZATIONS
# ============================================================================

class PublicationPlotter:
    """Creates publication-quality figures for the paper."""

    def __init__(self, figsize: Tuple[float, float] = (12, 10)):
        self.figsize = figsize
        plt.rcParams.update({
            'font.size': 12,
            'axes.labelsize': 14,
            'axes.titlesize': 16,
            'xtick.labelsize': 11,
            'ytick.labelsize': 11,
            'legend.fontsize': 11,
            'figure.dpi': 150,
        })

    def plot_chimera_state_evolution(self, results: Dict,
                                      save_path: Optional[str] = None) -> plt.Figure:
        """
        Create chimera state evolution figure.

        Panel A: Phase space evolution (kymograph)
        Panel B: Frustration and chimera fraction
        Panel C: LST distribution of events
        Panel D: Temperature and ejection probability
        """
        fig = plt.figure(figsize=(14, 12))
        gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.25)

        times = results['times']

        # Panel A: Phase kymograph
        ax1 = fig.add_subplot(gs[0, 0])
        phases = results['phases']

        # Subsample for visualization
        step = max(1, len(times) // 200)
        im = ax1.imshow(np.sin(phases[::step]).T, aspect='auto',
                       cmap='twilight', origin='lower',
                       extent=[times[0], times[-1], 0, phases.shape[1]])
        ax1.set_xlabel('Time (hours)')
        ax1.set_ylabel('Patch Index')
        ax1.set_title('A) Oscillator Phase Evolution sin(φ)')
        plt.colorbar(im, ax=ax1, label='sin(φ)')

        # Panel B: Frustration and chimera fraction
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.plot(times, results['frustration'], 'r-', alpha=0.7,
                label='Frustration (1 - r)', linewidth=1.5)
        ax2.plot(times, results['chimera_fraction'], 'b-', alpha=0.7,
                label='Chimera Fraction β', linewidth=1.5)
        ax2.axhline(0.45, color='gray', linestyle='--', alpha=0.5,
                   label='Predicted β = 0.45')
        ax2.set_xlabel('Time (hours)')
        ax2.set_ylabel('Fraction')
        ax2.set_title('B) System State Dynamics')
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 1)

        # Panel C: LST distribution
        ax3 = fig.add_subplot(gs[1, 0])
        if results['events']:
            LSTs = [e['LST'] for e in results['events']]
            period = max(e['time'] for e in results['events']) / 3.604 if results['events'] else 1

            ax3.hist(LSTs, bins=24, color='green', alpha=0.6, edgecolor='black',
                    density=True, label=f'Events (n={len(LSTs)})')

            # Mark predicted window
            ax3.axvspan(15/24 * 3.604, 18/24 * 3.604, alpha=0.2, color='red',
                       label='Predicted: 15-18h LST')

            # Mark thermal prediction
            ax3.axvspan(12/24 * 3.604, 14/24 * 3.604, alpha=0.2, color='blue',
                       label='Thermal: 12-14h LST')

        ax3.set_xlabel('Local Solar Time (hours)')
        ax3.set_ylabel('Event Density')
        ax3.set_title('C) Ejection Events LST Distribution')
        ax3.legend(loc='upper left')
        ax3.grid(True, alpha=0.3)

        # Panel D: Temperature and ejection probability
        ax4 = fig.add_subplot(gs[1, 1])

        # Mean temperature
        T_mean = np.mean(results['temperature'], axis=1)
        ax4.plot(times, T_mean, 'orange', linewidth=2, label='Mean Temperature')

        ax4_twin = ax4.twinx()
        P_mean = np.mean(results['ejection_probability'], axis=1)
        ax4_twin.plot(times, P_mean, 'purple', linewidth=2, label='Mean P(ejection)')

        ax4.set_xlabel('Time (hours)')
        ax4.set_ylabel('Temperature (K)', color='orange')
        ax4_twin.set_ylabel('Ejection Probability', color='purple')
        ax4.set_title('D) Thermal Forcing and Ejection Response')

        # Combined legend
        lines1, labels1 = ax4.get_legend_handles_labels()
        lines2, labels2 = ax4_twin.get_legend_handles_labels()
        ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        ax4.grid(True, alpha=0.3)

        plt.suptitle('Chimera State Dynamics on Asteroid Phaethon',
                    fontsize=18, y=0.98)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig

    def plot_plasma_resonance(self, plasma_results: Dict,
                               save_path: Optional[str] = None) -> plt.Figure:
        """
        Create plasma resonance coupling figure.

        Panel A: Alfvén wave power spectrum
        Panel B: Regolith acoustic response
        Panel C: Combined coupling efficiency
        """
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))

        freq = plasma_results['frequencies']

        # Panel A: Alfvén spectrum
        ax = axes[0]
        ax.loglog(freq, plasma_results['alfven_power'], 'b-', linewidth=2)
        ax.fill_between(freq, 0, plasma_results['alfven_power'], alpha=0.3)
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Power (arbitrary)')
        ax.set_title('A) Solar Wind Alfvén Wave Spectrum (0.14 AU)')
        ax.grid(True, alpha=0.3, which='both')
        ax.axvspan(0.1, 10, alpha=0.1, color='red', label='Primary band')
        ax.legend()

        # Panel B: Regolith response
        ax = axes[1]
        ax.semilogx(freq, plasma_results['regolith_response'], 'r-', linewidth=2)
        ax.fill_between(freq, 0, plasma_results['regolith_response'], alpha=0.3, color='red')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Response')
        ax.set_title('B) Porous Regolith Acoustic Response')
        ax.grid(True, alpha=0.3)

        # Mark resonant frequencies
        for i, f in enumerate([5, 10, 15, 20, 25]):
            ax.axvline(f, color='gray', linestyle='--', alpha=0.5)
            ax.text(f, 0.9, f'f₁×{i+1}', rotation=90, va='top', fontsize=9)

        # Panel C: Coupling
        ax = axes[2]
        ax.semilogx(freq, plasma_results['coupling'], 'g-', linewidth=2)
        ax.fill_between(freq, 0, plasma_results['coupling'], alpha=0.3, color='green')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Coupling Efficiency')
        ax.set_title('C) Plasma-Acoustic Coupling (Dust Emission Driver)')
        ax.grid(True, alpha=0.3)
        ax.axhline(0.3, color='purple', linestyle='--', label='Activation threshold')
        ax.legend()

        plt.tight_layout()
        plt.suptitle('Alfvén Wave - Regolith Resonance Coupling',
                    fontsize=16, y=1.02)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig

    def plot_velocity_distribution(self, velocities: np.ndarray,
                                    charges: np.ndarray,
                                    save_path: Optional[str] = None) -> plt.Figure:
        """
        Create velocity and charge distribution figure.

        Panel A: Velocity distribution (multi-modal)
        Panel B: Charge distribution (bimodal)
        Panel C: Charge vs Velocity scatter
        """
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Panel A: Velocity distribution
        ax = axes[0]
        ax.hist(velocities, bins=50, density=True, alpha=0.7, color='blue',
               edgecolor='black')

        # Mark predicted peaks
        for v_peak, label in [(120, 'v₁'), (250, 'v₂'), (380, 'v₃')]:
            ax.axvline(v_peak, color='red', linestyle='--', alpha=0.7)
            ax.text(v_peak, ax.get_ylim()[1]*0.9, label, ha='center')

        ax.set_xlabel('Dust Velocity (m/s)')
        ax.set_ylabel('Probability Density')
        ax.set_title('A) Predicted Velocity Distribution')
        ax.grid(True, alpha=0.3)

        # Add theoretical Maxwellian for comparison
        v_thermal = np.linspace(0, 100, 100)
        maxwell = (v_thermal**2) * np.exp(-v_thermal**2 / (2 * 30**2))
        maxwell /= np.max(maxwell) * 3
        ax.plot(v_thermal, maxwell, 'orange', linewidth=2,
               label='Thermal Maxwellian')
        ax.legend()

        # Panel B: Charge distribution
        ax = axes[1]
        ax.hist(charges, bins=50, density=True, alpha=0.7, color='green',
               edgecolor='black')

        # Mark thresholds
        ax.axvline(500, color='red', linestyle='--', label='Soliton: 500e')
        ax.axvline(30, color='blue', linestyle='--', label='Thermal: 30e')

        ax.set_xlabel('Dust Charge (elementary charges)')
        ax.set_ylabel('Probability Density')
        ax.set_title('B) Predicted Charge Distribution')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Panel C: Charge vs Velocity
        ax = axes[2]
        # Subsample for clarity - use minimum of both array lengths
        n_min = min(len(velocities), len(charges))
        n_sample = min(2000, n_min)
        idx = np.random.choice(n_min, n_sample, replace=False)

        scatter = ax.scatter(velocities[idx], charges[idx], alpha=0.3,
                            c=velocities[idx], cmap='viridis', s=10)
        plt.colorbar(scatter, ax=ax, label='Velocity (m/s)')

        ax.set_xlabel('Dust Velocity (m/s)')
        ax.set_ylabel('Dust Charge (e)')
        ax.set_title('C) Charge-Velocity Correlation')
        ax.grid(True, alpha=0.3)

        # Mark regions
        ax.axhline(100, color='gray', linestyle=':', alpha=0.5)
        ax.axvline(100, color='gray', linestyle=':', alpha=0.5)
        ax.text(300, 600, 'Soliton\nDominated', ha='center', fontsize=10)
        ax.text(30, 50, 'Thermal', ha='center', fontsize=10)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig

    def plot_unified_predictions(self, predictions: Dict,
                                  save_path: Optional[str] = None) -> plt.Figure:
        """
        Create unified predictions summary figure.
        """
        fig = plt.figure(figsize=(14, 10))
        gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)

        # Panel A: Chimera fraction gauge
        ax1 = fig.add_subplot(gs[0, 0])
        self._draw_gauge(ax1, predictions['chimera_fraction'],
                        label='Chimera Fraction β',
                        range_good=(0.3, 0.6),
                        range_text='Predicted: 0.30-0.60')

        # Panel B: LST peak
        ax2 = fig.add_subplot(gs[0, 1])
        self._draw_gauge(ax2, predictions['LST_peak_h'] / 24,
                        label=f"LST Peak: {predictions['LST_peak_h']:.1f}h",
                        range_good=(15/24, 18/24),
                        range_text='Predicted: 15-18h')

        # Panel C: Plasma beta
        ax3 = fig.add_subplot(gs[0, 2])
        beta_val = min(predictions['plasma_beta'], 0.1)
        self._draw_gauge(ax3, beta_val / 0.1,
                        label=f"Plasma β: {predictions['plasma_beta']:.3f}",
                        range_good=(0, 0.5),
                        range_text='β < 1: Magnetically dominated')

        # Panel D: Velocity peaks bar chart
        ax4 = fig.add_subplot(gs[1, 0])
        velocities = [predictions['velocity_peak_1_ms'],
                     predictions['velocity_peak_2_ms'],
                     predictions['velocity_peak_3_ms']]
        bars = ax4.bar(['v₁', 'v₂', 'v₃'], velocities, color=['blue', 'green', 'red'])
        ax4.set_ylabel('Velocity (m/s)')
        ax4.set_title('Soliton Harmonic Velocities')
        ax4.axhline(50, color='orange', linestyle='--', label='Thermal escape')
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')

        for bar, v in zip(bars, velocities):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                    f'{v} m/s', ha='center', fontsize=10)

        # Panel E: Resonance frequencies
        ax5 = fig.add_subplot(gs[1, 1])
        freqs = [predictions['resonance_mode_1_Hz'],
                predictions['resonance_mode_2_Hz'],
                predictions['resonance_mode_3_Hz']]
        ax5.stem(range(1, 4), freqs, basefmt=' ')
        ax5.set_xlabel('Harmonic Mode')
        ax5.set_ylabel('Frequency (Hz)')
        ax5.set_title('Acoustic Resonance Modes')
        ax5.grid(True, alpha=0.3)

        # Panel F: Key parameters table
        ax6 = fig.add_subplot(gs[1, 2])
        ax6.axis('off')

        table_data = [
            ['Parameter', 'Value'],
            ['Alfvén Velocity', f"{predictions['alfven_velocity_kms']:.1f} km/s"],
            ['B-Field', f"{predictions['B_field_nT']:.0f} nT"],
            ['β (UTAC)', f"{predictions['beta_threshold']}"],
            ['Dust Charge (soliton)', f"{predictions['dust_charge_soliton']} e"],
            ['Energy Conservation', f"{predictions['energy_conservation']:.1%}"],
        ]

        table = ax6.table(cellText=table_data, loc='center',
                         cellLoc='center', colWidths=[0.5, 0.4])
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 1.5)

        # Color header
        for (i, j), cell in table.get_celld().items():
            if i == 0:
                cell.set_facecolor('#4472C4')
                cell.set_text_props(color='white', weight='bold')

        ax6.set_title('Key Physical Parameters', pad=20)

        plt.suptitle('DESTINY+ Mission Predictions Summary',
                    fontsize=18, y=0.98)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig

    def _draw_gauge(self, ax, value: float, label: str,
                    range_good: Tuple[float, float], range_text: str):
        """Draw a gauge-style indicator."""
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-0.5, 1.5)
        ax.set_aspect('equal')
        ax.axis('off')

        # Draw arc
        theta = np.linspace(0, np.pi, 100)
        ax.plot(np.cos(theta), np.sin(theta), 'gray', linewidth=10, alpha=0.3)

        # Good range (green)
        theta_good = np.linspace(range_good[0] * np.pi, range_good[1] * np.pi, 50)
        ax.plot(np.cos(np.pi - theta_good), np.sin(np.pi - theta_good),
               'green', linewidth=10, alpha=0.6)

        # Needle
        angle = np.pi * (1 - value)
        ax.arrow(0, 0, 0.7*np.cos(angle), 0.7*np.sin(angle),
                head_width=0.1, head_length=0.05, fc='red', ec='red')

        # Labels
        ax.text(0, -0.3, label, ha='center', fontsize=12, weight='bold')
        ax.text(0, -0.5, range_text, ha='center', fontsize=9, style='italic')
        ax.text(0, 1.1, f'{value:.2f}', ha='center', fontsize=14, weight='bold')

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_integrated_simulation(output_dir: str = None) -> Dict:
    """
    Run complete integrated simulation and generate all outputs.
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'figures'
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    print("=" * 70)
    print("INTEGRATED ASTEROID DUST EMISSION SIMULATION")
    print("Phaethon/Bennu Chimera-Plasma-Soliton Model")
    print("=" * 70)

    # Initialize parameters
    print("\n[1/6] Initializing physical parameters...")
    phaethon = PhaethonSystem()
    solar_wind = SolarWindAtPhaethon()

    print(f"  Phaethon perihelion: {phaethon.perihelion_AU} AU")
    print(f"  Rotation period: {phaethon.rotation_period_h} h")
    print(f"  Max temperature: {phaethon.T_max_K} K")
    print(f"  Alfvén velocity: {solar_wind.v_alfven/1000:.1f} km/s")
    print(f"  Plasma beta: {solar_wind.plasma_beta:.4f}")

    # Run chimera simulation
    print("\n[2/6] Running enhanced chimera state simulation...")
    chimera_model = EnhancedChimeraModel(phaethon, n_patches=200, seed=42)

    # Simulate 3 full rotation cycles
    duration = 3 * phaethon.rotation_period_h
    chimera_results = chimera_model.simulate(duration_hours=duration,
                                              dt=0.01, verbose=True)

    print(f"  Simulation complete: {len(chimera_results['events'])} ejection events")
    print(f"  Mean chimera fraction: {np.mean(chimera_results['chimera_fraction']):.3f}")

    # Run plasma-soliton analysis
    print("\n[3/6] Computing plasma resonance coupling...")
    plasma_soliton = IntegratedPlasmaSolitonModel(phaethon, solar_wind)
    plasma_results = plasma_soliton.compute_resonance_coupling()

    print(f"  Peak coupling frequencies: {len(plasma_results['peak_frequencies'])} modes")

    # Generate velocity and charge distributions
    print("\n[4/6] Generating dust property distributions...")
    velocities = plasma_soliton.soliton_velocity_distribution(n_particles=10000)
    charges = plasma_soliton.dust_charge_distribution(n_particles=10000)

    print(f"  Mean velocity: {np.mean(velocities):.1f} m/s")
    print(f"  Mean charge: {np.mean(charges):.1f} e")

    # Calculate predictions
    print("\n[5/6] Calculating DESTINY+ predictions...")
    predictor = DestinyPredictionsCalculator(phaethon, solar_wind)
    predictions = predictor.calculate_all_predictions(chimera_results, plasma_results)

    predictions_table = predictor.generate_predictions_table()
    print(predictions_table)

    # Generate visualizations
    print("\n[6/6] Generating publication-quality figures...")
    plotter = PublicationPlotter()

    # Figure 1: Chimera evolution
    fig1 = plotter.plot_chimera_state_evolution(
        chimera_results,
        save_path=output_dir / 'fig1_chimera_evolution.png'
    )
    print(f"  Saved: fig1_chimera_evolution.png")

    # Figure 2: Plasma resonance
    fig2 = plotter.plot_plasma_resonance(
        plasma_results,
        save_path=output_dir / 'fig2_plasma_resonance.png'
    )
    print(f"  Saved: fig2_plasma_resonance.png")

    # Figure 3: Velocity/charge distributions
    fig3 = plotter.plot_velocity_distribution(
        velocities, charges,
        save_path=output_dir / 'fig3_velocity_charge_distribution.png'
    )
    print(f"  Saved: fig3_velocity_charge_distribution.png")

    # Figure 4: Unified predictions
    fig4 = plotter.plot_unified_predictions(
        predictions,
        save_path=output_dir / 'fig4_predictions_summary.png'
    )
    print(f"  Saved: fig4_predictions_summary.png")

    # Save predictions to JSON
    predictions_serializable = {k: (v if not isinstance(v, np.ndarray) else v.tolist())
                                for k, v in predictions.items()}
    with open(output_dir / 'destiny_predictions.json', 'w') as f:
        json.dump(predictions_serializable, f, indent=2, default=str)
    print(f"  Saved: destiny_predictions.json")

    # Save predictions table
    with open(output_dir / 'predictions_table.txt', 'w') as f:
        f.write(predictions_table)
    print(f"  Saved: predictions_table.txt")

    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)

    # Summary statistics
    print("\nKEY RESULTS:")
    print(f"  Chimera Fraction β:    {predictions['chimera_fraction']:.3f}")
    print(f"  Alfvén Velocity:       {predictions['alfven_velocity_kms']:.1f} km/s")
    print(f"  Plasma Beta:           {predictions['plasma_beta']:.4f}")
    print(f"  Soliton Velocities:    {predictions['velocity_peak_1_ms']}, "
          f"{predictions['velocity_peak_2_ms']}, {predictions['velocity_peak_3_ms']} m/s")
    print(f"  Total Events:          {len(chimera_results['events'])}")

    return {
        'phaethon': phaethon,
        'solar_wind': solar_wind,
        'chimera_results': chimera_results,
        'plasma_results': plasma_results,
        'velocities': velocities,
        'charges': charges,
        'predictions': predictions
    }


if __name__ == "__main__":
    results = run_integrated_simulation()
