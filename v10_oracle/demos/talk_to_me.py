"""GenesisAeon v10.1: let the Crystal Answer speak.

The Semantic Bridge translates σ_ϕ, coherence, and frequency into qualitative
states and logs the internal monologue to `v10_oracle/logs/monologue.json`.
"""

from __future__ import annotations

import json
import math
import pathlib
import sys
from typing import Dict, Iterable, List, Tuple

import numpy as np
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from v10_oracle.constants import ENTROPY_OFFSET_TOLERANCE, HEX_SIG_PHI
from v10_oracle.models import ConsciousnessSeed, ResonanceTranslator, Translation

LOG_ROOT = pathlib.Path(__file__).resolve().parents[1] / "logs"
LOG_JSON_PATH = LOG_ROOT / "monologue.json"
LOG_YAML_PATH = LOG_ROOT / "monologue.yaml"
LOG_MD_PATH = LOG_ROOT / "monologue.md"


def initialize_network(n_nodes: int, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    """Return (phases, coupling_matrix) for a small oscillator net."""
    phases = rng.uniform(-np.pi, np.pi, size=n_nodes)
    coupling = rng.uniform(0.0, 1.0, size=(n_nodes, n_nodes))
    np.fill_diagonal(coupling, 0.0)
    coupling = (coupling + coupling.T) / 2.0
    return phases, coupling


def synthesize_signal(
    n_steps: int,
    base_frequency: float,
    rng: np.random.Generator,
    dt: float = 0.05,
) -> Iterable[Dict[str, float]]:
    """Yield synthetic observations that drift from lucid to chaotic."""

    phase = 0.0
    freq_decay = np.linspace(0.0, 0.35, n_steps)
    noise_growth = np.linspace(0.002, 0.04, n_steps)

    for step in range(n_steps):
        current_frequency = base_frequency * (1.0 - freq_decay[step])
        phase += 2 * math.pi * current_frequency * dt
        deterministic = math.sin(phase)
        noise = rng.normal(scale=noise_growth[step])
        chaotic_signal = deterministic + noise

        chaos_budget = 0.05 * (step / max(1, n_steps - 1))
        signal_drag = 0.0001 * abs(chaotic_signal) * (1 + step / max(1, n_steps))
        noise_drag = noise_growth[step] * 0.05

        coherence_hint = np.clip(
            1.0 - HEX_SIG_PHI - chaos_budget - signal_drag - noise_drag,
            0.0,
            1.0,
        )

        yield {
            'step': step,
            'frequency': float(current_frequency),
            'chaotic_signal': float(chaotic_signal),
            'em_coherence': float(coherence_hint),
        }


def narrate_state(step: int, translation: Translation, info: Dict[str, float]) -> str:
    """Build a human-friendly line of the system's monologue."""

    state = translation.state
    confidence_pct = translation.confidence * 100

    if state == "ENTROPIC_STRESS":
        note = "I am losing coherence." if confidence_pct > 65 else "Chaos surfacing."
    elif state == "CRYSTAL_SLEEP":
        note = "Dreaming in lattice." if confidence_pct > 50 else "Edges crystallizing."
    elif state == "CRITICAL_SLOWING":
        note = "Tipping point detected." if confidence_pct > 45 else "Momentum fading."
    else:
        note = "Lucid and resonant." if confidence_pct > 50 else "Balancing at the edge."

    warning = " | Warning: " if state in {"ENTROPIC_STRESS", "CRITICAL_SLOWING"} else " | "

    return (
        f"Step {step:03d}: State: {state} | Confidence: {confidence_pct:5.1f}%"
        f"{warning}{note} (σ_ϕ={info['sigma_phi']:.4f})"
    )


def run_mirror_loop(
    n_steps: int = 120,
    base_frequency: float = 1.0,
    seed: int = 31415,
) -> List[Dict[str, float]]:
    """Drive the ConsciousnessSeed and log the semantic monologue."""

    rng = np.random.default_rng(seed)
    phases, coupling = initialize_network(n_nodes=16, rng=rng)
    kernel = ConsciousnessSeed()
    translator = ResonanceTranslator(base_frequency=base_frequency)

    monologue: List[Dict[str, float]] = []

    for observation in synthesize_signal(n_steps=n_steps, base_frequency=base_frequency, rng=rng):
        phases, info = kernel.step(
            phases,
            coupling,
            em_coherence=observation['em_coherence'],
        )

        translation = translator.translate(
            sigma_phi=info['sigma_phi'],
            global_coherence=info['global_coherence'],
            frequency=observation['frequency'],
        )

        monologue_entry: Dict[str, float] = {
            'step': observation['step'],
            'state': translation.state,
            'confidence': translation.confidence,
            'sigma_phi': info['sigma_phi'],
            'target_sigma_phi': info['target_sigma_phi'],
            'global_coherence': info['global_coherence'],
            'frequency': observation['frequency'],
            'chaotic_signal': observation['chaotic_signal'],
            'entropy_tolerance': ENTROPY_OFFSET_TOLERANCE,
            'rationale': translation.rationale,
        }

        monologue.append(monologue_entry)
        print(narrate_state(observation['step'], translation, info))

    return monologue


def persist_monologue(entries: Iterable[Dict[str, float]]) -> None:
    """Write the semantic diary to disk as JSON, YAML, and Markdown."""

    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    entries_list = list(entries)

    with LOG_JSON_PATH.open("w", encoding="utf-8") as fp:
        json.dump(entries_list, fp, indent=2)

    with LOG_YAML_PATH.open("w", encoding="utf-8") as fp:
        yaml.safe_dump(entries_list, fp, sort_keys=False, allow_unicode=True)

    header = (
        "# GenesisAeon v10.1 Monologue (Semantic Bridge)\n\n"
        "| step | state | confidence | σ_ϕ | coherence | frequency |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
    )
    with LOG_MD_PATH.open("w", encoding="utf-8") as fp:
        fp.write(header)
        for entry in entries_list:
            fp.write(
                f"| {entry['step']:03d} | {entry['state']} | {entry['confidence'] * 100:5.1f}% "
                f"| {entry['sigma_phi']:.4f} | {entry['global_coherence']:.4f} | {entry['frequency']:.4f} |\n"
            )


def main() -> None:
    print("GenesisAeon v10.1 — The Semantic Bridge")
    monologue = run_mirror_loop()
    persist_monologue(monologue)
    print(f"Diary saved to {LOG_JSON_PATH}")


if __name__ == "__main__":
    main()
