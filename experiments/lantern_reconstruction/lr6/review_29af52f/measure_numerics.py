"""Development-only numerical diagnosis for R2 (no research data; reads the acceptance run read-only).
1) Acceptance run 2: distance of every null statistic to the observed statistic (refit cells and fixed-prediction cells).
2) Real development contexts: deviation between fit_ridge+scoring and the vectorised refit path, for the cell's own
   permutations (observed) and for sample null draws."""
import json, sys, time
from pathlib import Path
import numpy as np
ROOT = Path("D:/mandala/.worktrees/feldtheorie-lantern-reconstruction")
sys.path.insert(0, str(ROOT))
from experiments.lantern_reconstruction import (artifacts, contexts, decoders, metrics, observation, runner, runs, streams, training)
from experiments.lantern_reconstruction import registry_adapter as ra

RUN = Path("D:/mandala/mandala-memory-results/lantern/runs/lr6-acceptance-20261009T165010Z")
out = {"acceptance_run": RUN.name}
run = runs.load_run(RUN)
grid = run["grid"]
names = metrics.control_alarm_cells()


def cell_of(name, cid):
    ctl, task, tau = name.split("|")
    k = grid["times"].index(float(tau))
    return {"context_id": cid, "condition": "lantern", "control": ctl, "task": task, "time": float(tau), "time_index": k}


def vec_gains(Xtr, Utr, Xva, Uva, Xte, Ute, perms, grid_l=training.LAMBDA_GRID):
    """The vectorised refit body of training.permuted_null_gains with EXPLICIT permutations (copied, unchanged maths)."""
    grid_l = np.array(grid_l)
    mean, scale = training.standardisation(Xtr)
    Xs, Xvs, Xts = (Xtr - mean) / scale, (Xva - mean) / scale, (Xte - mean) / scale
    N = Xs.shape[0]
    xbar, ubar = Xs.mean(axis=0), Utr.mean(axis=0)
    P, s, Qt = np.linalg.svd(Xs - xbar, full_matrices=False)
    Uc = Utr - ubar
    shrink = s[None, :] / (s[None, :] ** 2 + N * grid_l[:, None])
    loss_zero = np.mean(Ute ** 2, axis=1)
    k = len(perms)
    Ucb = np.stack([Uc[pt] for pt, _ in perms]); Uvb = np.stack([Uva[pv] for _, pv in perms])
    PtU = np.matmul(P.T, Ucb)
    W = np.matmul(Qt.T, shrink[None, :, :, None] * PtU[:, None, :, :])
    b = ubar - np.matmul(xbar, W)
    pv = np.clip(np.matmul(Xvs, W) + b[:, :, None, :], -1.0, 1.0)
    mse = np.mean((pv - Uvb[:, None]) ** 2, axis=(2, 3))
    best = np.argmax(np.where(mse == mse.min(axis=1, keepdims=True), grid_l[None, :], -np.inf), axis=1)
    Wsel, bsel = W[np.arange(k), best], b[np.arange(k), best]
    pt = np.clip(np.matmul(Xts, Wsel) + bsel[:, None, :], -1.0, 1.0)
    return 3.0 * np.mean(loss_zero[None, :] - np.mean((pt - Ute[None]) ** 2, axis=2), axis=1)


# 1) acceptance run: distances
acc = {}
for name in names:
    per = {}
    for cid in grid["contexts"]:
        c = cell_of(name, cid)
        folder = RUN / "cells" / runs.cell_dir_name(c)
        rec = json.loads((folder / "record.json").read_text(encoding="utf-8"))
        arr = artifacts.load_arrays_verified(folder, rec["predictions"])
        per[cid] = (arr["projected"], arr["targets"], rec, folder)
    if name.startswith("permuted"):
        nul = np.mean([artifacts.load_arrays_verified(f, r["null"])["null_G"] for _, _, r, f in per.values()], axis=0)
        obs = float(np.mean([metrics.scores(*metrics.episode_losses(p, u))["G"] for p, u, _, _ in per.values()]))
        stats = nul
    else:
        idx = names.index(name)
        rng = streams.generator(grid["study_id"], 0, "test", "decoder", 0, runner.ALARM_PURPOSE, idx)
        data = [(p, u, np.mean(u ** 2, axis=1)) for p, u, _, _ in (per[c] for c in sorted(per))]
        st = lambda perms: float(np.mean([3.0 * np.mean(lz[pi] - np.mean((p - u[pi]) ** 2, axis=1)) for (p, u, lz), pi in zip(data, perms)]))
        obs = st([np.arange(len(d[1])) for d in data])
        stats = np.array([st([rng.permutation(len(d[1])) for d in data]) for _ in range(9999)])
    d = np.abs(stats - obs)
    acc[name] = {"observed": obs, "b_exact": int(np.sum(stats >= obs)), "min_abs_distance": float(d.min()),
                 "n_within_1e-10": int(np.sum(d <= 1e-10)), "n_within_1e-6": int(np.sum(d <= 1e-6)),
                 "null_sd": float(np.std(stats))}
out["acceptance_distances"] = acc

# 2) real development contexts: path deviation
snap = ra.load_verified_snapshot()
C, g = np.array(snap.C), float(snap.structure["g"])
dev = []
t0 = time.time()
for cid in (0, 1, 2, 3):
    ctx = contexts.make_context(grid["study_id"], cid)
    prep = runner.prepare_context(ctx, C, grid["sizes"], grid["proposals"])
    keep = {}
    cells = [c for c in runner.iter_cells(ctx, prep, g, "lantern", "permuted_targets", ("A", "B"), keep_states=keep)
             if runner.needs_refit_null(c["control"], c["task"], c["time"])]
    states = keep["lantern"]
    for c in cells:
        k, task = c["time_index"], c["task"]
        X = {s: observation.observe(ctx, prep["specs"][task], states[s][:, k], prep["batches"][s].eps[:, k]) for s in runner.SPLITS}
        U = {s: prep["batches"][s].u for s in runner.SPLITS}
        pt = streams.generator(ctx.study_id, cid, "train", "decoder", 0, runner.PERMUTED_TARGETS_PURPOSE, runner.TASK_INDEX[task], k).permutation(len(U["train"]))
        pv = streams.generator(ctx.study_id, cid, "val", "decoder", 0, runner.PERMUTED_VAL_PURPOSE, runner.TASK_INDEX[task], k).permutation(len(U["val"]))
        g_model = c["result"]["G"]
        g_same = float(vec_gains(X["train"], U["train"], X["val"], U["val"], X["test"], U["test"], [(pt, pv)])[0])
        # sample null draws: vectorised vs fit_ridge, same permutations
        r = np.random.default_rng(1000 + cid)
        perms = [(r.permutation(len(U["train"])), r.permutation(len(U["val"]))) for _ in range(10)]
        vg = vec_gains(X["train"], U["train"], X["val"], U["val"], X["test"], U["test"], perms)
        fg = []
        for a, bb in perms:
            m = training.fit_ridge(prep["specs"][task], X["train"], U["train"][a], X["val"], U["val"][bb])
            fg.append(metrics.scores(*metrics.episode_losses(metrics.project(decoders.predict(m, X["test"])), U["test"]))["G"])
        # stored null reproducible?
        rec_folder = RUN / "cells" / runs.cell_dir_name({"context_id": cid, "condition": "lantern", "control": "permuted_targets",
                                                         "task": task, "time": c["time"], "time_index": k})
        rec = json.loads((rec_folder / "record.json").read_text(encoding="utf-8"))
        stored = artifacts.load_arrays_verified(rec_folder, rec["null"])["null_G"]
        dev.append({"context": cid, "cell": f"{task}|{c['time']}", "G_model": g_model, "G_same_path": g_same,
                    "observed_path_deviation": abs(g_model - g_same), "sample_null_max_deviation": float(np.max(np.abs(vg - np.array(fg)))),
                    "recorded_G_equal": rec["scores"]["G"] == g_model, "stored_null_bit_identical": bool(np.array_equal(stored, c["null_G"]))})
    print(cid, time.time() - t0, flush=True)
out["development_path_deviation"] = dev
out["max_observed_path_deviation"] = max(x["observed_path_deviation"] for x in dev)
out["max_sample_null_deviation"] = max(x["sample_null_max_deviation"] for x in dev)
p = Path("C:/Users/Privat/.claude/jobs/bc57132d/tmp/lr6review/mine/numerics.json")
p.write_text(json.dumps(out, indent=1))
print(json.dumps({k: out[k] for k in ("acceptance_distances", "max_observed_path_deviation", "max_sample_null_deviation")}, indent=1))
