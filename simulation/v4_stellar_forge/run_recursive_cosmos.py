import sys
import os

# Ensure the project root is in path
sys.path.append(os.getcwd())

from simulation.v4_stellar_forge.run_multiverse import build_parser
from simulation.v4_stellar_forge.multiverse_manager import MultiverseManager

def main(argv=None):
    print("================================================================")
    print("🌌 V6: THE FECUND UNIVERSE - RECURSIVE COSMOLOGY ENGINE")
    print("================================================================")
    print("Initializing Multiverse Manager...")

    args = build_parser().parse_args(argv)
    manager = MultiverseManager(root_seed=args.seed, max_universes=args.max_universes, frames=args.frames)

    # Start the "Adam" Universe; run() is bounded and always terminates children
    summary = manager.run(max_seconds=args.max_seconds)
    if summary["stopped_by"] == "interrupt":
        print("\n\n🛑 HEAT DEATH INITIATED. Multiverse shut down.")
    print(f"\nRoot seed {summary['root_seed']}: {summary['universes_started']} universes, stopped by {summary['stopped_by']}")
    return summary

if __name__ == "__main__":
    main()
