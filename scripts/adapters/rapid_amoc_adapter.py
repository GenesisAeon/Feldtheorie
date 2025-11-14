#!/usr/bin/env python3
"""
RAPID AMOC Adapter (Mock Version)
==================================

Adapter for AMOC (Atlantic Meridional Overturning Circulation) strength data.

**Mock Version:** Reads generated CSV mock data
**Production Version:** Would connect to RAPID-MOCHA/CMIP6 APIs

Data Source: RAPID-MOCHA Array, van Westen (2024)
Papers: van Westen et al. (2024) Science Advances, Ditlevsen & Ditlevsen (2023)

Author: Claude Sonnet 4.5
Date: 2025-11-14
"""

import json
import csv
from datetime import datetime
from pathlib import Path
import numpy as np


class RAPIDAMOCAdapter:
    """Mock adapter for RAPID AMOC data."""

    def __init__(self, mock_data_path: str = None):
        """Initialize adapter.

        Args:
            mock_data_path: Path to mock CSV file
        """
        if mock_data_path is None:
            mock_data_path = Path(__file__).parent.parent.parent / "data" / "ocean" / "amoc_strength_mock.csv"

        self.data_path = Path(mock_data_path)

        if not self.data_path.exists():
            raise FileNotFoundError(f"Mock data not found: {self.data_path}")

    def load_data(self):
        """Load AMOC strength data from CSV.

        Returns:
            dict: Parsed data with metadata
        """
        data = {
            'dates': [],
            'strength_Sv': [],
            'fovs_indicator': [],
            'cold_blob_sst_anomaly_C': [],
            'greenland_meltwater_Sv': [],
            'temp_anomaly_C': [],
            'distance_to_tipping': [],
            'ar1_coefficient': []
        }

        with open(self.data_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data['dates'].append(row['date'])
                data['strength_Sv'].append(float(row['strength_Sv']))
                data['fovs_indicator'].append(float(row['fovs_indicator']))
                data['cold_blob_sst_anomaly_C'].append(float(row['cold_blob_sst_anomaly_C']))
                data['greenland_meltwater_Sv'].append(float(row['greenland_meltwater_Sv']))
                data['temp_anomaly_C'].append(float(row['temp_anomaly_C']))
                data['distance_to_tipping'].append(float(row['distance_to_tipping']))
                data['ar1_coefficient'].append(float(row['ar1_coefficient']))

        return data

    def compute_statistics(self, data: dict) -> dict:
        """Compute summary statistics for AMOC data.

        Args:
            data: Loaded data from load_data()

        Returns:
            dict: Statistics summary
        """
        strength = np.array(data['strength_Sv'])
        fovs = np.array(data['fovs_indicator'])
        cold_blob = np.array(data['cold_blob_sst_anomaly_C'])
        meltwater = np.array(data['greenland_meltwater_Sv'])
        temp = np.array(data['temp_anomaly_C'])
        ar1 = np.array(data['ar1_coefficient'])

        # Current values (most recent)
        current_strength = strength[-1]
        current_fovs = fovs[-1]
        current_cold_blob = cold_blob[-1]
        current_meltwater = meltwater[-1]
        current_temp = temp[-1]
        current_ar1 = ar1[-1]

        # Trends
        # Split into early (2004-2010) and late (2020-2024) periods
        n_total = len(strength)
        early_end = int(n_total * 0.30)  # ~6 years
        late_start = int(n_total * 0.80)  # ~16 years

        early_ar1 = np.mean(ar1[:early_end])
        late_ar1 = np.mean(ar1[late_start:])
        ar1_increase_percent = ((late_ar1 - early_ar1) / early_ar1) * 100

        early_strength = np.mean(strength[:early_end])
        late_strength = np.mean(strength[late_start:])
        strength_decline_percent = ((late_strength - early_strength) / early_strength) * 100

        # FovS crossing detection (critical tipping signal!)
        fovs_crossings = np.where(np.diff(np.sign(fovs)))[0]
        fovs_crossed_zero = bool(len(fovs_crossings) > 0 and fovs[-1] > 0)

        # Weakening rate (linear trend)
        years = np.arange(len(strength)) / 36.5  # ~36.5 datapoints per year (10-day intervals)
        strength_trend = np.polyfit(years, strength, 1)[0]  # Sv per year

        stats = {
            'n_datapoints': len(strength),
            'date_range': {
                'start': data['dates'][0],
                'end': data['dates'][-1]
            },
            'current_state': {
                'strength_Sv': float(current_strength),
                'fovs_indicator': float(current_fovs),
                'cold_blob_sst_anomaly_C': float(current_cold_blob),
                'greenland_meltwater_Sv': float(current_meltwater),
                'temperature_anomaly_C': float(current_temp),
                'distance_to_tipping': float(data['distance_to_tipping'][-1]),
                'ar1_coefficient': float(current_ar1)
            },
            'early_warning_signals': {
                'ar1_early_period': float(early_ar1),
                'ar1_late_period': float(late_ar1),
                'ar1_increase_percent': float(ar1_increase_percent),
                'fovs_crossed_zero': bool(fovs_crossed_zero),
                'fovs_crossing_count': int(len(fovs_crossings)),
                'critical_slowing': bool(late_ar1 > 0.70)  # AR(1) threshold
            },
            'trends': {
                'strength_early_period_Sv': float(early_strength),
                'strength_late_period_Sv': float(late_strength),
                'strength_decline_percent': float(strength_decline_percent),
                'weakening_rate_Sv_per_year': float(strength_trend),
                'weakening_accelerating': bool(strength_trend < -0.05)  # Threshold: -0.05 Sv/year
            },
            'tipping_indicators': {
                'fovs_positive': bool(current_fovs > 0),
                'cold_blob_present': bool(current_cold_blob < -0.5),  # Cold blob = SST < -0.5°C
                'high_meltwater': bool(current_meltwater > 0.08),  # Threshold from papers
                'status': 'TIPPED' if fovs_crossed_zero else 'WEAKENING'
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
            output_path = Path(__file__).parent.parent / "analysis" / "results" / "amoc_adapter_output.json"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = self.load_data()
        stats = self.compute_statistics(data)

        export = {
            'metadata': {
                'system': 'AMOC',
                'system_full_name': 'Atlantic Meridional Overturning Circulation',
                'utac_type': 'Type-2: Thermodynamic (Bistable)',
                'beta_expected': 10.2,
                'theta_expected_C': 4.0,
                'status': stats['tipping_indicators']['status'],
                'data_source': 'Mock (RAPID-MOCHA based)',
                'adapter_version': '1.0.0',
                'generated': datetime.now().isoformat() + 'Z',
                'papers': [
                    'van Westen et al. (2024) Science Advances',
                    'Ditlevsen & Ditlevsen (2023) Nature Communications'
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

    parser = argparse.ArgumentParser(description='RAPID AMOC Adapter (Mock)')
    parser.add_argument('--input', type=str, help='Input CSV path (default: data/ocean/amoc_strength_mock.csv)')
    parser.add_argument('--output', type=str, help='Output JSON path (default: analysis/results/amoc_adapter_output.json)')

    args = parser.parse_args()

    adapter = RAPIDAMOCAdapter(mock_data_path=args.input)
    output_path = adapter.export_json(output_path=args.output)

    print(f"✅ RAPID AMOC Adapter: Data exported to {output_path}")

    # Print summary
    data = adapter.load_data()
    stats = adapter.compute_statistics(data)

    print(f"\n📊 Summary:")
    print(f"   Datapoints: {stats['n_datapoints']}")
    print(f"   Date Range: {stats['date_range']['start']} → {stats['date_range']['end']}")
    print(f"   Current Strength: {stats['current_state']['strength_Sv']:.2f} Sv")
    print(f"   Weakening Rate: {stats['trends']['weakening_rate_Sv_per_year']:.3f} Sv/year")
    print(f"   FovS Indicator: {stats['current_state']['fovs_indicator']:.3f}")
    print(f"   FovS Crossed Zero: {'🔴 YES' if stats['early_warning_signals']['fovs_crossed_zero'] else '🟢 NO'}")
    print(f"   AR(1) Coefficient: {stats['current_state']['ar1_coefficient']:.3f}")
    print(f"   AR(1) Increase: {stats['early_warning_signals']['ar1_increase_percent']:.1f}%")
    print(f"   Critical Slowing: {'🔴 YES' if stats['early_warning_signals']['critical_slowing'] else '🟢 NO'}")
    print(f"   Status: {stats['tipping_indicators']['status']}")
    print(f"   Distance to Tipping: {stats['current_state']['distance_to_tipping']:.1%}")


if __name__ == '__main__':
    main()
