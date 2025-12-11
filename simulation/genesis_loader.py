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

import logging
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from pathlib import Path

import pandas as pd

from .genesis_cube import GenesisCubeConfig

logger = logging.getLogger(__name__)

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
    domain: str | None = None
    description: str | None = None
    color_hex: str | None = None

    def apply_to_config(self, base: GenesisCubeConfig | None = None) -> GenesisCubeConfig:
        """Return a new config with β (and optional Θ) from this preset."""

        config = base or GenesisCubeConfig()
        updates = {"beta": self.beta}
        if self.theta is not None:
            updates["theta"] = self.theta
        return replace(config, **updates)


def _parse_float(value: str | float | None) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _normalize(name: str) -> str:
    return name.lower().replace("-", "_").replace(" ", "_")


def _safe_strip(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if hasattr(value, "strip"):
        return str(value).strip()
    return str(value).strip()


class GenesisLoader:
    """Lädt β/Θ-Presets aus CSV-Daten und färbt sie für die Visualisierung.

    The class API mirrors the functional helpers in this module but adds
    resilience: if the data path is missing or malformed, a small set of
    mock presets keeps the σ(β(R-Θ))-pipeline operational.
    """

    def __init__(self, data_path: Path | str = DEFAULT_BETA_ESTIMATES) -> None:
        self.data_path = Path(data_path)
        self.presets: dict[str, GenesisPreset] = {}

    def load(self) -> list[GenesisPreset]:
        """Load presets from disk or fall back to mock entries."""

        if not self.data_path.exists():
            logger.warning(
                "Beta estimate file missing: %s. Falling back to mock presets.", self.data_path
            )
            return self._generate_mock_presets()

        try:
            df = pd.read_csv(self.data_path)
            return self._load_from_dataframe(df)
        except Exception as exc:  # pragma: no cover - defensive guard
            logger.error("Fehler beim Laden der Daten: %s", exc)
            return self._generate_mock_presets()

    def get(self, system_name_query: str) -> GenesisPreset | None:
        """Resolve a preset by exact or substring query."""

        if not self.presets:
            self.load()

        normalized_query = _normalize(system_name_query)
        if normalized_query in self.presets:
            return self.presets[normalized_query]

        for key, preset in self.presets.items():
            if normalized_query in key:
                return preset

        logger.warning("Kein Preset für '%s' gefunden.", system_name_query)
        return None

    def list_domains(self) -> list[str]:
        """Return unique domains across loaded presets."""

        if not self.presets:
            self.load()
        return sorted({preset.domain for preset in self.presets.values() if preset.domain})

    def _load_from_dataframe(self, df: pd.DataFrame) -> list[GenesisPreset]:
        presets: dict[str, GenesisPreset] = {}
        missing = {"domain", "beta"} - set(df.columns)

        if missing:
            logger.warning(
                "CSV fehlt Felder %s – Versuche Header zu normalisieren.",
                ", ".join(sorted(missing)),
            )
            df = self._normalize_columns(df)

        for row in df.to_dict(orient="records"):
            name = _safe_strip(row.get("system_name")) or _safe_strip(row.get("domain")) or ""
            beta_value = _parse_float(row.get("beta") or row.get("beta_estimate"))

            if not name or name.isnumeric() or beta_value is None:
                continue

            theta_value = _parse_float(row.get("theta"))
            domain = _safe_strip(row.get("domain")) or "Generic"
            source_value = _safe_strip(row.get("source"))
            color = self._derive_color(domain, beta_value, provided=row.get("color"))
            description = (
                _safe_strip(row.get("description"))
                or f"Simuliert {name} mit Kritikalität β={beta_value:.2f}"
            )

            preset = GenesisPreset(
                name=name,
                beta=beta_value,
                theta=theta_value,
                source=source_value,
                domain=domain,
                description=description,
                color_hex=color,
            )
            presets[_normalize(name)] = preset

        self.presets = presets
        logger.info("✅ %s Presets aus %s geladen.", len(self.presets), self.data_path)
        return list(presets.values())

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        alias_map = {
            "beta_estimate": "beta",
            "system": "domain",
            "name": "domain",
        }
        renamed = df.rename(columns=alias_map)
        for column in EXPECTED_FIELDS:
            if column not in renamed.columns:
                renamed[column] = None
        return renamed[[col for col in EXPECTED_FIELDS if col in renamed.columns]]

    def _derive_color(self, domain: str, beta: float, provided: str | None = None) -> str:
        if provided and isinstance(provided, str) and provided.strip():
            return provided.strip()

        domain_colors = {
            "information": "#00ffff",
            "biology": "#00ff00",
            "climate": "#ff4500",
            "social": "#ff00ff",
            "cosmic": "#ffffff",
        }
        for key, color in domain_colors.items():
            if key in domain.lower():
                return color

        if beta < 3:
            return "#ff0000"
        if beta < 6:
            return "#ffa500"
        return "#1e90ff"

    def _generate_mock_presets(self) -> list[GenesisPreset]:
        mocks = [
            ("LLM_Consciousness", "Information", 4.23, "#00ffff"),
            ("Amazon_Rainforest", "Climate", 11.09, "#00ff00"),
            ("Stock_Market_Crash", "Social", 2.50, "#ff0000"),
            ("Cosmic_Void", "Cosmic", 137.036, "#ffffff"),
        ]
        presets = {}
        for name, dom, beta_value, col in mocks:
            presets[_normalize(name)] = GenesisPreset(
                name=name,
                beta=beta_value,
                domain=dom,
                description="Mock Data",
                color_hex=col,
            )
        self.presets = presets
        return list(presets.values())


def index_presets(presets: Iterable[GenesisPreset]) -> dict[str, GenesisPreset]:
    """Create a normalized lookup table for presets."""

    indexed: dict[str, GenesisPreset] = {}
    for preset in presets:
        indexed[_normalize(preset.name)] = preset
    return indexed


def resolve_preset(name: str, preset_index: Mapping[str, GenesisPreset]) -> GenesisPreset:
    """Resolve a preset by name (case-/separator-insensitive).

    Falls kein exakter Treffer existiert, wird eine Substring-Suche
    durchgeführt, um robuste CLI-Abfragen zu ermöglichen (``--preset Amazon``
    findet z.B. ``climate_amazon``).
    """

    normalized = _normalize(name)
    if normalized in preset_index:
        return preset_index[normalized]

    for key, preset in preset_index.items():
        if normalized in key:
            return preset

    available = ", ".join(sorted(preset_index))
    raise KeyError(f"Preset '{name}' not found. Available: {available}")


def load_beta_presets(csv_path: Path | str = DEFAULT_BETA_ESTIMATES) -> list[GenesisPreset]:
    """Load β presets from the empirical CSV or return mocks on failure."""

    loader = GenesisLoader(csv_path)
    return loader.load()


__all__ = [
    "DEFAULT_BETA_ESTIMATES",
    "GenesisLoader",
    "GenesisPreset",
    "index_presets",
    "load_beta_presets",
    "resolve_preset",
]
