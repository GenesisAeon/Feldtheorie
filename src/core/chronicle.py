import json
import time
from typing import Dict, List, Any

class TheChronicle:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TheChronicle, cls).__new__(cls)
            cls._instance.init_storage()
        return cls._instance

    def init_storage(self):
        # Der materielle Pool (Was ist verfügbar?)
        self.elemental_pool = {
            'HYDROGEN': 1000000, # Start-Kapital
            'HELIUM': 0,
            'METALS': 0,         # C, O, Fe, Au...
            'DUST': 0            # Komplexer Sternenstaub
        }
        
        # Der Friedhof der Agenten (Die Geschichte)
        # Liste von {'id', 'generation', 'life_yield', 'death_reason'}
        self.graveyard: List[Dict[str, Any]] = []
        
        # Kosmische Generation (Wie oft wurde recycelt?)
        self.cycle_count = 0

    def record_death(self, agent_data: Dict):
        """
        Ein Agent stirbt und überträgt seine Erfahrung und Materie.
        """
        # 1. Logge die Geschichte
        entry = {
            'timestamp': time.time(),
            'id': agent_data.get('id', 'unknown'),
            'role': agent_data.get('role', 'PARTICLE'),
            'lifespan': agent_data.get('age', 0),
            'yield': agent_data.get('yield', {})
        }
        self.graveyard.append(entry)
        
        # 2. Recycle die Materie (Gesetz der Erhaltung)
        # Wenn ein Stern stirbt, gibt er Helium/Metalle in den Pool
        output = agent_data.get('yield', {})
        for element, amount in output.items():
            self.elemental_pool[element] = self.elemental_pool.get(element, 0) + amount
            
        print(f"📜 CHRONICLE: Agent {entry['id']} recorded. Pool updated: {self.elemental_pool}")

    def request_incarnation(self, required_materials: Dict) -> bool:
        """
        Darf ein neuer Agent entstehen? Nur wenn Material da ist.
        """
        # Check
        for el, amt in required_materials.items():
            if self.elemental_pool.get(el, 0) < amt:
                return False
        
        # Consume
        for el, amt in required_materials.items():
            self.elemental_pool[el] -= amt
            
        return True

    def get_ancestry(self, agent_id) -> str:
        # Würde in einer komplexen DB den Stammbaum suchen
        return f"Du bist Teil von Zyklus {self.cycle_count}. Vor dir starben {len(self.graveyard)} Ahnen."
