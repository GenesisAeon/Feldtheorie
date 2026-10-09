"""LR5 mutation campaign (plan section 15: at least the 18 plan mutants, each with an executed proof; plus the
LR5 interruption/manipulation mutants). Each mutant changes production code in place, runs the responsible
test files (stop at the first failure) and restores the file byte-exactly. Results:
lr5/lr5_mutation_campaign.json (+ .yaml). Survivors and equivalent mutants are listed separately.

    python experiments/lantern_reconstruction/tools/lr5_mutation_campaign.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
T = "experiments/lantern_reconstruction/tests/"
LR1, LR2, LR3 = [T + "test_lr1.py"], [T + "test_lr2.py", T + "test_lr2_rk4.py"], [T + "test_lr3.py", T + "test_lr3_nachreview.py"]
LR4, ALARM, RUNS = [T + "test_lr4.py", T + "test_lr4_review.py"], [T + "test_lr5_alarms.py"], [T + "test_lr5_runs.py"]
# a mutant changes the code identity: the two tests bound to it (candidate binding, real candidate accepted)
# would kill EVERY mutant trivially, so they are deselected; killed_by is checked per mutant
L6 = [T + "test_lr6.py", "--deselect", T + "test_lr6.py::test_candidate_is_bound_to_the_current_code",
      "--deselect", T + "test_lr6.py::test_r4_real_candidate_accepted_in_its_own_environment"]
SNAP = '__import__("experiments.lantern_reconstruction.registry_adapter", fromlist=["x"]).load_verified_snapshot()'
ENC = '__import__("experiments.lantern_reconstruction.encoding", fromlist=["x"])'

PLAN = [
    ("1", "YAML order emitted as sorted order", "registry_adapter.py", 'ids = [r["id"] for r in rows]', 'ids = sorted(r["id"] for r in rows)', LR1),
    ("3", "sine argument reversed", "dynamics.py", "diff = theta[:, None, :] - theta[:, :, None]", "diff = theta[:, :, None] - theta[:, None, :]", LR2),
    ("4", "g applied twice", "dynamics.py", 'return omega + g * np.einsum("ij,bij->bi", C, np.sin(diff))',
     'return omega + g * g * np.einsum("ij,bij->bi", C, np.sin(diff))', LR2),
    ("5", "theta_threshold overwrites the phase", "encoding.py", "base = np.repeat(phi[:, None], N, axis=1)",
     f'base = np.repeat(phi[:, None], N, axis=1) + np.asarray({SNAP}.arrays["theta_threshold"])', LR3),
    ("7", "target-dependent frequency", "episodes.py", "dyn.integrate_rk4(theta0[s:s + chunk], C, ctx.omega_array(), g,",
     "dyn.integrate_rk4(theta0[s:s + chunk], C, ctx.omega_array() + 0.05 * float(batch.u[s, 0]), g,", LR3),
    ("8", "write again during the pause", "episodes.py", "steps[-1], steps), (1, 0, 2))\n    return out",
     f"steps[-1], steps), (1, 0, 2))\n        out[s:s + chunk, 1:] += 0.35 * (batch.u[s:s + chunk] @ {ENC}.write_matrix(ctx).T)[:, None, :]\n    return out", LR3),
    ("9", "written reference node allowed in B", "observation.py", "    if spec.reference in ctx.write_nodes:\n        raise", "    if False:\n        raise", LR3),
    ("10", "source-node feature in B", "observation.py", 'spec = ObservationSpec("B", tuple(ctx.read_nodes[:-1]), ctx.reference)',
     'spec = ObservationSpec("B", tuple(ctx.read_nodes[:-2]) + (ctx.write_nodes[0],), ctx.reference)', LR3),
    ("11", "standardisation fitted beyond the training split (fit never sees test: train+val)", "training.py",
     "mean, scale = standardisation(Xtr)", "mean, scale = standardisation(np.vstack([Xtr, Xva]))", LR4),
    ("12-analog", "model selection on the test split (Ridge analogue of plan mutant 12)", "runner.py",
     'X["val"], batches["val"].u,', 'X["test"], batches["test"].u,', LR4),
    ("13", "lambda convention without the factor N", "training.py", "s ** 2 + N * lam", "s ** 2 + lam", LR4),
    ("14", "negative G discarded (clipped to 0)", "metrics.py", '"G": float(3.0 * np.mean(loss_zero - loss))',
     '"G": max(0.0, float(3.0 * np.mean(loss_zero - loss)))', LR4),
    ("15", "episodes counted as independent contexts", "metrics.py",
     '    if not isinstance(values, Mapping):\n        raise ValueError("inference needs ONE value per context: a mapping context_id -> value")\n',
     "    if not isinstance(values, Mapping):\n        values = dict(enumerate(values))\n", LR4),
    ("16a", "missing grid cell replaced by zero (curve)", "metrics.py",
     '    if keys != grid or len(G_by_time) != len(grid):\n        raise ValueError(f"the curve needs exactly the grid times {grid} (got {keys}); a missing cell is not zero")\n    g = np.array([G_by_time[k] for k in grid], dtype=np.float64)',
     "    g = np.array([G_by_time.get(k, 0.0) for k in grid], dtype=np.float64)", LR4),
    ("16b", "missing grid cell ignored (release gate)", "release.py", '            problems.append(f"missing cell {name}")\n', "", RUNS),
    ("17", "release despite a failed reset control", "release.py",
     "    if failed_structure or len(structure) != len(grid[\"contexts\"]):", "    if False:", RUNS),
    ("18a", "resume with changed code/configuration/seed", "runs.py", "    if diffs:\n        raise ResumeRefused", "    if False:\n        raise ResumeRefused", RUNS),
    ("18b", "resume adopts a different (orphan) model", "runs.py", "        if artifacts.identity(meta) != ident:", "        if False:", RUNS),
]
NOT_APPLICABLE = {
    "2": "only C permuted, not E/omega/observation: a property of an invariance TEST, not of production code; the detection is the "
         "executed test test_lr3::test_joint_permutation_of_all_node_objects_keeps_the_features (it also shows that "
         "permuting only C changes the features) -- run below as a detection check",
    "6": "process noise with dt instead of sqrt(dt): the SDE module comes only in LR9 (plan: not_applicable before LR9)",
    "12": "best MLP initialisation chosen by test MSE: the optional MLP is not implemented (LR6 decision); the Ridge analogue 12-analog is executed",
}
LR5 = [
    ("L1", "artifact overwrite allowed", "artifacts.py", "        os.link(tmp, path)", "        os.replace(tmp, path)", RUNS),
    ("L2", "existence check before writing removed", "artifacts.py",
     '    if path.exists():\n        raise FileExistsError(f"{path} exists already (artifacts are never overwritten)")\n', "", RUNS),
    ("L3", "model integrity after evaluation unchecked", "artifacts.py", '    if model_identity(model) != expected_identity:\n        raise IntegrityError("model changed during evaluation")',
     '    if False:\n        raise IntegrityError("model changed during evaluation")', RUNS),
    ("L4", "record scores not recomputed", "runs.py", "        raise IntegrityError(f\"scores of {cell_dir_name(c)} do not follow", "        pass  # (f\"scores of {cell_dir_name(c)} do not follow", RUNS),
    ("L5", "structure record not recomputed", "release.py", "        if {k: s[k] for k in again} != again:", "        if False:", RUNS),
    ("L6", "study lock not exclusive", "runs.py", "fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)", "fd = os.open(self.path, os.O_CREAT | os.O_WRONLY)", RUNS),
    ("L7", "status transitions unchecked", "runs.py", "    if new not in RUN_STATES or (cur is not None and new not in TRANSITIONS[cur]):", "    if new not in RUN_STATES:", RUNS),
    ("L8", "run.json identity not checked", "runs.py", '    if run.get("schema") != RUN_SCHEMA or run_identity(run) != run.get("run_identity"):', '    if run.get("schema") != RUN_SCHEMA:', RUNS),
    ("L9", "foreign record accepted (cell binding off)", "runs.py",
     '    if rec.get("schema") != RECORD_SCHEMA or rec.get("run_identity") != run["run_identity"] or rec.get("cell") != expected_cell:',
     '    if rec.get("schema") != RECORD_SCHEMA:', RUNS),
    ("L10", "cells outside the grid ignored", "release.py", '        problems.append(f"cells outside the grid: {sorted(present - expected_dirs)}")', "        pass", RUNS),
    ("A1a", "positive alarm without the G > 0 condition (p-only)", "metrics.py", '"positive_spurious_success": g > 0 and a <= alpha', '"positive_spurious_success": a <= alpha', ALARM),
    ("A1b", "Holm over a subset only (the positive cells)", "metrics.py", "    adj = holm(p)\n", "    adj = [min(1.0, x * max(1, sum(gg > 0 for gg in G))) for x in p]\n", ALARM),
    ("A1c", "dependence alarm merged into the positive alarm", "metrics.py", '"target_dependence": a <= alpha}', '"target_dependence": g > 0 and a <= alpha}', ALARM),
    ("A1d", "control alarm accepts a missing cell", "metrics.py", "    if not isinstance(cells, Mapping) or set(cells) != set(names) or len(cells) != len(names):",
     "    if not isinstance(cells, Mapping) or not set(cells) <= set(names):", ALARM),
    ("A1e", "permuted-target control trains on the real targets", "runner.py", '    if control != "permuted_targets":\n        return u_train', "    if True:\n        return u_train", ALARM),
    ("A1f", "alarm with too few permutations (B = 999 allowed)", "runner.py", "    if n_perm != ALARM_PERMUTATIONS or isinstance(n_perm, (bool, np.bool_)):", "    if isinstance(n_perm, (bool, np.bool_)):", ALARM),
]


REVIEW_LR5 = [   # guards added after REVIEW_LR5 (R1-R4); responsible tests: test_lr5_review.py
    ("R1a", "execute accepts status running", "runs.py", '    if cur == "running":\n        raise ResumeRefused("run status is running',
     '    if False:\n        raise ResumeRefused("run status is running', [T + "test_lr5_review.py"]),
    ("R1b", "recover does not check whether the process is alive", "runs.py", "    if alive is not False:\n        raise ResumeRefused(f\"process",
     "    if False:\n        raise ResumeRefused(f\"process", [T + "test_lr5_review.py"]),
    ("R1c", "recover ignores the host", "runs.py", '    if last.get("host") != platform.node():', "    if False:", [T + "test_lr5_review.py"]),
    ("R1d", "unexpected exception leaves status running", "runs.py",
     '        except Exception as e:                              # any other failure: a defined, resumable state\n            set_status(log, "interrupted", f"unexpected {type(e).__name__}: {e}")\n            raise\n',
     "", [T + "test_lr5_review.py"]),
    ("R1e", "unparsable log lines silently skipped", "runs.py",
     '                if e.get("event") != "log_line_truncated":\n                    raise IntegrityError', '                if False:\n                    raise IntegrityError', [T + "test_lr5_review.py"]),
    ("R2a", "training/validation sizes not bound to the run", "runs.py", "    if (model.n_train, model.n_val) != (sizes[\"train\"], sizes[\"val\"]):", "    if False:", [T + "test_lr5_review.py"]),
    ("R2b", "model software not bound to the run", "runs.py", '    if (model.software.get("python"), model.software.get("numpy")) != (sw["python"], sw["numpy"]):', "    if False:", [T + "test_lr5_review.py"]),
    ("R2c", "sizes checked only on read, not before writing", "runs.py", "    check_model_against_run(model, run, cell_dir_name(c))           # also before anything is written\n", "", [T + "test_lr5_review.py"]),
    ("R3", "software not compared on resume", "runs.py", '    if cur["software"] != run["software"]:', "    if False:", [T + "test_lr5_review.py"]),
    ("R4a", "lone NPZ not compared", "runs.py", '        if _npz_identities(folder / "model.npz", f"orphan model.npz in {folder.name}") != expected["arrays"]:', "        if False:", [T + "test_lr5_review.py"]),
    ("R4b", "unreadable NPZ accepted", "runs.py", '        raise IntegrityError(f"{where}: unreadable NPZ', '        return {}  # (f"{where}: unreadable NPZ', [T + "test_lr5_review.py"]),
]
FOLLOWUP_B9C405B = [   # review of b9c405b: F1 recovery writes only after the read-only diagnosis; F2 CI selection
    ("F1a", "log repaired before the owner check (the reviewed order)", "runs.py",
     '    diag = _recovery_diagnosis(run, log)                    # READ-ONLY',
     '    log.acknowledge_truncation()\n    diag = _recovery_diagnosis(run, log)                    # READ-ONLY', [T + "test_lr5_review.py"]),
    ("F1b", "recovery guard not exclusive", "runs.py", "        fd = os.open(guard, os.O_CREAT | os.O_EXCL | os.O_WRONLY)",
     "        fd = os.open(guard, os.O_CREAT | os.O_WRONLY)", [T + "test_lr5_review.py"]),
    ("F1c", "no re-check under the recovery guard", "runs.py", "        if _recovery_diagnosis(run, log) != diag:", "        if False:", [T + "test_lr5_review.py"]),
    ("F2", "workflow without test_lr5_review.py", "../../.github/workflows/lantern-reconstruction.yml",
     "          experiments/lantern_reconstruction/tests/test_lr5_review.py\n", "", [T + "test_lr5_alarms.py"]),
    ("LF", "event log written in text mode (CRLF on Windows)", "runs.py", '        with open(self.path, "ab") as f:\n            f.write(json.dumps(rec, sort_keys=True, ensure_ascii=False, allow_nan=False).encode("utf-8") + b"\\n")',
     '        with open(self.path, "a", encoding="utf-8") as f:\n            f.write(json.dumps(rec, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\\n")', [T + "test_lr5_review.py"]),
]


NACHREVIEW_9B52D95 = [   # Astra's re-review of 9b52d95: N1 log framing, N2 shared administration lock
    ("N1", "valid JSON without LF treated as a clean log end", "runs.py",
     '            events.append(e)                                   # a valid event stays an event\n            return events, {"kind": "unterminated_event", **info}',
     '            events.append(e)                                   # a valid event stays an event\n            return events, None', [T + "test_lr5_review.py"]),
    ("N2a", "normal StudyLock acquisition bypasses the administration lock", "runs.py",
     '            with AdminLock(self.path, f"start {self.run_id}"):\n                self._create()',
     '            self._create()', [T + "test_lr5_review.py"]),
    ("N2b", "administration lock not exclusive", "runs.py",
     '            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)\n        except FileExistsError:\n            raise LockError(f"administration',
     '            fd = os.open(self.path, os.O_CREAT | os.O_WRONLY)\n        except FileExistsError:\n            raise LockError(f"administration', [T + "test_lr5_review.py"]),
    ("N2c", "no re-diagnosis under the administration lock", "runs.py", "        if _recovery_diagnosis(run, log) != diag:           # re-check under the administration lock",
     "        if False:", [T + "test_lr5_review.py"]),
]


LR6 = [   # LR6: research mode gated by the freeze; study evaluation only for interpretable research runs
    ("S1", "freeze status not checked", "runs.py", '    if freeze.get("schema") != FREEZE_SCHEMA or freeze.get("status") != "frozen":', "    if False:", [T + "test_lr6.py"]),
    ("S2", "approval not required", "runs.py", '    if not isinstance(freeze.get("approved_by"), list) or not freeze["approved_by"]:', "    if False:", [T + "test_lr6.py"]),
    ("S3", "freeze not bound to the candidate bytes", "runs.py", '    if freeze.get("candidate_sha256") != artifacts.sha256(cand_bytes):', "    if False:", [T + "test_lr6.py"]),
    ("S4", "frozen code identity not compared", "runs.py", '    if cand.get("code_identity") != current or freeze.get("code_identity") != current:', "    if False:", [T + "test_lr6.py"]),
    ("S5", "research may use the development study", "runs.py", '    if sid == streams.defaults()["development_study_id"]:', "    if False:", [T + "test_lr6.py"]),
    ("S6", "execute does not re-check the freeze", "runs.py", '    if run["kind"] == "research":                          # the freeze must still be valid',
     '    if False:                          # the freeze must still be valid', [T + "test_lr6.py"]),
    ("S7", "hypotheses evaluated although not interpretable", "release.py", "    if not interpretable:\n        return {\"status\": \"not_evaluated\", \"reason\": \"research run",
     "    if False:\n        return {\"status\": \"not_evaluated\", \"reason\": \"research run", [T + "test_lr6.py"]),
    ("S8", "allowed statements swapped", "release.py", '    (True, False): "distributed readability shown;', '    (False, True): "distributed readability shown;', [T + "test_lr6.py"]),
]


CONTROL_V2 = [   # control-alarm protocol v2 (decision 2026-10-09): permuted validation targets, refit null
    ("V1", "validation targets not permuted in the permuted-target control", "runner.py",
     '    if control != "permuted_targets":\n        return u_val', "    if True:\n        return u_val", [T + "test_lr6.py"]),
    ("V2", "permuted-target cells silently fall back to the fixed-prediction null", "runner.py",
     '        if name.startswith("permuted_targets|"):', '        if name.startswith("permuted_targets|") and nulls is not None:', [T + "test_lr5_alarms.py", T + "test_lr6.py"]),
    # V3/V5 targets follow the code of the LR6 review fix (tie rule, refit-path check); re-run, history kept
    ("V3", "refit-null ties not counted", "runner.py", "            b = upper_tail_count(np.mean(arrs, axis=0), obs)", "            b = int(np.sum(np.mean(arrs, axis=0) > obs))", L6),
    ("V4", "missing refit null accepted on read", "runs.py",
     '        if "null" not in rec:\n            raise IntegrityError(f"{cell_dir_name(c)} lacks its refit null', '        if False:\n            raise IntegrityError(f"{cell_dir_name(c)} lacks its refit null', [T + "test_lr5_runs.py"]),
    ("V5", "refit null presence not checked before writing", "runs.py",
     '    if (null_G is not None) != runner.needs_refit_null(c["control"], c["task"], c["time"]) or (null_G is None) != (null_meta is None):',
     "    if False:", [T + "test_lr5_runs.py"]),
    ("V6", "orphan refit null not compared", "runs.py",
     '        if null_ids is None or _npz_identities(folder / "null.npz", f"orphan null in {folder.name}") != null_ids:', "        if False:", [T + "test_lr5_runs.py"]),
]


REVIEW_LR6_29AF52F = [   # review LANTERN_LR6_REVIEW_29af52f: R1 software binding, R2 ties, R3 null provenance
    ("T1", "refit null compared exactly again (the reviewed state)", "runner.py", "            b = upper_tail_count(np.mean(arrs, axis=0), obs)",
     "            b = int(np.sum(np.mean(arrs, axis=0) >= obs))", L6),
    ("T2", "fixed-prediction null compared exactly", "metrics.py",
     "    b = upper_tail_count([stat([rng.permutation(len(d[1])) for d in data]) for _ in range(n_perm)], observed)",
     "    b = sum(stat([rng.permutation(len(d[1])) for d in data]) >= observed for _ in range(n_perm))", L6),
    ("T3", "tie tolerance applied anti-conservatively", "metrics.py", "    return int(np.sum(a >= observed - tol))",
     "    return int(np.sum(a >= observed + tol))", L6),
    ("T4", "protocol tie tolerance ignored by default", "metrics.py", "    tol = tie_tolerance() if tol is None else float(tol)",
     "    tol = 0.0 if tol is None else float(tol)", L6),
    ("T5", "refit-path check not enforced", "runner.py", "    if not dev <= tol:\n        raise ValueError(f\"refit-path check failed",
     "    if False:\n        raise ValueError(f\"refit-path check failed", L6),
    ("T6", "refit-path check compares the refit with itself", "runner.py", '    g_fit = float(score_cell(model, X["test"], u["test"])["G"])',
     "    g_fit = g_refit", L6),
    ("P1", "software not compared at the research start", "runs.py", '    problems += software_problems(cand.get("software"))', "    pass", L6),
    ("P2", "incomplete software block accepted", "runs.py",
     "            not all(isinstance(frozen[k], str) and frozen[k] for k in SOFTWARE_KEYS):", "            False:", L6),
    ("N1", "null provenance not checked on read", "runs.py", "        _check_null_binding(rec, run, c, ctx)", "        pass", L6),
    ("N2", "expected provenance taken from the null record itself", "runs.py",
     '    expected = null_provenance(run, c, ctx, rec["model"]["model_identity"], rec["predictions"]["arrays"]["targets"])',
     '    expected = nul.get("provenance")', L6),
    ("N3", "refit-path check fields not verified on read", "runs.py",
     '        raise IntegrityError(f"refit null of {cell_dir_name(c)}: refit-path check missing, inconsistent or not met")', "        pass", L6),
    ("N4", "resume ignores the recorded null provenance and inputs", "runs.py",
     "                or (null_extra is not None and {k: old_null.get(k) for k in null_extra} != null_extra)):", "                ):", L6),
    ("N5", "persist accepts a path check made for another observed gain", "runs.py",
     '        if null_meta.get("observed_G_fit_path") != res["G"]:', "        if False:", L6),
]


def run_mutant(mid, desc, fname, old, new, tests, env):
    p = HERE / fname
    orig = p.read_bytes()
    text = orig.decode("utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    o, n = old.replace("\n", nl), new.replace("\n", nl)
    if text.count(o) != 1:
        return {"id": mid, "description": desc, "file": fname, "result": f"TARGET NOT UNIQUE ({text.count(o)})"}
    t0 = time.perf_counter()
    try:
        p.write_bytes(text.replace(o, n).encode("utf-8"))
        r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", "--color=no", "-rf", *tests],
                           cwd=ROOT, env=env, capture_output=True, text=True)
    finally:
        p.write_bytes(orig)
        assert p.read_bytes() == orig, f"{fname} not restored"
    failed = [re.sub(r" - .*", "", l[7:]) for l in r.stdout.splitlines() if l.startswith(("FAILED", "ERROR"))]
    return {"id": mid, "description": desc, "file": fname, "tests": [t.split("/")[-1] for t in tests],
            "result": "killed" if r.returncode else "SURVIVED", "killed_by": failed[:3], "seconds": round(time.perf_counter() - t0, 1)}


def rerun(ids):
    """Re-run selected mutants after a test fix; the earlier result is kept in 'history' (nothing silently replaced)."""
    env = dict(os.environ, PYTHONPATH=".", PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    js = HERE / "lr5" / "lr5_mutation_campaign.json"
    out = json.loads(js.read_text(encoding="utf-8"))
    for group, defs in (("plan_mutants", PLAN), ("lr5_mutants", LR5), ("review_lr5_mutants", REVIEW_LR5),
                        ("followup_b9c405b_mutants", FOLLOWUP_B9C405B), ("nachreview_9b52d95_mutants", NACHREVIEW_9B52D95),
                        ("lr6_mutants", LR6), ("control_v2_mutants", CONTROL_V2),
                        ("review_lr6_29af52f_mutants", REVIEW_LR6_29AF52F)):
        for i, m in enumerate(out.get(group, [])):
            if m["id"] in ids:
                new = run_mutant(*next(d for d in defs if d[0] == m["id"]), env)
                new["history"] = m.get("history", []) + [{k: v for k, v in m.items() if k != "history"}]
                out[group][i] = new
                print(new["id"], new["result"], new.get("killed_by", [])[:1], flush=True)
    return out


def main():
    env = dict(os.environ, PYTHONPATH=".", PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    if len(sys.argv) > 2 and sys.argv[1] == "--only":
        return finish(rerun(set(sys.argv[2].split(","))))
    if len(sys.argv) > 1 and sys.argv[1] == "--review-lr6-29af52f":
        js = HERE / "lr5" / "lr5_mutation_campaign.json"
        out = json.loads(js.read_text(encoding="utf-8"))
        out["review_lr6_29af52f_mutants"] = []
        for m in REVIEW_LR6_29AF52F:
            out["review_lr6_29af52f_mutants"].append(run_mutant(*m, env))
            r = out["review_lr6_29af52f_mutants"][-1]
            print(r["id"], r["result"], r.get("killed_by", [])[:1], flush=True)
        return finish(out)
    if len(sys.argv) > 1 and sys.argv[1] == "--control-v2":
        js = HERE / "lr5" / "lr5_mutation_campaign.json"
        out = json.loads(js.read_text(encoding="utf-8"))
        out["control_v2_mutants"] = []
        for m in CONTROL_V2:
            out["control_v2_mutants"].append(run_mutant(*m, env))
            r = out["control_v2_mutants"][-1]
            print(r["id"], r["result"], r.get("killed_by", [])[:1], flush=True)
        return finish(out)
    if len(sys.argv) > 1 and sys.argv[1] == "--lr6":
        js = HERE / "lr5" / "lr5_mutation_campaign.json"
        out = json.loads(js.read_text(encoding="utf-8"))
        out["lr6_mutants"] = []
        for m in LR6:
            out["lr6_mutants"].append(run_mutant(*m, env))
            r = out["lr6_mutants"][-1]
            print(r["id"], r["result"], r.get("killed_by", [])[:1], flush=True)
        return finish(out)
    if len(sys.argv) > 1 and sys.argv[1] == "--nachreview-9b52d95":
        js = HERE / "lr5" / "lr5_mutation_campaign.json"
        out = json.loads(js.read_text(encoding="utf-8"))
        out["nachreview_9b52d95_mutants"] = []
        for m in NACHREVIEW_9B52D95:
            out["nachreview_9b52d95_mutants"].append(run_mutant(*m, env))
            r = out["nachreview_9b52d95_mutants"][-1]
            print(r["id"], r["result"], r.get("killed_by", [])[:1], flush=True)
        return finish(out)
    if len(sys.argv) > 1 and sys.argv[1] == "--followup-b9c405b":
        js = HERE / "lr5" / "lr5_mutation_campaign.json"
        out = json.loads(js.read_text(encoding="utf-8"))
        out["followup_b9c405b_mutants"] = []
        for m in FOLLOWUP_B9C405B:
            out["followup_b9c405b_mutants"].append(run_mutant(*m, env))
            r = out["followup_b9c405b_mutants"][-1]
            print(r["id"], r["result"], r.get("killed_by", [])[:1], flush=True)
        return finish(out)
    if len(sys.argv) > 1 and sys.argv[1] == "--review-lr5":
        js = HERE / "lr5" / "lr5_mutation_campaign.json"
        out = json.loads(js.read_text(encoding="utf-8"))
        out["review_lr5_mutants"] = []
        for m in REVIEW_LR5:
            out["review_lr5_mutants"].append(run_mutant(*m, env))
            print(out["review_lr5_mutants"][-1]["id"], out["review_lr5_mutants"][-1]["result"], out["review_lr5_mutants"][-1].get("killed_by", [])[:1], flush=True)
        return finish(out)
    out = {"schema": "lantern-lr5-mutation-campaign-v1", "plan_mutants": [], "not_applicable": NOT_APPLICABLE, "lr5_mutants": []}
    for m in PLAN:
        out["plan_mutants"].append(run_mutant(*m, env))
        print(out["plan_mutants"][-1]["id"], out["plan_mutants"][-1]["result"], flush=True)
    det = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "--color=no", T + "test_lr3.py", "-k", "joint_permutation"],
                         cwd=ROOT, env=env, capture_output=True, text=True)
    out["plan_mutant_2_detection_test"] = {"command": "pytest test_lr3.py -k joint_permutation", "passed": det.returncode == 0,
                                           "summary": det.stdout.strip().splitlines()[-1] if det.stdout.strip() else ""}
    for m in LR5:
        out["lr5_mutants"].append(run_mutant(*m, env))
        print(out["lr5_mutants"][-1]["id"], out["lr5_mutants"][-1]["result"], flush=True)
    return finish(out)


EQUIVALENT = {
    "L2": "removing the early existence check is equivalent in outcome: os.link still refuses an existing name "
          "(FileExistsError, nothing overwritten); the check only avoids writing a temp file. Confirmed by the "
          "race test and the overwrite test both passing under this mutant.",
    "R4b": "returning {} for an unreadable NPZ instead of raising is equivalent in outcome: {} never equals the "
           "expected array identities, so the orphan is still rejected as an integrity failure (only the message "
           "differs); test_r4_other_wrong_lone_npz_files[garbage_bytes] passes under the mutant for that reason.",
}


def finish(out):
    out["equivalent"] = {k: v for k, v in EQUIVALENT.items()}
    allm = (out["plan_mutants"] + out["lr5_mutants"] + out.get("review_lr5_mutants", []) + out.get("followup_b9c405b_mutants", [])
            + out.get("nachreview_9b52d95_mutants", []) + out.get("lr6_mutants", []) + out.get("control_v2_mutants", [])
            + out.get("review_lr6_29af52f_mutants", []))
    out["summary"] = {"executed": len(allm), "killed": sum(m["result"] == "killed" for m in allm),
                      "survived": [m["id"] for m in allm if m["result"] == "SURVIVED" and m["id"] not in EQUIVALENT],
                      "equivalent": [m["id"] for m in allm if m["result"] == "SURVIVED" and m["id"] in EQUIVALENT],
                      "first_run_survivors_closed_by_new_tests": sorted(m["id"] for m in allm if m.get("history") and m["result"] == "killed"),
                      "invalid_targets": [m["id"] for m in allm if m["result"].startswith("TARGET")],
                      "not_applicable": sorted(NOT_APPLICABLE)}
    js = HERE / "lr5" / "lr5_mutation_campaign.json"
    js.parent.mkdir(exist_ok=True)
    js.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    import yaml
    js.with_suffix(".yaml").write_text("# YAML twin of lr5_mutation_campaign.json (generated; the JSON is authoritative)\n"
                                       + yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=10 ** 6), encoding="utf-8")
    print(json.dumps(out["summary"], indent=1))
    return 0 if not out["summary"]["survived"] and not out["summary"]["invalid_targets"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
