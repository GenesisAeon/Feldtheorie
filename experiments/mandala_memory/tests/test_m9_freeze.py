"""M9b tests: the held-out draw, the seen check, the exclusive freeze and the
integrity of the committed frozen predictions. No kernel computation on
held-out combinations happens here."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from experiments.mandala_memory import m9_freeze, m9_registry as reg, predict

TMP = Path(r"D:/mandala/.tmp/mandala-memory/test-results/m9")


def test_draw_is_deterministic_balanced_and_in_family():
    a, b = m9_freeze.draw_held_out(), m9_freeze.draw_held_out()
    assert a == b and len(a) == 24
    for r in reg.HELD_OUT_READOUTS:
        assert sum(h["readout"] == r for h in a) == 6
    for h in a:
        predict.check_family(h)
        assert h["nonlinearity"] == "tanh"
        for k in reg.CONTINUOUS:
            if not (k == "c" and h["M"] == 1):
                assert h[k] in reg.HELD_OUT_GRID[k]
    same = [h for h in a if predict.modes(h)["same_module"]]
    assert 6 <= len(same) <= 18
    assert len({json.dumps(h, sort_keys=True) for h in a}) == 24


def test_grid_is_disjoint_from_everything_seen_so_far():
    held = m9_freeze.draw_held_out()
    info = m9_freeze.check_unseen(held, [dict(c) for c in reg.DEV_COMBOS])
    assert info["n_seen"] == len(reg.DEV_COMBOS)


def test_seen_check_rejects_overlaps():
    held = m9_freeze.draw_held_out()
    with pytest.raises(RuntimeError):                         # a held-out combination itself was seen
        m9_freeze.check_unseen(held, list(reg.DEV_COMBOS) + [held[3]])
    with pytest.raises(RuntimeError):                         # a grid value was used in the lab
        m9_freeze.check_unseen(held, list(reg.DEV_COMBOS) + [{**reg.BENCHMARK, "c": 0.35}])


def test_lab_entries_of_the_explore_protocol_count_as_seen(tmp_path):
    proto = tmp_path / "protocol.jsonl"
    lab_knobs = {**reg.BENCHMARK, "gamma": 0.7, "clear": "none", "ablation": {"edges": [], "mode": "budget_loss"}, "p_star": 0.75}
    proto.write_text(json.dumps({"run_id": "lab-x", "kind": "lab", "knobs": lab_knobs}) + "\n"
                     + json.dumps({"run_id": "explore-y", "request": {"runs": []}}) + "\n", encoding="utf-8")
    seen = m9_freeze.seen_combinations(proto)
    assert len(seen) == len(reg.DEV_COMBOS) + 1 and seen[-1]["gamma"] == 0.7
    with pytest.raises(RuntimeError):
        m9_freeze.check_unseen(m9_freeze.draw_held_out(), seen)


def test_build_refuses_when_a_held_out_combination_was_tried_in_the_lab(tmp_path):
    """The freeze itself (not only the helper) must run the seen check."""
    h = m9_freeze.draw_held_out()[5]
    knobs = {**h, "c": 0.25 if h["c"] is None else h["c"], "clear": "none", "p_star": 0.75,
             "ablation": {"edges": [], "mode": "budget_loss"}}
    proto = tmp_path / "protocol.jsonl"
    proto.write_text(json.dumps({"run_id": "lab-z", "kind": "lab", "knobs": knobs}) + "\n", encoding="utf-8")
    with pytest.raises(RuntimeError):
        m9_freeze.build(proto)


def test_write_exclusive_never_overwrites():
    TMP.mkdir(parents=True, exist_ok=True)
    f = TMP / "exclusive.json"
    if f.exists():
        f.unlink()
    m9_freeze.write_exclusive(f, "a")
    with pytest.raises(FileExistsError):
        m9_freeze.write_exclusive(f, "b")
    assert f.read_text(encoding="utf-8") == "a"


def test_freeze_does_not_import_the_kernel():
    code = ("import sys, experiments.mandala_memory.m9_freeze as f; f.draw_held_out(); "
            "bad = [m for m in sys.modules if m.startswith(('experiments.mandala_memory.core', 'experiments.mandala_memory.lab', "
            "'experiments.mandala_memory.serve', 'scoped_correspondence'))]; print(bad)")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env={**os.environ}, timeout=60)
    assert out.returncode == 0 and out.stdout.strip() == "[]", out.stderr


@pytest.mark.skipif(not m9_freeze.FROZEN.exists(), reason="predictions not frozen yet")
def test_committed_frozen_predictions_are_intact():
    fr = json.loads(m9_freeze.FROZEN.read_text(encoding="utf-8"))
    assert fr["schema"] == m9_freeze.SCHEMA and fr["kernel_evaluated_before_freeze"] is False
    # neither the prediction code nor the derivation nor the registry may change after the freeze
    assert fr["predict_py_sha256"] == m9_freeze.sha256_file(m9_freeze.HERE / "predict.py")
    assert fr["derivation_sha256"] == m9_freeze.sha256_file(m9_freeze.HERE / "docs" / "M9_HERLEITUNG.md")
    assert fr["registry_sha256"] == m9_freeze.sha256_file(m9_freeze.HERE / "m9_registry.py")
    held = m9_freeze.draw_held_out()
    assert [it["prediction"]["combination"] for it in fr["held_out"]] == held
    for it in fr["held_out"]:
        again = json.loads(json.dumps(predict.predict(it["prediction"]["combination"], fr["rules"]["p_star"])))
        assert again == it["prediction"]
