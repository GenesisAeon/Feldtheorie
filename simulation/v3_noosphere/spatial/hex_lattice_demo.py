"""Demo: Hex Lattice System for V3 Noosphere.

This demo showcases the spatial foundation of Project Noosphere by:
1. Creating a hexagonal lattice
2. Spawning agents on the grid
3. Demonstrating movement and pathfinding
4. Calculating territory control (Voronoi diagram)
5. Rendering the lattice as ASCII art

Run with:
    python -m simulation.v3_noosphere.spatial.hex_lattice_demo
"""

from __future__ import annotations

from simulation.v3_noosphere.spatial.hex_lattice import HexCoord, HexLattice


def main():
    print("=" * 80)
    print("V3 NOOSPHERE: HEX LATTICE DEMONSTRATION")
    print("=" * 80)
    print()

    # Create hex lattice (10-cell radius = ~300 cells)
    print("🌍 Creating hexagonal lattice (radius=10)...")
    lattice = HexLattice(radius=10, seed=42)
    stats = lattice.get_statistics()

    print(f"   Total cells: {stats['total_cells']}")
    print(f"   Average resource density: {stats['average_resource']:.2f}")
    print(f"   Terrain distribution:")
    for terrain, fraction in stats['terrain_distribution'].items():
        print(f"     - {terrain}: {fraction * 100:.1f}%")
    print()

    # Spawn agents
    print("👥 Spawning 12 agents on habitable cells...")
    spawn_points = lattice.find_spawn_points(count=12)
    agent_ids = [f"agent_{i:02d}" for i in range(len(spawn_points))]

    for agent_id, spawn_coord in zip(agent_ids, spawn_points):
        success = lattice.place_agent(spawn_coord, agent_id)
        if success:
            print(f"   ✓ {agent_id} spawned at {spawn_coord}")

    print()

    # Show initial map
    print("🗺️ Initial hex lattice:")
    print(lattice.render_ascii(width=50, height=24))
    print()

    # Demonstrate movement
    print("🚶 Demonstrating agent movement...")
    origin = HexCoord(0, 0)
    target = HexCoord(3, 2)

    # Find agent at origin
    agent_at_origin = None
    for coord, cell in lattice.cells.items():
        if cell.occupied_by is not None and coord.distance(origin) < 3:
            agent_at_origin = cell.occupied_by
            origin = coord
            break

    if agent_at_origin:
        print(f"   Agent: {agent_at_origin}")
        print(f"   Current position: {origin}")
        print(f"   Target position: {target}")

        # Find path
        path = lattice.find_path(origin, target)
        if path:
            print(f"   Path found ({len(path)} steps): {' → '.join(str(c) for c in path[:5])}...")

            # Move agent along path
            current = origin
            for next_coord in path[1:4]:  # Move 3 steps
                success = lattice.move_agent(current, next_coord)
                if success:
                    print(f"   ✓ Moved to {next_coord}")
                    current = next_coord
                else:
                    print(f"   ✗ Movement blocked at {next_coord}")
                    break
        else:
            print("   ✗ No path found (blocked by terrain)")
    print()

    # Calculate territories
    print("🏰 Calculating territory control (Voronoi diagram)...")
    territories = lattice.get_territory_map()

    for agent_id, controlled_cells in sorted(territories.items())[:5]:
        resource_sum = sum(
            lattice.cells[coord].resource
            for coord in controlled_cells
        )
        print(f"   {agent_id}: {len(controlled_cells)} cells, {resource_sum:.1f} total resources")

    print()

    # Show final map
    print("🗺️ Final hex lattice (after movement):")
    print(lattice.render_ascii(width=50, height=24))
    print()

    # Integration teaser
    print("=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("✓ Spatial foundation complete (hex lattice)")
    print("→ Integrate with V12 Crystal Gardener (agents on hex grid)")
    print("→ Add cognitive layer (vector embeddings for agent minds)")
    print("→ Add temporal layer (epoch simulator for civilizations)")
    print()
    print("V3 Noosphere: The Great Transition has begun.")
    print("=" * 80)


if __name__ == "__main__":
    main()
