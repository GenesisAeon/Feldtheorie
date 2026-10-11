"""V5b: the committed KV-V5 run is reproducible and its derived files are current.

Run explicitly: python -m pytest -q -p no:cacheprovider experiments/kosmische_vererbung/tests
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments.kosmische_vererbung.chem import evaluate_v5, export_v5_timeseries, run_v5

HERE = Path(__file__).resolve().parents[1] / "chem"
RUN = HERE / "runs" / "v5_mean_vs_distribution"
PROTOCOL = json.loads((HERE / "protocol_v5.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def raw():
    return json.loads((RUN / "raw.json").read_text(encoding="utf-8"))


def test_provenance_matches_frozen_protocol_and_code(raw):
    assert raw["provenance"]["protocol_sha256"] == run_v5.text_sha256(HERE / "protocol_v5.json")
    for name, sha in raw["provenance"]["code_sha256"].items():
        assert sha == run_v5.text_sha256(HERE / name), name


def test_run_covers_every_condition(raw):
    keys = {(r["rule"], r["init"], r["k"], r["dt"]) for r in raw["runs"]}
    for dt in PROTOCOL["dt_myr"]:
        for rule in PROTOCOL["rules"]:
            assert (rule, "C", 0.0, dt) in keys
            for init in ("A", "B"):
                for k in PROTOCOL["exchange_rates_per_myr"]:
                    assert (rule, init, k, dt) in keys
    assert len(keys) == len(raw["runs"]) == 2 * 3 * 7


@pytest.mark.parametrize("rule, init, k, dt", [("P3", "A", 0.01, 0.5), ("S", "A", 0.0, 0.5), ("L", "B", 0.1, 0.25)])
def test_selected_runs_reproduce_bit_identically(raw, rule, init, k, dt):
    committed = next(r["series"] for r in raw["runs"] if (r["rule"], r["init"], r["k"], r["dt"]) == (rule, init, k, dt))
    assert run_v5.simulate(PROTOCOL, rule, init, k, dt) == json.loads(json.dumps(committed))


def test_results_and_timeseries_are_current(raw):
    results = json.loads((RUN / "results.json").read_text(encoding="utf-8"))
    assert results == json.loads(json.dumps(evaluate_v5.evaluate(PROTOCOL, raw)))
    ts = json.loads((RUN / "timeseries.json").read_text(encoding="utf-8"))
    assert ts == json.loads(json.dumps(export_v5_timeseries.export(PROTOCOL, raw)))
    assert ts["status"] == "synthetic_only" and len(ts["series"]) == 21


def test_reported_key_numbers(raw):
    res = json.loads((RUN / "results.json").read_text(encoding="utf-8"))["rules"]
    assert all(c["r_max_abs"] <= 1e-12 for c in res["L"]["by_k"].values())
    assert all(c["r_signed_at_max"] > 0 for c in res["P3"]["by_k"].values())
    assert all(c["r_signed_at_max"] < 0 for c in res["S"]["by_k"].values())
    assert res["P3"]["by_k"]["0.01"]["resolution"]["A"]["pop3_mass_state"] == "numerical_failure"
    assert all(r["D2_B_vs_C_max_rel_diff"] <= 1e-12 for r in res.values())
