"""LR4 development pipeline for one context (plan sections 6-9, 11, 13). DEVELOPMENT ONLY: it refuses any
study id other than study_defaults' development_study_id -- the research runner with freeze, run ids and
resume belongs to LR5 / LR7.

Phases, strictly separated per (condition, task, time) cell:
  1. trajectories ONCE per (split, condition) with RK4, read at the 7 grid times (episodes.simulate);
  2. features ONLY through the validated entry point observation.observe(ctx, spec, states, eps);
  3. fit on train, lambda chosen on val (training.fit_ridge -- it never receives test data);
  4. test scoring of the finished decoder (evaluate.score_cell);
  5. A from the 7 G values of the fixed grid (metrics.curve_aggregate).
All conditions share targets, phases and measurement errors of a context; each condition has its own fit."""
from __future__ import annotations

from typing import Dict, Optional, Sequence

import numpy as np

from experiments.lantern_reconstruction import episodes, observation, streams
from experiments.lantern_reconstruction.contexts import ContextSpec, check_context, fingerprint
from experiments.lantern_reconstruction.decoders import check_decoder_for
from experiments.lantern_reconstruction.evaluate import score_cell
from experiments.lantern_reconstruction.metrics import curve_aggregate
from experiments.lantern_reconstruction.training import fit_ridge

SPLITS = ("train", "val", "test")
TASKS = ("A", "B")
CONTROLS = ("none", "reset", "zero_impulse", "permuted_targets")
TASK_INDEX = {"A": 0, "B": 1}
PERMUTED_TARGETS_PURPOSE = 2      # decoder-stream extra component (protocol/control_alarms.json)
ALARM_PURPOSE = 1


def development_sizes() -> Dict[str, int]:
    return dict(streams.defaults()["data_per_context"])


def check_selection(sizes, conditions, tasks, control) -> Dict[str, int]:
    sizes = development_sizes() if sizes is None else dict(sizes)
    if set(sizes) != set(SPLITS) or any(isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)) or n < 2 for n in sizes.values()):
        raise ValueError("sizes must give an integer >= 2 for exactly train, val and test")
    if not conditions or len(set(conditions)) != len(conditions) or not set(conditions) <= set(episodes.CONDITIONS):
        raise ValueError(f"conditions must be distinct entries of {episodes.CONDITIONS}")
    if not tasks or len(set(tasks)) != len(tasks) or not set(tasks) <= set(TASKS):
        raise ValueError("tasks must be distinct entries of ('A', 'B')")
    if control not in CONTROLS:
        raise ValueError(f"control must be one of {CONTROLS}")
    return sizes


def prepare_context(ctx: ContextSpec, C_lantern: np.ndarray, sizes: Dict[str, int], proposals: Optional[int] = None) -> Dict:
    """Everything per context that all cells share: the four condition matrices (+ surrogate report),
    the three batches and both observation specs."""
    mats, surrogate_report = episodes.coupling_matrices_with_report(C_lantern, ctx, proposals)
    return {"mats": mats, "surrogate_report": surrogate_report,
            "batches": {s: episodes.make_batch(ctx, s, range(sizes[s])) for s in SPLITS},
            "specs": {t: observation.observation_spec(ctx, t) for t in TASKS}}


def training_targets(ctx: ContextSpec, u_train: np.ndarray, control: str, task: str, time_index: int) -> np.ndarray:
    """The training targets of a cell: unchanged, or for the 'permuted_targets' control permuted by the
    decoder stream (study, context, train, decoder, 0, 2, task index, time index). Val/test stay unpermuted."""
    if control != "permuted_targets":
        return u_train
    perm = streams.generator(ctx.study_id, ctx.context_id, "train", "decoder", 0, PERMUTED_TARGETS_PURPOSE,
                             TASK_INDEX[task], time_index).permutation(u_train.shape[0])
    return u_train[perm]


def simulation_key(condition: str, control: str) -> tuple:
    """Which trajectory a unit needs: 'permuted_targets' uses EXACTLY the states of its condition without
    control, so it never integrates again (plan 13: one trajectory per context, split and coupling)."""
    return condition, ("none" if control == "permuted_targets" else control)


def initial_state_key(ctx: ContextSpec, prep: Dict, condition: str, control: str, dt: Optional[float] = None) -> tuple:
    """Content address of a trajectory: condition, dt and the SHA-256 of the initial states of all splits.
    Units with bit-identical inputs (e.g. 'reset' and 'zero_impulse', both phi * 1) integrate once; if the
    encoding ever made them differ, they would get different keys automatically."""
    import hashlib
    from experiments.lantern_reconstruction.encoding import initial_state

    a = streams.defaults()["content"]["impulse_rad"]
    h = hashlib.sha256()
    for s in SPLITS:
        b = prep["batches"][s]
        h.update(np.ascontiguousarray(initial_state(ctx, b.u, b.phi, a, simulation_key(condition, control)[1])).tobytes())
    return condition, dt, h.hexdigest()


def iter_cells(ctx: ContextSpec, prep: Dict, g: float, condition: str, control: str, tasks: Sequence[str],
               dt: Optional[float] = None, keep_states: Optional[Dict] = None, scorer=None, state_cache: Optional[Dict] = None):
    """One trajectory per split for (condition, control), then per (task, time) the fitted, cell-bound
    decoder and its test result. Features ONLY via observation.observe(). scorer(model, cell, X_test, U_test)
    replaces plain scoring (runs.py: persist the model, then score with integrity checks). state_cache
    (dict) reuses trajectories across units of the same context and simulation key."""
    d = streams.defaults()
    dt_used = d["integration"]["dt"] if dt is None else float(dt)
    sim_control = simulation_key(condition, control)[1]
    batches, specs = prep["batches"], prep["specs"]
    key = initial_state_key(ctx, prep, condition, control, dt) if state_cache is not None else None
    if key is not None and key in state_cache:
        states = state_cache[key]
    else:
        states = {s: episodes.simulate(ctx, batches[s], prep["mats"][condition], g, sim_control, dt=dt) for s in SPLITS}
        if key is not None:
            state_cache[key] = states
    if keep_states is not None:
        keep_states[condition] = states
    for task in tasks:
        for k, tau in enumerate(float(t) for t in d["time_grid"]):
            X = {s: observation.observe(ctx, specs[task], states[s][:, k], batches[s].eps[:, k]) for s in SPLITS}
            model = fit_ridge(specs[task], X["train"], training_targets(ctx, batches["train"].u, control, task, k), X["val"], batches["val"].u,
                              provenance={"study_id": ctx.study_id, "context_id": ctx.context_id, "condition": condition,
                                          "task": task, "time": tau, "control": control, "dt": dt_used,
                                          "context_fingerprint": fingerprint(ctx), "config_sha256": streams.config_sha256()})
            check_decoder_for(model, ctx, task, condition=condition, time=tau, control=control, dt=dt_used)
            cell = {"condition": condition, "control": control, "task": task, "time": tau, "time_index": k, "dt": dt_used}
            res = score_cell(model, X["test"], batches["test"].u) if scorer is None else scorer(model, cell, X["test"], batches["test"].u)
            yield {**cell, "model": model, "result": res}


def run_context(ctx: ContextSpec, C_lantern: np.ndarray, g: float, *, sizes: Optional[Dict[str, int]] = None,
                conditions: Sequence[str] = episodes.CONDITIONS, tasks: Sequence[str] = TASKS,
                control: str = "none", dt: Optional[float] = None, proposals: Optional[int] = None,
                keep_states: bool = False, keep_models: bool = False, keep_predictions: bool = False) -> Dict:
    check_context(ctx)
    d = streams.defaults()
    if ctx.study_id != d["development_study_id"]:
        raise ValueError("runner.run_context is development-only (no research run before the LR6 freeze and a release)")
    sizes = check_selection(sizes, conditions, tasks, control)
    prep = prepare_context(ctx, C_lantern, sizes, proposals)
    out = {"study_id": ctx.study_id, "context_id": ctx.context_id, "context_fingerprint": fingerprint(ctx),
           "config_sha256": streams.config_sha256(), "control": control, "dt": d["integration"]["dt"] if dt is None else float(dt),
           "sizes": sizes, "times": [float(t) for t in d["time_grid"]], "surrogate_report": prep["surrogate_report"],
           "cells": {}, "states": {}, "models": {}, "predictions": {}}
    for cond in conditions:
        acc = {}
        for c in iter_cells(ctx, prep, g, cond, control, tasks, dt, out["states"] if keep_states else None):
            a = acc.setdefault(c["task"], {"G": {}, "S": {}, "lambda": {}, "n_raw_outside_unit_box": {}})
            tau, res = c["time"], c["result"]
            a["G"][tau], a["S"][tau], a["lambda"][tau], a["n_raw_outside_unit_box"][tau] = res["G"], res["S"], c["model"].lam, res["n_raw_outside_unit_box"]
            if keep_models:
                out["models"][(cond, c["task"], tau)] = c["model"]
            if keep_predictions:
                out["predictions"][(cond, c["task"], tau)] = res["projected"]
        for task, a in acc.items():
            out["cells"][(cond, task)] = {**a, "A": curve_aggregate(a["G"])}
    return out


ALARM_PERMUTATIONS = 9999


def alarm_inputs(per_context: Dict[int, Dict[str, tuple]], study_id: int, n_perm: int = ALARM_PERMUTATIONS) -> Dict[str, Dict]:
    """Permutation result of every named control cell from the projected test predictions and targets of
    each context: per_context[context_id][cell_name] = (projected predictions, test targets). One stream
    per cell (protocol/control_alarms.json); the output feeds metrics.control_alarms (G AND p together).

    B is the protocol's 9999 and nothing else: the smallest Holm p over 12 cells is 12 / (B + 1), so with
    B = 999 (0.012) the alarm could NEVER fire at 0.01 -- a silently powerless control (found in LR5 tests)."""
    from experiments.lantern_reconstruction.metrics import control_alarm_cells, permutation_gain_test

    if n_perm != ALARM_PERMUTATIONS or isinstance(n_perm, (bool, np.bool_)):
        raise ValueError(f"the control alarm uses exactly B = {ALARM_PERMUTATIONS} permutations (protocol/control_alarms.json)")
    names = control_alarm_cells()
    out = {}
    for idx, name in enumerate(names):
        rng = streams.generator(study_id, 0, "test", "decoder", 0, ALARM_PURPOSE, idx)
        r = permutation_gain_test({cid: per_context[cid][name] for cid in sorted(per_context)}, rng, n_perm)
        out[name] = {"G": r["observed_mean_G"], "p": r["p"], "b": r["b"], "B": r["B"]}
    return out
