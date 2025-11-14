#!/usr/bin/env python3
"""
GRACE WAIS Adapter (Mock Version)
==================================

Adapter for GRACE/GRACE-FO ice mass balance data for West Antarctic Ice Sheet.

**Mock Version:** Reads generated CSV mock data
**Production Version:** Would connect to NASA Earthdata API

Data Source: NASA JPL GRACE Tellus (https://grace.jpl.nasa.gov/)
Papers: TiPACCs (2024), Armstrong-McKay et al. (2022) Science

Author: Claude Sonnet 4.5
Date: 2025-11-14
"""

import json
import csv
from datetime import datetime
from pathlib import Path
import numpy as np


class GRACEWAISAdapter:
    """Mock adapter for GRACE WAIS data."""

    def __init__(self, mock_data_path: str = None):
        """Initialize adapter.

        Args:
            mock_data_path: Path to mock CSV file
        """
        if mock_data_path is None:
            mock_data_path = Path(__file__).parent.parent.parent / "data" / "climate" / "wais_mass_balance_mock.csv"

        self.data_path = Path(mock_data_path)

        if not self.data_path.exists():
            raise FileNotFoundError(f"Mock data not found: {self.data_path}")

    def load_data(self):
        """Load WAIS mass balance data from CSV.

        Returns:
            dict: Parsed data with metadata
        """
        data = {
            'dates': [],
            'mass_balance_Gt': [],
            'mass_change_rate_Gt_per_year': [],
            'temp_anomaly_C': [],
            'distance_to_tipping': [],
            'variance_indicator': [],
            'ar1_coefficient': []
        }

        with open(self.data_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data['dates'].append(row['date'])
                data['mass_balance_Gt'].append(float(row['mass_balance_Gt']))
                data['mass_change_rate_Gt_per_year'].append(float(row['mass_change_rate_Gt_per_year']))
                data['temp_anomaly_C'].append(float(row['temp_anomaly_C']))
                data['distance_to_tipping'].append(float(row['distance_to_tipping']))
                data['variance_indicator'].append(float(row['variance_indicator']))
                data['ar1_coefficient'].append(float(row['ar1_coefficient']))

        return data

    def compute_statistics(self, data: dict) -> dict:
        """Compute summary statistics for WAIS data.

        Args:
            data: Loaded data from load_data()

        Returns:
            dict: Statistics summary
        """
        mass_balance = np.array(data['mass_balance_Gt'])
        mass_rate = np.array(data['mass_change_rate_Gt_per_year'])
        temp = np.array(data['temp_anomaly_C'])
        ar1 = np.array(data['ar1_coefficient'])
        variance = np.array(data['variance_indicator'])

        # Current values (most recent)
        current_mass = mass_balance[-1]
        current_rate = mass_rate[-1]
        current_temp = temp[-1]
        current_ar1 = ar1[-1]
        current_variance = variance[-1]

        # Trends
        # Split into early (2002-2010) and late (2020-2024) periods
        n_total = len(mass_balance)
        early_end = int(n_total * 0.35)  # ~8 years
        late_start = int(n_total * 0.80)  # ~18 years

        early_ar1 = np.mean(ar1[:early_end])
        late_ar1 = np.mean(ar1[late_start:])
        ar1_increase_percent = ((late_ar1 - early_ar1) / early_ar1) * 100

        early_var = np.mean(variance[:early_end])
        late_var = np.mean(variance[late_start:])
        variance_increase_percent = ((late_var - early_var) / early_var) * 100

        stats = {
            'n_datapoints': len(mass_balance),
            'date_range': {
                'start': data['dates'][0],
                'end': data['dates'][-1]
            },
            'current_state': {
                'mass_balance_Gt': float(current_mass),
                'mass_loss_rate_Gt_per_year': float(current_rate),
                'temperature_anomaly_C': float(current_temp),
                'distance_to_tipping': float(data['distance_to_tipping'][-1]),
                'ar1_coefficient': float(current_ar1),
                'variance_factor': float(current_variance)
            },
            'early_warning_signals': {
                'ar1_early_period': float(early_ar1),
                'ar1_late_period': float(late_ar1),
                'ar1_increase_percent': float(ar1_increase_percent),
                'variance_early_period': float(early_var),
                'variance_late_period': float(late_var),
                'variance_increase_percent': float(variance_increase_percent),
                'critical_slowing': bool(late_ar1 > 0.70)  # Threshold for critical slowing
            },
            'trends': {
                'total_mass_change_Gt': float(mass_balance[-1] - mass_balance[0]),
                'mean_annual_loss_rate_Gt_per_year': float(np.mean(mass_rate)),
                'accelerating': bool(np.polyfit(range(len(mass_rate)), mass_rate, 1)[0] < 0)  # Negative trend = accelerating loss
            }
        }

        return stats

    def export_json(self, output_path: str = None) -> str:
        """Export data and statistics as JSON for TypeScript consumption.

        Args:
            output_path: Path for JSON output

        Returns:
            str: Path to exported JSON
        """
        if output_path is None:
            output_path = Path(__file__).parent.parent / "analysis" / "results" / "wais_adapter_output.json"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = self.load_data()
        stats = self.compute_statistics(data)

        export = {
            'metadata': {
                'system': 'WAIS',
                'system_full_name': 'West Antarctic Ice Sheet',
                'utac_type': 'Type-2: Thermodynamic',
                'beta_expected': 13.5,
                'theta_expected_C': 1.5,
                'status': 'AT_TIPPING',
                'data_source': 'Mock (GRACE/GRACE-FO based)',
                'adapter_version': '1.0.0',
                'generated': datetime.now().isoformat() + 'Z',
                'papers': [
                    'TiPACCs Project (2024) CORDIS 820575',
                    'Armstrong-McKay et al. (2022) Science 377(6611)'
                ]
            },
            'data': data,
            'statistics': stats
        }

        with open(output_path, 'w') as f:
            json.dump(export, f, indent=2)

        return str(output_path)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='GRACE WAIS Adapter (Mock)')
    parser.add_argument('--input', type=str, help='Input CSV path (default: data/climate/wais_mass_balance_mock.csv)')
    parser.add_argument('--output', type=str, help='Output JSON path (default: analysis/results/wais_adapter_output.json)')

    args = parser.parse_args()

    adapter = GRACEWAISAdapter(mock_data_path=args.input)
    output_path = adapter.export_json(output_path=args.output)

    print(f"✅ GRACE WAIS Adapter: Data exported to {output_path}")

    # Print summary
    data = adapter.load_data()
    stats = adapter.compute_statistics(data)

    print(f"\n📊 Summary:")
    print(f"   Datapoints: {stats['n_datapoints']}")
    print(f"   Date Range: {stats['date_range']['start']} → {stats['date_range']['end']}")
    print(f"   Current Mass Loss Rate: {stats['current_state']['mass_loss_rate_Gt_per_year']:.1f} Gt/year")
    print(f"   AR(1) Coefficient: {stats['current_state']['ar1_coefficient']:.3f}")
    print(f"   AR(1) Increase: {stats['early_warning_signals']['ar1_increase_percent']:.1f}%")
    print(f"   Variance Increase: {stats['early_warning_signals']['variance_increase_percent']:.1f}%")
    print(f"   Critical Slowing: {'🔴 YES' if stats['early_warning_signals']['critical_slowing'] else '🟢 NO'}")
    print(f"   Distance to Tipping: {stats['current_state']['distance_to_tipping']:.1%}")


if __name__ == '__main__':
    main()
