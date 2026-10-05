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
    ("c_drive_guard_removed", "runner.py", "    if is_drive_c(out_dir):", "    if False:", ["test_m3_model_runner.py"]),
    # review R8: the guard must hold on POSIX too, where Path("C:/x").drive is empty
    ("c_drive_guard_not_portable", "core.py", "    if PureWindowsPath(raw).drive.upper().startswith(\"C\"):\n        return True\n",
     "", ["test_m3_model_runner.py"]),
    ("failed_seed_dropped", "runner.py", "            result[\"failed_seeds\"].append({\"seed\": seed, \"error\": f\"{type(e).__name__}: {e}\"})",
     "            pass", ["test_m3_model_runner.py"]),
    ("primary_pairing_shifted", "evaluate.py", "    diffs = paired_differences(result, \"adapted\", \"frozen\", primary_d)",
     "    _a = [r[\"delays\"][primary_d][\"adapted\"][\"balanced_accuracy\"] for r in result[\"runs\"]]\n"
     "    _f = [r[\"delays\"][primary_d][\"frozen\"][\"balanced_accuracy\"] for r in result[\"runs\"]]\n"
     "    diffs = [x - y for x, y in zip(_a, _f[1:] + _f[:1])]", ["test_m4_evaluate.py"]),
    # --- Astra review 2026-10-03 (R1 result identity, R2 inference release) ---
    ("r1_overwrite_instead_of_exclusive", "runner.py", "    write_exclusive(path, json.dumps(result, indent=1, ensure_ascii=False, allow_nan=False) + \"\\n\")",
     "    path.write_text(json.dumps(result, indent=1, ensure_ascii=False, allow_nan=False) + \"\\n\", encoding=\"utf-8\")",
     ["test_m3_model_runner.py"]),
    ("r1_no_execution_id", "runner.py", "    run_id = f\"{protocol_id}--{execution_id}\"", "    run_id = protocol_id",
     ["test_m3_model_runner.py"]),
    ("r1_negative_timeout_accepted", "runner.py", "    if timeout_s is not None and not (timeout_s > 0):", "    if False:",
     ["test_m3_model_runner.py"]),
    ("r2_release_ignores_seed_list", "evaluate.py", "    if executed != declared:\n        reasons.append(\"executed_seeds_differ_from_protocol\")",
     "    if False:\n        reasons.append(\"executed_seeds_differ_from_protocol\")", ["test_m4_evaluate.py"]),
    ("r2_release_ignores_status", "evaluate.py", "    if result.get(\"status\") != \"complete\":", "    if False:",
     ["test_m4_evaluate.py"]),
    ("r2_release_by_mode_only", "evaluate.py", "        \"inferential_claims\": release[\"released\"],",
     "        \"inferential_claims\": bool(mode == \"research\"),", ["test_m4_evaluate.py"]),
    ("frozen_membrane_not_frozen", "membrane_pilot.py", "FROZEN_GAINS = dict(plasticity=0.0,", "FROZEN_GAINS = dict(plasticity=0.1,",
     ["test_m5_membrane.py"]),
    ("whitelist_bypassed", "serve.py", "        if name is None:                               # fixed whitelist: no paths from the browser",
     "        if name is None:\n            name = route.lstrip('/')\n        if name is None:", ["test_m6_serve.py"]),
    ("bayes_on_max_coordinate", "serve.py", "\"bayes_accuracy_full_observation\": NormalDist().cdf(l2 / (2 * sigma)),",
     "\"bayes_accuracy_full_observation\": NormalDist().cdf(float(np.max(np.abs(a - b))) / (2 * sigma)),", ["test_m6_serve.py"]),
    # --- M8 knob lab ---
    ("lab_bound_ignores_readout_norm", "lab.py", "    kappa = float(np.sqrt((np.abs(H).sum(axis=1) ** 2).sum()))",
     "    kappa = 1.0", ["test_m8_lab.py"]),
    ("lab_renormalize_skipped", "lab.py", "    if k[\"ablation\"][\"mode\"] == \"renormalize\":", "    if False:", ["test_m8_lab.py"]),
    ("lab_ablation_one_direction", "lab.py", "        A[i, j] = A[j, i] = 0.0", "        A[i, j] = 0.0", ["test_m8_lab.py"]),
    ("lab_clears_wrong_modules", "lab.py", "if m == k[\"clear_module\"]]", "if m != k[\"clear_module\"]]", ["test_m8_lab.py"]),
    ("lab_duration_first_passage_only", "lab.py", "    last = above[-1] if above else None",
     "    last = (below[0] - 1 if below[0] > 0 else None) if below else len(bayes) - 1", ["test_m8_lab.py"]),
    ("lab_curve_ignores_readout", "lab.py", "    sep = [float(np.linalg.norm(H @ dx[d + 1])) for d in range(D_MAX + 1)]",
     "    sep = [float(np.linalg.norm(dx[d + 1])) for d in range(D_MAX + 1)]", ["test_m8_lab.py"]),
    ("lab_log_overwrites", "serve.py", "        with (EXPLORE_DIR / f\"{payload['run_id']}.json\").open(\"x\", encoding=\"utf-8\") as fh:",
     "        with (EXPLORE_DIR / f\"{payload['run_id']}.json\").open(\"w\", encoding=\"utf-8\") as fh:", ["test_m8_lab.py"]),
    # --- M9a closed-form predictions ---
    ("predict_mode_D_wrong_ratio", "predict.py", "    lam_D = None if M == 1 else g_ * (1 - c * N / (N - n))",
     "    lam_D = None if M == 1 else g_ * (1 - c * N / n)", ["test_m9_predict.py"]),
    ("predict_error_bound_dropped", "predict.py", "            E.append(acc * (1 + FLOAT_SAFETY[0]) + FLOAT_SAFETY[1])",
     "            E.append(0.0)", ["test_m9_predict.py"]),
    ("predict_bound_rate_from_D_only", "predict.py",
     "    rho = abs(mu(lam_I)) if same or M == 1 else max(abs(mu_D), abs(mu(lam_I)))",
     "    rho = abs(mu(lam_I)) if same or M == 1 else abs(mu_D) * 0.5", ["test_m9_predict.py"]),
    ("predict_tanh_in_linear_limit", "predict.py",
     "    g = ell * (math.tanh(p[\"amplitude\"]) if p[\"nonlinearity\"] == \"tanh\" else p[\"amplitude\"])",
     "    g = ell * math.tanh(p[\"amplitude\"])", ["test_m9_predict.py"]),
    # --- M9b/M9c freeze and evaluation ---
    # retargeted: disabling only the equality test is equivalent (the stricter "differs in no continuous knob"
    # layer catches the same case); the real gap was whether build() runs the check at all
    ("m9_freeze_skips_seen_check", "m9_freeze.py", "    seen_info = check_unseen(held, seen)",
     "    seen_info = {\"n_seen\": len(seen), \"seen_continuous_values\": {}}", ["test_m9_freeze.py"]),
    ("m9_integrity_not_checked", "m9_evaluate.py", "    if sha != expected_sha:", "    if False:", ["test_m9_evaluate.py"]),
    ("m9_duration_not_checked", "m9_evaluate.py", "    D_ok = _d(lo) <= _d(D_k) <= _d(hi)", "    D_ok = True", ["test_m9_evaluate.py"]),
    ("m9_band_ignores_bound", "m9_evaluate.py", "        allowed = Hn * e + 1e-12 * max(1.0, s) + 1e-15",
     "        allowed = Hn * e + 1e-12 * max(1.0, s) + 1e-15 + 1.0", ["test_m9_evaluate.py"]),
    ("m9_decoder_band_open", "m9_evaluate.py", "\"passed\": band[0] <= acc <= band[1]}", "\"passed\": True}", ["test_m9_evaluate.py"]),
    # --- M10 implementation (development settings) ---
    ("m10_window_shifted", "m10_task.py", "        slot = k - (d - W + 1)", "        slot = k - (d - W)", ["test_m10_portable.py"]),
    ("m10_logsumexp_unshifted", "m10_bayes.py", "    m = np.max(a, axis=axis, keepdims=True)\n",
     "    m = np.zeros_like(np.max(a, axis=axis, keepdims=True))\n", ["test_m10_portable.py"]),
    ("m10_update_not_conditioned", "m10_bayes.py", "        w = np.array([0.5 * float(pats[i][1] / p_last) for i in idx] * 2)",
     "        w = np.array([0.5 * float(pats[i][1]) for i in idx] * 2)", ["test_m10_portable.py"]),
    ("m10_update_not_marginalised", "m10_bayes.py", "        w = np.array([0.5 * float(pats[i][1] / p_last) for i in idx] * 2)",
     "        w = np.array([float(pats[i][1] / p_last) for i in idx] * 2)", ["test_m10_portable.py"]),
    ("m10_holm_no_stop", "m10_evaluate.py", "        still = still and reject", "        still = True", ["test_m10_portable.py"]),
    ("m10_se_zero_rule_wrong", "m10_evaluate.py", "        return 0.0 if delta_hat > delta else 1.0", "        return 0.0",
     ["test_m10_portable.py"]),
    ("m10_research_not_blocked", "m10_run.py", "    if FROZEN_PROTOCOL_SHA256 is None:", "    if False:", ["test_m10_controls.py"]),
    ("m10_release_ignores_overrides", "m10_evaluate.py", "    if any(v not in (None, False) for v in result.get(\"overrides\", {}).values()):",
     "    if False:", ["test_m10_controls.py"]),
    ("m10_lda_ignores_covariance", "m10_decoders.py", "        self.w = np.linalg.solve(self.cov, self.means[1] - self.means[0])",
     "        self.w = self.means[1] - self.means[0]", ["test_m10_portable.py"]),
    ("m10_a1_ignores_permutation", "m10_task.py", "worst = max(worst, float(np.max(np.abs(xb - xa[:, perm]))) / scale)",
     "worst = max(worst, float(np.max(np.abs(xb - xa))) / scale)", ["test_m10_kernel.py"]),
    ("m10_leak_check_blind", "m10_decoders.py", "    return {\"identical_pattern_counts\": bool(np.array_equal(*counts))}",
     "    return {\"identical_pattern_counts\": True}", ["test_m10_kernel.py"]),
    ("m10_split_check_blind", "m10_decoders.py", "    if shared or train.role == test.role:", "    if False:", ["test_m10_kernel.py"]),
    # --- review astra-m10-review R9-R12: enforcement in runner and release gate ---
    ("r9_gate_ignores_completeness", "m10_evaluate.py", "    reasons += completeness(result, mt.load_protocol())\n", "",
     ["test_m10_controls.py"]),
    ("r9_gate_ignores_bayes_streams", "m10_evaluate.py", "            if v.get(\"stream\") != want:", "            if False:",
     ["test_m10_controls.py"]),
    ("r9_gate_ignores_duplicate_d_rows", "m10_evaluate.py", "    if len(keys_d) != len(set(keys_d)):", "    if False:",
     ["test_m10_controls.py"]),
    ("r9_gate_ignores_code_hashes", "m10_evaluate.py", "            if result.get(\"code_sha256\") != rec[\"code_sha256\"]:",
     "            if False:", ["test_m10_controls.py"]),
    ("r10_runner_ignores_leak_check", "m10_run.py", "            if not all(checks.values()):", "            if False:",
     ["test_m10_controls.py"]),
    ("r10_diagnostics_not_enforced", "m10_run.py", "        enforce_diagnostics(result[\"diagnostics\"])\n", "",
     ["test_m10_controls.py"]),
    ("r10_gate_ignores_failed_controls", "m10_evaluate.py",
     "        if not isinstance(chk, dict) or set(chk) != REQUIRED_D_CHECKS or any(v is not True for v in chk.values()):",
     "        if False:", ["test_m10_controls.py"]),
    # --- follow-up review FOLLOWUP_R9_R12 ---
    ("f_gate_accepts_incomplete_check_set", "m10_evaluate.py", "set(chk) != REQUIRED_D_CHECKS or ", "", ["test_m10_controls.py"]),
    ("f_gate_k0_se_unchecked", "m10_evaluate.py", " or pv[\"se\"] != 0.0):", "):", ["test_m10_controls.py"]),
    ("f_gate_update_n_train_unchecked", "m10_evaluate.py", "n_train=n_tr - 2 * k_tr, ", "", ["test_m10_controls.py"]),
    ("f_gate_a2_need_from_result", "m10_evaluate.py", "        need_a2 = nl == \"identity\" and fixed",
     "        need_a2 = nl == \"identity\" and bool(r.get(\"p_fixed\"))", ["test_m10_controls.py"]),
    ("f_final_deadline_removed", "m10_run.py",
     "        deadline()                                           # also an overrun in the LAST unit must not count as complete\n",
     "", ["test_m10_controls.py"]),
    ("f_diagnostics_deadline_removed", "m10_run.py",
     "        if deadline:\n            deadline()\n        perm = mt.swap_permutation(", "        perm = mt.swap_permutation(",
     ["test_m10_controls.py"]),
    ("r11_smoke_not_frozen", "m10_run.py", "        require_frozen(mode)\n        s = proto[\"smoke\"]", "        s = proto[\"smoke\"]",
     ["test_m10_controls.py"]),
    ("r11_code_hash_not_checked", "m10_run.py", "    if rec.get(\"code_sha256\") != code_sha256():", "    if False:",
     ["test_m10_controls.py"]),
    ("r12_mc_without_deadline", "m10_run.py", "mb.bayes_accuracy_mc(mix, sigma, n_mc, rng, block, deadline=deadline)",
     "mb.bayes_accuracy_mc(mix, sigma, n_mc, rng, block)", ["test_m10_controls.py"]),
    ("r12_block_loop_unchecked", "m10_bayes.py", "        if deadline is not None:\n            deadline()\n", "",
     ["test_m10_controls.py"]),
    ("r12_timeout_counted_complete", "m10_run.py", "        result[\"status\"] = \"aborted_timeout\"",
     "        result[\"status\"] = \"complete\"", ["test_m10_controls.py"]),
    # --- M11 readout study (development; plan Fassung 2) ---
    ("m11_constant_rule_not_half", "m11_readout.py", "    if nw == 0.0:\n        return 0.5\n", "    if nw == 0.0:\n        return 0.0\n",
     ["test_m11_readout.py"]),
    ("m11_noise_stream_depends_on_n", "m11_readout.py", "    rng_e, key_e = stream(mode, seed, \"noise\", role)",
     "    rng_e, key_e = stream(mode, seed, \"noise\", role, n_pairs)", ["test_m11_readout.py"]),
    # retargeted: "every 5th EPISODE" is equivalent to "every 5th PAIR" for all n in the grid (multiples of 5,
    # A block then B block); the real risk is a validation set that is not class-stratified
    ("m11_validation_not_stratified", "m11_readout.py", "    is_val = val_pairs[pair]",
     "    is_val = np.concatenate([val_pairs, np.zeros(n_pairs, dtype=bool)])", ["test_m11_readout.py"]),
    ("m11_standardise_with_validation", "m11_readout.py", "        self.mean, self.std = Xfit.mean(axis=0), Xfit.std(axis=0) + 1e-12",
     "        Xall = np.concatenate([Xfit, Xval])\n        self.mean, self.std = Xall.mean(axis=0), Xall.std(axis=0) + 1e-12",
     ["test_m11_readout.py"]),
    ("m11_population_candidates_losable", "m11_readout.py",
     "    candidates = [r[\"end_acc\"] for r in runs] + [exact_accuracy(*rules[\"nm\"], z, probs, sigma),\n"
     "                                                exact_accuracy(*rules[\"lda\"], z, probs, sigma)]",
     "    candidates = [r[\"end_acc\"] for r in runs if r[\"start\"].startswith(\"random\")]", ["test_m11_kernel.py"]),
    ("m11_reference_phase_unversioned", "m11_references.py", "    if not git_clean(VERSIONED):", "    if False:",
     ["test_m11_kernel.py"]),
    # --- review FOLLOWUP_10cd638: service run ids ---
    ("service_run_id_from_clock", "serve.py", "    return f\"{prefix}-{uuid.uuid4().hex[:16]}\"", "    return f\"{prefix}-{int(time.time())}\"",
     ["test_m6_serve.py"]),
    ("service_explore_overwrites", "serve.py", "        _log(payload, \"explore\", {\"request\": payload[\"request\"]})",
     "        (EXPLORE_DIR / f\"{payload['run_id']}.json\").write_text(json.dumps(payload) + \"\\n\")\n"
     "        with (EXPLORE_DIR / \"protocol.jsonl\").open(\"a\") as fh:\n            fh.write(json.dumps({\"run_id\": payload[\"run_id\"]}) + \"\\n\")",
     ["test_m6_serve.py"]),
    # --- review IMPLEMENTIERUNGSREVIEW_c864678 (M11-R5 .. R9) ---
    ("r5_gate_ignores_references_content", "m11_evaluate.py", "    if refs != on_disk:", "    if False:", ["test_m11_kernel.py"]),
    # retargeted: in m11_run the check is doubled (settings() and the result record, both before any state) -> equivalent;
    # the single guard is the one in the reference computation
    ("r5_reference_compute_without_m10_check", "m11_references.py",
     "    m10_binding = require_m10_frozen()\n    return _compute_cases(case_set, m10_binding)",
     "    return _compute_cases(case_set, {})", ["test_m11_kernel.py"]),
    ("r6_nan_gradient_ignored", "m11_readout.py",
     "            _check_finite(f\"training loss or gradient in epoch {epoch}\", np.array([loss]), *grad.values())\n", "",
     ["test_m11_kernel.py"]),
    ("r7_gate_ignores_selection", "m11_evaluate.py", "            out.append(\"mlp_selection_inconsistent\")\n    except", "            pass\n    except",
     ["test_m11_kernel.py"]),
    ("r7_gate_ignores_init_streams", "m11_evaluate.py",
     "        if it.get(\"stream\") != list(mr.stream(smode, seed, \"mlp-init\", case, n, k)[1]):", "        if False:", ["test_m11_kernel.py"]),
    ("r8_phase_computes_before_checking_artifact", "m11_references.py",
     "    if RESEARCH_REFERENCES.exists():\n        raise MemoryLabError(\"reference phase already completed: artifact exists\")\n", "",
     ["test_m11_kernel.py"]),
    ("r8_direct_compute_unguarded", "m11_references.py", "    if case_set == \"research\" and not _claimed:", "    if False:",
     ["test_m11_kernel.py"]),
    ("r9_closed_share_unpaired", "m11_evaluate.py", "    num_b, den_b = d[idx].mean(axis=1) - l[idx].mean(axis=1), B - l[idx].mean(axis=1)",
     "    idx2 = rng.integers(0, d.size, size=(reps, d.size))\n    num_b, den_b = d[idx].mean(axis=1) - l[idx2].mean(axis=1), B - l[idx2].mean(axis=1)",
     ["test_m11_kernel.py"]),
    ("deadline_not_in_epochs", "m11_readout.py", "            if deadline is not None:                          # cooperative time limit, checked every epoch\n                deadline()\n",
     "", ["test_m11_kernel.py"]),
    ("m11_gate_blind_missing_rows", "m11_evaluate.py", "    if expected - set(keys):\n        problems.append(\"missing_rows\")\n", "",
     ["test_m11_kernel.py"]),
    ("m11_gate_blind_streams", "m11_evaluate.py", "        if r.get(\"train_streams\") != want_train or r.get(\"test_streams\") != want_test:",
     "        if False:", ["test_m11_kernel.py"]),
    ("m11_zero_variance_rule_wrong", "m11_evaluate.py", "\"p\": 0.0 if mean > delta else 1.0", "\"p\": 1.0", ["test_m11_kernel.py"]),
    ("m11_research_not_blocked", "m11_run.py", "    if FROZEN_PROTOCOL_SHA256 is None:\n        raise MemoryLabError(f\"{mode} run blocked: the M11 protocol is not frozen yet\")\n",
     "", ["test_m11_kernel.py"]),
    ("m10_update_k0_not_na", "m10_run.py", "            row[\"update\"] = None                                            # N/A for K0",
     "            row[\"update\"] = {\"estimate\": 0.5, \"se\": 0.0, \"n\": 0}", ["test_m10_kernel.py"]),
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
