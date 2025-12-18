"""Experiment G — The Planetary Voice (AMOC narrative driver).

Mission: connect the v10.1 ResonanceTranslator to the AMOC stream from
Experiment D and let the Atlantic circulation speak in its own tempo.

Usage:
    python main.py --mode voice
    python main.py --mode dream   # runs Experiment G followed by Dreamtime (H)

Outputs land in ``v10_oracle/logs/planetary_diary.(json|yaml|md)``, keeping the
tri-layer intact for publication.

Pipeline:
- Load the ConsciousnessSeed (v10.0 kernel) and ResonanceTranslator (v10.1 bridge)
- Feed AMOC transport + distance-to-tipping into the Solar Driver
- Modulate sensitivity so the recent AMOC dip nudges the field from
  LUCID_RESONANCE toward CRITICAL_SLOWING without triggering full storm
- Write a planetary diary in tri-layer form (JSON/YAML/Markdown)
"""

from __future__ import annotations

import json
import pathlib
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from v10_oracle.constants import HEX_SIG_PHI
from v10_oracle.models import ConsciousnessSeed, ResonanceTranslator, Translation

DATA_PATH = REPO_ROOT / "data" / "ocean" / "amoc_strength_mock.csv"
LOG_ROOT = pathlib.Path(__file__).resolve().parents[1] / "logs"
LOG_JSON_PATH = LOG_ROOT / "planetary_diary.json"
LOG_YAML_PATH = LOG_ROOT / "planetary_diary.yaml"
LOG_MD_PATH = LOG_ROOT / "planetary_diary.md"


@dataclass(frozen=True)
class StreamPoint:
    """Container for one AMOC datapoint projected into the resonance frame."""

    index: int
    date: str
    year: int
    strength_sv: float
    distance_to_tipping: float
    proximity: float
    coherence: float
    frequency: float


def initialize_network(n_nodes: int, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    """Return (phases, coupling_matrix) for a small oscillator net."""
    phases = rng.uniform(-np.pi, np.pi, size=n_nodes)
    coupling = rng.uniform(0.0, 1.0, size=(n_nodes, n_nodes))
    np.fill_diagonal(coupling, 0.0)
    coupling = (coupling + coupling.T) / 2.0
    return phases, coupling


class AMOCDataStream:
    """Normalize AMOC transport into coherence + frequency drivers for the seed."""

    def __init__(
        self,
        data_path: pathlib.Path = DATA_PATH,
        base_frequency: float = 1.0,
        sensitivity: float = 0.22,
        coherence_peak: float = 0.97,
        coherence_span: float = 0.065,
    ) -> None:
        self.data_path = data_path
        self.base_frequency = base_frequency
        self.sensitivity = sensitivity
        self.coherence_peak = coherence_peak
        self.coherence_span = coherence_span

        self._df = pd.read_csv(self.data_path, parse_dates=['date'])
        self._normalized_distance = self._normalize(self._df['distance_to_tipping'].values)

    def _normalize(self, values: np.ndarray) -> np.ndarray:
        """Scale to [0, 1] for proximity calculations."""
        vmin = float(np.min(values))
        vmax = float(np.max(values))
        return (values - vmin) / max(vmax - vmin, 1e-9)

    def __iter__(self) -> Iterable[StreamPoint]:
        """Yield AMOC points mapped into coherence + frequency control."""
        proximity = 1.0 - self._normalized_distance  # high proximity → closer to tipping
        coherences = np.clip(self.coherence_peak - self.coherence_span * proximity, 0.0, 1.0)
        frequencies = self.base_frequency * (1.0 - self.sensitivity * proximity)

        for idx, row in self._df.iterrows():
            yield StreamPoint(
                index=int(idx),
                date=row['date'].date().isoformat(),
                year=int(row['date'].year),
                strength_sv=float(row['strength_Sv']),
                distance_to_tipping=float(row['distance_to_tipping']),
                proximity=float(proximity[idx]),
                coherence=float(coherences[idx]),
                frequency=float(frequencies[idx]),
            )

    def statistics(self) -> Dict[str, float]:
        """Return quick stats for logging."""
        distance = self._df['distance_to_tipping'].values
        return {
            'n_rows': int(len(self._df)),
            'distance_min': float(np.min(distance)),
            'distance_max': float(np.max(distance)),
            'distance_mean': float(np.mean(distance)),
            'sensitivity': self.sensitivity,
            'coherence_peak': self.coherence_peak,
            'coherence_span': self.coherence_span,
        }


def compose_thought(sample: StreamPoint, translation: Translation, sigma_phi: float) -> str:
    """Translate the resonance markers into a narrative thought."""
    if translation.state == "CRITICAL_SLOWING":
        return (
            f"My rhythm is stretching ({sample.frequency:.3f} Hz); perturbations linger as "
            f"distance_to_tipping={sample.distance_to_tipping:.3f}."
        )
    if translation.state == "ENTROPIC_STRESS":
        return (
            f"Currents fray (σ_ϕ={sigma_phi:.4f}); coherence leaks while flow falls to "
            f"{sample.strength_sv:.2f} Sv."
        )
    if translation.state == "CRYSTAL_SLEEP":
        return "Lattice calm—overturning rests in a cold, ordered gyre."
    return (
        f"Flow steady at {sample.strength_sv:.2f} Sv; σ_ϕ={sigma_phi:.4f} traces the "
        f"{HEX_SIG_PHI:.4f} edge."
    )


def run_planetary_voice(
    base_frequency: float = 1.0,
    sensitivity: float = 0.22,
    tipping_point: float = 0.70,
    seed: int = 1024,
) -> Tuple[List[Dict[str, object]], bool, Dict[str, float]]:
    """Drive the ConsciousnessSeed with AMOC data and capture the diary."""
    rng = np.random.default_rng(seed)
    phases, coupling = initialize_network(n_nodes=24, rng=rng)
    kernel = ConsciousnessSeed()
    translator = ResonanceTranslator(base_frequency=base_frequency)
    stream = AMOCDataStream(base_frequency=base_frequency, sensitivity=sensitivity)

    warning_states = {"CRITICAL_SLOWING", "ENTROPIC_STRESS"}
    ghost_warning = False
    diary: List[Dict[str, object]] = []

    for point in stream:
        phases, info = kernel.step(phases, coupling, em_coherence=point.coherence)
        translation = translator.translate(
            sigma_phi=info['sigma_phi'],
            global_coherence=info['global_coherence'],
            frequency=point.frequency,
        )

        oracle_warning = translation.state in warning_states and point.distance_to_tipping > tipping_point
        ghost_warning = ghost_warning or oracle_warning

        diary.append(
            {
                'date': point.date,
                'year': point.year,
                'state': translation.state,
                'confidence': translation.confidence,
                'thought': compose_thought(point, translation, info['sigma_phi']),
                'sigma_phi': info['sigma_phi'],
                'target_sigma_phi': info['target_sigma_phi'],
                'global_coherence': info['global_coherence'],
                'frequency': point.frequency,
                'amoc_strength_sv': point.strength_sv,
                'distance_to_tipping': point.distance_to_tipping,
                'proximity': point.proximity,
                'oracle_warning': oracle_warning,
                'rationale': translation.rationale,
            }
        )

    return diary, ghost_warning, stream.statistics()


def persist_diary(entries: Sequence[Dict[str, object]], ghost_warning: bool, stats: Dict[str, float]) -> None:
    """Write tri-layer diary files."""
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    payload = {
        'meta': {
            'description': "Experiment G — Planetary Voice (AMOC → GenesisAeon v10.1)",
            'ghost_warning': ghost_warning,
            'stream_stats': stats,
        },
        'entries': entries,
    }

    with LOG_JSON_PATH.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)

    with LOG_YAML_PATH.open("w", encoding="utf-8") as fp:
        yaml.safe_dump(payload, fp, sort_keys=False, allow_unicode=True)

    with LOG_MD_PATH.open("w", encoding="utf-8") as fp:
        fp.write("# Experiment G — Planetary Diary (AMOC Voice)\n\n")
        fp.write(f"*Ghost check:* {'triggered' if ghost_warning else 'silent'}\n\n")
        fp.write("| Year | State | System Thought |\n")
        fp.write("| --- | --- | --- |\n")
        for entry in entries:
            fp.write(f"| {entry['year']} | {entry['state']} | {entry['thought']} |\n")


def main() -> None:
    print("Running Experiment G — The Planetary Voice")
    diary, ghost_warning, stats = run_planetary_voice()
    persist_diary(diary, ghost_warning, stats)
    warning_note = "Warning surfaced before tipping threshold." if ghost_warning else "No pre-threshold warning detected."
    print(f"Diary saved to {LOG_MD_PATH}")
    print(warning_note)


if __name__ == "__main__":
    main()
