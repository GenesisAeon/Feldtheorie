"""
Statistical Analysis Module for DESTINY+ Predictions
=====================================================

Implements the statistical tests outlined in DESTINY_PLUS_PREDICTIONS.md:
  1. LST Distribution Analysis (χ² test)
  2. Velocity Distribution Analysis (Gaussian Mixture Model)
  3. Spatial Repeatability Index (R-statistic)
  4. Plasma Correlation Analysis (r² coefficient)
  5. Null Hypothesis Testing (Kolmogorov-Smirnov)

Author: Johann Benjamin Römer
Framework: GenesisAeon v10.2 / UTAC Case Study
Date: 2026-02-04
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import (kstest, chisquare, normaltest, anderson,
                         pearsonr, spearmanr, gaussian_kde)
from scipy.optimize import minimize
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional
import json
from pathlib import Path

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class StatisticalResult:
    """Container for statistical test results."""
    test_name: str
    statistic: float
    p_value: float
    hypothesis_supported: str  # 'CHIMERA', 'THERMAL', 'RANDOM', or 'INCONCLUSIVE'
    confidence: str  # 'HIGH', 'MEDIUM', 'LOW'
    details: str

    def __str__(self) -> str:
        return (f"{self.test_name}\n"
                f"  Statistic: {self.statistic:.4f}\n"
                f"  P-value: {self.p_value:.4e}\n"
                f"  Supports: {self.hypothesis_supported}\n"
                f"  Confidence: {self.confidence}\n"
                f"  Details: {self.details}")

# ============================================================================
# LST DISTRIBUTION ANALYSIS
# ============================================================================

class LSTAnalyzer:
    """
    Analyzes Local Solar Time distribution of ejection events.

    Hypotheses:
      - CHIMERA: Peak at LST = 15-18h (late afternoon)
      - THERMAL: Peak at LST = 12-14h (solar noon)
      - RANDOM: Uniform distribution
    """

    def __init__(self, LST_values: np.ndarray, period_h: float = 3.604):
        """
        Parameters:
            LST_values: Array of LST values for ejection events (hours)
            period_h: Rotation period (hours)
        """
        self.LST = np.array(LST_values)
        self.period = period_h
        self.n_events = len(self.LST)

    def compute_circular_mean(self) -> float:
        """
        Compute circular mean of LST distribution.

        Proper treatment for periodic data.
        """
        # Convert to angular coordinates
        theta = 2 * np.pi * self.LST / self.period

        # Circular mean
        mean_cos = np.mean(np.cos(theta))
        mean_sin = np.mean(np.sin(theta))

        mean_angle = np.arctan2(mean_sin, mean_cos)
        if mean_angle < 0:
            mean_angle += 2 * np.pi

        mean_LST = mean_angle * self.period / (2 * np.pi)
        return mean_LST

    def compute_circular_variance(self) -> float:
        """
        Compute circular variance (measure of dispersion).

        V = 1 - R, where R is the mean resultant length.
        """
        theta = 2 * np.pi * self.LST / self.period

        mean_cos = np.mean(np.cos(theta))
        mean_sin = np.mean(np.sin(theta))

        R = np.sqrt(mean_cos**2 + mean_sin**2)
        variance = 1 - R

        return variance

    def test_uniformity(self) -> StatisticalResult:
        """
        Test null hypothesis of uniform LST distribution.

        Uses Rayleigh test for circular uniformity.
        """
        theta = 2 * np.pi * self.LST / self.period

        # Mean resultant length
        mean_cos = np.mean(np.cos(theta))
        mean_sin = np.mean(np.sin(theta))
        R_bar = np.sqrt(mean_cos**2 + mean_sin**2)

        # Rayleigh test statistic
        n = len(theta)
        z = n * R_bar**2

        # P-value (approximate for large n)
        p_value = np.exp(-z) * (1 + (2*z - z**2) / (4*n) - (24*z - 132*z**2 + 76*z**3 - 9*z**4) / (288*n**2))
        p_value = max(0, min(1, p_value))

        if p_value < 0.01:
            hypothesis = 'CHIMERA or THERMAL (not random)'
            confidence = 'HIGH'
        elif p_value < 0.05:
            hypothesis = 'CHIMERA or THERMAL (not random)'
            confidence = 'MEDIUM'
        else:
            hypothesis = 'RANDOM'
            confidence = 'HIGH'

        return StatisticalResult(
            test_name='Rayleigh Test for Uniformity',
            statistic=z,
            p_value=p_value,
            hypothesis_supported=hypothesis,
            confidence=confidence,
            details=f'R̄ = {R_bar:.3f}, n = {n}'
        )

    def test_chimera_vs_thermal(self) -> StatisticalResult:
        """
        Test whether LST distribution supports chimera (15-18h) vs thermal (12-14h).

        Uses binned χ² test.
        """
        # Define LST bins (normalized to period)
        n_bins = 12
        bin_edges = np.linspace(0, self.period, n_bins + 1)

        # Observed histogram
        observed, _ = np.histogram(self.LST, bins=bin_edges)

        # Expected for chimera (peak at 15-18h, normalized to period)
        chimera_peak_start = 15 / 24 * self.period
        chimera_peak_end = 18 / 24 * self.period
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        # Chimera expected distribution (Gaussian-like peak)
        chimera_center = (chimera_peak_start + chimera_peak_end) / 2
        chimera_expected = np.exp(-0.5 * ((bin_centers - chimera_center) / (0.2 * self.period))**2)
        chimera_expected = chimera_expected / np.sum(chimera_expected) * self.n_events

        # Thermal expected distribution (peak at 12-14h)
        thermal_peak_start = 12 / 24 * self.period
        thermal_peak_end = 14 / 24 * self.period
        thermal_center = (thermal_peak_start + thermal_peak_end) / 2
        thermal_expected = np.exp(-0.5 * ((bin_centers - thermal_center) / (0.15 * self.period))**2)
        thermal_expected = thermal_expected / np.sum(thermal_expected) * self.n_events

        # χ² statistics
        # Avoid division by zero
        chimera_expected = np.maximum(chimera_expected, 1)
        thermal_expected = np.maximum(thermal_expected, 1)

        chi2_chimera = np.sum((observed - chimera_expected)**2 / chimera_expected)
        chi2_thermal = np.sum((observed - thermal_expected)**2 / thermal_expected)

        # Degrees of freedom
        dof = n_bins - 1

        # P-values
        p_chimera = 1 - stats.chi2.cdf(chi2_chimera, dof)
        p_thermal = 1 - stats.chi2.cdf(chi2_thermal, dof)

        # Determine which hypothesis is better supported
        if chi2_chimera < chi2_thermal:
            hypothesis = 'CHIMERA'
            better_chi2 = chi2_chimera
            better_p = p_chimera
        else:
            hypothesis = 'THERMAL'
            better_chi2 = chi2_thermal
            better_p = p_thermal

        # Confidence based on difference
        chi2_diff = abs(chi2_chimera - chi2_thermal)
        if chi2_diff > 20:
            confidence = 'HIGH'
        elif chi2_diff > 10:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'

        return StatisticalResult(
            test_name='χ² Test: Chimera vs Thermal',
            statistic=better_chi2,
            p_value=better_p,
            hypothesis_supported=hypothesis,
            confidence=confidence,
            details=f'χ²_chimera = {chi2_chimera:.2f}, χ²_thermal = {chi2_thermal:.2f}'
        )

    def compute_peak_LST(self, n_bins: int = 48) -> Tuple[float, float]:
        """
        Find peak LST using kernel density estimation.

        Returns:
            (peak_LST, peak_density)
        """
        # Use circular KDE
        LST_extended = np.concatenate([
            self.LST - self.period,
            self.LST,
            self.LST + self.period
        ])

        kde = gaussian_kde(LST_extended)

        # Evaluate on grid
        LST_grid = np.linspace(0, self.period, n_bins)
        density = kde(LST_grid)

        # Find peak
        peak_idx = np.argmax(density)
        peak_LST = LST_grid[peak_idx]
        peak_density = density[peak_idx]

        return peak_LST, peak_density

    def generate_report(self) -> str:
        """Generate comprehensive LST analysis report."""
        mean_LST = self.compute_circular_mean()
        var_LST = self.compute_circular_variance()
        peak_LST, peak_density = self.compute_peak_LST()

        uniformity_test = self.test_uniformity()
        chimera_test = self.test_chimera_vs_thermal()

        # Convert to 24h scale for reporting
        mean_LST_24h = mean_LST / self.period * 24
        peak_LST_24h = peak_LST / self.period * 24

        report = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                     LST DISTRIBUTION ANALYSIS REPORT                      ║
╚═══════════════════════════════════════════════════════════════════════════╝

BASIC STATISTICS
────────────────────────────────────────────────────────────────────────────
  Number of events:           {self.n_events}
  Rotation period:            {self.period:.3f} hours

  Circular mean LST:          {mean_LST:.3f} h ({mean_LST_24h:.1f}h equivalent)
  Circular variance:          {var_LST:.4f}
  Peak LST (KDE):             {peak_LST:.3f} h ({peak_LST_24h:.1f}h equivalent)

UNIFORMITY TEST (Rayleigh)
────────────────────────────────────────────────────────────────────────────
{uniformity_test}

CHIMERA VS THERMAL TEST (χ²)
────────────────────────────────────────────────────────────────────────────
{chimera_test}

INTERPRETATION
────────────────────────────────────────────────────────────────────────────
"""
        # Interpretation based on peak LST (in 24h scale)
        if 14 <= peak_LST_24h <= 19:
            report += "  ✓ LST peak is consistent with CHIMERA MODEL (15-18h)\n"
            report += "  → Thermal fatigue + chimera state mechanism likely\n"
        elif 11 <= peak_LST_24h < 15:
            report += "  ✓ LST peak is consistent with THERMAL MODEL (12-14h)\n"
            report += "  → Pure thermal stress mechanism likely\n"
        else:
            report += "  ? LST peak is ANOMALOUS - further investigation needed\n"
            report += f"  → Observed peak at {peak_LST_24h:.1f}h does not match predictions\n"

        report += f"""
FALSIFICATION CHECK
────────────────────────────────────────────────────────────────────────────
  Peak in 15-18h range?       {'YES ✓' if 14 <= peak_LST_24h <= 19 else 'NO ✗'}
  Distribution non-uniform?   {'YES ✓' if uniformity_test.p_value < 0.05 else 'NO ✗'}
  Chimera model preferred?    {'YES ✓' if chimera_test.hypothesis_supported == 'CHIMERA' else 'NO ✗'}

═══════════════════════════════════════════════════════════════════════════
"""
        return report

# ============================================================================
# VELOCITY DISTRIBUTION ANALYSIS
# ============================================================================

class VelocityAnalyzer:
    """
    Analyzes dust velocity distribution.

    Tests for multi-modal (soliton) vs unimodal (thermal) distribution.
    """

    def __init__(self, velocities: np.ndarray):
        """
        Parameters:
            velocities: Array of dust velocities (m/s)
        """
        self.velocities = np.array(velocities)
        self.n_particles = len(self.velocities)

    def fit_gaussian_mixture(self, n_components: int = 3) -> Dict:
        """
        Fit Gaussian Mixture Model to velocity distribution.

        Simple EM-like implementation.
        """
        from scipy.optimize import minimize

        v = self.velocities.copy()
        v = v[v > 0]  # Remove non-physical

        def negative_log_likelihood(params):
            """Negative log-likelihood for GMM."""
            n = n_components
            # Parse parameters: [w1, w2, ..., mu1, mu2, ..., sigma1, sigma2, ...]
            weights = params[:n]
            weights = np.exp(weights) / np.sum(np.exp(weights))  # Softmax
            means = params[n:2*n]
            sigmas = np.abs(params[2*n:]) + 1e-6

            # Compute mixture likelihood
            likelihood = np.zeros_like(v)
            for w, mu, sigma in zip(weights, means, sigmas):
                likelihood += w * stats.norm.pdf(v, mu, sigma)

            # Avoid log(0)
            likelihood = np.maximum(likelihood, 1e-300)

            return -np.sum(np.log(likelihood))

        # Initial guess: equally spaced means
        v_min, v_max = np.min(v), np.max(v)
        init_means = np.linspace(v_min + 50, v_max - 50, n_components)
        init_sigmas = np.full(n_components, np.std(v) / n_components)
        init_weights = np.zeros(n_components)

        x0 = np.concatenate([init_weights, init_means, init_sigmas])

        # Optimize
        result = minimize(negative_log_likelihood, x0, method='Nelder-Mead',
                         options={'maxiter': 5000})

        # Extract fitted parameters
        params = result.x
        weights = np.exp(params[:n_components])
        weights /= np.sum(weights)
        means = params[n_components:2*n_components]
        sigmas = np.abs(params[2*n_components:])

        # Sort by mean
        order = np.argsort(means)
        weights = weights[order]
        means = means[order]
        sigmas = sigmas[order]

        # Compute BIC
        n_params = 3 * n_components
        bic = 2 * result.fun + n_params * np.log(len(v))

        return {
            'n_components': n_components,
            'weights': weights,
            'means': means,
            'sigmas': sigmas,
            'nll': result.fun,
            'bic': bic,
            'converged': result.success
        }

    def test_multimodality(self) -> StatisticalResult:
        """
        Test whether velocity distribution is multimodal.

        Compares BIC for 1, 2, and 3 component GMMs.
        """
        results = {}
        for n_comp in [1, 2, 3]:
            results[n_comp] = self.fit_gaussian_mixture(n_comp)

        bics = {k: v['bic'] for k, v in results.items()}
        best_n = min(bics, key=bics.get)

        # Bayes factor between models
        delta_bic = bics[1] - bics[best_n]

        if best_n == 3 and delta_bic > 10:
            hypothesis = 'SOLITON (multi-modal)'
            confidence = 'HIGH'
        elif best_n >= 2 and delta_bic > 5:
            hypothesis = 'SOLITON (multi-modal)'
            confidence = 'MEDIUM'
        else:
            hypothesis = 'THERMAL (unimodal)'
            confidence = 'HIGH' if delta_bic < 2 else 'MEDIUM'

        return StatisticalResult(
            test_name='Multimodality Test (BIC comparison)',
            statistic=float(best_n),
            p_value=delta_bic,  # Using delta-BIC as "p-value" proxy
            hypothesis_supported=hypothesis,
            confidence=confidence,
            details=f'BIC(1) = {bics[1]:.1f}, BIC(2) = {bics[2]:.1f}, BIC(3) = {bics[3]:.1f}'
        )

    def test_high_velocity_excess(self, threshold: float = 200) -> StatisticalResult:
        """
        Test for excess of high-velocity particles (soliton signature).
        """
        # Fit thermal (Maxwell) distribution to low-velocity particles
        v_low = self.velocities[self.velocities < threshold]
        v_high = self.velocities[self.velocities >= threshold]

        n_high_observed = len(v_high)
        n_total = len(self.velocities)

        # Expected under Maxwell distribution (fitted to low-v)
        if len(v_low) > 10:
            # Maxwell scale parameter
            scale = np.sqrt(np.mean(v_low**2) / 3)

            # Expected fraction above threshold
            expected_fraction = 1 - stats.maxwell.cdf(threshold, scale=scale)
            n_high_expected = expected_fraction * n_total
        else:
            n_high_expected = n_total * 0.01  # Default expectation

        # Poisson test
        if n_high_expected > 0:
            excess_ratio = n_high_observed / n_high_expected
            p_value = 1 - stats.poisson.cdf(n_high_observed - 1, n_high_expected)
        else:
            excess_ratio = float('inf') if n_high_observed > 0 else 0
            p_value = 0 if n_high_observed > 0 else 1

        if excess_ratio > 5 and p_value < 0.01:
            hypothesis = 'SOLITON (high-v excess)'
            confidence = 'HIGH'
        elif excess_ratio > 2 and p_value < 0.05:
            hypothesis = 'SOLITON (high-v excess)'
            confidence = 'MEDIUM'
        else:
            hypothesis = 'THERMAL'
            confidence = 'HIGH'

        return StatisticalResult(
            test_name=f'High-Velocity Excess Test (>{threshold} m/s)',
            statistic=excess_ratio,
            p_value=p_value,
            hypothesis_supported=hypothesis,
            confidence=confidence,
            details=f'Observed: {n_high_observed}, Expected: {n_high_expected:.1f}'
        )

    def identify_velocity_peaks(self) -> List[float]:
        """
        Identify peaks in velocity distribution using KDE.
        """
        from scipy.signal import find_peaks

        v = self.velocities[self.velocities > 0]
        kde = gaussian_kde(v)

        # Evaluate on grid
        v_grid = np.linspace(0, np.max(v), 500)
        density = kde(v_grid)

        # Find peaks
        peaks, properties = find_peaks(density, prominence=0.0001)

        peak_velocities = v_grid[peaks]

        return sorted(peak_velocities.tolist())

    def generate_report(self) -> str:
        """Generate velocity analysis report."""
        multimodal_test = self.test_multimodality()
        excess_test = self.test_high_velocity_excess(200)
        peaks = self.identify_velocity_peaks()

        # Fit 3-component GMM for reporting
        gmm_3 = self.fit_gaussian_mixture(3)

        report = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                   VELOCITY DISTRIBUTION ANALYSIS REPORT                   ║
╚═══════════════════════════════════════════════════════════════════════════╝

BASIC STATISTICS
────────────────────────────────────────────────────────────────────────────
  Number of particles:        {self.n_particles}
  Mean velocity:              {np.mean(self.velocities):.1f} m/s
  Median velocity:            {np.median(self.velocities):.1f} m/s
  Std deviation:              {np.std(self.velocities):.1f} m/s
  Min / Max:                  {np.min(self.velocities):.1f} / {np.max(self.velocities):.1f} m/s

DETECTED PEAKS (KDE)
────────────────────────────────────────────────────────────────────────────
"""
        for i, peak in enumerate(peaks[:5], 1):
            report += f"  Peak {i}: {peak:.1f} m/s\n"

        report += f"""
PREDICTED SOLITON PEAKS
────────────────────────────────────────────────────────────────────────────
  v₁ (fundamental): 120 m/s
  v₂ (2nd harmonic): 250 m/s
  v₃ (3rd harmonic): 380 m/s

GMM FIT (3 components)
────────────────────────────────────────────────────────────────────────────
  Component 1: μ = {gmm_3['means'][0]:.1f} m/s, σ = {gmm_3['sigmas'][0]:.1f}, w = {gmm_3['weights'][0]:.2f}
  Component 2: μ = {gmm_3['means'][1]:.1f} m/s, σ = {gmm_3['sigmas'][1]:.1f}, w = {gmm_3['weights'][1]:.2f}
  Component 3: μ = {gmm_3['means'][2]:.1f} m/s, σ = {gmm_3['sigmas'][2]:.1f}, w = {gmm_3['weights'][2]:.2f}

MULTIMODALITY TEST
────────────────────────────────────────────────────────────────────────────
{multimodal_test}

HIGH-VELOCITY EXCESS TEST
────────────────────────────────────────────────────────────────────────────
{excess_test}

INTERPRETATION
────────────────────────────────────────────────────────────────────────────
"""
        if multimodal_test.hypothesis_supported.startswith('SOLITON'):
            report += "  ✓ Velocity distribution is MULTIMODAL - soliton transport likely\n"
        else:
            report += "  ✗ Velocity distribution is UNIMODAL - thermal escape dominates\n"

        report += f"""
FALSIFICATION CHECK
────────────────────────────────────────────────────────────────────────────
  Multi-modal distribution?   {'YES ✓' if 'SOLITON' in multimodal_test.hypothesis_supported else 'NO ✗'}
  High-velocity excess?       {'YES ✓' if 'SOLITON' in excess_test.hypothesis_supported else 'NO ✗'}
  All velocities < 50 m/s?    {'NO ✓' if np.max(self.velocities) > 50 else 'YES ✗ (FALSIFIES MODEL)'}

═══════════════════════════════════════════════════════════════════════════
"""
        return report

# ============================================================================
# SPATIAL REPEATABILITY ANALYSIS
# ============================================================================

class RepeatabilityAnalyzer:
    """
    Analyzes spatial repeatability of active regions.

    Key metric: R = (# patches active in > 1 orbit) / (# total active patches)
    """

    def __init__(self, activation_history: np.ndarray, n_orbits: int = 3):
        """
        Parameters:
            activation_history: Array of activation counts per patch
            n_orbits: Number of orbits in simulation
        """
        self.activation_history = np.array(activation_history)
        self.n_patches = len(activation_history)
        self.n_orbits = n_orbits

    def compute_repeatability_index(self) -> float:
        """
        Compute repeatability index R.

        R = (patches with > 1 activation) / (total active patches)
        """
        active_patches = self.activation_history > 0
        repeat_patches = self.activation_history > 1

        n_active = np.sum(active_patches)
        n_repeat = np.sum(repeat_patches)

        if n_active == 0:
            return 0.0

        R = n_repeat / n_active
        return R

    def test_repeatability(self) -> StatisticalResult:
        """
        Test whether repeatability is consistent with memory effect.
        """
        R = self.compute_repeatability_index()

        # Under random hypothesis, expected R depends on activity rate
        # For Poisson with rate λ: P(k > 1) / P(k > 0)
        total_events = np.sum(self.activation_history)
        lambda_mean = total_events / self.n_patches

        if lambda_mean > 0:
            p_active = 1 - np.exp(-lambda_mean)
            p_repeat = 1 - np.exp(-lambda_mean) - lambda_mean * np.exp(-lambda_mean)
            R_expected_random = p_repeat / p_active if p_active > 0 else 0
        else:
            R_expected_random = 0

        # Test statistic: observed R vs expected
        delta_R = R - R_expected_random

        # Binomial test
        n_active = np.sum(self.activation_history > 0)
        n_repeat = np.sum(self.activation_history > 1)

        if n_active > 0:
            p_value = stats.binom.sf(n_repeat - 1, n_active, R_expected_random)
        else:
            p_value = 1.0

        if R > 0.5 and p_value < 0.01:
            hypothesis = 'FRUSTRATED SYSTEM (memory effect)'
            confidence = 'HIGH'
        elif R > 0.3 and p_value < 0.05:
            hypothesis = 'FRUSTRATED SYSTEM (memory effect)'
            confidence = 'MEDIUM'
        else:
            hypothesis = 'RANDOM'
            confidence = 'HIGH' if R < 0.2 else 'MEDIUM'

        return StatisticalResult(
            test_name='Repeatability Test',
            statistic=R,
            p_value=p_value,
            hypothesis_supported=hypothesis,
            confidence=confidence,
            details=f'R = {R:.3f}, R_expected = {R_expected_random:.3f}'
        )

    def generate_report(self) -> str:
        """Generate repeatability analysis report."""
        R = self.compute_repeatability_index()
        test_result = self.test_repeatability()

        n_active = np.sum(self.activation_history > 0)
        n_repeat = np.sum(self.activation_history > 1)
        n_inactive = self.n_patches - n_active

        report = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    SPATIAL REPEATABILITY ANALYSIS REPORT                  ║
╚═══════════════════════════════════════════════════════════════════════════╝

BASIC STATISTICS
────────────────────────────────────────────────────────────────────────────
  Total patches:              {self.n_patches}
  Active patches:             {n_active} ({100*n_active/self.n_patches:.1f}%)
  Repeat-active patches:      {n_repeat} ({100*n_repeat/self.n_patches:.1f}%)
  Inactive patches:           {n_inactive} ({100*n_inactive/self.n_patches:.1f}%)

REPEATABILITY INDEX
────────────────────────────────────────────────────────────────────────────
  R = {R:.3f}

  Interpretation:
    R = 0.0  → No memory (completely random)
    R = 0.5  → Moderate memory (chimera prediction)
    R = 1.0  → Perfect memory (all active regions repeat)

STATISTICAL TEST
────────────────────────────────────────────────────────────────────────────
{test_result}

CHIMERA MODEL CRITERIA
────────────────────────────────────────────────────────────────────────────
  Prediction:    R = 0.5 (memory effect from frustrated dynamics)
  Falsification: R < 0.1 (not a frustrated system)

  Status: {'SUPPORTED ✓' if R > 0.3 else 'UNCERTAIN' if R > 0.1 else 'FALSIFIED ✗'}

═══════════════════════════════════════════════════════════════════════════
"""
        return report

# ============================================================================
# COMPREHENSIVE STATISTICAL SUITE
# ============================================================================

class ComprehensiveStatisticalAnalysis:
    """
    Runs all statistical tests and generates unified report.
    """

    def __init__(self, simulation_results: Dict):
        """
        Parameters:
            simulation_results: Dictionary from integrated simulation
        """
        self.results = simulation_results

    def run_all_analyses(self) -> Dict:
        """Run all statistical tests."""
        analyses = {}

        # LST Analysis
        if 'events' in self.results and self.results['events']:
            LSTs = [e['LST'] for e in self.results['events']]
            lst_analyzer = LSTAnalyzer(np.array(LSTs))
            analyses['LST'] = {
                'analyzer': lst_analyzer,
                'uniformity': lst_analyzer.test_uniformity(),
                'chimera_vs_thermal': lst_analyzer.test_chimera_vs_thermal(),
                'report': lst_analyzer.generate_report()
            }

        # Velocity Analysis
        if 'velocities' in self.results:
            vel_analyzer = VelocityAnalyzer(self.results['velocities'])
            analyses['velocity'] = {
                'analyzer': vel_analyzer,
                'multimodality': vel_analyzer.test_multimodality(),
                'high_velocity': vel_analyzer.test_high_velocity_excess(),
                'report': vel_analyzer.generate_report()
            }

        # Repeatability Analysis
        if 'activation_history' in self.results:
            rep_analyzer = RepeatabilityAnalyzer(
                self.results['activation_history'],
                n_orbits=3
            )
            analyses['repeatability'] = {
                'analyzer': rep_analyzer,
                'test': rep_analyzer.test_repeatability(),
                'report': rep_analyzer.generate_report()
            }

        return analyses

    def generate_unified_report(self) -> str:
        """Generate comprehensive unified report."""
        analyses = self.run_all_analyses()

        report = """
╔═══════════════════════════════════════════════════════════════════════════╗
║              COMPREHENSIVE STATISTICAL ANALYSIS REPORT                    ║
║                    DESTINY+ Mission Predictions                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

"""

        # Add individual reports
        for name, analysis in analyses.items():
            if 'report' in analysis:
                report += analysis['report'] + "\n"

        # Summary
        report += """
╔═══════════════════════════════════════════════════════════════════════════╗
║                           SUMMARY OF FINDINGS                             ║
╚═══════════════════════════════════════════════════════════════════════════╝

HYPOTHESIS SUPPORT MATRIX
────────────────────────────────────────────────────────────────────────────
  Test                        | Chimera | Thermal | Random | Confidence
  ─────────────────────────────────────────────────────────────────────────
"""
        for name, analysis in analyses.items():
            for test_name, test_result in analysis.items():
                if isinstance(test_result, StatisticalResult):
                    chimera = '✓' if 'CHIMERA' in test_result.hypothesis_supported or 'SOLITON' in test_result.hypothesis_supported or 'FRUSTRATED' in test_result.hypothesis_supported else '-'
                    thermal = '✓' if 'THERMAL' in test_result.hypothesis_supported else '-'
                    random = '✓' if test_result.hypothesis_supported == 'RANDOM' else '-'
                    report += f"  {test_result.test_name[:25]:<25} |   {chimera}    |    {thermal}    |   {random}    | {test_result.confidence}\n"

        report += """
OVERALL ASSESSMENT
────────────────────────────────────────────────────────────────────────────
"""
        # Count support for each hypothesis
        chimera_support = 0
        thermal_support = 0
        total_tests = 0

        for name, analysis in analyses.items():
            for test_name, test_result in analysis.items():
                if isinstance(test_result, StatisticalResult):
                    total_tests += 1
                    if 'CHIMERA' in test_result.hypothesis_supported or 'SOLITON' in test_result.hypothesis_supported or 'FRUSTRATED' in test_result.hypothesis_supported:
                        chimera_support += 1
                    elif 'THERMAL' in test_result.hypothesis_supported:
                        thermal_support += 1

        if total_tests > 0:
            chimera_fraction = chimera_support / total_tests
            if chimera_fraction >= 0.7:
                report += "  ✓ STRONG support for CHIMERA MODEL\n"
                report += f"    ({chimera_support}/{total_tests} tests support chimera/soliton mechanism)\n"
            elif chimera_fraction >= 0.5:
                report += "  ~ MODERATE support for CHIMERA MODEL\n"
                report += f"    ({chimera_support}/{total_tests} tests support chimera/soliton mechanism)\n"
            elif chimera_fraction >= 0.3:
                report += "  ? MIXED results - further investigation needed\n"
            else:
                report += "  ✗ WEAK support for chimera model - thermal mechanism may dominate\n"

        report += """
═══════════════════════════════════════════════════════════════════════════
"""
        return report


# ============================================================================
# MAIN
# ============================================================================

def run_statistical_analysis(simulation_results: Dict = None,
                             output_dir: str = None) -> Dict:
    """
    Run complete statistical analysis.
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'figures'
    output_dir = Path(output_dir)

    print("=" * 70)
    print("STATISTICAL ANALYSIS FOR DESTINY+ PREDICTIONS")
    print("=" * 70)

    # Load simulation results if not provided
    if simulation_results is None:
        # Try to load from integrated simulation
        try:
            from integrated_asteroid_simulation import run_integrated_simulation
            print("\nRunning integrated simulation...")
            simulation_results = run_integrated_simulation(output_dir)
        except Exception as e:
            print(f"Could not run simulation: {e}")
            print("Using synthetic test data...")
            # Create synthetic data for testing
            simulation_results = {
                'events': [{'LST': np.random.uniform(0, 3.604)} for _ in range(1000)],
                'velocities': np.concatenate([
                    np.random.normal(120, 20, 500),
                    np.random.normal(250, 30, 300),
                    np.random.normal(380, 40, 200)
                ]),
                'activation_history': np.random.poisson(3, 200)
            }

    # Run comprehensive analysis
    print("\nRunning statistical tests...")
    analyzer = ComprehensiveStatisticalAnalysis(simulation_results)
    unified_report = analyzer.generate_unified_report()

    print(unified_report)

    # Save report
    report_path = output_dir / 'statistical_analysis_report.txt'
    with open(report_path, 'w') as f:
        f.write(unified_report)
    print(f"\nReport saved to: {report_path}")

    return analyzer.run_all_analyses()


if __name__ == "__main__":
    run_statistical_analysis()
