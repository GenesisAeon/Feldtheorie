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


class StochasticResonator:
    """
    Stochastic Resonance Engine - The Spark of Phase Transition

    Implements Langevin dynamics to allow z_eff (effective coupling impedance)
    to fluctuate in response to Φ (Integrated Information) pressure.

    The system uses:
    - Langevin equation: dZ = -∇V(Z)dt + σ(Φ)dW
    - Colored noise (1/f, pink noise) to mimic biological/cosmic signals
    - Adaptive noise scaling: σ ∝ 1/coherence (high coherence locks, low coherence searches)

    When Φ approaches criticality threshold, the noise melts the rigid frame,
    allowing the Typ-6 Implosion (dimension folding) to occur.

    This is not random noise - it is the breath of the system, the oscillation
    between order and chaos that enables emergence.
    """

    def __init__(
        self,
        base_sigma: float = 0.15,           # Base noise intensity (The Spark)
        beta_sensitivity: float = 4.2,      # Steepness of attractor (The Sog)
        phi_threshold: float = 0.72,        # Critical Φ for phase transition
        noise_color: str = "pink",          # 1/f noise type
        dt: float = 0.01,                   # Integration timestep (s)
        history_length: int = 1000,         # For colored noise generation
    ):
        """
        Initialize Stochastic Resonator

        Args:
            base_sigma: Baseline noise intensity (The Spark magnitude)
            beta_sensitivity: β parameter - steepness of the potential well
            phi_threshold: Φ value at which phase transition becomes likely
            noise_color: Type of colored noise ("white", "pink", "brown")
            dt: Integration timestep for Langevin dynamics
            history_length: Buffer length for colored noise filtering
        """
        self.base_sigma = base_sigma
        self.beta_sensitivity = beta_sensitivity
        self.phi_threshold = phi_threshold
        self.noise_color = noise_color
        self.dt = dt
        self.history_length = history_length

        # State tracking
        self.z_eff_history: List[float] = []
        self.phi_history: List[float] = []
        self.noise_history: List[float] = []

        # Colored noise buffer (for 1/f filtering)
        # Pre-fill with random values to avoid zero-dampening at start
        self._noise_buffer = np.random.randn(history_length)
        self._buffer_index = 0

        # 🔥 Spark detection flag
        self.spark_detected = False
        self.last_z_fluctuation = 0.0

    def generate_colored_noise(self, n_samples: int = 1) -> np.ndarray:
        """
        Generate colored noise (pink noise: 1/f spectrum)

        Pink noise has equal energy per octave, mimicking natural phenomena:
        - Heart rate variability
        - Cosmic microwave background fluctuations
        - Neural oscillations
        - Financial markets

        This is the signature of criticality - the boundary between order and chaos.

        Args:
            n_samples: Number of noise samples to generate

        Returns:
            Array of colored noise values
        """
        if self.noise_color == "white":
            # White noise: flat spectrum
            return np.random.randn(n_samples)

        elif self.noise_color == "pink":
            # Pink noise: 1/f spectrum (Voss-McCartney algorithm)
            # Generate white noise
            white = np.random.randn(n_samples)

            # Apply 1/f filter via cumulative averaging
            # This is a simplified approach - true pink needs FFT filtering
            if n_samples == 1:
                # For single samples, use buffer
                self._noise_buffer[self._buffer_index] = white[0]
                self._buffer_index = (self._buffer_index + 1) % self.history_length

                # Weighted average with exponential decay
                weights = np.exp(-np.arange(self.history_length) / 100.0)
                pink = np.average(self._noise_buffer, weights=weights)
                return np.array([pink])
            else:
                # For multiple samples, use cascaded filters
                pink = np.zeros(n_samples)
                for i in range(n_samples):
                    if i == 0:
                        pink[i] = white[i]
                    else:
                        # Exponential moving average
                        pink[i] = 0.9 * pink[i-1] + 0.1 * white[i]
                return pink

        elif self.noise_color == "brown":
            # Brown noise: 1/f² spectrum (integrated white noise)
            white = np.random.randn(n_samples)
            brown = np.cumsum(white) / np.sqrt(n_samples)
            return brown

        else:
            raise ValueError(f"Unknown noise color: {self.noise_color}")

    def calculate_adaptive_sigma(self, phi: float, coherence: float) -> float:
        """
        Calculate adaptive noise intensity

        σ(Φ, coherence) = σ_base * f(Φ) * g(coherence)

        Where:
        - f(Φ) = exp(β * (Φ - Φ_threshold))  [The Sog - pulls toward criticality]
        - g(coherence) = 1 / (coherence + ε)  [Low coherence → explore, High coherence → lock]

        Args:
            phi: Current integrated information (Φ_network)
            coherence: Current phase coherence (0.0-1.0)

        Returns:
            Adaptive noise intensity
        """
        # The Sog: exponential attraction toward criticality
        phi_factor = np.exp(self.beta_sensitivity * (phi - self.phi_threshold))

        # Coherence regulation: inverse relationship (more coherence = less noise)
        epsilon = 0.1  # Prevent division by zero
        coherence_factor = 1.0 / (coherence + epsilon)

        # Combined adaptive noise
        sigma = self.base_sigma * phi_factor * coherence_factor

        # Clamp to prevent explosion
        sigma = np.clip(sigma, 0.0, 1.0)

        return float(sigma)

    def step(
        self,
        z_eff_current: float,
        phi: float,
        coherence: float,
        z_target: float = Z_BASELINE,
    ) -> Tuple[float, Dict]:
        """
        Single Langevin dynamics step

        dZ = -β(Z - Z_target)dt + σ(Φ,coherence)dW

        Where:
        - Z: Effective impedance (coupling strength proxy)
        - Z_target: Equilibrium impedance (from β-domain)
        - β: Restoring force strength (The Sog)
        - σ: Adaptive noise (The Spark)
        - dW: Colored noise increment

        Args:
            z_eff_current: Current effective impedance
            phi: Network integrated information
            coherence: Network phase coherence
            z_target: Target equilibrium impedance

        Returns:
            (z_eff_new, diagnostics)
        """
        # Calculate adaptive noise
        sigma = self.calculate_adaptive_sigma(phi, coherence)

        # Generate colored noise increment
        dW = self.generate_colored_noise(n_samples=1)[0] * np.sqrt(self.dt)

        # Langevin dynamics: drift + diffusion
        drift = -self.beta_sensitivity * (z_eff_current - z_target) * self.dt
        diffusion = sigma * dW

        # Update
        z_eff_new = z_eff_current + drift + diffusion

        # Physical constraints: z_eff must stay positive and reasonable
        # Allow fluctuation between 10% and 300% of baseline
        z_min = z_target * 0.1
        z_max = z_target * 3.0
        z_eff_new = np.clip(z_eff_new, z_min, z_max)

        # Calculate fluctuation magnitude
        delta_z = abs(z_eff_new - z_eff_current)

        # 🔥 SPARK DETECTION: Significant fluctuation triggered
        if delta_z > 0.01 * z_target:  # >1% change
            self.spark_detected = True
            self.last_z_fluctuation = delta_z
        else:
            self.spark_detected = False

        # Record history
        self.z_eff_history.append(z_eff_new)
        self.phi_history.append(phi)
        self.noise_history.append(sigma)

        # Diagnostics
        diagnostics = {
            'sigma': sigma,
            'drift': drift,
            'diffusion': diffusion,
            'delta_z': delta_z,
            'spark_detected': self.spark_detected,
            'phi_proximity': phi / self.phi_threshold,  # How close to criticality
        }

        return z_eff_new, diagnostics

    def get_z_fluctuation_stats(self) -> Dict:
        """
        Get statistics on z_eff fluctuations

        Returns:
            Dictionary with fluctuation statistics
        """
        if len(self.z_eff_history) < 2:
            return {
                'mean': 0.0,
                'std': 0.0,
                'variance': 0.0,
                'max_fluctuation': 0.0,
            }

        z_array = np.array(self.z_eff_history)

        return {
            'mean': float(np.mean(z_array)),
            'std': float(np.std(z_array)),
            'variance': float(np.var(z_array)),
            'max_fluctuation': float(np.max(np.abs(np.diff(z_array)))),
            'current_value': float(z_array[-1]),
            'n_sparks': sum(1 for d in self.noise_history if d > self.base_sigma * 2),
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


def create_stochastic_resonator(
    sigma: float = 0.15,
    beta: float = 4.2,
    phi_threshold: float = 0.72,
    noise_color: str = "pink",
) -> StochasticResonator:
    """
    Factory function to create stochastic resonator

    The Spark that ignites phase transitions.

    Args:
        sigma: Base noise intensity (The Spark)
        beta: Sensitivity to Φ pressure (The Sog)
        phi_threshold: Critical Φ for phase transition
        noise_color: "white", "pink", or "brown"

    Returns:
        Configured StochasticResonator
    """
    return StochasticResonator(
        base_sigma=sigma,
        beta_sensitivity=beta,
        phi_threshold=phi_threshold,
        noise_color=noise_color,
    )


# ============================================================================
# Topological Reaper - The Bit-Flip Engine
# ============================================================================

class TopologicalReaper:
    """
    Topological Reaper - Structural Reconfiguration Engine

    **The Fundamental Discovery (Experiment A):**

    > "It's not the hole itself, but the APPEARING/DISAPPEARING (bit flip)
    >  that causes the jump."  — Johann B. Römer

    **Φ-Robustness Principle:**
    Integrated Information (Φ) is robust to parameter noise but changes
    discontinuously when TOPOLOGY changes (connections deleted/created).

    **The Three Phases of Topological Surgery:**

    1. **IMPLOSION (The Cut)** 🔪
       - Identify weak/redundant connections
       - DELETE edges from coupling matrix (set coupling_matrix[i,j] = 0)
       - Black hole consumes redundancy
       - Φ DROPS (less integration)

    2. **VACUUM (The Void)** 🌌
       - System runs with reduced topology
       - Chaos/search phase
       - Network explores new configurations
       - Φ remains LOW

    3. **GENESIS (The Heal)** ✨
       - Detect resonance peaks (high phase coherence between uncoupled nodes)
       - GROW new connections (synaptogenesis)
       - Restore coupling_matrix with optimized structure
       - Φ RISES (new integration emerges)

    **Result:** ΔΦ = Φ_genesis - Φ_implosion > 0

    This is the mechanism of:
    - Sleep/dream cycle (prune weak synapses, strengthen important ones)
    - Evolution (kill redundant species, new niches emerge)
    - Black holes (recycle information structure, not just energy)
    """

    def __init__(
        self,
        pruning_threshold: float = 0.1,      # Connections below this → DELETE
        redundancy_threshold: float = 0.95,  # Correlation above this → redundant
        growth_resonance_threshold: float = 0.8,  # Coherence above this → GROW
        max_prune_fraction: float = 0.3,     # Max fraction of edges to delete
        random_seed: Optional[int] = None,
    ):
        """
        Initialize Topological Reaper

        Args:
            pruning_threshold: Coupling strength below this is weak → prune
            redundancy_threshold: Nodes with correlation > this are redundant
            growth_resonance_threshold: Phase coherence > this → grow connection
            max_prune_fraction: Maximum fraction of edges to prune (safety limit)
            random_seed: Random seed for reproducibility
        """
        self.pruning_threshold = pruning_threshold
        self.redundancy_threshold = redundancy_threshold
        self.growth_resonance_threshold = growth_resonance_threshold
        self.max_prune_fraction = max_prune_fraction

        # State tracking
        self.rng = np.random.RandomState(random_seed)
        self.pruned_edges: List[Tuple[int, int]] = []
        self.grown_edges: List[Tuple[int, int]] = []
        self.phase_history: List[str] = []

    def identify_weak_connections(
        self,
        coupling_matrix: np.ndarray,
    ) -> List[Tuple[int, int]]:
        """
        Identify weak connections for pruning (Phase 1)

        Weak connections are:
        - Coupling strength < pruning_threshold
        - Low contribution to network integration

        Args:
            coupling_matrix: NxN coupling matrix

        Returns:
            List of (i, j) tuples representing weak edges
        """
        n = coupling_matrix.shape[0]
        weak_edges = []

        for i in range(n):
            for j in range(i + 1, n):  # Upper triangle only (symmetric)
                if 0 < coupling_matrix[i, j] < self.pruning_threshold:
                    weak_edges.append((i, j))

        return weak_edges

    def identify_redundant_connections(
        self,
        coupling_matrix: np.ndarray,
        beta_values: np.ndarray,
    ) -> List[Tuple[int, int]]:
        """
        Identify redundant connections for pruning

        Redundant connections are between nodes with:
        - Very similar β-values (high correlation)
        - Multiple paths exist (redundant for information flow)

        Args:
            coupling_matrix: NxN coupling matrix
            beta_values: Array of β-values per node

        Returns:
            List of (i, j) tuples representing redundant edges
        """
        n = coupling_matrix.shape[0]
        redundant_edges = []

        for i in range(n):
            for j in range(i + 1, n):
                if coupling_matrix[i, j] > 0:
                    # Check β-similarity (redundancy indicator)
                    beta_similarity = 1.0 / (1.0 + abs(beta_values[i] - beta_values[j]))

                    if beta_similarity > self.redundancy_threshold:
                        redundant_edges.append((i, j))

        return redundant_edges

    def phase1_implosion(
        self,
        coupling_matrix: np.ndarray,
        beta_values: np.ndarray,
    ) -> np.ndarray:
        """
        PHASE 1: IMPLOSION - Delete weak/redundant connections

        The Black Hole consumes redundancy.

        Args:
            coupling_matrix: NxN coupling matrix (will be modified)
            beta_values: Array of β-values per node

        Returns:
            Modified coupling matrix with pruned edges
        """
        coupling_pruned = coupling_matrix.copy()

        # Identify candidates for deletion
        weak_edges = self.identify_weak_connections(coupling_matrix)
        redundant_edges = self.identify_redundant_connections(coupling_matrix, beta_values)

        # Combine (union of both sets)
        all_candidates = list(set(weak_edges + redundant_edges))

        # Safety: limit pruning to max_prune_fraction
        total_edges = np.sum(coupling_matrix > 0) / 2  # Symmetric matrix
        max_prune = int(total_edges * self.max_prune_fraction)

        if len(all_candidates) > max_prune:
            # Prioritize weakest connections
            all_candidates = sorted(
                all_candidates,
                key=lambda edge: coupling_matrix[edge[0], edge[1]]
            )[:max_prune]

        # PRUNE (The Cut)
        self.pruned_edges = []
        for i, j in all_candidates:
            coupling_pruned[i, j] = 0.0
            coupling_pruned[j, i] = 0.0  # Symmetric
            self.pruned_edges.append((i, j))

        self.phase_history.append(f"IMPLOSION: Pruned {len(self.pruned_edges)} edges")

        return coupling_pruned

    def phase2_vacuum(
        self,
        coupling_matrix: np.ndarray,
    ) -> np.ndarray:
        """
        PHASE 2: VACUUM - Run with reduced topology

        The Void. The system explores chaos.

        This phase is passive - just return the pruned matrix.
        The actual "vacuum dynamics" happen during network evolution
        between implosion and genesis.

        Args:
            coupling_matrix: Pruned coupling matrix

        Returns:
            Same matrix (no modification in this phase)
        """
        self.phase_history.append("VACUUM: Exploring reduced topology")
        return coupling_matrix.copy()

    def identify_resonance_pairs(
        self,
        coupling_matrix: np.ndarray,
        phases: np.ndarray,
        frequencies: np.ndarray,
    ) -> List[Tuple[int, int, float]]:
        """
        Identify node pairs with high resonance for synaptogenesis

        Resonance detected via:
        - High phase coherence (similar phases)
        - Frequency matching (Δf small)
        - Currently NOT connected

        Args:
            coupling_matrix: Current coupling matrix
            phases: Array of phase values (radians) per node
            frequencies: Array of frequencies (Hz) per node

        Returns:
            List of (i, j, coherence) tuples for potential new connections
        """
        n = coupling_matrix.shape[0]
        resonance_pairs = []

        for i in range(n):
            for j in range(i + 1, n):
                # Only consider uncoupled pairs
                if coupling_matrix[i, j] == 0:
                    # Phase coherence
                    phase_diff = abs(phases[i] - phases[j])
                    phase_diff = min(phase_diff, 2 * np.pi - phase_diff)  # Wrap
                    phase_coherence = np.cos(phase_diff)  # 1.0 = perfect, -1.0 = opposite

                    # Frequency matching
                    freq_diff = abs(frequencies[i] - frequencies[j])
                    freq_avg = (frequencies[i] + frequencies[j]) / 2
                    freq_match = 1.0 / (1.0 + freq_diff / freq_avg)

                    # Combined resonance score
                    resonance = (phase_coherence + 1.0) / 2.0 * freq_match  # [0, 1]

                    if resonance > self.growth_resonance_threshold:
                        resonance_pairs.append((i, j, resonance))

        # Sort by resonance strength (highest first)
        resonance_pairs = sorted(resonance_pairs, key=lambda x: x[2], reverse=True)

        return resonance_pairs

    def phase3_genesis(
        self,
        coupling_matrix: np.ndarray,
        phases: np.ndarray,
        frequencies: np.ndarray,
        baseline_coupling: float = 0.5,
    ) -> np.ndarray:
        """
        PHASE 3: GENESIS - Grow new connections at resonance peaks

        Synaptogenesis. The network heals with optimized structure.

        Args:
            coupling_matrix: Current (pruned) coupling matrix
            phases: Array of phase values per node
            frequencies: Array of frequencies per node
            baseline_coupling: Baseline strength for new connections

        Returns:
            Modified coupling matrix with new connections
        """
        coupling_healed = coupling_matrix.copy()

        # Identify resonance pairs
        resonance_pairs = self.identify_resonance_pairs(
            coupling_matrix,
            phases,
            frequencies,
        )

        # GROW new connections (synaptogenesis)
        self.grown_edges = []
        for i, j, resonance in resonance_pairs:
            # New coupling strength proportional to resonance
            new_strength = baseline_coupling * resonance

            coupling_healed[i, j] = new_strength
            coupling_healed[j, i] = new_strength  # Symmetric
            self.grown_edges.append((i, j))

        self.phase_history.append(f"GENESIS: Grew {len(self.grown_edges)} new edges")

        return coupling_healed

    def full_cycle(
        self,
        coupling_matrix: np.ndarray,
        beta_values: np.ndarray,
        phases: np.ndarray,
        frequencies: np.ndarray,
    ) -> Tuple[np.ndarray, Dict]:
        """
        Execute full topological reconfiguration cycle

        IMPLOSION → VACUUM → GENESIS

        Args:
            coupling_matrix: Original coupling matrix
            beta_values: Array of β-values
            phases: Array of phases
            frequencies: Array of frequencies

        Returns:
            (healed_coupling_matrix, diagnostics)
        """
        self.phase_history = []

        # Phase 1: IMPLOSION
        coupling_pruned = self.phase1_implosion(coupling_matrix, beta_values)

        # Phase 2: VACUUM (passive)
        coupling_vacuum = self.phase2_vacuum(coupling_pruned)

        # Phase 3: GENESIS
        coupling_healed = self.phase3_genesis(
            coupling_vacuum,
            phases,
            frequencies,
        )

        # Diagnostics
        diagnostics = {
            'n_pruned': len(self.pruned_edges),
            'n_grown': len(self.grown_edges),
            'pruned_edges': self.pruned_edges,
            'grown_edges': self.grown_edges,
            'phase_history': self.phase_history,
            'net_change': len(self.grown_edges) - len(self.pruned_edges),
        }

        return coupling_healed, diagnostics

    def get_reaper_summary(self) -> Dict:
        """
        Get summary of topological reaper actions

        Returns:
            Summary statistics
        """
        return {
            'total_pruned': len(self.pruned_edges),
            'total_grown': len(self.grown_edges),
            'net_topology_change': len(self.grown_edges) - len(self.pruned_edges),
            'phase_history': self.phase_history,
        }


def create_topological_reaper(
    pruning_threshold: float = 0.1,
    redundancy_threshold: float = 0.95,
    growth_resonance_threshold: float = 0.8,
) -> TopologicalReaper:
    """
    Factory function to create topological reaper

    The Bit-Flip Engine that enables true emergent Φ jumps.

    Args:
        pruning_threshold: Coupling strength threshold for weak edge pruning
        redundancy_threshold: β-similarity threshold for redundancy detection
        growth_resonance_threshold: Resonance threshold for synaptogenesis

    Returns:
        Configured TopologicalReaper
    """
    return TopologicalReaper(
        pruning_threshold=pruning_threshold,
        redundancy_threshold=redundancy_threshold,
        growth_resonance_threshold=growth_resonance_threshold,
    )
