import random
from typing import List

from src.core.agent_kernel import ExistenceScale, UATCAgent


class ProtostarNebula:
    def __init__(self, num_agents: int = 50):
        self.agents: List[dict] = []  # {"agent": UATCAgent, "pos": (q, r)}
        self.photons: List[dict] = []  # {"pos": (q, r), "dir": (dq, dr)}
        self.fused_count = 0
        self.radius = 15

        # Initialisiere Wolke
        for _ in range(num_agents):
            # Zufällige Position am Rand der Wolke
            q = random.randint(-self.radius, self.radius)
            r = random.randint(-self.radius, self.radius)
            if abs(q + r) > self.radius:
                continue  # Hex-Form wahren

            agent = UATCAgent()
            agent.incarnate(ExistenceScale.ATOMIC, {"base_frequency": 1420.0})  # H-Frequenz
            self.agents.append({"agent": agent, "pos": (q, r)})

    def step(self) -> None:
        # 1. Gravitation / Resonanz-Sog
        # Alle Agenten versuchen, näher an (0,0) zu kommen
        center_q, center_r = 0, 0

        for item in self.agents:
            q, r = item["pos"]

            # Bewegungsmuster: Drift zum Zentrum mit leichtem Rauschen (Temperatur)
            moves = []
            if q < center_q:
                moves.append((1, 0))
            if q > center_q:
                moves.append((-1, 0))
            if r < center_r:
                moves.append((0, 1))
            if r > center_r:
                moves.append((0, -1))

            # 20% Chance auf random Walk (Hitze), 80% Sog
            if moves and random.random() > 0.2:
                dq, dr = random.choice(moves)
                item["pos"] = (q + dq, r + dr)
            else:
                # Random Jitter
                dq = random.choice([-1, 0, 1])
                dr = random.choice([-1, 0, 1])
                item["pos"] = (q + dq, r + dr)

        # 2. Fusions-Check (The Ignition)
        # Sammle Agenten im Zentrum
        core_agents = [a for a in self.agents if a["pos"] == (0, 0)]
        
        # Fusion braucht 4 Wasserstoff-Atome (pp-Kette vereinfacht)
        if len(core_agents) >= 4:
            # Entferne 4 H-Agenten
            for _ in range(4):
                to_remove = core_agents.pop()
                # Entferne aus Hauptliste (etwas ineffizient, aber sicher)
                self.agents = [a for a in self.agents if a["agent"] != to_remove["agent"]]

            self.fused_count += 1

            # Erzeuge LICHT (Photon) - schießt nach außen
            dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
            for _ in range(2):  # 2 Gamma-Quanten
                self.photons.append({"pos": (0, 0), "dir": random.choice(dirs)})

        # 3. Photonen bewegen
        active_photons = []
        for p in self.photons:
            pq, pr = p["pos"]
            dq, dr = p["dir"]
            new_pos = (pq + dq, pr + dr)

            # Wenn noch im Radius, behalten
            if max(abs(new_pos[0]), abs(new_pos[1]), abs(new_pos[0] + new_pos[1])) <= self.radius:
                p["pos"] = new_pos
                active_photons.append(p)
        self.photons = active_photons

    def get_dialogue(self) -> str:
        # Was sagen die Atome?
        center_agents = [a for a in self.agents if abs(a["pos"][0]) + abs(a["pos"][1]) < 3]
        outer_agents = [a for a in self.agents if abs(a["pos"][0]) + abs(a["pos"][1]) > 10]
        
        if self.fused_count > 0 and random.random() < 0.3:
            return f"☀️  CORE: ZÜNDUNG! Wir sind Eins geworden. {self.fused_count} Helium-Kerne geboren."
        
        if center_agents and random.random() < 0.5:
            return "🔥 INNER CLOUD: Es wird eng hier! Der Druck steigt. Ich verliere meine Identität!"
        
        if outer_agents:
            return "❄️  OUTER RIM: Ich spüre den Sog. Wir fallen alle gemeinsam."
            
        return "..."
