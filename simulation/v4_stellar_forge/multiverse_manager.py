import subprocess
import sys
import json
import os
import time
import uuid
from typing import List, Dict
from dataclasses import asdict
from .universe_dna import UniverseDNA

MAX_CONCURRENT_UNIVERSES = 4
LOG_FILE = "output/multiverse_log.json"
SIGNAL_DIR = "output/signals"

class MultiverseManager:
    def __init__(self):
        self.active_processes: List[subprocess.Popen] = []
        self.genesis_queue: List[Dict] = []
        self.universe_counter = 0
        
        # Ensure directories exist
        os.makedirs("output/logs", exist_ok=True)
        os.makedirs("output/frames", exist_ok=True)
        os.makedirs(SIGNAL_DIR, exist_ok=True)
        
        # Initialize Log
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w') as f:
                json.dump([], f)

    def start_root_universe(self):
        """Starts the Ur-Universe (Generation 0)"""
        print("🌌 IGNITION: Starting Root Universe...")
        root_dna = UniverseDNA() # Default constants
        self._spawn_process(root_dna, generation=0, parent_id="VOID")

    def update(self):
        """Main loop: Check signals, clean processes, spawn from queue"""
        # 1. Check for Genesis Signals (Black Holes created in children)
        self._scan_for_signals()

        # 2. Clean up finished/crashed processes
        self.active_processes = [p for p in self.active_processes if p.poll() is None]

        # 3. Spawn from Queue if slots available
        while len(self.active_processes) < MAX_CONCURRENT_UNIVERSES and self.genesis_queue:
            next_genesis = self.genesis_queue.pop(0)
            self._spawn_process(
                next_genesis['dna'], 
                next_genesis['generation'], 
                next_genesis['parent_id']
            )

        # Status Display
        sys.stdout.write(f"\r♾️  Multiverse Status: Active={len(self.active_processes)} | Queued={len(self.genesis_queue)} | Total Spawns={self.universe_counter}   ")
        sys.stdout.flush()

    def _scan_for_signals(self):
        """Reads json files emitted by universes when BHs form"""
        for filename in os.listdir(SIGNAL_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(SIGNAL_DIR, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    
                    # Mutate and Queue
                    parent_dna = UniverseDNA(**data['parent_dna'])
                    child_dna = parent_dna.mutate()
                    
                    self.genesis_queue.append({
                        'dna': child_dna,
                        'generation': data['generation'] + 1,
                        'parent_id': data['universe_id']
                    })
                    
                    # Log Genealogy
                    self._log_birth(data['universe_id'], self.universe_counter + 1, parent_dna, child_dna)
                    
                    # Remove signal file
                    os.remove(filepath)
                except Exception as e:
                    print(f"\n⚠️ Error processing signal {filename}: {e}")

    def _spawn_process(self, dna: UniverseDNA, generation: int, parent_id: str):
        self.universe_counter += 1
        uni_id = str(uuid.uuid4())[:8]
        
        # Serialize DNA for CLI
        dna_json = json.dumps(asdict(dna))
        
        cmd = [
            sys.executable, "-m", "simulation.v4_stellar_forge.big_bang_renderer",
            "--dna", dna_json,
            "--gen", str(generation),
            "--id", uni_id,
            "--frames", "300" # Short life for rapid evolution testing
        ]
        
        # Start detached process
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.active_processes.append(p)

    def _log_birth(self, parent_id, child_num, p_dna, c_dna):
        entry = {
            "timestamp": time.time(),
            "parent": parent_id,
            "child_number": child_num,
            "mutation_g": c_dna.gravity_strength - p_dna.gravity_strength,
            "mutation_clumping": c_dna.clumping_factor - p_dna.clumping_factor,
            "child_clumping": c_dna.clumping_factor,
            "parent_clumping": p_dna.clumping_factor,
        }
        
        # Append to log file properly
        try:
            with open(LOG_FILE, 'r+') as f:
                logs = json.load(f)
                logs.append(entry)
                f.seek(0)
                json.dump(logs, f, indent=2)
        except:
            # Fallback for empty or corrupt file
            with open(LOG_FILE, 'w') as f:
                json.dump([entry], f, indent=2)
