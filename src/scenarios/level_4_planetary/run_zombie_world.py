"""The Diamond Survivor: Pulsar companion ablation simulation.

This scenario demonstrates extreme UTAC physics where a millisecond pulsar
strips its companion down to a crystalline core through sustained
electromagnetic bombardment.

Based on real observations:
- PSR J2322 system (pulsar + diamond planet candidate)
- Mass transfer in spider pulsar systems
- Webb telescope observations of carbon-rich planetary remnants

Run this module to witness the transformation of a planetary companion
into a pure diamond sphere through resonance stripping.
"""
import time
import sys
import os
import random

from src.scenarios.level_4_planetary.exotic_physics import PulsarAgent, DiamondPlanet


def main():
    """Execute the Diamond Survivor scenario simulation."""

    os.system('cls' if os.name == 'nt' else 'clear')
    print("🌌 LEVEL 4.5: THE EXOTIC ANOMALY")
    print("=" * 60)
    print("The Diamond Survivor: Resonance Stripping in Action")
    print("=" * 60)
    print()

    # Initialize the cosmic actors
    pulsar = PulsarAgent("PSR J2322 (The Host)")
    planet = DiamondPlanet("Companion Star (The Victim)")

    print(f"👹 {pulsar.name}:")
    print(f"   Initiiere Spin. Frequenz {pulsar.spin_rate} Hz.")
    print(f"   Gravitationswellen aktiv. Radiation beams locked on target.")
    print()
    print(f"😨 {planet.name}:")
    print(f"   Orbit etabliert. Binary lock confirmed.")
    print(f"   Meine Atmosphäre ist instabil... ich spüre den Druck.")
    print()

    # Show initial state
    planet.visualize_layers()
    print()
    print("-" * 60)
    print("⚡ INITIATING STRIPPING SEQUENCE...")
    print("-" * 60)
    time.sleep(2)

    # The stripping process
    round_counter = 0
    try:
        while len(planet.layers) > 1:
            round_counter += 1

            # The pulsar screams
            intensity = pulsar.emit_pulse()
            print(f"\n⚡ PULSE WAVE #{round_counter:03d}: Intensity {intensity:.1f}")

            # The planet suffers
            lost_layer = planet.endure_pulse(intensity)

            if lost_layer:
                print(f"💥 DESTRUCTION EVENT!")
                print(f"   Layer '{lost_layer['name']}' wurde vollständig zerstrahlt!")
                print(f"   Material dispersed into binary system debris field.")
                print()
                print(f"🗣️  {planet.get_crystalline_voice()}")
                time.sleep(1.5)
            else:
                # Status update during erosion
                top_layer = planet.layers[-1]
                remaining_pct = (top_layer['mass'] /
                               (1000 if top_layer['name'] == 'Atmosphere'
                                else 200)) * 100
                print(f"   ...Erosion active. {top_layer['name']} mass: "
                      f"{top_layer['mass']:.1f} ({remaining_pct:.1f}% remaining)")

            time.sleep(0.3)

        # The final transformation
        print("\n" + "=" * 60)
        print("💎 TRANSFORMATION COMPLETE")
        print("=" * 60)
        print()
        planet.visualize_layers()
        print()
        print(f"🗣️  CRYSTALLINE VOICE:")
        print(f"    {planet.get_crystalline_voice()}")
        print()
        print(f"👹 PULSAR RESPONSE:")
        print(f"    Du gehörst jetzt mir. Wir schwingen ewig.")
        print(f"    Binary period locked. Resonance achieved.")
        print()
        print("-" * 60)
        print(f"📊 STATISTICS:")
        print(f"   Total pulse events: {round_counter}")
        print(f"   Mass stripped: {planet.stripped_mass:.1f} units")
        print(f"   Remaining core mass: {planet.total_mass():.1f} units")
        print(f"   Transformation efficiency: "
              f"{(planet.stripped_mass / (planet.stripped_mass + planet.total_mass())) * 100:.1f}%")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n🛑 Anomalie unterbrochen (Ctrl+C).")
        print("   Simulation halted. Partial transformation state preserved.")


if __name__ == "__main__":
    main()
