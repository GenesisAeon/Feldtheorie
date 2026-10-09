"""LR5-A1 (review LANTERN_LR4_NACHREVIEW_25ba293): a permutation p-value tests DEPENDENCE on the test
targets, not G > 0. The 12 named control cells deliver observed G and p together; Holm runs over all 12;
positive spurious success and target dependence are separate alarms. Plus the permuted-target control."""
from __future__ import annotations

import json
import math

import numpy as np
import pytest

from experiments.lantern_reconstruction import contexts, metrics, runner, streams
from experiments.lantern_reconstruction import registry_adapter as ra

SID = streams.defaults()["development_study_id"]
NAMES = metrics.control_alarm_cells()


def _cells(**override):
    base = {n: {"G": -0.01, "p": 1.0} for n in NAMES}
    base.update(override)
    return base


def _review_case():
    u = np.tile(np.linspace(-.1, .1, 10)[:, None], (1, 4))
    return .75 + .1 * u, u


def test_twelve_named_cells_in_protocol_order():
    assert len(NAMES) == 12 and NAMES[0] == "reset|A|1.0" and NAMES[-1] == "permuted_targets|B|5.0"
    assert NAMES == tuple(f"{c}|{t}|{tau}" for c in ("reset", "zero_impulse", "permuted_targets") for t in ("A", "B") for tau in (1.0, 5.0))


def test_review_counterexample_negative_G_small_p_is_dependence_not_positive_success():
    """Review: predictions .75 + .1u, 2 contexts, 9999 permutations, seed 123: G = -1.6851777777777779,
    p = 1e-4, Holm 0.0012 with eleven p = 1. The old p-only alarm fired; it is not a positive spurious success."""
    p_, u = _review_case()
    r = metrics.permutation_gain_test({0: (p_, u), 1: (p_, u)}, np.random.default_rng(123), 9999)
    assert r["observed_mean_G"] == -1.6851777777777779 and r["p"] == 0.0001
    out = metrics.control_alarms(_cells(**{NAMES[0]: {"G": r["observed_mean_G"], "p": r["p"]}}))
    cell = out["cells"][NAMES[0]]
    assert math.isclose(cell["holm_p"], 0.0012) and cell["target_dependence"] and not cell["positive_spurious_success"]
    assert out["target_dependence_alarm"] and not out["positive_spurious_success_alarm"]


def test_positive_G_small_p_raises_both_alarms():
    out = metrics.control_alarms(_cells(**{NAMES[5]: {"G": 0.3, "p": 1e-4}}))
    assert out["positive_spurious_success_alarm"] and out["target_dependence_alarm"]
    assert out["cells"][NAMES[5]]["positive_spurious_success"]


def test_positive_G_not_significant_raises_no_alarm():
    out = metrics.control_alarms(_cells(**{NAMES[5]: {"G": 0.3, "p": 0.2}}))
    assert not out["positive_spurious_success_alarm"] and not out["target_dependence_alarm"]


def test_holm_always_over_all_twelve_never_over_the_positive_subset():
    """p = .004 in the only positive cell: Holm over that subset alone would give .004 <= .01 (alarm);
    over the declared family of 12 it is .048 (no alarm)."""
    out = metrics.control_alarms(_cells(**{NAMES[3]: {"G": 0.2, "p": 0.004}}))
    assert out["holm_family_size"] == 12 and math.isclose(out["cells"][NAMES[3]]["holm_p"], 0.048)
    assert not out["positive_spurious_success_alarm"]


@pytest.mark.parametrize("bad", [
    {n: {"G": 0.0, "p": 1.0} for n in NAMES[:11]},                                         # missing
    {**{n: {"G": 0.0, "p": 1.0} for n in NAMES}, "extra|A|1.0": {"G": 0.0, "p": 1.0}},     # extra
    {**{n: {"G": 0.0, "p": 1.0} for n in NAMES[1:]}, "reset|A|1": {"G": 0.0, "p": 1.0}},   # misnamed (1 vs 1.0)
    {**{n: {"G": 0.0, "p": 1.0} for n in NAMES[1:]}, "Reset|A|1.0": {"G": 0.0, "p": 1.0}},
])
def test_missing_extra_or_misnamed_cells_are_refused(bad):
    with pytest.raises(ValueError, match="exactly the 12 named cells"):
        metrics.control_alarms(bad)


@pytest.mark.parametrize("cell", [{"p": 0.5}, {"G": 0.1}, {"G": float("nan"), "p": .5}, {"G": .1, "p": 1.5},
                                  {"G": True, "p": .5}, {"G": .1, "p": .5, "holm_p": .1}])
def test_each_cell_needs_finite_G_and_valid_p_together(cell):
    with pytest.raises(ValueError):
        metrics.control_alarms(_cells(**{NAMES[0]: cell}))


def test_release_rule_is_documented_as_endorsed_not_yet_frozen():
    rule = metrics.control_alarms(_cells())["release_rule"]
    assert rule["status"].startswith("ENDORSED") and "binding with the research freeze" in rule["status"]
    assert "negative G does not make a target dependence harmless" in rule["proposal"]
    assert "no automatic override" in rule["investigation"] and "does not prove independence" in rule["interpretation"]


def test_alarm_inputs_end_to_end_with_streams():
    """Adapter from per-context predictions to the 12 cells: the review case in one cell, independent
    predictions elsewhere -> dependence alarm only; one stream per cell, reproducible."""
    rng = np.random.default_rng(5)
    rev = _review_case()
    per = {}
    for cid in (0, 1):
        per[cid] = {}
        for n in NAMES:
            u = rng.uniform(-1, 1, (10, 4))
            per[cid][n] = rev if n == NAMES[2] else (np.clip(rng.normal(0, .2, (10, 4)), -1, 1), u)
    a1 = runner.alarm_inputs(per, SID)
    assert a1 == runner.alarm_inputs(per, SID)                                    # reproducible
    with pytest.raises(ValueError, match="9999"):
        runner.alarm_inputs(per, SID, n_perm=999)          # min Holm p 12/1000 = .012 > .01: could never fire
    assert a1[NAMES[2]]["G"] == -1.6851777777777779 and a1[NAMES[2]]["b"] == 0
    out = metrics.control_alarms(a1)
    assert out["target_dependence_alarm"] and not out["positive_spurious_success_alarm"]
    assert [n for n, c in out["cells"].items() if c["target_dependence"]] == [NAMES[2]]


def test_permuted_training_targets_control():
    ctx = contexts.make_context(SID, 0)
    u = np.arange(40, dtype=float).reshape(10, 4)
    p1 = runner.training_targets(ctx, u, "permuted_targets", "A", 2)
    assert not np.array_equal(p1, u) and sorted(map(tuple, p1)) == sorted(map(tuple, u))          # a row permutation
    assert np.array_equal(p1, runner.training_targets(ctx, u, "permuted_targets", "A", 2))       # deterministic
    assert not np.array_equal(p1, runner.training_targets(ctx, u, "permuted_targets", "B", 2))   # own stream per cell
    assert runner.training_targets(ctx, u, "none", "A", 2) is u
    perm = streams.generator(SID, 0, "train", "decoder", 0, 2, 0, 2).permutation(10)
    assert np.array_equal(p1, u[perm])


def test_permuted_targets_run_destroys_the_trained_information():
    s = ra.load_verified_snapshot()
    ctx = contexts.make_context(SID, 0)
    kw = dict(sizes={"train": 120, "val": 40, "test": 120}, conditions=("uncoupled",), tasks=("A",), proposals=100)
    real = runner.run_context(ctx, np.array(s.C), float(s.structure["g"]), **kw)
    perm = runner.run_context(ctx, np.array(s.C), float(s.structure["g"]), control="permuted_targets", keep_predictions=True, **kw)
    assert real["cells"][("uncoupled", "A")]["G"][0.0] > 0.5 and perm["cells"][("uncoupled", "A")]["G"][0.0] < 0.1
    assert len(perm["predictions"]) == 7


@pytest.mark.parametrize("stem", ["protocol/control_alarms", "lr5/lr5_budget", "lr5/lr5_mutation_campaign", "lr5/lr5_status"])
def test_lr5_yaml_twins(stem):
    import yaml
    p = streams.HERE / stem
    assert yaml.safe_load(p.with_suffix(".yaml").read_text(encoding="utf-8")) == json.loads(p.with_suffix(".json").read_text(encoding="utf-8"))


def test_ci_workflow_runs_every_lab_test_file_exactly_once_without_masking():
    """Review of b9c405b (F2): test_lr5_review.py was missing from the workflow. The explicit file lists of
    all jobs together must equal the test files of the lab -- a new test file cannot be forgotten again."""
    import re
    import yaml
    wf_path = streams.HERE.parents[1] / ".github" / "workflows" / "lantern-reconstruction.yml"
    wf = yaml.safe_load(wf_path.read_text(encoding="utf-8"))
    selected = []
    for job in wf["jobs"].values():
        assert "continue-on-error" not in job and job["strategy"]["matrix"]["python-version"] == ["3.11", "3.12"]
        for step in job["steps"]:
            run = step.get("run", "")
            assert "continue-on-error" not in step and "||" not in run and "exit 0" not in run
            selected += re.findall(r"experiments/lantern_reconstruction/tests/(test_\w+\.py)", run)
    present = sorted(p.name for p in (streams.HERE / "tests").glob("test_*.py"))
    assert sorted(selected) == present and len(selected) == len(set(selected)) and len(present) == 13


def test_mutation_campaign_record_is_consistent():
    """Every applicable plan mutant (1-18 without 2, 6, 12) was executed and killed; 2/6/12 carry a reason;
    survivors are only the documented equivalent ones."""
    d = json.loads((streams.HERE / "lr5" / "lr5_mutation_campaign.json").read_text(encoding="utf-8"))
    ids = {m["id"].split("-")[0].rstrip("ab") for m in d["plan_mutants"]}
    assert ids | set(d["not_applicable"]) == {str(i) for i in range(1, 19)}
    assert all(m["result"] == "killed" for m in d["plan_mutants"]) and d["plan_mutant_2_detection_test"]["passed"]
    surv = [m["id"] for m in d["plan_mutants"] + d["lr5_mutants"] + d.get("review_lr5_mutants", []) + d.get("followup_b9c405b_mutants", [])
            + d.get("nachreview_9b52d95_mutants", []) + d.get("lr6_mutants", []) if m["result"] != "killed"]
    assert surv == sorted(d["equivalent"]) and d["summary"]["survived"] == []


def test_budget_record_separates_measurement_and_extrapolation():
    d = json.loads((streams.HERE / "lr5" / "lr5_budget.json").read_text(encoding="utf-8"))
    assert "EXTRAPOLATION" in d["status"] and d["measured"]["peak_working_set_bytes"] and d["measured"]["peak_working_set_bytes"] > 0
    ex, b = d["extrapolated_full_study"], d["budget_draft"]
    assert d["within_budget"] == {"production_training": ex["production_training_s"] <= b["production_training_s"],
                                  "evaluation": ex["evaluation_s"] <= b["evaluation_s"],
                                  "ram_measured_peak": d["measured"]["peak_working_set_bytes"] <= b["ram_bytes"],
                                  "artifacts": ex["artifacts_bytes"] <= b["artifacts_bytes"]}
