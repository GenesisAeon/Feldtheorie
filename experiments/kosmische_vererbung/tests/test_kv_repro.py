"""C5: the reproduction comparison accepts rounding noise and rejects everything else.

Run explicitly: python -m pytest -q -p no:cacheprovider experiments/kosmische_vererbung/tests
"""
from __future__ import annotations

import builtins
import copy
import json
from pathlib import Path

import pytest

import kv_repro

RUNS = Path(__file__).resolve().parents[1] / "chem" / "runs"


@pytest.fixture(scope="module")
def series():
    v5 = json.loads((RUNS / "v5_mean_vs_distribution" / "raw.json").read_text(encoding="utf-8"))
    v5c = json.loads((RUNS / "v5c_resolution" / "raw.json").read_text(encoding="utf-8"))
    a = next(r["series"] for r in v5["runs"] if (r["rule"], r["init"], r["k"], r["dt"]) == ("S", "A", 0.0, 0.5))
    b = next(r["series"] for r in v5c["runs"] if (r["scheme"], r["rule"], r["init"], r["k"], r["dt"]) == ("event", "P3", "A", 0.01, 0.5))
    return {"v5": a, "v5c": b}


def _scaled_tol(values):
    flat = [v for x in values for v in (x if isinstance(x, list) else [x])]
    return kv_repro.SCALED_RTOL * max(abs(v) for v in flat)


def test_every_committed_key_has_a_rule(series):
    for s in series.values():
        assert kv_repro.compare_series(copy.deepcopy(s), s) == []


def test_astra_measured_deviations_pass(series):
    s = copy.deepcopy(series["v5"])
    s["mean_Z"][5] += 3.122502256758253e-17
    s["gas_mass"][7] += 2.0954757928848267e-09
    s["f_primordial_origin"][3] += 6.11e-16
    s["budget_rel_error"][4] += 1.1641532182693488e-16
    assert kv_repro.compare_series(s, series["v5"]) == []


def test_python312_style_summation_breaks_bits_but_passes_tolerances(series, monkeypatch):
    # Different summation order is the kind of difference seen under Python 3.12 (C5).
    from experiments.kosmische_vererbung.chem import run_v5

    protocol = json.loads((RUNS.parent / "protocol_v5.json").read_text(encoding="utf-8"))
    monkeypatch.setattr(builtins, "sum", kv_repro.neumaier_sum)
    new = json.loads(json.dumps(run_v5.simulate(protocol, "S", "A", 0.0, 0.5)))
    monkeypatch.undo()
    assert new != series["v5"]
    assert kv_repro.compare_series(new, series["v5"]) == []


def test_neumaier_sum_compensates_and_matches_plain_sum_on_exact_cases():
    assert kv_repro.neumaier_sum([1e16, 1.0, -1e16]) == 1.0
    assert sum([1e16, 1.0, -1e16]) in (0.0, 1.0)
    assert kv_repro.neumaier_sum([1, 2, 3]) == 6
    assert kv_repro.neumaier_sum([0.5, 0.25], 1.0) == 1.75


@pytest.mark.parametrize("key", ["mean_Z", "gas_mass", "f_primordial_origin", "synthesized_O", "f0"])
def test_scaled_quantity_beyond_tolerance_fails(series, key):
    s = copy.deepcopy(series["v5"])
    tol = _scaled_tol(series["v5"][key])
    s[key][6] += 0.5 * tol
    assert kv_repro.compare_series(s, series["v5"]) == []
    s[key][6] += 2.0 * tol
    assert any(p.startswith(key) for p in kv_repro.compare_series(s, series["v5"]))


def test_nested_zone_z_beyond_tolerance_fails(series):
    s = copy.deepcopy(series["v5"])
    s["zone_Z"][9][1] += 2.0 * _scaled_tol(series["v5"]["zone_Z"])
    assert any(p.startswith("zone_Z") for p in kv_repro.compare_series(s, series["v5"]))


def test_pop3_mass_beyond_tolerance_fails(series):
    s = copy.deepcopy(series["v5c"])
    s["pop3_mass_formed"][-1] += 2.0 * _scaled_tol(series["v5c"]["pop3_mass_formed"])
    assert any(p.startswith("pop3_mass_formed") for p in kv_repro.compare_series(s, series["v5c"]))


def test_budget_beyond_absolute_tolerance_fails(series):
    s = copy.deepcopy(series["v5c"])
    s["budget_rel_error"][2] += 2.0 * kv_repro.ABSOLUTE["budget_rel_error"]
    assert any(p.startswith("budget_rel_error") for p in kv_repro.compare_series(s, series["v5c"]))


def test_time_axis_and_event_count_are_exact(series):
    s = copy.deepcopy(series["v5c"])
    s["t"][3] = s["t"][3] + 1e-15 * s["t"][3]
    assert s["t"][3] != series["v5c"]["t"][3]
    assert any(p.startswith("t:") for p in kv_repro.compare_series(s, series["v5c"]))
    s = copy.deepcopy(series["v5c"])
    s["event_splits"] += 1
    assert any(p.startswith("event_splits") for p in kv_repro.compare_series(s, series["v5c"]))


def test_keys_lengths_and_finiteness_are_checked(series):
    s = copy.deepcopy(series["v5"])
    del s["f0"]
    assert any("keys differ" in p for p in kv_repro.compare_series(s, series["v5"]))
    s = copy.deepcopy(series["v5"])
    s["unknown"] = s.pop("f0")
    assert kv_repro.compare_series(s, series["v5"])
    s = copy.deepcopy(series["v5"])
    s["mean_Z"] = s["mean_Z"][:-1]
    assert any(p.startswith("mean_Z: shape") for p in kv_repro.compare_series(s, series["v5"]))
    s = copy.deepcopy(series["v5"])
    s["mean_Z"][2] = float("nan")
    assert any(p.startswith("mean_Z: non-finite") for p in kv_repro.compare_series(s, series["v5"]))
    s = copy.deepcopy(series["v5"])
    s["extra"] = [0.0]
    committed = dict(series["v5"], extra=[0.0])
    assert any("no comparison rule" in p for p in kv_repro.compare_series(s, committed))


def test_environment_binding_reports_each_difference():
    here = kv_repro.environment()
    assert kv_repro.environment_mismatch(dict(here)) is None
    other = dict(here, python="0.0.1", numpy="0.0.2")
    reason = kv_repro.environment_mismatch(other)
    assert "python 0.0.1 (Lauf)" in reason and "numpy 0.0.2 (Lauf)" in reason and "scipy" not in reason


def test_tolerance_stays_below_strictest_protocol_criterion():
    # L: |r| <= 1e-12 (V5 and V5c); a relative error eps in Z_A and Z_B moves r by at most about 2*eps.
    assert 2 * kv_repro.SCALED_RTOL < 1e-12
    assert kv_repro.ABSOLUTE["budget_rel_error"] < 1e-9
