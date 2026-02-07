from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_climate_timeseries(path: str | Path, value_column: str) -> pd.DataFrame:
    """Load climate telemetry with expected columns: timestamp + value_column."""
    frame = pd.read_csv(path)
    required = {"timestamp", value_column}
    missing = required.difference(frame.columns)
    if missing:
        msg = f"Missing required columns: {sorted(missing)}"
        raise ValueError(msg)
    out = frame[["timestamp", value_column]].copy()
    out.columns = ["timestamp", "value"]
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out = out.sort_values("timestamp").reset_index(drop=True)
    return out


def compute_sigma_phi_series(values: pd.Series, window: int = 12) -> pd.Series:
    """Compute rolling σ_Φ proxy as std/|mean| over a moving window."""
    if window < 2:
        msg = "window must be >=2"
        raise ValueError(msg)
    mean = values.rolling(window=window, min_periods=window).mean().abs().clip(lower=1e-12)
    std = values.rolling(window=window, min_periods=window).std(ddof=0)
    return (std / mean).clip(lower=0.0)


def build_dashboard_snapshot(
    frame: pd.DataFrame,
    sigma_phi_series: pd.Series,
    critical_threshold: float = 0.055,
    warning_threshold: float = 0.0625,
) -> dict[str, object]:
    merged = frame.copy()
    merged["sigma_phi"] = sigma_phi_series
    critical_events = int((merged["sigma_phi"] < critical_threshold).fillna(False).sum())
    warning_events = int(
        (
            (merged["sigma_phi"] < warning_threshold)
            & (merged["sigma_phi"] >= critical_threshold)
        )
        .fillna(False)
        .sum()
    )
    latest = merged["sigma_phi"].dropna()
    latest_value = float(latest.iloc[-1]) if not latest.empty else None
    return {
        "points": int(len(merged)),
        "critical_events": critical_events,
        "warning_events": warning_events,
        "latest_sigma_phi": latest_value,
        "assumptions": {
            "value_column": "Single normalized climate signal (e.g., AMOC index or Arctic sea-ice anomaly).",
            "sampling": "Uniform daily/weekly cadence after ingestion.",
        },
    }
