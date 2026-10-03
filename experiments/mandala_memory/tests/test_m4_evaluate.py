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


ORIGINAL_RESEARCH = Path(r"D:/mandala/mandala-memory-results/research/research-e19650a0a0.json")


@pytest.mark.skipif(not ORIGINAL_RESEARCH.exists(), reason="original research result not present")
def test_review_r2_original_full_round_released_and_numerically_unchanged():
    res = json.loads(ORIGINAL_RESEARCH.read_text(encoding="utf-8"))
    ev = evaluate(res)
    assert ev["inference_release"]["released"] is True and ev["inference_release"]["reasons"] == []
    assert ev["primary"]["mean_paired_difference"] == -0.0009999999999999898
    assert ev["primary"]["bootstrap_95"]["low"] == -0.0025000000000000022
    assert ev["primary"]["bootstrap_95"]["high"] == 0.0005000000000000227


@pytest.mark.skipif(not ORIGINAL_RESEARCH.exists(), reason="original research result not present")
@pytest.mark.parametrize("case", ["two_seeds", "duplicates", "aborted", "failed", "renamed_smoke", "config_changed"])
def test_review_r2_incomplete_protocol_not_released(case):
    res = json.loads(ORIGINAL_RESEARCH.read_text(encoding="utf-8"))
    if case == "two_seeds":
        res["runs"] = res["runs"][:2]
        res["seeds"] = res["seeds"][:2]
        expected = "executed_seeds_differ_from_protocol"
    elif case == "duplicates":
        res["runs"] = res["runs"][:19] + [res["runs"][0]]
        expected = "duplicate_seeds"
    elif case == "aborted":
        res["status"] = "aborted"
        res["runs"] = []
        expected = "status_aborted"
    elif case == "failed":
        res["status"] = "complete_with_failures"
        res["failed_seeds"] = [{"seed": res["seeds"][-1], "error": "x"}]
        res["runs"] = res["runs"][:-1]
        expected = "failed_seeds_present"
    elif case == "renamed_smoke":
        # a smoke result relabelled as research must not become inferential
        res["config"] = json.loads(json.dumps(res["config"]))
        res["config"]["research"]["seeds"] = res["config"]["smoke"]["seeds"]
        res["runs"] = res["runs"][:3]
        res["seeds"] = res["config"]["smoke"]["seeds"]
        expected = "configuration_differs_from_frozen_protocol"
    else:
        res["config"] = json.loads(json.dumps(res["config"]))
        res["config"]["observation"]["sigma"] = 0.01
        expected = "configuration_differs_from_frozen_protocol"
    ev = evaluate(res)
    assert ev["inference_release"]["released"] is False and ev["inferential_claims"] is False
    assert expected in ev["inference_release"]["reasons"], ev["inference_release"]["reasons"]
    assert ev["reading"].startswith("descriptive only")


def test_exact_sign_flip_equals_scf_enumeration():
    from fractions import Fraction as F
    from scoped_correspondence.validation.modular_networks.decoders import sign_flip_test
    from experiments.mandala_memory.evaluate import sign_flip_p_exact

    rng = np.random.default_rng(3)
    for n in range(1, 13):
        diffs = [F(int(k), 200) for k in rng.integers(-6, 7, size=n)]
        assert sign_flip_p_exact(diffs) == sign_flip_test(diffs), diffs
    assert sign_flip_p_exact([F(1)] * 5) == F(1, 16)


@pytest.mark.skipif(not ORIGINAL_RESEARCH.exists(), reason="original research result not present")
def test_original_sign_flip_p_unchanged():
    res = json.loads(ORIGINAL_RESEARCH.read_text(encoding="utf-8"))
    assert evaluate(res)["primary"]["sign_flip_p_two_sided"] == "11/32", "same value as the M4 report"


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
