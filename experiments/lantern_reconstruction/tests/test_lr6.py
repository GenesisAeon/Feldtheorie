"""LR6: a research run exists only through a VALID freeze (protocol/freeze.json bound to the candidate file and to
the code identity; every parameter from the candidate), and the release gate evaluates the study (plan 9) only
for an interpretable research run. No research run is executed here: the gate is tested up to run creation,
the evaluation on synthetic records."""
from __future__ import annotations

import json
import math

import numpy as np
import pytest

from experiments.lantern_reconstruction import artifacts, metrics, release, runs, streams

DEV = streams.defaults()["development_study_id"]


def _candidate(**over):
    c = {"schema": runs.CANDIDATE_SCHEMA, "study": {"research_study_id": 1234567890},
         "grid": {"contexts": [0, 1], "conditions": ["lantern", "uncoupled"], "tasks": ["A", "B"],
                  "sizes": {"train": 30, "val": 12, "test": 20}, "dt": 0.02, "proposals": 100,
                  "times": [0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0], "controls": ["reset", "zero_impulse", "permuted_targets"]},
         "code_identity": runs.code_identity(exclude=("protocol/freeze.json",))["identity"],
         "software": runs.software()}         # a fixture of THIS environment; the real candidate is tested separately
    c.update(over)
    return c


@pytest.fixture()
def freeze_files(tmp_path, monkeypatch):
    cand_path, freeze_path = tmp_path / "freeze_candidate.json", tmp_path / "freeze.json"
    monkeypatch.setattr(runs, "CANDIDATE_FILE", cand_path)
    monkeypatch.setattr(runs, "FREEZE_FILE", freeze_path)

    def write(cand=None, **freeze_over):
        cand = _candidate() if cand is None else cand
        cand_path.write_text(json.dumps(cand), encoding="utf-8")
        f = {"schema": runs.FREEZE_SCHEMA, "status": "frozen", "approved_by": ["Johann", "Astra"],
             "candidate_sha256": artifacts.sha256(cand_path.read_bytes()), "code_identity": cand["code_identity"]}
        f.update(freeze_over)
        freeze_path.write_text(json.dumps(f), encoding="utf-8")
        return cand
    return write


def test_no_research_run_without_a_freeze(tmp_path, monkeypatch):
    """Isolated from the checkout (review R4): the freeze path points to a file that does not exist."""
    monkeypatch.setattr(runs, "FREEZE_FILE", tmp_path / "no_freeze.json")
    with pytest.raises(ValueError, match="frozen protocol"):
        runs.create_research_run(tmp_path / "runs")
    assert not (tmp_path / "runs").exists()
    with pytest.raises(ValueError, match="kind"):
        runs.create_run(tmp_path, "research", [0, 1])


def test_valid_freeze_creates_a_research_run_with_candidate_parameters_only(freeze_files, tmp_path):
    cand = freeze_files()
    rd = runs.create_research_run(tmp_path / "runs", run_id="r")
    run = runs.load_run(rd)
    assert run["kind"] == "research" and run["grid"]["study_id"] == 1234567890 and run["grid"]["contexts"] == [0, 1]
    assert run["grid"]["sizes"] == cand["grid"]["sizes"] and run["grid"]["proposals"] == 100
    import inspect
    assert list(inspect.signature(runs.create_research_run).parameters) == ["runs_root", "run_id"]   # nothing else to pass


@pytest.mark.parametrize("defect, match", [
    ({"status": "candidate"}, "not a frozen"), ({"schema": "x"}, "not a frozen"), ({"approved_by": []}, "no approval"),
    ({"candidate_sha256": "0" * 64}, "different candidate"), ({"code_identity": "0" * 64}, "frozen code identity"),
])
def test_defective_freeze_records_are_refused(freeze_files, tmp_path, defect, match):
    freeze_files(**defect)
    with pytest.raises(ValueError, match=match):
        runs.create_research_run(tmp_path / "runs")


def test_candidate_changed_after_the_freeze_is_refused(freeze_files, tmp_path):
    freeze_files()
    c = json.loads(runs.CANDIDATE_FILE.read_text(encoding="utf-8"))
    c["grid"]["proposals"] = 101
    runs.CANDIDATE_FILE.write_text(json.dumps(c), encoding="utf-8")
    with pytest.raises(ValueError, match="different candidate"):
        runs.create_research_run(tmp_path / "runs")


def test_changed_code_after_the_freeze_is_refused(freeze_files, tmp_path, monkeypatch):
    freeze_files()
    real = runs.code_identity
    monkeypatch.setattr(runs, "code_identity", lambda exclude=(): {**real(exclude), "identity": "f" * 64})
    with pytest.raises(ValueError, match="frozen code identity"):
        runs.create_research_run(tmp_path / "runs")


@pytest.mark.parametrize("sid, match", [(DEV, "development study"), (900050, "excluded")])
def test_research_study_id_must_be_new_and_not_excluded(freeze_files, tmp_path, sid, match):
    freeze_files(_candidate(study={"research_study_id": sid}))
    with pytest.raises(ValueError, match=match):
        runs.create_research_run(tmp_path / "runs")


def test_execute_rechecks_the_freeze_before_anything_runs(freeze_files, tmp_path):
    freeze_files()
    rd = runs.create_research_run(tmp_path / "runs", run_id="r")
    runs.FREEZE_FILE.unlink()                                   # the freeze is withdrawn
    with pytest.raises(runs.ResumeRefused, match="frozen protocol"):
        runs.execute(rd, lock_root=tmp_path / "locks")
    assert runs.status(rd) is None and not (rd / "structure" / "c000.json").exists()


# --- study evaluation (plan 9) on synthetic records ---------------------------------------------------------
def _grid_records(G_of):
    grid = {"contexts": [0, 1, 2, 3, 4], "conditions": ["lantern", "uncoupled", "uniform_total", "strength_surrogate"],
            "tasks": ["A", "B"], "times": [0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0]}
    records = {}
    for cid in grid["contexts"]:
        for cond in grid["conditions"]:
            for task in grid["tasks"]:
                for k, tau in enumerate(grid["times"]):
                    name = runs.cell_dir_name({"context_id": cid, "condition": cond, "control": "none", "task": task, "time": tau, "time_index": k})
                    records[name] = {"scores": {"G": G_of(cid, cond, task)}}
    return grid, records


def test_study_evaluation_both_hypotheses_and_task_A_estimation():
    """Constant G per curve -> A equals that G exactly (K21 weights sum to 1)."""
    G = lambda cid, cond, task: {"lantern": 0.30, "strength_surrogate": 0.10}.get(cond, 0.0) + 0.01 * cid if task == "B" else \
        {"lantern": 0.40, "uncoupled": 0.90}.get(cond, 0.5) + 0.002 * cid
    grid, records = _grid_records(G)
    ev = release.study_evaluation(grid, records)
    bl = release.curve_values(grid, records, "B", "lantern")
    assert all(math.isclose(bl[c], 0.30 + 0.01 * c, rel_tol=1e-12) for c in bl)
    h = ev["task_B_hypotheses"]
    assert h["rejected"] == [True, True] and h["allowed_statement"] == release.ALLOWED_STATEMENTS[(True, True)]
    assert h["holm_adjusted"] == metrics.holm([h["H_B1"]["p"], h["H_B2"]["p"]])
    a = ev["task_A_estimation"]
    assert math.isclose(a["paired_difference"]["mean"], -0.5, abs_tol=1e-12) and a["A_lantern"]["n_contexts"] == 5
    assert "success threshold" in a["kind"] and set(ev["task_B_descriptive"]) == set(grid["conditions"])


def test_study_evaluation_only_B1_and_none():
    # surrogate close to lantern (paired difference ~0.01, varying): H-B1 yes, H-B2 (> .05) no
    G1 = lambda cid, cond, task: {"lantern": 0.30 + 0.01 * cid, "strength_surrogate": 0.29 + 0.01 * cid - 0.002 * cid ** 2}.get(cond, 0.0)
    ev1 = release.study_evaluation(*_grid_records(G1))
    assert ev1["task_B_hypotheses"]["rejected"] == [True, False]
    # identical lantern and surrogate in every context: zero SD of the difference -> descriptive, no decision
    Gd = lambda cid, cond, task: (0.30 + 0.01 * cid) if cond in ("lantern", "strength_surrogate") else 0.0
    evd = release.study_evaluation(*_grid_records(Gd))
    assert evd["task_B_hypotheses"]["rejected"] is None and "degenerate" in evd["task_B_hypotheses"]["allowed_statement"]
    assert ev1["task_B_hypotheses"]["allowed_statement"] == release.ALLOWED_STATEMENTS[(True, False)]
    G0 = lambda cid, cond, task: ({"lantern": -0.01 + 0.005 * cid, "strength_surrogate": 0.003 * cid ** 2}.get(cond, 0.0)
                                  if task == "B" else 0.5 + 0.001 * cid)
    ev0 = release.study_evaluation(*_grid_records(G0))
    assert ev0["task_B_hypotheses"]["rejected"] == [False, False]
    assert "no general impossibility proof" in ev0["task_B_hypotheses"]["allowed_statement"]


def test_hypothesis_section_only_for_an_interpretable_research_run(monkeypatch):
    """Mutation check (S7 survived first): blocked research runs and development runs are never evaluated --
    study_evaluation is not even called."""
    grid, records = _grid_records(lambda cid, cond, task: 0.3 + 0.01 * cid if cond == "lantern" else 0.01 * cid)
    calls = []
    real = release.study_evaluation
    monkeypatch.setattr(release, "study_evaluation", lambda g, r: calls.append(1) or real(g, r))
    for kind, interp in (("development", True), ("smoke", True), ("research", False)):
        h = release.hypothesis_section(kind, interp, grid, records)
        assert h["status"] == "not_evaluated" and h["reason"]
    assert calls == []
    assert "not interpreted" in release.hypothesis_section("research", False, grid, records)["reason"]
    h = release.hypothesis_section("research", True, grid, records)
    assert h["status"] == "evaluated" and "task_B_hypotheses" in h and calls == [1]


## --- control alarm v2: permuted-target cells with a refit null (decision 2026-10-09) -------------------------
from experiments.lantern_reconstruction import contexts as _contexts, observation as _observation, runner as _runner, training as _training
from experiments.lantern_reconstruction.decoders import predict as _predict


def _synthetic(seed):
    rng = np.random.default_rng(seed)
    U = {s: rng.uniform(-1, 1, (n, 4)) for s, n in (("tr", 300), ("va", 80), ("te", 300))}
    M = rng.normal(size=(4, 16))
    X = {s: U[s] @ M * 0.5 + rng.normal(0, 1, (U[s].shape[0], 16)) for s in U}   # features encode the target
    return rng, U, X


def test_refit_null_equals_the_complete_fit_procedure():
    spec = _observation.observation_spec(_contexts.make_context(DEV, 0), "B")
    _, U, X = _synthetic(3)
    null = _training.permuted_null_gains(X["tr"], U["tr"], X["va"], U["va"], X["te"], U["te"], np.random.default_rng(9), 25)
    r = np.random.default_rng(9)
    ref = []
    for _ in range(25):                                         # documented draw order: train permutation, then val
        pt, pv = r.permutation(300), r.permutation(80)
        m = _training.fit_ridge(spec, X["tr"], U["tr"][pt], X["va"], U["va"][pv])
        ref.append(metrics.scores(*metrics.episode_losses(metrics.project(_predict(m, X["te"])), U["te"]))["G"])
    assert np.max(np.abs(null - np.array(ref))) < 1e-12


@pytest.mark.parametrize("seed", [4, 9])
def test_old_null_fired_by_construction_refit_null_does_not(seed):
    """LR6 acceptance alarm, reproduced on synthetic features that encode u: a label-permuted control decoder
    (train AND val permuted) gives p <= .01 under the old fixed-prediction null, but not under the refit null."""
    spec = _observation.observation_spec(_contexts.make_context(DEV, 0), "B")
    rng, U, X = _synthetic(seed)
    m = _training.fit_ridge(spec, X["tr"], U["tr"][rng.permutation(300)], X["va"], U["va"][rng.permutation(80)])
    proj = metrics.project(_predict(m, X["te"]))
    G = metrics.scores(*metrics.episode_losses(proj, U["te"]))["G"]
    old = metrics.permutation_gain_test({0: (proj, U["te"]), 1: (proj, U["te"])}, np.random.default_rng(100 + seed), 999)["p"]
    null = _training.permuted_null_gains(X["tr"], U["tr"], X["va"], U["va"], X["te"], U["te"], np.random.default_rng(200 + seed), 999)
    assert old <= 0.01 and (1 + np.sum(null >= G)) / 1000 > 0.01


def test_refit_null_keeps_its_power_against_a_real_leak():
    """A 'control' that in truth learned from the real targets is caught by the refit null (G > 0, p = 1/(B+1))."""
    spec = _observation.observation_spec(_contexts.make_context(DEV, 0), "B")
    _, U, X = _synthetic(0)
    m = _training.fit_ridge(spec, X["tr"], U["tr"], X["va"], U["va"])
    G = metrics.scores(*metrics.episode_losses(metrics.project(_predict(m, X["te"])), U["te"]))["G"]
    null = _training.permuted_null_gains(X["tr"], U["tr"], X["va"], U["va"], X["te"], U["te"], np.random.default_rng(1), 999)
    assert G > 0.3 and np.sum(null >= G) == 0


def test_validation_targets_permuted_only_for_the_permuted_control():
    ctx = _contexts.make_context(DEV, 0)
    u = np.arange(40, dtype=float).reshape(10, 4)
    pv = _runner.validation_targets(ctx, u, "permuted_targets", "A", 2)
    assert sorted(map(tuple, pv)) == sorted(map(tuple, u)) and not np.array_equal(pv, u)
    assert np.array_equal(pv, u[streams.generator(DEV, 0, "val", "decoder", 0, 3, 0, 2).permutation(10)])
    assert not np.array_equal(pv, _runner.training_targets(ctx, u, "permuted_targets", "A", 2))   # its own stream
    for control in ("none", "reset", "zero_impulse"):
        assert _runner.validation_targets(ctx, u, control, "A", 2) is u


def test_refit_null_cells_are_exactly_the_four_permuted_alarm_cells():
    cells = [(c, t, tau) for c in _runner.CONTROLS for t in ("A", "B") for tau in (0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0)
             if _runner.needs_refit_null(c, t, tau)]
    assert cells == [("permuted_targets", "A", 1.0), ("permuted_targets", "A", 5.0), ("permuted_targets", "B", 1.0), ("permuted_targets", "B", 5.0)]


def test_alarm_inputs_refit_p_by_hand():
    names = metrics.control_alarm_cells()
    rng = np.random.default_rng(2)
    per = {cid: {n: (np.zeros((6, 4)), rng.uniform(-1, 1, (6, 4))) for n in names} for cid in (0, 1)}   # zero prediction: G = 0
    low = {cid: {n: np.full(9999, -0.5) for n in names if n.startswith("permuted")} for cid in (0, 1)}
    high = {cid: {n: np.full(9999, 0.0) for n in names if n.startswith("permuted")} for cid in (0, 1)}
    a_low, a_high = _runner.alarm_inputs(per, DEV, nulls=low), _runner.alarm_inputs(per, DEV, nulls=high)
    p = "permuted_targets|A|1.0"
    assert a_low[p]["G"] == 0.0 and a_low[p]["b"] == 0 and a_low[p]["p"] == 1 / 10000           # null always below
    assert a_high[p]["b"] == 9999 and a_high[p]["p"] == 1.0                                      # ties count as >=
    bad = {cid: {n: np.full(999, 0.0) for n in names if n.startswith("permuted")} for cid in (0, 1)}
    with pytest.raises(ValueError, match="9999 finite gains"):
        _runner.alarm_inputs(per, DEV, nulls=bad)


## --- the freeze candidate in this repository ------------------------------------------------------------------
def _real_candidate():
    return json.loads(runs.CANDIDATE_FILE.read_text(encoding="utf-8"))


def test_candidate_is_bound_to_the_current_code():
    """Fails as soon as a production module or protocol file changes after the candidate: a stale candidate must
    be replaced by a new, documented one -- it can never silently cover other code. (Independent of whether a
    freeze exists in the checkout, review R4.)"""
    c = _real_candidate()
    assert c["schema"] == runs.CANDIDATE_SCHEMA and c["status"].startswith("CANDIDATE")
    assert c["code_identity"] == runs.code_identity(exclude=("protocol/freeze.json",))["identity"]
    assert c["git"]["dirty"] is False


def test_candidate_values_come_from_the_protocol():
    c, d = _real_candidate(), streams.defaults()
    g = runs.research_grid(c)
    assert g["study_id"] == c["study"]["research_study_id"] != d["development_study_id"]
    assert not d["streams"]["excluded_master_seeds"]["from"] <= g["study_id"] <= d["streams"]["excluded_master_seeds"]["to"]
    assert g["contexts"] == list(range(20)) and g["sizes"] == dict(d["data_per_context"]) and g["dt"] == d["integration"]["dt"]
    assert g["proposals"] == d["strength_surrogate"]["proposals"] and c["grid"]["cells"] == len(runs.expected_cells(g)) == 1960
    assert c["control_rules"]["control_alarms"] == metrics.control_alarm_protocol() and c["control_rules"]["permutations"] == 9999
    assert c["decoder"]["lambda_grid"] == [1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0]
    assert c["decoder"]["mlp"]["decision"].startswith("WAIVED") and "Astra" in c["decoder"]["mlp"]["basis"]
    assert c["study"]["research_study_id"] == 1431972670          # kept from the first candidate, never redrawn
    assert "secrets.randbelow" in c["study"]["method"]
    # the contract, not this machine (review R4): a complete, explicit environment; equality is the readiness check
    assert set(c["software"]) == set(runs.SOFTWARE_KEYS) and all(isinstance(v, str) and v for v in c["software"].values())
    assert set(c["streams"]["decoder_extras"]) == {"1", "2", "3", "4"}


def test_candidate_supersedes_the_first_one_which_is_kept():
    c = _real_candidate()
    old = runs.HERE / c["supersedes"]["file"]
    assert old.exists() and artifacts.sha256(old.read_bytes().replace(b"\r\n", b"\n")) == c["supersedes"]["sha256"]
    o = json.loads(old.read_text(encoding="utf-8"))
    assert o["study"]["research_study_id"] == c["study"]["research_study_id"] and o["code_identity"] != c["code_identity"]


def test_candidate_yaml_twin():
    import yaml
    assert yaml.safe_load(runs.CANDIDATE_FILE.with_suffix(".yaml").read_text(encoding="utf-8")) == _real_candidate()


def test_study_evaluation_missing_cell_is_an_error_not_zero():
    grid, records = _grid_records(lambda cid, cond, task: 0.2)
    records.pop(next(iter(records)))
    with pytest.raises(KeyError):
        release.study_evaluation(grid, records)


## --- review LANTERN_LR6_REVIEW_29af52f: R1 software binding, R2 ties, R3 null provenance, R4 test contract -----
import shutil as _shutil
from types import SimpleNamespace as _NS

from experiments.lantern_reconstruction.artifacts import IntegrityError as _IntegrityError


# R1 -- the frozen environment is enforced before a research run folder exists, and again before start/resume
@pytest.mark.parametrize("key", ["python", "numpy", "scipy"])
def test_r1_each_software_deviation_refuses_before_any_run_folder(freeze_files, tmp_path, monkeypatch, key):
    freeze_files()
    real = runs.software()
    monkeypatch.setattr(runs, "software", lambda: {**real, key: real[key] + ".other"})
    with pytest.raises(ValueError, match="software differs from the frozen environment"):
        runs.create_research_run(tmp_path / "runs", run_id="r")
    assert not (tmp_path / "runs").exists()


@pytest.mark.parametrize("sw", [None, {}, {"python": "3.11.9", "numpy": "2.2.6"}, {"python": "3.11.9", "numpy": "2.2.6", "scipy": 1.15},
                                {"python": "3.11.9", "numpy": "2.2.6", "scipy": "1.15.3", "extra": "x"}, "3.11.9"])
def test_r1_missing_or_incomplete_software_block_is_refused(freeze_files, tmp_path, sw):
    cand = _candidate()
    if sw is None:
        cand.pop("software")
    else:
        cand["software"] = sw
    freeze_files(cand)
    with pytest.raises(ValueError, match="no complete software environment"):
        runs.create_research_run(tmp_path / "runs")
    assert not (tmp_path / "runs").exists()


def test_r1_software_is_checked_again_before_start(freeze_files, tmp_path, monkeypatch):
    freeze_files()
    rd = runs.create_research_run(tmp_path / "runs", run_id="r")
    real = runs.software()
    wrong = {**real, "python": real["python"] + ".review-mismatch"}
    assert wrong != real
    monkeypatch.setattr(runs, "software", lambda: dict(wrong))
    with pytest.raises(runs.ResumeRefused, match="software"):
        runs.execute(rd, lock_root=tmp_path / "locks")
    assert runs.status(rd) is None and not (rd / "structure" / "c000.json").exists()


def test_r1_a_manifest_made_in_the_wrong_environment_never_legitimises_it(freeze_files, tmp_path, monkeypatch):
    """Review R1 counterexample: a manifest written under Python 3.12.14 was consistent with exactly that wrong
    environment. Neither the same wrong environment nor the frozen one may start it."""
    cand = freeze_files()
    real = runs.software()
    wrong = {**real, "python": real["python"] + ".review-mismatch"}
    assert wrong != real
    monkeypatch.setattr(runs, "software", lambda: dict(wrong))
    rd = runs._create(tmp_path / "runs", "research", runs.research_grid(cand), "made-elsewhere")   # bypasses the gate
    assert runs.load_run(rd)["software"] == wrong
    with pytest.raises(runs.ResumeRefused, match="software differs from the frozen environment"):
        runs.execute(rd, lock_root=tmp_path / "locks")
    monkeypatch.setattr(runs, "software", lambda: dict(real))
    with pytest.raises(runs.ResumeRefused, match="software"):
        runs.execute(rd, lock_root=tmp_path / "locks")
    assert runs.status(rd) is None and not (rd / "structure" / "c000.json").exists()


# R4 -- the REAL candidate: accepted only in its own environment, refused in any other (both independent of this machine)
@pytest.fixture()
def real_candidate_frozen(tmp_path, monkeypatch):
    cp, fp = tmp_path / "cand.json", tmp_path / "freeze.json"
    cp.write_bytes(runs.CANDIDATE_FILE.read_bytes())
    cand = json.loads(cp.read_text(encoding="utf-8"))
    fp.write_text(json.dumps({"schema": runs.FREEZE_SCHEMA, "status": "frozen", "approved_by": ["SYNTHETIC TEST FIXTURE -- NO APPROVAL"],
                              "candidate_sha256": artifacts.sha256(cp.read_bytes().replace(b"\r\n", b"\n")),
                              "code_identity": cand["code_identity"]}), encoding="utf-8")
    monkeypatch.setattr(runs, "CANDIDATE_FILE", cp)
    monkeypatch.setattr(runs, "FREEZE_FILE", fp)
    return cand


def test_r4_real_candidate_refused_in_a_foreign_environment(real_candidate_frozen, monkeypatch, tmp_path):
    wrong_python = real_candidate_frozen["software"]["python"] + ".review-mismatch"
    monkeypatch.setattr(runs, "software", lambda: {**real_candidate_frozen["software"], "python": wrong_python})
    with pytest.raises(ValueError, match="software differs"):
        runs.create_research_run(tmp_path / "runs")
    r = runs.research_readiness()
    assert r["research_start_allowed"] is False and wrong_python in r["refusal"] and r["software_problems"]


def test_r4_real_candidate_accepted_in_its_own_environment(real_candidate_frozen, monkeypatch):
    monkeypatch.setattr(runs, "software", lambda: dict(real_candidate_frozen["software"]))
    assert runs.frozen_candidate() == real_candidate_frozen
    r = runs.research_readiness()
    assert r["research_start_allowed"] is True and r["software_problems"] == [] and r["code_matches_candidate"] is True


# R2 -- numerical ties
def _review_tie_case():
    """Review R2, exactly: observe() of zero states and zero measurement errors (sin 0, cos 1: every column constant,
    standardised to 0), so W = 0 and b = mean(U_train) for every permutation; observed and null gains are equal."""
    ctx = _contexts.make_context(DEV, 0)
    spec = _observation.observation_spec(ctx, "B")
    names, target = metrics.control_alarm_cells(), "permuted_targets|B|1.0"
    per, nulls, diffs = {}, {}, []
    for cid, seed in enumerate((0, 1)):
        rng = np.random.default_rng(seed)
        U = [rng.uniform(-1, 1, (n, 4)) for n in (30, 12, 20)]
        X = [_observation.observe(ctx, spec, np.zeros((len(u), 34)), np.zeros((len(u), 34))) for u in U]
        pt, pv = rng.permutation(30), rng.permutation(12)
        model = _training.fit_ridge(spec, X[0], U[0][pt], X[1], U[1][pv])
        pred = metrics.project(_predict(model, X[2]))
        gain = metrics.scores(*metrics.episode_losses(pred, U[2]))["G"]
        null = _training.permuted_null_gains(X[0], U[0], X[1], U[1], X[2], U[2], np.random.default_rng(99 + cid), 9999)
        diffs.append(float(np.max(np.abs(null - gain))))
        per[cid] = {n: (np.zeros_like(pred), U[2]) for n in names}
        per[cid][target] = (pred, U[2])
        nulls[cid] = {n: np.zeros(9999) for n in names if n.startswith("permuted")}
        nulls[cid][target] = null
    return per, nulls, target, diffs


def test_r2_review_tie_case_gives_p_1_and_no_alarm():
    per, nulls, target, diffs = _review_tie_case()
    assert max(diffs) < 1e-15                                   # mathematically equal; round-off only (review: 4.16e-17)
    cells = _runner.alarm_inputs(per, DEV, nulls=nulls)
    assert cells[target]["b"] == 9999 and cells[target]["p"] == 1.0
    alarms = metrics.control_alarms(cells)
    assert not alarms["target_dependence_alarm"] and not alarms["positive_spurious_success_alarm"]


@pytest.mark.parametrize("obs", [0.3, -0.2, 0.0])
def test_r2_exact_ties_count_for_positive_negative_and_zero(obs):
    assert metrics.upper_tail_count(np.full(7, obs), obs) == 7
    assert metrics.upper_tail_count(np.full(7, obs), obs, tol=0.0) == 7          # exact ties always count


@pytest.mark.parametrize("obs", [0.3, -0.2, 0.0])
def test_r2_values_outside_the_tolerance_on_both_sides(obs):
    tol = metrics.tie_tolerance()
    assert tol == 1e-10 == metrics.control_alarm_protocol()["statistic"]["tie_rule"]["absolute_tolerance"]
    null = np.array([obs - 2 * tol, obs - 0.5 * tol, obs + 0.5 * tol, obs + 2 * tol])
    assert metrics.upper_tail_count(null, obs) == 3                          # only the value 2 tol BELOW is not counted
    assert metrics.upper_tail_count(null[[0]], obs) == 0 and metrics.upper_tail_count(null[[3]], obs) == 1


def test_r2_tie_rule_is_conservative_and_validated():
    rng = np.random.default_rng(5)
    null, obs = rng.normal(size=500), 0.1
    assert metrics.upper_tail_count(null, obs) >= int(np.sum(null >= obs))
    for bad in (np.array([np.nan]), np.zeros((2, 2))):
        with pytest.raises(ValueError):
            metrics.upper_tail_count(bad, 0.0)
    with pytest.raises(ValueError):
        metrics.upper_tail_count(np.zeros(3), 0.0, tol=-1e-10)


def test_r2_fixed_prediction_null_counts_round_off_ties_too():
    """Constant predictions: every target permutation gives mathematically the observed G (a reordering of the same
    rows); the fixed-prediction test must give p = 1 as well (same numerical contract as the refit null)."""
    rng = np.random.default_rng(11)
    cells = {cid: (np.full((37, 4), 0.3), rng.uniform(-1, 1, (37, 4))) for cid in (0, 1)}
    r = metrics.permutation_gain_test(cells, np.random.default_rng(4), 999)
    assert r["b"] == 999 and r["p"] == 1.0


@pytest.mark.parametrize("chunk", [1, 7, 50, 128])
def test_r2_chunk_size_and_explicit_permutations_give_identical_gains(chunk):
    _, U, X = _synthetic(6)
    ref = _training.permuted_null_gains(X["tr"], U["tr"], X["va"], U["va"], X["te"], U["te"], np.random.default_rng(3), 150, chunk=150)
    got = _training.permuted_null_gains(X["tr"], U["tr"], X["va"], U["va"], X["te"], U["te"], np.random.default_rng(3), 150, chunk=chunk)
    assert np.array_equal(ref, got)
    r = np.random.default_rng(3)
    perms = [(r.permutation(300), r.permutation(80)) for _ in range(150)]
    assert np.array_equal(_training.refit_gains(X["tr"], U["tr"], X["va"], U["va"], X["te"], U["te"], perms), ref)
    assert np.array_equal(_training.refit_gains(X["tr"], U["tr"], X["va"], U["va"], X["te"], U["te"], perms[chunk - 1:chunk]), ref[chunk - 1:chunk])


def test_r2_refit_against_an_independent_normal_equation_reference():
    """No production fit, standardisation or prediction function in the reference (review 3.1)."""
    rng = np.random.default_rng(17)
    U = [rng.uniform(-1, 1, (n, 4)) for n in (30, 12, 20)]
    M = rng.normal(size=(4, 16))
    X = [u @ M + rng.normal(size=(len(u), 16)) for u in U]
    mean, sd = X[0].mean(0), X[0].std(0)
    Z = [(x - mean) / sd for x in X]
    xc = Z[0] - Z[0].mean(0)
    replay, direct = np.random.default_rng(91), []
    for _ in range(20):
        u, v = U[0][replay.permutation(30)], U[1][replay.permutation(12)]
        ym, sols = u.mean(0), []
        for lam in (1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0):
            W = np.linalg.solve(xc.T @ xc / 30 + lam * np.eye(16), xc.T @ (u - ym) / 30)
            b = ym - Z[0].mean(0) @ W
            sols.append((np.mean((np.clip(Z[1] @ W + b, -1, 1) - v) ** 2), -lam, W, b))
        _, _, W, b = min(sols, key=lambda z: (z[0], z[1]))
        p = np.clip(Z[2] @ W + b, -1, 1)
        direct.append(3 * np.mean(np.mean(U[2] ** 2, 1) - np.mean((p - U[2]) ** 2, 1)))
    fast = _training.permuted_null_gains(X[0], U[0], X[1], U[1], X[2], U[2], np.random.default_rng(91), 20)
    assert np.max(np.abs(fast - np.array(direct))) < 1e-12


def test_r2_injected_learning_channel_still_fires_the_alarm():
    """A 'control' decoder that learned from the REAL targets: G > 0, p = 1/(B+1) in both contexts' mean, both
    alarms fire (the tie rule must not blunt a real effect)."""
    spec = _observation.observation_spec(_contexts.make_context(DEV, 0), "B")
    names, target = metrics.control_alarm_cells(), "permuted_targets|B|1.0"
    per, nulls = {}, {}
    for cid in (0, 1):
        _, U, X = _synthetic(20 + cid)
        m = _training.fit_ridge(spec, X["tr"], U["tr"], X["va"], U["va"])
        pred = metrics.project(_predict(m, X["te"]))
        per[cid] = {n: (np.zeros_like(pred), U["te"]) for n in names}
        per[cid][target] = (pred, U["te"])
        nulls[cid] = {n: np.zeros(9999) for n in names if n.startswith("permuted")}
        nulls[cid][target] = _training.permuted_null_gains(X["tr"], U["tr"], X["va"], U["va"], X["te"], U["te"],
                                                           np.random.default_rng(30 + cid), 9999)
    cells = _runner.alarm_inputs(per, DEV, nulls=nulls)
    assert cells[target]["G"] > 0.3 and cells[target]["b"] == 0 and cells[target]["p"] == 1 / 10000
    alarms = metrics.control_alarms(cells)
    assert alarms["target_dependence_alarm"] and alarms["positive_spurious_success_alarm"]


def _refit_inputs(seed=8):
    ctx = _contexts.make_context(DEV, 0)
    spec = _observation.observation_spec(ctx, "B")
    _, U, X = _synthetic(seed)
    Xd = {"train": X["tr"], "val": X["va"], "test": X["te"]}
    batches = {"train": _NS(u=U["tr"]), "val": _NS(u=U["va"]), "test": _NS(u=U["te"])}
    k = 2
    pt, pv = (_runner.target_permutation(ctx, s, len(batches[s].u), "B", k) for s in ("train", "val"))
    model = _training.fit_ridge(spec, X["tr"], U["tr"][pt], X["va"], U["va"][pv])
    return ctx, Xd, batches, model


def test_r2_refit_path_check_holds_and_records_the_inputs():
    ctx, X, batches, model = _refit_inputs()
    chk = _runner.refit_path_check(ctx, "B", 2, X, batches, model)
    assert chk["abs_deviation"] <= 1e-12 == chk["tolerance"] and set(chk["inputs"]) == set(runs._NULL_INPUTS)
    assert chk["observed_G_fit_path"] == metrics.scores(*metrics.episode_losses(metrics.project(_predict(model, X["test"])), batches["test"].u))["G"]


def test_r2_refit_path_check_refuses_a_deviating_path(monkeypatch):
    ctx, X, batches, model = _refit_inputs()
    real = _training.refit_gains
    monkeypatch.setattr(_training, "refit_gains", lambda *a, **k: real(*a, **k) + 1e-9)
    with pytest.raises(ValueError, match="refit-path check failed"):
        _runner.refit_path_check(ctx, "B", 2, X, batches, model)


# R3 -- a refit null belongs to exactly one run, context, cell, model and test targets
R3_GRID = dict(conditions=("lantern",), tasks=("A",), sizes={"train": 30, "val": 12, "test": 20}, proposals=100)
R3_CELL = {"context_id": 0, "condition": "lantern", "control": "permuted_targets", "task": "A", "time": 1.0, "time_index": 2}


@pytest.fixture(scope="module")
def r3_runs(tmp_path_factory):
    root = tmp_path_factory.mktemp("r3")
    ref = runs.create_run(root / "runs", "smoke", [0, 1], run_id="reference", **R3_GRID)
    assert runs.execute(ref, lock_root=root / "locks") == "complete"
    other = runs.create_run(root / "runs", "smoke", [0, 1], run_id="other", **R3_GRID)
    with pytest.raises(runs.Interrupted):                     # 3 units x 7 cells, then permuted A t0..t2
        runs.execute(other, lock_root=root / "locks", stop_after=24)
    assert (other / "cells" / runs.cell_dir_name(R3_CELL) / "null.npz").exists()
    return ref, other


def _with_foreign_null(r3_runs, tmp_path, source):
    ref, other = r3_runs
    rd = tmp_path / "copy"
    _shutil.copytree(ref, rd)
    src = {"context": rd / "cells" / runs.cell_dir_name({**R3_CELL, "context_id": 1}),
           "time": rd / "cells" / runs.cell_dir_name({**R3_CELL, "time": 5.0, "time_index": 5}),
           "run": other / "cells" / runs.cell_dir_name(R3_CELL)}[source]
    dst = rd / "cells" / runs.cell_dir_name(R3_CELL)
    (dst / "null.npz").unlink()
    _shutil.copyfile(src / "null.npz", dst / "null.npz")
    rec = json.loads((dst / "record.json").read_text(encoding="utf-8"))
    rec["null"] = json.loads((src / "record.json").read_text(encoding="utf-8"))["null"]   # the valid null block, too
    (dst / "record.json").write_text(json.dumps(rec), encoding="utf-8")
    return rd


def test_r3_original_null_is_accepted_and_carries_its_provenance(r3_runs):
    ref = r3_runs[0]
    run = runs.load_run(ref)
    rec = runs.verify_record(ref, run, R3_CELL, _contexts.make_context(DEV, 0))
    assert rec["schema"] == "lantern-cell-record-v2" and rec["null"]["provenance"]["context_id"] == 0
    assert rec["null"]["provenance"]["run_identity"] == run["run_identity"] and rec["null"]["provenance"]["B"] == 9999


@pytest.mark.parametrize("source", ["context", "time", "run"])
def test_r3_foreign_null_with_its_valid_record_block_is_refused(r3_runs, tmp_path, source):
    """Review R3 counterexample (null.npz AND its valid record['null'] from another context), extended to another
    time and another run (there the null arrays are even bit-identical: only the provenance tells them apart)."""
    rd = _with_foreign_null(r3_runs, tmp_path, source)
    with pytest.raises(_IntegrityError, match="does not belong to this cell"):
        runs.verify_record(rd, runs.load_run(rd), R3_CELL, _contexts.make_context(DEV, 0))
    rep = release.release_report(rd)
    assert not rep["technically_complete"] and not rep["scientifically_interpretable"]


@pytest.mark.parametrize("edit", ["drop_provenance", "deviation", "observed", "inputs_missing"])
def test_r3_edited_null_block_is_refused(r3_runs, tmp_path, edit):
    rd = tmp_path / "copy"
    _shutil.copytree(r3_runs[0], rd)
    p = rd / "cells" / runs.cell_dir_name(R3_CELL) / "record.json"
    rec = json.loads(p.read_text(encoding="utf-8"))
    chk = rec["null"]["refit_path_check"]
    if edit == "drop_provenance":
        rec["null"].pop("provenance")
    elif edit == "deviation":
        chk["abs_deviation"] = 1.0
    elif edit == "observed":
        chk["observed_G_fit_path"] += 1e-3
    else:
        chk["inputs"].pop("X_train")
    p.write_text(json.dumps(rec), encoding="utf-8")
    with pytest.raises(_IntegrityError, match="refit null"):
        runs.verify_record(rd, runs.load_run(rd), R3_CELL, _contexts.make_context(DEV, 0))


def test_r3_resume_compares_the_recorded_null_inputs(r3_runs, tmp_path):
    """The input identities cannot be re-derived without the trajectories; the resume recomputes them and must
    find the recorded ones."""
    rd = tmp_path / "other"
    _shutil.copytree(r3_runs[1], rd)
    p = rd / "cells" / runs.cell_dir_name(R3_CELL) / "record.json"
    rec = json.loads(p.read_text(encoding="utf-8"))
    rec["null"]["refit_path_check"]["inputs"]["X_train"] = "0" * 64
    p.write_text(json.dumps(rec), encoding="utf-8")
    with pytest.raises(_IntegrityError, match="differs from its record"):
        runs.execute(rd, lock_root=tmp_path / "locks")
    assert runs.status(rd) == "failed_integrity"


def test_r3_persist_refuses_a_path_check_for_another_observed_gain(r3_runs, tmp_path):
    ref = r3_runs[0]
    run = runs.load_run(ref)
    folder = ref / "cells" / runs.cell_dir_name(R3_CELL)
    rec = json.loads((folder / "record.json").read_text(encoding="utf-8"))
    model = artifacts.load_model_verified(folder, rec["model"])
    meta = {**rec["null"]["refit_path_check"], "observed_G_fit_path": 0.5}
    with pytest.raises(_IntegrityError, match="different observed gain"):
        runs._persist_cell(tmp_path / "x", run, _contexts.make_context(DEV, 0), R3_CELL, model, np.zeros((20, 66)),
                           np.zeros((20, 4)), null_G=np.zeros(9999), null_meta=meta)
    with pytest.raises(_IntegrityError, match="refit null"):
        runs._persist_cell(tmp_path / "x", run, _contexts.make_context(DEV, 0), R3_CELL, model, np.zeros((20, 66)),
                           np.zeros((20, 4)), null_G=np.zeros(9999))            # null without its path check
    assert not (tmp_path / "x").exists()


# Pre-start review LANTERN_LR7_VORSTARTREVIEW_2822141 (LR7-F1, LR7-F2, section 6): the start tool. No numerical
# execution here: runs.execute and (where noted) the report writer are replaced by recorders; research manifests are
# created from the synthetic freeze fixture (2 contexts), never from the real candidate.
import contextlib  # noqa: E402
import importlib.util  # noqa: E402
import io  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

_TOOL_PATH = runs.HERE / "tools" / "lr7_research_run.py"
_spec = importlib.util.spec_from_file_location("lr7_research_run_under_test", _TOOL_PATH)
lr7 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lr7)
_BUDGET = {"extrapolated_research": {"execute_seconds": 1.0, "release_seconds": 1.0}, "operating_window": {"recommended_s": 9000}}
SID = 1234567890
_REAL_WRITE_REPORT = release.write_release_report     # captured before any fixture replaces it


@pytest.fixture()
def tool_env(freeze_files, tmp_path, monkeypatch):
    """A valid synthetic freeze, an isolated runs root, recorders for every effect."""
    freeze_files(_candidate(budget=_BUDGET))
    calls = []
    monkeypatch.setattr(lr7, "RUNS_ROOT", tmp_path / "runs")
    monkeypatch.setattr(lr7, "keep_awake", lambda on: calls.append(("awake", on)))

    def fake_execute(rd, **kw):
        calls.append(("execute", Path(rd).name))
        return "complete"

    def fake_report(rd):
        calls.append(("report", Path(rd).name))
        return {"technically_complete": True, "scientifically_interpretable": True, "n_verified_cells": 0, "scientific_blocks": []}
    monkeypatch.setattr(runs, "execute", fake_execute)
    monkeypatch.setattr(lr7.release, "write_release_report", fake_report)
    return calls


def _invoke(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", [str(_TOOL_PATH), *argv])
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            return lr7.main(), out.getvalue()
        except SystemExit as e:
            return ("exit", str(e.code)), out.getvalue()


def _research_run(tmp_path, name="r1"):
    return runs.create_research_run(tmp_path / "runs", run_id=name)


def _events(rd):
    return (Path(rd) / "events.jsonl").read_bytes()


def _to_complete(rd):
    log = runs.EventLog(Path(rd) / "events.jsonl")
    runs.set_status(log, "running", "SYNTHETIC TEST STATUS")
    runs.set_status(log, "complete", "SYNTHETIC TEST STATUS; no simulation executed")


def test_lr7_dry_run_creates_and_runs_nothing(tool_env, tmp_path, monkeypatch):
    res, text = _invoke(monkeypatch)
    assert res == 0 and "DRY RUN" in text and not (tmp_path / "runs").exists() and tool_env == []


@pytest.mark.parametrize("args", [["--start"], ["--start", "--confirm-study", "1"]])
def test_lr7_start_without_or_with_wrong_confirmation_refused_before_creation(tool_env, tmp_path, monkeypatch, args):
    res, _ = _invoke(monkeypatch, *args)
    assert res[0] == "exit" and "--confirm-study" in res[1] and not (tmp_path / "runs").exists() and tool_env == []


def test_lr7_start_and_resume_exclude_each_other(tool_env, monkeypatch):
    res, _ = _invoke(monkeypatch, "--start", "--resume", "unused")
    assert res[0] == "exit" and "exclude" in res[1] and tool_env == []


def test_lr7_valid_start_order_create_execute_report(tool_env, tmp_path, monkeypatch):
    res, _ = _invoke(monkeypatch, "--start", "--confirm-study", str(SID))
    created = [p.name for p in (tmp_path / "runs").iterdir()]
    assert res == 0 and len(created) == 1
    assert tool_env == [("awake", True), ("execute", created[0]), ("report", created[0]), ("awake", False)]
    assert runs.load_run(tmp_path / "runs" / created[0])["kind"] == "research"


def test_lr7_f2_development_run_refused_as_resume_target(tool_env, tmp_path, monkeypatch):
    rd = runs.create_run(tmp_path / "dev", "smoke", [0, 1], run_id="dev")
    before = _events(rd)
    res, _ = _invoke(monkeypatch, "--resume", str(rd))
    assert res[0] == "exit" and "not a research run" in res[1]
    assert tool_env == [] and _events(rd) == before


def test_lr7_f2_wrong_explicit_confirmation_refused_on_resume(tool_env, tmp_path, monkeypatch):
    rd = _research_run(tmp_path)
    before = _events(rd)
    res, _ = _invoke(monkeypatch, "--resume", str(rd), "--confirm-study", "1")
    assert res[0] == "exit" and "--confirm-study 1" in res[1] and tool_env == [] and _events(rd) == before
    res, _ = _invoke(monkeypatch, "--resume", str(rd), "--confirm-study", str(SID))     # the right value is accepted
    assert res == 0 and [c[0] for c in tool_env] == ["awake", "execute", "report", "awake"]


def test_lr7_f2_research_manifest_with_other_grid_or_software_refused(tool_env, freeze_files, tmp_path, monkeypatch):
    rd = _research_run(tmp_path)
    before = _events(rd)
    freeze_files(_candidate(budget=_BUDGET, grid={**_candidate()["grid"], "contexts": [0, 2]}))   # a different frozen grid
    res, _ = _invoke(monkeypatch, "--resume", str(rd))
    assert res[0] == "exit" and "grid" in res[1] and tool_env == [] and _events(rd) == before
    freeze_files(_candidate(budget=_BUDGET))
    real_software = runs.software()
    monkeypatch.setattr(runs, "software", lambda: {**real_software, "numpy": "0.0.0-review"})
    res, _ = _invoke(monkeypatch, "--resume", str(rd))
    assert res[0] == "exit" and "software" in res[1] and tool_env == [] and _events(rd) == before


def test_lr7_execution_failure_releases_keep_awake(tool_env, tmp_path, monkeypatch):
    rd = _research_run(tmp_path)

    def boom(rd, **kw):
        tool_env.append(("execute", "boom"))
        raise RuntimeError("injected before numerical execution")
    monkeypatch.setattr(runs, "execute", boom)
    with pytest.raises(RuntimeError, match="injected"):
        lr7.run(rd)
    assert tool_env == [("awake", True), ("execute", "boom"), ("awake", False)] and runs.status(rd) is None


def test_lr7_f1_complete_without_report_writes_report_only(tool_env, tmp_path, monkeypatch):
    rd = _research_run(tmp_path)
    _to_complete(rd)
    monkeypatch.setattr(lr7.release, "write_release_report", _REAL_WRITE_REPORT)   # the real exclusive writer
    res = lr7.run(rd)
    assert tool_env == [("awake", True), ("awake", False)]          # no execute
    assert (rd / "release_report.json").exists() and runs.status(rd) == "complete"
    assert res == 1          # an empty synthetic run is honestly not technically complete


def test_lr7_f1_complete_with_report_never_overwritten_nor_recomputed(tool_env, tmp_path, monkeypatch):
    rd = _research_run(tmp_path)
    _to_complete(rd)
    _REAL_WRITE_REPORT(rd)
    before = (rd / "release_report.json").read_bytes()
    assert lr7.run(rd) == 1 and tool_env == [] and (rd / "release_report.json").read_bytes() == before
    tampered = json.loads(before)
    tampered["technically_complete"] = not tampered["technically_complete"]
    (rd / "release_report.json").write_text(json.dumps(tampered), encoding="utf-8")
    kept = (rd / "release_report.json").read_bytes()
    with pytest.raises(SystemExit, match="differs from a read-only recomputation"):
        lr7.run(rd)
    assert tool_env == [] and (rd / "release_report.json").read_bytes() == kept


def test_lr7_f1_report_failure_can_be_finished_later(tool_env, tmp_path, monkeypatch):
    rd = _research_run(tmp_path)
    _to_complete(rd)
    cells_before = sorted(p.name for p in (rd / "cells").iterdir())

    def fail(rd):
        raise RuntimeError("injected report failure")
    monkeypatch.setattr(lr7.release, "write_release_report", fail)
    with pytest.raises(RuntimeError, match="injected report failure"):
        lr7.run(rd)
    assert tool_env[-1] == ("awake", False) and not (rd / "release_report.json").exists() and runs.status(rd) == "complete"
    monkeypatch.setattr(lr7.release, "write_release_report", _REAL_WRITE_REPORT)
    lr7.run(rd)
    assert (rd / "release_report.json").exists() and sorted(p.name for p in (rd / "cells").iterdir()) == cells_before
    assert not any(c[0] == "execute" for c in tool_env)


@pytest.mark.parametrize("final", list(runs.TERMINAL))
def test_lr7_final_states_refused_without_new_attempt(tool_env, tmp_path, final):
    rd = _research_run(tmp_path)
    log = runs.EventLog(rd / "events.jsonl")
    runs.set_status(log, "running", "SYNTHETIC TEST STATUS")
    runs.set_status(log, final, "SYNTHETIC TEST STATUS")
    before = _events(rd)
    with pytest.raises(SystemExit, match="final"):
        lr7.run(rd)
    assert tool_env == [] and _events(rd) == before


def test_lr7_running_refers_to_recover_and_removes_no_lock(tool_env, tmp_path):
    rd = _research_run(tmp_path)
    runs.set_status(runs.EventLog(rd / "events.jsonl"), "running", "SYNTHETIC TEST STATUS")
    before = _events(rd)
    with pytest.raises(SystemExit, match="recover"):
        lr7.run(rd)
    assert tool_env == [] and _events(rd) == before


def test_lr7_report_present_but_run_not_complete_refused(tool_env, tmp_path):
    rd = _research_run(tmp_path)
    (rd / "release_report.json").write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit, match="inspect manually"):
        lr7.run(rd)
    assert tool_env == []


def test_lr7_section6_second_first_start_refused(tool_env, tmp_path, monkeypatch):
    first = _research_run(tmp_path, "existing")
    res, _ = _invoke(monkeypatch, "--start", "--confirm-study", str(SID))
    assert res[0] == "exit" and "already exists" in res[1] and first.name in res[1]
    assert [p.name for p in (tmp_path / "runs").iterdir()] == ["existing"] and tool_env == []
