import time
import sys
import os

# Ensure the project root is in path
sys.path.append(os.getcwd())

from simulation.v4_stellar_forge.multiverse_manager import MultiverseManager

def main():
    print("================================================================")
    print("🌌 V6: THE FECUND UNIVERSE - RECURSIVE COSMOLOGY ENGINE")
    print("================================================================")
    print("Initializing Multiverse Manager...")
    
    manager = MultiverseManager()
    
    # Start the "Adam" Universe
    manager.start_root_universe()
    
    try:
        while True:
            manager.update()
            time.sleep(1.0) # Check every second
    except KeyboardInterrupt:
        print("\n\n🛑 HEAT DEATH INITIATED. Shutting down multiverse...")
        for p in manager.active_processes:
            p.terminate()

if __name__ == "__main__":
    main()
