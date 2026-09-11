"""Independent analytic limits and geometry fixtures for the exact pilot."""

import math
import tempfile
import unittest
from pathlib import Path

import numpy as np

from run_exact import all_states, block_counts, boundary_length, exact_metrics, run


class ExactCalibrationTests(unittest.TestCase):
    def test_enumeration_support_and_fixed_density(self):
        x = all_states()
        self.assertEqual(x.shape, (65536, 4, 4))
        self.assertEqual(len(np.unique(x.reshape(len(x), -1), axis=0)), 65536)
        self.assertEqual(int(np.count_nonzero(x.sum(axis=(1, 2)) == 8)), math.comb(16, 8))

    def test_identity_and_constant_observers(self):
        x = all_states(2)
        identity, _ = exact_metrics(x, np.arange(16))
        constant, _ = exact_metrics(x, np.zeros(16))
        self.assertEqual(identity["conditional_entropy_bits"], 0)
        self.assertEqual(identity["bayes_cell_error_fraction"], 0)
        self.assertEqual(constant["conditional_entropy_bits"], 4)
        self.assertEqual(constant["bayes_cell_error_fraction"], 0.5)

    def test_block_loss_matches_analytic_binomial_count(self):
        x = all_states()
        result, _ = exact_metrics(x, block_counts(x))
        expected = 4 * sum(math.comb(4, k) / 16 * math.log2(math.comb(4, k)) for k in range(5))
        self.assertAlmostEqual(result["conditional_entropy_bits"], expected, places=11)
        expected_error = sum(math.comb(4, k) / 16 * min(k, 4 - k) / 4 for k in range(5))
        self.assertAlmostEqual(result["bayes_cell_error_fraction"], expected_error, places=12)

    def test_explicit_block_orientation(self):
        x = np.zeros((1, 4, 4), dtype=np.uint8)
        x[0, :2, :2] = 1
        x[0, 2, 2] = 1
        np.testing.assert_array_equal(block_counts(x), [[4, 0, 0, 1]])

    def test_boundary_fixtures_and_symmetries(self):
        x = np.zeros((4, 4, 4), dtype=np.uint8)
        x[1, 0, 0] = 1
        x[2, :, :2] = 1
        x[3] = np.indices((4, 4)).sum(axis=0) % 2
        expected = [0, 4, 8, 32]
        np.testing.assert_array_equal(boundary_length(x), expected)
        np.testing.assert_array_equal(boundary_length(np.rot90(x, axes=(1, 2))), expected)
        np.testing.assert_array_equal(boundary_length(np.roll(x, 1, axis=1)), expected)

    def test_refinement_identity_and_nonnegative_loss(self):
        x = all_states(2)
        coarse, _ = exact_metrics(x, x.sum(axis=(1, 2)))
        refined, _ = exact_metrics(x, np.column_stack((x.sum(axis=(1, 2)), x[:, 0, 0])))
        self.assertGreaterEqual(refined["conditional_entropy_bits"], 0)
        self.assertLessEqual(refined["conditional_entropy_bits"], coarse["conditional_entropy_bits"])
        self.assertLessEqual(refined["bayes_cell_error_fraction"], coarse["bayes_cell_error_fraction"])

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            sentinel = Path(directory) / "sentinel.txt"
            sentinel.write_text("preserve me")
            with self.assertRaises(FileExistsError):
                run(Path(directory))
            self.assertEqual(sentinel.read_text(), "preserve me")


if __name__ == "__main__":
    unittest.main()
