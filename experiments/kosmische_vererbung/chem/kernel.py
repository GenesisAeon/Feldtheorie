"""Instance-based gas / star / remnant mass balance (package V3).

A small, separately testable chemical kernel. It replaces nothing in
StellarLifecycle/TheChronicle (finding F5, toy models kept as they are).

Units: mass in solar masses (M_sun), time in Myr internally. Times can be
passed in other units through ``UNITS`` (oracle 7). The arithmetic is plain
Python, so ``fractions.Fraction`` inputs give exact results (oracles 1-4).

Yield convention (plan §6.1; no double counting):

* ``net[i]``  newly synthesised mass of element i per formed stellar mass;
  sum over elements is 0 (nuclear mass defect neglected, a documented
  baryonic-mass approximation).
* total ejecta of element i of a star of mass m born with mass fractions X:
  ``E_i = m * (R * X[i] + net[i])``; the remnant keeps ``(1 - R) * m`` with
  the birth composition.

Hence the total mass is conserved exactly and every element changes exactly
by its synthesis. Yields given as *total* ejecta must be converted with
``net_from_total`` and the convention must always be named explicitly.

Return happens exactly at ``t_birth + lifetime``: never earlier, and in full.
Provenance: every gas parcel carries a tag (``primordial``, ``inflow:<name>``,
``<yield model>:star<k>``); star formation and outflow take tags in
proportion (well-mixed gas).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from numbers import Real

ELEMENTS = ("H", "He", "C", "O", "Si", "REST")
METALS = ("C", "O", "Si", "REST")
UNITS = {"Myr": 1, "kyr": Fraction(1, 1000), "yr": Fraction(1, 10**6), "Gyr": 1000}
PRIMORDIAL = "primordial"


def _check_mass(value, what):
    if not isinstance(value, Real) or value != value or value in (float("inf"), float("-inf")) or value < 0:
        raise ValueError(f"{what} must be a finite number >= 0, got {value!r}")


def to_myr(t, unit: str):
    if unit not in UNITS:
        raise ValueError(f"unknown time unit {unit!r}; known: {sorted(UNITS)}")
    return t * UNITS[unit]


def composition(masses: dict) -> dict:
    total = sum(masses.values())
    if total == 0:
        raise ValueError("composition of an empty reservoir is undefined")
    return {e: masses.get(e, 0) / total for e in ELEMENTS}


def metallicity(masses: dict):
    """Gas-phase metal mass fraction Z = sum of C, O, Si, REST."""

    return sum(composition(masses)[e] for e in METALS)


@dataclass(frozen=True)
class YieldModel:
    """Synthetic yield model in the *net* convention (see module docstring)."""

    name: str
    return_fraction: Real
    net: dict
    lifetime_myr: Real

    def __post_init__(self):
        unknown = set(self.net) - set(ELEMENTS)
        if unknown:
            raise ValueError(f"unknown elements {sorted(unknown)}")
        if not 0 <= self.return_fraction <= 1:
            raise ValueError("return_fraction must lie in [0, 1]")
        _check_mass(self.lifetime_myr, "lifetime_myr")
        total = sum(self.net.values())
        if abs(total) > (0 if isinstance(total, (int, Fraction)) else 1e-12):
            raise ValueError(f"net yields must sum to 0 (got {total}); mass defect is not modelled")

    def ejecta(self, mass, birth_fractions: dict) -> dict:
        out = {e: mass * (self.return_fraction * birth_fractions[e] + self.net.get(e, 0)) for e in ELEMENTS}
        negative = [e for e, v in out.items() if v < 0]
        if negative:
            raise ValueError(f"yield model {self.name!r} gives negative ejecta of {negative} "
                             "for this birth composition (outside its scope)")
        return out


def net_from_total(total_per_mass: dict, return_fraction, birth_fractions: dict) -> dict:
    """Convert total ejected element mass per formed stellar mass to net yields."""

    return {e: total_per_mass.get(e, 0) - return_fraction * birth_fractions[e] for e in ELEMENTS}


def total_from_net(net: dict, return_fraction, birth_fractions: dict) -> dict:
    return {e: return_fraction * birth_fractions[e] + net.get(e, 0) for e in ELEMENTS}


@dataclass
class StarParcel:
    star_id: int
    t_birth: Real
    mass: Real
    birth_masses: dict           # element -> mass at birth
    birth_provenance: dict       # tag -> mass at birth
    yield_model: YieldModel

    @property
    def t_death(self):
        return self.t_birth + self.yield_model.lifetime_myr


@dataclass
class ChemState:
    """One well-mixed gas zone with explicit stars, remnants and outflow sink."""

    t: Real = 0
    gas: dict = field(default_factory=dict)          # tag -> {element: mass}
    stars: list = field(default_factory=list)
    remnants: dict = field(default_factory=lambda: {e: 0 for e in ELEMENTS})
    ejected: dict = field(default_factory=lambda: {e: 0 for e in ELEMENTS})   # outflow sink
    inflow_total: dict = field(default_factory=lambda: {e: 0 for e in ELEMENTS})
    synthesized: dict = field(default_factory=lambda: {e: 0 for e in ELEMENTS})
    events: list = field(default_factory=list)
    _next_star: int = 0

    @classmethod
    def with_gas(cls, masses: dict, t=0, tag: str = PRIMORDIAL) -> "ChemState":
        state = cls(t=t)
        state._add_gas(tag, masses)
        return state

    # -- views ---------------------------------------------------------
    def gas_masses(self) -> dict:
        return {e: sum(parcel.get(e, 0) for parcel in self.gas.values()) for e in ELEMENTS}

    def gas_mass(self):
        return sum(self.gas_masses().values())

    def star_masses(self) -> dict:
        return {e: sum(s.birth_masses[e] for s in self.stars) for e in ELEMENTS}

    def provenance(self) -> dict:
        return {tag: sum(m.values()) for tag, m in self.gas.items()}

    def budget(self) -> dict:
        """Element ledger: gas + stars + remnants + ejected - inflow - synthesized."""

        g, s = self.gas_masses(), self.star_masses()
        return {e: g[e] + s[e] + self.remnants[e] + self.ejected[e] - self.inflow_total[e] - self.synthesized[e]
                for e in ELEMENTS}

    # -- processes -----------------------------------------------------
    def _add_gas(self, tag: str, masses: dict):
        unknown = set(masses) - set(ELEMENTS)
        if unknown:
            raise ValueError(f"unknown elements {sorted(unknown)}")
        for e, v in masses.items():
            _check_mass(v, f"mass of {e}")
        parcel = self.gas.setdefault(tag, {e: 0 for e in ELEMENTS})
        for e in ELEMENTS:
            parcel[e] += masses.get(e, 0)

    def _take_gas(self, mass) -> tuple:
        """Remove ``mass`` from the well-mixed gas; return (elements, provenance)."""

        total = self.gas_mass()
        if mass > total:
            raise ValueError(f"requested {mass} M_sun but only {total} M_sun of gas present")
        if mass == 0:
            return {e: 0 for e in ELEMENTS}, {}
        share = mass / total
        taken, prov = {e: 0 for e in ELEMENTS}, {}
        for tag, parcel in self.gas.items():
            part = {e: parcel[e] * share for e in ELEMENTS}
            prov[tag] = sum(part.values())
            for e in ELEMENTS:
                parcel[e] -= part[e]
                taken[e] += part[e]
        return taken, prov

    def _require_time(self, t):
        if t < self.t:
            raise ValueError(f"time {t} Myr lies before the current time {self.t} Myr")

    def form_stars(self, mass, yield_model: YieldModel, t=None, unit: str = "Myr") -> StarParcel:
        """Form one stellar parcel at time t (default: now) from the mixed gas."""

        _check_mass(mass, "star mass")
        t = self.t if t is None else to_myr(t, unit)
        self.advance_to(t)
        if mass:
            if mass > self.gas_mass():
                raise ValueError(f"requested {mass} M_sun but only {self.gas_mass()} M_sun of gas present")
            # fail before any state change if the model is outside its scope
            yield_model.ejecta(mass, composition(self.gas_masses()))
        birth, prov = self._take_gas(mass)
        star = StarParcel(self._next_star, t, mass, birth, prov, yield_model)
        self._next_star += 1
        self.stars.append(star)
        self.events.append(("form", t, star.star_id, mass))
        self.advance_to(t)  # lifetime 0 = instantaneous return
        return star

    def inflow(self, masses: dict, name: str, t=None, unit: str = "Myr"):
        t = self.t if t is None else to_myr(t, unit)
        self.advance_to(t)
        self._add_gas(f"inflow:{name}", masses)
        for e in ELEMENTS:
            self.inflow_total[e] += masses.get(e, 0)
        self.events.append(("inflow", t, name, sum(masses.values())))

    def outflow(self, mass, t=None, unit: str = "Myr"):
        """Remove mixed gas to the explicit outflow sink (ejected material)."""

        _check_mass(mass, "outflow mass")
        t = self.t if t is None else to_myr(t, unit)
        self.advance_to(t)
        taken, _ = self._take_gas(mass)
        for e in ELEMENTS:
            self.ejected[e] += taken[e]
        self.events.append(("outflow", t, None, mass))

    def advance_to(self, t, unit: str = "Myr"):
        """Advance the clock; release every star with t_death <= t, in death order."""

        t = to_myr(t, unit)
        self._require_time(t)
        due = sorted((s for s in self.stars if s.t_death <= t), key=lambda s: (s.t_death, s.star_id))
        for star in due:
            self.t = star.t_death
            self._release(star)
        self.t = t

    def _release(self, star: StarParcel):
        model = star.yield_model
        ejecta = model.ejecta(star.mass, composition(star.birth_masses)) if star.mass else {e: 0 for e in ELEMENTS}
        tag = f"{model.name}:star{star.star_id}"
        self._add_gas(tag, ejecta)
        for e in ELEMENTS:
            self.remnants[e] += (1 - model.return_fraction) * star.birth_masses[e]
            self.synthesized[e] += star.mass * model.net.get(e, 0)
        self.stars.remove(star)
        self.events.append(("release", star.t_death, star.star_id, sum(ejecta.values())))
