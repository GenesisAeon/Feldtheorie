"""M10 tests with the kernel (need SCF): states, A1/A2 with negative controls,
K0 against the analytic M9 value, level-D episodes with leak and split negative
controls, and a small end-to-end development run. Development conditions only."""
import dataclasses

import numpy as np
import pytest

from experiments.mandala_memory import m10_bayes as mb
from experiments.mandala_memory import m10_decoders as md
from experiments.mandala_memory import m10_run
from experiments.mandala_memory import m10_task as mt
from experiments.mandala_memory.core import MemoryLabError

PROTO = mt.load_protocol()
DEV = PROTO["development"]["conditions"]
PATS = mt.patterns()


def _perm(net):
    return mt.swap_permutation(12, PROTO["networks"][net]["M"])


@pytest.mark.parametrize("net,cond,expected", [("modular", "Fdev", True), ("uniform", "Fdev", True),
                                               ("uniform", "Ndev", True), ("modular", "Ndev", False)])
@pytest.mark.parametrize("nl", ["tanh", "identity"])
def test_a1_state_identity_and_negative_control(net, cond, expected, nl):
    spec = mt.network(PROTO, net, nl, DEV[cond])
    assert mt.condition_is_p_fixed(_perm(net), DEV[cond]) is expected
    res = mt.check_a1(spec, _perm(net), 4, PATS, PROTO["diagnostics"]["A1"]["tol_rel"])
    assert res["holds"] is expected


@pytest.mark.parametrize("net,cond,expected", [("modular", "Fdev", True), ("uniform", "Ndev", True), ("modular", "Ndev", False)])
def test_a2_structural_and_negative_control(net, cond, expected):
    spec = mt.network(PROTO, net, "identity", DEV[cond])
    z = mt.readout_states(spec, 4, PATS)
    assert mt.check_a2_structural(z, PATS, _perm(net), PROTO["diagnostics"]["A2_structural"]["tol"])["holds"] is expected


def test_k0_states_and_analytic_baseline():
    spec = mt.network(PROTO, "modular", "tanh", None)
    z = mt.readout_states(spec, 4, PATS)
    assert all(np.array_equal(z[s, i], z[s, 0]) for s in (0, 1) for i in range(27))
    assert mb.k0_preserve_analytic(z[:, 0], 0.02) == pytest.approx(0.9352, abs=5e-4)     # M8/M9 value at d = 4
    zu = mt.readout_states(mt.network(PROTO, "uniform", "tanh", None), 4, PATS)
    assert mb.k0_preserve_analytic(zu[:, 0], 0.02) == pytest.approx(0.670, abs=2e-3)       # E2 (predict.py)


def test_level_d_episodes_pairing_leak_and_split_controls():
    tr = md.make_episodes("m10", 901, "decoder_train", 4, 300, PATS, 12, 0.02)
    te = md.make_episodes("m10", 901, "test", 4, 300, PATS, 12, 0.02)
    assert md.check_class_independence(tr, 27)["identical_pattern_counts"]
    assert md.check_split(tr, te) == {"ids_disjoint": True, "streams_disjoint": True}
    # negative control 1: class-dependent distraction -> leak check fails
    leaky = dataclasses.replace(tr, pattern_index=np.where(tr.target == 1, 0, tr.pattern_index))
    assert not md.check_class_independence(leaky, 27)["identical_pattern_counts"]
    # negative control 2: the test split drawn from the training stream -> split check fails
    same = md.make_episodes("m10", 901, "decoder_train", 4, 300, PATS, 12, 0.02)
    with pytest.raises(Exception):
        md.check_split(tr, dataclasses.replace(same, ids=tuple(i + ":x" for i in same.ids)))
    # same streams for every network/condition (pairing), different streams for another seed
    assert np.array_equal(tr.noise, md.make_episodes("m10", 901, "decoder_train", 4, 300, PATS, 12, 0.02).noise)
    assert not np.array_equal(tr.noise, md.make_episodes("m10", 902, "decoder_train", 4, 300, PATS, 12, 0.02).noise)


def test_update_task_excludes_episodes_without_pulse():
    z = mt.readout_states(mt.network(PROTO, "uniform", "tanh", DEV["Fdev"]), 4, PATS)
    tr = md.make_episodes("m10", 902, "decoder_train", 4, 400, PATS, 12, 0.02)
    te = md.make_episodes("m10", 902, "test", 4, 400, PATS, 12, 0.02)
    r = md.evaluate_level_d(z, tr, te, "update")
    assert r["n_excluded_test"] == int((te.last == 0).sum()) > 0 and r["n_test"] + r["n_excluded_test"] == 800


def test_small_development_run_end_to_end():
    from experiments.mandala_memory import m10_evaluate

    res = m10_run.run("dev", None, delays=[4], n_mc=5000, seeds=[901], write=False)
    assert res["status"] == "complete" and not res["failures"]
    assert all(r["A1_as_expected"] for r in res["diagnostics"])
    k0 = [r for r in res["level_B"] if r["condition"] == "K0"]
    assert all(r["update"] is None and r["preserve"]["n"] == 0 for r in k0)
    ev = m10_evaluate.evaluate(res)
    assert not ev["release"]["released"] and ev["confirmatory_label"].startswith("DESCRIPTIVE ONLY")
    assert ev["deterministic_diagnostics"] == {"A1_all_as_expected": True, "A2_structural_all_hold": True}
    assert ev["numeric_diagnostics"]["n_A3_checks"] == 4          # 2 networks x 2 dev conditions x 1 delay
    assert {r["decoder"] for r in ev["level_D"]} == {"nearest_mean", "lda_ledoit_wolf"}
