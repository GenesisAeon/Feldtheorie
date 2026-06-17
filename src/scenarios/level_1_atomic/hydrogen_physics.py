import math
import random

from src.core.agent_kernel import ExistenceScale, UATCAgent


class HydrogenAtom:
    def __init__(self):
        # Der Kern (Proton) - sitzt fest im Zentrum (0,0)
        self.proton = UATCAgent()
        self.proton.incarnate(ExistenceScale.ATOMIC, {"base_frequency": 100.0})  # Hohe Frequenz = Masse

        # Das Elektron - tanzt drumherum
        self.electron = UATCAgent()
        self.electron.incarnate(ExistenceScale.ATOMIC, {"base_frequency": 10.0})

        # Elektron Position (q, r) im Hex-Grid
        self.e_pos = (2, 0)

        # Spur der Verwischung (wo war das Elektron zuletzt?)
        self.history = []

    def calculate_probability(self, q, r):
        # UATC Physik: Das Elektron sucht den "Goldenen Abstand"
        # Sagen wir, der perfekte Radius ist 3 Hex-Zellen (Bohr-Radius Simulation)
        dist = math.sqrt(q ** 2 + r ** 2 + q * r)  # Hex-Distanz-Metrik (grob)

        target_radius = 3.0
        diff = abs(dist - target_radius)

        # Je näher am Target Radius, desto höher die Wahrscheinlichkeit
        # Gauß-Glocke um Radius 3
        probability = math.exp(-(diff**2) / 2.0)
        return probability

    def step(self):
        # Quantensprung: Das Elektron wählt eine neue Position basierend auf Wahrscheinlichkeit
        # Es prüft alle Nachbarn und entscheidet
        current_q, current_r = self.e_pos

        candidates = [
            (current_q, current_r),  # Bleiben
            (current_q + 1, current_r),
            (current_q - 1, current_r),
            (current_q, current_r + 1),
            (current_q, current_r - 1),
            (current_q + 1, current_r - 1),
            (current_q - 1, current_r + 1),
        ]

        # Wähle Kandidaten gewichtet nach Resonanz-Wahrscheinlichkeit
        weighted_candidates = []
        weights = []

        for pos in candidates:
            prob = self.calculate_probability(*pos)
            weighted_candidates.append(pos)
            weights.append(prob)

        # Kollaps der Wellenfunktion (Entscheidung)
        new_pos = random.choices(weighted_candidates, weights=weights, k=1)[0]
        self.e_pos = new_pos

        # Speichere Historie für Visualisierung (die "Wolke")
        self.history.append(new_pos)
        if len(self.history) > 20:  # Behalte nur die letzten 20 Positionen
            self.history.pop(0)

    def get_dialogue(self):
        # Kommunikation zwischen Kern und Schale
        if random.random() < 0.5:
            return f"🔴 PROTON: Ich bin der Anker. Frequenz {self.proton.frequency}Hz stabil."
        dist = math.sqrt(self.e_pos[0] ** 2 + self.e_pos[1] ** 2)
        state = "harmonisch" if 2.5 < dist < 3.5 else "gespannt"
        return f"🔵 ELECTRON: Ich tanze bei Radius {dist:.1f}. Mein Zustand ist {state}."
