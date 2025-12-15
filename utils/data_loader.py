"""
UTAC Data Loader - v1.3
Reads YAML metadata files and loads associated datasets for analysis.

This module provides transparent data infrastructure for UTAC v2.0:
- Automatic loading of YAML metadata
- Support for CSV, NetCDF, JSON formats
- Error handling and validation
- Integration with UTAC analysis pipelines

Author: Johann Römer & Aeon
Date: December 2024
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import yaml

try:
    import xarray as xr
    XARRAY_AVAILABLE = True
except ImportError:
    XARRAY_AVAILABLE = False
    xr = None

METADATA_DIR = Path("data/metadata/")
DATA_DIR = Path("data/")


def load_metadata(file_name: str | Path) -> Dict[str, Any]:
    """
    Load a YAML metadata file.

    Parameters
    ----------
    file_name : str or Path
        Name of the YAML file (with or without .yaml extension)

    Returns
    -------
    dict
        Metadata dictionary

    Raises
    ------
    FileNotFoundError
        If metadata file not found
    yaml.YAMLError
        If YAML parsing fails
    """
    if not str(file_name).endswith('.yaml'):
        file_name = f"{file_name}.yaml"

    path = METADATA_DIR / file_name

    if not path.exists():
        raise FileNotFoundError(f"Metadata file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Failed to parse {path}: {e}")


def load_dataset(meta: Dict[str, Any]) -> Optional[pd.DataFrame | Any]:
    """
    Load dataset based on metadata.

    Supports:
    - CSV files (pandas DataFrame)
    - NetCDF files (xarray Dataset, if xarray installed)
    - JSON files (pandas DataFrame)

    Parameters
    ----------
    meta : dict
        Metadata dictionary with 'dataset' key

    Returns
    -------
    DataFrame or Dataset or None
        Loaded data, or None if file not found

    Notes
    -----
    File search order: CSV -> NetCDF -> JSON
    """
    dataset_name = meta.get("dataset", "unknown").replace(" ", "_").lower()
    data_path = DATA_DIR / dataset_name

    # Try CSV
    csv_file = data_path.with_suffix(".csv")
    if csv_file.exists():
        try:
            return pd.read_csv(csv_file)
        except Exception as e:
            print(f"Warning: Failed to load CSV {csv_file}: {e}")

    # Try NetCDF
    if XARRAY_AVAILABLE:
        nc_file = data_path.with_suffix(".nc")
        if nc_file.exists():
            try:
                return xr.open_dataset(nc_file)
            except Exception as e:
                print(f"Warning: Failed to load NetCDF {nc_file}: {e}")
    else:
        nc_file = data_path.with_suffix(".nc")
        if nc_file.exists():
            print(f"Warning: NetCDF file found ({nc_file}) but xarray not installed")

    # Try JSON
    json_file = data_path.with_suffix(".json")
    if json_file.exists():
        try:
            return pd.read_json(json_file)
        except Exception as e:
            print(f"Warning: Failed to load JSON {json_file}: {e}")

    print(f"No dataset found for '{meta.get('dataset', 'unknown')}' (searched: CSV, NetCDF, JSON)")
    return None


def load_all() -> Dict[str, Dict[str, Any]]:
    """
    Load all metadata + datasets into a dictionary.

    Returns
    -------
    dict
        Dictionary mapping dataset names to dicts with keys:
        - 'metadata': YAML metadata dict
        - 'data': Loaded dataset (DataFrame, xarray Dataset, or None)

    Raises
    ------
    FileNotFoundError
        If metadata directory doesn't exist
    """
    if not METADATA_DIR.exists():
        raise FileNotFoundError(f"Metadata directory not found: {METADATA_DIR}")

    datasets = {}
    yaml_files = list(METADATA_DIR.glob("*.yaml"))

    if not yaml_files:
        print(f"Warning: No YAML files found in {METADATA_DIR}")
        return datasets

    for yaml_file in yaml_files:
        try:
            meta = load_metadata(yaml_file.name)
            data = load_dataset(meta)
            dataset_name = meta.get("dataset", yaml_file.stem)
            datasets[dataset_name] = {
                "metadata": meta,
                "data": data
            }
        except Exception as e:
            print(f"Error loading {yaml_file.name}: {e}")
            continue

    return datasets


def calculate_tau_star(beta: float, theta: float, R: float) -> float:
    """
    Calculate τ* (critical time to threshold) for UTAC system.

    Parameters
    ----------
    beta : float
        Steepness parameter
    theta : float
        Threshold value
    R : float
        Current order parameter value

    Returns
    -------
    float
        Time to threshold (τ*)

    Notes
    -----
    Simplified formula: τ* = (Θ - R) / (dR/dt)
    Assumes linear approach for first-order approximation
    """
    if R >= theta:
        return 0.0  # Already at or past threshold

    # Simplified: assume dR/dt proportional to beta
    # More sophisticated: use actual time series derivative
    delta_R = theta - R
    rate = beta * 0.1  # Scaling factor (domain-specific)

    return delta_R / rate if rate > 0 else float('inf')


def summarize_datasets(datasets: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    """
    Create summary DataFrame of all loaded datasets.

    Parameters
    ----------
    datasets : dict
        Output from load_all()

    Returns
    -------
    DataFrame
        Summary with columns: dataset, beta, theta, field_type, data_shape, loaded
    """
    summaries = []
    for name, content in datasets.items():
        meta = content['metadata']
        data = content['data']

        summary = {
            'dataset': name,
            'beta': meta.get('beta', None),
            'theta': meta.get('theta', None),
            'field_type': meta.get('field_type', 'unknown'),
            'data_loaded': data is not None,
            'data_shape': str(data.shape) if hasattr(data, 'shape') else 'xarray'
        }
        summaries.append(summary)

    return pd.DataFrame(summaries)


if __name__ == "__main__":
    print("🌊 UTAC Data Loader v1.3")
    print("=" * 50)

    try:
        all_data = load_all()
        print(f"\n✅ Loaded {len(all_data)} datasets\n")

        for name, content in all_data.items():
            print(f"📊 {name}:")
            meta = content['metadata']
            print(f"   β = {meta.get('beta', 'N/A')}")
            print(f"   Θ = {meta.get('theta', 'N/A')}")
            print(f"   Field Type: {meta.get('field_type', 'unknown')}")

            if content["data"] is not None:
                data = content['data']
                if hasattr(data, 'shape'):
                    print(f"   Data shape: {data.shape}")
                else:
                    print(f"   Data type: xarray Dataset")
            else:
                print(f"   ⚠️  No data file found")
            print()

        # Summary table
        print("\n" + "=" * 50)
        print("Summary Table:")
        print("=" * 50)
        summary_df = summarize_datasets(all_data)
        print(summary_df.to_string(index=False))

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nEnsure data/metadata/ directory exists with YAML files")
