"""V5c (protocol commit): event scheme, crossing time and evaluation logic.

Only short horizons and the reproduction of one KV-V5 run; the KV-V5c protocol
run itself starts after the GO of the SCF coordination.

Run explicitly: python -m pytest -q -p no:cacheprovider experiments/kosmische_vererbung/tests
"""
from __future__ import annotations

import ast
import json
import math
from pathlib import Path

import pytest

from experiments.kosmische_vererbung.chem import evaluate_v5c, run_v5c
from experiments.kosmische_vererbung.chem.run_v5 import initial_zones

HERE = Path(__file__).resolve().parents[1] / "chem"
P5 = json.loads((HERE / "protocol_v5.json").read_text(encoding="utf-8"))
P5C = json.loads((HERE / "protocol_v5c.json").read_text(encoding="utf-8"))
HV = P5C["hand_values"]


def short(duration):
    return dict(P5C, duration_myr=duration)


def test_v5c_keeps_the_v5_model():
    for key in ("zone_gas_mass", "primordial_mass_fractions", "star_formation", "rules", "exchange_rates_per_myr", "duration_myr"):
        assert P5C[key] == P5[key], key
    for init in ("A", "B"):
        assert P5C["initial_states"][init]["zones"] == P5["initial_states"][init]["zones"]


def test_hand_values_follow_their_formulas():
    for k in (0.01, 0.1):
        ts = math.log(1 / (1 - 1e-5 / 0.01)) / (2 * k)
        assert HV["crossing_time_myr"][f"k={k}"] == pytest.approx(ts, rel=1e-15)
        assert HV["pop3_mass_event_msun"][f"k={k}"] == pytest.approx(1e4 * ts, rel=1e-15)
    for dt in P5C["dt_myr"]:
        assert HV["pop3_mass_grid_k_gt_0_msun"][str(dt)] == 1e4 * dt
        assert HV["pop3_mass_k0_msun"][str(dt)] == pytest.approx(1e6 * (1 - (1 - 0.01 * dt) ** (3 / dt)), rel=1e-14)


def test_grid_scheme_reproduces_the_committed_v5_run():
    raw = json.loads((HERE / "runs" / "v5_mean_vs_distribution" / "raw.json").read_text(encoding="utf-8"))
    v5 = next(r["series"] for r in raw["runs"] if (r["rule"], r["init"], r["k"], r["dt"]) == ("P3", "A", 0.01, 0.5))
    grid = run_v5c.simulate(P5C, "P3", "A", 0.01, 0.5, "grid")
    assert grid["mean_Z"] == v5["mean_Z"] and grid["pop3_mass_formed"] == v5["pop3_mass_formed"]


@pytest.mark.parametrize("k", [0.01, 0.1])
def test_crossing_time_matches_hand_value(k):
    zones = initial_zones(P5C, "A")
    rates = [[0.0, k], [k, 0.0]]
    xtol = P5C["event_scheme"]["xtol_myr"]
    tau = run_v5c.crossing_time(zones, rates, 1e-5, 0.5, xtol)
    assert tau == pytest.approx(HV["crossing_time_myr"][f"k={k}"], abs=2 * xtol)
    zones.exchange(rates, tau)
    assert zones.zone_metallicities()[0] >= 1e-5   # upper bracket end: threshold reached


def test_no_crossing_without_exchange_or_above_threshold():
    zones = initial_zones(P5C, "B")
    assert run_v5c.crossing_time(zones, [[0, 0.1], [0.1, 0]], 1e-5, 0.5, 1e-12) is None
    zones = initial_zones(P5C, "A")
    assert run_v5c.crossing_time(zones, [[0, 0.0], [0.0, 0]], 1e-5, 0.5, 1e-12) is None


@pytest.mark.parametrize("k", [0.01, 0.1])
@pytest.mark.parametrize("dt", [0.5, 0.125])
def test_event_pop3_mass_matches_hand_value_for_any_dt(k, dt):
    s = run_v5c.simulate(short(2.0), "P3", "A", k, dt, "event")
    assert s["pop3_mass_formed"][-1] == pytest.approx(HV["pop3_mass_event_msun"][f"k={k}"], rel=1e-6)
    assert s["event_splits"] == 1
    assert max(s["budget_rel_error"]) < 1e-12


@pytest.mark.parametrize("dt", [0.5, 0.25])
def test_grid_pop3_mass_is_one_step(dt):
    s = run_v5c.simulate(short(2.0), "P3", "A", 0.01, dt, "grid")
    assert s["pop3_mass_formed"][-1] == pytest.approx(HV["pop3_mass_grid_k_gt_0_msun"][str(dt)], rel=1e-12)


def test_without_exchange_both_schemes_agree_and_match_hand_value():
    g = run_v5c.simulate(short(5.0), "P3", "A", 0.0, 0.5, "grid")
    e = run_v5c.simulate(short(5.0), "P3", "A", 0.0, 0.5, "event")
    assert g["mean_Z"] == e["mean_Z"] and g["pop3_mass_formed"] == e["pop3_mass_formed"]
    assert g["pop3_mass_formed"][-1] == pytest.approx(HV["pop3_mass_k0_msun"]["0.5"], rel=1e-12)


def test_linear_rule_stays_lumpable_in_the_event_scheme():
    A = run_v5c.simulate(short(10.0), "L", "A", 0.1, 0.5, "event")
    B = run_v5c.simulate(short(10.0), "L", "B", 0.1, 0.5, "event")
    assert all(abs(a - b) / b <= 1e-12 for a, b in zip(A["mean_Z"], B["mean_Z"]))


def test_split_guard_raises():
    p = dict(P5C, event_scheme={"xtol_myr": 1e-12, "max_splits_per_step": 0}, duration_myr=1.0)
    with pytest.raises(RuntimeError):
        run_v5c.simulate(p, "P3", "A", 0.01, 0.5, "event")


def test_convergence_rule_uses_absolute_and_relative_tolerance():
    tol = {"atol": 10.0, "rtol": 0.02}
    assert evaluate_v5c._converged(29572.68, 29563.57, tol)[0] == "evaluated"     # 9.1 <= 10 + 591
    assert evaluate_v5c._converged(1250.0, 625.0, tol)[0] == "numerical_failure"   # 625 > 10 + 12.5
    assert evaluate_v5c._converged(50.03, 50.02, tol)[0] == "evaluated"
    assert evaluate_v5c._converged(None, 1.0, tol)[0] == "not_evaluated"
    # tiny values: the relative error is 100 %, only atol decides (Astra's note)
    tol_r = P5C["convergence"]["r"]
    assert evaluate_v5c._converged(2e-5, 1e-5, tol_r)[0] == "evaluated"
    assert evaluate_v5c._converged(3e-4, 1e-5, tol_r)[0] == "numerical_failure"


def test_evaluation_does_not_import_the_model():
    tree = ast.parse((HERE / "evaluate_v5c.py").read_text(encoding="utf-8"))
    names = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    names |= {n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert not any(x in m for m in names for x in ("kernel", "zones", "rules", "run_v5"))
