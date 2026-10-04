"""Test tiers of the Mandala memory lab (review R8).

Instead of excluding the whole folder outside the Windows lab, every test
declares what it needs; a missing prerequisite skips ONLY the affected tests,
with its own reason:

  portable          no marker: numpy + pytest (+ PyYAML for the Trilayer test)
  scf               scoped-correspondence >= 0.42.0 (network construction, SCF
                    reference functions); declared in requirements-lab.txt
  lab_integration   the Windows lab layout on D:/mandala: original result files,
                    the unified-mandala view worktree (HTTP/UI tests), benchmark
                    files that must stay untouched
  git_history       the Feldtheorie history containing the plan commit 0e46ec8
                    (absent in shallow CI clones)

Mandatory lab run (documented in README): set MANDALA_LAB_REQUIRED=1. Then a
missing prerequisite is an ERROR and any skipped test fails the session -- the
lab run can never pass by silently skipping.

Safety: on POSIX a relative path "D:/..." or "C:/..." would silently create a
folder named "D:"/"C:" in the working directory; the session fails if one
appears.
"""
import importlib.metadata
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
REQUIRED = os.environ.get("MANDALA_LAB_REQUIRED") == "1"

# --- explicit dependency table (node ids relative to this folder) ---------------
SCF = {
    # service run ids (explore needs the kernel networks)
    "test_m6_serve.py::test_identical_requests_with_a_frozen_clock_get_distinct_ids",
    "test_m6_serve.py::test_forced_id_collision_never_overwrites_and_logs_nothing",
    # M11 optimiser/reference phase/runner/gate: scipy and the kernel (SCF network construction)
    "test_m11_kernel.py::test_optimiser_finds_a_known_linear_optimum",
    "test_m11_kernel.py::test_l_found_never_below_the_population_rules_on_a_mixture",
    "test_m11_kernel.py::test_reference_phase_refuses_unversioned_procedures",
    "test_m11_kernel.py::test_dev_references_and_the_bayes_source_check",
    "test_m11_kernel.py::test_smoke_and_research_blocked_before_the_freeze",
    "test_m11_kernel.py::test_small_development_run_end_to_end_and_exact_vs_test",
    "test_m11_kernel.py::test_timeout_is_enforced",
    "test_m11_kernel.py::test_gate_completeness_on_synthetic_data",
    "test_m11_kernel.py::test_t_test_holm_and_zero_variance_rules",
    "test_m11_kernel.py::test_closed_share_is_na_for_a_small_denominator",
    "test_m11_kernel.py::test_r5_bound_references_release_and_arbitrary_references_do_not",
    "test_m11_kernel.py::test_r5_changed_m10_protocol_is_detected_before_any_state",
    "test_m11_kernel.py::test_r6_nan_gradient_raises_in_the_mlp",
    "test_m11_kernel.py::test_r6_nan_gradient_fails_the_runner_and_the_release",
    "test_m11_kernel.py::test_deadline_is_checked_every_epoch",
    "test_m11_kernel.py::test_r8_existing_artifact_claim_or_failure_blocks_before_compute",
    "test_m11_kernel.py::test_r8_unversioned_or_m10_not_frozen_blocks_before_compute",
    "test_m11_kernel.py::test_r8_one_phase_then_locked_and_failure_is_recorded",
    "test_m11_kernel.py::test_r9_closed_share_bootstrap_paired_and_na_rules",
    "test_m11_kernel.py::test_m11_freeze_is_consistent",
    # M10 kernel tests (network construction via SCF budget_adjacency; split check via SCF)
    "test_m10_kernel.py::test_a1_state_identity_and_negative_control",
    "test_m10_kernel.py::test_a2_structural_and_negative_control",
    "test_m10_kernel.py::test_k0_states_and_analytic_baseline",
    "test_m10_kernel.py::test_level_d_episodes_pairing_leak_and_split_controls",
    "test_m10_kernel.py::test_update_task_excludes_episodes_without_pulse",
    "test_m10_kernel.py::test_small_development_run_end_to_end",
    "test_m10_controls.py::test_r10_failed_leak_check_fails_the_run",
    "test_m10_controls.py::test_r10_failed_split_check_fails_the_run",
    "test_m10_controls.py::test_r10_unexpected_deterministic_diagnostic_fails_the_run",
    "test_m10_controls.py::test_r10_expected_negative_a1_control_does_not_fail_the_run",
    "test_m10_controls.py::test_r12_timeout_through_the_runner",
    "test_m10_controls.py::test_r12_overrun_in_the_last_unit_is_not_complete",
    "test_m10_controls.py::test_r12_deadline_is_checked_inside_the_diagnostics",
    # derived from a Linux run WITHOUT scoped-correspondence: exactly these failed on the
    # missing module (directly, or via a runner seed that caught it); see ROADMAP, review R8
    "test_m1_core.py::test_k3_reset_after_pulse",
    "test_m1_core.py::test_k7_exact_matrix_and_identical_trajectories",
    "test_m1_core.py::test_k8_contraction_bound_production_step",
    "test_m1_core.py::test_k9_continuation_network_snapshot_restore",
    "test_m1_core.py::test_pulse_applied_exactly_once",
    "test_m1_core.py::test_readout_is_state_after_d_plus_one_steps",
    "test_m1_core.py::test_scf_simulate_trial_parity",
    "test_m1_core.py::test_scope_errors",
    "test_m1_core.py::test_snapshot_restore_roundtrip_and_mismatch",
    "test_m1_core.py::test_uncoupled_leak_decays_geometrically",
    "test_m1_core.py::test_weights_untouched_by_episodes",
    "test_m2_data.py::test_episode_sets_reproducible_and_ids_disjoint",
    "test_m2_data.py::test_k2_decoder_near_bayes",
    "test_m2_data.py::test_k6_permutation_frozen_vs_refit",
    "test_m2_data.py::test_paired_conditions_share_test_noise",
    "test_m3_model_runner.py::test_adaptation_changes_weights_only_in_training_and_keeps_budget_and_mask",
    "test_m3_model_runner.py::test_adaptation_is_deterministic_per_seed_and_order_differs_between_seeds",
    "test_m3_model_runner.py::test_adaptation_requires_training_only_and_balance",
    "test_m3_model_runner.py::test_condition_specs_and_identity_control",
    "test_m3_model_runner.py::test_review_r1_full_partial_aborted_never_overwrite",
    "test_m3_model_runner.py::test_run_seed_checks_and_pairing",
    "test_m3_model_runner.py::test_runner_deterministic_and_refuses_c_drive",
    "test_m3_model_runner.py::test_runner_reports_failed_seed",
    "test_m4_evaluate.py::test_exact_sign_flip_equals_scf_enumeration",
    "test_m4_evaluate.py::test_primary_is_paired_and_honest",
    "test_m4_evaluate.py::test_primary_pairs_values_of_the_same_seed",
    "test_m5_membrane.py::test_run_pilot_structure_and_vocabulary",
    "test_m6_serve.py::test_clear_intervention_and_identical_start",
    "test_m6_serve.py::test_comparison_reports_bayes_accuracy_over_all_coordinates",
    "test_m6_serve.py::test_each_request_gets_a_new_run_id_and_protocol_entry",
    "test_m6_serve.py::test_traces_come_from_the_tested_kernel",
    "test_m8_lab.py::test_ablating_every_edge_is_the_uncoupled_leak_model",
    "test_m8_lab.py::test_ablation_budget_loss_and_renormalize",
    "test_m8_lab.py::test_benchmark_knobs_reproduce_the_frozen_network_and_kernel",
    "test_m8_lab.py::test_clear_all_and_clear_one_module",
    "test_m8_lab.py::test_explore_dir_can_be_redirected_but_never_to_c",
    "test_m8_lab.py::test_identity_nonlinearity_is_exactly_linear_propagation",
    "test_m8_lab.py::test_lab_logging_new_ids_never_overwrite",
    "test_m8_lab.py::test_memory_duration_definition",
    "test_m8_lab.py::test_q_bound_is_never_exceeded",
    "test_m8_lab.py::test_readout_operators",
    "test_m8_lab.py::test_same_q_different_memory_and_bound_is_loose",
    "test_m9_erratum.py::test_r3_negative_coupling_eigenvalue_without_sign_change",
    "test_m9_erratum.py::test_r3_positive_control_sign_alternates_exactly_when_mu_D_negative",
    "test_m9_erratum.py::test_r4_below_threshold_at_d0_is_not_no_memory",
    "test_m9_evaluate.py::test_decoder_check_and_its_negative_control",
    "test_m9_evaluate.py::test_primary_check_detects_a_wrong_duration",
    "test_m9_evaluate.py::test_primary_check_passes_and_detects_a_too_narrow_band",
    "test_m9_predict.py::test_band_contains_the_kernel_on_development_combinations",
    "test_m9_predict.py::test_identity_is_predicted_exactly",
    "test_m9_predict.py::test_mode_eigenvalues_match_the_kernel_matrix",
    "test_m9_predict.py::test_symmetry_permutation_is_an_automorphism",
}
LAB_INTEGRATION = {
    "test_m11_kernel.py::test_dev_references_and_the_bayes_source_check",   # reads the M10 dev result on D:
    "test_m4_evaluate.py::test_review_r2_original_full_round_released_and_numerically_unchanged",
    "test_m4_evaluate.py::test_review_r2_incomplete_protocol_not_released",
    "test_m4_evaluate.py::test_original_sign_flip_p_unchanged",
    "test_m6_serve.py::test_http_routes_whitelist_and_binding",
    "test_m6_serve.py::test_http_run_and_bad_request",
    "test_m6_serve.py::test_benchmark_results_are_never_written",
    "test_m8_lab.py::test_http_lab_routes",
    "test_m8_lab.py::test_lab_never_writes_benchmark",
}
GIT_HISTORY = {
    "test_m5_membrane.py::test_feldtheorie_membrane_source_unchanged",
}


def _scf_problem():
    try:
        version = importlib.metadata.version("scoped-correspondence")
    except importlib.metadata.PackageNotFoundError:
        return "scoped-correspondence not installed (see experiments/mandala_memory/requirements-lab.txt)"
    parts = tuple(int(p) for p in version.split(".")[:2] if p.isdigit())
    if parts < (0, 42):
        return f"scoped-correspondence {version} < 0.42.0"
    return None


def _lab_problem():
    if sys.platform != "win32":
        return "lab integration needs the Windows lab layout (D:/mandala results and view worktree)"
    if not os.path.isdir("D:/mandala"):
        return "lab layout D:/mandala not present"
    return None


def _git_problem():
    r = subprocess.run(["git", "-C", str(REPO), "cat-file", "-e", "0e46ec88181b430c41330016279a8bd1ea2c0d9b^{commit}"],
                       capture_output=True)
    return None if r.returncode == 0 else "git history with plan commit 0e46ec8 not available (shallow clone?)"


PROBLEMS = {"scf": _scf_problem(), "lab_integration": _lab_problem(), "git_history": _git_problem()}
TABLE = {"scf": SCF, "lab_integration": LAB_INTEGRATION, "git_history": GIT_HISTORY}


def pytest_configure(config):
    for name, text in (("scf", "needs scoped-correspondence >= 0.42.0"),
                       ("lab_integration", "needs the Windows lab layout on D:/mandala"),
                       ("git_history", "needs the Feldtheorie history with the plan commit")):
        config.addinivalue_line("markers", f"{name}: {text}")
    if REQUIRED:
        missing = {k: v for k, v in PROBLEMS.items() if v}
        try:
            import yaml  # noqa: F401
        except ImportError:
            missing["yaml"] = "PyYAML missing (Trilayer test)"
        if missing:
            raise pytest.UsageError(f"MANDALA_LAB_REQUIRED=1 but the lab environment is incomplete: {missing}")


def _key(item) -> str:
    rel = Path(str(item.fspath)).resolve().relative_to(HERE).as_posix()
    return f"{rel}::{item.originalname or item.name}"


def pytest_collection_modifyitems(config, items):
    for item in items:
        if Path(str(item.fspath)).resolve().parent != HERE:
            continue
        key = _key(item)
        for marker, names in TABLE.items():
            if key in names:
                item.add_marker(getattr(pytest.mark, marker))
                if PROBLEMS[marker]:
                    item.add_marker(pytest.mark.skip(reason=f"[{marker}] {PROBLEMS[marker]}"))


_SKIPPED = []


def pytest_runtest_logreport(report):
    if report.skipped and HERE.as_posix() in Path(str(report.fspath)).resolve().as_posix():
        _SKIPPED.append(report.nodeid)


def pytest_sessionfinish(session, exitstatus):
    tr = session.config.pluginmanager.get_plugin("terminalreporter")
    stray = [d for d in ("D:", "C:") if sys.platform != "win32" and (Path.cwd() / d).exists()]
    if stray:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED
        if tr:
            tr.write_line(f"[mandala_memory] FAIL: relative folder(s) {stray} created in {Path.cwd()} -- a test wrote to a Windows path")
    if REQUIRED and _SKIPPED:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED
        if tr:
            tr.write_line(f"[mandala_memory] FAIL: mandatory lab run, but {len(_SKIPPED)} test(s) skipped: {_SKIPPED[:5]}")
    elif tr and any(PROBLEMS.values()):
        tr.write_line("[mandala_memory] tiers skipped here: " + "; ".join(f"{k}: {v}" for k, v in PROBLEMS.items() if v)
                      + "  -- this is NOT a lab test run (see README)")
