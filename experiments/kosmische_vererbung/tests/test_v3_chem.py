"""V3: chemical base kernel. Oracles 1-4 and 7 of plan §10.1 plus the balance,
non-negativity, yield-convention and provenance contracts.

Hand values (derived with Fractions before the code):
  O2  t=5: gas 73 (H 1093/20, He 73/4, O 1/10); t=13: gas 79, O 3/10, remnants 21
  O3  10 M_sun pulse, lifetime 10 Myr, R=3/10: gas 90 before t=10, exactly 93 from t=10
  O4  closed box, instantaneous return: Z(M_g=50) = 0.02 ln 2 = 0.013862943611198907

Run explicitly: python -m pytest -q -p no:cacheprovider experiments/kosmische_vererbung/tests
"""
from __future__ import annotations

import math
from fractions import Fraction as F
from pathlib import Path

import pytest

from experiments.kosmische_vererbung.chem import kernel
from experiments.kosmische_vererbung.chem.kernel import ELEMENTS, ChemState, YieldModel

PRIMORDIAL_100 = {"H": F(75), "He": F(25)}
R = F(3, 10)
NET_O = {"H": F(-1, 100), "O": F(1, 100)}


def model(lifetime, net=NET_O, r=R, name="toyO"):
    return YieldModel(name, r, net, lifetime)


def total(state):
    return state.gas_mass() + sum(state.star_masses().values()) + sum(state.remnants.values()) + sum(state.ejected.values())


def test_module_comes_from_this_checkout():
    assert Path(kernel.__file__).resolve().is_relative_to(Path(__file__).resolve().parents[3])


# --- oracle 1: closed system without star formation --------------------------

def test_oracle1_nothing_changes_without_star_formation():
    s = ChemState.with_gas(PRIMORDIAL_100)
    before = s.gas_masses()
    s.advance_to(F(1000))
    assert s.gas_masses() == before and s.stars == [] and all(v == 0 for v in s.remnants.values())


# --- oracle 2: closed system with redistribution -------------------------------

def test_oracle2_total_balance_with_two_generations():
    s = ChemState.with_gas(PRIMORDIAL_100)
    s.form_stars(F(10), model(F(5)), t=F(0))
    s.form_stars(F(20), model(F(10)), t=F(3))
    s.advance_to(F(5))
    g = s.gas_masses()
    assert s.gas_mass() == 73
    assert (g["H"], g["He"], g["O"]) == (F(1093, 20), F(73, 4), F(1, 10))
    s.advance_to(F(13))
    assert s.gas_mass() == 79 and s.gas_masses()["O"] == F(3, 10)
    assert sum(s.remnants.values()) == 21 and s.stars == []
    assert total(s) == 100
    assert s.budget() == {e: PRIMORDIAL_100.get(e, 0) for e in ELEMENTS}


def test_balance_holds_at_every_event_with_inflow_and_outflow():
    s = ChemState.with_gas(PRIMORDIAL_100)
    s.form_stars(F(10), model(F(2)), t=F(0))
    s.inflow({"H": F(6), "He": F(2)}, "igm", t=F(1))
    s.form_stars(F(15), model(F(4)), t=F(2))
    s.outflow(F(5), t=F(3))
    s.advance_to(F(10))
    # budget() = gas + stars + remnants + ejected - inflow - synthesized = initial stock
    assert s.budget() == {e: PRIMORDIAL_100.get(e, 0) for e in ELEMENTS}
    assert s.inflow_total["H"] == 6 and sum(s.ejected.values()) == 5
    assert total(s) == 108


# --- oracle 3: one pulse with fixed return time ----------------------------------

def test_oracle3_no_return_before_lifetime_and_exact_return_after():
    s = ChemState.with_gas(PRIMORDIAL_100)
    s.form_stars(F(10), model(F(10)), t=F(0))
    s.advance_to(F(10) - F(1, 10**9))
    assert s.gas_mass() == 90 and len(s.stars) == 1
    s.advance_to(F(10))
    assert s.gas_mass() == 93 and sum(s.remnants.values()) == 7 and s.stars == []


def test_time_cannot_run_backwards():
    s = ChemState.with_gas(PRIMORDIAL_100)
    s.advance_to(F(5))
    with pytest.raises(ValueError):
        s.form_stars(F(1), model(F(1)), t=F(4))


# --- oracle 4: closed box with instantaneous recycling ------------------------------

def _closed_box(steps, y=F(2, 100), r=R, mg_end=F(50)):
    net = {"H": -y * (1 - r), "O": y * (1 - r)}   # y per locked-up mass
    m = YieldModel("ira", r, net, 0)
    s = ChemState.with_gas(PRIMORDIAL_100)
    locked_per_step = (100 - mg_end) / steps
    for k in range(steps):
        s.form_stars(locked_per_step / (1 - r), m, t=F(k))
    return s


def test_oracle4_discrete_recursion_exact():
    # Independent exact recursion: M' = M - (1-R)D, Z' = Z + y(1-R)D / M'
    y, steps = F(2, 100), 7
    mg, z = F(100), F(0)
    d = (F(100) - 50) / steps / (1 - R)
    for _ in range(steps):
        mg -= (1 - R) * d
        z += y * (1 - R) * d / mg
    s = _closed_box(steps)
    assert s.gas_mass() == mg == 50
    assert kernel.metallicity(s.gas_masses()) == z


def test_oracle4_converges_to_closed_box_formula():
    target = 0.02 * math.log(100 / 50)
    assert target == pytest.approx(0.013862943611198907, abs=1e-18)
    errors = []
    for steps in (50, 200, 800):
        s = _closed_box(steps, y=0.02, r=0.3, mg_end=50.0)
        errors.append(abs(kernel.metallicity(s.gas_masses()) - target))
    assert errors[2] < 1e-5
    # first-order convergence: error shrinks ~4x per 4x steps
    assert 3.0 < errors[0] / errors[1] < 5.0 and 3.0 < errors[1] / errors[2] < 5.0


def test_oracle4_formula_does_not_hold_with_delayed_return():
    # Same yields with a 50 Myr delay: before the deaths no metals at all.
    net = {"H": F(-14, 1000), "O": F(14, 1000)}
    s = ChemState.with_gas(PRIMORDIAL_100)
    for k in range(10):
        s.form_stars(F(5), YieldModel("delayed", R, net, 50), t=F(k))
    assert kernel.metallicity(s.gas_masses()) == 0


# --- oracle 7: units -----------------------------------------------------------------

def test_oracle7_same_experiment_in_years_and_myr():
    def run(unit, scale):
        s = ChemState.with_gas({"H": 75.0, "He": 25.0})
        m = YieldModel("u", 0.3, {"H": -0.01, "O": 0.01}, 7.5)  # lifetime in Myr
        for k in range(12):
            s.form_stars(2.0, m, t=k * 1.25 * scale, unit=unit)
        s.advance_to(30 * scale, unit=unit)
        return s.gas_masses(), s.t
    myr, t_myr = run("Myr", 1)
    yr, t_yr = run("yr", 10**6)
    assert t_myr == pytest.approx(t_yr, rel=1e-12)
    for e in ELEMENTS:
        assert myr[e] == pytest.approx(yr[e], rel=1e-12, abs=1e-15)
    with pytest.raises(ValueError):
        kernel.to_myr(1, "parsec")


# --- contracts -----------------------------------------------------------------------

def test_non_negativity_is_enforced():
    s = ChemState.with_gas(PRIMORDIAL_100)
    with pytest.raises(ValueError):
        s.form_stars(F(101), model(F(1)))
    with pytest.raises(ValueError):
        s.outflow(F(101))
    with pytest.raises(ValueError):
        s.form_stars(F(-1), model(F(1)))
    with pytest.raises(ValueError):
        ChemState.with_gas({"H": -1})
    # a yield model that would eject negative He from metal-free gas is out of scope
    with pytest.raises(ValueError, match="negative ejecta"):
        s.form_stars(F(1), model(F(1), net={"He": F(-1, 2), "O": F(1, 2)}))
    assert s.gas_mass() == 100   # failed calls left no partial state behind


def test_yield_model_validation():
    with pytest.raises(ValueError):
        YieldModel("x", R, {"H": F(-1, 100), "O": F(2, 100)}, 1)   # net yields must sum to 0
    with pytest.raises(ValueError):
        YieldModel("x", F(11, 10), NET_O, 1)
    with pytest.raises(ValueError):
        YieldModel("x", R, {"Fe": F(0)}, 1)
    with pytest.raises(ValueError):
        YieldModel("x", R, NET_O, -1)


def test_net_and_total_conventions_are_not_mixed_up():
    X = kernel.composition(PRIMORDIAL_100)
    total_per_mass = kernel.total_from_net(NET_O, R, X)
    assert total_per_mass["O"] == F(1, 100) and total_per_mass["H"] == R * F(3, 4) - F(1, 100)
    assert kernel.net_from_total(total_per_mass, R, X) == {e: NET_O.get(e, 0) for e in ELEMENTS}
    # Double counting: feeding total ejecta in as if they were net yields breaks
    # the mass balance and is rejected.
    with pytest.raises(ValueError):
        YieldModel("wrong", R, total_per_mass, 1)


def test_provenance_tags_add_up_and_track_generations():
    s = ChemState.with_gas(PRIMORDIAL_100)
    s.form_stars(F(10), model(F(1)), t=F(0))
    s.form_stars(F(20), model(F(1)), t=F(2))   # star 1 forms from gas containing star0 ejecta
    s.advance_to(F(5))
    prov = s.provenance()
    assert sum(prov.values()) == s.gas_mass()
    assert set(prov) == {"primordial", "toyO:star0", "toyO:star1"}
    assert all(v >= 0 for v in prov.values())
    assert prov["toyO:star0"] == 3 * (1 - F(20, 93))   # 20 of 93 M_sun of mixed gas went into star 1
    assert prov["toyO:star1"] == 6
