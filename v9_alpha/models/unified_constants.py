"""Shim: re-export from root Feldtheorie models/unified_constants.py."""
from v9_alpha.models._root_shim import load_root_module as _load

globals().update(
    {k: v for k, v in vars(_load("unified_constants")).items() if not k.startswith("_")}
)
