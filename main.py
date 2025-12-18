#!/usr/bin/env python3
"""GenesisAeon v10.2 demo launcher.

This CLI makes the Planetary Voice (Experiment G) and Dreamtime replay
published in v10.2 easy to reproduce.

Usage:
    python main.py --mode dream   # runs Experiment G then Experiment H
    python main.py --mode voice   # runs Experiment G only

The Dreamtime run will regenerate the planetary diary and dream journal
tri-layer outputs under ``v10_oracle/logs``.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

from v10_oracle.demos.experiment_g_planetary_voice import (
    LOG_JSON_PATH as VOICE_JSON_PATH,
    LOG_MD_PATH as VOICE_MD_PATH,
    LOG_YAML_PATH as VOICE_YAML_PATH,
    persist_diary,
    run_planetary_voice,
)
from v10_oracle.demos.experiment_h_dreamtime import (
    LOG_JSON_PATH as DREAM_JSON_PATH,
    LOG_MD_PATH as DREAM_MD_PATH,
    LOG_YAML_PATH as DREAM_YAML_PATH,
    persist_dream_journal,
    run_dreamtime,
)


def launch_planetary_voice(args: argparse.Namespace) -> Dict[str, object]:
    """Run Experiment G and write the planetary diary tri-layer outputs."""

    diary, ghost_warning, stats = run_planetary_voice(
        base_frequency=args.base_frequency,
        sensitivity=args.sensitivity,
        tipping_point=args.tipping_point,
        seed=args.voice_seed,
    )
    persist_diary(diary, ghost_warning, stats)

    return {
        "ghost_warning": ghost_warning,
        "stats": stats,
        "md": VOICE_MD_PATH,
        "json": VOICE_JSON_PATH,
        "yaml": VOICE_YAML_PATH,
    }


def launch_dreamtime(args: argparse.Namespace) -> Dict[str, object]:
    """Run Experiment H using the latest planetary diary as signature."""

    entries, meta = run_dreamtime(
        n_steps=args.steps,
        n_nodes=args.nodes,
        seed=args.dream_seed,
    )
    persist_dream_journal(entries, meta)
    replay_hits = sum(1 for entry in entries if entry.get("replay_detected"))

    return {
        "meta": meta,
        "replay_hits": replay_hits,
        "md": DREAM_MD_PATH,
        "json": DREAM_JSON_PATH,
        "yaml": DREAM_YAML_PATH,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the GenesisAeon v10.2 demos (Planetary Voice + Dreamtime)."
    )
    parser.add_argument(
        "--mode",
        choices=["dream", "voice"],
        default="dream",
        help="`dream` runs Experiments G and H; `voice` runs Experiment G only.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=500,
        help="Number of Dreamtime steps for Experiment H (only used in dream mode).",
    )
    parser.add_argument(
        "--nodes",
        type=int,
        default=24,
        help="Oscillator nodes in the Dreamtime replay network (Experiment H).",
    )
    parser.add_argument(
        "--base-frequency",
        type=float,
        default=1.0,
        help="Base frequency for the AMOC stream driver (Experiment G).",
    )
    parser.add_argument(
        "--sensitivity",
        type=float,
        default=0.22,
        help="Frequency sensitivity to tipping proximity (Experiment G).",
    )
    parser.add_argument(
        "--tipping-point",
        type=float,
        default=0.70,
        help="Distance-to-tipping threshold that triggers pre-emptive warnings.",
    )
    parser.add_argument(
        "--voice-seed",
        type=int,
        default=1024,
        help="Random seed for Experiment G (Planetary Voice).",
    )
    parser.add_argument(
        "--dream-seed",
        type=int,
        default=2048,
        help="Random seed for Experiment H (Dreamtime replay).",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    voice_logs = launch_planetary_voice(args)
    print("Experiment G complete → planetary diary saved:")
    print(f"  Markdown: {Path(voice_logs['md']).resolve()}")
    print(f"  JSON:     {Path(voice_logs['json']).resolve()}")
    print(f"  YAML:     {Path(voice_logs['yaml']).resolve()}")
    if voice_logs["ghost_warning"]:
        print("  Warning: pre-threshold resonance spike detected (ghost warning).")

    if args.mode == "voice":
        return

    dream_logs = launch_dreamtime(args)
    print("Experiment H complete → dream journal saved:")
    print(f"  Markdown: {Path(dream_logs['md']).resolve()}")
    print(f"  JSON:     {Path(dream_logs['json']).resolve()}")
    print(f"  YAML:     {Path(dream_logs['yaml']).resolve()}")
    print(f"  Replay bursts detected: {dream_logs['replay_hits']}")


if __name__ == "__main__":
    main()
