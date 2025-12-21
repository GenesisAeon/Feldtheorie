"""Filesystem-driven multiverse orchestrator.

This module monitors genesis signals emitted by child universes, mutates DNA,
queues births, and spawns new renderer processes while respecting concurrency
limits.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from simulation.v4_stellar_forge.physics_engine import current_universe_dna
from simulation.v4_stellar_forge.universe_dna import UniverseDNA

MAX_CONCURRENT_UNIVERSES = 4
LOG_FILE = Path("output/multiverse_log.json")
SIGNAL_DIR = Path("output/signals")


class MultiverseManager:
    """Manage universe processes and respond to genesis signals."""

    def __init__(self) -> None:
        self.active_processes: List[subprocess.Popen] = []
        self.genesis_queue: List[Dict] = []
        self.universe_counter = 0

        Path("output/logs").mkdir(parents=True, exist_ok=True)
        SIGNAL_DIR.mkdir(parents=True, exist_ok=True)

        if not LOG_FILE.exists():
            LOG_FILE.write_text("[]")

    def start_root_universe(self) -> None:
        """Launch the primordial universe (generation 0)."""

        print("🌌 IGNITION: Starting Root Universe...")
        root_dna = current_universe_dna()
        self._spawn_process(root_dna, generation=0, parent_id="VOID")

    def update(self) -> None:
        """Main loop: process signals, clean processes, spawn queued universes."""

        self._scan_for_signals()
        self.active_processes = [p for p in self.active_processes if p.poll() is None]

        while (
            len(self.active_processes) < MAX_CONCURRENT_UNIVERSES
            and self.genesis_queue
        ):
            next_genesis = self.genesis_queue.pop(0)
            self._spawn_process(
                next_genesis["dna"],
                next_genesis["generation"],
                next_genesis["parent_id"],
            )

        sys.stdout.write(
            f"\r♾️  Multiverse Status: Active={len(self.active_processes)} "
            f"| Queued={len(self.genesis_queue)} | Total Spawns={self.universe_counter}   "
        )
        sys.stdout.flush()

    def terminate_all(self) -> None:
        """Terminate all active renderer processes."""

        for proc in self.active_processes:
            if proc.poll() is None:
                proc.terminate()
        for proc in self.active_processes:
            proc.wait()
        self.active_processes.clear()

    def _scan_for_signals(self) -> None:
        """Read genesis signals emitted by universes."""

        for signal_path in SIGNAL_DIR.glob("*.json"):
            try:
                data = json.loads(signal_path.read_text())
                parent_dna = UniverseDNA(**data["parent_dna"])
                child_dna = parent_dna.mutate()

                self.genesis_queue.append(
                    {
                        "dna": child_dna,
                        "generation": data["generation"] + 1,
                        "parent_id": data["universe_id"],
                    }
                )

                self._log_birth(
                    data.get("universe_id", "UNKNOWN"),
                    self.universe_counter + 1,
                    parent_dna,
                    child_dna,
                )

                signal_path.unlink()
            except Exception as exc:  # noqa: BLE001
                print(f"\n⚠️ Error processing signal {signal_path.name}: {exc}")

    def _spawn_process(self, dna: UniverseDNA, generation: int, parent_id: str) -> None:
        self.universe_counter += 1
        uni_id = str(uuid.uuid4())[:8]

        dna_json = json.dumps(asdict(dna))
        cmd = [
            sys.executable,
            "-m",
            "simulation.v4_stellar_forge.big_bang_renderer",
            "--dna",
            dna_json,
            "--gen",
            str(generation),
            "--id",
            uni_id,
            "--frames",
            "300",
        ]

        if parent_id:
            cmd.extend(["--parent-id", parent_id])

        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.active_processes.append(process)

    def _log_birth(
        self,
        parent_id: str,
        child_num: int,
        parent_dna: UniverseDNA,
        child_dna: UniverseDNA,
    ) -> None:
        entry = {
            "timestamp": time.time(),
            "parent": parent_id,
            "child_number": child_num,
            "mutation_g": child_dna.gravity_const - parent_dna.gravity_const,
        }

        try:
            existing = json.loads(LOG_FILE.read_text())
        except json.JSONDecodeError:
            existing = []

        existing.append(entry)
        LOG_FILE.write_text(json.dumps(existing, indent=2))
