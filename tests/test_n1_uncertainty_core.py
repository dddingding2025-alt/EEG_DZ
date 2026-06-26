import unittest

import numpy as np

from n1_uncertainty.metrics import compute_metrics
from n1_uncertainty.soft_labels import soft_targets, stage_adjacent_matrix
from n1_uncertainty.transitions import boundary_type_counts, transition_mask


class N1UncertaintyCoreTest(unittest.TestCase):
    def test_stage_adjacent_matrix(self):
        matrix = stage_adjacent_matrix(epsilon=0.1)
        self.assertEqual(matrix.shape, (5, 5))
        self.assertAlmostEqual(float(matrix[1].sum()), 1.0, places=6)
        self.assertGreater(matrix[1, 0], 0.0)
        self.assertGreater(matrix[1, 2], 0.0)

    def test_transition_mask(self):
        labels = np.asarray([0, 0, 1, 1, 2, 2, 1, 0])
        mask = transition_mask(labels, k=1)
        self.assertTrue(mask[1])
        self.assertTrue(mask[2])
        counts = boundary_type_counts(labels)
        self.assertGreaterEqual(counts["W<->N1"], 1)
        self.assertGreaterEqual(counts["N1<->N2"], 1)

    def test_soft_targets_transition_strength(self):
        labels = np.asarray([0, 1, 2])
        mask = np.asarray([False, True, False])
        targets = soft_targets(labels, epsilon=0.05, transition_mask=mask, transition_epsilon=0.2)
        self.assertLess(targets[1, 1], targets[0, 0])

    def test_metrics(self):
        labels = np.asarray([0, 1, 1, 2, 2])
        probs = np.eye(5)[labels] * 0.9 + 0.1 / 5
        metrics = compute_metrics(labels, probs, transition_mask=np.asarray([False, True, True, False, False]))
        self.assertAlmostEqual(metrics["n1_f1"], 1.0)
        self.assertIn("transition_n1_f1", metrics)


if __name__ == "__main__":
    unittest.main()
