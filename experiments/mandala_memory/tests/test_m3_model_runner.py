"""M3 tests: adaptation only in training, budget/mask, frozen tests, runner
determinism, C: guard, timeout/abort and failed-seed reporting.

No effect direction is asserted (plan: no winner as acceptance criterion).
"""
import json
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

from experiments.mandala_memory.core import MemoryLabError, recall_state
from experiments.mandala_memory.model import adapt_network, condition_specs, network_from_config
from experiments.mandala_memory.runner import peak_rss_bytes, run_experiment, run_seed
from experiments.mandala_memory.tests._paths import scratch

CFG_PATH = Path(__file__).resolve().parents[1] / "protocol" / "startkonfiguration.json"
CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
TMP_OUT = scratch()


def small_cfg(**smoke):
    cfg = json.loads(json.dumps(CFG))
    cfg["smoke"].update({"seeds": [11, 12], "decoder_train_per_class_per_delay": 6, "test_per_class_per_delay": 6, **smoke})
    cfg["episode"]["delay_steps"] = [0, 4]
    return cfg


def test_adaptation_changes_weights_only_in_training_and_keeps_budget_and_mask():
    frozen = network_from_config(CFG["network"])
    A0 = frozen.A.copy()
    adapted, rec = adapt_network(frozen, CFG["adaptation"], mode="test", seed=1)
    assert np.array_equal(frozen.A, A0), "the input network is not modified"
    assert not np.array_equal(adapted.A, A0) and rec.weight_change_fro > 0
    assert np.allclose(adapted.A.sum(axis=1), 0.8, atol=1e-12), "row budget gamma kept"
    assert rec.masked_entries_zero and np.all(np.diag(adapted.A) == 0)
    assert rec.order.count(0) == rec.order.count(1) == 20 and rec.n_updates == 40 and rec.steps_per_episode == 5
    before = adapted.A.copy()
    for s in (0, 1):
        recall_state(adapted, s, 32)
    assert np.array_equal(adapted.A, before), "evaluation episodes never change A"


def test_adaptation_is_deterministic_per_seed_and_order_differs_between_seeds():
    frozen = network_from_config(CFG["network"])
    a1, r1 = adapt_network(frozen, CFG["adaptation"], mode="test", seed=1)
    a2, r2 = adapt_network(frozen, CFG["adaptation"], mode="test", seed=1)
    a3, r3 = adapt_network(frozen, CFG["adaptation"], mode="test", seed=2)
    assert np.array_equal(a1.A, a2.A) and r1.order == r2.order
    assert r1.order != r3.order


def test_adaptation_requires_training_only_and_balance():
    frozen = network_from_config(CFG["network"])
    with pytest.raises(MemoryLabError):
        adapt_network(frozen, {**CFG["adaptation"], "update_on": "test"}, mode="test", seed=1)
    with pytest.raises(MemoryLabError):
        adapt_network(frozen, {**CFG["adaptation"], "trials_total": 41}, mode="test", seed=1)


def test_condition_specs_and_identity_control():
    specs = condition_specs(CFG["network"])
    assert np.array_equal(specs["uniform_M1"].A, specs["renamed_M3_c8_11"].A)
    assert not np.any(specs["uncoupled_leak"].A) and specs["linear"].nonlinearity == "identity"
    for name in ("frozen", "linear", "uniform_M1"):
        assert np.allclose(specs[name].A.sum(axis=1), 0.8, atol=1e-12)


def test_run_seed_checks_and_pairing():
    timings = {}
    res = run_seed(small_cfg(), "test", 11, {"train": 6, "test": 6, "validation": 0}, timings)
    assert all(res["checks"].values())
    for d, row in res["delays"].items():
        assert row["checks"]["uniform_equals_renamed_states"] and row["checks"]["reset_control_states_identical"]
        assert row["uniform_M1"]["balanced_accuracy"] == row["renamed_M3_c8_11"]["balanced_accuracy"]
        assert row["checks"]["split_sizes"] == {"decoder_train": 12, "test": 12}


def test_runner_deterministic_and_refuses_c_drive(tmp_path_factory):
    cfg = small_cfg()
    r1 = run_experiment(cfg, "smoke", TMP_OUT / "a")
    r2 = run_experiment(cfg, "smoke", TMP_OUT / "b")
    assert r1["status"] == r2["status"] == "complete"
    assert json.dumps(r1["runs"], sort_keys=True) == json.dumps(r2["runs"], sort_keys=True), "identical repetition"
    # review R1: the protocol id is fixed per configuration, every execution has its own id
    assert r1["protocol_id"] == r2["protocol_id"] and r1["config_sha256"] == r2["config_sha256"]
    assert r1["run_id"] != r2["run_id"]
    with pytest.raises(MemoryLabError):
        run_experiment(cfg, "smoke", Path("C:/mandala-memory-should-not-exist"))


def test_c_drive_guard_is_portable(monkeypatch):
    """Review R8: on POSIX Path("C:/x").drive is empty and resolve() yields a path
    without a drive. The guard must still refuse C: from the raw spelling."""
    import pathlib

    from experiments.mandala_memory.core import is_drive_c

    monkeypatch.setattr(pathlib.Path, "resolve", lambda self, strict=False: pathlib.Path("/no-drive"))
    assert is_drive_c("C:/mandala") and is_drive_c("c:\\x") and is_drive_c(Path("C:/y"))
    assert not is_drive_c("D:/mandala") and not is_drive_c("/tmp/x")


def test_runner_timeout_aborts_without_shrinking_claims(monkeypatch):
    import experiments.mandala_memory.runner as runner

    clock = iter(float(i) for i in range(10 ** 6))         # deterministic clock: +1 s per call
    monkeypatch.setattr(runner.time, "perf_counter", lambda: next(clock))
    res = run_experiment(small_cfg(), "smoke", TMP_OUT / "timeout", timeout_s=0.5)
    assert res["status"] == "aborted" and "timeout" in res["abort_reason"] and res["runs"] == []
    assert res["seeds"] == [11, 12], "declared seeds stay recorded"
    assert res["inference_release"]["released"] is False


@pytest.mark.parametrize("bad", [0.0, -1.0])
def test_runner_rejects_non_positive_timeout(bad):
    with pytest.raises(MemoryLabError):
        run_experiment(small_cfg(), "smoke", TMP_OUT / "bad-timeout", timeout_s=bad)


def test_runner_rejects_duplicate_seeds():
    with pytest.raises(MemoryLabError):
        run_experiment(small_cfg(), "smoke", TMP_OUT / "dup", seeds=[11, 11])


def test_review_r1_full_partial_aborted_never_overwrite(monkeypatch):
    """Review R1: full, partial and aborted executions of the SAME configuration in
    the SAME directory must all survive."""
    import shutil
    import experiments.mandala_memory.runner as runner

    out = TMP_OUT / "r1"
    shutil.rmtree(out, ignore_errors=True)
    cfg = small_cfg()
    full = run_experiment(cfg, "smoke", out)
    part = run_experiment(cfg, "smoke", out, seeds=[11])
    clock = iter(float(i) for i in range(10 ** 6))
    monkeypatch.setattr(runner.time, "perf_counter", lambda: next(clock))
    abort = run_experiment(cfg, "smoke", out, timeout_s=0.5)
    paths = [Path(r["output_path"]) for r in (full, part, abort)]
    assert len(set(paths)) == 3 and all(p.is_file() for p in paths)
    runs = [len(json.loads(p.read_text(encoding="utf-8"))["runs"]) for p in paths]
    assert runs == [2, 1, 0], "nothing was overwritten"
    assert {full["protocol_id"], part["protocol_id"], abort["protocol_id"]} == {full["protocol_id"]}
    assert part["execution_options"]["seeds_override"] is True and full["execution_options"]["seeds_override"] is False
    assert not any(p.name.startswith(".") for p in out.iterdir()), "no leftover temp files"


def test_runner_itself_never_overwrites_on_id_collision(monkeypatch):
    """Mutation-check finding: unique execution ids hid whether the RUNNER writes
    exclusively. Force an id collision; the second run must fail and the first
    file must stay intact."""
    import shutil
    import uuid as uuid_mod
    import experiments.mandala_memory.runner as runner

    out = TMP_OUT / "collision"
    shutil.rmtree(out, ignore_errors=True)
    fixed = uuid_mod.UUID("12345678123456781234567812345678")
    monkeypatch.setattr(runner.uuid, "uuid4", lambda: fixed)
    monkeypatch.setattr(runner.time, "strftime", lambda fmt: "20261003T000000")
    first = run_experiment(small_cfg(), "smoke", out)
    before = Path(first["output_path"]).read_bytes()
    with pytest.raises(MemoryLabError):
        run_experiment(small_cfg(), "smoke", out, seeds=[11])
    assert Path(first["output_path"]).read_bytes() == before


def test_write_exclusive_refuses_existing(tmp_path_factory):
    from experiments.mandala_memory.runner import write_exclusive

    target = TMP_OUT / "excl" / "x.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.unlink(missing_ok=True)
    write_exclusive(target, "first")
    with pytest.raises(MemoryLabError):
        write_exclusive(target, "second")
    assert target.read_text(encoding="utf-8") == "first"


def test_runner_reports_failed_seed(monkeypatch):
    import experiments.mandala_memory.runner as runner

    real = runner.run_seed

    def flaky(cfg, mode, seed, sizes, timings):
        if seed == 12:
            raise RuntimeError("injected failure")
        return real(cfg, mode, seed, sizes, timings)

    monkeypatch.setattr(runner, "run_seed", flaky)
    res = runner.run_experiment(small_cfg(), "smoke", TMP_OUT / "fail")
    assert res["status"] == "complete_with_failures"
    assert res["failed_seeds"] == [{"seed": 12, "error": "RuntimeError: injected failure"}]
    assert [r["seed"] for r in res["runs"]] == [11]


def test_peak_rss_measured():
    v = peak_rss_bytes()
    assert v is not None and v > 10 * 2 ** 20
