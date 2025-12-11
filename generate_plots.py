import os

import matplotlib.pyplot as plt
import numpy as np

# Ordner sicherstellen
os.makedirs("figures", exist_ok=True)

# --- Plot 1: Klimakluft (Beta Amplification) ---
print("Generiere Klimakluft-Plot...")
ginis = np.linspace(0.2, 0.9, 50)
# Simulation der Formel: beta_eff = beta_base * (1 + gini * load_factor)
betas = [4.2 * (1 + g * 2.5) for g in ginis]

plt.figure(figsize=(10, 6))
plt.plot(ginis, betas, color="darkred", linewidth=3)
plt.axhline(y=11.0, color="orange", linestyle="--", label="Climate Tipping (AMOC)")
plt.axhline(y=13.5, color="red", linestyle="--", label="Catastrophic (WAIS)")
plt.xlabel("Inequality (Gini Coefficient)")
plt.ylabel("System Steepness (beta)")
plt.title("The Price of Inequality: Beta-Amplification through Load Concentration")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("figures/klimakluft_beta_amplification.png", dpi=300)
plt.close()

# --- Plot 2: Implosive Genesis (Trajektorie) ---
print("Generiere Implosions-Plot...")
R = np.linspace(-5, 5, 100)
Theta = 0
Beta = 4.2
# Invertierte Sigmoid (Type-6)
S = 1 / (1 + np.exp(Beta * (R - Theta)))

plt.figure(figsize=(10, 6))
plt.plot(R, S, color="indigo", linewidth=3, label="Type-6 Trajectory")
plt.fill_between(R, S, color="indigo", alpha=0.1)
plt.xlabel("Distance from Singularity (R)")
plt.ylabel("Activation / Structure (S)")
plt.title("Implosive Genesis: Emergence from Compression")
plt.axvline(x=0, color="black", linestyle=":", label="Threshold Theta (Pre-Space)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("figures/implosive_genesis_trajectory.png", dpi=300)
plt.close()

print("Fertig! Bilder wurden im Ordner /figures gespeichert.")
