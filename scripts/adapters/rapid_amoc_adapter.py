#!/usr/bin/env python3
"""RAPID AMOC adapter (functional version).

This adapter fetches Atlantic Meridional Overturning Circulation (AMOC) strength
data from the RAPID array if available and falls back to local staging data when
offline. It computes a lag-1 autocorrelation early warning signal and
translates it into a beta estimate consistent with the Sigillin format.

Execution (default uses staged/mock data when offline)::

    python scripts/adapters/rapid_amoc_adapter.py

Environment overrides:
- ``RAPID_DATA_URL``: custom CSV endpoint for RAPID transport data
- ``RAPID_LOCAL_PATH``: preferred local CSV (e.g., real RAPID download)
"""

from __future__ import annotations

import csv
import io
import json
import os
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "ocean"
DEFAULT_MOCK_PATH = DATA_DIR / "amoc_strength_mock.csv"
DEFAULT_LOCAL_PATH = DATA_DIR / "amoc_transport.csv"
DEFAULT_RAPID_URL = "https://rapid.ac.uk/rapidmoc/rapid_data/dataprod/AMOC_table.php?download=csv"


@dataclass
class AdapterResult:
    """Structured adapter output."""

    timestamp: str
    sensor: str
    beta_estimate: float
    ar1_score: float
    status: str
    mock_data: bool
    source: str

    def to_json(self) -> str:
        return json.dumps(
            {
                "timestamp": self.timestamp,
                "sensor": self.sensor,
                "beta_estimate": round(self.beta_estimate, 3),
                "ar1_score": round(self.ar1_score, 3),
                "status": self.status,
                "mock_data": self.mock_data,
                "source": self.source,
            },
            indent=2,
        )


def fetch_rapid_data(
    rapid_url: str = DEFAULT_RAPID_URL,
    local_path: Path | None = None,
    mock_path: Path = DEFAULT_MOCK_PATH,
) -> tuple[Iterable[dict], bool, str]:
    """Load RAPID data from the web, a local CSV, or a mock CSV.

    Returns an iterable of row dicts, a flag indicating whether data are mock,
    and a string describing the data source.
    """

    # 1) Prefer explicitly provided local path
    if local_path and Path(local_path).exists():
        return _read_csv(Path(local_path)), False, f"local:{Path(local_path)}"

    # 2) Attempt live download
    try:
        response = requests.get(rapid_url, timeout=10)
        response.raise_for_status()
        content = response.content.decode("utf-8")
        return _read_csv(io.StringIO(content)), False, f"remote:{rapid_url}"
    except Exception:
        pass

    # 3) Fall back to staged real data if present
    if DEFAULT_LOCAL_PATH.exists():
        return _read_csv(DEFAULT_LOCAL_PATH), False, f"local:{DEFAULT_LOCAL_PATH}"

    # 4) Final fallback to mock data
    return _read_csv(mock_path), True, f"mock:{mock_path}"


def _read_csv(path_or_buffer) -> Iterable[dict]:
    if isinstance(path_or_buffer, (str, Path)):
        with open(path_or_buffer, newline="") as fh:
            return list(csv.DictReader(fh))

    return list(csv.DictReader(path_or_buffer))


def _normalize_rows(rows: Iterable[dict]) -> tuple[np.ndarray, np.ndarray]:
    """Extract dates and AMOC strength (Sv) from heterogeneous sources."""

    date_values = []
    strength_values = []
    for row in rows:
        date_raw = row.get("date") or row.get("Date") or row.get("DATE")
        if not date_raw:
            continue

        try:
            date = datetime.fromisoformat(date_raw.replace("/", "-"))
        except ValueError:
            continue

        strength_raw = (
            row.get("strength_Sv") or row.get("AMOC") or row.get("transport") or row.get("MOC")
        )
        try:
            strength = float(strength_raw) if strength_raw is not None else None
        except (TypeError, ValueError):
            strength = None

        if strength is None:
            continue

        date_values.append(date)
        strength_values.append(strength)

    order = np.argsort(date_values)
    sorted_dates = np.array(date_values)[order]
    sorted_strengths = np.array(strength_values)[order]
    return sorted_dates, sorted_strengths


def _resample_monthly(dates: np.ndarray, strengths: np.ndarray) -> np.ndarray:
    """Average strength values per calendar month."""

    monthly = {}
    for date, value in zip(dates, strengths):
        key = (date.year, date.month)
        monthly.setdefault(key, []).append(value)

    sorted_keys = sorted(monthly.keys())
    return np.array([np.mean(monthly[k]) for k in sorted_keys])


def _rolling_ar1(series: np.ndarray, window: int = 12) -> float:
    if len(series) < window + 1:
        return float("nan")

    windowed = series[-window:]
    x, y = windowed[:-1], windowed[1:]
    x_centered = x - np.mean(x)
    y_centered = y - np.mean(y)
    denominator = np.sqrt(np.sum(x_centered**2) * np.sum(y_centered**2))
    if denominator == 0:
        return float("nan")
    return float(np.sum(x_centered * y_centered) / denominator)


def _beta_from_ar1(ar1: float) -> float:
    if ar1 >= 1:
        return float("inf")
    return 1.0 / max(1e-6, (1 - ar1))


def _status_from_ar1(ar1: float) -> str:
    if ar1 >= 0.9:
        return "lock_in"
    if ar1 >= 0.7:
        return "critical_slowing"
    return "stable"


def run_adapter() -> AdapterResult:
    local_override = os.environ.get("RAPID_LOCAL_PATH")
    rapid_url = os.environ.get("RAPID_DATA_URL", DEFAULT_RAPID_URL)

    rows, mock_flag, source_label = fetch_rapid_data(
        rapid_url=rapid_url,
        local_path=Path(local_override) if local_override else None,
    )

    dates, strengths = _normalize_rows(rows)
    if len(strengths) == 0 and not mock_flag:
        rows = _read_csv(DEFAULT_MOCK_PATH)
        mock_flag = True
        source_label = f"mock:{DEFAULT_MOCK_PATH}"
        dates, strengths = _normalize_rows(rows)

    if len(strengths) == 0:
        raise RuntimeError("No AMOC strength data could be parsed.")

    monthly = _resample_monthly(dates, strengths)
    ar1_score = float(_rolling_ar1(monthly, window=12))
    beta_estimate = float(_beta_from_ar1(ar1_score))
    status = _status_from_ar1(ar1_score)

    return AdapterResult(
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        sensor="RAPID_AMOC_26N",
        beta_estimate=beta_estimate,
        ar1_score=ar1_score,
        status=status,
        mock_data=mock_flag,
        source=source_label,
    )


def main() -> None:
    result = run_adapter()
    print(result.to_json())


if __name__ == "__main__":
    main()
