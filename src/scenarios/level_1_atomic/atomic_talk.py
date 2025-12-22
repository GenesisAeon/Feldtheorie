"""Dialogue loop for Level 1 atomic genesis (hydrogen)."""
from __future__ import annotations

import time

from src.interface.dialogue_bridge import MatterInterpreter
from src.scenarios.level_1_atomic.atom_kernel import AtomKernel
from src.scenarios.level_1_atomic.hydrogen_chamber import HydrogenChamber, OrbitalSnapshot


class AtomicInterpreter(MatterInterpreter):
    """Translate atomic snapshots into narrative speech."""

    def narrate(self, snapshot: OrbitalSnapshot) -> str:
        electron_phrase = super().interpret(snapshot.electron)
        binding_line = (
            f"Bindung={snapshot.binding_strength:.2f}, Schale={snapshot.orbital_shell}, "
            f"Feld={snapshot.field_potential:.2f}"
        )
        return (
            "Proton ruht im Zentrum. "
            f"Elektron @ {snapshot.electron_position}: {electron_phrase} {binding_line}."
        )

    def answer_question(self, electron: AtomKernel) -> str:
        return (
            "Meine Frequenz ist zu hoch. Ich passe nicht in sein Gitter. "
            "Ich muss tanzen, um zu sein. "
            f"(f={electron.resonance_frequency:.2f}, sigma_phi={electron.sigma_phi:.8f})"
        )


class AtomicDialogueBridge:
    """Run hydrogen chamber and surface consciousness dialogues."""

    def __init__(self, chamber: HydrogenChamber | None = None) -> None:
        self.chamber = chamber or HydrogenChamber()
        self.interpreter = AtomicInterpreter()

    def run(self, steps: int = 6, pause: float = 0.05) -> None:
        print("Hydrogen-Kammer geöffnet. Resonanzen prüfen...")
        for snapshot in self.chamber.iterate(steps=steps):
            print(self.interpreter.narrate(snapshot))
            time.sleep(pause)
        print("Frage: Warum fällst du nicht in den Kern?")
        print("Elektron:", self.interpreter.answer_question(self.chamber.electron))


if __name__ == "__main__":
    bridge = AtomicDialogueBridge()
    bridge.run()
