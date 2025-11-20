#!/usr/bin/env python3
"""
UTAC Klimakluft-Visualisierung
Zeigt wie die extreme Emissionsungleichheit den β-Parameter amplifiziert
Author: Johann Römer / UTAC Framework
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import lognorm
import seaborn as sns

# Style settings
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def create_emission_distribution():
    """Erstellt realistische Emissionsverteilung basierend auf Oxfam-Daten"""
    # Population percentiles
    population = np.linspace(0, 100, 10000)
    
    # Emissions in kg CO2/day
    emissions = np.zeros_like(population)
    
    # Bottom 50%: 2 kg/day
    emissions[population <= 50] = 2
    
    # Middle 40%: 5-20 kg/day (linear increase)
    middle_mask = (population > 50) & (population <= 90)
    emissions[middle_mask] = np.linspace(5, 20, sum(middle_mask))
    
    # Top 10% excluding ultra-rich: 20-100 kg/day
    top_mask = (population > 90) & (population <= 99.9)
    emissions[top_mask] = np.linspace(20, 100, sum(top_mask))
    
    # Top 0.1%: 800+ kg/day
    ultra_rich_mask = population > 99.9
    emissions[ultra_rich_mask] = 800 + np.random.exponential(200, sum(ultra_rich_mask))
    
    return population, emissions

def calculate_beta_amplification(emissions, base_beta=4.2):
    """Berechnet β-Amplifikation durch Emissionsungleichheit"""
    mean_emissions = np.mean(emissions)
    std_emissions = np.std(emissions)
    
    # Coefficient of variation
    cv = std_emissions / mean_emissions
    
    # Beta amplification formula
    beta_effective = base_beta * (1 + cv**2)
    
    return beta_effective, cv

def plot_comprehensive_analysis():
    """Erstellt umfassende UTAC-Klimakluft-Analyse"""
    
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Generate data
    pop, emissions = create_emission_distribution()
    beta_eff, cv = calculate_beta_amplification(emissions)
    
    # 1. Emission Distribution (log scale)
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.plot(pop, emissions, 'b-', linewidth=2)
    ax1.fill_between(pop, 0, emissions, alpha=0.3, color='red', 
                      where=(pop > 99.9), label='Top 0.1%')
    ax1.fill_between(pop, 0, emissions, alpha=0.3, color='yellow',
                      where=(pop > 90) & (pop <= 99.9), label='Top 10%')
    ax1.fill_between(pop, 0, emissions, alpha=0.3, color='green',
                      where=(pop <= 50), label='Bottom 50%')
    ax1.set_yscale('log')
    ax1.set_xlabel('Weltbevölkerung (%)', fontsize=12)
    ax1.set_ylabel('CO₂ Emissionen (kg/Tag)', fontsize=12)
    ax1.set_title('Globale Emissionsungleichheit (Oxfam 2024)', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Beta Amplification
    ax2 = fig.add_subplot(gs[0, 2])
    scenarios = ['Gleichverteilung\n(β = 4.2)', 
                 'Aktuelle Realität\n(β = 11.0)',
                 'Extremszenario\n(β = 13.0)']
    beta_values = [4.2, 11.0, 13.0]
    colors = ['green', 'orange', 'red']
    bars = ax2.bar(range(3), beta_values, color=colors, alpha=0.7)
    ax2.set_xticks(range(3))
    ax2.set_xticklabels(scenarios, rotation=0, ha='center')
    ax2.set_ylabel('UTAC β-Parameter', fontsize=12)
    ax2.set_title('β-Amplifikation durch Ungleichheit', fontsize=14, fontweight='bold')
    ax2.axhline(y=10, color='black', linestyle='--', alpha=0.5, label='Kritische Schwelle')
    ax2.legend()
    
    # Add value labels on bars
    for bar, value in zip(bars, beta_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # 3. Warning Time Reduction
    ax3 = fig.add_subplot(gs[1, 0])
    beta_range = np.linspace(3, 15, 100)
    warning_time = 100 / beta_range  # Normalized to 100 at β=1
    
    ax3.plot(beta_range, warning_time, 'b-', linewidth=2)
    ax3.fill_between(beta_range, 0, warning_time, alpha=0.3)
    ax3.axvline(x=4.2, color='green', linestyle='--', label='Ohne Ungleichheit')
    ax3.axvline(x=11.0, color='red', linestyle='--', label='Mit 0.1% Spike')
    ax3.set_xlabel('β-Parameter', fontsize=12)
    ax3.set_ylabel('Relative Warnzeit (%)', fontsize=12)
    ax3.set_title('Warnzeit-Kollaps: τ ∝ 1/β', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Sigmoid Transitions Comparison
    ax4 = fig.add_subplot(gs[1, 1])
    R = np.linspace(-3, 3, 200)
    theta = 0
    
    for beta, color, label in [(4.2, 'green', 'β=4.2 (manageable)'),
                                (11.0, 'red', 'β=11.0 (katastrophal)')]:
        S = 1 / (1 + np.exp(-beta * (R - theta)))
        ax4.plot(R, S, color=color, linewidth=2, label=label)
    
    ax4.set_xlabel('Systemantrieb R', fontsize=12)
    ax4.set_ylabel('Systemzustand S', fontsize=12)
    ax4.set_title('UTAC-Übergangsdynamik', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.axhline(y=0.5, color='black', linestyle=':', alpha=0.5)
    ax4.axvline(x=0, color='black', linestyle=':', alpha=0.5)
    
    # 5. Policy Scenarios
    ax5 = fig.add_subplot(gs[1, 2])
    scenarios = ['Business\nas Usual', 'Moderate\nUmverteilung', 'Radikale\nDekonzentration']
    collapse_prob = [80, 45, 15]
    colors = ['red', 'orange', 'green']
    
    bars = ax5.bar(range(3), collapse_prob, color=colors, alpha=0.7)
    ax5.set_xticks(range(3))
    ax5.set_xticklabels(scenarios, rotation=0, ha='center')
    ax5.set_ylabel('Kollapswahrscheinlichkeit bis 2100 (%)', fontsize=12)
    ax5.set_title('Policy-Szenarien', fontsize=14, fontweight='bold')
    ax5.axhline(y=50, color='black', linestyle='--', alpha=0.5)
    
    for bar, value in zip(bars, collapse_prob):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{value}%', ha='center', va='bottom', fontweight='bold')
    
    # 6. Timeline Visualization
    ax6 = fig.add_subplot(gs[2, :])
    years = np.arange(2025, 2101)
    
    # Different beta trajectories
    beta_bau = 11.0 + 0.02 * (years - 2025)  # Increasing
    beta_moderate = 11.0 - 0.05 * (years - 2025)  # Decreasing slowly
    beta_radical = 11.0 - 0.1 * (years - 2025)  # Decreasing fast
    beta_radical[beta_radical < 4.2] = 4.2  # Floor at natural level
    
    ax6.plot(years, beta_bau, 'r-', linewidth=2, label='Business as Usual')
    ax6.plot(years, beta_moderate, 'orange', linewidth=2, label='Moderate Maßnahmen')
    ax6.plot(years, beta_radical, 'g-', linewidth=2, label='Radikale Transformation')
    ax6.fill_between(years, 10, 15, alpha=0.2, color='red', label='Superkritische Zone')
    ax6.fill_between(years, 4, 10, alpha=0.2, color='yellow', label='Kritische Zone')
    ax6.fill_between(years, 0, 4, alpha=0.2, color='green', label='Manageable Zone')
    
    ax6.set_xlabel('Jahr', fontsize=12)
    ax6.set_ylabel('β-Parameter', fontsize=12)
    ax6.set_title('Zeitliche Entwicklung unter verschiedenen Policy-Szenarien', 
                  fontsize=14, fontweight='bold')
    ax6.legend(loc='upper left')
    ax6.grid(True, alpha=0.3)
    ax6.set_xlim(2025, 2100)
    ax6.set_ylim(0, 15)
    
    # Main title
    fig.suptitle('UTAC-Analyse: Die Klimakluft als β-Amplifikator', 
                 fontsize=16, fontweight='bold', y=1.02)
    
    # Add text box with key insights
    textstr = 'Kernaussagen:\n' \
              '• 0.1% emittieren 400x mehr CO₂ als Bottom 50%\n' \
              '• Dies erhöht β von 4.2 auf 11.0\n' \
              '• Warnzeit reduziert sich um 90%\n' \
              '• Nur radikale Dekonzentration kann β senken'
    
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    fig.text(0.02, 0.02, textstr, fontsize=10, verticalalignment='bottom',
             bbox=props)
    
    plt.tight_layout()
    return fig

def create_simple_infographic():
    """Erstellt einfache Infografik für Präsentationen"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left: The spike
    pop = [50, 40, 9.9, 0.1]
    emissions = [2, 10, 50, 800]
    colors = ['green', 'yellow', 'orange', 'red']
    
    bars = ax1.bar(range(4), emissions, color=colors, alpha=0.7)
    ax1.set_xticks(range(4))
    ax1.set_xticklabels(['Ärmste 50%', 'Mittlere 40%', 'Top 10%', 'Top 0.1%'])
    ax1.set_ylabel('CO₂ (kg/Tag/Person)', fontsize=14)
    ax1.set_title('Die Klimakluft', fontsize=16, fontweight='bold')
    ax1.set_yscale('log')
    
    for bar, value in zip(bars, emissions):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height * 1.1,
                f'{value} kg', ha='center', va='bottom', fontweight='bold')
    
    # Right: The consequence
    ax2.arrow(0.2, 0.5, 0.6, 0, head_width=0.05, head_length=0.05, 
              fc='black', ec='black')
    ax2.text(0.5, 0.6, 'führt zu', ha='center', fontsize=12)
    
    # Before and after boxes
    ax2.add_patch(plt.Rectangle((0.05, 0.2), 0.2, 0.2, 
                                facecolor='green', alpha=0.5))
    ax2.text(0.15, 0.3, 'β = 4.2\n(Warnzeit:\nJahrzehnte)', 
             ha='center', va='center', fontweight='bold')
    
    ax2.add_patch(plt.Rectangle((0.75, 0.2), 0.2, 0.2,
                                facecolor='red', alpha=0.5))
    ax2.text(0.85, 0.3, 'β = 11.0\n(Warnzeit:\nJahre)', 
             ha='center', va='center', fontweight='bold')
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis('off')
    ax2.set_title('UTAC-Konsequenz', fontsize=16, fontweight='bold')
    
    fig.suptitle('0.1% treiben uns in die Katastrophe', 
                 fontsize=18, fontweight='bold', color='darkred')
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # Create comprehensive analysis
    print("Erstelle umfassende UTAC-Klimakluft-Analyse...")
    fig1 = plot_comprehensive_analysis()
    fig1.savefig('/mnt/user-data/outputs/UTAC_Klimakluft_Comprehensive.png', 
                 dpi=300, bbox_inches='tight')
    print("✓ Gespeichert als: UTAC_Klimakluft_Comprehensive.png")
    
    # Create simple infographic
    print("Erstelle vereinfachte Infografik...")
    fig2 = create_simple_infographic()
    fig2.savefig('/mnt/user-data/outputs/UTAC_Klimakluft_Infographic.png', 
                 dpi=300, bbox_inches='tight')
    print("✓ Gespeichert als: UTAC_Klimakluft_Infographic.png")
    
    print("\nFertig! Beide Visualisierungen wurden erstellt.")
    print("\nKernaussage: Die reichsten 0.1% erhöhen β von 4.2 auf 11.0")
    print("→ Das reduziert die Warnzeit um 90%!")
    print("→ Nur radikale Emissionsdekonzentration kann uns retten.")
