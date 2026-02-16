"""Helper to load modules from the root Feldtheorie models/ package.

v9_alpha/models/ shadows the root models/ package on sys.path.  This helper
resolves the collision by bootstrapping the root models package properly so
that relative imports within root modules work.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

_ROOT_MODELS = Path(__file__).resolve().parents[2] / "models"
_ROOT_PKG_NAME = "_root_models"


def _ensure_root_package() -> types.ModuleType:
    """Register the root models/ directory as ``_root_models`` in sys.modules."""
    if _ROOT_PKG_NAME in sys.modules:
        return sys.modules[_ROOT_PKG_NAME]

    init = _ROOT_MODELS / "__init__.py"
    spec = importlib.util.spec_from_file_location(
        _ROOT_PKG_NAME,
        init,
        submodule_search_locations=[str(_ROOT_MODELS)],
    )
    pkg = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules[_ROOT_PKG_NAME] = pkg
    spec.loader.exec_module(pkg)  # type: ignore[union-attr]
    return pkg


def load_root_module(name: str) -> types.ModuleType:
    """Load ``models/<name>.py`` from the Feldtheorie root.

    The module is loaded as a submodule of ``_root_models`` so that
    relative imports (``from .unified_constants import ...``) resolve
    correctly within the root models package.
    """
    fqn = f"{_ROOT_PKG_NAME}.{name}"
    if fqn in sys.modules:
        return sys.modules[fqn]

    _ensure_root_package()

    src = _ROOT_MODELS / f"{name}.py"
    if not src.exists():
        raise ImportError(f"Root module models/{name}.py not found at {src}")

    spec = importlib.util.spec_from_file_location(fqn, src)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    mod.__package__ = _ROOT_PKG_NAME
    sys.modules[fqn] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod
