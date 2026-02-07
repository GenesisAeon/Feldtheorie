from __future__ import annotations

from analysis.climate_sigma_dashboard import (
    build_dashboard_snapshot,
    compute_sigma_phi_series,
    load_climate_timeseries,
)


def test_climate_loader_and_sigma_flags(tmp_path) -> None:
    csv_path = tmp_path / "climate.csv"
    csv_path.write_text(
        "timestamp,amoc\n"
        "2026-01-01T00:00:00Z,1.0\n"
        "2026-01-02T00:00:00Z,0.95\n"
        "2026-01-03T00:00:00Z,0.7\n"
        "2026-01-04T00:00:00Z,0.6\n"
        "2026-01-05T00:00:00Z,0.5\n",
        encoding="utf-8",
    )

    frame = load_climate_timeseries(csv_path, value_column="amoc")
    sigma_series = compute_sigma_phi_series(frame["value"], window=3)
    snapshot = build_dashboard_snapshot(frame, sigma_series, critical_threshold=0.055)

    assert len(frame) == 5
    assert snapshot["points"] == 5
    assert "critical_events" in snapshot


def test_sigma_series_is_bounded() -> None:
    import pandas as pd

    values = pd.Series([1.0, 0.99, 1.01, 1.0, 1.02])
    sigma_series = compute_sigma_phi_series(values, window=3)
    assert (sigma_series.dropna() >= 0.0).all()
