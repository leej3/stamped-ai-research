"""Synthetic tests of detection, not comparisons against any worker result."""
import unittest

from compare import compare


class ComparatorChecks(unittest.TestCase):
    def test_tolerance_counts_and_missingness(self):
        self.assertEqual(compare(1.0, 1.0 + 0.5e-6)[0]["status"], "passed")
        self.assertEqual(compare(1.0, 1.0 + 2e-6)[0]["status"], "failed")
        self.assertEqual(compare(1, 1.0)[0]["status"], "failed")
        self.assertEqual(compare(1.0, float("nan"))[0]["status"], "failed")
        self.assertEqual(compare({"mean_ms": 3.0}, {})[0]["status"], "failed")

    def test_identity_order_and_wrong_direction(self):
        expected = [{"participant_id": "sub-a", "cost_ms": 3.0},
                    {"participant_id": "sub-b", "cost_ms": -2.0}]
        self.assertTrue(all(item["status"] == "passed" for item in compare(expected, expected[::-1])))
        wrong = [{"participant_id": "sub-a", "cost_ms": -3.0}, expected[1]]
        self.assertTrue(any(item["status"] == "failed" for item in compare(expected, wrong)))


if __name__ == "__main__":
    unittest.main()
