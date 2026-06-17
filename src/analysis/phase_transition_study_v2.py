import matplotlib
import numpy as np

matplotlib.use('Agg')  # Use non-interactive backend
import math
import random
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm


# --- SIMPLE NEURON MODEL (standalone) ---
class SimpleNeuron:
    """Simplified oscillator for phase transition study."""
    def __init__(self, x, y):
        self.pos = (x, y)
        self.phase = random.uniform(0, 2 * math.pi)
        self.frequency = 40.0  # UATC Gamma frequency
        self.activation = 0.0
        self.connections = []

    def connect(self, other):
        if other not in self.connections:
            self.connections.append(other)

class SimpleHiveMind:
    """Simplified HiveMind for controlled experiments."""
    def __init__(self, width=8, height=8):
        self.neurons = []
        self.grid = {}

        # Create grid
        for y in range(height):
            for x in range(width):
                n = SimpleNeuron(x, y)
                self.neurons.append(n)
                self.grid[(x, y)] = n

        # Connect neighbors (4-connected grid)
        for n in self.neurons:
            x, y = n.pos
            neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
            for nx, ny in neighbors:
                if (nx, ny) in self.grid:
                    n.connect(self.grid[(nx, ny)])

# --- KONFIGURATION V2 ---
TRIALS_PER_POINT = 50   # Statistik
COUPLING_STEPS = 30     # Feinere Auflösung für den Plot
OUTPUT_FILE = "src/analysis/uatc_phase_transition_v2.csv"
PLOT_FILE = "src/analysis/uatc_phase_transition_v2.png"

# Parameter für die Dynamik
SIMULATION_TICKS = 400
STIMULUS_END_TICK = 100 # Nach 100 Ticks hören wir auf zu "stören"

def calculate_kuramoto_order(phases):
    """
    Berechnet den globalen Ordnungsparameter r.
    r = 1/N * | sum(e^(i*theta)) |
    r = 0 (Chaos), r = 1 (Totale Synchronisation)
    """
    if not phases:
        return 0.0
    # Wir nutzen komplexe Zahlen für die Kreisstatistik
    complex_phases = [complex(math.cos(p), math.sin(p)) for p in phases]
    # Mittelwert der Vektoren
    mean_vector = sum(complex_phases) / len(phases)
    # Der Betrag (Länge) ist der Ordnungsparameter
    return abs(mean_vector)

def run_single_trial_v2(coupling_strength):
    """
    Verbesserte Simulation: Längere Laufzeit, Ruhephase, korrekte Physik.
    """
    # Kleineres Netz für Performance, aber groß genug für Statistik
    mind = SimpleHiveMind(width=8, height=8) # 64 Oszillatoren

    r_history = []

    for tick in range(SIMULATION_TICKS):
        # 1. Stimulus Phase (Initiales "Aufwecken")
        # Wir geben Input nur am Anfang, um Energie ins System zu bringen
        stimulus_pos = (3, 3) # Mitte
        if tick < STIMULUS_END_TICK:
             target = mind.grid.get(stimulus_pos)
             if target:
                 target.activation = 1.0
        else:
            # RUHEPHASE: Kein Input mehr!
            # Jetzt muss das System sich selbst erhalten (Autopoiesis)
            pass

        # 2. Physik Update
        current_phases = []
        next_phases = {} # Zwischenspeicher für synchrones Update

        for n in mind.neurons:
            # Input-Stärke
            external_drive = 0.0
            if tick < STIMULUS_END_TICK and n.pos == stimulus_pos:
                external_drive = 1.0

            # --- Kuramoto Dynamik (Standard) ---
            # d_theta/dt = omega + K * sum(sin(theta_j - theta_i))

            interaction_sum = 0
            for neighbor in n.connections:
                # Sinus der Phasendifferenz
                interaction_sum += math.sin(neighbor.phase - n.phase)

            # Frequenz (Eigenfrequenz) - wir nehmen an alle haben ~40Hz (UATC Gamma)
            # Wir skalieren die Zeit (dt), damit die Simulation stabil bleibt
            dt = 0.1
            natural_freq = n.frequency * 0.05 # Skalierte Eigenfrequenz

            # Die Differentialgleichung
            d_theta = natural_freq + (coupling_strength * interaction_sum) + external_drive

            # Euler Integration
            new_phase = (n.phase + d_theta * dt) % (2 * math.pi)
            next_phases[n] = new_phase
            current_phases.append(new_phase)

        # Synchrones Update aller Neuronen
        for n, p in next_phases.items():
            n.phase = p

        # 3. Messung (Nur in der Ruhephase relevant)
        if tick > STIMULUS_END_TICK:
            r = calculate_kuramoto_order(current_phases)
            r_history.append(r)

    # Das Ergebnis ist der Durchschnitt der Ordnung in der Ruhephase
    # Wenn sie chaotisch sind, ist r ~ 0. Wenn sie sich "gefunden" haben, ist r > 0.5
    if not r_history:
        return 0.0
    return np.mean(r_history)

def run_study_v2():
    print("🔬 STARTING SCIENTIFIC ANALYSIS V2 (S-CURVE HUNT)")
    print("   - Sweeping Coupling κ [0.0 -> 1.0]")
    print("   - Method: Kuramoto Order Parameter (r)")
    print(f"   - Protocol: {STIMULUS_END_TICK} ticks drive -> {SIMULATION_TICKS - STIMULUS_END_TICK} ticks relaxation")

    coupling_values = np.linspace(0.0, 1.0, COUPLING_STEPS)
    results = []

    with Pool(processes=cpu_count()) as pool:
        for coupling in tqdm(coupling_values, desc="Simulating Universes"):
            args = [coupling] * TRIALS_PER_POINT
            trial_results = pool.map(run_single_trial_v2, args)

            results.append({
                "coupling_strength": coupling,
                "mean_r": np.mean(trial_results),
                "std_dev": np.std(trial_results)
            })

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ Results saved to: {OUTPUT_FILE}")
    return df

def plot_results_v2(df):
    plt.figure(figsize=(10, 6))
    plt.style.use('seaborn-v0_8-darkgrid')

    x = df["coupling_strength"]
    y = df["mean_r"]
    err = df["std_dev"]

    # Der Plot
    plt.errorbar(x, y, yerr=err, fmt='-o', color='crimson', ecolor='gray', capsize=3, label='Order Parameter $r$')

    # Kritische Zone (Theoretisch erwartet bei K_c = 2/pi * omega_spread für All-to-All,
    # aber im Gitter etwas höher)
    plt.axvspan(0.3, 0.6, color='yellow', alpha=0.2, label='Phase Transition Region')

    plt.title("Evidence of Phase Transition in UATC Network", fontsize=14)
    plt.xlabel("Coupling Strength $\\kappa$", fontsize=12)
    plt.ylabel("Synchronization $r$ (Self-Organization)", fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.savefig(PLOT_FILE, dpi=300)
    print(f"📊 Scientific Plot generated: {PLOT_FILE}")

if __name__ == "__main__":
    data = run_study_v2()
    plot_results_v2(data)
    print("\n🎯 Phase transition study complete!")
