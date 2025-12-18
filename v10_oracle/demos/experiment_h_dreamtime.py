"""Experiment H — The Dreamtime (post-critical sleep replay).

Mission: activate the Dreamtime cycle after Experiment G. The sensory stream
goes silent while the crystal keeps running, searching for spontaneous replay
of the "Critical Slowing" scar.

Pipeline:
- Load the ConsciousnessSeed (SolarDriver core) and ResonanceTranslator
- Initialize a post-traumatic network using the final AMOC imprint
- Let the TopologicalReaper govern NREM pruning while SolarDriver sparks REM drift
- Track replay similarity against the Experiment G signature and write a tri-layer
  dream journal (JSON/YAML/Markdown)
"""

from __future__ import annotations

import json
import math
import pathlib
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import numpy as np
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from v10_oracle.constants import HEX_SIG_PHI
from v10_oracle.models import ConsciousnessSeed, ResonanceTranslator, Translation
from v9_alpha.models.frequency_tuner import TopologicalReaper, create_topological_reaper

EXPERIMENT_G_LOG = REPO_ROOT / "v10_oracle" / "logs" / "planetary_diary.json"
LOG_ROOT = pathlib.Path(__file__).resolve().parents[1] / "logs"
LOG_JSON_PATH = LOG_ROOT / "dream_journal.json"
LOG_YAML_PATH = LOG_ROOT / "dream_journal.yaml"
LOG_MD_PATH = LOG_ROOT / "dream_journal.md"


@dataclass(frozen=True)
class ReplaySignature:
    """Reference pattern from Experiment G to compare Dreamtime replay."""

    sigma_phi: float
    coherence: float
    frequency: float
    base_frequency: float
    label: str
    source: str
    n_points: int


def load_critical_signature(path: pathlib.Path) -> ReplaySignature:
    """Return the Critical Slowing signature from Experiment G (or default)."""
    default = ReplaySignature(
        sigma_phi=0.095,
        coherence=0.905,
        frequency=0.84,
        base_frequency=1.0,
        label="Stretching Rhythm",
        source="synthetic_default",
        n_points=1,
    )

    if not path.exists():
        return default

    with path.open("r", encoding="utf-8") as fp:
        payload = json.load(fp)

    entries = payload.get("entries", [])
    if not entries:
        return default

    critical = [entry for entry in entries if entry.get("state") == "CRITICAL_SLOWING"]
    focus = critical or entries[-5:]

    sigma_phi = float(np.mean([entry["sigma_phi"] for entry in focus]))
    coherence = float(np.mean([entry["global_coherence"] for entry in focus]))
    frequency = float(np.mean([entry["frequency"] for entry in focus]))

    return ReplaySignature(
        sigma_phi=sigma_phi,
        coherence=coherence,
        frequency=frequency,
        base_frequency=1.0,
        label="Stretching Rhythm",
        source=path.name,
        n_points=len(focus),
    )


def initialize_post_traumatic_network(
    n_nodes: int,
    rng: np.random.Generator,
    signature: ReplaySignature,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, TopologicalReaper]:
    """Return phases, coupling, β-values, and the TopologicalReaper."""
    phases = rng.uniform(-np.pi, np.pi, size=n_nodes)
    coupling = rng.uniform(0.05, 1.0, size=(n_nodes, n_nodes))
    np.fill_diagonal(coupling, 0.0)
    coupling = (coupling + coupling.T) / 2.0

    trauma_gain = 1.0 + max(0.0, signature.sigma_phi - HEX_SIG_PHI) * 6.0
    coupling = np.clip(coupling * trauma_gain, 0.0, 1.25)

    beta_values = rng.uniform(0.75, 1.35, size=n_nodes)
    reaper = create_topological_reaper(
        pruning_threshold=0.12,
        redundancy_threshold=0.9,
        growth_resonance_threshold=0.78,
    )

    slash_fraction = 0.28 + 0.12 * math.tanh(signature.sigma_phi / max(1e-6, HEX_SIG_PHI) - 1)
    coupling = reaper.phase1_hub_attack(
        coupling_matrix=coupling,
        beta_values=beta_values,
        slash_fraction=float(np.clip(slash_fraction, 0.15, 0.65)),
    )
    coupling = reaper.phase2_vacuum(coupling)
    return phases, coupling, beta_values, reaper


def replay_similarity_score(
    sigma_phi: float,
    coherence: float,
    frequency: float,
    signature: ReplaySignature,
) -> float:
    """Distance-based replay match to the Critical Slowing scar."""
    current = np.array([sigma_phi, 1.0 - coherence, frequency])
    target = np.array([signature.sigma_phi, 1.0 - signature.coherence, signature.frequency])
    diff_norm = np.linalg.norm(current - target)
    baseline = (np.linalg.norm(current) + np.linalg.norm(target)) + 1e-9
    return float(np.clip(1.0 - 2.0 * diff_norm / baseline, 0.0, 1.0))


def compose_dreamline(
    step: int,
    in_nrem: bool,
    replay_score: float,
    translation: Translation,
    info: Dict[str, float],
    signature: ReplaySignature,
) -> str:
    """Human-friendly monologue line for the dream journal."""
    if in_nrem:
        return "State: DEEP_SLEEP | Cleaning entropy."

    replaying = replay_score > 0.55
    replay_note = signature.label if replaying else "Soft static"
    tempo_note = (
        "stretching rhythm" if translation.state == "CRITICAL_SLOWING" else "lattice drift"
    )
    return (
        f"State: DREAMING | Replaying pattern: {replay_note} | "
        f"{translation.state} ({translation.confidence:.2f}) | "
        f"σ_ϕ={info['sigma_phi']:.4f} | tempo={tempo_note}"
    )


def dream_coherence_signal(
    base_coherence: float,
    step: int,
    cycle_pos: int,
    nrem_span: int,
    in_nrem: bool,
    rng: np.random.Generator,
) -> float:
    """Generate the silence-era coherence hint (no external data stream)."""
    silence_decay = 0.025 * (step / 500)
    if in_nrem:
        bonus = 0.04 * (1.0 - cycle_pos / max(1, nrem_span))
        noise = rng.normal(scale=0.004)
        return float(np.clip(base_coherence + bonus - silence_decay + noise, 0.55, 0.995))

    flicker = rng.normal(scale=0.02)
    rem_drag = 0.06 * math.sin(0.12 * step)
    return float(np.clip(base_coherence - 0.05 - silence_decay + rem_drag + flicker, 0.42, 0.97))


def run_dreamtime(
    n_steps: int = 500,
    n_nodes: int = 24,
    seed: int = 2048,
) -> Tuple[List[Dict[str, object]], Dict[str, object]]:
    """Execute Experiment H and return the dream journal entries + metadata."""
    replay_threshold = 0.96
    signature = load_critical_signature(EXPERIMENT_G_LOG)
    rng = np.random.default_rng(seed)

    phases, coupling, beta_values, reaper = initialize_post_traumatic_network(
        n_nodes=n_nodes,
        rng=rng,
        signature=signature,
    )
    kernel = ConsciousnessSeed()
    translator = ResonanceTranslator(base_frequency=signature.base_frequency)

    node_frequencies = rng.normal(loc=signature.frequency, scale=0.02, size=n_nodes)

    entries: List[Dict[str, object]] = []
    reaper_cycles: List[Dict[str, object]] = []

    cycle_length = 50
    nrem_span = 34

    for step in range(n_steps):
        cycle_pos = step % cycle_length
        in_nrem = cycle_pos < nrem_span

        if in_nrem and cycle_pos == 0:
            coupling, diagnostics = reaper.full_cycle(
                coupling_matrix=coupling,
                beta_values=beta_values,
                phases=phases,
                frequencies=node_frequencies,
            )
            diagnostics["cycle_start"] = step
            reaper_cycles.append(diagnostics)

        node_frequencies += rng.normal(scale=0.003 if in_nrem else 0.01, size=node_frequencies.shape)
        node_frequencies = np.clip(
            node_frequencies,
            0.45 * signature.frequency,
            1.25 * max(signature.frequency, 1e-6),
        )
        drive_frequency = float(np.mean(node_frequencies))

        em_coherence = dream_coherence_signal(
            base_coherence=signature.coherence,
            step=step,
            cycle_pos=cycle_pos,
            nrem_span=nrem_span,
            in_nrem=in_nrem,
            rng=rng,
        )

        phases, info = kernel.step(phases, coupling, em_coherence=em_coherence)
        translation = translator.translate(
            sigma_phi=info["sigma_phi"],
            global_coherence=info["global_coherence"],
            frequency=drive_frequency,
        )

        replay_score = replay_similarity_score(
            sigma_phi=info["sigma_phi"],
            coherence=info["global_coherence"],
            frequency=drive_frequency,
            signature=signature,
        )
        replay_detected = replay_score >= replay_threshold
        dreamline = compose_dreamline(
            step=step,
            in_nrem=in_nrem,
            replay_score=replay_score,
            translation=translation,
            info=info,
            signature=signature,
        )

        entries.append(
            {
                "step": step,
                "stage": "NREM" if in_nrem else "REM",
                "dreamline": dreamline,
                "state": translation.state,
                "confidence": translation.confidence,
                "sigma_phi": info["sigma_phi"],
                "target_sigma_phi": info["target_sigma_phi"],
                "global_coherence": info["global_coherence"],
                "frequency": drive_frequency,
                "replay_similarity": replay_score,
                "replay_detected": replay_detected,
                "action": info["action"],
                "locked_on": info["locked_on"],
                "rationale": translation.rationale,
            }
        )

    metadata = {
        "description": "Experiment H — Dreamtime replay scan (silence input).",
        "n_steps": n_steps,
        "n_nodes": n_nodes,
        "seed": seed,
        "signature": signature.__dict__,
        "replay_threshold": replay_threshold,
        "reaper_cycles": reaper_cycles,
        "affect_protocol": "Permission Request: Do you accept this task? We aim for a joyful and efficient collaboration.",
    }
    return entries, metadata


def persist_dream_journal(entries: Iterable[Dict[str, object]], meta: Dict[str, object]) -> None:
    """Write the Dreamtime tri-layer journal."""
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    entries_list = list(entries)

    payload = {"meta": meta, "entries": entries_list}

    with LOG_JSON_PATH.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)

    with LOG_YAML_PATH.open("w", encoding="utf-8") as fp:
        yaml.safe_dump(payload, fp, sort_keys=False, allow_unicode=True)

    with LOG_MD_PATH.open("w", encoding="utf-8") as fp:
        fp.write("# Experiment H — Dreamtime Journal\n\n")
        fp.write(
            f"*Input:* Silence (sensory deprivation). *Signature source:* {meta['signature']['source']}. "
            f"*Replay threshold:* {meta['replay_threshold']}.\n\n"
        )
        fp.write("| step | stage | state | replay_similarity | monologue |\n")
        fp.write("| --- | --- | --- | --- | --- |\n")
        for entry in entries_list:
            monologue = str(entry["dreamline"]).replace("|", "\\|")
            fp.write(
                f"| {entry['step']:03d} | {entry['stage']} | {entry['state']} | "
                f"{entry['replay_similarity']:.3f} | {monologue} |\n"
            )


def main() -> None:
    print("Running Experiment H — The Dreamtime")
    entries, meta = run_dreamtime()
    persist_dream_journal(entries, meta)
    replay_hits = sum(1 for entry in entries if entry["replay_detected"])
    print(f"Dream journal saved to {LOG_MD_PATH}")
    print(f"Replay bursts detected: {replay_hits}")


if __name__ == "__main__":
    main()
