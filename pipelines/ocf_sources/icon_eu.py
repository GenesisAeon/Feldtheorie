"""
ICON-EU Loader (Zarr) – OCF-Style Ingest for Feldtheorie

Portions inspired by Open Climate Fix (MIT): graph_weather, PVNet.
Original code © Open Climate Fix. See ACKNOWLEDGEMENTS.md for full attribution.

Function: load_icon_eu_zarr(url, rename_map, drop_missing, chunks)
- Opens consolidated Zarr via fsspec
- Subsets/renames variables to Feldtheorie FieldCube standard
- Returns xarray.Dataset (lazy, dask-chunked)
"""
from __future__ import annotations
import contextlib
from typing import Dict, Iterable, Optional
import xarray as xr
import fsspec


def load_icon_eu_zarr(
    store_url: str,
    *,
    rename_map: Optional[Dict[str, str]] = None,
    keep: Optional[Iterable[str]] = None,
    chunks: Optional[Dict[str, int]] = None,
    consolidated: bool = True,
    drop_missing: bool = True,
) -> xr.Dataset:
    """Load ICON-EU Zarr dataset via fsspec.

    Args:
        store_url: URL to consolidated Zarr store
        rename_map: Dictionary mapping original variable names to FieldCube names
        keep: List of variables to keep (before renaming)
        chunks: Dask chunk sizes (if None, auto-chunks)
        consolidated: Whether to use consolidated metadata
        drop_missing: If True, ignore missing variables in keep list

    Returns:
        xarray.Dataset with lazy-loaded, chunked data

    Example:
        >>> ds = load_icon_eu_zarr(
        ...     "https://huggingface.co/datasets/openclimatefix/dwd-icon-eu/resolve/main/icon_eu.zarr",
        ...     rename_map={"t_2m": "t2m", "u_10m": "u10"},
        ...     chunks={"time": 8, "latitude": 256, "longitude": 256}
        ... )
    """
    mapper = fsspec.get_mapper(store_url)
    ds = xr.open_zarr(mapper, consolidated=consolidated)

    # Filter variables
    if keep:
        present = [v for v in keep if v in ds.data_vars]
        missing = sorted(set(keep) - set(present))
        if missing and not drop_missing:
            raise KeyError(f"ICON-EU: missing variables requested: {missing}")
        ds = ds[present] if present else ds

    # Rename variables (e.g., t_2m → t2m)
    if rename_map:
        ds = ds.rename({k: v for k, v in rename_map.items() if k in ds})

    # Apply chunking
    if chunks:
        ds = ds.chunk(chunks)
    else:
        # Robust default chunks: time small, spatial moderate
        auto_chunks = {}
        for d in ds.dims:
            if d in ("time", "step", "forecast_hour"):
                auto_chunks[d] = min(8, ds.sizes[d])
            elif d in ("latitude", "lat", "y", "rlat"):
                auto_chunks[d] = 256
            elif d in ("longitude", "lon", "x", "rlon"):
                auto_chunks[d] = 256
        with contextlib.suppress(Exception):
            ds = ds.chunk(auto_chunks)

    return ds
