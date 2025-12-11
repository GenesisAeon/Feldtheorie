#!/usr/bin/env python3
"""NOAA OISST coral bleaching adapter (mock).

This adapter completes the AMOC/WAIS/Coral sensor triad by translating
mocked Coral Reef Watch observations into Sigillin-standard telemetry.
It operates on the pre-generated CSV located at ``data/biology/coral_bleaching_global_mock.csv``
and returns a biologically grounded beta estimate based on Degree Heating
Weeks (DHW) stress accumulation.
"""

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class CoralBleachingRecord:
    """Typed record for a single coral bleaching observation."""

    year: int
    bleaching_percent: float
    dhw_degree_heating_weeks: float
    sst_anomaly_C: float
    distance_to_tipping: float

    @property
    def timestamp(self) -> str:
        """Return a date string for the observation year (end-of-year).

        The mock dataset is annual, so we bind the reading to December 31st
        of the corresponding year to produce an ISO-compatible date stamp.
        """

        return f"{self.year}-12-31"


class OISSTCoralAdapter:
    """Mock adapter for OISST Coral bleaching data."""

    def __init__(self, mock_data_path: str = None):
        """Initialize adapter.

        Args:
            mock_data_path: Path to mock CSV file
        """
        if mock_data_path is None:
            mock_data_path = (
                Path(__file__).parent.parent.parent
                / "data"
                / "biology"
                / "coral_bleaching_global_mock.csv"
            )

        self.data_path = Path(mock_data_path)

        if not self.data_path.exists():
            raise FileNotFoundError(f"Mock data not found: {self.data_path}")

    def fetch_bleaching_data(self) -> list[CoralBleachingRecord]:
        """Load mock coral bleaching observations from CSV.

        Returns:
            List[CoralBleachingRecord]: Parsed annual records ordered by year.
        """

        records: list[CoralBleachingRecord] = []
        with open(self.data_path, encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                records.append(
                    CoralBleachingRecord(
                        year=int(row["year"]),
                        bleaching_percent=float(row["bleaching_percent"]),
                        dhw_degree_heating_weeks=float(row["dhw_degree_heating_weeks"]),
                        sst_anomaly_C=float(row["sst_anomaly_C"]),
                        distance_to_tipping=float(row["distance_to_tipping"]),
                    )
                )

        return records

    def load_data(self) -> dict:
        """Return legacy dictionary representation for downstream stats helpers."""

        records = self.fetch_bleaching_data()
        return {
            "years": [record.year for record in records],
            "bleaching_percent": [record.bleaching_percent for record in records],
            "dhw_degree_heating_weeks": [record.dhw_degree_heating_weeks for record in records],
            "sst_anomaly_C": [record.sst_anomaly_C for record in records],
            "distance_to_tipping": [record.distance_to_tipping for record in records],
        }

    def compute_statistics(self, data: dict) -> dict:
        """Compute summary statistics for coral bleaching data.

        Args:
            data: Loaded data from load_data()

        Returns:
            dict: Statistics summary
        """
        years = np.array(data["years"])
        bleaching = np.array(data["bleaching_percent"])
        dhw = np.array(data["dhw_degree_heating_weeks"])
        sst = np.array(data["sst_anomaly_C"])
        distance = np.array(data["distance_to_tipping"])

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
            "n_datapoints": len(bleaching),
            "date_range": {"start": int(years[0]), "end": int(years[-1])},
            "current_state": {
                "bleaching_percent": float(current_bleaching),
                "dhw_degree_heating_weeks": float(current_dhw),
                "sst_anomaly_C": float(current_sst),
                "distance_to_tipping": float(current_distance),
            },
            "historical_trends": {
                "bleaching_early_period_percent": float(early_bleaching),
                "bleaching_late_period_percent": float(late_bleaching),
                "bleaching_increase_percent": float(bleaching_increase_percent),
                "dhw_early_period": float(early_dhw),
                "dhw_late_period": float(late_dhw),
                "dhw_increase_percent": float(dhw_increase_percent),
                "bleaching_rate_percent_per_decade": float(bleaching_trend),
            },
            "mass_bleaching_events": {
                "count": int(mass_bleaching_count),
                "years": [int(y) for y in mass_bleaching_years],
                "first_event": int(mass_bleaching_years[0]) if mass_bleaching_count > 0 else None,
            },
            "tipping_assessment": {
                "status": "TIPPED" if tipped else ("PRE_TIPPING" if pre_tipping else "STABLE"),
                "tipped": bool(tipped),
                "pre_tipping": bool(pre_tipping),
                "threshold_exceeded": bool(
                    current_bleaching >= 84.0
                ),  # 84% = 4th global event threshold
                "heat_stress_critical": bool(current_dhw >= 8.0),  # DHW > 8 = severe bleaching
            },
            "thresholds": {
                "bleaching_moderate": 30.0,
                "bleaching_severe": 50.0,
                "bleaching_mass_event": 84.0,
                "dhw_mild_stress": 4.0,
                "dhw_severe_stress": 8.0,
                "sst_anomaly_danger": 1.0,
            },
        }

        return stats

    def _bleaching_alert_level(self, dhw: float) -> str:
        """Map Degree Heating Weeks to NOAA-style alert levels."""

        if dhw >= 8.0:
            return "Alert Level 2"
        if dhw >= 4.0:
            return "Alert Level 1"
        if dhw >= 1.0:
            return "Watch"
        return "No Stress"

    def _beta_estimate(self, dhw: float) -> float:
        """Estimate beta coupling strength from DHW.

        Piecewise scaling ensures DHW > 4 → beta > 8 and DHW > 8 → beta > 20,
        aligning with the stress-accumulation guidance in the activation prompt.
        """

        if dhw <= 4.0:
            return dhw * 2.0
        if dhw <= 8.0:
            # Interpolate from beta=8 at DHW=4 to beta=20 at DHW=8
            return 8.0 + (dhw - 4.0) * 3.0
        # Beyond severe bleaching, beta accelerates faster (steeper slope)
        return 20.0 + (dhw - 8.0) * 4.0

    def _status(self, dhw: float) -> str:
        """Classify resilience status based on DHW stress."""

        return "resilience_loss" if dhw >= 4.0 else "stable"

    def latest_sensor_payload(self) -> dict[str, object]:
        """Return the latest observation in Sigillin-standard JSON shape."""

        records = self.fetch_bleaching_data()
        if not records:
            raise ValueError("No coral bleaching records available")

        latest = records[-1]
        beta_estimate = self._beta_estimate(latest.dhw_degree_heating_weeks)
        alert_level = self._bleaching_alert_level(latest.dhw_degree_heating_weeks)
        status = self._status(latest.dhw_degree_heating_weeks)

        return {
            "timestamp": latest.timestamp,
            "sensor": "NOAA_CORAL_REEF_WATCH",
            "sst_anomaly_C": latest.sst_anomaly_C,
            "degree_heating_weeks": latest.dhw_degree_heating_weeks,
            "bleaching_alert_level": alert_level,
            "beta_estimate": beta_estimate,
            "status": status,
        }

    def export_json(self, output_path: str = None) -> str:
        """Export Sigillin-standard coral telemetry as JSON.

        Args:
            output_path: Destination JSON path.

        Returns:
            str: Path to exported JSON file.
        """

        if output_path is None:
            output_path = (
                Path(__file__).parent.parent / "analysis" / "results" / "coral_adapter_output.json"
            )

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        payload = self.latest_sensor_payload()

        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

        return str(output_path)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="OISST Coral Adapter (Mock)")
    parser.add_argument(
        "--input",
        type=str,
        help="Input CSV path (default: data/biology/coral_bleaching_global_mock.csv)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON path (default: analysis/results/coral_adapter_output.json)",
    )

    args = parser.parse_args()

    adapter = OISSTCoralAdapter(mock_data_path=args.input)
    output_path = adapter.export_json(output_path=args.output)

    payload = adapter.latest_sensor_payload()
    print(f"✅ OISST Coral Adapter: Data exported to {output_path}")
    print("\n📡 Coral Sensor Payload (latest):")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
