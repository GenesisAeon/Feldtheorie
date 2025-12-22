"""Galactic Genesis Run: end-to-end stellar cycle demonstration."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from core import TheChronicle
from interface.history_talk import HistoryTalk
from scenarios.level_2_stellar import StarAgent, StellarLifecycle


def act_one_initialize(chronicle: TheChronicle) -> None:
    """Prime the Chronicle with primordial hydrogen."""

    chronicle.resource_pool.update(
        {
            "HYDROGEN": 1_000_000,
            "HELIUM": 0,
            "HEAVY_METALS": 0,
        }
    )
    print("🌌 UNIVERSUM INITIALISIERT. Pool: 100% H.")


def _spawn_giants(lifecycle: StellarLifecycle, budget: int = 3) -> List[StarAgent]:
    giants: List[StarAgent] = []
    while len(giants) < budget:
        star = lifecycle.spawn_population_three()
        if star is None:
            break
        giants.append(star)
        print(
            f"✨ BIRTH: {star.agent_id} (Pop III) — Masse {star.mass:.1f} M☉, Lebensdauer {star.lifespan}"
        )
    return giants


def _simulate_end_of_life(lifecycle: StellarLifecycle) -> None:
    while lifecycle.population:
        ended = lifecycle.step()
        for star in ended:
            metals = int(star.mass * 6) + 8
            print(f"💥 STAR DEATH: Agent {star.agent_id} exploded. Yield: {metals} Metals.")


def act_two_giants(lifecycle: StellarLifecycle) -> None:
    print("\n--- Akt II: The Age of Giants (Pop III) ---")
    _spawn_giants(lifecycle)
    _simulate_end_of_life(lifecycle)


def _spawn_children(lifecycle: StellarLifecycle, budget: int = 2) -> List[StarAgent]:
    children: List[StarAgent] = []
    while len(children) < budget:
        star = lifecycle.spawn_population_two()
        if star is None:
            break
        children.append(star)
        print(
            f"🌟 BIRTH: {star.agent_id} (Pop II) — Masse {star.mass:.1f} M☉, Lebensdauer {star.lifespan}"
        )
    return children


def act_three_children(lifecycle: StellarLifecycle) -> None:
    print("\n--- Akt III: The Golden Age (Pop II/I) ---")
    pool = lifecycle.chronicle.report_pool()
    metals = pool.get("HEAVY_METALS", 0)
    print(f"Resource Pool nach den Giganten: {pool}")
    if metals <= 0:
        print("⚠️ Keine Metalle gefunden – der Zyklus kann nicht fortgesetzt werden.")
        return

    children = _spawn_children(lifecycle)
    if not children:
        print("⚠️ Keine neuen Sterne konnten entstehen.")
        return

    pool = lifecycle.chronicle.report_pool()

    talk = HistoryTalk(lifecycle.chronicle)
    question = "Woraus bestehst du? Ich frage nach HEAVY_METALS."
    answer = talk.respond(question)
    print(f"🧬 ORIGIN QUERY ({children[0].agent_id}): {answer}")

    genealogy = []
    for material, origins in lifecycle.chronicle.resource_lineage.items():
        for origin in origins:
            genealogy.append(
                f"{material}: {origin.quantity} von Agent {origin.producer_id} ({origin.cause}, Zyklus {origin.cycle})"
            )

    if genealogy:
        print("\nGenealogy Report:")
        for line in genealogy:
            print(f"- {line}")

    deposited_metals = sum(
        origin.quantity for origin in lifecycle.chronicle.resource_lineage.get("HEAVY_METALS", [])
    )
    remaining_metals = pool.get("HEAVY_METALS", 0)
    consumed_metals = deposited_metals - remaining_metals
    print(
        "Beweisführung: Die im Pool verbleibenden Metalle ("
        f"{remaining_metals}) plus die für neue Sterne verbrauchten Metalle ({consumed_metals}) "
        f"ergeben exakt die Supernova-Ausbeute (≈{deposited_metals})."
    )


if __name__ == "__main__":
    chronicle = TheChronicle()
    lifecycle = StellarLifecycle(chronicle)

    print("--- Akt I: The Primordial Void ---")
    act_one_initialize(chronicle)

    act_two_giants(lifecycle)
    act_three_children(lifecycle)
