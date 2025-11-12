"""
Zarr Storage/Reading for Feldtheorie

write_zarr(ds, path, mode="w", consolidated=True):
- Writes Dataset as Zarr (with Consolidated Metadata)

read_zarr(path):
- Efficiently loads Zarr
"""
from __future__ import annotations
from typing import Optional
import xarray as xr
import zarr
import fsspec


def write_zarr(
    ds: xr.Dataset,
    path: str,
    *,
    mode: str = "w",
    consolidated: bool = True,
    compressor: Optional[zarr.codecs.Codec] = None,
) -> None:
    """Write xarray.Dataset to Zarr store.

    Args:
        ds: Dataset to write
        path: Path to Zarr store (local or remote via fsspec)
        mode: Write mode ("w" = overwrite, "a" = append)
        consolidated: Whether to consolidate metadata
        compressor: Zarr compressor (default: Zstd level 3)

    Example:
        >>> ds = xr.open_zarr("input.zarr")
        >>> write_zarr(ds, "output.zarr", mode="w", consolidated=True)
    """
    # Default compressor: Zstd level 3
    if compressor is None:
        compressor = zarr.codecs.Zstd(level=3)

    # Apply compressor to all variables
    encoding = {}
    for var in list(ds.data_vars) + list(ds.coords):
        encoding[var] = {"compressor": compressor}

    mapper = fsspec.get_mapper(path)
    ds.to_zarr(mapper, mode=mode, consolidated=consolidated, encoding=encoding)


def read_zarr(path: str, *, consolidated: bool = True) -> xr.Dataset:
    """Read Zarr store into xarray.Dataset.

    Args:
        path: Path to Zarr store
        consolidated: Whether to use consolidated metadata

    Returns:
        Lazy-loaded xarray.Dataset

    Example:
        >>> ds = read_zarr("fieldcube.zarr")
        >>> print(ds)
    """
    mapper = fsspec.get_mapper(path)
    return xr.open_zarr(mapper, consolidated=consolidated)
