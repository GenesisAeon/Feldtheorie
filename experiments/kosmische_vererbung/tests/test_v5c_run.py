"""V5c run: the committed KV-V5c run is reproducible and its results are current.

Run explicitly: python -m pytest -q -p no:cacheprovider experiments/kosmische_vererbung/tests
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments.kosmische_vererbung.chem import evaluate_v5c, run_v5c

HERE = Path(__file__).resolve().parents[1] / "chem"
RUN = HERE / "runs" / "v5c_resolution"
PROTOCOL = json.loads((HERE / "protocol_v5c.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def raw():
    return json.loads((RUN / "raw.json").read_text(encoding="utf-8"))


def test_provenance_matches_frozen_protocol_and_code(raw):
    assert raw["provenance"]["protocol_sha256"] == run_v5c.text_sha256(HERE / "protocol_v5c.json")
    for name, sha in raw["provenance"]["code_sha256"].items():
        assert sha == run_v5c.text_sha256(HERE / name), name


def test_run_is_complete(raw):
    assert len(raw["runs"]) == 2 * 4 * 3 * 2 * 3
    assert all(r["state"] == "completed" for r in raw["runs"])


@pytest.mark.parametrize("scheme, rule, init, k, dt", [("event", "P3", "A", 0.01, 0.5), ("event", "P3", "B", 0.1, 0.5), ("grid", "S", "A", 0.01, 0.5)])
def test_selected_runs_reproduce_bit_identically(raw, scheme, rule, init, k, dt):
    committed = next(r["series"] for r in raw["runs"] if (r["scheme"], r["rule"], r["init"], r["k"], r["dt"]) == (scheme, rule, init, k, dt))
    assert run_v5c.simulate(PROTOCOL, rule, init, k, dt, scheme) == json.loads(json.dumps(committed))


def test_results_are_current_and_key_numbers_hold(raw):
    res = json.loads((RUN / "results.json").read_text(encoding="utf-8"))
    assert res == json.loads(json.dumps(evaluate_v5c.evaluate(PROTOCOL, raw)))
    q = res["quantities"]
    hv = PROTOCOL["hand_values"]["pop3_mass_event_msun"]
    for k in ("0.01", "0.1"):
        assert q[f"P3|k={k}|pop3"]["event"]["state"] == "evaluated"
        assert q[f"P3|k={k}|pop3"]["grid"]["state"] == "numerical_failure"
        for v in q[f"P3|k={k}|pop3"]["event"]["by_dt"].values():
            assert v == pytest.approx(hv[f"k={k}"], rel=1e-9)
    assert q["P3|k=0.1|r_final"]["event"]["state"] == "numerical_failure"
    assert all(q[f"S|k={k}|{w}"][s]["state"] == "evaluated" for k in ("0.0", "0.01", "0.1") for w in ("r_max_signed", "r_final") for s in ("grid", "event"))
    assert res["max_budget_rel_error"] < PROTOCOL["balance_tolerance_rel"]
