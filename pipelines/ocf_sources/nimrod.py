"""
Radar Loader (Nimrod/MRMS) for Feldtheorie

Portions inspired by Open Climate Fix (MIT): skillful_nowcasting.
Original code © Open Climate Fix. See ACKNOWLEDGEMENTS.md for full attribution.

Function: load_radar_zarr(url, rename_map, chunks)
- Opens Zarr (consolidated) or NetCDF (fallback)
- Normalizes dimensions to (time, y, x)
- Renames variables to FieldCube standard
"""
from __future__ import annotations
from typing import Dict, Optional
import xarray as xr
import fsspec


def _open_any(url: str) -> xr.Dataset:
    """Try consolidated Zarr first, fallback to NetCDF."""
    try:
        mapper = fsspec.get_mapper(url)
        return xr.open_zarr(mapper, consolidated=True)
    except Exception:
        # Fallback: NetCDF (local/remote via fsspec)
        return xr.open_dataset(url, engine="netcdf4")


def _normalize_dims(ds: xr.Dataset) -> xr.Dataset:
    """Normalize dimension names to (time, y, x)."""
    dim_map = {}
    if "latitude" in ds.dims:
        dim_map["latitude"] = "y"
    if "longitude" in ds.dims:
        dim_map["longitude"] = "x"
    if "lat" in ds.dims:
        dim_map["lat"] = "y"
    if "lon" in ds.dims:
        dim_map["lon"] = "x"
    if "valid_time" in ds.dims:
        dim_map["valid_time"] = "time"
    if "step" in ds.dims:
        dim_map["step"] = "time"
    if dim_map:
        ds = ds.rename(dim_map)

    # Sort dimensions
    for d in ("time", "y", "x"):
        if d in ds.dims:
            ds = ds.sortby(d)

    return ds


def load_radar_zarr(
    store_url: str,
    *,
    rename_map: Optional[Dict[str, str]] = None,
    chunks: Optional[Dict[str, int]] = None,
) -> xr.Dataset:
    """Load radar data (Nimrod/MRMS) from Zarr or NetCDF.

    Args:
        store_url: Path to Zarr store or NetCDF file
        rename_map: Dictionary mapping original variable names to FieldCube names
        chunks: Dask chunk sizes (if None, auto-chunks)

    Returns:
        xarray.Dataset with normalized dimensions and variables

    Example:
        >>> ds = load_radar_zarr(
        ...     "s3://bucket/radar/nimrod.zarr",
        ...     rename_map={"rainrate": "rr", "reflectivity": "dbz"},
        ...     chunks={"time": 24, "y": 512, "x": 512}
        ... )
    """
    ds = _open_any(store_url)
    ds = _normalize_dims(ds)

    # Rename variables
    if rename_map:
        ds = ds.rename({k: v for k, v in rename_map.items() if k in ds})

    # Apply chunking
    if chunks:
        ds = ds.chunk(chunks)
    else:
        # Sensible default chunks
        auto = {}
        if "time" in ds.dims:
            auto["time"] = min(24, ds.sizes["time"])
        if "y" in ds.dims:
            auto["y"] = min(512, ds.sizes["y"])
        if "x" in ds.dims:
            auto["x"] = min(512, ds.sizes["x"])
        try:
            ds = ds.chunk(auto)
        except Exception:
            pass

    return ds
