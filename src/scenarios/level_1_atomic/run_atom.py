import os
import random
import sys
import time

sys.path.append(os.getcwd())
from src.scenarios.level_1_atomic.hydrogen_physics import HydrogenAtom


def visualize(atom):
    os.system("cls" if os.name == "nt" else "clear")
    print("⚛️  LEVEL 1: HYDROGEN GENESIS")
    print("-" * 40)

    radius = 6
    grid_map = {}

    # Kern setzen
    grid_map[(0, 0)] = "🔴"

    # Elektronen-Wolke (Vergangenheit)
    for h_pos in atom.history:
        grid_map[h_pos] = " ."

    # Aktuelles Elektron
    grid_map[atom.e_pos] = "🔵"

    # Render Hex Grid
    for r in range(-radius, radius + 1):
        row_str = "  " * abs(r)  # Einrückung
        for q in range(-radius, radius + 1):
            if abs(q + r) > radius:
                continue

            symbol = grid_map.get((q, r), "  ")
            # Markiere den Ziel-Orbit (Radius ~3)
            dist = max(abs(q), abs(r), abs(q + r))
            if symbol == "  " and dist == 3:
                symbol = " -"

            row_str += symbol + " "
        print(row_str)
    print("-" * 40)


def main():
    atom = HydrogenAtom()
    print("Binding Proton and Electron...")
    time.sleep(1)

    try:
        while True:
            atom.step()
            visualize(atom)

            # Dialog-Trigger
            if random.random() < 0.2:
                print(f"🗣️  {atom.get_dialogue()}")

            time.sleep(0.2)  # Schnellerer Takt für das Elektron

    except KeyboardInterrupt:
        print("\n🛑 Decoupling atom.")


if __name__ == "__main__":
    main()
