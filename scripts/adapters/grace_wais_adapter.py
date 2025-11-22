#!/usr/bin/env python3
"""GRACE/GRACE-FO WAIS early-warning adapter.

This adapter ingests West Antarctic Ice Sheet (WAIS) mass balance proxies
from GRACE/GRACE-FO (staged as a CSV) and translates accelerating mass loss
into a beta estimate for Sigillin telemetry.

Execution examples (default mock data):

    python scripts/adapters/grace_wais_adapter.py --dry-run
    python scripts/adapters/grace_wais_adapter.py --output analysis/results/wais_adapter_output.json
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import numpy as np


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = BASE_DIR / "data" / "climate" / "wais_mass_balance_mock.csv"
DEFAULT_OUTPUT_PATH = BASE_DIR / "analysis" / "results" / "wais_adapter_output.json"


@dataclass
class WAISAdapterResult:
    """Structured adapter output for WAIS mass balance."""

    timestamp: str
    sensor: str
    mass_loss_rate_Gt_yr: float
    acceleration_Gt_yr2: float
    beta_estimate: float
    status: str

    def to_json(self) -> str:
        return json.dumps(
            {
                "timestamp": self.timestamp,
                "sensor": self.sensor,
                "mass_loss_rate_Gt_yr": round(self.mass_loss_rate_Gt_yr, 3),
                "acceleration_Gt_yr2": round(self.acceleration_Gt_yr2, 3),
                "beta_estimate": round(self.beta_estimate, 3),
                "status": self.status,
            },
            indent=2,
        )


def fetch_grace_data(
    csv_path: Path = DEFAULT_DATA_PATH,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load WAIS mass change data from a staged GRACE/GRACE-FO CSV.

    The function validates the presence of a ``date`` column and either
    ``mass_change_Gt`` directly or a ``mass_balance_Gt`` column that can be used
    to derive mass change relative to the first observation.
    """

    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"GRACE WAIS CSV not found: {csv_path}")

    with open(csv_path, "r", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        if "date" not in fieldnames:
            raise ValueError("CSV must include a 'date' column in YYYY-MM format.")

        has_mass_change = "mass_change_Gt" in fieldnames
        has_mass_balance = "mass_balance_Gt" in fieldnames
        if not has_mass_change and not has_mass_balance:
            raise ValueError(
                "CSV must provide either 'mass_change_Gt' or 'mass_balance_Gt' to derive mass change."
            )

        rows: List[Tuple[datetime, dict]] = []
        for row in reader:
            rows.append((_parse_date(row["date"]), row))

    rows.sort(key=lambda item: item[0])

    dates: List[datetime] = []
    mass_change: List[float] = []
    mass_balance: List[float] = []
    mass_change_rates: List[float] = []

    for date, row in rows:
        dates.append(date)
        if has_mass_change:
            mass_change.append(float(row["mass_change_Gt"]))
        if has_mass_balance:
            mass_balance.append(float(row["mass_balance_Gt"]))

        rate_raw = row.get("mass_change_rate_Gt_per_year")
        if rate_raw not in (None, ""):
            try:
                mass_change_rates.append(float(rate_raw))
            except ValueError:
                pass

    if not mass_change and mass_balance:
        baseline = mass_balance[0]
        mass_change = [value - baseline for value in mass_balance]

    if not mass_change:
        raise ValueError("No mass change data could be parsed from the GRACE CSV.")

    return np.array(dates), np.array(mass_change), np.array(mass_change_rates)


def _parse_date(date_str: str) -> datetime:
    normalized = date_str.strip()
    if len(normalized) >= 7:
        normalized = normalized[:7]
    return datetime.strptime(normalized, "%Y-%m")


def _beta_from_acceleration(acceleration: float) -> float:
    base_beta = 4.0
    if np.isnan(acceleration):
        return float("nan")

    if acceleration < -5:
        severity = -acceleration - 5
        return base_beta + float(np.exp(min(6.0, severity / 2.0)))

    return base_beta + max(0.0, -acceleration) * 0.25


def _mass_loss_rate_from_fit(coeffs: Iterable[float], t_last: float) -> float:
    a, b, _ = coeffs
    return float(2 * a * t_last + b)


def compute_wais_state(
    dates: np.ndarray,
    mass_change: np.ndarray,
    mass_change_rates: Optional[np.ndarray] = None,
    window_years: int = 5,
) -> WAISAdapterResult:
    """Estimate mass loss acceleration and beta over a sliding window."""

    if len(dates) < 3:
        raise ValueError("At least three observations are required for a quadratic fit.")

    window_months = max(3, int(window_years * 12))
    start_idx = max(0, len(dates) - window_months)
    window_dates = dates[start_idx:]
    window_series = mass_change[start_idx:]

    t = np.array([(d - window_dates[0]).days / 365.25 for d in window_dates], dtype=float)
    coeffs = np.polyfit(t, window_series, 2)
    acceleration = float(coeffs[0])

    if mass_change_rates is not None and len(mass_change_rates) == len(mass_change):
        mass_loss_rate = float(mass_change_rates[-1])
    else:
        mass_loss_rate = _mass_loss_rate_from_fit(coeffs, t_last=t[-1])

    beta_estimate = _beta_from_acceleration(acceleration)
    status = "accelerating_loss" if acceleration < -5 else "stable"

    return WAISAdapterResult(
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        sensor="GRACE_WAIS",
        mass_loss_rate_Gt_yr=mass_loss_rate,
        acceleration_Gt_yr2=acceleration,
        beta_estimate=beta_estimate,
        status=status,
    )


def run_adapter(
    csv_path: Path = DEFAULT_DATA_PATH, window_years: int = 5
) -> WAISAdapterResult:
    dates, mass_change, mass_change_rates = fetch_grace_data(csv_path=csv_path)
    return compute_wais_state(
        dates=dates, mass_change=mass_change, mass_change_rates=mass_change_rates, window_years=window_years
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="GRACE WAIS Adapter")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help="Input GRACE/GRACE-FO CSV (default: data/climate/wais_mass_balance_mock.csv)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Output JSON path (default: analysis/results/wais_adapter_output.json)",
    )
    parser.add_argument("--window-years", type=int, default=5, help="Sliding window size in years (default: 5)")
    parser.add_argument("--dry-run", action="store_true", help="Compute without writing JSON to disk")

    args = parser.parse_args()

    result = run_adapter(csv_path=args.input, window_years=args.window_years)
    print(result.to_json())

    if not args.dry_run:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as fh:
            fh.write(result.to_json())


if __name__ == "__main__":
    main()
