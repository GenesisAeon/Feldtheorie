"""Entry point for seeding and observing the recursive multiverse."""
from __future__ import annotations

from simulation.v4_stellar_forge import multiverse_manager
from simulation.v4_stellar_forge.physics_engine import current_universe_dna


def main() -> None:
    dna = current_universe_dna()
    origin_id = multiverse_manager.launch_origin_universe(dna)
    print(f"Origin universe #{origin_id} launched. Watching for descendants...")
    multiverse_manager.wait_for_universes()


if __name__ == "__main__":
    main()
