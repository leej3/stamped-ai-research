import unittest
from compare import compare


class ComparisonChecks(unittest.TestCase):
    def test_counts_tolerance_and_missing_fields(self):
        self.assertEqual(compare(2, 2.0)[0]["status"], "passed")
        self.assertEqual(compare(2, 2.000001)[0]["status"], "failed")
        self.assertEqual(compare(1, True)[0]["status"], "failed")
        self.assertEqual(compare(1.0, 1.0 + 0.5e-6)[0]["status"], "passed")
        self.assertEqual(compare(1.0, 1.0 + 2e-6)[0]["status"], "failed")
        self.assertEqual(compare(1.0, float("nan"))[0]["status"], "failed")
        self.assertEqual(compare({"n_excluded_union": 2}, {})[0]["status"], "failed")

    def test_canonical_order_and_wrong_sign(self):
        expected = [{"participant_id": "a", "run": "01", "rt_ms": 20.0},
                    {"participant_id": "b", "run": "01", "rt_ms": 10.0}]
        self.assertTrue(all(c["status"] == "passed" for c in compare(expected, expected[::-1])))
        self.assertEqual(compare(20.0, -20.0)[0]["status"], "failed")


if __name__ == "__main__":
    unittest.main()
