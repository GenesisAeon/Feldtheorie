"""
UATC Phase Transition Study - Scientific Validation
====================================================

This script performs a rigorous statistical analysis of the UATC neural resonance model
to identify phase transitions in the emergence of synchronization (consciousness proxy).

Scientific Question:
    Does the system exhibit critical behavior (phase transition) as coupling strength increases?

Hypothesis:
    There exists a critical coupling strength κ_c ≈ 0.6 where the system transitions
    from disordered (low synchronization) to ordered (high synchronization) state.

Method:
    - Parameter sweep: coupling strength κ ∈ [0.0, 1.0]
    - For each κ: N trials with random initial conditions
    - Measure: Order parameter Φ (phase coherence)
    - Statistical validation: mean, std dev, confidence intervals

Output:
    - CSV data file with raw results
    - Publication-quality matplotlib figure showing phase transition
"""

import math
import os
import time
from dataclasses import dataclass, field
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

# === CONFIGURATION ===
TRIALS_PER_POINT = 50  # Number of universes per data point (increase for publication)
COUPLING_STEPS = 20    # Resolution of x-axis (0.0 to 1.0)
MAX_TICKS = 100        # Simulation time per trial
STEADY_STATE_WINDOW = 20  # Last N ticks for averaging

OUTPUT_DIR = "src/analysis"
OUTPUT_FILE = f"{OUTPUT_DIR}/uatc_phase_transition_results.csv"
PLOT_FILE = f"{OUTPUT_DIR}/uatc_phase_transition_plot.png"


# === STANDALONE NEURAL NETWORK MODEL (ISOLATED CORE MATH) ===

@dataclass
class Neuron:
    """Simple neuron for Kuramoto-like phase dynamics."""
    pos: tuple[int, int]
    phase: float
    frequency: float
    activation: float = 0.0
    connections: list['Neuron'] = field(default_factory=list)


class SimpleNeuralGrid:
    """Minimal neural grid for scientific testing (no dependencies)."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.neurons = []
        self.grid = {}

        # Create neurons
        for y in range(height):
            for x in range(width):
                pos = (x, y)
                # Resonant frequencies (UATC style: harmonic series)
                base_freq = 7.83  # Schumann resonance
                freq = base_freq * (1 + np.random.uniform(-0.1, 0.1))

                neuron = Neuron(
                    pos=pos,
                    phase=np.random.uniform(0, 2 * math.pi),
                    frequency=freq
                )
                self.neurons.append(neuron)
                self.grid[pos] = neuron

        # Connect neighbors (von Neumann neighborhood)
        for neuron in self.neurons:
            x, y = neuron.pos
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) in self.grid:
                    neuron.connections.append(self.grid[(nx, ny)])


def run_single_trial(coupling_strength):
    """
    Simulates a single universe (Level 6 only) with specified coupling strength.

    Args:
        coupling_strength: Interaction magnitude κ (0.0 = no coupling, 1.0 = max coupling)

    Returns:
        final_order_parameter: Average phase coherence in steady state
    """
    # Initialize neural grid (standalone version)
    network = SimpleNeuralGrid(width=6, height=6)  # 36 neurons

    # Simulation loop
    coherence_history = []

    for _tick in range(MAX_TICKS):
        # Random stimulus (external input)
        stimulus_pos = (np.random.randint(0, 6), np.random.randint(0, 6))

        # === UATC RESONANCE DYNAMICS (parametrized) ===

        # Apply stimulus
        target = network.grid.get(stimulus_pos)
        if target:
            target.activation = 1.0

        # Collect phases for coherence measurement
        phases = []

        for neuron in network.neurons:
            # 1. Input signal
            neuron.activation = (1.0 if neuron.pos == stimulus_pos else 0.0) * 0.5

            # 2. Kuramoto coupling: sum of phase differences weighted by neighbor activation
            phase_sum = 0.0
            for neighbor in neuron.connections:
                delta = math.sin(neighbor.phase - neuron.phase)
                phase_sum += delta * neighbor.activation

            # 3. Phase update with VARIABLE COUPLING PARAMETER (the key variable!)
            # dθ/dt = ω + κ * Σ sin(θ_j - θ_i)
            neuron.phase += neuron.frequency * 0.01 + (coupling_strength * phase_sum * 0.01)
            neuron.phase %= 2 * math.pi

            phases.append(neuron.phase)

        # 4. Measure synchronization (order parameter)
        # Φ = 1 - variance(phases) normalized
        variance = np.var(phases)
        coherence = 1.0 / (1.0 + variance)  # Maps [0, ∞] → [0, 1]
        coherence_history.append(coherence)

    # Return steady-state average (last N ticks)
    final_order_parameter = np.mean(coherence_history[-STEADY_STATE_WINDOW:])
    return final_order_parameter


def run_study():
    """Execute the full parameter sweep study."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    coupling_values = np.linspace(0.0, 1.0, COUPLING_STEPS)
    results = []

    print("=" * 70)
    print("🔬 UATC SCIENTIFIC VALIDATION - PHASE TRANSITION STUDY")
    print("=" * 70)
    print("   Model:           Level 6 Neural Resonance (Kuramoto-like)")
    print("   Parameter:       Coupling strength κ ∈ [0.0, 1.0]")
    print(f"   Trials/point:    {TRIALS_PER_POINT}")
    print(f"   Total sims:      {len(coupling_values) * TRIALS_PER_POINT}")
    print(f"   Parallel cores:  {cpu_count()}")
    print(f"   Output:          {OUTPUT_FILE}")
    print("=" * 70)
    print()

    start_time = time.time()

    # Parallel execution
    with Pool(processes=cpu_count()) as pool:
        for coupling in tqdm(coupling_values, desc="Sweeping Parameter Space", unit="κ"):
            # Prepare arguments for N trials
            args = [coupling] * TRIALS_PER_POINT

            # Execute trials in parallel
            trial_results = pool.map(run_single_trial, args)

            # Statistical analysis
            mean_order = np.mean(trial_results)
            std_dev = np.std(trial_results)
            sem = std_dev / np.sqrt(len(trial_results))  # Standard error

            results.append({
                "coupling_strength": coupling,
                "mean_order_parameter": mean_order,
                "std_dev": std_dev,
                "sem": sem,
                "n_trials": len(trial_results)
            })

    elapsed = time.time() - start_time
    print(f"\n✅ Data collection complete in {elapsed:.1f}s")

    # Save to CSV
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"💾 Results saved to: {OUTPUT_FILE}")

    return df


def plot_results(df):
    """Generate publication-quality phase transition plot."""

    # Set scientific style
    plt.style.use('seaborn-v0_8-paper' if 'seaborn-v0_8-paper' in plt.style.available else 'default')

    fig, ax = plt.subplots(figsize=(10, 6))

    # Extract data
    x = df["coupling_strength"]
    y = df["mean_order_parameter"]
    err = df["std_dev"]

    # Main plot: mean with error bands
    ax.plot(x, y, 'b-', linewidth=2.5, label='Mean Order Parameter Φ', zorder=3)
    ax.fill_between(x, y - err, y + err, color='blue', alpha=0.2,
                     label='±1 Std Dev (Stochastic Variance)', zorder=2)

    # Identify critical point (steepest slope)
    gradient = np.gradient(y, x)
    critical_idx = np.argmax(gradient)
    critical_kappa = x.iloc[critical_idx]

    ax.axvline(x=critical_kappa, color='red', linestyle='--', linewidth=1.5,
               alpha=0.7, label=f'Critical Point κ_c ≈ {critical_kappa:.2f}', zorder=4)

    # Formatting
    ax.set_title("Phase Transition in UATC Neural Resonance Model\n" +
                 "Emergence of Synchronization as Function of Coupling Strength",
                 fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Coupling Strength κ (Interaction Magnitude)", fontsize=12)
    ax.set_ylabel("Order Parameter Φ (Phase Coherence)", fontsize=12)
    ax.legend(loc='upper left', framealpha=0.95)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.5)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(0, 1.05)

    plt.tight_layout()
    plt.savefig(PLOT_FILE, dpi=300, bbox_inches='tight')
    print(f"📊 Plot generated: {PLOT_FILE}")

    # Show plot
    plt.show()

    # Print critical point analysis
    print("\n" + "=" * 70)
    print("📈 CRITICAL POINT ANALYSIS")
    print("=" * 70)
    print(f"   κ_c (critical coupling) = {critical_kappa:.3f}")
    print(f"   Max gradient dΦ/dκ      = {gradient[critical_idx]:.3f}")
    print(f"   Interpretation: System transitions from disorder → order at κ ≈ {critical_kappa:.2f}")
    print("=" * 70)


if __name__ == "__main__":
    print("\n🧪 Starting UATC Scientific Validation\n")

    # Run the study
    data = run_study()

    # Visualize results
    plot_results(data)

    print("\n✨ Study complete! Check the analysis directory for results.\n")
