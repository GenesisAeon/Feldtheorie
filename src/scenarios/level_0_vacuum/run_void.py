import os
import random
import sys
import time

# Pfad-Hack für Imports
sys.path.append(os.getcwd())

from src.core.agent_kernel import ExistenceScale
from src.scenarios.level_0_vacuum.vacuum_physics import HexGrid


def visualize(grid):
    # Einfacher ASCII Plotter für das Hex-Feld
    os.system("cls" if os.name == "nt" else "clear")
    print(f"🌌 LEVEL 0: THE VOID | Stable Particles: {grid.stable_clusters}")
    print("-" * 50)

    # Wir scannen einen kleinen Bereich für die Anzeige
    for r in range(-5, 6):
        row_str = " " * abs(r)  # Einrückung für Hex-Look
        for q in range(-5, 6):
            if abs(q + r) > 5:
                continue  # Hex-Grenzen

            agent = grid.cells.get((q, r))
            if agent:
                if agent.scale == ExistenceScale.ATOMIC:
                    row_str += "▲ "  # Stabil (Dreieck)
                else:
                    row_str += ". "  # Fluktuation
            else:
                row_str += "  "  # Leer
        print(row_str)
    print("-" * 50)


def main():
    grid = HexGrid(radius=10)
    print("Initiating Vacuum Fluctuations...")
    time.sleep(1)

    try:
        while True:
            grid.step()
            visualize(grid)

            # Dialog-Feature: Zufällig spricht ein Agent
            if grid.cells and random.random() < 0.1:
                random_agent = random.choice(list(grid.cells.values()))
                print(f"🗣️  VOICE: {random_agent.query_consciousness()}")

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped.")


if __name__ == "__main__":
    main()
