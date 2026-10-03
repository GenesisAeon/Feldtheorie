"""M9c tests: integrity check of the frozen file, the primary and decoder
checks with targeted negative controls (on DEVELOPMENT combinations only),
exclusive result writing and the separate random streams of mode m9."""
import copy
import json
import shutil
from pathlib import Path

import numpy as np
import pytest

from experiments.mandala_memory import lab, m9_evaluate as ev, m9_freeze, predict
from experiments.mandala_memory.data import stream
from experiments.mandala_memory.m9_registry import BENCHMARK, DEV_COMBOS
from experiments.mandala_memory.tests._paths import scratch

TMP = scratch("m9")
STRONG = DEV_COMBOS[14]                    # a = 3, ell = 1, gamma = 0.95, c = 0: strongest nonlinearity of the dev set
RULES = m9_freeze.RULES


def _ker(c):
    return lab.compute(ev.knobs_of(c, 0.75))


def test_frozen_file_integrity_and_tamper_detection():
    fr = ev.load_frozen()
    assert len(fr["held_out"]) == 24 and fr["kernel_evaluated_before_freeze"] is False
    TMP.mkdir(parents=True, exist_ok=True)
    bad = TMP / "tampered.json"
    data = json.loads(m9_freeze.FROZEN.read_text(encoding="utf-8"))
    data["held_out"][0]["prediction"]["D_interval"] = [0, 64]
    bad.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    with pytest.raises(ev.IntegrityError):
        ev.load_frozen(bad)
    crlf = TMP / "crlf.json"                         # a CRLF checkout of the untouched file still passes
    crlf.write_bytes(m9_freeze.FROZEN.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    assert ev.load_frozen(crlf)["held_out"][0]["id"] == "h00"


def test_primary_check_passes_and_detects_a_too_narrow_band():
    pred = predict.predict(STRONG)
    ker = _ker(STRONG)
    assert ev.check_primary(pred, ker)["passed"]
    narrow = copy.deepcopy(pred)
    narrow["error_bound_E"] = [0.0] * len(pred["error_bound_E"])     # pretend the linearisation were exact
    res = ev.check_primary(narrow, ker)
    assert not res["band_ok"] and res["n_violations"] > 0 and not res["passed"]


def test_primary_check_detects_a_wrong_duration():
    pred = predict.predict(BENCHMARK)
    ker = _ker(BENCHMARK)
    wrong = copy.deepcopy(pred)
    wrong["D_interval"] = [7, 7]
    res = ev.check_primary(wrong, ker)
    assert res["band_ok"] and not res["D_ok"] and not res["passed"] and res["D_kernel"] == 6


def test_decoder_check_and_its_negative_control():
    pred = predict.predict(BENCHMARK)
    ker = _ker(BENCHMARK)
    ok = ev.decoder_check(pred, ker, 9999, 6, RULES)
    assert ok["passed"] and abs(ok["balanced_accuracy"] - ker["curve"]["bayes"][6]) < 0.03
    assert ev.decoder_check(pred, ker, 9999, 6, RULES) == ok           # deterministic
    wrong = copy.deepcopy(pred)
    wrong["bayes_band_lo"][6] = wrong["bayes_band_hi"][6] = 0.97         # a false prediction must fail
    assert not ev.decoder_check(wrong, ker, 9999, 6, RULES)["passed"]


def test_m9_streams_are_separate_from_all_earlier_modes():
    keys = {mode: stream(mode, 9000, "observation", "test", 6, 12)[1] for mode in ("smoke", "research", "explore", "m9", "test")}
    assert len(set(keys.values())) == 5
    a = stream("m9", 9000, "observation", "test", 6, 12)[0].normal(size=4)
    b = stream("research", 9000, "observation", "test", 6, 12)[0].normal(size=4)
    assert not np.array_equal(a, b)


def test_write_result_is_exclusive_and_refuses_c():
    out = TMP / "results"
    shutil.rmtree(out, ignore_errors=True)
    res = {"schema": ev.SCHEMA, "x": 1}
    p = ev.write_result(res, out)
    assert p.is_file()
    with pytest.raises(FileExistsError):
        ev.write_result(res, out)
    with pytest.raises(RuntimeError):
        ev.write_result(res, Path("C:/mandala-m9-should-not-exist"))
