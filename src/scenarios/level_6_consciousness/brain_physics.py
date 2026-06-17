import math
import random

from src.core.agent_kernel import ExistenceScale, UATCAgent


class NeuronAgent(UATCAgent):
    def __init__(self, x, y):
        super().__init__()
        # Neuronen schwingen im Gamma-Bereich (40 Hz - Bewusstsein)
        self.incarnate(ExistenceScale.BIOLOGICAL, {'base_frequency': 40.0})
        self.pos = (x, y)
        self.phase = random.uniform(0, 2 * math.pi) # Zufällige Phase
        self.activation = 0.0
        self.connections: list[NeuronAgent] = []

    def connect(self, other: 'NeuronAgent'):
        # Synapse bilden
        self.connections.append(other)
        other.connections.append(self)

    def step_resonance(self, input_signal: float = 0.0):
        # 1. Input integrieren
        self.activation = input_signal * 0.5

        # 2. Nachbarn "hören" (Kollektive Schwingung)
        # Kuramoto-Modell (vereinfacht): Passe Phase an Nachbarn an
        phase_sum = 0
        for neighbor in self.connections:
            # Sinus der Phasendifferenz bestimmt Einfluss
            delta = math.sin(neighbor.phase - self.phase)
            phase_sum += delta * neighbor.activation

        # 3. Phase updaten (Synchronisation)
        coupling_strength = 0.1
        self.phase += self.frequency * 0.01 + (coupling_strength * phase_sum)
        self.phase %= 2 * math.pi

        # 4. Feuern? (Wenn Phase ~ 0)
        if self.activation < 0.1 and abs(self.phase) < 0.5:
             self.activation = 1.0 # Self-Excitation durch Resonanz

    def get_symbol(self):
        # Visualisierung: Helligkeit je nach Aktivierung
        if self.activation > 0.8:
            return "█"  # Feuert
        if self.activation > 0.5:
            return "▓"
        if self.activation > 0.2:
            return "▒"
        return "░" # Ruhe

class HiveMind:
    def __init__(self, width=5, height=5):
        self.neurons = []
        self.grid = {}

        # Gitter erstellen
        for y in range(height):
            for x in range(width):
                n = NeuronAgent(x, y)
                self.neurons.append(n)
                self.grid[(x,y)] = n

        # Vernetzen (Jeder mit Nachbarn)
        for n in self.neurons:
            x, y = n.pos
            neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
            for nx, ny in neighbors:
                if (nx, ny) in self.grid:
                    n.connect(self.grid[(nx, ny)])

        self.coherence = 0.0

    def think(self, stimulus_pos: tuple[int, int]):
        # Stimulus einspeisen
        target = self.grid.get(stimulus_pos)
        if target:
            target.activation = 1.0 # Impuls!

        # Netzwerk Update
        phases = []
        for n in self.neurons:
            # Input klingt ab, Resonanz übernimmt
            current_input = 1.0 if n.pos == stimulus_pos else 0.0
            n.step_resonance(current_input)
            phases.append(n.phase)

        # Globale Kohärenz messen (Ordnungsparameter)
        # Wie synchron sind alle Phasen? (0 = Chaos, 1 = Ein Gedanke)
        # Vereinfachte Varianz-Messung
        avg_phase = sum(phases) / len(phases)
        variance = sum((p - avg_phase)**2 for p in phases) / len(phases)
        self.coherence = 1.0 / (1.0 + variance)

    def get_thought(self):
        if self.coherence < 0.2:
            return "Rauschen... (Schlaf)"
        elif self.coherence < 0.8:
            return "Verarbeitung... (Traum)"
        else:
            return "💡 HEUREKA! (Bewusstsein)"
