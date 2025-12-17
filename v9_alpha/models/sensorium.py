"""Sensorium utilities for multi-stream climate/economic cognition.

Provides the MultiStreamLoader and DataStream types originally prototyped in
`v9_alpha/demos/sensorium.py`. Streams follow the Trilayer principle: structured
(normalized arrays), semantic labels, and narrative-ready summaries.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import numpy as np
import pandas as pd
import yaml


@dataclass
class DataStream:
    """Normalized time-series wrapper."""

    name: str
    values: np.ndarray
    normalization: str = "minmax"
    invert: bool = False
    time_index: Optional[np.ndarray] = None

    def __post_init__(self) -> None:
        normalized = self._normalize(self.values)
        self.values = 1.0 - normalized if self.invert else normalized
        self.length = len(self.values)
        self.current_index = 0

    def _normalize(self, values: np.ndarray) -> np.ndarray:
        if self.normalization == "raw":
            return values.astype(float)
        if self.normalization == "zscore":
            mean = float(np.mean(values))
            std = float(np.std(values))
            if std < 1e-12:
                return np.zeros_like(values, dtype=float)
            return (values - mean) / std
        vmin = float(np.min(values))
        vmax = float(np.max(values))
        if abs(vmax - vmin) < 1e-12:
            return np.zeros_like(values, dtype=float)
        return (values - vmin) / (vmax - vmin)

    def step(self) -> float:
        value = float(self.values[self.current_index % self.length])
        self.current_index = (self.current_index + 1) % self.length
        return value

    def get_full(self) -> np.ndarray:
        return self.values.copy()

    def reset(self) -> None:
        self.current_index = 0


class MultiStreamLoader:
    """Load and synchronize multiple stress signals.

    Each stream can point to a CSV (value_column required) or request a
    synthetic proxy. Streams are combined via σ(β(R-Θ)) = (Σ stress_i) +
    coupling_factor * Π stress_i, capturing both additive pressure and
    interference.
    """

    def __init__(
        self,
        stream_configs: Iterable[Dict],
        default_length: int = 512,
        coupling_factor: float = 0.3,
        seed: int = 42,
    ):
        self.default_length = default_length
        self.coupling_factor = coupling_factor
        self.rng = np.random.default_rng(seed)
        self.streams: Dict[str, DataStream] = {}

        for cfg in stream_configs:
            stream = self._build_stream(cfg)
            self.streams[stream.name] = stream

        if not self.streams:
            raise ValueError("MultiStreamLoader requires at least one stream.")

        self.length = max(stream.length for stream in self.streams.values())

    def _build_stream(self, cfg: Dict) -> DataStream:
        name = cfg.get("name", f"stream_{len(self.streams)}")
        normalization = cfg.get("normalization", "minmax")
        invert = cfg.get("invert", False)

        if cfg.get("path") and cfg.get("value_column") and os.path.exists(cfg["path"]):
            try:
                values, time_index = self._load_from_csv(cfg["path"], cfg["value_column"], cfg.get("time_column"))
            except Exception:
                values, time_index = self._synthetic_signal(cfg)
        else:
            values, time_index = self._synthetic_signal(cfg)

        return DataStream(
            name=name,
            values=values,
            normalization=normalization,
            invert=invert,
            time_index=time_index,
        )

    def _load_from_csv(self, path: str, value_column: str, time_column: Optional[str]) -> tuple[np.ndarray, Optional[np.ndarray]]:
        df = pd.read_csv(path)
        if value_column not in df.columns:
            raise ValueError(f"Column '{value_column}' not found in {path}")
        values = df[value_column].to_numpy(dtype=float)
        time_index = pd.to_datetime(df[time_column]).to_numpy() if time_column and time_column in df.columns else None
        return values, time_index

    def _synthetic_signal(self, cfg: Dict) -> tuple[np.ndarray, None]:
        length = int(cfg.get("length", self.default_length))
        base = cfg.get("synthetic_base", "seasonal")
        trend_strength = float(cfg.get("trend_strength", 0.15))
        seasonal_freq = float(cfg.get("seasonal_freq", 0.05))
        noise_level = float(cfg.get("noise_level", 0.08))

        x = np.linspace(0, 2 * np.pi, num=length)
        if base == "pulse":
            values = np.sin(x * seasonal_freq * length) ** 2
        else:
            values = 0.5 + 0.5 * np.sin(x * seasonal_freq * length)

        trend = trend_strength * np.linspace(0, 1, num=length)
        noise = self.rng.normal(0, noise_level, size=length)
        synthetic = np.clip(values + trend + noise, 0.0, 1.0)
        return synthetic, None

    def step(self) -> Dict:
        inputs = {name: stream.step() for name, stream in self.streams.items()}
        additive = sum(inputs.values())
        interaction = self.coupling_factor * self._interaction_term(inputs.values())
        combined = additive + interaction
        return {
            "inputs": inputs,
            "additive": additive,
            "interaction": interaction,
            "combined_stress": combined,
        }

    def _interaction_term(self, values: Iterable[float]) -> float:
        product = 1.0
        for v in values:
            product *= v
        return product

    def reset(self) -> None:
        for stream in self.streams.values():
            stream.reset()

    def summary(self) -> Dict:
        return {
            "n_streams": len(self.streams),
            "coupling_factor": self.coupling_factor,
            "length": self.length,
            "streams": {name: {"length": stream.length, "normalization": stream.normalization, "invert": stream.invert} for name, stream in self.streams.items()},
        }


def load_stream_configs(path: Path) -> List[Dict]:
    """Load stream configs from YAML or JSON."""
    if not path.exists():
        raise FileNotFoundError(f"Stream config not found: {path}")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(path.read_text())
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text())
    raise ValueError(f"Unsupported config format for {path}")


__all__ = ["DataStream", "MultiStreamLoader", "load_stream_configs"]
