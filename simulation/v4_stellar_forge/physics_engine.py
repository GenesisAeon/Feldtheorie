import math
import uuid
import json
import os
from dataclasses import asdict, dataclass
from enum import Enum

class ElementTypes(str, Enum):
    HYDROGEN = "HYDROGEN"
    BLACK_HOLE = "BLACK_HOLE"

    @property
    def color(self) -> str:
        return {
            ElementTypes.HYDROGEN: "#66ccff",
            ElementTypes.BLACK_HOLE: "#111111",
        }[self]

@dataclass
class AtomAgent:
    x: float
    y: float
    vx: float
    vy: float
    element_type: ElementTypes
    mass: float = 1.0

    def __post_init__(self):
        self.type = self.element_type
        self.color = self.element_type.color

class PhysicsEngine:
    def __init__(self, universe_dna, universe_id, generation):
        self.dna = universe_dna
        self.universe_id = universe_id
        self.generation = generation
        self.signal_sent = False
        
        # Konstanten aus DNA
        self.G = self.dna.gravity_strength
        self.FUSION_DIST = 0.5
        
    def gravity_step(self, agents):
        for i, a in enumerate(agents):
            fx, fy = 0, 0
            for j, b in enumerate(agents):
                if i == j: continue
                
                dx = b.x - a.x
                dy = b.y - a.y
                dist_sq = dx*dx + dy*dy
                dist = math.sqrt(dist_sq)
                
                if dist < 0.1: dist = 0.1 # Softening
                
                # F = G * m1 * m2 / r^2
                f = self.G * (a.mass * b.mass) / dist_sq
                
                fx += f * (dx / dist)
                fy += f * (dy / dist)
            
            a.vx += fx / a.mass
            a.vy += fy / a.mass
            
            # Update Position
            a.x += a.vx
            a.y += a.vy

    def fusion_step(self, agents):
        # Einfache Fusion + Black Hole Detection
        to_remove = []
        new_agents = []
        
        # Check for Black Hole Singularity Trigger
        for agent in agents:
            if agent.type == ElementTypes.BLACK_HOLE and agent.mass > 20.0: # Schwelle für Demo niedrig
                 if not self.signal_sent:
                     self._trigger_genesis(agent)

        return agents # In V4 hatten wir komplexe Fusionslogik, für V6 Demo Fokus auf Trigger

    def _trigger_genesis(self, bh_agent):
        """Emits a signal to the Multiverse Manager"""
        self.signal_sent = True
        
        # Ensure directory exists (in case running standalone)
        os.makedirs("output/signals", exist_ok=True)
        
        signal_data = {
            "universe_id": self.universe_id,
            "generation": self.generation,
            "bh_mass": bh_agent.mass,
            "parent_dna": asdict(self.dna)
        }
        
        filename = f"output/signals/genesis_{uuid.uuid4()}.json"
        with open(filename, 'w') as f:
            json.dump(signal_data, f)
        
        # print(f"🌑 SINGULARITY REACHED in {self.universe_id}! DNA Transmitted.")
