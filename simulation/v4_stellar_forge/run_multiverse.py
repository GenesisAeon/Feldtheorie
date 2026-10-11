"""Entry point for seeding and observing the recursive multiverse.

Runs are bounded (universes and wall time) and always clean up their child
processes; see MultiverseManager for the run contract.
"""
from __future__ import annotations

import argparse
import json

from simulation.v4_stellar_forge.multiverse_manager import DEFAULT_MAX_UNIVERSES, MultiverseManager


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=None, help="root seed (drawn and reported if omitted)")
    parser.add_argument("--max-universes", type=int, default=DEFAULT_MAX_UNIVERSES)
    parser.add_argument("--max-seconds", type=float, default=600.0)
    parser.add_argument("--frames", type=int, default=300)
    return parser


def main(argv: list[str] | None = None) -> dict:
    args = build_parser().parse_args(argv)
    manager = MultiverseManager(root_seed=args.seed, max_universes=args.max_universes, frames=args.frames)
    print(f"Origin universe launched (root seed {manager.root_seed}). Watching for descendants...")
    summary = manager.run(max_seconds=args.max_seconds)
    print("\n" + json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    main()
