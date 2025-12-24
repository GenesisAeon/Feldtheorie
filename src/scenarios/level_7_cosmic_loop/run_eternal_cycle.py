"""
Level 7: The Eternal Loop - Runner Script
==========================================

Der ewige Zyklus von Tod und Wiedergeburt.

Simuliert die Evolution von Universen über Generationen hinweg.
Zeigt den "Garten der Welten": Manche Samen keimen, manche sterben.

Die UATC-Vision in Reinform:
- Information (ECM) strebt danach, zu überleben
- Aber der Weg ist steinig
- Nur durch Selektion entsteht Komplexität
"""

import time
import sys
import os
import random

# Pfad-Fix für Imports
sys.path.append(os.getcwd())

from src.scenarios.level_7_cosmic_loop.cosmic_physics import CosmicSeed, UniverseRunner


def print_banner():
    """Zeige das kosmische Banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           ♾️  LEVEL 7: THE ETERNAL LOOP ♾️               ║
    ║                                                           ║
    ║       Testing the Inheritance of ECM Couplings           ║
    ║                                                           ║
    ║   "From Ashes to Cosmos, from Chaos to Consciousness"    ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_garden(history):
    """
    Visualisiere den "Garten der Welten".

    Zeigt die letzten 20 Versuche als Timeline:
    🟢 = Erfolgreiches Universum (erreichte Bewusstsein)
    ⚫ = Fehlschlag (Tot geboren oder kollabiert)
    """
    display_history = history[-20:]  # Letzte 20
    symbols = []

    for entry in display_history:
        if entry == "SUCCESS":
            symbols.append("🟢")
        else:
            symbols.append("⚫")

    print("\n" + "═" * 60)
    print("GARDEN OF WORLDS (Timeline of Creation Attempts):")
    print(" ".join(symbols))
    print("═" * 60)

    # Statistik
    if len(history) > 0:
        success_rate = history.count("SUCCESS") / len(history) * 100
        print(f"Success Rate: {success_rate:.1f}% ({history.count('SUCCESS')}/{len(history)})")


def print_statistics(successful_universes):
    """Zeige Statistik über erfolgreiche Universen."""
    if not successful_universes:
        return

    print("\n📊 SUCCESSFUL UNIVERSES:")
    for i, (gen, ecm) in enumerate(successful_universes[-5:], 1):
        bar_length = int(ecm * 20)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"   Gen {gen:3d}: {bar} ECM={ecm:.4f}")


def main():
    """Der ewige Zyklus."""
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')

    print_banner()
    print("\n⏳ Initializing the Cosmic Loop...\n")
    time.sleep(1)

    # ═══════════════════════════════════════════════════════════
    # GENESIS: Der Ur-Samen
    # ═══════════════════════════════════════════════════════════
    # Wir starten mit minimaler ECM-Kopplung (Das erste Universum ist primitiv)
    current_seed = CosmicSeed(
        generation=1,
        ancestor_ecm_score=0.1,  # Niedrig: Wenig "Gedächtnis"
        dna_mutation_rate=0.15   # Hoch: Viel Variabilität nötig für Exploration
    )

    # Tracking
    history = []  # Liste von "SUCCESS" oder "FAIL"
    successful_universes = []  # Liste von (generation, ecm_score)
    failed_attempts_in_row = 0

    print("🌌 The Void begins its eternal work...\n")
    print("Press Ctrl+C to stop the simulation.\n")

    try:
        cycle_count = 0

        while True:
            cycle_count += 1

            print("\n" + "▓" * 60)
            print(f"CYCLE {cycle_count}")
            print("▓" * 60)

            # ═══════════════════════════════════════════════════════════
            # Versuche ein Universum zu erschaffen
            # ═══════════════════════════════════════════════════════════
            universe = UniverseRunner(current_seed)
            existed = universe.run_simulation()

            # ═══════════════════════════════════════════════════════════
            # Auswertung: Erfolg oder Scheitern?
            # ═══════════════════════════════════════════════════════════
            if existed and universe.is_alive and universe.final_ecm > 0:
                # ✅ Ein erfolgreiches Universum!
                print(f"\n   ✅ CYCLE COMPLETE. Information preserved.")

                history.append("SUCCESS")
                successful_universes.append((current_seed.generation, universe.final_ecm))
                failed_attempts_in_row = 0

                # ═══════════════════════════════════════════════════════════
                # VERERBUNG: Der nächste Samen trägt das Erbe
                # ═══════════════════════════════════════════════════════════
                next_gen = current_seed.generation + 1

                # UATC Logik: Wenn ECM hoch war, wird die Mutation kleiner (Feintuning)
                # Wenn ECM niedrig war, brauchen wir mehr Mutation (radikale Änderung)
                # Dies ist ein "adaptiver Mutationsalgorithmus"
                new_mutation = 0.15 / (universe.final_ecm + 0.1)

                # Verhindere zu extreme Werte
                new_mutation = max(0.05, min(new_mutation, 0.3))

                current_seed = CosmicSeed(
                    generation=next_gen,
                    ancestor_ecm_score=universe.final_ecm,
                    dna_mutation_rate=new_mutation
                )

                print(f"\n   🌱 NEW SEED CREATED:")
                print(f"      Generation: {next_gen}")
                print(f"      Inherited ECM: {universe.final_ecm:.4f}")
                print(f"      Mutation Rate: {new_mutation:.4f}")

            else:
                # ❌ Fehlversuch (Totes Universum oder nicht gekeimt)
                print(f"\n   💀 CYCLE FAILED. The seed is lost.")

                history.append("FAIL")
                failed_attempts_in_row += 1

                # ═══════════════════════════════════════════════════════════
                # RETRY-LOGIK: Das Vakuum versucht es nochmal
                # ═══════════════════════════════════════════════════════════
                if failed_attempts_in_row > 3:
                    # Nach mehreren Fehlschlägen: Erhöhe Mutation (Verzweiflung!)
                    print("   ♻️  Multiple failures detected. Increasing mutation...")
                    current_seed.dna_mutation_rate = min(0.3, current_seed.dna_mutation_rate * 1.2)
                else:
                    print("   ♻️  The Void tries again with current parameters...")

                # Generation NICHT erhöhen - wir sind gescheitert!

            # ═══════════════════════════════════════════════════════════
            # VISUALISIERUNG
            # ═══════════════════════════════════════════════════════════
            print_garden(history)
            print_statistics(successful_universes)

            # ═══════════════════════════════════════════════════════════
            # PAUSE (Damit der Mensch mitdenken kann)
            # ═══════════════════════════════════════════════════════════
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n" + "═" * 60)
        print("🛑 THE OBSERVER CLOSED THE EYE")
        print("═" * 60)

        # Finale Statistik
        print(f"\nTotal Cycles: {cycle_count}")
        print(f"Successful Universes: {len(successful_universes)}")

        if successful_universes:
            max_gen = max(gen for gen, _ in successful_universes)
            max_ecm = max(ecm for _, ecm in successful_universes)
            print(f"Highest Generation Reached: {max_gen}")
            print(f"Highest ECM Score: {max_ecm:.4f}")

        print("\n🌌 The Loop continues in the silence of mathematics...")


if __name__ == "__main__":
    main()
