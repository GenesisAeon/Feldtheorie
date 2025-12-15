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


def load_metadata(
    file_name: str | Path,
    *,
    metadata_dir: str | Path | None = None,
) -> Dict[str, Any]:
    """
    Load a YAML metadata file.

    Parameters
    ----------
    file_name : str or Path
        Name of the YAML file (with or without .yaml extension)
    metadata_dir : str or Path, optional
        Override directory for metadata files; defaults to ``data/metadata``

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
    if not str(file_name).endswith(".yaml"):
        file_name = f"{file_name}.yaml"

    base_dir = Path(metadata_dir) if metadata_dir is not None else METADATA_DIR
    path = base_dir / file_name

    if not path.exists():
        raise FileNotFoundError(f"Metadata file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Failed to parse {path}: {e}")


def load_dataset(
    meta: Dict[str, Any], *, data_dir: str | Path | None = None
) -> Optional[pd.DataFrame | Any]:
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
    data_dir : str or Path, optional
        Override base directory for data files; defaults to ``data``

    Returns
    -------
    DataFrame or Dataset or None
        Loaded data, or None if file not found

    Notes
    -----
    File search order: CSV -> CSV.GZ -> NetCDF -> JSON
    """
    dataset_raw = str(meta.get("dataset", "")).strip()
    if not dataset_raw:
        raise ValueError("Metadata must include a non-empty 'dataset' field")

    normalized_name = dataset_raw.replace(" ", "_").lower()
    base_dir = Path(data_dir) if data_dir is not None else DATA_DIR
    normalized_path = Path(normalized_name)

    candidates = []
    if normalized_path.suffixes:
        candidates.append(base_dir / normalized_path)
        # If a CSV is requested explicitly, also try the gzipped twin
        if normalized_path.suffixes[-1] == ".csv":
            candidates.append(base_dir / normalized_path.with_suffix(".csv.gz"))
        # If the request is already gzipped, allow a non-gz fallback
        if normalized_path.suffixes[-2:] == [".csv", ".gz"]:
            candidates.append(base_dir / normalized_path.with_suffix(".csv"))
    else:
        root = base_dir / normalized_path
        candidates.extend(
            [
                root.with_suffix(".csv"),
                root.with_suffix(".csv.gz"),
            ]
        )
        if XARRAY_AVAILABLE:
            candidates.append(root.with_suffix(".nc"))
        candidates.append(root.with_suffix(".json"))

    for candidate in candidates:
        if not candidate.exists():
            continue

        try:
            if candidate.suffix in {".csv", ""} or candidate.suffixes[-2:] == [".csv", ".gz"]:
                return pd.read_csv(candidate)
            if candidate.suffix == ".json":
                return pd.read_json(candidate)
            if candidate.suffix == ".nc" and XARRAY_AVAILABLE:
                return xr.open_dataset(candidate)
            if candidate.suffix == ".nc" and not XARRAY_AVAILABLE:
                print(
                    f"Warning: NetCDF file found ({candidate}) but xarray is not installed; "
                    "install xarray to access σ(β(R-Θ)) phase grids."
                )
        except Exception as e:  # pragma: no cover - defensive logging
            print(f"Warning: Failed to load {candidate}: {e}")

    print(
        "No dataset found for "
        f"'{dataset_raw}' (searched: CSV, CSV.GZ, NetCDF, JSON)"
    )
    return None


def load_all(
    *, metadata_dir: str | Path | None = None, data_dir: str | Path | None = None
) -> Dict[str, Dict[str, Any]]:
    """
    Load all metadata + datasets into a dictionary.

    Parameters
    ----------
    metadata_dir : str or Path, optional
        Override directory for YAML metadata; defaults to ``data/metadata``
    data_dir : str or Path, optional
        Override directory for datasets; defaults to ``data``

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
    base_metadata_dir = Path(metadata_dir) if metadata_dir is not None else METADATA_DIR
    base_data_dir = Path(data_dir) if data_dir is not None else DATA_DIR

    if not base_metadata_dir.exists():
        raise FileNotFoundError(f"Metadata directory not found: {base_metadata_dir}")

    datasets = {}
    yaml_files = list(base_metadata_dir.glob("*.yaml"))

    if not yaml_files:
        print(f"Warning: No YAML files found in {base_metadata_dir}")
        return datasets

    for yaml_file in yaml_files:
        try:
            meta = load_metadata(yaml_file.name, metadata_dir=base_metadata_dir)
            dataset_name_raw = str(meta.get("dataset", "")).strip()
            if not dataset_name_raw:
                raise ValueError(
                    f"Metadata entry {yaml_file.name} is missing the required 'dataset' field"
                )

            data = load_dataset(meta, data_dir=base_data_dir)
            dataset_name = dataset_name_raw.replace(" ", "_").lower()
            datasets[dataset_name] = {
                "metadata": meta,
                "data": data
            }
        except Exception as e:
            print(f"Error loading {yaml_file.name}: {e}")
            raise

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
    β must remain positive to keep σ(β(R-Θ)) meaningful
    """
    if beta <= 0:
        raise ValueError("beta must be positive to keep σ(β(R-Θ)) resonant")

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
