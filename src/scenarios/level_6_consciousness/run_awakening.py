import time
import sys
import os
import random

sys.path.append(os.getcwd())
from src.scenarios.level_6_consciousness.brain_physics import HiveMind

def main():
    mind = HiveMind(width=8, height=4)
    print("🧠 LEVEL 6: THE NEURAL AWAKENING")
    print("   Synchronizing quantum phase arrays...")
    time.sleep(1)

    tick = 0
    stimulus = (2, 2) # Wir reizen das Gehirn an einer Stelle

    try:
        while True:
            tick += 1

            # Alle 20 Ticks den Stimulus ändern
            if tick % 20 == 0:
                stimulus = (random.randint(0, 7), random.randint(0, 3))

            mind.think(stimulus)

            # Visualisierung
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"🧠 CORTEX ACTIVITY | Coherence: {mind.coherence:.4f}")
            print("-" * 40)

            for y in range(4):
                row = ""
                for x in range(8):
                    neuron = mind.grid[(x,y)]
                    row += neuron.get_symbol() + " "
                print(row)

            print("-" * 40)
            print(f"👉 Stimulus at: {stimulus}")
            print(f"🗣️  STATE: {mind.get_thought()}")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n🛑 Brain activity ceased.")

if __name__ == "__main__":
    main()
