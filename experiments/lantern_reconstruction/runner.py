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
from experiments.lantern_reconstruction.evaluate import score_cell
from experiments.lantern_reconstruction.metrics import curve_aggregate
from experiments.lantern_reconstruction.training import fit_ridge

SPLITS = ("train", "val", "test")


def development_sizes() -> Dict[str, int]:
    return dict(streams.defaults()["data_per_context"])


def run_context(ctx: ContextSpec, C_lantern: np.ndarray, g: float, *, sizes: Optional[Dict[str, int]] = None,
                conditions: Sequence[str] = episodes.CONDITIONS, tasks: Sequence[str] = ("A", "B"),
                control: str = "none", dt: Optional[float] = None, proposals: Optional[int] = None,
                keep_states: bool = False, keep_models: bool = False) -> Dict:
    check_context(ctx)
    d = streams.defaults()
    if ctx.study_id != d["development_study_id"]:
        raise ValueError("runner.run_context is development-only (no research run before the LR6 freeze and a release)")
    sizes = development_sizes() if sizes is None else dict(sizes)
    if set(sizes) != set(SPLITS) or any(isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)) or n < 2 for n in sizes.values()):
        raise ValueError("sizes must give an integer >= 2 for exactly train, val and test")
    if not conditions or len(set(conditions)) != len(conditions) or not set(conditions) <= set(episodes.CONDITIONS):
        raise ValueError(f"conditions must be distinct entries of {episodes.CONDITIONS}")
    if not tasks or len(set(tasks)) != len(tasks) or not set(tasks) <= {"A", "B"}:
        raise ValueError("tasks must be distinct entries of ('A', 'B')")
    times = [float(t) for t in d["time_grid"]]
    mats, surrogate_report = episodes.coupling_matrices_with_report(C_lantern, ctx, proposals)
    batches = {s: episodes.make_batch(ctx, s, range(sizes[s])) for s in SPLITS}
    specs = {t: observation.observation_spec(ctx, t) for t in tasks}
    out = {"study_id": ctx.study_id, "context_id": ctx.context_id, "context_fingerprint": fingerprint(ctx),
           "config_sha256": streams.config_sha256(), "control": control, "dt": d["integration"]["dt"] if dt is None else float(dt),
           "sizes": sizes, "times": times, "surrogate_report": surrogate_report, "cells": {}, "states": {}, "models": {}}
    for cond in conditions:
        states = {s: episodes.simulate(ctx, batches[s], mats[cond], g, control, dt=dt) for s in SPLITS}
        if keep_states:
            out["states"][cond] = states
        for task in tasks:
            G, S, lam, outside = {}, {}, {}, {}
            for k, tau in enumerate(times):
                X = {s: observation.observe(ctx, specs[task], states[s][:, k], batches[s].eps[:, k]) for s in SPLITS}
                model = fit_ridge(specs[task], X["train"], batches["train"].u, X["val"], batches["val"].u,
                                  provenance={"study_id": ctx.study_id, "context_id": ctx.context_id, "condition": cond,
                                              "task": task, "time": tau, "control": control, "dt": out["dt"],
                                              "context_fingerprint": out["context_fingerprint"], "config_sha256": out["config_sha256"]})
                res = score_cell(model, X["test"], batches["test"].u)
                G[tau], S[tau], lam[tau], outside[tau] = res["G"], res["S"], model.lam, res["n_raw_outside_unit_box"]
                if keep_models:
                    out["models"][(cond, task, tau)] = model
            out["cells"][(cond, task)] = {"G": G, "S": S, "lambda": lam, "n_raw_outside_unit_box": outside, "A": curve_aggregate(G)}
    return out
