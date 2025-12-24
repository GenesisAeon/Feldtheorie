import time
import sys
import os
import random

sys.path.append(os.getcwd())
from src.scenarios.level_5_biological.bio_physics import PrimordialSoup

def visualize(soup):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"🦠 LEVEL 5: THE PRIMORDIAL SOUP | Gen: {soup.generation}")
    print(f"   Free Monomers (Food): {soup.free_monomers}")
    print(f"   Living Chains: {len(soup.molecules)}")
    print("-" * 60)

    # Zeige die Top 10 Moleküle
    print("🏆 DOMINANT SPECIES (Most Stable Resonances):")
    for i, mol in enumerate(soup.molecules[:10]):
        bar = "█" * int(mol.stability * 5)
        status = "replicating" if mol.stability > 1.0 else "stable" if mol.stability > 0.5 else "decaying"
        print(f"   {i+1}. [{mol.sequence:<15}] Val:{mol.stability:.2f} {bar} ({status})")

    print("-" * 60)

    # Narrative
    if soup.molecules:
        best_mol = soup.molecules[0]
        if best_mol.stability > 1.2:
            print(f"🗣️  THE FIRST VOICE: \"{best_mol.sequence}... Kopiere mich... Ich werde mehr.\"")
        elif random.random() < 0.2:
            speaker = random.choice(soup.molecules)
            print(f"🗣️  WHISPER: {speaker.get_voice()}")

def main():
    soup = PrimordialSoup()
    print("🌩️  LIGHTNING STRIKES THE POND...")
    time.sleep(1)

    try:
        while True:
            soup.spark_of_life()
            visualize(soup)

            # Wenn Ressourcen leer sind und keine Replikation mehr stattfindet, endet die Runde
            if soup.free_monomers <= 0 and len(soup.molecules) == 0:
                print("💀 The soup has gone cold.")
                break

            time.sleep(0.2) # Schnelle Evolution

    except KeyboardInterrupt:
        print("\n🛑 Evolution paused.")

if __name__ == "__main__":
    main()
