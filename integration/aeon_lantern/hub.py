"""Aeon-Lantern integration hub with optional sonification and VR map export."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from aeon.api_bridge import AeonLanternAsyncBridge

try:
    import mido
except ImportError:  # pragma: no cover
    mido = None

try:
    import plotly.graph_objects as go
except ImportError:  # pragma: no cover
    go = None


@dataclass
class QuartzOscillatorSim:
    frequency_hz: float = 13.5e6
    jitter_ppm: float = 2.0


class AeonLanternHub:
    """End-to-end coordinator for nested Aeon↔lanternNet coupling."""

    def __init__(self, bridge: AeonLanternAsyncBridge, oscillator: QuartzOscillatorSim | None = None) -> None:
        self.bridge = bridge
        self.oscillator = oscillator or QuartzOscillatorSim()

    def run_cascade(self, datasets: list[np.ndarray], n_crit: int = 137) -> dict[str, Any]:
        cascades = 0
        coherence_scores: list[float] = []
        for data in datasets:
            self.bridge.ingest_em_frame(np.asarray(data, dtype=np.float64))
            coherence = float(np.clip(np.mean(np.abs(data)), 0.0, 1.0))
            coherence_scores.append(coherence)
            if coherence > 0.7:
                cascades += 1
        return {
            "dataset_count": len(datasets),
            "cascades": cascades,
            "n_crit_reached": cascades >= n_crit,
            "mean_coherence": float(np.mean(coherence_scores) if coherence_scores else 0.0),
        }

    def coherence_to_midi(self, coherence: float) -> list[int]:
        pitch = int(np.clip(36 + coherence * 60, 36, 96))
        if mido is None:
            return [pitch]
        msg = mido.Message("note_on", note=pitch, velocity=100)
        return [msg.note]

    def build_vr_teaser_points(self, embeddings: np.ndarray) -> dict[str, Any]:
        points = np.asarray(embeddings, dtype=np.float64)
        payload = {"x": points[:, 0].tolist(), "y": points[:, 1].tolist(), "z": points[:, 2].tolist()}
        if go is None:
            return payload
        fig = go.Figure(data=[go.Scatter3d(x=payload["x"], y=payload["y"], z=payload["z"], mode="markers")])
        payload["plotly_traces"] = len(fig.data)
        return payload
