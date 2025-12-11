"""
UTAC Data Loader – v1.2
Reads YAML metadata files and loads associated datasets for analysis.
"""

from pathlib import Path
from typing import Any, Union

import pandas as pd
import xarray as xr
import yaml

METADATA_DIR = "data/metadata/"
DATA_DIR = "data/"


DatasetType = Union[pd.DataFrame, xr.Dataset]


def load_metadata(file_name: str, metadata_dir: str = METADATA_DIR) -> dict[str, Any]:
    """Load a YAML metadata file from the configured directory."""

    path = Path(metadata_dir) / file_name
    if not path.exists():
        raise FileNotFoundError(f"Metadata file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_dataset(meta: dict[str, Any], data_dir: str = DATA_DIR) -> DatasetType:
    """
    Load a dataset based on metadata.

    The loader supports CSV (plain or gzip-compressed), NetCDF and JSON files.
    The `dataset` field in the metadata is used to derive the filename;
    whitespace is replaced with underscores and the name is lowercased to
    stabilize lookups.
    """

    dataset_name = meta.get("dataset")
    if not dataset_name:
        raise ValueError("Metadata must include a non-empty 'dataset' field")

    base_path = Path(data_dir) / dataset_name.replace(" ", "_").lower()

    for suffix, reader in (
        (".csv", pd.read_csv),
        (".csv.gz", pd.read_csv),
        (".nc", xr.open_dataset),
        (".json", pd.read_json),
    ):
        candidate = base_path.with_suffix(suffix)
        if candidate.exists():
            return reader(candidate)

    raise FileNotFoundError(f"No dataset found for {dataset_name} in {Path(data_dir).resolve()}")


def calculate_tau_star(beta: float, theta: float, R: float) -> float:
    """
    Calculate τ* (time to threshold) for a system.

    Args:
        beta: Steepness parameter
        theta: Threshold value
        R: Current resource/activation level

    Returns:
        float: Time to threshold (arbitrary units)
    """
    if R >= theta:
        return 0.0  # Already at threshold

    # Simplified τ* calculation: τ* ∝ 1/(β·(θ-R))
    # This is a first-order approximation
    tau_star = 1.0 / (beta * (theta - R) + 1e-10)
    return tau_star


def load_all(metadata_dir: str = METADATA_DIR, data_dir: str = DATA_DIR):
    """Load all metadata + datasets into a dictionary keyed by dataset name."""

    datasets: dict[str, dict[str, Any]] = {}
    metadata_path = Path(metadata_dir)

    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata directory does not exist: {metadata_dir}")

    for file in metadata_path.glob("*.yaml"):
        try:
            meta = load_metadata(file.name, metadata_dir=metadata_dir)
            try:
                data = load_dataset(meta, data_dir=data_dir)
            except FileNotFoundError:
                data = None

            datasets[meta["dataset"]] = {
                "metadata": meta,
                "data": data,
            }
        except Exception as e:  # pragma: no cover - defensive logging path
            print(f"Error loading {file.name}: {e}")

    return datasets


if __name__ == "__main__":
    all_data = load_all()
    print(f"\n📊 Loaded {len(all_data)} datasets:\n")

    for name, content in all_data.items():
        print(f"  ✅ {name}")
        meta = content["metadata"]
        print(f"     β: {meta.get('beta_estimate', 'N/A')}")
        print(f"     Period: {meta.get('period', 'N/A')}")
        print(f"     Source: {meta.get('source', 'N/A')}")

        if content["data"] is not None:
            if hasattr(content["data"], "shape"):
                print(f"     Shape: {content['data'].shape}")
            else:
                print("     Type: xarray dataset")
        else:
            print("     ⚠️  No data file found (metadata only)")
        print()
