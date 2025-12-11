#!/usr/bin/env python3
"""
GRACE WAIS Adapter (Production Ready)
=====================================

Early-warning adapter for GRACE/GRACE-FO West Antarctic Ice Sheet (WAIS) mass
change data. Follows the Sigillin/UTAC pattern: ingest → physics → beta
estimate → JSON payload.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_DATA_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "climate" / "wais_mass_balance_mock.csv"
)
REQUIRED_COLUMNS = {"date", "mass_change_Gt"}


def fetch_grace_data(mock_data_path: str | None = None) -> pd.DataFrame:
    """Load WAIS mass-change data from the GRACE/GRACE-FO proxy CSV.

    Validates that the dataset exposes the expected columns and computes
    ``mass_change_Gt`` if only cumulative ``mass_balance_Gt`` is present.

    Args:
        mock_data_path: Optional override path to the mock GRACE dataset.

    Returns:
        DataFrame with ``date`` (datetime64) and ``mass_change_Gt`` (float).

    Raises:
        FileNotFoundError: When the CSV is missing.
        ValueError: When required columns cannot be satisfied.
    """

    data_path = Path(mock_data_path) if mock_data_path else DEFAULT_DATA_PATH
    if not data_path.exists():
        raise FileNotFoundError(f"GRACE/GRACE-FO proxy not found: {data_path}")

    df = pd.read_csv(data_path)

    # Attempt to backfill ``mass_change_Gt`` from ``mass_balance_Gt`` if needed
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        if missing == {"mass_change_Gt"} and "mass_balance_Gt" in df.columns:
            baseline = float(df["mass_balance_Gt"].iloc[0])
            df["mass_change_Gt"] = df["mass_balance_Gt"].astype(float) - baseline
            missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(
            "Required columns missing from GRACE dataset: " + ", ".join(sorted(missing))
        )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df["date"].isna().any():
        raise ValueError("Invalid date entries detected in GRACE dataset.")

    df = df.sort_values("date").reset_index(drop=True)
    df["mass_change_Gt"] = df["mass_change_Gt"].astype(float)
    return df


def _beta_from_acceleration(acceleration: float) -> float:
    """Map acceleration (Gt/yr²) to beta using an exponential ramp."""

    baseline_beta = 4.0
    if acceleration < -5.0:
        return baseline_beta + float(np.exp((-acceleration - 5.0) / 5.0))

    damped_penalty = max(0.0, -acceleration) / 10.0
    return baseline_beta + damped_penalty


def estimate_beta_signal(df: pd.DataFrame, window_years: int = 5) -> dict[str, float | str]:
    """Estimate beta dynamics via quadratic acceleration over a rolling window.

    Args:
        df: GRACE WAIS DataFrame containing ``date`` and ``mass_change_Gt``.
        window_years: Width of the trailing window (years) for the fit.

    Returns:
        Dictionary containing mass-loss rate, acceleration, beta, and status.

    Raises:
        ValueError: When insufficient data exist for a quadratic fit.
    """

    if df.empty:
        raise ValueError("No data available for WAIS beta estimation.")

    window_start = df["date"].max() - pd.DateOffset(years=window_years)
    window = df[df["date"] >= window_start].copy()

    if len(window) < 3:
        raise ValueError("Insufficient data points for quadratic fit (need >= 3).")

    t_years = (window["date"] - window["date"].min()).dt.total_seconds() / (365.25 * 24 * 3600)
    mass_change = window["mass_change_Gt"].to_numpy()

    a, b, _ = np.polyfit(t_years, mass_change, 2)
    t_last = t_years.iloc[-1]
    instantaneous_loss_rate = 2 * a * t_last + b

    acceleration = float(a)
    beta_estimate = _beta_from_acceleration(acceleration)
    status = "accelerating_loss" if acceleration < -5.0 else "stable"

    return {
        "mass_loss_rate_Gt_yr": float(instantaneous_loss_rate),
        "acceleration_Gt_yr2": acceleration,
        "beta_estimate": beta_estimate,
        "status": status,
    }


def build_payload(df: pd.DataFrame, window_years: int = 5) -> dict[str, str | float]:
    """Build the Sigillin-standard payload for WAIS early warnings."""

    beta_signal = estimate_beta_signal(df, window_years=window_years)

    return {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "sensor": "GRACE_WAIS",
        "mass_loss_rate_Gt_yr": beta_signal["mass_loss_rate_Gt_yr"],
        "acceleration_Gt_yr2": beta_signal["acceleration_Gt_yr2"],
        "beta_estimate": beta_signal["beta_estimate"],
        "status": beta_signal["status"],
    }


def export_payload(payload: dict[str, str | float], output_path: str | None) -> str:
    """Export the payload as JSON to the requested path."""

    destination = (
        Path(output_path)
        if output_path
        else Path(__file__).resolve().parents[1]
        / "analysis"
        / "results"
        / "wais_adapter_output.json"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return str(destination)


def main() -> None:
    """CLI entry point for activating the WAIS adapter."""

    import argparse

    parser = argparse.ArgumentParser(description="GRACE WAIS Adapter (Production)")
    parser.add_argument(
        "--input",
        type=str,
        help="Input CSV path (default: data/climate/wais_mass_balance_mock.csv)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON path (default: analysis/results/wais_adapter_output.json)",
    )
    parser.add_argument(
        "--window-years",
        type=int,
        default=5,
        help="Trailing window (years) for quadratic fit (default: 5)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute and print payload without writing to disk.",
    )

    args = parser.parse_args()

    df = fetch_grace_data(args.input)
    payload = build_payload(df, window_years=args.window_years)

    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return

    output_path = export_payload(payload, args.output)
    print(f"✅ GRACE WAIS Adapter activated: payload written to {output_path}")


if __name__ == "__main__":
    main()
