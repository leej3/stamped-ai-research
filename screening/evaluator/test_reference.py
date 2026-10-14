"""Synthetic numerical checks; no public-data endpoints and no worker outputs."""
import math
import unittest

from reference import classify, estimate, percentile, summarize


def row(condition, rt, correctness="correct"):
    return {"Stimulus": condition, "response_time": str(rt), "correctness": correctness}


class ReferenceChecks(unittest.TestCase):
    def test_missingness_and_band_boundaries(self):
        cases = [("n/a", "missing"), ("", "missing"), ("nan", "nonfinite"),
                 ("inf", "nonfinite"), ("bad", "invalid_number"),
                 (0, "nonpositive"), (-1, "nonpositive")]
        for value, expected in cases:
            self.assertEqual(classify(row("congruent", value))[0], expected)
        self.assertEqual(classify(row("congruent", 0.1, "incorrect"))[0], "incorrect")
        self.assertEqual(classify(row("unknown", 0.5))[0], "unknown_condition")
        for value in (0.2, 2.0):
            self.assertEqual(classify(row("congruent", value), True)[0], "retained")
        self.assertEqual(classify(row("congruent", 2.1), True)[0], "outside_band")

    def test_equal_participant_weight_missing_condition_and_run_pairing(self):
        data = {
            ("sub-01", "1"): [row("congruent", 1)] * 8 + [row("incongruent", 2)],
            ("sub-01", "2"): [row("congruent", 1), row("incongruent", 4), row("incongruent", 99, "incorrect")],
            ("sub-02", "1"): [row("congruent", 2), row("incongruent", 4)],
            ("sub-02", "2"): [row("congruent", 2), row("incongruent", 2), row("incongruent", "n/a")],
            ("sub-03", "1"): [row("congruent", 1)],
            ("sub-03", "2"): [row("congruent", 1), row("incongruent", 3)],
        }
        result = summarize(data, "median_primary")
        self.assertEqual(result["eligible_participants"], ["sub-01", "sub-02"])
        self.assertEqual(result["excluded_participants"], ["sub-03"])
        self.assertEqual(result["participant_costs_ms"], {"sub-01": 2000.0, "sub-02": 1000.0})
        self.assertEqual(result["cohort"]["mean_ms"], 1500.0)
        self.assertEqual(result["run2_minus_run1"]["mean_ms"], 0.0)
        self.assertEqual(result["cohort"]["ci95_ms"], [1000.0, 2000.0])

    def test_median_mean_and_deterministic_intervals(self):
        data = {(subject, run): [row("congruent", 0.5), row("incongruent", 0.7),
                                row("incongruent", 0.7), row("incongruent", 1.9)]
                for subject in ("sub-a", "sub-b") for run in ("1", "2")}
        median = summarize(data, "median_primary")["cohort"]["mean_ms"]
        mean = summarize(data, "mean_primary")["cohort"]["mean_ms"]
        self.assertAlmostEqual(median, 200.0)
        self.assertAlmostEqual(mean, 600.0)
        self.assertEqual(estimate([0.1, 0.3, -0.2]), estimate([0.1, 0.3, -0.2]))
        self.assertEqual(estimate([0.1])["ci95_ms"], None)
        self.assertEqual(estimate([])["mean_ms"], None)
        self.assertEqual(percentile([0, 10], 0.025), 0.25)


if __name__ == "__main__":
    unittest.main()
