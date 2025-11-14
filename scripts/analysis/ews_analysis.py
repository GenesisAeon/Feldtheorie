#!/usr/bin/env python3
"""
Early Warning Signals (EWS) Analysis
====================================

Computes Early Warning Signals for critical transitions in tipping point systems.

EWS Metrics:
  - Variance (sliding window)
  - AR(1) autocorrelation (sliding window)
  - Spectral reddening (low-freq power increase)
  - Kendall τ trend detection

Systems: WAIS, AMOC, Coral Reefs

References:
  - Scheffer et al. (2009) Nature
  - Dakos et al. (2012) PLoS ONE
  - Lenton et al. (2012) Phil Trans R Soc A

Author: Claude Sonnet 4.5
Date: 2025-11-14
"""

import json
import csv
from pathlib import Path
import numpy as np
from scipy import stats, signal
import warnings

warnings.filterwarnings('ignore')


class EWSAnalyzer:
    """Compute Early Warning Signals for tipping point systems."""

    def __init__(self, window_size: int = None):
        """Initialize EWS analyzer.

        Args:
            window_size: Rolling window size (default: 50% of data)
        """
        self.window_size = window_size
        self.results = {}

    @staticmethod
    def detrend_data(y):
        """Detrend data using linear regression."""
        x = np.arange(len(y))
        slope, intercept = np.polyfit(x, y, 1)
        trend = slope * x + intercept
        return y - trend, trend

    @staticmethod
    def compute_ar1(y):
        """Compute AR(1) autocorrelation coefficient."""
        if len(y) < 2:
            return np.nan

        # Lag-1 autocorrelation
        y_mean = np.mean(y)
        numerator = np.sum((y[:-1] - y_mean) * (y[1:] - y_mean))
        denominator = np.sum((y - y_mean)**2)

        if denominator == 0:
            return np.nan

        return numerator / denominator

    @staticmethod
    def compute_variance(y):
        """Compute variance."""
        return np.var(y, ddof=1)

    @staticmethod
    def rolling_window_metric(y, window_size, metric_func):
        """Compute metric in rolling windows.

        Args:
            y: Time series
            window_size: Window size
            metric_func: Function to compute metric (e.g., np.var, compute_ar1)

        Returns:
            Array of metric values (one per window)
        """
        n = len(y)
        if window_size > n:
            window_size = n // 2

        n_windows = n - window_size + 1
        metrics = np.zeros(n_windows)

        for i in range(n_windows):
            window = y[i:i + window_size]
            metrics[i] = metric_func(window)

        return metrics

    @staticmethod
    def compute_spectral_reddening(y, sampling_rate=1.0):
        """Compute spectral reddening (increase in low-frequency power).

        Args:
            y: Time series
            sampling_rate: Sampling rate (Hz)

        Returns:
            dict: Spectral metrics
        """
        # Detrend
        y_detrended = signal.detrend(y)

        # Compute power spectral density
        freqs, psd = signal.periodogram(y_detrended, fs=sampling_rate)

        # Split into low and high frequency bands
        # Low: bottom 20%, High: top 20%
        n_freqs = len(freqs)
        low_idx = int(n_freqs * 0.2)
        high_idx = int(n_freqs * 0.8)

        low_power = np.mean(psd[1:low_idx])  # Skip DC component
        high_power = np.mean(psd[high_idx:])

        # Reddening ratio (higher = more low-frequency power)
        reddening_ratio = low_power / high_power if high_power > 0 else np.nan

        return {
            'low_freq_power': float(low_power),
            'high_freq_power': float(high_power),
            'reddening_ratio': float(reddening_ratio)
        }

    @staticmethod
    def kendall_tau_trend(y):
        """Compute Kendall τ for trend detection.

        Returns:
            dict: τ coefficient and p-value
        """
        x = np.arange(len(y))
        tau, p_value = stats.kendalltau(x, y)

        return {
            'tau': float(tau),
            'p_value': float(p_value),
            'significant': bool(p_value < 0.05)
        }

    def analyze_timeseries(self, y, system_name: str, detrend: bool = True):
        """Analyze time series for Early Warning Signals.

        Args:
            y: Time series data
            system_name: Name of system
            detrend: Whether to detrend before computing EWS

        Returns:
            dict: EWS analysis results
        """
        y = np.array(y)

        # Remove NaN/Inf
        y = y[np.isfinite(y)]

        if len(y) < 20:
            raise ValueError(f"Insufficient data for {system_name}: {len(y)} points")

        # Set window size if not specified
        window_size = self.window_size if self.window_size else max(20, len(y) // 2)

        # Detrend
        if detrend:
            y_detrended, trend = self.detrend_data(y)
        else:
            y_detrended = y
            trend = np.zeros_like(y)

        # Rolling window metrics
        variance_rolling = self.rolling_window_metric(y_detrended, window_size, self.compute_variance)
        ar1_rolling = self.rolling_window_metric(y_detrended, window_size, self.compute_ar1)

        # Trend in EWS (Kendall τ)
        variance_trend = self.kendall_tau_trend(variance_rolling)
        ar1_trend = self.kendall_tau_trend(ar1_rolling)

        # Spectral analysis
        spectral = self.compute_spectral_reddening(y_detrended)

        # Summary statistics
        early_period_size = len(variance_rolling) // 3
        late_period_start = (2 * len(variance_rolling)) // 3

        variance_early = np.mean(variance_rolling[:early_period_size])
        variance_late = np.mean(variance_rolling[late_period_start:])
        variance_increase = ((variance_late - variance_early) / variance_early * 100) if variance_early > 0 else 0.0

        ar1_early = np.mean(ar1_rolling[:early_period_size])
        ar1_late = np.mean(ar1_rolling[late_period_start:])
        ar1_increase = ((ar1_late - ar1_early) / ar1_early * 100) if ar1_early > 0 else 0.0

        result = {
            'system': system_name,
            'n_datapoints': int(len(y)),
            'window_size': int(window_size),
            'detrended': bool(detrend),
            'variance_ews': {
                'rolling_values': variance_rolling.tolist(),
                'trend': variance_trend,
                'early_period_mean': float(variance_early),
                'late_period_mean': float(variance_late),
                'increase_percent': float(variance_increase)
            },
            'ar1_ews': {
                'rolling_values': ar1_rolling.tolist(),
                'trend': ar1_trend,
                'early_period_mean': float(ar1_early),
                'late_period_mean': float(ar1_late),
                'increase_percent': float(ar1_increase)
            },
            'spectral_ews': spectral,
            'critical_slowing_detected': bool(
                ar1_trend['significant'] and ar1_trend['tau'] > 0.3 and
                variance_trend['significant'] and variance_trend['tau'] > 0.3
            )
        }

        return result

    def analyze_wais(self, data_path: str = None):
        """Analyze WAIS EWS."""
        if data_path is None:
            data_path = Path(__file__).parent.parent.parent / "data" / "climate" / "wais_mass_balance_mock.csv"

        # Load mass change rate (more sensitive to critical slowing)
        mass_rate = []

        with open(data_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                mass_rate.append(float(row['mass_change_rate_Gt_per_year']))

        result = self.analyze_timeseries(mass_rate, 'WAIS', detrend=True)
        self.results['WAIS'] = result
        return result

    def analyze_amoc(self, data_path: str = None):
        """Analyze AMOC EWS."""
        if data_path is None:
            data_path = Path(__file__).parent.parent.parent / "data" / "ocean" / "amoc_strength_mock.csv"

        # Load AMOC strength
        strength = []

        with open(data_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                strength.append(float(row['strength_Sv']))

        result = self.analyze_timeseries(strength, 'AMOC', detrend=True)
        self.results['AMOC'] = result
        return result

    def analyze_coral(self, data_path: str = None):
        """Analyze Coral EWS."""
        if data_path is None:
            data_path = Path(__file__).parent.parent.parent / "data" / "biology" / "coral_bleaching_global_mock.csv"

        # Load bleaching percent
        bleaching = []

        with open(data_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                bleaching.append(float(row['bleaching_percent']))

        result = self.analyze_timeseries(bleaching, 'Coral', detrend=False)  # Already monotonic
        self.results['Coral'] = result
        return result

    def export_results(self, output_path: str = None):
        """Export EWS results as JSON."""
        if output_path is None:
            output_path = Path(__file__).parent / "results" / "ews_analysis_v3.json"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        export = {
            'metadata': {
                'analysis': 'Early Warning Signals (EWS)',
                'metrics': ['Variance', 'AR(1)', 'Spectral Reddening', 'Kendall τ'],
                'version': '1.0.0',
                'generated': np.datetime64('now').astype(str) + 'Z'
            },
            'systems': self.results
        }

        with open(output_path, 'w') as f:
            json.dump(export, f, indent=2)

        return str(output_path)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Early Warning Signals Analysis')
    parser.add_argument('--system', type=str, choices=['wais', 'amoc', 'coral', 'all'], default='all')
    parser.add_argument('--window', type=int, help='Window size for rolling metrics')
    parser.add_argument('--output', type=str, help='Output JSON path')

    args = parser.parse_args()

    analyzer = EWSAnalyzer(window_size=args.window)

    print("⚠️  Early Warning Signals Analysis")
    print("=" * 60)

    if args.system in ['wais', 'all']:
        print("\n📊 Analyzing WAIS...")
        result = analyzer.analyze_wais()
        print(f"   Variance increase: {result['variance_ews']['increase_percent']:.1f}%")
        print(f"   AR(1) increase: {result['ar1_ews']['increase_percent']:.1f}%")
        print(f"   Variance trend τ: {result['variance_ews']['trend']['tau']:.3f} (p={result['variance_ews']['trend']['p_value']:.4f})")
        print(f"   AR(1) trend τ: {result['ar1_ews']['trend']['tau']:.3f} (p={result['ar1_ews']['trend']['p_value']:.4f})")
        print(f"   Spectral reddening: {result['spectral_ews']['reddening_ratio']:.2f}")
        print(f"   Critical slowing: {'🔴 YES' if result['critical_slowing_detected'] else '🟢 NO'}")

    if args.system in ['amoc', 'all']:
        print("\n📊 Analyzing AMOC...")
        result = analyzer.analyze_amoc()
        print(f"   Variance increase: {result['variance_ews']['increase_percent']:.1f}%")
        print(f"   AR(1) increase: {result['ar1_ews']['increase_percent']:.1f}%")
        print(f"   Variance trend τ: {result['variance_ews']['trend']['tau']:.3f} (p={result['variance_ews']['trend']['p_value']:.4f})")
        print(f"   AR(1) trend τ: {result['ar1_ews']['trend']['tau']:.3f} (p={result['ar1_ews']['trend']['p_value']:.4f})")
        print(f"   Spectral reddening: {result['spectral_ews']['reddening_ratio']:.2f}")
        print(f"   Critical slowing: {'🔴 YES' if result['critical_slowing_detected'] else '🟢 NO'}")

    if args.system in ['coral', 'all']:
        print("\n📊 Analyzing Coral...")
        result = analyzer.analyze_coral()
        print(f"   Variance increase: {result['variance_ews']['increase_percent']:.1f}%")
        print(f"   AR(1) increase: {result['ar1_ews']['increase_percent']:.1f}%")
        print(f"   Variance trend τ: {result['variance_ews']['trend']['tau']:.3f} (p={result['variance_ews']['trend']['p_value']:.4f})")
        print(f"   AR(1) trend τ: {result['ar1_ews']['trend']['tau']:.3f} (p={result['ar1_ews']['trend']['p_value']:.4f})")
        print(f"   Spectral reddening: {result['spectral_ews']['reddening_ratio']:.2f}")
        print(f"   Critical slowing: {'🔴 YES' if result['critical_slowing_detected'] else '🟢 NO'}")

    # Export
    output_path = analyzer.export_results(output_path=args.output)
    print(f"\n✅ Results exported to {output_path}")


if __name__ == '__main__':
    main()
