#!/usr/bin/env python3
"""
OISST Coral Bleaching Adapter (Mock Version)
============================================

Adapter for global coral reef bleaching data.

**Mock Version:** Reads generated CSV mock data
**Production Version:** Would connect to NOAA Coral Reef Watch / OISST

Data Source: NOAA Coral Reef Watch, OISST v2.1
Papers: Lenton et al. (2025) Global Tipping Points Report, Hughes et al. (2018)

Author: Claude Sonnet 4.5
Date: 2025-11-14
"""

import json
import csv
from datetime import datetime
from pathlib import Path
import numpy as np


class OISSTCoralAdapter:
    """Mock adapter for OISST Coral bleaching data."""

    def __init__(self, mock_data_path: str = None):
        """Initialize adapter.

        Args:
            mock_data_path: Path to mock CSV file
        """
        if mock_data_path is None:
            mock_data_path = Path(__file__).parent.parent.parent / "data" / "biology" / "coral_bleaching_global_mock.csv"

        self.data_path = Path(mock_data_path)

        if not self.data_path.exists():
            raise FileNotFoundError(f"Mock data not found: {self.data_path}")

    def load_data(self):
        """Load coral bleaching data from CSV.

        Returns:
            dict: Parsed data with metadata
        """
        data = {
            'years': [],
            'bleaching_percent': [],
            'dhw_degree_heating_weeks': [],
            'sst_anomaly_C': [],
            'distance_to_tipping': []
        }

        with open(self.data_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data['years'].append(int(row['year']))
                data['bleaching_percent'].append(float(row['bleaching_percent']))
                data['dhw_degree_heating_weeks'].append(float(row['dhw_degree_heating_weeks']))
                data['sst_anomaly_C'].append(float(row['sst_anomaly_C']))
                data['distance_to_tipping'].append(float(row['distance_to_tipping']))

        return data

    def compute_statistics(self, data: dict) -> dict:
        """Compute summary statistics for coral bleaching data.

        Args:
            data: Loaded data from load_data()

        Returns:
            dict: Statistics summary
        """
        years = np.array(data['years'])
        bleaching = np.array(data['bleaching_percent'])
        dhw = np.array(data['dhw_degree_heating_weeks'])
        sst = np.array(data['sst_anomaly_C'])
        distance = np.array(data['distance_to_tipping'])

        # Current values (most recent)
        current_bleaching = bleaching[-1]
        current_dhw = dhw[-1]
        current_sst = sst[-1]
        current_distance = distance[-1]

        # Trends
        # Split into early (1980-1995) and late (2010-2024) periods
        n_total = len(bleaching)
        early_end = int(n_total * 0.35)  # ~15 years
        late_start = int(n_total * 0.67)  # ~30 years

        early_bleaching = np.mean(bleaching[:early_end])
        late_bleaching = np.mean(bleaching[late_start:])
        bleaching_increase_percent = ((late_bleaching - early_bleaching) / early_bleaching) * 100

        early_dhw = np.mean(dhw[:early_end])
        late_dhw = np.mean(dhw[late_start:])
        dhw_increase_percent = ((late_dhw - early_dhw) / early_dhw) * 100

        # Mass bleaching events (> 50% threshold)
        mass_bleaching_years = years[bleaching > 50.0].tolist()
        mass_bleaching_count = len(mass_bleaching_years)

        # Acceleration (linear trend in bleaching rate)
        time_decades = (years - years[0]) / 10.0
        bleaching_trend = np.polyfit(time_decades, bleaching, 1)[0]  # % per decade

        # Tipping point detection
        tipped = bool(current_bleaching >= 99.0 or current_distance <= 0.01)
        pre_tipping = bool(50.0 <= current_bleaching < 99.0)

        stats = {
            'n_datapoints': len(bleaching),
            'date_range': {
                'start': int(years[0]),
                'end': int(years[-1])
            },
            'current_state': {
                'bleaching_percent': float(current_bleaching),
                'dhw_degree_heating_weeks': float(current_dhw),
                'sst_anomaly_C': float(current_sst),
                'distance_to_tipping': float(current_distance)
            },
            'historical_trends': {
                'bleaching_early_period_percent': float(early_bleaching),
                'bleaching_late_period_percent': float(late_bleaching),
                'bleaching_increase_percent': float(bleaching_increase_percent),
                'dhw_early_period': float(early_dhw),
                'dhw_late_period': float(late_dhw),
                'dhw_increase_percent': float(dhw_increase_percent),
                'bleaching_rate_percent_per_decade': float(bleaching_trend)
            },
            'mass_bleaching_events': {
                'count': int(mass_bleaching_count),
                'years': [int(y) for y in mass_bleaching_years],
                'first_event': int(mass_bleaching_years[0]) if mass_bleaching_count > 0 else None
            },
            'tipping_assessment': {
                'status': 'TIPPED' if tipped else ('PRE_TIPPING' if pre_tipping else 'STABLE'),
                'tipped': bool(tipped),
                'pre_tipping': bool(pre_tipping),
                'threshold_exceeded': bool(current_bleaching >= 84.0),  # 84% = 4th global event threshold
                'heat_stress_critical': bool(current_dhw >= 8.0)  # DHW > 8 = severe bleaching
            },
            'thresholds': {
                'bleaching_moderate': 30.0,
                'bleaching_severe': 50.0,
                'bleaching_mass_event': 84.0,
                'dhw_mild_stress': 4.0,
                'dhw_severe_stress': 8.0,
                'sst_anomaly_danger': 1.0
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
            output_path = Path(__file__).parent.parent / "analysis" / "results" / "coral_adapter_output.json"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = self.load_data()
        stats = self.compute_statistics(data)

        export = {
            'metadata': {
                'system': 'Coral Reefs',
                'system_full_name': 'Global Coral Reef Bleaching',
                'utac_type': 'Type-2/3: Thermo/Electrochemical',
                'beta_expected': 7.5,
                'theta_expected_C': 1.0,
                'status': stats['tipping_assessment']['status'],
                'data_source': 'Mock (NOAA Coral Reef Watch based)',
                'adapter_version': '1.0.0',
                'generated': datetime.now().isoformat() + 'Z',
                'papers': [
                    'Lenton et al. (2025) Global Tipping Points Report',
                    'Hughes et al. (2018) Nature',
                    'NOAA Coral Reef Watch'
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

    parser = argparse.ArgumentParser(description='OISST Coral Adapter (Mock)')
    parser.add_argument('--input', type=str, help='Input CSV path (default: data/biology/coral_bleaching_global_mock.csv)')
    parser.add_argument('--output', type=str, help='Output JSON path (default: analysis/results/coral_adapter_output.json)')

    args = parser.parse_args()

    adapter = OISSTCoralAdapter(mock_data_path=args.input)
    output_path = adapter.export_json(output_path=args.output)

    print(f"✅ OISST Coral Adapter: Data exported to {output_path}")

    # Print summary
    data = adapter.load_data()
    stats = adapter.compute_statistics(data)

    print(f"\n📊 Summary:")
    print(f"   Datapoints: {stats['n_datapoints']}")
    print(f"   Date Range: {stats['date_range']['start']} → {stats['date_range']['end']}")
    print(f"   Current Bleaching: {stats['current_state']['bleaching_percent']:.1f}%")
    print(f"   Bleaching Increase: {stats['historical_trends']['bleaching_increase_percent']:.1f}%")
    print(f"   Mass Bleaching Events: {stats['mass_bleaching_events']['count']}")
    print(f"   First Mass Event: {stats['mass_bleaching_events']['first_event']}")
    print(f"   Current DHW: {stats['current_state']['dhw_degree_heating_weeks']:.1f} weeks")
    print(f"   Status: {stats['tipping_assessment']['status']}")
    print(f"   Tipped: {'🔴 YES' if stats['tipping_assessment']['tipped'] else '🟢 NO'}")
    print(f"   Distance to Tipping: {stats['current_state']['distance_to_tipping']:.1%}")


if __name__ == '__main__':
    main()
