"""M4 tests: paired primary contrast, whole-seed bootstrap, vocabulary, honesty fields."""
import json
from pathlib import Path

import numpy as np
import pytest

from experiments.mandala_memory.evaluate import bootstrap_mean_ci, evaluate, paired_differences
from experiments.mandala_memory.runner import run_experiment

CFG = json.loads((Path(__file__).resolve().parents[1] / "protocol" / "startkonfiguration.json").read_text(encoding="utf-8"))
OUT = Path(r"D:/mandala/.tmp/mandala-memory/test-results/m4")


@pytest.fixture(scope="module")
def small_result():
    cfg = json.loads(json.dumps(CFG))
    cfg["smoke"].update({"seeds": [21, 22, 23], "decoder_train_per_class_per_delay": 8, "test_per_class_per_delay": 8})
    cfg["episode"]["delay_steps"] = [0, 8]
    return run_experiment(cfg, "smoke", OUT)


def test_bootstrap_deterministic_and_brackets_mean():
    v = [0.01, -0.02, 0.0, 0.03, -0.01]
    a = bootstrap_mean_ci(v, 2000, 7)
    b = bootstrap_mean_ci(v, 2000, 7)
    assert a == b and a["low"] <= np.mean(v) <= a["high"] and a["resampling_unit"] == "whole seed"
    assert bootstrap_mean_ci([0.1], 2000, 7)["low"] is None


def test_primary_pairs_values_of_the_same_seed():
    """Mutation-check finding: the small fixture has all-zero differences, so a
    wrong pairing order was invisible. Here per-seed values differ."""
    runs = []
    for seed, (a, f) in enumerate([(0.60, 0.58), (0.70, 0.71), (0.80, 0.75)]):
        runs.append({"seed": seed, "adaptation": {"weight_change_fro": 0.0, "weight_change_max": 0.0},
                     "delays": {"8": {c: {"balanced_accuracy": v} for c, v in
                                      (("adapted", a), ("frozen", f), ("adapted_with_frozen_decoder", a))}}})
    for c in ("uncoupled_leak", "linear", "uniform_M1", "renamed_M3_c8_11", "reset_control", "sum_observation_frozen",
              "permutation_frozen_decoder", "permutation_refit_decoder"):
        for r in runs:
            r["delays"]["8"][c] = {"balanced_accuracy": 0.5}
    res = {"config": CFG, "mode": "research", "run_id": "synthetic", "config_sha256": "x", "status": "complete",
           "failed_seeds": [], "runs": runs}
    p = evaluate(res)["primary"]
    assert p["per_seed_paired_differences"] == pytest.approx([0.02, -0.01, 0.05], abs=1e-12)
    assert p["mean_paired_difference"] == pytest.approx(0.02, abs=1e-12)


def test_primary_is_paired_and_honest(small_result):
    ev = evaluate(small_result)
    p = ev["primary"]
    assert p["delay"] == 8 and p["n_seeds"] == 3
    expected = [r["delays"]["8"]["adapted"]["balanced_accuracy"] - r["delays"]["8"]["frozen"]["balanced_accuracy"]
                for r in small_result["runs"]]
    assert p["per_seed_paired_differences"] == expected == paired_differences(small_result, "adapted", "frozen", "8")
    assert "synthetic" in p["uncertainty_kind"] and "exchangeability" in p["sign_flip_assumption"]
    assert ev["evidence_kind"] == "numerical_sample" and ev["empirical_status"] == "synthetic_only"
    assert ev["inferential_claims"] is False, "smoke results are descriptive only"
    assert "no winner" in ev["not_claimed"]
    json.dumps(ev, allow_nan=False)
