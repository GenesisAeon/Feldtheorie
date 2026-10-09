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
         "code_identity": runs.code_identity(exclude=("protocol/freeze.json",))["identity"]}
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


def test_no_research_run_without_a_freeze_in_this_repository(tmp_path):
    assert not runs.FREEZE_FILE.exists()
    with pytest.raises(ValueError, match="frozen protocol"):
        runs.create_research_run(tmp_path)
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


def test_study_evaluation_missing_cell_is_an_error_not_zero():
    grid, records = _grid_records(lambda cid, cond, task: 0.2)
    records.pop(next(iter(records)))
    with pytest.raises(KeyError):
        release.study_evaluation(grid, records)
