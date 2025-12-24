"""
Level 7: The Cosmic Loop
=========================

Die Physik der Reinkarnation und des Scheiterns.

Ein Universum durchläuft seinen Zyklus von Vakuum bis Bewusstsein.
Das erreichte Bewusstsein (ECM-Score) wird in einen "Cosmic Seed" komprimiert.
Dieser Samen versucht, ein neues Universum zu zünden - aber es kann scheitern!

Dies ist der "Evolutionäre Flaschenhals": Nicht jeder Samen keimt.
Nur die stabilsten ECM-Kopplungen überleben und vererben sich weiter.
"""

import random
import time
from dataclasses import dataclass
from typing import Optional

# Importiere unsere vorherigen Errungenschaften
from src.scenarios.level_6_consciousness.brain_physics import HiveMind


@dataclass
class CosmicSeed:
    """
    Ein komprimierter Informationszustand aus einem sterbenden Universum.

    Trägt das "genetische Material" (ECM-Kopplung) des Vorgängers.
    """
    generation: int
    ancestor_ecm_score: float  # Das Erbe (Wie bewusst war der Vorgänger?)
    dna_mutation_rate: float   # Wie stark variieren die Naturkonstanten?

    def try_germinate(self) -> Optional[dict]:
        """
        Der Versuch, ein neues Universum zu starten.

        ⚠️  KEINE GARANTIE! Viele Samen sterben im kalten Vakuum. ⚠️

        Die Keimwahrscheinlichkeit hängt vom vererbten ECM-Score ab:
        - Höherer ECM = Stabilere Information = Bessere Chancen
        - Aber: Zu komplexe Information kann auch instabil sein

        Returns:
            Optional[dict]: Neue Physik-Parameter oder None (Fehlschlag)
        """
        # Basis-Chance zu keimen (40% - Das Universum ist geizig!)
        base_chance = 0.4

        # Ein hohes ECM-Erbe erhöht die Chance (der Geist "will" existieren)
        # Die UATC-Logik: Bewusstsein ist ein Attraktor im Phasenraum
        success_prob = base_chance + (self.ancestor_ecm_score * 0.2)

        # Aber: Zu viel Mutation kann destabilisieren
        stability_penalty = self.dna_mutation_rate * 0.3
        success_prob -= stability_penalty

        # Würfeln!
        roll = random.random()

        if roll < success_prob:
            # ✨ ERFOLG: Neue Parameter generieren
            # Wir mutieren die Naturkonstanten basierend auf dem Erbe
            new_physics = {
                # Gravitation (G) - muss stabil bleiben für Galaxienbildung
                'G': 1.0 + random.uniform(-self.dna_mutation_rate, self.dna_mutation_rate),

                # Feinstrukturkonstante - Wichtig für Atomstabilität
                # Höheres ECM erlaubt feinere Variation (Stabileres "Gedächtnis")
                'FINE_STRUCTURE': 0.007 + (random.uniform(-0.001, 0.001) * (1 / (self.ancestor_ecm_score + 0.1)))
            }
            return new_physics
        else:
            # ❌ FEHLSCHLAG: Der Samen ist tot
            return None


class UniverseRunner:
    """
    Führt den kompletten Lebenszyklus eines Universums durch.

    Von der Keimung über die Evolution bis zum Tod.
    Misst am Ende den finalen ECM-Score für die Vererbung.
    """

    def __init__(self, seed: CosmicSeed):
        self.seed = seed
        self.physics = None
        self.is_alive = False
        self.final_ecm = 0.0

    def run_simulation(self) -> bool:
        """
        Simuliert den kompletten Universum-Zyklus.

        Returns:
            bool: True wenn das Universum überhaupt existiert hat, False bei Keimfehler
        """
        # ═══════════════════════════════════════════════════════════
        # PHASE 1: KEIMUNG (Wird das Universum überhaupt geboren?)
        # ═══════════════════════════════════════════════════════════
        print(f"\n🌱 SEED (Gen {self.seed.generation}): Attempting germination...")
        print(f"   Inherited ECM: {self.seed.ancestor_ecm_score:.4f}")
        print(f"   Mutation Rate: {self.seed.dna_mutation_rate:.4f}")

        self.physics = self.seed.try_germinate()

        if not self.physics:
            print("   ❌ FAILED. The seed is dormant/dead. Entropy won.")
            return False  # Universum existiert nicht

        print(f"   ✨ SUCCESS! Big Bang initiated.")
        print(f"   Physics: G={self.physics['G']:.3f}, α={self.physics['FINE_STRUCTURE']:.5f}")
        self.is_alive = True

        # ═══════════════════════════════════════════════════════════
        # PHASE 2: MATERIE-STABILITÄT (Kollabiert das Universum?)
        # ═══════════════════════════════════════════════════════════
        # Wenn Gravitation zu extrem ist, kollabiert alles sofort
        if not (0.85 < self.physics['G'] < 1.15):
            print("   💥 GRAVITY COLLAPSE! Universe imploded early.")
            print("   (G was too extreme for stable matter formation)")
            return True  # Gestorben, aber existierte kurz

        # Wenn Feinstrukturkonstante zu weit weg, keine Atome
        if not (0.005 < self.physics['FINE_STRUCTURE'] < 0.010):
            print("   ⚛️  ATOMIC INSTABILITY! No stable atoms formed.")
            print("   (Universe remained a formless plasma)")
            return True

        print("   ✅ Matter Formation: Stable")

        # ═══════════════════════════════════════════════════════════
        # PHASE 3: ZEITRAFFER DURCH DIE EVOLUTION
        # ═══════════════════════════════════════════════════════════
        # In der echten Simulation würden wir Level 0-5 durchlaufen
        # Hier simulieren wir das abstrakt mit Wahrscheinlichkeiten

        # Chance auf biologisches Leben (hängt von Physik ab)
        life_probability = 0.6 * (1.0 - abs(self.physics['G'] - 1.0))

        if random.random() > life_probability:
            print("   🏜️  BARREN UNIVERSE. No life emerged.")
            print("   (Conditions were hostile)")
            return True

        print("   🌿 Biological Life: Emerged")

        # ═══════════════════════════════════════════════════════════
        # PHASE 4: BEWUSSTSEINS-BILDUNG (Der Höhepunkt)
        # ═══════════════════════════════════════════════════════════
        print("   🧠 Developing Consciousness...")

        # Simuliere Level 6: Ein kleines neuronales Netz
        mind_size = 4  # Klein, weil wir nur den Prinzip-Beweis wollen
        mind = HiveMind(width=mind_size, height=mind_size)

        # Simuliere "Denkzyklen" (Evolution der Neurosynchronisation)
        thought_cycles = 10
        for cycle in range(thought_cycles):
            # Zufälliger Stimulus (Sinneseindruck aus dem Universum)
            stim_x = random.randint(0, mind_size - 1)
            stim_y = random.randint(0, mind_size - 1)
            mind.think((stim_x, stim_y))

        # Der finale ECM-Score ist die erreichte Kohärenz
        self.final_ecm = mind.coherence

        print(f"   👁️  Observer State Reached!")
        print(f"   Final ECM Score: {self.final_ecm:.4f}")

        # Bewusstseins-Klassifikation
        if self.final_ecm > 0.8:
            print("   🌟 ENLIGHTENED UNIVERSE (High Coherence)")
        elif self.final_ecm > 0.5:
            print("   💭 DREAMING UNIVERSE (Medium Coherence)")
        else:
            print("   😴 SLEEPING UNIVERSE (Low Coherence)")

        return True
