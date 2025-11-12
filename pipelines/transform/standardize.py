"""
FieldCube Standardization for Feldtheorie

to_fieldcube(ds, attrs, enforce_cf=True):
- Unifies coordinates (time, lat, lon / y, x)
- Enforces CF-like metadata, sets global attributes
- Normalizes unit fields (attribute-level only; hard conversion with pint-xarray can be added later)
"""
from __future__ import annotations
from typing import Dict, Optional
import xarray as xr

_CF_LAT_NAMES = ("latitude", "lat", "y", "rlat")
_CF_LON_NAMES = ("longitude", "lon", "x", "rlon")
_CF_TIME_NAMES = ("time", "valid_time", "forecast_time")


def _coerce_axes(ds: xr.Dataset) -> xr.Dataset:
    """Coerce dimension names to lat/lon/time standard."""
    rename = {}

    # Find and rename latitude dimension
    for cand in _CF_LAT_NAMES:
        if cand in ds.coords or cand in ds.dims:
            rename[cand] = "lat"
            break

    # Find and rename longitude dimension
    for cand in _CF_LON_NAMES:
        if cand in ds.coords or cand in ds.dims:
            rename[cand] = "lon"
            break

    # Find and rename time dimension
    for cand in _CF_TIME_NAMES:
        if cand in ds.coords or cand in ds.dims:
            rename[cand] = "time"
            break

    if rename:
        ds = ds.rename({k: v for k, v in rename.items() if k in ds})

    # Sort dimensions
    for d in ("time", "lat", "lon"):
        if d in ds.dims:
            ds = ds.sortby(d)

    return ds


def _ensure_cf_attrs(ds: xr.Dataset) -> xr.Dataset:
    """Add CF-compliant attributes to coordinates."""
    if "lat" in ds.coords:
        ds["lat"] = ds["lat"].assign_attrs({
            "standard_name": "latitude",
            "units": "degrees_north"
        })
    if "lon" in ds.coords:
        ds["lon"] = ds["lon"].assign_attrs({
            "standard_name": "longitude",
            "units": "degrees_east"
        })
    if "time" in ds.coords:
        ds["time"] = ds["time"].assign_attrs({
            "standard_name": "time"
        })

    return ds


def to_fieldcube(
    ds: xr.Dataset,
    *,
    global_attrs: Optional[Dict[str, str]] = None,
    enforce_cf: bool = True,
) -> xr.Dataset:
    """Convert dataset to Feldtheorie FieldCube standard.

    Args:
        ds: Input xarray.Dataset
        global_attrs: Dictionary of global attributes to add
        enforce_cf: Whether to enforce CF-compliant coordinate attributes

    Returns:
        Standardized xarray.Dataset

    Example:
        >>> ds = xr.open_zarr("raw_icon_eu.zarr")
        >>> fc = to_fieldcube(ds, global_attrs={
        ...     "source": "ICON-EU via OCF",
        ...     "institution": "GenesisAeon/Feldtheorie",
        ... })
    """
    ds = _coerce_axes(ds)

    if enforce_cf:
        ds = _ensure_cf_attrs(ds)

    # Add global attributes
    base_attrs = {
        "title": "Feldtheorie FieldCube",
        "Conventions": "CF-1.10",
        "history": "created by Feldtheorie pipelines/transform/standardize.py",
    }
    if global_attrs:
        base_attrs.update(global_attrs)

    ds = ds.assign_attrs(base_attrs)

    return ds
