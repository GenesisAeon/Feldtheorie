"""
Chimera State Model for Asteroid Bennu
========================================

Models the coexistence of "jammed" (solid) and "fluidized" (gas-like) regolith
phases on asteroid (101955) Bennu under the influence of:
  - Thermal stress (day/night cycling)
  - Electrostatic forces (photoelectron layer)
  - Micro-gravity (g ~ 10^-5 m/s^2)

Based on:
  - OSIRIS-REx observational data (2018-2021)
  - Frustrated systems theory (spin-glass analogy)
  - Kuramoto-like coupled oscillator models

Author: Johann Benjamin Römer
Framework: GenesisAeon v10.2 / UTAC Case Study
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from dataclasses import dataclass
from typing import Tuple, List

@dataclass
class BennuParameters:
    """Physical parameters for Bennu from OSIRIS-REx"""
    
    # Gravitational
    surface_gravity: float = 1e-5  # m/s^2 (micro-gravity)
    escape_velocity: float = 0.20  # m/s
    
    # Thermal
    max_temperature: float = 400   # K (dayside)
    min_temperature: float = 100   # K (nightside)
    rotation_period: float = 4.297 # hours
    
    # Material properties
    cohesion_strength: float = 0.5  # Pascal (extremely weak)
    porosity: float = 0.50          # 50% void space
    regolith_depth: float = 5.0     # meters (estimated)
    
    # Electrostatic
    photoemission_current: float = 1e-8  # A/m^2 (UV-driven)
    surface_potential: float = 5.0       # Volts (dayside)
    
    # Observational constraints
    ejection_time_window: Tuple[float, float] = (15.0, 18.0)  # LST (local solar time)
    typical_particle_size: float = 0.01   # meters (cm-scale)
    ejection_velocity: float = 0.10       # m/s (sub-escape)
    

class ChimeraStateModel:
    """
    Models the frustrated regolith system as coupled oscillators.
    
    Each "oscillator" represents a patch of regolith that can be in:
      - Phase 0: Jammed (solid-like, coherent oscillation)
      - Phase 1: Unjammed (fluid-like, incoherent motion)
    """
    
    def __init__(self, params: BennuParameters, n_patches: int = 100):
        self.params = params
        self.n_patches = n_patches
        
        # Initialize random phases and natural frequencies
        self.phases = np.random.uniform(0, 2*np.pi, n_patches)
        self.omega_natural = np.random.normal(1.0, 0.1, n_patches)  # Natural frequencies
        
        # Coupling matrix (all-to-all for simplicity)
        self.coupling_strength = 0.5  # K in Kuramoto model
        
    def thermal_forcing(self, t: float) -> float:
        """
        Solar heating cycle (simplified sinusoid).
        
        Parameters:
            t : time in hours since sunrise
            
        Returns:
            Thermal stress amplitude (normalized 0-1)
        """
        period_hours = self.params.rotation_period
        phase = 2 * np.pi * t / period_hours
        return 0.5 * (1 + np.sin(phase - np.pi/2))  # Peak at "noon"
    
    def electrostatic_forcing(self, t: float) -> float:
        """
        Photoelectric effect modulation (day/night).
        
        Parameters:
            t : time in hours
            
        Returns:
            Electrostatic force amplitude (normalized 0-1)
        """
        period_hours = self.params.rotation_period
        phase = 2 * np.pi * t / period_hours
        
        # Only active on dayside (> 0)
        dayside = np.maximum(0, np.sin(phase))
        return dayside
    
    def frustration_parameter(self, theta: np.ndarray) -> float:
        """
        Measure of frustration: inability to synchronize.
        
        Parameters:
            theta : array of oscillator phases
            
        Returns:
            Frustration F in [0, 1] where:
              F ~ 0 : fully coherent (all jammed)
              F ~ 1 : fully incoherent (all fluidized)
        """
        # Order parameter (Kuramoto)
        r = np.abs(np.mean(np.exp(1j * theta)))
        
        # Frustration is inverse of order
        return 1 - r
    
    def chimera_fraction(self, theta: np.ndarray, threshold: float = 0.3) -> float:
        """
        Fraction of system in 'unjammed' (chimera) state.
        
        Parameters:
            theta : oscillator phases
            threshold : coherence threshold for jamming
            
        Returns:
            Fraction in range [0, 1]
        """
        # Compute local order parameter for each oscillator
        local_order = np.zeros(len(theta))
        for i in range(len(theta)):
            # Measure synchrony with neighbors
            neighbors = theta[np.abs(np.arange(len(theta)) - i) <= 5]  # Window of 5
            local_order[i] = np.abs(np.mean(np.exp(1j * neighbors)))
        
        # Count how many are below threshold (unjammed)
        unjammed_count = np.sum(local_order < threshold)
        return unjammed_count / len(theta)
    
    def ejection_probability(self, chimera_frac: float, thermal: float, 
                            electrostatic: float) -> float:
        """
        Probability of particle ejection event.
        
        Combines:
          - Degree of fluidization (chimera fraction)
          - Thermal stress
          - Electrostatic lifting force
          
        Returns:
            P(ejection) in [0, 1]
        """
        # Threshold model (UTAC-style)
        beta = 3.5  # Steepness parameter
        threshold = 0.6  # Combined stress threshold
        
        # Combined stress
        stress = 0.4 * thermal + 0.3 * electrostatic + 0.3 * chimera_frac
        
        # Sigmoid activation
        prob = 1 / (1 + np.exp(-beta * (stress - threshold)))
        return prob
    
    def kuramoto_dynamics(self, theta: np.ndarray, t: float) -> np.ndarray:
        """
        Kuramoto model with external forcing.
        
        d(theta_i)/dt = omega_i + (K/N) * sum_j sin(theta_j - theta_i) + F(t)
        
        Parameters:
            theta : current phases
            t : time
            
        Returns:
            dtheta/dt
        """
        N = len(theta)
        K = self.coupling_strength
        
        # Natural frequency term
        dtheta = self.omega_natural.copy()
        
        # Coupling term (all-to-all)
        for i in range(N):
            coupling_sum = np.sum(np.sin(theta - theta[i]))
            dtheta[i] += (K / N) * coupling_sum
        
        # External forcing (thermal stress disrupts synchrony)
        thermal = self.thermal_forcing(t)
        noise = thermal * np.random.normal(0, 0.1, N)  # Thermal noise
        dtheta += noise
        
        return dtheta
    
    def simulate(self, duration_hours: float = 12.0, dt: float = 0.1) -> dict:
        """
        Run full simulation over multiple rotation cycles.
        
        Parameters:
            duration_hours : simulation time
            dt : time step
            
        Returns:
            Dictionary with time series data
        """
        times = np.arange(0, duration_hours, dt)
        n_steps = len(times)
        
        # Preallocate arrays
        theta_history = np.zeros((n_steps, self.n_patches))
        frustration_history = np.zeros(n_steps)
        chimera_fraction_history = np.zeros(n_steps)
        ejection_prob_history = np.zeros(n_steps)
        events = []
        
        # Initial condition
        theta = self.phases.copy()
        
        for i, t in enumerate(times):
            # Store current state
            theta_history[i] = theta
            frustration_history[i] = self.frustration_parameter(theta)
            chimera_fraction_history[i] = self.chimera_fraction(theta)
            
            # Calculate ejection probability
            thermal = self.thermal_forcing(t)
            electrostatic = self.electrostatic_forcing(t)
            ejection_prob = self.ejection_probability(
                chimera_fraction_history[i], thermal, electrostatic
            )
            ejection_prob_history[i] = ejection_prob
            
            # Check for ejection event (stochastic)
            if np.random.rand() < ejection_prob * dt:
                # Record event with LST
                lst = t % self.params.rotation_period
                events.append({
                    'time': t,
                    'LST': lst,
                    'chimera_fraction': chimera_fraction_history[i],
                    'thermal': thermal,
                    'electrostatic': electrostatic
                })
            
            # Evolve dynamics
            dtheta = self.kuramoto_dynamics(theta, t)
            theta += dtheta * dt
            theta = theta % (2 * np.pi)  # Wrap phases
        
        return {
            'times': times,
            'theta_history': theta_history,
            'frustration': frustration_history,
            'chimera_fraction': chimera_fraction_history,
            'ejection_probability': ejection_prob_history,
            'events': events
        }
    
    def plot_results(self, results: dict):
        """Create diagnostic plots"""
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        times = results['times']
        
        # Plot 1: Frustration and Chimera Fraction
        ax = axes[0]
        ax.plot(times, results['frustration'], label='Frustration', color='red', alpha=0.7)
        ax.plot(times, results['chimera_fraction'], label='Chimera Fraction', color='blue', alpha=0.7)
        ax.set_ylabel('Fraction')
        ax.set_xlabel('Time (hours)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_title('System State Evolution')
        
        # Plot 2: Ejection Probability
        ax = axes[1]
        ax.plot(times, results['ejection_probability'], color='orange', linewidth=2)
        ax.set_ylabel('Ejection Probability')
        ax.set_xlabel('Time (hours)')
        ax.grid(True, alpha=0.3)
        ax.set_title('Particle Ejection Likelihood')
        
        # Plot 3: LST Distribution of Events
        ax = axes[2]
        if results['events']:
            lsts = [evt['LST'] for evt in results['events']]
            ax.hist(lsts, bins=20, color='green', alpha=0.6, edgecolor='black')
            ax.axvspan(15, 18, alpha=0.2, color='red', label='Observed window (OSIRIS-REx)')
            ax.set_xlabel('Local Solar Time (hours)')
            ax.set_ylabel('Event Count')
            ax.legend()
            ax.set_title(f'Ejection Events (n={len(results["events"])})')
        else:
            ax.text(0.5, 0.5, 'No events detected', ha='center', va='center', 
                   transform=ax.transAxes)
        
        plt.tight_layout()
        return fig


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("Chimera State Model for Bennu")
    print("=" * 60)
    
    # Initialize with Bennu parameters
    params = BennuParameters()
    model = ChimeraStateModel(params, n_patches=100)
    
    print(f"Running simulation over {3 * params.rotation_period:.1f} hours")
    print(f"({3:.0f} rotation cycles)")
    print()
    
    # Run simulation
    results = model.simulate(duration_hours=3 * params.rotation_period, dt=0.05)
    
    # Analysis
    print(f"Total events detected: {len(results['events'])}")
    if results['events']:
        lsts = [evt['LST'] for evt in results['events']]
        print(f"LST range: {min(lsts):.1f} - {max(lsts):.1f} hours")
        print(f"Mean LST: {np.mean(lsts):.1f} hours")
        
        # Check if events cluster in observed window
        in_window = [lst for lst in lsts if 15 <= lst <= 18]
        print(f"Events in observed window (15-18h): {len(in_window)} ({100*len(in_window)/len(lsts):.1f}%)")
    
    print("\nGenerating plots...")
    fig = model.plot_results(results)
    plt.savefig('/home/claude/bennu_chimera_simulation.png', dpi=150, bbox_inches='tight')
    print("Saved to: bennu_chimera_simulation.png")
    
    print("\n✓ Simulation complete!")
