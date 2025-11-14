#!/usr/bin/env python3
"""
UTAC β-Fit Analysis
===================

Fits the UTAC logistic model σ(β(R-Θ)) to real-world tipping point data.

Model: σ = 1 / (1 + exp(-β(R - Θ)))
Where:
  - R: Order parameter (temperature/forcing)
  - Θ: Threshold (tipping point)
  - β: Steepness parameter (key UTAC metric)
  - σ: Response (normalized 0-1)

Systems: WAIS, AMOC, Coral Reefs

Author: Claude Sonnet 4.5
Date: 2025-11-14
"""

import json
import csv
from pathlib import Path
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import linregress
import warnings

warnings.filterwarnings('ignore')


class UTACBetaFitter:
    """Fits UTAC logistic model to tipping point data."""

    def __init__(self):
        self.results = {}

    @staticmethod
    def logistic(R, beta, theta):
        """UTAC logistic function: σ(β(R-Θ))"""
        return 1.0 / (1.0 + np.exp(-beta * (R - theta)))

    @staticmethod
    def normalize_response(y, y_min=None, y_max=None):
        """Normalize response to [0, 1] range."""
        if y_min is None:
            y_min = np.min(y)
        if y_max is None:
            y_max = np.max(y)

        # Avoid division by zero
        if y_max - y_min < 1e-10:
            return np.ones_like(y) * 0.5

        return (y - y_min) / (y_max - y_min)

    @staticmethod
    def compute_aic(n, rss, k):
        """Compute AIC: 2k + n*ln(RSS/n)"""
        if rss <= 0:
            return np.inf
        return 2 * k + n * np.log(rss / n)

    def fit_system(self, R, response, system_name: str, expected_beta: float = None):
        """Fit UTAC model to a system.

        Args:
            R: Order parameter (temperature/forcing)
            response: Response variable (raw, will be normalized)
            system_name: Name of system (e.g., 'WAIS')
            expected_beta: Expected β value for initial guess

        Returns:
            dict: Fit results
        """
        # Normalize response to [0, 1]
        sigma = self.normalize_response(response)

        # Remove any NaN/Inf
        mask = np.isfinite(R) & np.isfinite(sigma)
        R_clean = R[mask]
        sigma_clean = sigma[mask]

        if len(R_clean) < 10:
            raise ValueError(f"Insufficient data for {system_name}: {len(R_clean)} points")

        # Initial parameter guess
        theta_guess = np.median(R_clean)
        beta_guess = expected_beta if expected_beta else 5.0

        try:
            # Fit logistic model
            popt, pcov = curve_fit(
                self.logistic,
                R_clean,
                sigma_clean,
                p0=[beta_guess, theta_guess],
                bounds=([0.1, R_clean.min()], [20.0, R_clean.max()]),
                maxfev=10000
            )
            beta_fit, theta_fit = popt
            beta_std, theta_std = np.sqrt(np.diag(pcov))

            # Predictions
            sigma_pred = self.logistic(R_clean, beta_fit, theta_fit)
            residuals = sigma_clean - sigma_pred
            rss_logistic = np.sum(residuals**2)

            # R² for logistic
            ss_total = np.sum((sigma_clean - np.mean(sigma_clean))**2)
            r2_logistic = 1.0 - (rss_logistic / ss_total) if ss_total > 0 else 0.0

            # Linear model comparison
            slope, intercept, r_linear, _, _ = linregress(R_clean, sigma_clean)
            sigma_pred_linear = slope * R_clean + intercept
            rss_linear = np.sum((sigma_clean - sigma_pred_linear)**2)
            r2_linear = r_linear**2

            # AIC comparison
            n = len(R_clean)
            aic_logistic = self.compute_aic(n, rss_logistic, k=2)  # 2 params: β, Θ
            aic_linear = self.compute_aic(n, rss_linear, k=2)  # 2 params: slope, intercept
            delta_aic = aic_linear - aic_logistic  # Positive = logistic better

            # Bootstrap confidence intervals (simple percentile method)
            n_bootstrap = 1000
            beta_bootstrap = []
            theta_bootstrap = []

            for _ in range(n_bootstrap):
                indices = np.random.choice(len(R_clean), size=len(R_clean), replace=True)
                R_boot = R_clean[indices]
                sigma_boot = sigma_clean[indices]

                try:
                    popt_boot, _ = curve_fit(
                        self.logistic,
                        R_boot,
                        sigma_boot,
                        p0=[beta_fit, theta_fit],
                        bounds=([0.1, R_clean.min()], [20.0, R_clean.max()]),
                        maxfev=5000
                    )
                    beta_bootstrap.append(popt_boot[0])
                    theta_bootstrap.append(popt_boot[1])
                except:
                    continue

            # Compute confidence intervals
            if len(beta_bootstrap) > 10:
                beta_ci_lower = np.percentile(beta_bootstrap, 2.5)
                beta_ci_upper = np.percentile(beta_bootstrap, 97.5)
                theta_ci_lower = np.percentile(theta_bootstrap, 2.5)
                theta_ci_upper = np.percentile(theta_bootstrap, 97.5)
            else:
                # Fallback to parameter uncertainty
                beta_ci_lower = beta_fit - 1.96 * beta_std
                beta_ci_upper = beta_fit + 1.96 * beta_std
                theta_ci_lower = theta_fit - 1.96 * theta_std
                theta_ci_upper = theta_fit + 1.96 * theta_std

            result = {
                'system': system_name,
                'n_datapoints': int(n),
                'fit_parameters': {
                    'beta': float(beta_fit),
                    'beta_std': float(beta_std),
                    'beta_ci_95': [float(beta_ci_lower), float(beta_ci_upper)],
                    'theta': float(theta_fit),
                    'theta_std': float(theta_std),
                    'theta_ci_95': [float(theta_ci_lower), float(theta_ci_upper)]
                },
                'goodness_of_fit': {
                    'r2_logistic': float(r2_logistic),
                    'r2_linear': float(r2_linear),
                    'rss_logistic': float(rss_logistic),
                    'rss_linear': float(rss_linear),
                    'aic_logistic': float(aic_logistic),
                    'aic_linear': float(aic_linear),
                    'delta_aic': float(delta_aic),
                    'logistic_preferred': bool(delta_aic > 2)  # ΔAIC > 2 = substantial support
                },
                'comparison_to_expected': {
                    'beta_expected': float(expected_beta) if expected_beta else None,
                    'beta_deviation_percent': float(100 * (beta_fit - expected_beta) / expected_beta) if expected_beta else None
                }
            }

            return result

        except Exception as e:
            raise RuntimeError(f"Fit failed for {system_name}: {e}")

    def fit_wais(self, data_path: str = None):
        """Fit WAIS data."""
        if data_path is None:
            data_path = Path(__file__).parent.parent.parent / "data" / "climate" / "wais_mass_balance_mock.csv"

        # Load data
        temp = []
        mass_balance = []

        with open(data_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                temp.append(float(row['temp_anomaly_C']))
                mass_balance.append(float(row['mass_balance_Gt']))

        R = np.array(temp)

        # Response: Invert mass balance (more negative = more ice loss = higher response)
        # Normalize to [0, 1] where 0 = initial state, 1 = maximum loss
        response = -np.array(mass_balance)  # Make positive (loss increases)

        result = self.fit_system(R, response, 'WAIS', expected_beta=13.5)
        self.results['WAIS'] = result
        return result

    def fit_amoc(self, data_path: str = None):
        """Fit AMOC data."""
        if data_path is None:
            data_path = Path(__file__).parent.parent.parent / "data" / "ocean" / "amoc_strength_mock.csv"

        # Load data
        temp = []
        strength = []

        with open(data_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                temp.append(float(row['temp_anomaly_C']))
                strength.append(float(row['strength_Sv']))

        R = np.array(temp)

        # Response: Invert strength (weaker AMOC = higher response toward tipping)
        response = 20.0 - np.array(strength)  # Invert (higher = more weakened)

        result = self.fit_system(R, response, 'AMOC', expected_beta=10.2)
        self.results['AMOC'] = result
        return result

    def fit_coral(self, data_path: str = None):
        """Fit Coral data."""
        if data_path is None:
            data_path = Path(__file__).parent.parent.parent / "data" / "biology" / "coral_bleaching_global_mock.csv"

        # Load data
        sst = []
        bleaching = []

        with open(data_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sst.append(float(row['sst_anomaly_C']))
                bleaching.append(float(row['bleaching_percent']))

        R = np.array(sst)
        response = np.array(bleaching)  # Already in correct direction

        result = self.fit_system(R, response, 'Coral', expected_beta=7.5)
        self.results['Coral'] = result
        return result

    def export_results(self, output_path: str = None):
        """Export all fit results as JSON."""
        if output_path is None:
            output_path = Path(__file__).parent / "results" / "beta_fits_v3.json"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        export = {
            'metadata': {
                'analysis': 'UTAC β-Fit',
                'model': 'σ(β(R-Θ)) = 1/(1 + exp(-β(R-Θ)))',
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

    parser = argparse.ArgumentParser(description='UTAC β-Fit Analysis')
    parser.add_argument('--system', type=str, choices=['wais', 'amoc', 'coral', 'all'], default='all',
                        help='Which system to fit')
    parser.add_argument('--output', type=str, help='Output JSON path')

    args = parser.parse_args()

    fitter = UTACBetaFitter()

    print("🔬 UTAC β-Fit Analysis")
    print("=" * 60)

    if args.system in ['wais', 'all']:
        print("\n📊 Fitting WAIS...")
        result = fitter.fit_wais()
        print(f"   β = {result['fit_parameters']['beta']:.2f} ± {result['fit_parameters']['beta_std']:.2f}")
        print(f"   Θ = {result['fit_parameters']['theta']:.2f}°C ± {result['fit_parameters']['theta_std']:.2f}")
        print(f"   R² = {result['goodness_of_fit']['r2_logistic']:.4f}")
        print(f"   ΔAIC = {result['goodness_of_fit']['delta_aic']:.1f} (vs linear)")

    if args.system in ['amoc', 'all']:
        print("\n📊 Fitting AMOC...")
        result = fitter.fit_amoc()
        print(f"   β = {result['fit_parameters']['beta']:.2f} ± {result['fit_parameters']['beta_std']:.2f}")
        print(f"   Θ = {result['fit_parameters']['theta']:.2f}°C ± {result['fit_parameters']['theta_std']:.2f}")
        print(f"   R² = {result['goodness_of_fit']['r2_logistic']:.4f}")
        print(f"   ΔAIC = {result['goodness_of_fit']['delta_aic']:.1f} (vs linear)")

    if args.system in ['coral', 'all']:
        print("\n📊 Fitting Coral...")
        result = fitter.fit_coral()
        print(f"   β = {result['fit_parameters']['beta']:.2f} ± {result['fit_parameters']['beta_std']:.2f}")
        print(f"   Θ = {result['fit_parameters']['theta']:.2f}°C ± {result['fit_parameters']['theta_std']:.2f}")
        print(f"   R² = {result['goodness_of_fit']['r2_logistic']:.4f}")
        print(f"   ΔAIC = {result['goodness_of_fit']['delta_aic']:.1f} (vs linear)")

    # Export
    output_path = fitter.export_results(output_path=args.output)
    print(f"\n✅ Results exported to {output_path}")


if __name__ == '__main__':
    main()
