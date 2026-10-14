import unittest

from reference import estimate, flags_and_rt, percentile, run_summary, summarize


def row(rt, respnum=1, respcat=1):
    return {"response_time": str(rt), "respnum": str(respnum), "respcat": str(respcat)}


class IndependentReferenceChecks(unittest.TestCase):
    def test_nonexclusive_flags_and_union(self):
        absent_zero, value = flags_and_rt(row(0, 0, -1))
        self.assertTrue(absent_zero["nonpositive_rt"])
        self.assertTrue(absent_zero["absent_response"])
        self.assertFalse(absent_zero["response_presence_disagreement"])
        self.assertIsNone(value)
        absent_positive, value = flags_and_rt(row(1.938, 0, -1))
        self.assertTrue(absent_positive["absent_response"])
        self.assertTrue(absent_positive["response_presence_disagreement"])
        self.assertIsNone(value)
        summary = run_summary([row(0, 0, -1), row(1.938, 0, -1), row(1)], "median_primary")
        self.assertEqual(summary["n_excluded_union"], 2)
        self.assertGreater(sum(summary["flag_counts"].values()), 2)
        self.assertEqual(summary["n_retained"], 1)

    def test_pair_disagreement_and_rt_edge_cases(self):
        flags, value = flags_and_rt(row(1, 1, 0))
        self.assertTrue(flags["response_code_pair_disagreement"])
        self.assertIsNone(value)
        flags, value = flags_and_rt(row("n/a", 0, -1))
        self.assertTrue(flags["missing_rt"])
        self.assertTrue(flags["absent_response"])
        self.assertFalse(flags["invalid_numeric_rt"])
        for rt in (0.2, 3.0):
            self.assertIsNotNone(flags_and_rt(row(rt), True)[1])
        for rt in (0.1, 3.1, "nan", "inf", "bad", -1):
            self.assertIsNone(flags_and_rt(row(rt), True)[1])

    def test_paired_equal_weight_not_pooled(self):
        data = {
            ("sub-01", "01"): [row(1)] * 10,
            ("sub-01", "03"): [row(3)],
            ("sub-02", "01"): [row(2)],
            ("sub-02", "03"): [row(1), row(1), row(1)],
            ("sub-03", "01"): [row(1)],
            ("sub-03", "03"): [row(0, 0, -1)],
        }
        result = summarize(data, "median_primary")
        self.assertEqual(result["eligible_participants"], ["sub-01", "sub-02"])
        self.assertEqual(result["excluded_participants"], ["sub-03"])
        self.assertEqual(result["participant_changes_ms"], {"sub-01": 2000.0, "sub-02": -1000.0})
        self.assertEqual(result["cohort"]["mean_change_ms"], 500.0)
        self.assertEqual(result["cohort"]["ci95_ms"], [-1000.0, 2000.0])

    def test_summary_variants_and_bootstrap(self):
        rows = [row(0.5), row(0.5), row(5)]
        self.assertEqual(run_summary(rows, "median_primary")["rt_ms"], 500.0)
        self.assertEqual(run_summary(rows, "mean_primary")["rt_ms"], 2000.0)
        self.assertEqual(run_summary(rows, "mean_band")["rt_ms"], 500.0)
        self.assertEqual(estimate([1, -2, 3]), estimate([1, -2, 3]))
        self.assertIsNone(estimate([1])["ci95_ms"])
        self.assertEqual(percentile([0, 10], 0.025), 0.25)


if __name__ == "__main__":
    unittest.main()
