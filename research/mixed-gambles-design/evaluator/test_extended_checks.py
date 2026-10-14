import copy
import json
from pathlib import Path
import unittest

from compare import expected_for
from extended_checks import audit_rows, decimal_audit, submission_consistency


class ExtendedChecks(unittest.TestCase):
    def test_decimal_presence_band_and_invalid_code(self):
        row = {"response_time": "1.938", "respnum": "0", "respcat": "-1"}
        value = decimal_audit(row)
        self.assertFalse(value["retained"])
        self.assertTrue(value["flags"]["absent_response"])
        self.assertTrue(value["flags"]["response_presence_disagreement"])
        for rt in ("0.2", "3.0"):
            self.assertTrue(decimal_audit({"response_time": rt, "respnum": "2", "respcat": "1"}, True)["retained"])
        for code in ("1.00000000000000001", "sNaN", "inf", "bad"):
            value = decimal_audit({"response_time": "1", "respnum": code, "respcat": "1"})
            self.assertTrue(value["flags"]["unexpected_response_code"])
            self.assertFalse(value["retained"])

    def test_row_audit_catches_missing_duplicate_and_wrong_flags(self):
        raw = {"response_time": "0", "respnum": "0", "respcat": "-1", "onset": "0"}
        expect = decimal_audit(raw)
        source = {"rows": [{"participant_id": "sub-01", "run": "01", "data_row": 1,
                            "raw": raw, "primary": expect, "band": decimal_audit(raw, True)}]}
        row = {"participant_id": "sub-01", "run": "01", "data_row": 1, "retained": False,
               "raw": raw, "flag_counts": {key: int(value) for key, value in expect["flags"].items()}}
        self.assertTrue(audit_rows(source, [row])["passed"])
        self.assertFalse(audit_rows(source, [row, row])["passed"])
        self.assertFalse(audit_rows(source, [])["passed"])
        wrong = copy.deepcopy(row)
        wrong["flag_counts"]["absent_response"] = 0
        self.assertFalse(audit_rows(source, [wrong])["passed"])

    def test_submitted_relations_both_stages_and_detect_changed_group_value(self):
        reference = json.loads((Path(__file__).parent / "reference-results.json").read_text())
        for stage in ("02", "03"):
            normalized = expected_for(reference, stage)
            self.assertTrue(submission_consistency(normalized)["passed"])
            wrong = copy.deepcopy(normalized)
            endpoint = wrong if stage == "02" else wrong["all_variants"]["mean_band"]
            endpoint["cohort"]["mean_change_ms"] += 1
            self.assertFalse(submission_consistency(wrong)["passed"])


if __name__ == "__main__":
    unittest.main()
