import random

from src.core.agent_kernel import ExistenceScale, UATCAgent
from src.core.chronicle import TheChronicle


class MolecularChain(UATCAgent):
    def __init__(self, sequence: str = ""):
        super().__init__()
        self.incarnate(ExistenceScale.BIOLOGICAL, {'base_frequency': 432.0}) # Life Freq
        self.sequence = sequence # z.B. "A-C-G-T"
        self.stability = 0.0
        self.energy = 0.0

    def calculate_resonance(self):
        """
        UATC Bio-Logik:
        Komplexität erzeugt Stabilität, aber nur wenn Muster harmonisch sind.
        Wir simulieren einfache Basen-Paarung Logik.
        """
        if not self.sequence:
            self.stability = 0.0
            return

        # Einfache Regel: Palindrome oder Wiederholungen sind stabiler (Kristallin)
        # Aber LEBEN braucht Asymmetrie.
        # Wir belohnen Länge und Vielfalt.
        length = len(self.sequence)
        variety = len(set(self.sequence))

        # Basis-Stabilität
        self.stability = (length * 0.1) + (variety * 0.2)

        # 'Goldene Sequenz' Bonus (Zufälliges Ziel-Muster)
        if "A-T" in self.sequence or "G-C" in self.sequence:
            self.stability += 0.5

    def step_entropy(self) -> bool:
        """
        Der Zahn der Zeit. Gibt True zurück, wenn das Molekül zerfällt.
        """
        decay_chance = 0.1 / (self.stability + 0.01)
        if random.random() < decay_chance:
            # Molekül zerbricht
            return True
        return False

    def try_replicate(self, resource_pool: int) -> bool:
        """
        Autopoiesis: Wenn genug Energie und Stabilität da ist, kopiere dich.
        """
        cost = len(self.sequence)
        if self.stability > 1.0 and resource_pool >= cost:
            # Erfolgreiche Replikation
            return True
        return False

    def get_voice(self):
        if len(self.sequence) < 3:
            return "Ich bin nur ein Fragment..."
        elif self.stability < 0.5:
            return "Ich halte... kaum... zusammen..."
        else:
            return f"🧬 {self.sequence}: Ich bin eine Schleife. Ich erinnere mich."

class PrimordialSoup:
    def __init__(self):
        self.chronicle = TheChronicle()
        self.molecules: list[MolecularChain] = []
        self.free_monomers = 1000 # Der "Dreck" im Wasser (C, H, O, N)
        self.generation = 0

    def spark_of_life(self):
        """
        Blitzschlag! Energie führt zu zufälligen Kombinationen.
        """
        self.generation += 1

        # 1. Spontane Entstehung (Random Synthesis)
        if self.free_monomers > 0:
            for _ in range(5): # 5 Versuche pro Tick
                length = random.randint(1, 4)
                if self.free_monomers >= length:
                    bases = ['A', 'C', 'G', 'T']
                    seq = "-".join(random.choices(bases, k=length))

                    new_mol = MolecularChain(seq)
                    new_mol.calculate_resonance()
                    self.molecules.append(new_mol)
                    self.free_monomers -= length

        # 2. Evolutionäre Schritte
        next_gen_molecules = []
        for mol in self.molecules:
            # A. Entropie Check
            if mol.step_entropy():
                # Zerfall zurück in den Pool
                self.free_monomers += len(mol.sequence)
                continue # Stirbt

            # B. Wachstum / Interaktion
            if random.random() < 0.3 and self.free_monomers > 0:
                # Wächst um eine Base
                mol.sequence += "-" + random.choice(['A', 'C', 'G', 'T'])
                mol.calculate_resonance()
                self.free_monomers -= 1

            # C. Replikation (Das Wunder)
            if mol.try_replicate(self.free_monomers):
                # Kopie erstellen!
                child = MolecularChain(mol.sequence)
                child.calculate_resonance()
                child.stability += 0.1 # Evolutionärer Vorteil (Lerneffekt)
                next_gen_molecules.append(child)
                self.free_monomers -= len(mol.sequence)

            next_gen_molecules.append(mol)

        self.molecules = next_gen_molecules
        # Sortiere nach Stabilität (Survival of the Fittest)
        self.molecules.sort(key=lambda x: x.stability, reverse=True)
