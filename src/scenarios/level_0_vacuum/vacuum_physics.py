import random

from src.core.agent_kernel import ExistenceScale, UATCAgent


class HexGrid:
    def __init__(self, radius: int):
        self.radius = radius
        self.cells: dict[tuple[int, int], UATCAgent] = {}
        self.stable_clusters = 0

    def get_neighbors(self, q, r) -> list[tuple[int, int]]:
        # Die 6 Nachbarn im Hex-Gitter
        directions = [
            (1, 0),
            (1, -1),
            (0, -1),
            (-1, 0),
            (-1, 1),
            (0, 1),
        ]
        return [(q + dq, r + dr) for dq, dr in directions]

    def step(self):
        # 1. Entropie: Instabile Fluktuationen zerfallen
        to_remove = []
        for coord, agent in self.cells.items():
            # Wenn nicht stabilisiert (Scale ist noch VACUUM), zerfällt es
            if agent.scale == ExistenceScale.VACUUM:
                if random.random() < 0.3:  # 30% Zerfallsrate pro Tick
                    to_remove.append(coord)

        for coord in to_remove:
            del self.cells[coord]

        # 2. Fluktuation: Neue Agenten erscheinen
        # Wir versuchen 5 neue Spawns pro Tick
        for _ in range(5):
            q = random.randint(-self.radius, self.radius)
            r = random.randint(-self.radius, self.radius)
            if (q, r) not in self.cells:
                # Neuer Geist erscheint
                agent = UATCAgent()
                agent.incarnate(ExistenceScale.VACUUM, {"base_frequency": random.uniform(0.1, 0.9)})
                self.cells[(q, r)] = agent

        # 3. Resonanz: Suche nach Dreiecken (Triangulation)
        # In UATC ist das Dreieck die stabilste Form (Proton-Basis?)
        self._check_geometry()

    def _check_geometry(self):
        # Prüfe jeden Agenten
        for coord, agent in self.cells.items():
            if agent.scale != ExistenceScale.VACUUM:
                continue  # Schon stabil

            neighbors = self.get_neighbors(*coord)
            active_neighbors = [n for n in neighbors if n in self.cells]

            # Einfachste Resonanz: Hat 2 Nachbarn, die auch zueinander Nachbarn sind (Dreieck)
            # Wir prüfen vereinfacht auf Cluster-Dichte
            if len(active_neighbors) >= 2:
                # Stabilisierung!
                agent.scale = ExistenceScale.ATOMIC
                agent.sigma_phi = 0.0625  # Perfekte Resonanz
                self.stable_clusters += 1

                # UATC Logik: Wenn stabil, wird die Frequenz harmonisiert
                agent.frequency = 1.618  # Phi-Resonanz
