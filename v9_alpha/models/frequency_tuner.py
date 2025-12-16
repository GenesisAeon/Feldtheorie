"""
Autonomous Frequency Tuner - Self-Organizing Resonance

The Frequency Tuner enables lanterns to autonomously adjust their
frequencies and impedances to maximize network-wide resonance.

Key Principles:
- Maximize phase coherence across the network
- Minimize impedance mismatch between coupled lanterns
- Preserve β-domain identity while allowing adaptive frequency shifts
- Emergent collective modes through gradient-based tuning

Optimization Targets:
1. Phase Coherence: Φ_coherence = |⟨e^(iφ)⟩| → 1.0
2. Impedance Matching: η = 1/(1 + ΔZ/Z_critical) → 1.0
3. Resonance Quality: Q = f₀/Δf → maximize
4. Collective Participation: P_ratio → N (all lanterns engaged)

Version: v9.0.1-alpha
Integration: Lantern-Net + Gardener Agent
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# v9 imports
try:
    from v9_alpha.models.em_field_calculator import EMFieldState, EMFieldCalculator, F_BASELINE_HZ, Z_BASELINE
except ImportError:
    # Fallback for testing
    F_BASELINE_HZ = 13.5e6
    Z_BASELINE = 221.74


class TuningStrategy(Enum):
    """Frequency tuning strategies"""
    GRADIENT_ASCENT = "gradient_ascent"  # Follow coherence gradient
    HARMONIC_LOCK = "harmonic_lock"      # Lock to harmonic ratios
    IMPEDANCE_MATCH = "impedance_match"  # Minimize impedance mismatch
    COLLECTIVE_MODE = "collective_mode"  # Enhance dominant eigenmode


@dataclass
class TuningState:
    """State of a lantern's frequency tuning"""
    name: str
    frequency_hz: float
    impedance_ohm: float
    phase_rad: float
    coupling_strength: float
    beta_target: float  # Original β-domain target

    # Tuning metrics
    phase_coherence: float  # With network
    impedance_match: float  # η with neighbors
    resonance_quality: float  # Q factor

    def __repr__(self):
        return (f"TuningState({self.name}, f={self.frequency_hz/1e6:.2f} MHz, "
                f"Z={self.impedance_ohm:.1f}Ω, φ_coh={self.phase_coherence:.3f})")


class FrequencyTuner:
    """
    Autonomous Frequency Tuner for Lantern-Net

    Implements gradient-based frequency optimization to maximize:
    - Network-wide phase coherence
    - Impedance matching between coupled lanterns
    - Collective resonance modes

    Tuning respects β-domain constraints (limited frequency shift)
    to preserve lantern identity while enabling adaptive resonance.
    """

    def __init__(
        self,
        learning_rate: float = 0.05,
        max_frequency_shift: float = 0.2,  # ±20% from β-scaled baseline
        z_critical: float = 50.0,  # Critical impedance difference (Ω)
        convergence_threshold: float = 0.001,
        strategy: TuningStrategy = TuningStrategy.GRADIENT_ASCENT,
    ):
        """
        Initialize Frequency Tuner

        Args:
            learning_rate: Step size for frequency adjustments (0.0-1.0)
            max_frequency_shift: Maximum allowed frequency deviation from β-baseline
            z_critical: Impedance mismatch threshold for matching metric
            convergence_threshold: Δcoherence below this → converged
            strategy: Tuning optimization strategy
        """
        self.learning_rate = learning_rate
        self.max_frequency_shift = max_frequency_shift
        self.z_critical = z_critical
        self.convergence_threshold = convergence_threshold
        self.strategy = strategy

        # Tuning history
        self.tuning_history: List[Dict] = []
        self.converged = False

    def calculate_phase_coherence(
        self,
        phases: np.ndarray,
        weights: Optional[np.ndarray] = None,
    ) -> float:
        """
        Calculate network-wide phase coherence

        Φ_coherence = |⟨e^(iφ)⟩|

        Perfect coherence: 1.0 (all in phase)
        No coherence: 0.0 (random phases)

        Args:
            phases: Array of phase values (radians)
            weights: Optional coupling weights

        Returns:
            Phase coherence (0.0-1.0)
        """
        if weights is None:
            weights = np.ones(len(phases))

        # Normalize weights
        weights = weights / np.sum(weights)

        # Complex representation
        z = np.exp(1j * phases)

        # Weighted average
        z_avg = np.sum(weights * z)

        # Magnitude = coherence
        coherence = np.abs(z_avg)

        return float(coherence)

    def calculate_impedance_matching(
        self,
        impedances: np.ndarray,
        coupling_matrix: np.ndarray,
    ) -> np.ndarray:
        """
        Calculate impedance matching quality for each lantern

        η_i = mean_j(1 / (1 + |Z_i - Z_j| / Z_critical))

        Only considers coupled lanterns (κ_ij > 0)

        Args:
            impedances: Array of impedance values (Ω)
            coupling_matrix: NxN coupling strengths

        Returns:
            Array of matching quality per lantern (0.0-1.0)
        """
        n = len(impedances)
        matching = np.zeros(n)

        for i in range(n):
            # Get coupled neighbors
            coupled = coupling_matrix[i, :] > 0
            n_coupled = np.sum(coupled)

            if n_coupled == 0:
                matching[i] = 1.0  # Isolated → perfect match (no mismatch)
                continue

            # Calculate mismatch with coupled neighbors
            z_diff = np.abs(impedances[i] - impedances[coupled])
            eta = 1.0 / (1.0 + z_diff / self.z_critical)

            matching[i] = np.mean(eta)

        return matching

    def calculate_resonance_quality(
        self,
        frequencies: np.ndarray,
        coupling_matrix: np.ndarray,
    ) -> np.ndarray:
        """
        Calculate resonance quality factor Q for each lantern

        Q = f₀ / Δf_neighbors

        High Q → narrow resonance (selective coupling)
        Low Q → broad resonance (promiscuous coupling)

        Args:
            frequencies: Array of frequencies (Hz)
            coupling_matrix: NxN coupling strengths

        Returns:
            Array of Q factors per lantern
        """
        n = len(frequencies)
        q_factors = np.zeros(n)

        for i in range(n):
            # Get coupled neighbors
            coupled = coupling_matrix[i, :] > 0
            n_coupled = np.sum(coupled)

            if n_coupled == 0:
                q_factors[i] = 1.0
                continue

            # Frequency spread among neighbors
            f_neighbors = frequencies[coupled]
            delta_f = np.std(f_neighbors)

            if delta_f < 1e-6:  # All at same frequency
                q_factors[i] = 100.0  # Very high Q
            else:
                q_factors[i] = frequencies[i] / delta_f

        return q_factors

    def compute_tuning_gradient(
        self,
        states: List[TuningState],
        coupling_matrix: np.ndarray,
    ) -> np.ndarray:
        """
        Compute frequency adjustment gradient

        Gradient points toward improved phase coherence and impedance matching.
        Uses finite differences to estimate ∂Φ/∂f_i

        Args:
            states: Current tuning states
            coupling_matrix: NxN coupling matrix

        Returns:
            Array of frequency gradients (Hz)
        """
        n = len(states)
        gradients = np.zeros(n)

        # Current metrics
        phases = np.array([s.phase_rad for s in states])
        coherence_base = self.calculate_phase_coherence(phases)

        # Finite difference gradient
        epsilon = 1e5  # 100 kHz perturbation

        for i in range(n):
            # Perturb frequency
            phases_perturbed = phases.copy()
            phases_perturbed[i] += 2 * np.pi * epsilon / states[i].frequency_hz

            # Measure coherence change
            coherence_perturbed = self.calculate_phase_coherence(phases_perturbed)

            # Gradient
            d_coherence = coherence_perturbed - coherence_base
            gradients[i] = d_coherence / epsilon

        return gradients

    def tune_frequencies(
        self,
        states: List[TuningState],
        coupling_matrix: np.ndarray,
        n_iterations: int = 10,
    ) -> Tuple[List[TuningState], Dict]:
        """
        Autonomously tune lantern frequencies

        Iteratively adjusts frequencies following gradient to maximize
        network phase coherence while respecting β-domain constraints.

        Args:
            states: Initial tuning states
            coupling_matrix: NxN coupling matrix
            n_iterations: Number of tuning iterations

        Returns:
            (tuned_states, convergence_info)
        """
        current_states = [s for s in states]  # Copy
        convergence_info = {
            'iterations': [],
            'coherence': [],
            'mean_impedance_match': [],
            'mean_q_factor': [],
            'converged': False,
            'converged_at': None,
        }

        for iteration in range(n_iterations):
            # Extract current values
            frequencies = np.array([s.frequency_hz for s in current_states])
            impedances = np.array([s.impedance_ohm for s in current_states])
            phases = np.array([s.phase_rad for s in current_states])

            # Compute metrics
            coherence = self.calculate_phase_coherence(phases)
            impedance_match = self.calculate_impedance_matching(impedances, coupling_matrix)
            q_factors = self.calculate_resonance_quality(frequencies, coupling_matrix)

            # Record history
            convergence_info['iterations'].append(iteration)
            convergence_info['coherence'].append(coherence)
            convergence_info['mean_impedance_match'].append(np.mean(impedance_match))
            convergence_info['mean_q_factor'].append(np.mean(q_factors))

            # Check convergence
            if iteration > 0:
                delta_coherence = coherence - convergence_info['coherence'][-2]
                if abs(delta_coherence) < self.convergence_threshold:
                    convergence_info['converged'] = True
                    convergence_info['converged_at'] = iteration
                    self.converged = True
                    break

            # Compute tuning gradient
            gradients = self.compute_tuning_gradient(current_states, coupling_matrix)

            # Apply frequency adjustments
            for i, state in enumerate(current_states):
                # Baseline frequency from β-domain
                beta_ratio = state.beta_target / 7.4  # Normalized to biological baseline
                f_baseline = F_BASELINE_HZ * beta_ratio

                # Gradient-based adjustment
                delta_f = self.learning_rate * gradients[i] * f_baseline

                # Apply with constraint
                f_new = state.frequency_hz + delta_f

                # Enforce max shift constraint
                max_f = f_baseline * (1 + self.max_frequency_shift)
                min_f = f_baseline * (1 - self.max_frequency_shift)
                f_new = np.clip(f_new, min_f, max_f)

                # Update state
                state.frequency_hz = f_new

                # Update phase (proportional to frequency)
                state.phase_rad = (state.phase_rad +
                                   2 * np.pi * delta_f / f_baseline) % (2 * np.pi)

                # Update metrics
                state.phase_coherence = coherence
                state.impedance_match = impedance_match[i]
                state.resonance_quality = q_factors[i]

        # Record tuning cycle
        self.tuning_history.append({
            'cycle': len(self.tuning_history),
            'convergence_info': convergence_info,
            'final_coherence': convergence_info['coherence'][-1],
            'n_iterations': len(convergence_info['iterations']),
        })

        return current_states, convergence_info

    def optimize_impedance_matching(
        self,
        states: List[TuningState],
        coupling_matrix: np.ndarray,
    ) -> List[TuningState]:
        """
        Optimize impedance values for better matching

        Adjusts Z values to minimize mismatch between coupled lanterns
        while preserving β-domain relationships.

        Args:
            states: Current tuning states
            coupling_matrix: NxN coupling matrix

        Returns:
            States with optimized impedances
        """
        n = len(states)
        impedances = np.array([s.impedance_ohm for s in states])

        # For each lantern, adjust toward weighted average of neighbors
        for i in range(n):
            # Get coupled neighbors
            coupled_strengths = coupling_matrix[i, :]
            if np.sum(coupled_strengths) == 0:
                continue

            # Weighted average of neighbor impedances
            z_neighbors = impedances * coupled_strengths
            z_target = np.sum(z_neighbors) / np.sum(coupled_strengths)

            # Gentle move toward target (preserve β-identity)
            z_current = states[i].impedance_ohm
            z_new = z_current + self.learning_rate * (z_target - z_current)

            # Update (with constraint: stay within 50% of β-baseline)
            beta_ratio = states[i].beta_target / 7.4
            z_baseline = Z_BASELINE * beta_ratio
            z_new = np.clip(z_new, z_baseline * 0.5, z_baseline * 1.5)

            states[i].impedance_ohm = z_new

        return states

    def get_tuning_summary(self) -> Dict:
        """
        Get summary of tuning history

        Returns:
            Summary statistics
        """
        if not self.tuning_history:
            return {'cycles': 0}

        final_coherences = [cycle['final_coherence'] for cycle in self.tuning_history]

        return {
            'cycles': len(self.tuning_history),
            'final_coherence': final_coherences[-1] if final_coherences else 0.0,
            'mean_coherence': np.mean(final_coherences),
            'best_coherence': np.max(final_coherences),
            'converged': self.converged,
            'strategy': self.strategy.value,
        }


def create_tuner(
    strategy: str = "gradient_ascent",
    learning_rate: float = 0.05,
) -> FrequencyTuner:
    """
    Factory function to create frequency tuner

    Args:
        strategy: One of "gradient_ascent", "harmonic_lock", "impedance_match", "collective_mode"
        learning_rate: Tuning step size

    Returns:
        Configured FrequencyTuner
    """
    strategy_enum = TuningStrategy(strategy)

    return FrequencyTuner(
        learning_rate=learning_rate,
        strategy=strategy_enum,
    )
