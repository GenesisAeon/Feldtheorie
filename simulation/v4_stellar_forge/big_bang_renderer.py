import argparse
import json
import os
import random
import matplotlib.pyplot as plt
from .universe_dna import UniverseDNA
from .physics_engine import AtomAgent, ElementTypes, PhysicsEngine

def initialize_bang(dna):
    agents = []
    # Create a dense core that will collapse or expand based on G
    for _ in range(50):
        a = AtomAgent(
            x=random.gauss(0, 1.0),
            y=random.gauss(0, 1.0),
            vx=random.gauss(0, 0.5), # Explosion
            vy=random.gauss(0, 0.5),
            element_type=ElementTypes.HYDROGEN
        )
        agents.append(a)
    
    # Add a seed Black Hole to ensure we trigger the recursion for the demo
    # In a real simulation, this would form naturally from collapse
    seed_bh = AtomAgent(0,0,0,0, ElementTypes.BLACK_HOLE)
    seed_bh.mass = 25.0 # Enough to trigger genesis immediately for testing
    agents.append(seed_bh)
    
    return agents

def run_timeline(engine, agents, frames, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    for f in range(frames):
        engine.gravity_step(agents)
        engine.fusion_step(agents)
        
        # Visualization (Headless)
        if f % 10 == 0: # Save every 10th frame to save disk IO
            plt.figure(figsize=(5,5))
            plt.style.use('dark_background')
            
            xs = [a.x for a in agents]
            ys = [a.y for a in agents]
            colors = [a.color for a in agents]
            sizes = [a.mass * 10 for a in agents]
            
            plt.scatter(xs, ys, c=colors, s=sizes, alpha=0.7)
            plt.xlim(-20, 20)
            plt.ylim(-20, 20)
            plt.title(f"Uni: {engine.universe_id} | Gen: {engine.generation} | G={engine.dna.gravity_strength:.3f}")
            
            plt.savefig(f"{output_dir}/frame_{f:03d}.png")
            plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dna", type=str, help="JSON string of UniverseDNA")
    parser.add_argument("--gen", type=int, default=0)
    parser.add_argument("--id", type=str, default="root")
    parser.add_argument("--frames", type=int, default=200)
    parser.add_argument("--output", type=str, default="output/frames")
    args = parser.parse_args()

    # DNA laden oder Default nutzen
    if args.dna:
        dna_dict = json.loads(args.dna)
        dna = UniverseDNA(**dna_dict)
    else:
        dna = UniverseDNA()

    # Engine mit ID und Gen initieren
    engine = PhysicsEngine(dna, args.id, args.gen)
    
    # Big Bang Setup
    agents = initialize_bang(dna)
    
    # Run
    # print(f"Universum {args.id} (Gen {args.gen}) running...")
    run_timeline(engine, agents, args.frames, f"output/frames/{args.id}")
