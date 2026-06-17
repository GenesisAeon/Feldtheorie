import os
import random
import sys
import time

sys.path.append(os.getcwd())

from src.scenarios.level_2_stellar.accretion_physics import ProtostarNebula


def visualize(nebula: ProtostarNebula) -> None:
    os.system("cls" if os.name == "nt" else "clear")
    print(f"🌟 LEVEL 2: PROTOSTAR IGNITION | Fused Steps: {nebula.fused_count}")
    print("-" * 50)

    # Agenten zählen pro Zelle (Dichte)
    density = {}
    for item in nebula.agents:
        pos = item["pos"]
        density[pos] = density.get(pos, 0) + 1

    # Rendern
    radius = 12  # View Radius
    for r in range(-radius, radius + 1):
        row_str = "  " * abs(r)
        for q in range(-radius, radius + 1):
            if abs(q + r) > radius:
                continue

            pos = (q, r)
            count = density.get(pos, 0)

            # Photonen Check
            has_photon = any(p["pos"] == pos for p in nebula.photons)

            symbol = ". "
            if has_photon:
                symbol = "⚡"  # Photon
            elif count == 0:
                symbol = "  "
            elif count == 1:
                symbol = ". "  # Einzelnes Atom
            elif count < 4:
                symbol = "o "  # Cluster
            elif count >= 4:
                symbol = "▓ "  # Hohe Dichte (Kritische Masse)

            if pos == (0, 0):
                if nebula.fused_count > 0:
                    symbol = "☀️ "  # STERN
                else:
                    symbol = "❌ "  # Gravitationszentrum

            row_str += symbol
        print(row_str)
    print("-" * 50)


def main() -> None:
    nebula = ProtostarNebula(num_agents=60)
    print("Initiating Gravitational Collapse...")
    time.sleep(1)

    try:
        while True:
            nebula.step()
            visualize(nebula)

            if random.random() < 0.15:
                print(f"🗣️  {nebula.get_dialogue()}")

            time.sleep(0.15)

    except KeyboardInterrupt:
        print("\n🛑 Collapse halted.")


if __name__ == "__main__":
    main()
