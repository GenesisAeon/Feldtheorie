"""Load β-driven GenesisCube presets from empirical CSV estimates.

Formal:
    Bridges the logistic σ(β(R-Θ)) driver in ``GenesisCube`` to empirical
    β/Θ estimates gathered across domains. The loader accepts mildly malformed
    CSV rows (line-wrapped sources) so that presets remain usable even when
    the data stream is noisy.

Empirical:
    Reads ``data/derived/beta_estimates.csv`` (or a provided path) and
    returns structured ``GenesisPreset`` objects with β, optional Θ, source
    metadata, and helper utilities to build ``GenesisCubeConfig`` snapshots.

Poetic:
    Wir injizieren das Blut der 78 Systeme in den Kubus: jede Zeile trägt
    ihr eigenes β, das σ(β(R-Θ)) schärft, während ζ(R) die Membran dämpft.
    Selbst wenn die Quelle über Zeilen ausfranst, bleibt der Atem kohärent.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, Iterable, List, Mapping

from .genesis_cube import GenesisCubeConfig

DEFAULT_BETA_ESTIMATES = Path(__file__).resolve().parents[1] / "data/derived/beta_estimates.csv"
EXPECTED_FIELDS = (
    "domain",
    "beta",
    "beta_ci_lower",
    "beta_ci_upper",
    "beta_ci_width",
    "theta",
    "r_squared",
    "delta_aic",
    "source",
)


@dataclass(frozen=True)
class GenesisPreset:
    """A β/Θ preset that can be injected into a ``GenesisCubeConfig``."""

    name: str
    beta: float
    theta: float | None = None
    source: str | None = None

    def apply_to_config(self, base: GenesisCubeConfig | None = None) -> GenesisCubeConfig:
        """Return a new config with β (and optional Θ) from this preset."""

        config = base or GenesisCubeConfig()
        updates = {"beta": self.beta}
        if self.theta is not None:
            updates["theta"] = self.theta
        return replace(config, **updates)


def _parse_float(value: str | None) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except ValueError:
        return None


def load_beta_presets(csv_path: Path | str = DEFAULT_BETA_ESTIMATES) -> List[GenesisPreset]:
    """Load β presets from the empirical CSV, skipping malformed rows.

    The CSV occasionally contains line-wrapped sources or truncated rows.
    We keep any row with a non-empty, non-numeric domain and a parsable β;
    all other rows are skipped to keep σ(β(R-Θ)) clean.
    """

    path = Path(csv_path)
    presets: List[GenesisPreset] = []

    if not path.exists():
        raise FileNotFoundError(f"Beta estimate file not found: {path}")

    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, fieldnames=None)
        # Ensure header alignment if the file provides custom fields
        if reader.fieldnames is None or tuple(reader.fieldnames) != EXPECTED_FIELDS:
            reader.fieldnames = list(EXPECTED_FIELDS)

        for row in reader:
            name = (row.get("domain") or "").strip()
            beta_value = _parse_float(row.get("beta"))

            if not name or name.isnumeric() or beta_value is None:
                continue

            theta_value = _parse_float(row.get("theta"))
            source_value = (row.get("source") or "").strip() or None

            presets.append(
                GenesisPreset(
                    name=name,
                    beta=beta_value,
                    theta=theta_value,
                    source=source_value,
                )
            )

    return presets


def _normalize(name: str) -> str:
    return name.lower().replace("-", "_").replace(" ", "_")


def index_presets(presets: Iterable[GenesisPreset]) -> Dict[str, GenesisPreset]:
    """Create a normalized lookup table for presets."""

    indexed: Dict[str, GenesisPreset] = {}
    for preset in presets:
        indexed[_normalize(preset.name)] = preset
    return indexed


def resolve_preset(name: str, preset_index: Mapping[str, GenesisPreset]) -> GenesisPreset:
    """Resolve a preset by name (case-/separator-insensitive)."""

    normalized = _normalize(name)
    try:
        return preset_index[normalized]
    except KeyError as exc:
        available = ", ".join(sorted(preset_index))
        raise KeyError(f"Preset '{name}' not found. Available: {available}") from exc


__all__ = [
    "DEFAULT_BETA_ESTIMATES",
    "GenesisPreset",
    "index_presets",
    "load_beta_presets",
    "resolve_preset",
]
