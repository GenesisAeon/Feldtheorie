"""
UTAC Data Loader – v1.2
Reads YAML metadata files and loads associated datasets for analysis.
"""

import os
import yaml
import pandas as pd
import xarray as xr
from pathlib import Path

METADATA_DIR = "data/metadata/"
DATA_DIR = "data/"

def load_metadata(file_name):
    """Load a YAML metadata file."""
    path = os.path.join(METADATA_DIR, file_name)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_dataset(meta):
    """
    Load dataset based on metadata.
    Supports CSV, NetCDF, JSON.
    """
    dataset_name = meta["dataset"].replace(" ", "_").lower()
    data_path = os.path.join(DATA_DIR, dataset_name)

    # Try CSV
    csv_file = data_path + ".csv"
    if os.path.exists(csv_file):
        return pd.read_csv(csv_file)

    # Try NetCDF
    nc_file = data_path + ".nc"
    if os.path.exists(nc_file):
        return xr.open_dataset(nc_file)

    # Try JSON
    json_file = data_path + ".json"
    if os.path.exists(json_file):
        return pd.read_json(json_file)

    print(f"No dataset found for {meta['dataset']}")
    return None

def calculate_tau_star(beta, theta, R):
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

def load_all():
    """Load all metadata + datasets into a dictionary."""
    datasets = {}
    metadata_path = Path(METADATA_DIR)
    
    if not metadata_path.exists():
        print(f"Warning: {METADATA_DIR} does not exist")
        return datasets
    
    for file in os.listdir(METADATA_DIR):
        if file.endswith(".yaml"):
            try:
                meta = load_metadata(file)
                data = load_dataset(meta)
                datasets[meta["dataset"]] = {
                    "metadata": meta,
                    "data": data
                }
            except Exception as e:
                print(f"Error loading {file}: {e}")
    
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
            if hasattr(content['data'], 'shape'):
                print(f"     Shape: {content['data'].shape}")
            else:
                print(f"     Type: xarray dataset")
        else:
            print(f"     ⚠️  No data file found (metadata only)")
        print()
