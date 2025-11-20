#!/usr/bin/env python3
"""
Klimakluft Beta-Bomb Analysis
==============================

Quantifies how emission inequality acts as a β-amplification mechanism
in climate tipping point dynamics.

Based on: Römer, J.B. (2025). "The 0.1% Beta-Bomb: How Emission Inequality
Drives Climate Criticality"

Author: Johann B. Römer
Date: 2025-11-20
License: MIT
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import gini


class KlimaklustAnalyzer:
    """
    Analyzes β-amplification from emission inequality.

    Attributes:
        beta_base (float): Baseline climate β (without inequality amplification)
        variance_coupling (float): Coupling strength κ for variance-β relationship
        political_impedance (float): ζ_political factor (governance delay)
    """

    def __init__(self, beta_base=4.5, variance_coupling=5.0, political_impedance=1.75):
        self.beta_base = beta_base
        self.kappa = variance_coupling
        self.zeta_pol = political_impedance

    def compute_gini(self, emissions):
        """Compute Gini coefficient of emission distribution."""
        n = len(emissions)
        emissions_sorted = np.sort(emissions)
        index = np.arange(1, n + 1)
        return ((2 * index - n - 1) * emissions_sorted).sum() / (n * emissions_sorted.sum())

    def beta_from_gini(self, gini_coef):
        """
        Compute effective β from Gini coefficient.

        Equation: β_eff = β_base × (1 + κ·G²) × (1 + ζ_pol)

        Args:
            gini_coef (float): Emission Gini coefficient (0-1)

        Returns:
            float: Effective steepness parameter β
        """
        beta_variance = self.beta_base * (1 + self.kappa * gini_coef**2)
        beta_total = beta_variance * (1 + self.zeta_pol)
        return beta_total

    def warning_time(self, beta_eff, tau_baseline=50.0):
        """
        Compute early warning time from β.

        Equation: τ_warning ∝ 1/β

        Args:
            beta_eff (float): Effective β
            tau_baseline (float): Baseline warning time at β_base

        Returns:
            float: Warning time in years
        """
        return tau_baseline * (self.beta_base / beta_eff)

    def collapse_probability(self, beta_eff, time_horizon=2100):
        """
        Estimate collapse probability by given year.

        Heuristic model based on β-regime:
        - β < 5: Low risk (<20%)
        - β 5-8: Moderate risk (20-50%)
        - β > 8: High risk (>50%)

        Args:
            beta_eff (float): Effective β
            time_horizon (int): Year for probability estimate

        Returns:
            float: Collapse probability (0-1)
        """
        # Logistic function mapping β to probability
        # Calibrated to match scenario estimates
        beta_critical = 8.0
        steepness = 0.5
        p_base = 1 / (1 + np.exp(-steepness * (beta_eff - beta_critical)))

        # Time factor (assumes current trajectory)
        years_to_horizon = time_horizon - 2025
        time_factor = min(1.0, years_to_horizon / 75)  # 75-year horizon

        return p_base * time_factor

    def emission_distribution(self, n_population=1000000):
        """
        Generate realistic emission distribution with 0.1% spike.

        Args:
            n_population (int): Population size to simulate

        Returns:
            np.ndarray: Emission values (kg CO₂/day)
        """
        emissions = np.zeros(n_population)

        # Bottom 50%: ~2 kg/day (Gaussian around baseline)
        n_bottom = int(n_population * 0.50)
        emissions[:n_bottom] = np.random.normal(2.0, 0.5, n_bottom)

        # 50-90th percentile: ~10 kg/day
        n_mid = int(n_population * 0.40)
        emissions[n_bottom:n_bottom+n_mid] = np.random.normal(10.0, 3.0, n_mid)

        # 90-99th percentile: ~50 kg/day
        n_upper = int(n_population * 0.09)
        start_idx = n_bottom + n_mid
        emissions[start_idx:start_idx+n_upper] = np.random.lognormal(np.log(50), 0.3, n_upper)

        # 99-99.9th percentile: ~200 kg/day
        n_top1 = int(n_population * 0.009)
        start_idx = start_idx + n_upper
        emissions[start_idx:start_idx+n_top1] = np.random.lognormal(np.log(200), 0.2, n_top1)

        # Top 0.1%: >800 kg/day (delta spike)
        n_top01 = int(n_population * 0.001)
        emissions[-n_top01:] = np.random.lognormal(np.log(800), 0.15, n_top01)

        return np.maximum(emissions, 0)  # Ensure non-negative

    def scenario_analysis(self):
        """
        Compute β, τ_warning, and P(collapse) for three policy scenarios.

        Returns:
            pd.DataFrame: Scenario comparison table
        """
        scenarios = {
            'Business-as-Usual': {
                'top_01_emission': 850,
                'gini': 0.72,
                'description': 'Current inequality persists'
            },
            'Moderate Redistribution': {
                'top_01_emission': 100,
                'gini': 0.50,
                'description': 'Progressive carbon taxes, wealth taxes'
            },
            'Radical Deconcentration': {
                'top_01_emission': 20,
                'gini': 0.28,
                'description': 'Global emission cap at 20 kg/day'
            }
        }

        results = []
        for name, params in scenarios.items():
            beta = self.beta_from_gini(params['gini'])
            tau = self.warning_time(beta)
            p_collapse = self.collapse_probability(beta)

            results.append({
                'Scenario': name,
                'Top 0.1% Emission (kg/day)': params['top_01_emission'],
                'Gini Coefficient': params['gini'],
                'β (Steepness)': round(beta, 1),
                'τ_warning (years)': round(tau, 1),
                'P(Collapse 2100) (%)': round(p_collapse * 100, 0),
                'Description': params['description']
            })

        return pd.DataFrame(results)

    def visualize_beta_bomb(self, save_path='klimakluft_beta_bomb.png'):
        """
        Create comprehensive 4-panel visualization.

        Args:
            save_path (str): Path to save figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Panel A: Emission distribution
        pop_percentile = np.linspace(0, 100, 1000)
        emissions = self._emission_curve(pop_percentile)

        axes[0,0].plot(pop_percentile, emissions, 'b-', linewidth=2.5)
        axes[0,0].fill_between(pop_percentile, 0, emissions, alpha=0.3, color='skyblue')
        axes[0,0].set_xlabel('Population Percentile (%)', fontsize=11)
        axes[0,0].set_ylabel('CO₂ Emission (kg/day)', fontsize=11)
        axes[0,0].set_yscale('log')
        axes[0,0].set_title('A) Emission Delta-Peak (0.1% Spike)', fontsize=12, fontweight='bold')
        axes[0,0].axhline(y=2, color='green', linestyle='--', linewidth=2, label='Sustainable (~2 kg/day)')
        axes[0,0].axhline(y=800, color='red', linestyle='--', linewidth=2, label='0.1% Peak (>800 kg/day)')
        axes[0,0].legend(fontsize=10, loc='upper left')
        axes[0,0].grid(True, alpha=0.3)
        axes[0,0].set_ylim([1, 2000])

        # Panel B: Beta amplification
        gini_range = np.linspace(0, 0.8, 100)
        beta_curve = [self.beta_from_gini(g) for g in gini_range]

        axes[0,1].plot(gini_range, beta_curve, 'r-', linewidth=2.5)
        axes[0,1].axhline(y=self.beta_base, color='green', linestyle='--', linewidth=2,
                         label=f'β_base = {self.beta_base} (manageable)')
        axes[0,1].axhline(y=11, color='red', linestyle='--', linewidth=2,
                         label='β = 11 (catastrophic)')
        axes[0,1].fill_between(gini_range, self.beta_base, beta_curve,
                              where=(np.array(beta_curve) > self.beta_base),
                              color='red', alpha=0.2, label='Amplified zone')
        axes[0,1].axvline(x=0.72, color='orange', linestyle=':', linewidth=2.5,
                         label='Current G_CO₂ ≈ 0.72')
        axes[0,1].set_xlabel('Emission Gini Coefficient', fontsize=11)
        axes[0,1].set_ylabel('Effective β (Steepness)', fontsize=11)
        axes[0,1].set_title('B) β-Amplification Mechanism', fontsize=12, fontweight='bold')
        axes[0,1].legend(fontsize=9, loc='upper left')
        axes[0,1].grid(True, alpha=0.3)
        axes[0,1].set_ylim([3, 18])

        # Panel C: Warning time collapse
        tau_curve = [self.warning_time(self.beta_from_gini(g)) for g in gini_range]

        axes[1,0].plot(gini_range, tau_curve, 'b-', linewidth=2.5)
        axes[1,0].axhline(y=50, color='green', linestyle='--', linewidth=2,
                         label='Baseline (50 yr)')
        axes[1,0].axhline(y=5, color='red', linestyle='--', linewidth=2,
                         label='Collapsed (5 yr)')
        axes[1,0].fill_between(gini_range, 0, tau_curve, alpha=0.3, color='lightblue')
        axes[1,0].axvline(x=0.72, color='orange', linestyle=':', linewidth=2.5,
                         label='Current G_CO₂')
        axes[1,0].set_xlabel('Emission Gini Coefficient', fontsize=11)
        axes[1,0].set_ylabel('τ_warning (years)', fontsize=11)
        axes[1,0].set_title('C) Early Warning Time Collapse (AMOC)', fontsize=12, fontweight='bold')
        axes[1,0].legend(fontsize=10, loc='upper right')
        axes[1,0].grid(True, alpha=0.3)
        axes[1,0].set_ylim([0, 60])

        # Panel D: Policy scenarios
        df_scenarios = self.scenario_analysis()
        scenarios = ['BAU\n(G=0.72)', 'Moderate\n(G=0.50)', 'Radical\n(G=0.28)']
        beta_vals = df_scenarios['β (Steepness)'].values
        collapse_prob = df_scenarios['P(Collapse 2100) (%)'].values
        colors = ['darkred', 'orange', 'green']

        x_pos = np.arange(len(scenarios))
        bars = axes[1,1].bar(x_pos, collapse_prob, color=colors, alpha=0.75, width=0.6,
                            edgecolor='black', linewidth=1.5)
        axes[1,1].set_ylabel('Collapse Probability by 2100 (%)', fontsize=11)
        axes[1,1].set_title('D) Policy Scenario Comparison', fontsize=12, fontweight='bold')
        axes[1,1].set_xticks(x_pos)
        axes[1,1].set_xticklabels(scenarios, fontsize=10)
        axes[1,1].axhline(y=50, color='black', linestyle=':', alpha=0.6, linewidth=2,
                         label='50% threshold')
        axes[1,1].grid(True, alpha=0.3, axis='y')

        # Add beta values as text on bars
        for i, (b, p) in enumerate(zip(beta_vals, collapse_prob)):
            axes[1,1].text(i, p + 4, f'β={b}', ha='center', fontsize=11,
                          fontweight='bold', color='white' if p > 30 else 'black')

        axes[1,1].legend(fontsize=10)
        axes[1,1].set_ylim([0, 100])

        plt.suptitle('The 0.1% Beta-Bomb: Emission Inequality Drives Climate Criticality',
                     fontsize=15, fontweight='bold', y=0.998)
        plt.tight_layout(rect=[0, 0, 1, 0.995])
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✓ Figure saved to {save_path}")
        plt.show()

    def _emission_curve(self, percentiles):
        """Helper: Generate smooth emission curve for plotting."""
        emissions = np.ones_like(percentiles) * 2.0
        emissions[(percentiles > 50) & (percentiles <= 90)] = 10.0
        emissions[(percentiles > 90) & (percentiles <= 99)] = 50.0
        emissions[(percentiles > 99) & (percentiles <= 99.9)] = 200.0
        emissions[percentiles > 99.9] = 850.0
        return emissions


def main():
    """Run complete Klimakluft analysis."""
    print("=" * 60)
    print("KLIMAKLUFT β-BOMB ANALYSIS")
    print("=" * 60)
    print()

    # Initialize analyzer
    analyzer = KlimaklustAnalyzer(
        beta_base=4.5,
        variance_coupling=5.0,
        political_impedance=1.75
    )

    # Generate emission distribution
    print("1. Generating emission distribution...")
    emissions = analyzer.emission_distribution(n_population=1000000)
    gini_computed = analyzer.compute_gini(emissions)
    print(f"   Computed Gini coefficient: {gini_computed:.3f}")
    print(f"   Top 0.1% mean emission: {emissions[-1000:].mean():.1f} kg/day")
    print(f"   Bottom 50% mean emission: {emissions[:500000].mean():.1f} kg/day")
    print(f"   Ratio: {emissions[-1000:].mean() / emissions[:500000].mean():.0f}x")
    print()

    # Scenario analysis
    print("2. Policy scenario analysis...")
    df = analyzer.scenario_analysis()
    print(df.to_string(index=False))
    print()

    # Key findings
    print("3. Key findings:")
    bau_beta = df.loc[0, 'β (Steepness)']
    rad_beta = df.loc[2, 'β (Steepness)']
    bau_tau = df.loc[0, 'τ_warning (years)']
    rad_tau = df.loc[2, 'τ_warning (years)']

    print(f"   • BAU β-amplification: {analyzer.beta_base:.1f} → {bau_beta:.1f} " +
          f"({(bau_beta/analyzer.beta_base - 1)*100:.0f}% increase)")
    print(f"   • Warning time collapse: {rad_tau:.0f} yr → {bau_tau:.0f} yr " +
          f"({(1 - bau_tau/rad_tau)*100:.0f}% reduction)")
    print(f"   • Radical deconcentration recovers: β = {rad_beta:.1f} " +
          f"(near baseline {analyzer.beta_base:.1f})")
    print()

    # Visualize
    print("4. Generating visualization...")
    analyzer.visualize_beta_bomb(save_path='analysis/results/klimakluft_beta_bomb.png')
    print()

    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print()
    print("Citation:")
    print("Römer, J.B. (2025). The 0.1% Beta-Bomb: How Emission Inequality")
    print("Drives Climate Criticality. Feldtheorie Project.")
    print()


if __name__ == "__main__":
    main()
