"""
UTAC Data Loader – v1.2
Reads YAML metadata files and loads associated datasets for analysis.
"""

import os
import yaml
import pandas as pd
import xarray as xr

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
    Calculate τ* (time to threshold) using the logistic UTAC model.

    Parameters:
    -----------
    beta : float
        Steepness of the logistic curve
    theta : float
        Threshold value
    R : float
        Current state variable

    Returns:
    --------
    float
        Time to threshold τ* (in years, assuming normalized time scale)
    """
    import numpy as np
    # Simplified calculation: τ* ≈ (Θ - R) / (β * σ(β(R-Θ)))
    # For demonstration purposes, using a linear approximation
    sigma_val = 1 / (1 + np.exp(-beta * (R - theta)))
    if sigma_val < 0.01:
        # System far from threshold
        return (theta - R) / 0.1  # Conservative estimate
    else:
        # System near threshold
        return (theta - R) / (beta * sigma_val)

def load_all():
    """Load all metadata + datasets into a dictionary."""
    datasets = {}
    for file in os.listdir(METADATA_DIR):
        if file.endswith(".yaml"):
            meta = load_metadata(file)
            data = load_dataset(meta)
            datasets[meta["dataset"]] = {
                "metadata": meta,
                "data": data
            }
    return datasets

if __name__ == "__main__":
    all_data = load_all()
    for name, content in all_data.items():
        print(f"Loaded: {name}")
        if content["data"] is not None:
            print(f" → Shape: {content['data'].shape if hasattr(content['data'], 'shape') else 'xarray dataset'}")
