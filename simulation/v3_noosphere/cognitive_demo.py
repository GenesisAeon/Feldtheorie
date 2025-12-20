#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cognitive Manifold Demo: Agents with Psychological Depth.

This demo showcases V3.1 of the Noosphere - the cognitive layer where agents
possess 64-dimensional mind vectors that determine their terrain preferences.

Watch as:
- Mountain-type agents seek peaks and highlands
- Water-type agents gravitate toward rivers and lakes
- Forest-type agents find sanctuary in woods
- Balanced agents prefer plains

The movement is no longer random - it's **preference-driven**, emerging from
the resonance between mind vectors and terrain embeddings.

Usage:
    python simulation/v3_noosphere/cognitive_demo.py
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from simulation.v3_noosphere.cognitive.mind_vector import CognitiveAgent, NoosphereEmbedder
from simulation.v3_noosphere.spatial.hex_lattice import HexCoord, HexLattice


def find_best_locations(
    agent: CognitiveAgent,
    lattice: HexLattice,
    embedder: NoosphereEmbedder,
    top_k: int = 5,
) -> List[Tuple[HexCoord, str, float]]:
    """Scan the entire map and find the best locations for this agent.

    Args:
        agent: The cognitive agent doing the search
        lattice: The hex lattice world
        embedder: NoosphereEmbedder for resonance computation
        top_k: Number of top locations to return

    Returns:
        List of (coord, terrain, resonance) tuples, sorted by resonance
    """
    resonances = []

    for coord, cell in lattice.cells.items():
        terrain_vec = embedder.get_terrain_vector(cell.terrain)
        resonance = agent.perceive(terrain_vec, embedder)
        resonances.append((coord, cell.terrain, resonance))

    # Sort by resonance (highest first)
    resonances.sort(key=lambda x: x[2], reverse=True)

    return resonances[:top_k]


def print_agent_preferences(agent: CognitiveAgent, embedder: NoosphereEmbedder):
    """Display agent's terrain preferences as resonance scores."""
    print(f"\nAgent: {agent.agent_id}")
    print("   Terrain Preferences:")

    preferences = []
    for terrain in ["mountain", "water", "forest", "plains"]:
        terrain_vec = embedder.get_terrain_vector(terrain)
        resonance = agent.perceive(terrain_vec, embedder)
        preferences.append((terrain, resonance))

    # Sort by preference
    preferences.sort(key=lambda x: x[1], reverse=True)

    for terrain, resonance in preferences:
        bar_length = int((resonance + 1) / 2 * 20)  # Map [-1,1] to [0,20]
        bar = "#" * bar_length
        print(f"   {terrain:10s} [{bar:20s}] {resonance:+.3f}")


def run_cognitive_demo():
    """Main demo: Create a world and spawn agents with different minds."""
    print("=" * 70)
    print("V3.1 NOOSPHERE: THE COGNITIVE MANIFOLD")
    print("=" * 70)
    print("\nInitializing spatial substrate (hexagonal lattice)...")

    # Create the world (small map for demo)
    lattice = HexLattice(radius=8, seed=42)

    print(f"Created {len(lattice.cells)} hex cells")

    # Initialize the cognitive embedder
    embedder = NoosphereEmbedder(seed=42)
    print("Initialized semantic terrain embeddings (64-dim)")

    # Create agents with different psychological profiles
    print("\n" + "-" * 70)
    print("SPAWNING COGNITIVE AGENTS")
    print("-" * 70)

    agents = []

    # Agent 1: Mountain-type (seeks rigidity, structure)
    agent_1 = CognitiveAgent(
        agent_id="Crystalline-alpha",
        coord=HexCoord(0, 0),
        mind_state=embedder.create_random_mind(bias="mountain"),
    )
    agents.append(agent_1)

    # Agent 2: Water-type (seeks fluidity, change)
    agent_2 = CognitiveAgent(
        agent_id="Fluid-beta",
        coord=HexCoord(0, 0),
        mind_state=embedder.create_random_mind(bias="water"),
    )
    agents.append(agent_2)

    # Agent 3: Forest-type (seeks vitality, growth)
    agent_3 = CognitiveAgent(
        agent_id="Vital-gamma",
        coord=HexCoord(0, 0),
        mind_state=embedder.create_random_mind(bias="forest"),
    )
    agents.append(agent_3)

    # Agent 4: Plains-type (seeks balance, openness)
    agent_4 = CognitiveAgent(
        agent_id="Balanced-delta",
        coord=HexCoord(0, 0),
        mind_state=embedder.create_random_mind(bias="plains"),
    )
    agents.append(agent_4)

    # Agent 5: Random (no bias, chaotic mind)
    agent_5 = CognitiveAgent(
        agent_id="Chaotic-epsilon",
        coord=HexCoord(0, 0),
        mind_state=embedder.create_random_mind(bias=None),
    )
    agents.append(agent_5)

    # Display each agent's psychological profile
    for agent in agents:
        print_agent_preferences(agent, embedder)

    # Now each agent scans the map for their ideal locations
    print("\n" + "-" * 70)
    print("TERRAIN RESONANCE ANALYSIS")
    print("-" * 70)
    print("\nEach agent scans the map to find locations with highest resonance...")

    for agent in agents:
        print(f"\n{agent.agent_id} searching for resonant locations:")

        best_locations = find_best_locations(agent, lattice, embedder, top_k=5)

        for i, (coord, terrain, resonance) in enumerate(best_locations, 1):
            # Visual indicator based on resonance strength
            if resonance > 0.8:
                indicator = "[+++]"  # Strong resonance
            elif resonance > 0.5:
                indicator = "[++-]"  # Medium resonance
            else:
                indicator = "[+--]"  # Weak resonance

            print(f"   {i}. {indicator} {coord} [{terrain:10s}] resonance: {resonance:+.3f}")

    # Compute map statistics
    print("\n" + "-" * 70)
    print("MAP STATISTICS")
    print("-" * 70)

    stats = lattice.get_statistics()
    print(f"\nTotal cells: {stats['total_cells']}")
    print(f"Terrain distribution:")
    for terrain, fraction in stats["terrain_distribution"].items():
        bar_length = int(fraction * 40)
        bar = "#" * bar_length
        print(f"  {terrain:10s} [{bar:40s}] {fraction:.1%}")

    # Summary
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print("\nThe agents have developed clear preferences based on their mind vectors.")
    print("This is the foundation of **emergent culture**:")
    print("  -> Mountain-types will form highland civilizations")
    print("  -> Water-types will settle along rivers")
    print("  -> Forest-types will build in the woods")
    print("  -> Plains-types will prefer open land")
    print("\nNext steps:")
    print("  * V3.2: Agent migration (movement toward preferred terrain)")
    print("  * V3.3: Cultural clusters (agents with similar minds form tribes)")
    print("  * V3.4: Memetic diffusion (ideas spread between neighbors)")
    print("  * V3.5: Ideology conflict (incompatible mind vectors -> war)")
    print()


if __name__ == "__main__":
    run_cognitive_demo()
