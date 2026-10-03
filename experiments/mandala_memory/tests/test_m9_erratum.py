"""Regression tests for docs/M9_ERRATUM_1.md (review astra-m8-m9-review, R3 and
R4). They use the review's counterexamples verbatim. The frozen derivation
itself stays unchanged (guarded by test_m9_freeze)."""
import json

import numpy as np
import pytest

from experiments.mandala_memory import lab, predict
from experiments.mandala_memory.m9_evaluate import knobs_of

R3 = {"N": 12, "M": 3, "c": 0.8, "gamma": 0.8, "ell": 0.5, "amplitude": 0.6, "sigma": 0.02, "inputs": [0, 4],
      "readout": "module_means", "readout_node": 0, "nonlinearity": "tanh"}
R4 = {"N": 12, "M": 3, "c": 0.25, "gamma": 0.8, "ell": 0.5, "amplitude": 0.6, "sigma": 0.01, "inputs": [0, 4],
      "readout": "node", "readout_node": 1, "nonlinearity": "tanh"}


def _module_contrast(p):
    k = lab.compute(knobs_of(p, 0.75))
    dx = np.array(k["trajectory"]["A"]) - np.array(k["trajectory"]["B"])
    return [float(dx[t][0:4].mean() - dx[t][4:8].mean()) for t in range(1, 6)]


def test_r3_negative_coupling_eigenvalue_without_sign_change():
    m = predict.modes(R3)
    assert m["lam_D"] == pytest.approx(-0.16, abs=1e-12) and m["mu_D"] == pytest.approx(0.42, abs=1e-12)
    contrast = _module_contrast(R3)
    assert contrast == pytest.approx([0.1342624, 0.0563928, 0.0236859, 0.0099484, 0.0041785], abs=5e-8)
    assert all(c > 0 for c in contrast)                    # lambda_D < 0, but no alternation since mu_D > 0


def test_r3_positive_control_sign_alternates_exactly_when_mu_D_negative():
    p = {**R3, "c": 1.0, "gamma": 0.95, "ell": 1.0}
    m = predict.modes(p)
    assert m["mu_D"] == pytest.approx(-0.475, abs=1e-12)
    c = _module_contrast(p)
    assert all(a * b < 0 for a, b in zip(c, c[1:]))


def test_r4_below_threshold_at_d0_is_not_no_memory():
    k = lab.compute(knobs_of(R4, 0.75))
    b = k["curve"]["bayes"]
    assert b[0] == 0.5 and b[1] == pytest.approx(0.879704, abs=1e-6) and b[2] == pytest.approx(0.911444, abs=1e-6)
    md = k["memory_duration"]
    assert md["last_delay_at_or_above"] == 5 and md["first_passage"] is None and md["monotone_non_increasing"] is False
    assert "already below p* at d = 0" not in md["definition"]
    assert "every" in md["definition"]
    pr = predict.predict(R4)
    assert pr["D_linear"] == 5 and pr["D_interval"] == [5, 5]


def test_r4_frozen_dash_predictions_stay_below_at_every_delay():
    """The ten '-' predictions of M9 mean: below p* at EVERY d = 0..64 (not only at d = 0)."""
    from experiments.mandala_memory.m9_freeze import FROZEN
    fr = json.loads(FROZEN.read_text(encoding="utf-8"))
    dashes = [it["prediction"] for it in fr["held_out"] if it["prediction"]["D_interval"] == [None, None]]
    assert len(dashes) == 10
    for pred in dashes:
        assert max(pred["bayes_band_hi"]) < 0.75
