"""Several gas reservoirs (zones) with linear exchange (package V5).

Each zone is a ``ChemState`` (kernel.py). Exchange moves well-mixed gas
between zones with a constant rate matrix ``k[j][i]`` (fraction of zone i's
gas per Myr that flows to zone j). Over a step dt the transfer matrix is the
matrix exponential P = expm(G dt) of the generator G = k - diag(column sums),
applied to every element and provenance tag at once. Stars stay in their birth
zone and return their ejecta there.

Observables (interface agreed with the SCF session, 2026-10-11):

* ``mean_metallicity``: mass-weighted Z over all zones' gas.
* ``f0(z_crit)``: mass fraction of gas in zones with Z < z_crit. This is the
  "untouched gas" of SCF MV-K1..K4; z_crit must be declared in advance.
* ``f_primordial_origin``: mass fraction of gas carrying the provenance tag
  ``primordial``. Deliberately a different quantity from f0: in a mixed zone
  it stays > 0 after enrichment while f0 drops to 0.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import expm

from .kernel import ELEMENTS, METALS, PRIMORDIAL, ChemState


def transfer_matrix(rates, dt) -> np.ndarray:
    k = np.asarray(rates, dtype=float)
    if k.ndim != 2 or k.shape[0] != k.shape[1]:
        raise ValueError("rates must be a square matrix")
    if (k < 0).any() or (np.diag(k) != 0).any():
        raise ValueError("rates must be >= 0 with a zero diagonal")
    if dt < 0:
        raise ValueError("dt must be >= 0")
    G = k - np.diag(k.sum(axis=0))
    P = expm(G * float(dt))
    P[P < 0] = 0.0                     # rounding only (G is a Metzler matrix)
    return P / P.sum(axis=0, keepdims=True)


class Zones:
    def __init__(self, zones: list):
        if not zones:
            raise ValueError("need at least one zone")
        if len({z.t for z in zones}) != 1:
            raise ValueError("zones must share the same clock")
        self.zones = list(zones)

    @property
    def t(self):
        return self.zones[0].t

    def advance_to(self, t):
        for z in self.zones:
            z.advance_to(t)

    def exchange(self, rates, dt):
        """Mix gas between zones over dt (at the current time, lumped)."""

        P = transfer_matrix(rates, dt)
        n = len(self.zones)
        if P.shape != (n, n):
            raise ValueError("rates must be n_zones x n_zones")
        old = [{tag: dict(parcel) for tag, parcel in z.gas.items()} for z in self.zones]
        tags = sorted({tag for g in old for tag in g})
        for j, zone in enumerate(self.zones):
            zone.gas = {}
            for tag in tags:
                parcel = {e: sum(P[j, i] * old[i].get(tag, {}).get(e, 0.0) for i in range(n)) for e in ELEMENTS}
                if any(parcel.values()):
                    zone.gas[tag] = parcel

    # -- observables ----------------------------------------------------
    def gas_masses(self) -> list:
        return [z.gas_mass() for z in self.zones]

    def zone_metallicities(self) -> list:
        out = []
        for z in self.zones:
            g = z.gas_masses()
            m = sum(g.values())
            out.append(sum(g[e] for e in METALS) / m if m else None)
        return out

    def mean_metallicity(self):
        total = sum(self.gas_masses())
        metals = sum(sum(z.gas_masses()[e] for e in METALS) for z in self.zones)
        return metals / total

    def f0(self, z_crit):
        masses, zs = self.gas_masses(), self.zone_metallicities()
        return sum(m for m, z in zip(masses, zs) if z is not None and z < z_crit) / sum(masses)

    def f_primordial_origin(self):
        total = sum(self.gas_masses())
        return sum(sum(z.gas.get(PRIMORDIAL, {}).values()) for z in self.zones) / total

    def budget(self) -> dict:
        budgets = [z.budget() for z in self.zones]
        return {e: sum(b[e] for b in budgets) for e in ELEMENTS}
