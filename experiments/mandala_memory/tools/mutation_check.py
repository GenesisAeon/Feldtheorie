"""M7: small targeted mutation check -- do the tests catch important errors?

Each mutant replaces one exact snippet in a COPY of the experiment (the
working tree is never modified; its file hashes are checked before/after),
then runs the targeted test files on the copy. Outcome: killed (a test
failed) / survived / invalid (snippet not found exactly once).

    python experiments/mandala_memory/tools/mutation_check.py --out FILE
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
REPO = EXP.parents[1]

MUTANTS = [
    ("pulse_applied_twice", "core.py", "    op.step(one_hot(s, spec.n_inputs))\n    if reset_after_pulse:",
     "    op.step(one_hot(s, spec.n_inputs))\n    op.step(one_hot(s, spec.n_inputs))\n    if reset_after_pulse:", ["test_m1_core.py"]),
    ("readout_one_step_early", "core.py", "    for _ in range(d):\n        op.step(np.zeros(spec.n_inputs))\n    return op.x.copy()",
     "    for _ in range(max(d - 1, 0)):\n        op.step(np.zeros(spec.n_inputs))\n    return op.x.copy()", ["test_m1_core.py"]),
    # retargeted: the first version scaled BOTH matrices identically (equivalent mutant)
    ("float_matrix_not_exact", "core.py", "    g = gamma if isinstance(gamma, Fraction) else Fraction(str(gamma))",
     "    g = float(gamma)", ["test_m1_core.py"]),
    ("restore_ignores_network", "core.py", "        if not (np.array_equal(snap[\"A\"], s.A)", "        if False and not (np.array_equal(snap[\"A\"], s.A)",
     ["test_m1_core.py"]),
    ("noise_depends_on_condition", "data.py", "    Y = np.array(rows) + eps.noise",
     "    Y = np.array(rows) + eps.noise * (1 + 0.1 * float(np.abs(H).sum() != H.shape[0]) + 0.1 * float(np.array(rows).sum() > 0.5))",
     ["test_m2_data.py"]),
    ("tie_break_to_class_1", "data.py", "        return np.where(d1 < d0, 1, 0)       # exact tie -> class 0",
     "        return np.where(d1 <= d0, 1, 0)", ["test_m2_data.py"]),
    ("decoder_standardises", "data.py", "        self.means = np.array([Y[labels == c].mean(axis=0) for c in (0, 1)])",
     "        self._sd = Y.std(axis=0) + 1e-12\n        Y = Y / self._sd\n        self.means = np.array([Y[labels == c].mean(axis=0) for c in (0, 1)])",
     ["test_m2_data.py"]),
    ("adaptation_on_unbalanced_order", "model.py", "    order = np.array([0] * (n // 2) + [1] * (n // 2))",
     "    order = np.array([0] * n)", ["test_m3_model_runner.py"]),
    # retargeted: the default mask already allows every off-diagonal edge, so dropping it was equivalent
    ("adapted_mask_allows_self_loops", "model.py", "    mask = spec.mask.tolist()", "    mask = np.ones((spec.N, spec.N), dtype=int).tolist()",
     ["test_m3_model_runner.py"]),
    ("c_drive_guard_removed", "runner.py", "    if out_dir.drive.upper().startswith(\"C\"):", "    if False:", ["test_m3_model_runner.py"]),
    ("failed_seed_dropped", "runner.py", "            result[\"failed_seeds\"].append({\"seed\": seed, \"error\": f\"{type(e).__name__}: {e}\"})",
     "            pass", ["test_m3_model_runner.py"]),
    ("primary_pairing_shifted", "evaluate.py", "    diffs = paired_differences(result, \"adapted\", \"frozen\", primary_d)",
     "    _a = [r[\"delays\"][primary_d][\"adapted\"][\"balanced_accuracy\"] for r in result[\"runs\"]]\n"
     "    _f = [r[\"delays\"][primary_d][\"frozen\"][\"balanced_accuracy\"] for r in result[\"runs\"]]\n"
     "    diffs = [x - y for x, y in zip(_a, _f[1:] + _f[:1])]", ["test_m4_evaluate.py"]),
    ("frozen_membrane_not_frozen", "membrane_pilot.py", "FROZEN_GAINS = dict(plasticity=0.0,", "FROZEN_GAINS = dict(plasticity=0.1,",
     ["test_m5_membrane.py"]),
    ("whitelist_bypassed", "serve.py", "        if name is None:                               # fixed whitelist: no paths from the browser",
     "        if name is None:\n            name = route.lstrip('/')\n        if name is None:", ["test_m6_serve.py"]),
    ("bayes_on_max_coordinate", "serve.py", "\"bayes_accuracy_full_observation\": NormalDist().cdf(l2 / (2 * sigma)),",
     "\"bayes_accuracy_full_observation\": NormalDist().cdf(float(np.max(np.abs(a - b))) / (2 * sigma)),", ["test_m6_serve.py"]),
]


def tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.rglob("*.py")):
        h.update(str(p.relative_to(root)).encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def run() -> dict:
    before = tree_hash(EXP)
    results = []
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "OPENBLAS_NUM_THREADS": "2",
           "TMP": r"D:/mandala/.tmp/mandala-memory", "TEMP": r"D:/mandala/.tmp/mandala-memory"}
    base = Path(r"D:/mandala/.tmp/mandala-memory/mutants")
    base.mkdir(parents=True, exist_ok=True)
    for mid, fname, find, repl, targets in MUTANTS:
        work = Path(tempfile.mkdtemp(dir=base))
        try:
            dst = work / "experiments" / "mandala_memory"
            shutil.copytree(EXP, dst, ignore=shutil.ignore_patterns("__pycache__"))
            (work / "experiments" / "__init__.py").write_text('"""copy"""\n', encoding="utf-8")
            (work / "models").mkdir()
            shutil.copy2(REPO / "models" / "adaptive_logistic_membrane.py", work / "models")
            f = dst / fname
            src = f.read_text(encoding="utf-8")
            if src.count(find) != 1:
                results.append({"id": mid, "status": "invalid", "detail": f"snippet found {src.count(find)} times"})
                continue
            f.write_text(src.replace(find, repl), encoding="utf-8")
            cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-x",
                   *[str(dst / "tests" / t) for t in targets], "-k", "not source_unchanged and not loader_does_not"]
            r = subprocess.run(cmd, cwd=work, env={**env, "PYTHONPATH": str(work)}, capture_output=True, text=True, timeout=600)
            last = (r.stdout.strip().splitlines() or [""])[-1]
            results.append({"id": mid, "file": fname, "targets": targets,
                            "status": "killed" if r.returncode != 0 else "survived", "pytest": last})
        finally:
            shutil.rmtree(work, ignore_errors=True)
    after = tree_hash(EXP)
    killed = sum(r["status"] == "killed" for r in results)
    return {"n_mutants": len(results), "killed": killed, "survived": [r["id"] for r in results if r["status"] == "survived"],
            "invalid": [r["id"] for r in results if r["status"] == "invalid"],
            "working_tree_unchanged": before == after, "mutants": results}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    rep = run()
    text = json.dumps(rep, indent=1)
    if a.out:
        a.out.write_text(text + "\n", encoding="utf-8")
    for m in rep["mutants"]:
        print(f"{m['status']:9} {m['id']}")
    print(f"killed {rep['killed']}/{rep['n_mutants']}, survived {rep['survived']}, invalid {rep['invalid']}, "
          f"tree unchanged {rep['working_tree_unchanged']}")
    return 0 if not rep["survived"] and not rep["invalid"] and rep["working_tree_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
