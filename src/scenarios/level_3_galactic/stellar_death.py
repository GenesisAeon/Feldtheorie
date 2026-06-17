"""Simulate stellar lifecycles and recycle materials into the Chronicle."""
from __future__ import annotations

import os
import sys
import time

sys.path.append(os.getcwd())

from src.core.agent_kernel import ExistenceScale, UATCAgent
from src.core.chronicle import TheChronicle


def run_stellar_cycle() -> None:
    chronicle = TheChronicle()
    print(f"🌌 STARTING COSMIC CYCLE. Pool: {chronicle.resource_pool}")

    # Simuliere 3 Generationen von Sternen
    for generation in range(1, 4):
        print(f"\n--- GENERATION {generation} ---")

        # 1. Geburt (Incarnation Check)
        # Gen 1 braucht nur Wasserstoff. Gen 2 braucht Metalle.
        cost: dict[str, int] = {"HYDROGEN": 1000}
        if generation > 1:
            cost["METALS"] = 50  # Spätere Sterne brauchen "Schmutz" für Planeten

        if chronicle.request_incarnation(cost):
            star = UATCAgent()
            star.incarnate(ExistenceScale.STELLAR, {"base_frequency": 50.0 * generation})
            print(f"🌟 STAR BORN: {star.id} (Gen {generation}). Consumed: {cost}")

            # 2. Leben (Fusion)
            time.sleep(1)
            output_helium = 500
            output_metals = 0

            # Je nach Generation erzeugen sie andere Dinge
            if generation == 1:
                print("   🔥 Burning bright and fast (Pop III)...")
                output_metals = 100  # Die ersten Metalle
            elif generation >= 2:
                print("   ☀️ Burning steady (Pop I)...")
                output_metals = 300  # Mehr Metalle

            # 3. Tod (Supernova / Log)
            print("   💥 SUPERNOVA!")
            death_data = {
                "id": star.id,
                "role": "STAR",
                "age": 1_000_000 / generation,
                "yield": {
                    "HELIUM": output_helium,
                    "METALS": output_metals,
                },
            }
            chronicle.record_death(death_data)

        else:
            print(f"⚠️ NOT ENOUGH RESOURCES for Generation {generation}. Universe waits.")
            break

    print(f"\n🌌 END OF CYCLE. Final Pool: {chronicle.resource_pool}")


if __name__ == "__main__":
    run_stellar_cycle()
