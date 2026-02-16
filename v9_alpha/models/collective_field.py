"""Shim: re-export from root Feldtheorie models/collective_field.py."""
from v9_alpha.models._root_shim import load_root_module as _load

globals().update(
    {k: v for k, v in vars(_load("collective_field")).items() if not k.startswith("_")}
)
