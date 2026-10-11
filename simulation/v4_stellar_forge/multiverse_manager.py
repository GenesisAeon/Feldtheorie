"""Process and lineage control for the recursive multiverse demo.

Run contract (package V1, findings F2/F4 and observations N1/N4):

* Seed hierarchy: one root seed. Every universe has a lineage id
  (``u``, ``u.0``, ``u.0.1`` ...). Its mutation RNG and its initial-state seed
  are derived from ``SeedSequence(root_seed, spawn_key=lineage + (stream,))``.
  Universe ids and DNA therefore depend only on the root seed and the
  lineage, not on process timing. ``child_number`` is the global arrival
  order of births; it is unique within a run but timing-dependent.
* Bounded runs: at most ``max_universes`` universes are started (root
  included). Signals beyond that budget are logged as ``not_spawned_budget``.
  ``run()`` additionally stops at ``max_seconds``.
* Clean shutdown: ``terminate_all()`` terminates, waits for and if necessary
  kills every child process. ``run()`` always calls it.

The renderer still inserts a black hole into every universe (finding F1), so
this remains a demo of the machinery, not a selection experiment.
"""
import subprocess
import sys
import json
import os
import time
from pathlib import Path
from typing import List, Dict
from dataclasses import asdict

import numpy as np

from .universe_dna import UniverseDNA

MAX_CONCURRENT_UNIVERSES = 4
DEFAULT_MAX_UNIVERSES = 16
LOG_FILE = "output/multiverse_log.json"
SIGNAL_DIR = "output/signals"
ROOT_ID = "u"

# Independent RNG streams below each universe in the seed hierarchy.
STREAM_MUTATION = 0
STREAM_INITIAL_STATE = 1

_REPO_ROOT = Path(__file__).resolve().parents[2]


def lineage_path(universe_id: str) -> tuple:
    """Return the lineage tuple of an id such as ``u.0.2`` -> ``(0, 2)``."""

    parts = str(universe_id).split(".")
    if parts[0] != ROOT_ID or not all(p.isdigit() for p in parts[1:]):
        raise ValueError(f"not a lineage id: {universe_id!r}")
    return tuple(int(p) for p in parts[1:])


def child_id(parent_id: str, index: int) -> str:
    return f"{parent_id}.{index}"


class MultiverseManager:
    def __init__(self, root_seed: int | None = None,
                 max_universes: int | None = DEFAULT_MAX_UNIVERSES,
                 frames: int = 300,
                 max_concurrent: int = MAX_CONCURRENT_UNIVERSES):
        if root_seed is None:
            # Drawn once and logged with every birth, so the run stays replayable.
            root_seed = int(np.random.SeedSequence().entropy)
        if not isinstance(root_seed, int) or isinstance(root_seed, bool) or root_seed < 0:
            raise ValueError("root_seed must be a non-negative int")
        if max_universes is not None and max_universes < 1:
            raise ValueError("max_universes must be >= 1 or None (explicitly unbounded)")
        self.root_seed = root_seed
        self.max_universes = max_universes
        self.frames = int(frames)
        self.max_concurrent = int(max_concurrent)

        self.active_processes: List[subprocess.Popen] = []
        self.genesis_queue: List[Dict] = []
        self.universe_counter = 0          # universes started (root included)
        self.births = 0                    # accepted signals, unique child_number
        self.not_spawned_budget = 0
        self.rejected_signals: List[str] = []
        self.known_ids: set = set()
        self._children_per_parent: Dict[str, int] = {}

        # Ensure directories exist
        os.makedirs("output/logs", exist_ok=True)
        os.makedirs("output/frames", exist_ok=True)
        os.makedirs(SIGNAL_DIR, exist_ok=True)

        # Initialize Log
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w', encoding="utf-8") as f:
                json.dump([], f)

    # -- seed hierarchy -------------------------------------------------
    def seed_sequence(self, universe_id: str, stream: int) -> np.random.SeedSequence:
        return np.random.SeedSequence(self.root_seed, spawn_key=lineage_path(universe_id) + (stream,))

    def initial_state_seed(self, universe_id: str) -> int:
        return int(self.seed_sequence(universe_id, STREAM_INITIAL_STATE).generate_state(1)[0])

    def mutation_rng(self, universe_id: str) -> np.random.Generator:
        return np.random.default_rng(self.seed_sequence(universe_id, STREAM_MUTATION))

    def _budget_left(self) -> bool:
        if self.max_universes is None:
            return True
        return self.universe_counter + len(self.genesis_queue) < self.max_universes

    # -- lifecycle ------------------------------------------------------
    def start_root_universe(self):
        """Starts the Ur-Universe (Generation 0)"""
        print("🌌 IGNITION: Starting Root Universe...")
        root_dna = UniverseDNA() # Default constants
        self._spawn_process(root_dna, generation=0, parent_id="VOID", universe_id=ROOT_ID)

    def update(self):
        """Main loop: Check signals, clean processes, spawn from queue"""
        # 1. Check for Genesis Signals (Black Holes created in children)
        self._scan_for_signals()

        # 2. Clean up finished/crashed processes
        self.active_processes = [p for p in self.active_processes if p.poll() is None]

        # 3. Spawn from Queue if slots available
        while len(self.active_processes) < self.max_concurrent and self.genesis_queue:
            next_genesis = self.genesis_queue.pop(0)
            self._spawn_process(
                next_genesis['dna'],
                next_genesis['generation'],
                next_genesis['parent_id'],
                next_genesis['universe_id'],
            )

        # Status Display
        sys.stdout.write(f"\r♾️  Multiverse Status: Active={len(self.active_processes)} | Queued={len(self.genesis_queue)} | Total Spawns={self.universe_counter}   ")
        sys.stdout.flush()

    def is_idle(self) -> bool:
        return not self.active_processes and not self.genesis_queue

    def run(self, max_seconds: float | None = None, poll_interval: float = 1.0) -> Dict:
        """Run until no work is left, the time limit is hit or Ctrl+C.

        Child processes are always cleaned up before returning.
        """
        if not self.known_ids:
            self.start_root_universe()
        deadline = None if max_seconds is None else time.monotonic() + max_seconds
        stopped_by = "finished"
        try:
            while True:
                self.update()
                if self.is_idle():
                    # A child may have written its signal just before exiting.
                    self.update()
                    if self.is_idle():
                        break
                if deadline is not None and time.monotonic() >= deadline:
                    stopped_by = "time_limit"
                    break
                time.sleep(poll_interval)
        except KeyboardInterrupt:
            stopped_by = "interrupt"
        finally:
            terminated = self.terminate_all()
        return {
            "root_seed": self.root_seed,
            "stopped_by": stopped_by,
            "universes_started": self.universe_counter,
            "births": self.births,
            "not_spawned_budget": self.not_spawned_budget,
            "queued_unstarted": len(self.genesis_queue),
            "rejected_signals": list(self.rejected_signals),
            "terminated_processes": terminated,
        }

    def terminate_all(self, timeout: float = 5.0) -> int:
        """Terminate, wait for and if needed kill every child process.

        Returns the number of processes that were still running.
        """
        running = [p for p in self.active_processes if p.poll() is None]
        for p in running:
            p.terminate()
        for p in running:
            try:
                p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait()
        self.active_processes = []
        return len(running)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.terminate_all()
        return False

    # -- signals and spawning ------------------------------------------
    def _scan_for_signals(self):
        """Reads json files emitted by universes when BHs form"""
        for filename in sorted(os.listdir(SIGNAL_DIR)):
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(SIGNAL_DIR, filename)
            try:
                with open(filepath, 'r', encoding="utf-8") as f:
                    data = json.load(f)
                parent_id = data['universe_id']
                if parent_id not in self.known_ids:
                    raise ValueError(f"signal from unknown universe {parent_id!r}")
                parent_dna = UniverseDNA(**data['parent_dna'])
                generation = int(data['generation']) + 1
            except Exception as e:
                print(f"\n⚠️ Rejected signal {filename}: {e}")
                self.rejected_signals.append(filename)
                os.makedirs(os.path.join(SIGNAL_DIR, "rejected"), exist_ok=True)
                os.replace(filepath, os.path.join(SIGNAL_DIR, "rejected", filename))
                continue

            index = self._children_per_parent.get(parent_id, 0)
            self._children_per_parent[parent_id] = index + 1
            cid = child_id(parent_id, index)
            child_dna = parent_dna.mutate(self.mutation_rng(cid))

            if self._budget_left():
                status = "queued"
                self.births += 1
                self.genesis_queue.append({
                    'dna': child_dna,
                    'generation': generation,
                    'parent_id': parent_id,
                    'universe_id': cid,
                })
            else:
                status = "not_spawned_budget"
                self.not_spawned_budget += 1

            # Log Genealogy
            self._log_birth(parent_id, cid, generation, status, parent_dna, child_dna)

            # Remove signal file
            os.remove(filepath)

    def _spawn_process(self, dna: UniverseDNA, generation: int, parent_id: str, universe_id: str):
        lineage_path(universe_id)  # validates the id
        if universe_id in self.known_ids:
            raise ValueError(f"universe id {universe_id!r} already started")
        self.universe_counter += 1
        self.known_ids.add(universe_id)

        # Serialize DNA for CLI
        dna_json = json.dumps(asdict(dna))

        cmd = [
            sys.executable, "-m", "simulation.v4_stellar_forge.big_bang_renderer",
            "--dna", dna_json,
            "--gen", str(generation),
            "--id", universe_id,
            "--frames", str(self.frames),
            "--seed", str(self.initial_state_seed(universe_id)),
        ]
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(
            [str(_REPO_ROOT)] + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else []))

        # Child output goes to ./output of the current working directory
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
        self.active_processes.append(p)

    def _log_birth(self, parent_id, cid, generation, status, p_dna, c_dna):
        entry = {
            "timestamp": time.time(),
            "root_seed": self.root_seed,
            "parent": parent_id,
            "child_id": cid,
            "child_number": self.births if status == "queued" else None,
            "generation": generation,
            "status": status,
            "child_dna": asdict(c_dna),
            "mutation_g": c_dna.gravity_strength - p_dna.gravity_strength,
            "mutation_clumping": c_dna.clumping_factor - p_dna.clumping_factor,
            "child_clumping": c_dna.clumping_factor,
            "parent_clumping": p_dna.clumping_factor,
        }

        # Append to log file properly
        try:
            with open(LOG_FILE, 'r+', encoding="utf-8") as f:
                logs = json.load(f)
                logs.append(entry)
                f.seek(0)
                json.dump(logs, f, indent=2)
                f.truncate()
        except (OSError, ValueError):
            # Fallback for empty or corrupt file
            with open(LOG_FILE, 'w', encoding="utf-8") as f:
                json.dump([entry], f, indent=2)
