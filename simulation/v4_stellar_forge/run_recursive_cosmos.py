"""Main controller for orchestrating recursive universe generation."""
from __future__ import annotations

import time

from simulation.v4_stellar_forge.multiverse_manager import MultiverseManager


def main() -> None:
    print("================================================================")
    print("🌌 V6: THE FECUND UNIVERSE - RECURSIVE COSMOLOGY ENGINE")
    print("================================================================")
    print("Initializing Multiverse Manager...")

    manager = MultiverseManager()
    manager.start_root_universe()

    try:
        while True:
            manager.update()
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n\n🛑 HEAT DEATH INITIATED. Shutting down multiverse...")
        manager.terminate_all()


if __name__ == "__main__":
    main()
