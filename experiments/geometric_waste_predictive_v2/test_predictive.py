"""Regression and reference checks using hand fixtures/development families only.

Run: python -m unittest -v test_predictive
No held-out generator is called, and no approved review record is fabricated.
"""

import runner  # Configure numerical threads before importing NumPy.

import argparse
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np

import model


def direct_step(x):
    """Independent, explicit cell-wise reference (no roll or vectorization)."""
    n = len(x)
    out = np.zeros_like(x)
    for r in range(n):
        for c in range(n):
            neighbours = sum(int(x[(r + a) % n, (c + b) % n])
                             for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b)
            out[r, c] = neighbours == 3 or (x[r, c] == 1 and neighbours == 2)
    return out


def brute_key(x):
    candidates = []
    for k in range(4):
        for oriented in (np.rot90(x, k), np.rot90(x, k)[:, ::-1]):
            for r in range(len(x)):
                for c in range(len(x)):
                    candidates.append(tuple(np.roll(oriented, (r, c), (0, 1)).ravel()))
    cells = np.array(min(candidates)).reshape(x.shape)
    return b"".join(int("".join(str(int(v)) for v in row), 2).to_bytes(2, "big")
                    for row in cells)


class DynamicsAndSensors(unittest.TestCase):
    def test_empty_and_still_life(self):
        empty = np.zeros((16, 16), dtype=np.uint8)
        block = empty.copy()
        block[5:7, 5:7] = 1
        np.testing.assert_array_equal(model.step(np.array([empty, block])), [empty, block])

    def test_blinker_and_periodic_transition(self):
        x = np.zeros((16, 16), dtype=np.uint8)
        x[0, [15, 0, 1]] = 1
        expected = np.zeros_like(x)
        expected[[15, 0, 1], 0] = 1
        np.testing.assert_array_equal(model.step(x), expected)
        np.testing.assert_array_equal(model.step(expected), x)

    def test_full_state_reference_zero_error(self):
        states = [model.make_state(f, np.random.default_rng(991))[0]
                  for f in model.DEVELOPMENT_FAMILIES]
        reference = np.asarray([direct_step(x) for x in states])
        np.testing.assert_array_equal(model.step(states), reference)
        self.assertEqual(model.mae(model.block_fractions(reference),
                                   model.block_fractions(model.step(states))), 0)

    def test_block_order_and_micro_windows(self):
        x = np.zeros((16, 16), dtype=np.uint8)
        for index in range(16):
            r, c = divmod(index, 4)
            local = np.zeros(16, dtype=np.uint8)
            local[:index] = 1
            x[r*4:r*4+4, c*4:c*4+4] = local.reshape(4, 4)
        np.testing.assert_array_equal(model.block_fractions(x)[0], np.arange(16)/16)
        x[:] = 0
        for count, (r, c) in enumerate(((0, 0), (0, 8), (8, 0), (8, 8))):
            for a, b in ((3, 3), (3, 4), (4, 3), (4, 4))[:count]:
                x[r+a, c+b] = 1
        np.testing.assert_array_equal(model.features(x)["MICRO"][0, -4:], np.arange(4)/3)
        x[11:13, 11:13] = 1
        self.assertEqual(model.features(x)["MICRO"][0, -1], 1)

    def test_boundaries_exclude_seams_and_cover_quantizer(self):
        x = np.zeros((16, 16), dtype=np.uint8)
        x[:, 8:] = 1
        np.testing.assert_array_equal(model.quadrant_boundaries(x), [[0, 0, 0, 0]])
        checker = np.indices((16, 16)).sum(axis=0) % 2
        np.testing.assert_array_equal(model.quadrant_boundaries(checker), [[112]*4])
        np.testing.assert_array_equal(model.features(checker)["GEOMETRY"][0, -4:], 1)
        for count in range(113):
            with patch.object(model, "quadrant_boundaries", return_value=np.full((1, 4), count)):
                got = model.features(x)["GEOMETRY"][0, -1] * 3
            expected = sum(count >= threshold for threshold in (29, 57, 85))
            self.assertEqual(got, expected)

    def test_coarse_redundancy_and_sensor_ranges(self):
        rng = np.random.default_rng(27)
        x = np.stack([model.make_state("iid", rng)[0] for _ in range(8)])
        permuted = x.reshape(-1, 4, 4, 4, 4).copy()
        permuted = permuted[:, :, ::-1, :, ::-1].reshape(-1, 16, 16)
        before, after = model.features(x), model.features(permuted)
        np.testing.assert_array_equal(before["COARSE"], after["COARSE"])
        for values in before.values():
            self.assertEqual(values.shape, (8, 20))
            self.assertTrue(np.all((values >= 0) & (values <= 1)))
            np.testing.assert_array_equal(values[:, :16]*16, np.round(values[:, :16]*16))
            np.testing.assert_array_equal(values[:, 16:]*3, np.round(values[:, 16:]*3))

    def test_shuffle_moves_whole_side_channel_rows_only(self):
        rng = np.random.default_rng(883)
        x = np.stack([model.make_state(f, rng)[0] for f in model.DEVELOPMENT_FAMILIES for _ in range(4)])
        observed = model.features(x, np.random.default_rng(117))
        order = np.random.default_rng(117).permutation(len(x))
        np.testing.assert_array_equal(observed["SHUFFLED"][:, :16], observed["BASE"][:, :16])
        np.testing.assert_array_equal(observed["SHUFFLED"][:, 16:], observed["GEOMETRY"][order, 16:])


class Sampling(unittest.TestCase):
    def test_canonical_key_matches_independent_small_grid_enumeration(self):
        for value in (0, 1, 0x1327, 0xAAAA, 0xEF12, 0xFFFF):
            x = np.unpackbits(np.frombuffer(value.to_bytes(2, "big"), dtype=np.uint8)).reshape(4, 4)
            self.assertEqual(model.canonical_key(x), brute_key(x))

    def test_canonical_key_symmetry_and_no_complement_identification(self):
        x = np.zeros((16, 16), dtype=np.uint8)
        x[1, 3] = x[4, 7] = x[6, 8] = 1
        key = model.canonical_key(x)
        for k in range(4):
            for flip in (False, True):
                y = np.rot90(x, k)
                if flip:
                    y = y[:, ::-1]
                self.assertEqual(key, model.canonical_key(np.roll(y, (13, 7), (0, 1))))
        self.assertNotEqual(key, model.canonical_key(1-x))

    def test_development_generator_density_and_reproducibility(self):
        for f in model.DEVELOPMENT_FAMILIES:
            a, metadata = model.make_state(f, np.random.default_rng(335))
            b, other = model.make_state(f, np.random.default_rng(335))
            self.assertEqual(int(a.sum()), 128)
            np.testing.assert_array_equal(a, b)
            self.assertEqual(metadata, other)

    def test_development_rejects_test_access_before_generator_call(self):
        config = runner.load_config()
        with patch.object(model, "make_state") as generate:
            for split in ("test_known", "test_unseen"):
                with self.assertRaises(ValueError):
                    model.generate_split(config, 0, split, set(), development=True)
            with self.assertRaises(ValueError):
                model.generate_split(config, 1, "train", set(), development=True)
            config["sampling"]["splits"]["train"]["counts"]["tiles"] = 1
            with self.assertRaises(ValueError):
                model.generate_split(config, 0, "train", set(), development=True)
            generate.assert_not_called()

    def test_split_registry_and_rng_reconstruction(self):
        config = runner.load_config()
        for split in ("train", "validation"):
            config["sampling"]["splits"][split]["counts"] = {f: 2 for f in model.DEVELOPMENT_FAMILIES}
        registry = set()
        first = model.generate_split(config, 0, "train", registry, development=True)
        second = model.generate_split(config, 0, "validation", registry, development=True)
        self.assertEqual(len(registry), 12)
        self.assertFalse(set(first[2]) & set(second[2]))
        for mask, record in zip(first[0], first[1]):
            rng = np.random.Generator(np.random.PCG64())
            rng.bit_generator.state = record["rng_state_before"]
            np.testing.assert_array_equal(mask, model.make_state(record["family"], rng)[0])

    def test_duplicate_rejection_records_and_bound(self):
        config = runner.load_config()
        config["sampling"]["splits"]["train"]["counts"] = {"iid": 1}
        x, _ = model.make_state("iid", np.random.default_rng(70))
        y, _ = model.make_state("iid", np.random.default_rng(71))
        with patch.object(model, "make_state", side_effect=[(x, {"family":"iid"}), (y, {"family":"iid"})]):
            result = model.generate_split(config, 0, "train", {model.canonical_key(x)}, development=True)
        self.assertEqual(result[3], {"iid": 1})
        with patch.object(model, "make_state", return_value=(x, {})), \
             patch.object(model, "canonical_key", return_value=b"duplicate"):
            with self.assertRaisesRegex(RuntimeError, "Duplicate rejection limit"):
                model.generate_split(config, 0, "train", {b"duplicate"}, development=True)

    def test_packed_state_roundtrip(self):
        x = np.indices((16, 16)).sum(axis=0) % 2
        np.testing.assert_array_equal(runner.unpack_states(runner.pack_states([x, 1-x])), [x, 1-x])


class LearningAndInference(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(302)
        self.x = rng.uniform(size=(40, 20))
        self.y = rng.uniform(size=(40, 16))
        self.v = rng.uniform(size=(12, 20))
        self.vy = rng.uniform(size=(12, 16))

    def test_ridge_matches_augmented_normal_equations(self):
        fitted = model.fit_ridge(self.x, self.y, self.v, self.vy, [0.01])
        raw = model.polynomial(self.x)
        a = np.column_stack((np.ones(len(raw)), (raw-raw.mean(0))/raw.std(0)))
        penalty = np.diag([0] + [len(a)*0.01]*230)
        independent = np.linalg.solve(a.T @ a + penalty, a.T @ self.y)
        np.testing.assert_allclose(fitted["intercept"], independent[0], atol=1e-11)
        np.testing.assert_allclose(fitted["coefficients"], independent[1:], atol=1e-11)
        self.assertEqual(raw.shape, (40, 230))
        self.assertLessEqual(fitted["effective_degrees_of_freedom"], fitted["design_rank"] + 1e-10)

    def test_train_only_normalization_and_constant_columns(self):
        self.x[:, 19] = 1/3
        fitted = model.fit_ridge(self.x, self.y, self.v, self.vy, [0.01])
        np.testing.assert_array_equal(fitted["mean"], model.polynomial(self.x).mean(0))
        changed = self.v.copy()
        constant = fitted["constant_columns"]
        self.assertIn(19, constant)
        self.assertIn(229, constant)  # z_19 squared is also constant on training.
        # Zeroing these columns is explicit even when an external input differs.
        expanded = model.polynomial(self.v)
        normalized = (expanded-fitted["mean"])/fitted["scale"]
        normalized[:, constant] = 0
        expected = np.clip(normalized @ fitted["coefficients"] + fitted["intercept"], 0, 1)
        np.testing.assert_array_equal(model.predict(fitted, self.v), expected)
        predicted = model.predict(fitted, self.v * 900)
        self.assertTrue(np.all((predicted >= 0) & (predicted <= 1)))

    def test_lambda_and_comparator_ties(self):
        fitted = model.fit_ridge(np.zeros((5, 20)), np.full((5, 16), .5),
                                  np.zeros((3, 20)), np.full((3, 16), .5), [1e-6, .01, 1])
        self.assertEqual(fitted["lambda"], 1)
        self.assertEqual(fitted["design_rank"], 1)
        self.assertEqual(model.choose_comparator(dict.fromkeys(model.COMPARATORS, .2)), "BASE")
        self.assertEqual(model.choose_comparator({"BASE": .3, "MICRO": .2, "COARSE": .1, "PERSISTENCE": .4}), "COARSE")

    def test_external_target_changes_do_not_change_features_or_fit(self):
        # Hand-made probe states/labels are not any scientific test split.
        states = np.array([np.indices((16, 16)).sum(0) % 2])
        observed = model.features(states)
        before = model.fit_ridge(self.x, self.y, self.v, self.vy, [.01, 1])
        probe_targets = np.zeros((1, 16))
        first_loss = model.mae(probe_targets, model.predict(before, observed["BASE"]))
        probe_targets[:] = 1
        second_loss = model.mae(probe_targets, model.predict(before, observed["BASE"]))
        after = model.fit_ridge(self.x, self.y, self.v, self.vy, [.01, 1])
        self.assertNotEqual(first_loss, second_loss)
        self.assertEqual(before, after)
        for name in observed:
            np.testing.assert_array_equal(observed[name], model.features(states)[name])
        scores = {"BASE": before["validation_mae"], "MICRO": 1, "COARSE": 1, "PERSISTENCE": 1}
        self.assertEqual(model.choose_comparator(scores), "BASE")

    def test_bootstrap_constant_and_seeded_paired_reference(self):
        np.testing.assert_allclose(model.repeat_bootstrap([.04]*20, 10000, 42), [.04, .04])
        values = np.arange(20)/100
        rng = np.random.Generator(np.random.PCG64(772))
        means = [np.mean(values[rng.integers(20, size=20)]) for _ in range(10000)]
        expected = np.quantile(means, [.025, .975], method="linear")
        np.testing.assert_array_equal(model.repeat_bootstrap(values, 10000, 772), expected)

    def test_aggregation_support_heterogeneity_and_zero_denominator(self):
        config = runner.load_config()
        rows = []
        for repeat in range(20):
            splits = {}
            for split in ("test_known", "test_unseen"):
                splits[split] = {f: dict.fromkeys((*model.OBSERVERS, "PERSISTENCE"), .2)
                                 for f in config["sampling"]["splits"][split]["counts"]}
                for scores in splits[split].values():
                    scores["GEOMETRY"] = .1
                    scores["SHUFFLED"] = 0
            rows.append({"repeat": repeat, "selected_comparator": "BASE", "splits": splits})
        result = runner.aggregate(config, rows)
        self.assertTrue(result["support_all_conditions"])
        self.assertAlmostEqual(result["mean_delta"], .1)
        self.assertEqual(result["secondary_descriptive_only"]["test_unseen"]["SHUFFLED"]["relative_improvement_by_repeat"], [None]*20)
        for row in rows:
            row["splits"]["test_unseen"]["tiles"]["GEOMETRY"] = .22
        result = runner.aggregate(config, rows)
        self.assertFalse(result["support_all_conditions"])
        self.assertFalse(result["family_guard_passed"])
        with self.assertRaises(ValueError):
            runner.aggregate(config, rows[:-1])
        rows[1]["repeat"] = 0
        with self.assertRaises(ValueError):
            runner.aggregate(config, rows)


class CheckpointsAndGates(unittest.TestCase):
    def test_atomic_preservation_integrity_and_no_partial_on_invalid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"state.json"
            runner.write_once(path, {"answer": 42})
            original = path.read_bytes()
            with self.assertRaises(FileExistsError):
                runner.write_once(path, {"answer": 43})
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(runner.read(path), {"answer": 42})
            tampered = json.loads(original)
            tampered["answer"] = 43
            path.write_text(json.dumps(tampered))
            with self.assertRaisesRegex(ValueError, "checksum"):
                runner.read(path)
            with self.assertRaises(ValueError):
                runner.write_once(Path(directory)/"nan.json", {"value": float("nan")})
            self.assertEqual(len(list(Path(directory).iterdir())), 1)

    def test_resume_requires_identical_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"run"
            expected = runner.open_run(path, "development", "a"*40)
            self.assertEqual(expected, runner.open_run(path, "development", "a"*40, resume=True))
            with self.assertRaises(FileExistsError):
                runner.open_run(path, "development", "a"*40)
            with self.assertRaises(ValueError):
                runner.open_run(path, "development", "b"*40, resume=True)

    def test_missing_reviews_block_evaluation_before_data_or_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"untouched"
            args = argparse.Namespace(stage="evaluate", output=path, reviews=None,
                                      code_commit="a"*40, resume=False)
            with patch.object(runner, "generate_split") as generator, \
                 patch.object(runner, "evaluate_repeat") as evaluate:
                with self.assertRaisesRegex(ValueError, "review evidence"):
                    runner.execute(args)
                generator.assert_not_called()
                evaluate.assert_not_called()
            self.assertFalse(path.exists())

    def test_review_record_without_reports_is_insufficient(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"reviews.json"
            record = {k: v for k, v in runner.signature("confirmatory", "a"*40).items()
                      if k.endswith("sha256")}
            path.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "Missing approved review"):
                runner.verify_reviews(path, runner.load_config())

    def test_output_cap_prevents_publish(self):
        with tempfile.TemporaryDirectory() as directory:
            budget = object.__new__(runner.Budget)
            budget.output = Path(directory)
            budget.disk_limit = 65536 + 100
            with patch.object(runner, "ACTIVE_BUDGET", budget):
                with self.assertRaisesRegex(RuntimeError, "storage limit"):
                    runner.write_once(Path(directory)/"large.json", {"value": "x"*100})
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
