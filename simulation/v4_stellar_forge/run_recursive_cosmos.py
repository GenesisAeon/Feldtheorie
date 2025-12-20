"""Main controller for orchestrating recursive universe generation."""
from __future__ import annotations

import time

from simulation.v4_stellar_forge import multiverse_manager
from simulation.v4_stellar_forge.physics_engine import current_universe_dna

STATUS_INTERVAL_SECONDS = 1.0


def main() -> None:
    dna = current_universe_dna()
    multiverse_manager.reset_state()
    origin_id = multiverse_manager.launch_origin_universe(dna)
    print(f"Launched origin universe {origin_id}. Entering recursive loop...")

    try:
        while multiverse_manager.has_activity():
            multiverse_manager.process_queue()
            print(multiverse_manager.live_status(), end="\r")
            time.sleep(STATUS_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nInterrupt received; terminating child universes...")
        multiverse_manager.terminate_all()

    # Clear the final status line for clean logs
    print("\nMultiverse recursion complete.")


if __name__ == "__main__":
    main()
