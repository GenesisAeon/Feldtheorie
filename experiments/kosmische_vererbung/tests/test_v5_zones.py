"""V5a: multi-zone kernel, oracles 5 and 6, causality, balance, yield rules.

Hand values are recorded in chem/protocol_v5.json ("hand_values"); they were
derived before the code. No protocol run happens in these tests.

Run explicitly: python -m pytest -q -p no:cacheprovider experiments/kosmische_vererbung/tests
"""
from __future__ import annotations

import json
import math
from fractions import Fraction as F
from pathlib import Path

import numpy as np
import pytest

from experiments.kosmische_vererbung.chem import rules, run_v5, zones as zmod
from experiments.kosmische_vererbung.chem.kernel import ELEMENTS, ChemState, YieldModel
from experiments.kosmische_vererbung.chem.zones import Zones, transfer_matrix

HERE = Path(__file__).resolve().parents[1] / "chem"
PROTOCOL = json.loads((HERE / "protocol_v5.json").read_text(encoding="utf-8"))


def zone(z, mass=F(1), tag=None):
    return ChemState.with_gas({"H": F(3, 4) * (1 - z) * mass, "He": F(1, 4) * (1 - z) * mass, "O": z * mass},
                              tag=tag or ("primordial" if z == 0 else "initial"))


# --- oracle 5: equal mean, different distribution ------------------------------

def test_oracle5_mean_is_equal_but_untouched_fraction_differs():
    A = Zones([zone(F(0)), zone(F(2, 100))])
    B = Zones([zone(F(1, 100)), zone(F(1, 100))])
    assert A.mean_metallicity() == B.mean_metallicity() == F(1, 100)
    assert A.f0(F(1, 10**5)) == F(1, 2) and B.f0(F(1, 10**5)) == 0
    assert A.f_primordial_origin() == F(1, 2) and B.f_primordial_origin() == 0


def test_f0_threshold_is_strict():
    # protocol: f0 counts zones with Z < z_crit; a zone exactly at z_crit is not untouched
    z_crit = F(1, 10**5)
    Z = Zones([zone(F(0)), zone(z_crit), zone(z_crit / 2)])
    assert Z.f0(z_crit) == F(2, 3)


def test_f0_and_primordial_origin_are_different_quantities():
    A = Zones([zone(0.0, 1.0), zone(0.02, 1.0)])
    A.exchange([[0, 0.1], [0.1, 0]], 0.5)
    assert A.f0(1e-5) == 0.0                     # every zone now has Z > z_crit
    assert 0.4 < A.f_primordial_origin() < 0.6   # but half of the gas is still of primordial origin


# --- oracle 6: two-zone exchange against the closed form ------------------------

def closed_form(a, b, t):
    s = a + b
    e = math.exp(-s * t)
    return np.array([[b + a * e, b * (1 - e)], [a * (1 - e), a + b * e]]) / s


@pytest.mark.parametrize("a, b, t", [(0.03, 0.01, 7.0), (0.1, 0.1, 0.5), (0.2, 0.05, 40.0)])
def test_oracle6_transfer_matrix_matches_closed_form(a, b, t):
    rates = [[0, b], [a, 0]]   # rates[j][i]: from zone i to zone j
    np.testing.assert_allclose(transfer_matrix(rates, t), closed_form(a, b, t), rtol=0, atol=1e-14)
    np.testing.assert_allclose(closed_form(0.03, 0.01, 7.0)[:, 0], [0.8168378060917941, 0.1831621939082059], atol=1e-15)


def test_oracle6_metal_masses_follow_closed_form_through_the_kernel():
    a, b = 0.03, 0.01
    Z = Zones([zone(0.0, 1.0), zone(0.02, 1.0)])
    o0 = np.array([0.0, 0.02])
    for _ in range(14):
        Z.exchange([[0, b], [a, 0]], 0.5)
    o = [z.gas_masses()["O"] for z in Z.zones]
    np.testing.assert_allclose(o, closed_form(a, b, 7.0) @ o0, rtol=1e-12, atol=0)
    # step size independence of the exact exchange (semigroup), not a second call of one integrator
    Z2 = Zones([zone(0.0, 1.0), zone(0.02, 1.0)])
    Z2.exchange([[0, b], [a, 0]], 7.0)
    np.testing.assert_allclose([z.gas_masses()["O"] for z in Z2.zones], o, rtol=1e-12)


def test_transfer_matrix_validation():
    for bad in ([[0, -1], [1, 0]], [[1, 0], [0, 0]], [[0, 1, 0], [1, 0, 0]]):
        with pytest.raises(ValueError):
            transfer_matrix(bad, 1.0)
    with pytest.raises(ValueError):
        transfer_matrix([[0, 1], [1, 0]], -1.0)


# --- causality, balance --------------------------------------------------------------

def test_no_exchange_means_no_influence_and_no_effect_before_a_change():
    def run(extra_o_at_5):
        Z = Zones([zone(0.0, 1e6), zone(0.02, 1e6)])
        m = YieldModel("x", 0.3, {"H": -0.01, "O": 0.01}, 3.0)
        z0 = []
        for step in range(20):
            t = step * 0.5
            Z.advance_to(t)
            if extra_o_at_5 and t == 5.0:
                Z.zones[1].inflow({"O": 1000.0}, "perturbation")
            z0.append(Z.zone_metallicities()[0])
            for zn in Z.zones:
                zn.form_stars(0.005 * zn.gas_mass(), m, t=t)
        return z0
    assert run(False) == run(True)   # k = 0: zone 0 never sees zone 1


def test_balance_with_exchange_star_formation_and_delays():
    Z = Zones([zone(0.0, 1e6), zone(0.02, 1e6)])
    rule = rules.make_rule(PROTOCOL["rules"]["P3"])
    before = Z.budget()
    for step in range(60):
        t = step * 0.5
        Z.advance_to(t)
        for zn, z in zip(Z.zones, Z.zone_metallicities()):
            zn.form_stars(0.005 * zn.gas_mass(), rule(z), t=t)
        Z.exchange([[0, 0.01], [0.01, 0]], 0.5)
    Z.advance_to(40.0)
    after = Z.budget()
    for e in ELEMENTS:
        assert after[e] == pytest.approx(before[e], rel=1e-12, abs=1e-6)


# --- rules (hand values in the protocol) ------------------------------------------------

def test_rules_reproduce_hand_values():
    hv = PROTOCOL["hand_values"]["initial_net_O_per_formed_mass"]
    for rid in ("L", "P3", "S"):
        rule = rules.make_rule(PROTOCOL["rules"][rid])
        got = [rule(z).net["O"] for z in hv["at_Z"]]
        np.testing.assert_allclose(got, hv[rid], rtol=1e-12)
    p3 = rules.make_rule(PROTOCOL["rules"]["P3"])
    assert p3(0.0).name == "pop3" and p3(1e-5).name == "pop2" and p3(0.99e-5).name == "pop3"
    assert p3(0.0).lifetime_myr == 3.0 and p3(0.02).lifetime_myr == 10.0
    s = rules.make_rule(PROTOCOL["rules"]["S"])
    assert s(0.05).net["O"] == 0.0   # saturated, never negative


def test_initial_synthesis_ratio_matches_hand_value():
    for rid, expected in PROTOCOL["hand_values"]["initial_synthesis_ratio_A_over_B"].items():
        rule = rules.make_rule(PROTOCOL["rules"][rid])
        a = (rule(0.0).net["O"] + rule(0.02).net["O"]) / 2
        b = rule(0.01).net["O"]
        assert a / b == pytest.approx(expected, rel=1e-12)


# --- runner contract (short horizon, not the protocol run) ------------------------------

def test_runner_short_horizon_contract():
    short = dict(PROTOCOL, duration_myr=10.0)
    for rid in ("L", "P3", "S"):
        A = run_v5.simulate(short, rid, "A", 0.01, 0.5)
        B = run_v5.simulate(short, rid, "B", 0.01, 0.5)
        assert A["t"] == [0.0, 5.0, 10.0]
        assert A["mean_Z"][0] == pytest.approx(B["mean_Z"][0], rel=1e-15)
        assert max(A["budget_rel_error"] + B["budget_rel_error"]) < 1e-12
        if rid == "L":   # linear rule: mean metallicity is exactly sufficient
            np.testing.assert_allclose(A["mean_Z"], B["mean_Z"], rtol=1e-12)
        if rid != "P3":
            assert A["pop3_mass_formed"][-1] == 0.0
    assert run_v5.simulate(short, "P3", "B", 0.0, 0.5)["pop3_mass_formed"][-1] == 0.0
    assert run_v5.simulate(short, "P3", "A", 0.0, 0.5)["pop3_mass_formed"][-1] > 0.0


def test_evaluation_does_not_import_the_kernel():
    import ast
    tree = ast.parse((HERE / "evaluate_v5.py").read_text(encoding="utf-8"))
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    imported |= {n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert not any(x in m for m in imported for x in ("kernel", "zones", "rules", "run_v5"))


def test_modules_come_from_this_checkout():
    assert Path(zmod.__file__).resolve().is_relative_to(Path(__file__).resolve().parents[3])
