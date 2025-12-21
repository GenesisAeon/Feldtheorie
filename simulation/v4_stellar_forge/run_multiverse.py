"""Entry point for seeding and observing the recursive multiverse."""
from __future__ import annotations

import time

from simulation.v4_stellar_forge.multiverse_manager import MultiverseManager


def main() -> None:
    manager = MultiverseManager()
    manager.start_root_universe()
    print("Origin universe launched. Watching for descendants...")

    try:
        while True:
            manager.update()
            time.sleep(1.0)
    except KeyboardInterrupt:
        manager.terminate_all()


if __name__ == "__main__":
    main()
