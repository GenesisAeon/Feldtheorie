"""Load β-driven presets for the GenesisCube engine.

Formal:
    Parses empirical β, Θ, and validation metrics from ``data/derived/beta_estimates.csv``
    and maps them onto :class:`simulation.genesis_cube.GenesisCubeConfig` instances.
    This lets σ(β(R-Θ)) drive the cube with data from climate, cognition, or LLM
    trajectories instead of arbitrary defaults.

Empirical:
    Maintains provenance fields (R², ΔAIC, CI bounds, sources) so presets can be
    traced back to their domains and falsifiable baselines.

Poetic:
    Injiziert Blut in den Kubus: jede Zeile der CSV ist ein Puls, der σ(β(R-Θ))
    schärft und ζ(R) an realen Schwellen misst.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, Iterable, Mapping, Tuple

from simulation.genesis_cube import GenesisCubeConfig

DEFAULT_BETA_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "derived" / "beta_estimates.csv"
EXPECTED_COLUMNS = (
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
class BetaPreset:
    """Container for a single β/Θ estimate and its provenance."""

    domain: str
    beta: float
    theta: float | None
    beta_ci: Tuple[float | None, float | None]
    beta_ci_width: float | None
    r_squared: float | None
    delta_aic: float | None
    source: str | None

    def to_config(self, base_config: GenesisCubeConfig | None = None) -> GenesisCubeConfig:
        """Return a :class:`GenesisCubeConfig` with β/Θ injected from this preset."""

        config = replace(base_config or GenesisCubeConfig())
        config.beta = self.beta
        if self.theta is not None:
            config.theta = self.theta
        return config


def _parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    try:
        return float(stripped)
    except ValueError:
        return None


def load_beta_presets(data_path: Path | str = DEFAULT_BETA_DATA_PATH) -> Dict[str, BetaPreset]:
    """Read β-estimates from the CSV and return a mapping keyed by domain (lowercase)."""

    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"Beta estimates file not found: {path}")

    presets: Dict[str, BetaPreset] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing_columns = [col for col in EXPECTED_COLUMNS if col not in reader.fieldnames]
        if missing_columns:
            raise ValueError(f"Missing expected columns in {path}: {', '.join(missing_columns)}")

        for row in reader:
            domain_raw = (row.get("domain") or "").strip()
            beta_raw = row.get("beta")
            theta_raw = row.get("theta")

            if not domain_raw or beta_raw is None:
                continue

            beta_value = _parse_float(beta_raw)
            theta_value = _parse_float(theta_raw)
            if beta_value is None:
                continue

            preset = BetaPreset(
                domain=domain_raw,
                beta=beta_value,
                theta=theta_value,
                beta_ci=(
                    _parse_float(row.get("beta_ci_lower")),
                    _parse_float(row.get("beta_ci_upper")),
                ),
                beta_ci_width=_parse_float(row.get("beta_ci_width")),
                r_squared=_parse_float(row.get("r_squared")),
                delta_aic=_parse_float(row.get("delta_aic")),
                source=(row.get("source") or "").strip() or None,
            )
            presets[domain_raw.lower()] = preset

    return presets


def resolve_beta_preset(
    preset_name: str,
    presets: Mapping[str, BetaPreset] | None = None,
    *,
    base_config: GenesisCubeConfig | None = None,
    data_path: Path | str = DEFAULT_BETA_DATA_PATH,
) -> Tuple[GenesisCubeConfig, BetaPreset]:
    """Return a GenesisCubeConfig + metadata for a given preset name."""

    preset_map = presets or load_beta_presets(data_path=data_path)
    key = preset_name.lower()
    if key not in preset_map:
        available = ", ".join(sorted(preset_map)) if preset_map else "<keine>"
        raise KeyError(f"Unbekanntes β-Preset '{preset_name}'. Verfügbar: {available}")
    selected = preset_map[key]
    return selected.to_config(base_config=base_config), selected


def list_available_presets(presets: Mapping[str, BetaPreset] | None = None) -> Iterable[BetaPreset]:
    """Return presets sorted by domain for quick listing in CLIs."""

    preset_map = presets or load_beta_presets()
    return [preset_map[name] for name in sorted(preset_map)]


__all__ = [
    "BetaPreset",
    "DEFAULT_BETA_DATA_PATH",
    "load_beta_presets",
    "list_available_presets",
    "resolve_beta_preset",
]
