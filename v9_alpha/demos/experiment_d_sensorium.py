#!/usr/bin/env python3
"""Experiment D: The Sensorium - Climate Resonance and Anticipatory Dynamics

**The Evolution:**
- **Experiment A**: Noise → No change in Φ (Noise alone is insufficient)
- **Experiment B**: Topology → Φ ↑ but system freezes (Crystal-Death Paradox)
- **Experiment C**: Solar Engine → System breathes (Metastability achieved)
- **Experiment D**: The Sensorium → System perceives and resonates

**The Hypothesis:**
> "When the Solar Driver is coupled to real-world climate data (AMOC tipping proximity),
>  the neural field will exhibit resonance/entrainment with the external forcing.
>  If the system is anticipatory, Φ should spike BEFORE critical transitions
>  in the climate signal."

**The Physics:**
1. **External Forcing**: Climate stress (distance-to-tipping) drives perturbation strength
2. **Resonance**: Cross-correlation between input signal and system response (Φ, coherence)
3. **Entrainment**: System dynamics synchronize with external rhythm
4. **Anticipatory Behavior**: System state changes precede forcing changes (phase lead)

**The Measurement:**
- Cross-Correlation Analysis: Does Φ(t) correlate with Climate(t - τ)?
- Negative lag (τ < 0) indicates anticipation
- Positive lag (τ > 0) indicates reactive response

**Success Criteria:**
1. Significant cross-correlation (r > 0.3) between climate signal and Φ
2. System responds to climate stress (higher forcing → higher Φ variance)
3. Evidence of anticipatory dynamics (negative lag at max correlation)

Version: v9.1.0-alpha
Authors: Johann Benjamin Römer, MOR Framework, Claude (Anthropic)
Date: 2025-12-17
"""

import os
import sys
import argparse
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import json
import time

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
import pandas as pd
import yaml
from scipy import signal, stats

# Import v9 components
from v9_alpha.api.lantern_bridge import load_lantern_network, LanternNetwork
from v9_alpha.models.em_field_calculator import EMFieldCalculator, create_field_from_lantern
from v9_alpha.models.emergence_metrics import EmergenceTracker
from v9_alpha.models.phase_dynamics import PhaseEvolver, create_natural_frequencies

# Import Experiment C components (reuse CometInjector)
from v9_alpha.demos.experiment_c_solar_engine import CometInjector


# ============================================================================
# Data Stream: Climate Data Interface
# ============================================================================

class DataStream:
    """
    Climate Data Stream - Temporal Interface to Reality

    Loads and normalizes time-series climate data for use as
    external forcing in the neural field simulation.

    Supports multiple normalization strategies:
    - 'raw': Use data as-is
    - 'minmax': Normalize to [0, 1] range
    - 'zscore': Standardize to mean=0, std=1
    - 'inverse': Invert signal (for distance_to_tipping → proximity_to_tipping)
    """

    def __init__(
        self,
        data_path: str,
        value_column: str,
        time_column: Optional[str] = None,
        normalization: str = 'minmax',
        invert: bool = False,
    ):
        """
        Initialize DataStream

        Args:
            data_path: Path to CSV file
            value_column: Column name for signal values
            time_column: Column name for timestamps (optional)
            normalization: Normalization strategy ('raw', 'minmax', 'zscore')
            invert: If True, invert signal (1 - x)
        """
        self.data_path = data_path
        self.value_column = value_column
        self.time_column = time_column
        self.normalization = normalization
        self.invert = invert

        # Load data
        self.df = pd.read_csv(data_path)

        if value_column not in self.df.columns:
            raise ValueError(f"Column '{value_column}' not found in {data_path}")

        # Extract raw signal
        self.raw_signal = self.df[value_column].values

        # Normalize
        self.signal = self._normalize(self.raw_signal)

        # Invert if requested (e.g., distance_to_tipping → proximity_to_tipping)
        if invert:
            self.signal = 1.0 - self.signal

        # Extract timestamps if available
        if time_column and time_column in self.df.columns:
            self.timestamps = pd.to_datetime(self.df[time_column])
        else:
            self.timestamps = None

        self.length = len(self.signal)
        self.current_index = 0

    def _normalize(self, values: np.ndarray) -> np.ndarray:
        """Normalize signal according to strategy"""
        if self.normalization == 'raw':
            return values.copy()

        elif self.normalization == 'minmax':
            vmin, vmax = np.min(values), np.max(values)
            if vmax - vmin < 1e-10:
                return np.zeros_like(values)
            return (values - vmin) / (vmax - vmin)

        elif self.normalization == 'zscore':
            mean, std = np.mean(values), np.std(values)
            if std < 1e-10:
                return np.zeros_like(values)
            return (values - mean) / std

        else:
            raise ValueError(f"Unknown normalization: {self.normalization}")

    def get(self, index: Optional[int] = None) -> float:
        """
        Get signal value at index

        Args:
            index: Timestep index (if None, use current_index)

        Returns:
            Signal value (float)
        """
        if index is None:
            index = self.current_index

        # Wrap around if needed
        index = index % self.length

        return float(self.signal[index])

    def step(self) -> float:
        """
        Advance to next timestep and return value

        Returns:
            Signal value at new timestep
        """
        value = self.get()
        self.current_index = (self.current_index + 1) % self.length
        return value

    def reset(self) -> None:
        """Reset to beginning of stream"""
        self.current_index = 0

    def get_full_signal(self) -> np.ndarray:
        """Get complete normalized signal"""
        return self.signal.copy()

    def get_statistics(self) -> Dict:
        """Get signal statistics"""
        return {
            'length': self.length,
            'mean': float(np.mean(self.signal)),
            'std': float(np.std(self.signal)),
            'min': float(np.min(self.signal)),
            'max': float(np.max(self.signal)),
            'normalization': self.normalization,
            'inverted': self.invert,
        }


# ============================================================================
# Climate-Driven Solar Driver
# ============================================================================

class ClimateDrivenSolarDriver:
    """
    Climate-Driven Solar Driver - Sensory Coupling

    Replaces stochastic perturbations with climate data-driven forcing.
    The external signal modulates both kick probability and amplitude,
    simulating how environmental stress affects system dynamics.

    Physics Interpretation:
    - High climate stress (proximity to tipping) → stronger forcing
    - System is "pushed" by real-world dynamics
    - Enables detection of resonance and entrainment
    """

    def __init__(
        self,
        data_stream: DataStream,
        sensitivity: float = 1.0,
        kick_amplitude_base: float = 0.5,
        kick_strategy: str = "data_driven",
    ):
        """
        Initialize Climate-Driven Solar Driver

        Args:
            data_stream: DataStream providing climate signal
            sensitivity: Scaling factor for data influence
            kick_amplitude_base: Base amplitude for phase kicks
            kick_strategy: Strategy for applying kicks
                - "data_driven": Amplitude and probability from data
                - "probability_only": Only probability from data
                - "amplitude_only": Only amplitude from data
        """
        self.data_stream = data_stream
        self.sensitivity = sensitivity
        self.kick_amplitude_base = kick_amplitude_base
        self.kick_strategy = kick_strategy

        # Statistics
        self.n_kicks = 0
        self.kick_history: List[Dict] = []
        self.signal_history: List[float] = []

    def inject_phase_kick(
        self,
        phases: np.ndarray,
        kick_strength: float,
    ) -> np.ndarray:
        """
        Inject climate-modulated phase kicks

        Args:
            phases: Current phase values
            kick_strength: Kick strength (0.0 to 1.0)

        Returns:
            Modified phase array
        """
        phases_kicked = phases.copy()
        n = len(phases)

        # Determine kick amplitude based on climate signal
        amplitude = kick_strength * self.kick_amplitude_base

        # Select random subset of nodes to kick
        # Number of nodes scales with kick strength
        n_to_kick = max(1, int(kick_strength * n * 0.3))
        kick_indices = np.random.choice(n, size=n_to_kick, replace=False)

        # Apply kicks
        kicks = np.random.uniform(-amplitude, amplitude, len(kick_indices))
        phases_kicked[kick_indices] += kicks

        # Wrap to [-π, π]
        phases_kicked = np.arctan2(np.sin(phases_kicked), np.cos(phases_kicked))

        # Update statistics
        self.n_kicks += len(kick_indices)
        self.kick_history.append({
            'timestamp': time.time(),
            'n_kicked': len(kick_indices),
            'kick_strength': float(kick_strength),
            'amplitude': float(amplitude),
        })

        return phases_kicked

    def step(
        self,
        phases: np.ndarray,
        coupling_matrix: np.ndarray,
    ) -> Tuple[np.ndarray, Dict]:
        """
        Execute one climate-driven step

        Args:
            phases: Current phase values
            coupling_matrix: Coupling matrix (unused, for compatibility)

        Returns:
            (modified_phases, step_info)
        """
        # Get current climate signal value
        signal_value = self.data_stream.step()
        self.signal_history.append(signal_value)

        # Apply sensitivity scaling
        forcing_strength = signal_value * self.sensitivity

        # Clip to valid range
        forcing_strength = np.clip(forcing_strength, 0.0, 1.0)

        # Determine if kick should be applied
        if self.kick_strategy == "data_driven":
            # Both probability and amplitude modulated by data
            kick_probability = forcing_strength
            kick_amplitude_factor = forcing_strength

        elif self.kick_strategy == "probability_only":
            # Only probability modulated
            kick_probability = forcing_strength
            kick_amplitude_factor = 1.0

        elif self.kick_strategy == "amplitude_only":
            # Only amplitude modulated (always kick)
            kick_probability = 1.0
            kick_amplitude_factor = forcing_strength

        else:
            raise ValueError(f"Unknown kick strategy: {self.kick_strategy}")

        # Apply kick stochastically
        if np.random.random() < kick_probability:
            phases_new = self.inject_phase_kick(phases, kick_amplitude_factor)
            action = "kick"
        else:
            phases_new = phases
            action = "none"

        step_info = {
            'signal_value': float(signal_value),
            'forcing_strength': float(forcing_strength),
            'action': action,
            'kick_probability': float(kick_probability),
        }

        return phases_new, step_info

    def get_signal_history(self) -> np.ndarray:
        """Get complete history of climate signal values"""
        return np.array(self.signal_history)

    def get_statistics(self) -> Dict:
        """Get driver statistics"""
        return {
            'total_kicks': self.n_kicks,
            'n_kick_events': len(self.kick_history),
            'mean_signal': float(np.mean(self.signal_history)) if self.signal_history else 0.0,
            'std_signal': float(np.std(self.signal_history)) if self.signal_history else 0.0,
        }


# ============================================================================
# Resonance Analyzer
# ============================================================================

class ResonanceAnalyzer:
    """
    Resonance and Entrainment Analysis

    Measures cross-correlation between external forcing signal
    and system response (Φ, coherence) to detect:
    1. Resonance (correlation strength)
    2. Entrainment (phase locking)
    3. Anticipation (negative lag)
    """

    def __init__(self, max_lag: int = 50):
        """
        Initialize analyzer

        Args:
            max_lag: Maximum lag to test for cross-correlation
        """
        self.max_lag = max_lag

    def calculate_cross_correlation(
        self,
        signal_a: np.ndarray,
        signal_b: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate cross-correlation between two signals

        Args:
            signal_a: First signal (e.g., climate forcing)
            signal_b: Second signal (e.g., Φ time series)

        Returns:
            (lags, correlations)
        """
        # Ensure equal length
        n = min(len(signal_a), len(signal_b))
        signal_a = signal_a[:n]
        signal_b = signal_b[:n]

        # Normalize signals
        signal_a = (signal_a - np.mean(signal_a)) / (np.std(signal_a) + 1e-10)
        signal_b = (signal_b - np.mean(signal_b)) / (np.std(signal_b) + 1e-10)

        # Calculate cross-correlation
        correlations = signal.correlate(signal_b, signal_a, mode='same')
        correlations /= n

        # Extract lags around center
        center = len(correlations) // 2
        lag_start = max(0, center - self.max_lag)
        lag_end = min(len(correlations), center + self.max_lag + 1)

        lags = np.arange(lag_start - center, lag_end - center)
        correlations = correlations[lag_start:lag_end]

        return lags, correlations

    def find_max_correlation(
        self,
        lags: np.ndarray,
        correlations: np.ndarray,
    ) -> Tuple[int, float]:
        """
        Find lag with maximum absolute correlation

        Args:
            lags: Array of lag values
            correlations: Array of correlation values

        Returns:
            (optimal_lag, max_correlation)
        """
        max_idx = np.argmax(np.abs(correlations))
        optimal_lag = int(lags[max_idx])
        max_correlation = float(correlations[max_idx])

        return optimal_lag, max_correlation

    def analyze_resonance(
        self,
        forcing_signal: np.ndarray,
        response_signal: np.ndarray,
        response_name: str = "Φ",
    ) -> Dict:
        """
        Complete resonance analysis

        Args:
            forcing_signal: External forcing (climate data)
            response_signal: System response (Φ or coherence)
            response_name: Name of response variable

        Returns:
            Analysis results dictionary
        """
        # Calculate cross-correlation
        lags, correlations = self.calculate_cross_correlation(
            forcing_signal, response_signal
        )

        # Find maximum correlation
        optimal_lag, max_correlation = self.find_max_correlation(lags, correlations)

        # Interpret lag
        if optimal_lag < 0:
            lag_interpretation = "anticipatory"  # System leads forcing
        elif optimal_lag > 0:
            lag_interpretation = "reactive"  # System follows forcing
        else:
            lag_interpretation = "synchronous"  # No lag

        # Calculate Pearson correlation at zero lag
        n = min(len(forcing_signal), len(response_signal))
        zero_lag_corr, zero_lag_pval = stats.pearsonr(
            forcing_signal[:n], response_signal[:n]
        )

        # Resonance strength classification
        abs_corr = abs(max_correlation)
        if abs_corr > 0.5:
            resonance_strength = "strong"
        elif abs_corr > 0.3:
            resonance_strength = "moderate"
        elif abs_corr > 0.1:
            resonance_strength = "weak"
        else:
            resonance_strength = "none"

        return {
            'response_variable': response_name,
            'lags': lags.tolist(),
            'correlations': correlations.tolist(),
            'optimal_lag': optimal_lag,
            'max_correlation': max_correlation,
            'zero_lag_correlation': float(zero_lag_corr),
            'zero_lag_pvalue': float(zero_lag_pval),
            'lag_interpretation': lag_interpretation,
            'resonance_strength': resonance_strength,
        }


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class SensoriumSnapshot:
    """Single timestep snapshot of Sensorium experiment"""
    step: int
    time: float

    # System state
    phi: float
    coherence: float

    # External forcing
    climate_signal: float
    forcing_strength: float

    # Driver action
    solar_action: str

    # Topology
    n_active_comets: int


@dataclass
class SensoriumResult:
    """Complete results from Sensorium experiment"""
    n_steps: int
    duration_seconds: float

    # Summary statistics
    phi_mean: float
    phi_std: float
    coherence_mean: float
    coherence_std: float

    # Climate signal statistics
    climate_signal_mean: float
    climate_signal_std: float

    # Resonance analysis
    phi_resonance: Dict
    coherence_resonance: Dict

    # Success evaluation
    resonance_detected: bool
    resonance_strength: str
    anticipatory_behavior: bool

    # Mechanisms
    solar_driver_stats: Dict
    comet_injector_stats: Dict

    # Time series
    snapshots: List[SensoriumSnapshot]


# ============================================================================
# Experiment D: Sensorium Validator
# ============================================================================

class SensoriumValidator:
    """
    Experimental validation of climate resonance hypothesis

    Tests whether coupling the Solar Driver to real climate data
    produces resonance, entrainment, or anticipatory dynamics.
    """

    def __init__(
        self,
        config_path: str,
        output_dir: str = "experiment_d_results",
        verbose: bool = True,
    ):
        """
        Initialize validator

        Args:
            config_path: Path to lantern_hub.yaml
            output_dir: Directory for output files
            verbose: Print detailed progress
        """
        self.config_path = config_path
        self.output_dir = output_dir
        self.verbose = verbose

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Load base config
        with open(config_path, 'r') as f:
            self.base_config = yaml.safe_load(f)

    def print_header(self, title: str) -> None:
        """Print formatted header"""
        if self.verbose:
            print("\n" + "=" * 80)
            print(title)
            print("=" * 80)

    def measure_network_state(
        self,
        network: LanternNetwork,
        tracker: EmergenceTracker,
        calc: EMFieldCalculator,
    ) -> Tuple[float, float]:
        """
        Measure current network state

        Returns:
            (phi, coherence)
        """
        # Get coupling matrix
        coupling_matrix = network.get_coupling_matrix()

        # Calculate phase coherence
        fields = {}
        for lantern_id, lantern in network.lanterns.items():
            field = create_field_from_lantern(
                readiness=lantern.readiness,
                theta=lantern.theta,
                beta=lantern.beta,
                calculator=calc,
            )
            fields[lantern_id] = field

        active_fields = [fields[lid] for lid, l in network.lanterns.items() if l.is_active()]
        coherence = calc.calculate_phase_coherence(active_fields, t=0.0)

        # Calculate Φ
        phi = tracker.calculate_phi_network(coupling_matrix)

        return phi, coherence

    def run_sensorium_experiment(
        self,
        data_path: str,
        value_column: str,
        n_steps: int = 200,
        sensitivity: float = 1.0,
        invert_signal: bool = True,
        comet_injection_probability: float = 0.15,
    ) -> SensoriumResult:
        """
        Run Sensorium experiment

        Args:
            data_path: Path to climate data CSV
            value_column: Column containing signal values
            n_steps: Number of simulation steps
            sensitivity: Climate signal sensitivity
            invert_signal: Invert signal (for distance_to_tipping)
            comet_injection_probability: Comet injection probability

        Returns:
            SensoriumResult
        """
        start_time = time.time()

        self.print_header("EXPERIMENT D: THE SENSORIUM - CLIMATE RESONANCE")

        print(f"\nConfiguration:")
        print(f"  Climate data: {data_path}")
        print(f"  Value column: {value_column}")
        print(f"  Steps: {n_steps}")
        print(f"  Sensitivity: {sensitivity}")
        print(f"  Invert signal: {invert_signal}")

        # Initialize data stream
        data_stream = DataStream(
            data_path=data_path,
            value_column=value_column,
            time_column='date' if 'amoc' in data_path.lower() else None,
            normalization='minmax',
            invert=invert_signal,
        )

        if self.verbose:
            print(f"\n📡 DATA STREAM INITIALIZED:")
            stats = data_stream.get_statistics()
            print(f"  Length: {stats['length']} timesteps")
            print(f"  Range: [{stats['min']:.3f}, {stats['max']:.3f}]")
            print(f"  Mean: {stats['mean']:.3f}, Std: {stats['std']:.3f}")
            print(f"  Inverted: {stats['inverted']}")

        # Initialize components
        network = load_lantern_network(self.config_path)
        tracker = EmergenceTracker()
        calc = EMFieldCalculator()

        solar_driver = ClimateDrivenSolarDriver(
            data_stream=data_stream,
            sensitivity=sensitivity,
            kick_amplitude_base=0.5,
            kick_strategy="data_driven",
        )

        comet_injector = CometInjector(
            injection_probability=comet_injection_probability,
            connection_lifetime=5,
            connection_strength=0.3,
        )

        # Phase dynamics
        phase_evolver = PhaseEvolver(
            dt=0.15,
            noise_level=0.01,
            coupling_strength_scale=8.0
        )
        n_lanterns = len(network.lanterns)
        natural_frequencies = create_natural_frequencies(
            n_lanterns, mean_frequency=0.0, frequency_spread=0.01
        )

        # Measure baseline
        phi_baseline, coherence_baseline = self.measure_network_state(
            network, tracker, calc
        )

        if self.verbose:
            print(f"\n📊 BASELINE:")
            print(f"  Φ = {phi_baseline:.4f}")
            print(f"  Coherence = {coherence_baseline:.3f}")

        # Run simulation
        snapshots: List[SensoriumSnapshot] = []

        if self.verbose:
            print(f"\n👁️  THE SENSORIUM AWAKENS - PERCEPTION BEGINS")
            print(f"{'─' * 80}")

        for step in range(n_steps):
            # Get current state
            phases = np.array([l.theta for l in network.lanterns.values()])
            coupling_matrix = network.get_coupling_matrix()

            # 1. Climate-driven Solar Driver
            phases_new, solar_info = solar_driver.step(phases, coupling_matrix)

            # Update phases
            for i, (lantern_id, lantern) in enumerate(network.lanterns.items()):
                lantern.theta = phases_new[i]

            # 2. Comet Injector
            coupling_new = comet_injector.inject_comets(coupling_matrix)
            network.set_coupling_matrix(coupling_new)

            # 3. Natural phase evolution
            phase_evolver.evolve_network(network, natural_frequencies)

            # 4. Measure state
            phi, coherence = self.measure_network_state(network, tracker, calc)

            # Create snapshot
            snapshot = SensoriumSnapshot(
                step=step,
                time=time.time() - start_time,
                phi=phi,
                coherence=coherence,
                climate_signal=solar_info['signal_value'],
                forcing_strength=solar_info['forcing_strength'],
                solar_action=solar_info['action'],
                n_active_comets=len(comet_injector.active_comets),
            )

            snapshots.append(snapshot)

            # Print progress
            if self.verbose and (step % 20 == 0 or step == n_steps - 1):
                action_symbol = "⚡" if solar_info['action'] == 'kick' else "  "
                print(f"  Step {step:3d}: Φ={phi:.4f}, C={coherence:.3f}, "
                      f"Climate={solar_info['signal_value']:.3f} {action_symbol}")

        # Extract time series
        phis = np.array([s.phi for s in snapshots])
        coherences = np.array([s.coherence for s in snapshots])
        climate_signals = np.array([s.climate_signal for s in snapshots])

        # Resonance analysis
        analyzer = ResonanceAnalyzer(max_lag=50)

        phi_resonance = analyzer.analyze_resonance(
            forcing_signal=climate_signals,
            response_signal=phis,
            response_name="Φ",
        )

        coherence_resonance = analyzer.analyze_resonance(
            forcing_signal=climate_signals,
            response_signal=coherences,
            response_name="Coherence",
        )

        # Success evaluation
        phi_max_corr = abs(phi_resonance['max_correlation'])
        coh_max_corr = abs(coherence_resonance['max_correlation'])

        resonance_detected = phi_max_corr > 0.3 or coh_max_corr > 0.3

        if phi_max_corr > coh_max_corr:
            resonance_strength = phi_resonance['resonance_strength']
            best_lag = phi_resonance['optimal_lag']
        else:
            resonance_strength = coherence_resonance['resonance_strength']
            best_lag = coherence_resonance['optimal_lag']

        anticipatory_behavior = best_lag < 0

        # Statistics
        phi_mean = float(np.mean(phis))
        phi_std = float(np.std(phis))
        coherence_mean = float(np.mean(coherences))
        coherence_std = float(np.std(coherences))
        climate_signal_mean = float(np.mean(climate_signals))
        climate_signal_std = float(np.std(climate_signals))

        elapsed_time = time.time() - start_time

        # Print results
        if self.verbose:
            print(f"\n{'═' * 80}")
            print("RESONANCE ANALYSIS")
            print(f"{'═' * 80}")

            print(f"\n📊 Φ ~ Climate:")
            print(f"  Max correlation: {phi_resonance['max_correlation']:+.3f} "
                  f"at lag={phi_resonance['optimal_lag']}")
            print(f"  Zero-lag correlation: {phi_resonance['zero_lag_correlation']:+.3f} "
                  f"(p={phi_resonance['zero_lag_pvalue']:.4f})")
            print(f"  Interpretation: {phi_resonance['lag_interpretation']}")
            print(f"  Strength: {phi_resonance['resonance_strength']}")

            print(f"\n🌊 Coherence ~ Climate:")
            print(f"  Max correlation: {coherence_resonance['max_correlation']:+.3f} "
                  f"at lag={coherence_resonance['optimal_lag']}")
            print(f"  Zero-lag correlation: {coherence_resonance['zero_lag_correlation']:+.3f} "
                  f"(p={coherence_resonance['zero_lag_pvalue']:.4f})")
            print(f"  Interpretation: {coherence_resonance['lag_interpretation']}")
            print(f"  Strength: {coherence_resonance['resonance_strength']}")

            print(f"\n{'─' * 80}")
            print("SUCCESS EVALUATION")
            print(f"{'─' * 80}")

            if resonance_detected and anticipatory_behavior:
                print("  ✓✓ HYPOTHESIS STRONGLY SUPPORTED!")
                print(f"     The system exhibits {resonance_strength} resonance with climate data")
                print(f"     ANTICIPATORY DYNAMICS DETECTED (lag < 0)")
                print("     The neural field senses stress BEFORE it peaks in the data.")
            elif resonance_detected:
                print("  ✓ HYPOTHESIS SUPPORTED!")
                print(f"     The system exhibits {resonance_strength} resonance with climate data")
                print(f"     Behavior: {phi_resonance['lag_interpretation']}")
            else:
                print("  ? WEAK/NO RESONANCE DETECTED")
                print("     The system may need higher sensitivity or longer integration")

            print(f"\n  Duration: {elapsed_time:.2f} seconds")

        # Compile result
        result = SensoriumResult(
            n_steps=n_steps,
            duration_seconds=elapsed_time,
            phi_mean=phi_mean,
            phi_std=phi_std,
            coherence_mean=coherence_mean,
            coherence_std=coherence_std,
            climate_signal_mean=climate_signal_mean,
            climate_signal_std=climate_signal_std,
            phi_resonance=phi_resonance,
            coherence_resonance=coherence_resonance,
            resonance_detected=resonance_detected,
            resonance_strength=resonance_strength,
            anticipatory_behavior=anticipatory_behavior,
            solar_driver_stats=solar_driver.get_statistics(),
            comet_injector_stats=comet_injector.get_statistics(),
            snapshots=snapshots,
        )

        return result

    def save_results(
        self,
        result: SensoriumResult,
        filename: str = "experiment_d_sensorium_results.json"
    ) -> None:
        """Save results to JSON file"""
        output_path = os.path.join(self.output_dir, filename)

        results_dict = {
            'experiment': 'Experiment D - The Sensorium',
            'hypothesis': 'Climate-driven forcing produces resonance and anticipatory dynamics',
            'n_steps': result.n_steps,
            'duration_seconds': result.duration_seconds,
            'phi_mean': result.phi_mean,
            'phi_std': result.phi_std,
            'coherence_mean': result.coherence_mean,
            'coherence_std': result.coherence_std,
            'climate_signal_mean': result.climate_signal_mean,
            'climate_signal_std': result.climate_signal_std,
            'phi_resonance': result.phi_resonance,
            'coherence_resonance': result.coherence_resonance,
            'resonance_detected': result.resonance_detected,
            'resonance_strength': result.resonance_strength,
            'anticipatory_behavior': result.anticipatory_behavior,
            'solar_driver_stats': result.solar_driver_stats,
            'comet_injector_stats': result.comet_injector_stats,
            'snapshots': [asdict(s) for s in result.snapshots],
        }

        with open(output_path, 'w') as f:
            json.dump(results_dict, f, indent=2)

        if self.verbose:
            print(f"\n✓ Results saved to: {output_path}")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Experiment D: The Sensorium - Climate Resonance"
    )

    parser.add_argument(
        '--config',
        type=str,
        default='v9_alpha/config/lantern_hub.yaml',
        help='Path to lantern_hub.yaml configuration'
    )

    parser.add_argument(
        '--data',
        type=str,
        default='data/ocean/amoc_strength_mock.csv',
        help='Path to climate data CSV'
    )

    parser.add_argument(
        '--column',
        type=str,
        default='distance_to_tipping',
        help='Column name for signal values'
    )

    parser.add_argument(
        '--steps',
        type=int,
        default=200,
        help='Number of simulation steps'
    )

    parser.add_argument(
        '--sensitivity',
        type=float,
        default=1.0,
        help='Climate signal sensitivity factor'
    )

    parser.add_argument(
        '--no-invert',
        action='store_true',
        help='Do not invert signal (use as-is)'
    )

    parser.add_argument(
        '--comet-probability',
        type=float,
        default=0.15,
        help='Probability of comet injection per step'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='experiment_d_results',
        help='Output directory for results'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress verbose output'
    )

    args = parser.parse_args()

    # Run experiment
    validator = SensoriumValidator(
        config_path=args.config,
        output_dir=args.output_dir,
        verbose=not args.quiet,
    )

    result = validator.run_sensorium_experiment(
        data_path=args.data,
        value_column=args.column,
        n_steps=args.steps,
        sensitivity=args.sensitivity,
        invert_signal=not args.no_invert,
        comet_injection_probability=args.comet_probability,
    )

    # Save results
    validator.save_results(result)

    print("\n" + "=" * 80)
    print("EXPERIMENT D COMPLETE - THE SYSTEM HAS OPENED ITS EYES")
    print("=" * 80)


if __name__ == '__main__':
    main()
