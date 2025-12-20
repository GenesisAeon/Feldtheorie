"""Utilities for spawning descendant universes as subprocesses."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

from simulation.v4_stellar_forge.universe_dna import UniverseDNA

UNIVERSE_COUNTER = 0
ACTIVE_PROCESSES: List[subprocess.Popen] = []


def _next_universe_id() -> int:
    global UNIVERSE_COUNTER
    UNIVERSE_COUNTER += 1
    return UNIVERSE_COUNTER


def spawn_child_universe(dna: UniverseDNA, black_hole_mass: float) -> int:
    """Mutate DNA and launch a child-universe renderer as a subprocess."""

    mutated = dna.mutate()
    universe_id = _next_universe_id()
    output_dir = Path(f"output/universe_{universe_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    seed_token = mutated.to_seed_token()
    command = [
        "python",
        "-m",
        "simulation.v4_stellar_forge.big_bang_renderer",
        "--seed",
        seed_token,
        "--output",
        str(output_dir),
    ]

    process = subprocess.Popen(command)
    ACTIVE_PROCESSES.append(process)
    print(
        "Spawned child universe",
        universe_id,
        "with mutated DNA",
        mutated,
        f"from black hole mass {black_hole_mass:.1f}",
    )
    return universe_id


def launch_origin_universe(dna: UniverseDNA, output_dir: str | Path | None = None) -> int:
    """Start the primordial universe without mutation."""

    universe_id = _next_universe_id()
    destination = Path(output_dir or f"output/universe_{universe_id}")
    destination.mkdir(parents=True, exist_ok=True)

    command = [
        "python",
        "-m",
        "simulation.v4_stellar_forge.big_bang_renderer",
        "--seed",
        dna.to_seed_token(),
        "--output",
        str(destination),
    ]
    process = subprocess.Popen(command)
    ACTIVE_PROCESSES.append(process)
    print(f"Launched origin universe #{universe_id} into {destination}")
    return universe_id


def wait_for_universes() -> None:
    """Block until all tracked universe processes exit."""

    for process in list(ACTIVE_PROCESSES):
        process.wait()
