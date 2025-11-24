#!/usr/bin/env python3
"""World Bank Data Pipeline for Social Rigidity Model.

This script fetches Gini coefficient time-series data from the World Bank API
and prepares it for integration with models/social_rigidity_ising.py. The
pipeline supports the hypothesis that high inequality (high Gini) drives social
systems toward "frozen" states (β_eff → ∞).

DATA GOVERNANCE:
- Source: World Bank Open Data API
- Indicator: SI.POV.GINI (Gini Index)
- License: CC BY 4.0 (World Bank Terms of Use)
- Provenance: Automatically tracked in metadata

USAGE:
    python scripts/ingest_world_bank_gini.py \
        --countries USA,DEU,BRA,ZAF,SWE,NOR \
        --start-year 1990 \
        --end-year 2023 \
        --output data/social/gini_timeseries.csv

INTEGRATION:
    The output CSV can be fed into analysis/social_rigidity_analysis.py
    (to be created) for T_social = 1 / (Gini · Load) validation.

REQUIREMENTS:
    pip install requests pandas
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

try:
    import requests
except ImportError:
    print("ERROR: requests library not found. Install via: pip install requests", file=sys.stderr)
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parents[1]

# World Bank API endpoints
WB_API_BASE = "https://api.worldbank.org/v2"
GINI_INDICATOR = "SI.POV.GINI"

# Country codes for interesting cases (high/low inequality)
DEFAULT_COUNTRIES = {
    # High inequality
    "ZAF": "South Africa",
    "BRA": "Brazil",
    "COL": "Colombia",
    "CHL": "Chile",
    "MEX": "Mexico",
    # Low inequality
    "SWE": "Sweden",
    "NOR": "Norway",
    "DNK": "Denmark",
    "FIN": "Finland",
    # Middle / Reference
    "USA": "United States",
    "DEU": "Germany",
    "CHN": "China",
    "IND": "India",
    "GBR": "United Kingdom",
    "FRA": "France",
}


@dataclass
class GiniDataPoint:
    """Single Gini coefficient observation."""

    country_code: str
    country_name: str
    year: int
    gini_value: float
    source: str = "World Bank"
    indicator: str = GINI_INDICATOR

    def to_dict(self) -> Dict[str, object]:
        return {
            "country_code": self.country_code,
            "country_name": self.country_name,
            "year": self.year,
            "gini_value": self.gini_value,
            "source": self.source,
            "indicator": self.indicator,
        }


def fetch_gini_for_country(
    country_code: str, start_year: int = 1990, end_year: int = 2023
) -> List[GiniDataPoint]:
    """Fetch Gini coefficient time series for a single country.

    Args:
        country_code: ISO 3-letter country code (e.g., 'USA', 'DEU')
        start_year: Start year for time series (default: 1990)
        end_year: End year for time series (default: 2023)

    Returns:
        List of GiniDataPoint objects

    Raises:
        requests.RequestException: If API call fails
        ValueError: If response parsing fails
    """
    url = f"{WB_API_BASE}/country/{country_code}/indicator/{GINI_INDICATOR}"
    params = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
        "per_page": 500,
    }

    print(f"Fetching Gini data for {country_code}...", file=sys.stderr)

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    # World Bank API returns [metadata, data]
    if not isinstance(data, list) or len(data) < 2:
        raise ValueError(f"Unexpected API response format for {country_code}")

    metadata = data[0]
    observations = data[1]

    if not observations:
        print(f"WARNING: No Gini data for {country_code} in {start_year}-{end_year}", file=sys.stderr)
        return []

    country_name = observations[0]["country"]["value"] if observations else country_code

    datapoints = []
    for obs in observations:
        if obs["value"] is not None:
            datapoints.append(
                GiniDataPoint(
                    country_code=country_code,
                    country_name=country_name,
                    year=int(obs["date"]),
                    gini_value=float(obs["value"]),
                )
            )

    print(f"  → Found {len(datapoints)} observations for {country_code}", file=sys.stderr)
    return datapoints


def fetch_gini_bulk(
    countries: List[str], start_year: int = 1990, end_year: int = 2023
) -> List[GiniDataPoint]:
    """Fetch Gini data for multiple countries.

    Args:
        countries: List of ISO 3-letter country codes
        start_year: Start year for time series
        end_year: End year for time series

    Returns:
        Combined list of GiniDataPoint objects
    """
    all_data = []

    for country in countries:
        try:
            country_data = fetch_gini_for_country(country, start_year, end_year)
            all_data.extend(country_data)
        except Exception as e:
            print(f"ERROR: Failed to fetch data for {country}: {e}", file=sys.stderr)
            continue

    return all_data


def export_to_csv(datapoints: List[GiniDataPoint], output_path: Path) -> None:
    """Export Gini data to CSV with metadata sidecar.

    Args:
        datapoints: List of GiniDataPoint objects
        output_path: Path to output CSV file
    """
    if not datapoints:
        print("WARNING: No data to export!", file=sys.stderr)
        return

    # Convert to DataFrame
    df = pd.DataFrame([dp.to_dict() for dp in datapoints])

    # Sort by country, year
    df = df.sort_values(["country_code", "year"])

    # Save CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"\n✅ Exported {len(df)} observations to {output_path}", file=sys.stderr)

    # Create metadata sidecar
    metadata = {
        "name": "World Bank Gini Coefficient Time Series",
        "source": "World Bank Open Data API",
        "indicator": GINI_INDICATOR,
        "url": f"{WB_API_BASE}/country/all/indicator/{GINI_INDICATOR}",
        "license": "CC BY 4.0 (World Bank Terms of Use)",
        "provenance": {
            "script": "scripts/ingest_world_bank_gini.py",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        },
        "description": "Gini index measures inequality of income/consumption distribution (0=perfect equality, 100=perfect inequality)",
        "variables": {
            "country_code": "ISO 3-letter country code",
            "country_name": "Country name",
            "year": "Year of observation",
            "gini_value": "Gini coefficient (0-100 scale)",
            "source": "Data source",
            "indicator": "World Bank indicator code",
        },
        "utac_context": {
            "model": "models/social_rigidity_ising.py",
            "hypothesis": "High Gini → T_social = 1/(Gini·Load) → β_eff → ∞ (frozen states)",
            "R": "Gini coefficient",
            "Theta": "Critical inequality threshold (to be empirically determined)",
            "beta": "Steepness of rigidity transition (to be fitted)",
        },
        "countries": sorted(df["country_code"].unique().tolist()),
        "year_range": {"min": int(df["year"].min()), "max": int(df["year"].max())},
        "observations": len(df),
    }

    metadata_path = output_path.with_suffix(".metadata.json")
    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"✅ Metadata saved to {metadata_path}", file=sys.stderr)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch Gini coefficient data from World Bank for social rigidity analysis"
    )
    parser.add_argument(
        "--countries",
        default=",".join(DEFAULT_COUNTRIES.keys()),
        help=f"Comma-separated country codes (default: {','.join(list(DEFAULT_COUNTRIES.keys())[:5])}...)",
    )
    parser.add_argument(
        "--start-year", type=int, default=1990, help="Start year for time series (default: 1990)"
    )
    parser.add_argument(
        "--end-year", type=int, default=2023, help="End year for time series (default: 2023)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE_DIR / "data" / "social" / "gini_timeseries.csv",
        help="Output CSV path (default: data/social/gini_timeseries.csv)",
    )
    parser.add_argument(
        "--list-countries",
        action="store_true",
        help="List default countries and exit",
    )

    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    if args.list_countries:
        print("Default countries:")
        for code, name in DEFAULT_COUNTRIES.items():
            print(f"  {code}: {name}")
        return 0

    # Parse country list
    countries = [c.strip().upper() for c in args.countries.split(",")]

    print(f"Fetching Gini data for {len(countries)} countries: {', '.join(countries)}", file=sys.stderr)
    print(f"Year range: {args.start_year}-{args.end_year}\n", file=sys.stderr)

    # Fetch data
    datapoints = fetch_gini_bulk(countries, args.start_year, args.end_year)

    if not datapoints:
        print("ERROR: No data fetched!", file=sys.stderr)
        return 1

    # Export
    export_to_csv(datapoints, args.output if args.output.is_absolute() else BASE_DIR / args.output)

    print("\n🎯 Next steps:", file=sys.stderr)
    print("  1. Run: python analysis/social_rigidity_analysis.py (to be created)", file=sys.stderr)
    print("  2. Fit T_social = 1/(Gini·Load) model", file=sys.stderr)
    print("  3. Validate β_eff → ∞ hypothesis for high Gini countries", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
