"""Review REVIEW_LR4 (Astra, reviewed 027fc0c / 18a89c3): one regression per reproduced counterexample
(R1 constant training column, R2 metadata accepted by the loader, model arrays re-writable), with the
review's exact inputs, plus positive controls that valid fits are unchanged."""
from __future__ import annotations

import json
from dataclasses import replace

import numpy as np
import pytest

from experiments.lantern_reconstruction import contexts, decoders, observation, streams, training
from experiments.lantern_reconstruction.contexts import fingerprint

SID = streams.defaults()["development_study_id"]


@pytest.fixture(scope="module")
def ctx():
    return contexts.make_context(SID, 0)


@pytest.fixture(scope="module")
def review_model(ctx):
    """The review's construction: seed 7654, 20 x 16 features, first 12 train, last 8 validation, task B."""
    spec = observation.observation_spec(ctx, "B")
    rng = np.random.default_rng(7654)
    x, u = rng.normal(size=(20, 16)), rng.uniform(-1, 1, (20, 4))
    prov = {"study_id": ctx.study_id, "context_id": ctx.context_id, "context_fingerprint": fingerprint(ctx),
            "config_sha256": streams.config_sha256(), "task": "B", "condition": "lantern", "time": 1.0}
    return training.fit_ridge(spec, x[:12], u[:12], x[12:], u[12:], provenance=prov), x


# --- R1 ----------------------------------------------------------------------------------------------
@pytest.mark.parametrize("n", [1000, 3, 7, 10, 2])
def test_r1_exactly_constant_column_gets_scale_one(n):
    """Review: np.full((1000, 1), 0.1) gave scale 1.3877787807814457e-17 instead of 1 (also n = 3, 7)."""
    x = np.full((n, 1), 0.1)
    assert n == 10 or np.std(x, axis=0)[0] != 0.0 or n == 2      # NumPy's own SD is not exactly 0 for most n
    mean, scale = training.standardisation(x)
    assert scale.tolist() == [1.0] and mean.tolist() == [0.1]
    assert np.all((x - mean) / scale == 0.0)                           # standardises to EXACTLY zero


def test_r1_nearly_constant_varying_column_keeps_its_true_sd():
    x = np.full((1000, 3), 0.1)
    x[-1, 0] += 1e-12                                                  # varies: no epsilon threshold may swallow it
    x[:, 1] = np.linspace(-1, 1, 1000)
    mean, scale = training.standardisation(x)
    old_mean, old_sd = x.mean(axis=0), x.std(axis=0, ddof=0)            # the previous rule (same summation order)
    assert scale[0] == old_sd[0] and 0 < scale[0] < 1e-12 and scale[2] == 1.0
    assert mean[0] == old_mean[0] and mean[1] == old_mean[1] and scale[1] == old_sd[1]   # varying columns exactly as before


def test_r1_varying_columns_bit_identical_to_the_previous_rule():
    rng = np.random.default_rng(11)
    x = rng.normal(size=(250, 66)) * rng.uniform(.01, 10, 66) + rng.uniform(-3, 3, 66)
    mean, scale = training.standardisation(x)
    old_sd = x.std(axis=0, ddof=0)
    assert np.array_equal(mean, x.mean(axis=0)) and np.array_equal(scale, np.where(old_sd == 0.0, 1.0, old_sd))


def test_r1_constant_column_cannot_amplify_a_later_deviation(ctx):
    """A training column of 0.1 that deviates by 1e-9 in validation/test must not move predictions."""
    spec = observation.observation_spec(ctx, "B")
    rng = np.random.default_rng(12)
    Xtr, Xva = rng.normal(size=(12, 16)), rng.normal(size=(8, 16))
    Xtr[:, 3] = 0.1
    Xva[:, 3] = 0.1
    m = training.fit_ridge(spec, Xtr, rng.uniform(-1, 1, (12, 4)), Xva, rng.uniform(-1, 1, (8, 4)))
    assert m.scale[3] == 1.0 and m.mean[3] == 0.1
    shifted = Xva.copy()
    shifted[:, 3] += 1e-9
    assert np.max(np.abs(decoders.predict(m, shifted) - decoders.predict(m, Xva))) < 1e-12


# --- R2 ----------------------------------------------------------------------------------------------
def _tamper(tmp_path, model, change):
    decoders.save(model, tmp_path / "m")
    meta = json.loads((tmp_path / "m.json").read_text(encoding="utf-8"))
    change(meta)
    (tmp_path / "m.json").write_text(json.dumps(meta), encoding="utf-8")
    return tmp_path / "m"


def test_r2_review_counterexample_negative_n_train_and_reference(review_model, tmp_path):
    m, _ = review_model
    with pytest.raises(ValueError, match="n_train"):
        decoders.load(_tamper(tmp_path, m, lambda d: d.__setitem__("n_train", -5)))
    with pytest.raises(ValueError, match="reference"):
        decoders.load(_tamper(tmp_path, m, lambda d: d["feature_definition"].__setitem__("reference", -1)))


def test_r2_foreign_context_id_needs_the_expected_cell(review_model, ctx, tmp_path):
    """context_id 999 is syntactically valid: the loader cannot know it is wrong (no LR5 manifest yet), the
    context-bound check against the expected cell rejects it."""
    m, _ = review_model
    back = decoders.load(_tamper(tmp_path, m, lambda d: d["provenance"].__setitem__("context_id", 999)))
    assert back.provenance["context_id"] == 999
    with pytest.raises(ValueError, match="provenance"):
        decoders.check_decoder_for(back, ctx, "B", condition="lantern", time=1.0)
    decoders.check_decoder_for(m, ctx, "B", condition="lantern", time=1.0)             # the original passes
    with pytest.raises(ValueError, match="provenance"):
        decoders.check_decoder_for(m, ctx, "B", condition="uncoupled", time=1.0)        # another expected cell
    with pytest.raises(ValueError, match="observation spec"):
        decoders.check_decoder_for(m, contexts.make_context(SID, 1), "B")               # other context's nodes


@pytest.mark.parametrize("change, match", [
    (lambda d: d.__setitem__("n_val", 0), "n_val"),
    (lambda d: d.__setitem__("n_train", True), "n_train"),
    (lambda d: d.__setitem__("n_train", 12.0), "n_train"),
    (lambda d: d["feature_definition"].__setitem__("nodes", d["feature_definition"]["nodes"][:-1] + [d["feature_definition"]["nodes"][0]]), "distinct"),
    (lambda d: d["feature_definition"].__setitem__("nodes", [34] + d["feature_definition"]["nodes"][1:]), "nodes"),
    (lambda d: d["feature_definition"].__setitem__("nodes", d["feature_definition"]["nodes"][:-1]), "nodes"),
    (lambda d: d["feature_definition"].__setitem__("reference", d["feature_definition"]["nodes"][0]), "reference"),
    (lambda d: d["feature_definition"].__setitem__("task", "A"), "task"),
    (lambda d: d["feature_definition"].__setitem__("order", "cos first"), "order"),
    (lambda d: d["feature_definition"].__setitem__("extra", 1), "exactly the keys"),
    (lambda d: d.__setitem__("lambda", True), "lambda"),
    (lambda d: d["provenance"].__setitem__("context_id", [0]), "provenance"),
    (lambda d: d["software"].__setitem__("numpy", {"v": 1}), "software"),
])
def test_r2_metadata_values_validated_on_load(review_model, tmp_path, change, match):
    with pytest.raises(ValueError, match=match):
        decoders.load(_tamper(tmp_path, review_model[0], change))


def test_r2_json_true_is_not_lambda_one(tmp_path):
    """Mutation check: with a selected lambda of 1.0, JSON true would pass as float(True) == 1.0."""
    A_like = {"task": "A", "nodes": list(range(1, 34)), "reference": 0, "order": decoders.FEATURE_ORDER}
    m = decoders.RidgeDecoder("A", A_like, np.zeros(66), np.ones(66), np.zeros((66, 4)), np.zeros(4), 1.0,
                              np.array([1.0]), np.array([0.3]), 5, 5)
    decoders.load(_tamper(tmp_path, m, lambda d: None))                                   # untouched copy loads
    with pytest.raises(ValueError, match="JSON number"):
        decoders.load(_tamper(tmp_path, m, lambda d: d.__setitem__("lambda", True)))


def test_r2_direct_construction_is_validated(review_model):
    m, _ = review_model
    for kw, match in (({"n_train": -5}, "n_train"), ({"n_val": np.bool_(True)}, "n_val"),
                      ({"feature_definition": {**m.feature_definition, "reference": -1}}, "reference"),
                      ({"lambda_grid": -m.lambda_grid}, "lambda grid|selection"),
                      ({"lambda_grid": np.array([1.0] * 7), "lam": 1.0}, "distinct"),
                      ({"val_mse": m.val_mse + 5}, r"\[0, 4\]"), ({"val_mse": m.val_mse - 5}, r"\[0, 4\]"),
                      ({"task": "A"}, "task")):
        with pytest.raises(ValueError, match=match):
            replace(m, **kw)
    A_like = {"task": "A", "nodes": list(range(1, 34)), "reference": 0, "order": decoders.FEATURE_ORDER}
    with pytest.raises(ValueError, match="ascending"):
        decoders.RidgeDecoder("A", {**A_like, "nodes": list(range(33, 0, -1))}, np.zeros(66), np.ones(66), np.zeros((66, 4)),
                              np.zeros(4), 1.0, np.array([1.0]), np.array([0.3]), 5, 5)
    decoders.RidgeDecoder("A", A_like, np.zeros(66), np.ones(66), np.zeros((66, 4)), np.zeros(4), 1.0, np.array([1.0]), np.array([0.3]), 5, 5)


def test_runner_binds_every_model_to_its_cell(ctx, monkeypatch):
    from experiments.lantern_reconstruction import registry_adapter as ra
    from experiments.lantern_reconstruction import runner
    s = ra.load_verified_snapshot()
    seen, real = [], runner.check_decoder_for
    monkeypatch.setattr(runner, "check_decoder_for", lambda m, c, task, **cell: seen.append((task, cell)) or real(m, c, task, **cell))
    runner.run_context(ctx, np.array(s.C), float(s.structure["g"]), sizes={"train": 30, "val": 12, "test": 20},
                       conditions=("uncoupled",), proposals=100)
    assert len(seen) == 2 * 7 and {c["condition"] for _, c in seen} == {"uncoupled"} and {t for t, _ in seen} == {"A", "B"}
    assert sorted({c["time"] for _, c in seen}) == [0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0]


def test_model_arrays_and_metadata_cannot_be_rewritten(review_model):
    """Review: m.W.setflags(write=True); m.W[:] = 0 changed predict() -- now refused, like the LR1 snapshot fix."""
    m, x = review_model
    before = decoders.predict(m, x[:3]).copy()
    for name in decoders.ARRAYS:
        with pytest.raises(ValueError):
            getattr(m, name).setflags(write=True)
        with pytest.raises(ValueError):
            getattr(m, name)[...] = 0
    with pytest.raises(TypeError):
        m.feature_definition["reference"] = -1
    with pytest.raises(TypeError):
        m.provenance["context_id"] = 999
    assert np.array_equal(decoders.predict(m, x[:3]), before)
