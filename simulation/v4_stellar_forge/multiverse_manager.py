"""Process orchestration for the recursive multiverse renderer."""
from __future__ import annotations

import base64
import json
import subprocess
import uuid
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Deque, Dict, List, Optional

from simulation.v4_stellar_forge.universe_dna import UniverseDNA

MAX_PARALLEL_UNIVERSES = 4
MULTIVERSE_LOG = Path("output/multiverse_log.json")


@dataclass
class GenesisRequest:
    """A queued request to birth a child universe."""

    parent_id: Optional[str]
    parent_gravity: float
    black_hole_mass: float
    dna: UniverseDNA
    generation: int


@dataclass
class UniverseProcess:
    """Metadata for a running universe process."""

    process: subprocess.Popen
    universe_id: str
    generation: int
    parent_id: Optional[str]
    dna: UniverseDNA
    output_dir: Path


PENDING_REQUESTS: Deque[GenesisRequest] = deque()
ACTIVE_PROCESSES: List[UniverseProcess] = []
TOTAL_SPAWNS = 0
LOCAL_UNIVERSE_ID = "origin"
LOCAL_GENERATION = 0


def reset_state() -> None:
    """Reset counters and queues. Primarily used by orchestrators."""

    global PENDING_REQUESTS, ACTIVE_PROCESSES, TOTAL_SPAWNS
    PENDING_REQUESTS = deque()
    ACTIVE_PROCESSES = []
    TOTAL_SPAWNS = 0


def set_local_context(universe_id: str, generation: int) -> None:
    """Record the identity and generation for the current process."""

    global LOCAL_UNIVERSE_ID, LOCAL_GENERATION
    LOCAL_UNIVERSE_ID = universe_id
    LOCAL_GENERATION = generation


def local_universe_id() -> str:
    """Return the identifier of the currently running universe."""

    return LOCAL_UNIVERSE_ID


def local_generation() -> int:
    """Return the generation index of the current universe."""

    return LOCAL_GENERATION


def live_status() -> str:
    """Return a human-readable status line for dashboards."""

    running = sum(1 for proc in ACTIVE_PROCESSES if proc.process.poll() is None)
    return (
        f"Active Universes: {running} | Queue: {len(PENDING_REQUESTS)} | "
        f"Total Spawns: {TOTAL_SPAWNS}"
    )


def _serialize_dna(dna: UniverseDNA) -> str:
    payload = json.dumps(asdict(dna))
    encoded = base64.urlsafe_b64encode(payload.encode("utf-8"))
    return encoded.decode("utf-8")


def _append_genealogy(
    *,
    parent_id: Optional[str],
    child_id: str,
    parent_gravity: float,
    child_gravity: float,
    generation: int,
    black_hole_mass: float,
    output_dir: Path,
) -> None:
    entry = {
        "parent_id": parent_id,
        "child_id": child_id,
        "generation": generation,
        "black_hole_mass": black_hole_mass,
        "parent_gravity": parent_gravity,
        "child_gravity": child_gravity,
        "output": str(output_dir),
    }
    MULTIVERSE_LOG.parent.mkdir(parents=True, exist_ok=True)
    existing: List[Dict] = []
    if MULTIVERSE_LOG.exists():
        try:
            existing = json.loads(MULTIVERSE_LOG.read_text())
        except json.JSONDecodeError:
            existing = []
    existing.append(entry)
    MULTIVERSE_LOG.write_text(json.dumps(existing, indent=2))


def request_genesis(parent_dna: UniverseDNA, black_hole_mass: float, parent_id: str | None) -> None:
    """Queue a child universe spawn originating from a local collapse."""

    child_dna = parent_dna.mutate()
    request = GenesisRequest(
        parent_id=parent_id,
        parent_gravity=parent_dna.gravity_const,
        black_hole_mass=black_hole_mass,
        dna=child_dna,
        generation=LOCAL_GENERATION + 1,
    )
    PENDING_REQUESTS.append(request)


def spawn_child_process(
    dna: UniverseDNA,
    generation: int,
    *,
    parent_id: str | None,
    parent_gravity: float,
    black_hole_mass: float,
) -> str:
    """Spawn a new universe renderer with serialized DNA and metadata."""

    global TOTAL_SPAWNS

    TOTAL_SPAWNS += 1
    universe_uuid = uuid.uuid4().hex[:8]
    universe_id = f"u{TOTAL_SPAWNS:04d}-{universe_uuid}"
    output_dir = Path(f"output/uni_{universe_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    serialized_dna = _serialize_dna(dna)
    command = [
        "python",
        "-m",
        "simulation.v4_stellar_forge.big_bang_renderer",
        "--dna",
        serialized_dna,
        "--gen",
        str(generation),
        "--output",
        str(output_dir),
        "--universe-id",
        universe_id,
    ]
    if parent_id is not None:
        command.extend(["--parent-id", parent_id])

    process = subprocess.Popen(command)
    ACTIVE_PROCESSES.append(
        UniverseProcess(
            process=process,
            universe_id=universe_id,
            generation=generation,
            parent_id=parent_id,
            dna=dna,
            output_dir=output_dir,
        )
    )

    _append_genealogy(
        parent_id=parent_id,
        child_id=universe_id,
        parent_gravity=parent_gravity,
        child_gravity=dna.gravity_const,
        generation=generation,
        black_hole_mass=black_hole_mass,
        output_dir=output_dir,
    )
    return universe_id


def process_queue() -> None:
    """Attempt to launch queued universes while resources allow."""

    prune_finished_processes()
    while PENDING_REQUESTS and len(ACTIVE_PROCESSES) < MAX_PARALLEL_UNIVERSES:
        request = PENDING_REQUESTS.popleft()
        spawn_child_process(
            request.dna,
            request.generation,
            parent_id=request.parent_id,
            parent_gravity=request.parent_gravity,
            black_hole_mass=request.black_hole_mass,
        )


def prune_finished_processes() -> None:
    """Remove completed processes from the active registry."""

    for proc in list(ACTIVE_PROCESSES):
        if proc.process.poll() is not None:
            ACTIVE_PROCESSES.remove(proc)


def terminate_all() -> None:
    """Terminate all running universes."""

    for proc in ACTIVE_PROCESSES:
        if proc.process.poll() is None:
            proc.process.terminate()
    for proc in ACTIVE_PROCESSES:
        proc.process.wait()
    ACTIVE_PROCESSES.clear()


def launch_origin_universe(dna: UniverseDNA, output_dir: str | Path | None = None) -> str:
    """Start the primordial universe without mutation."""

    destination = Path(output_dir or "output/origin_universe")
    destination.mkdir(parents=True, exist_ok=True)

    global TOTAL_SPAWNS
    TOTAL_SPAWNS += 1
    universe_id = "origin"
    serialized_dna = _serialize_dna(dna)
    command = [
        "python",
        "-m",
        "simulation.v4_stellar_forge.big_bang_renderer",
        "--dna",
        serialized_dna,
        "--gen",
        "0",
        "--output",
        str(destination),
        "--universe-id",
        universe_id,
    ]

    process = subprocess.Popen(command)
    ACTIVE_PROCESSES.append(
        UniverseProcess(
            process=process,
            universe_id=universe_id,
            generation=0,
            parent_id=None,
            dna=dna,
            output_dir=destination,
        )
    )

    _append_genealogy(
        parent_id=None,
        child_id=universe_id,
        parent_gravity=0.0,
        child_gravity=dna.gravity_const,
        generation=0,
        black_hole_mass=0.0,
        output_dir=destination,
    )
    return universe_id


def has_activity() -> bool:
    """Return True while processes are running or queued."""

    prune_finished_processes()
    return bool(ACTIVE_PROCESSES or PENDING_REQUESTS)
