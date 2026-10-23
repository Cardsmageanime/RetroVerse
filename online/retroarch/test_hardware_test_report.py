import unittest
from hardware_test_report import CHECKS, make_report

class ReportTests(unittest.TestCase):
    def test_unmeasured_is_incomplete(self):
        report=make_report({k:None for k in CHECKS},"Windows PC")
        self.assertEqual(report["result"],"incomplete")
    def test_partial_success_remains_incomplete(self):
        values={k:None for k in CHECKS}
        values["two_gamepads_visible_in_browser"]=True
        self.assertEqual(make_report(values)["result"],"incomplete")
    def test_failure_is_explicit(self):
        values={k:None for k in CHECKS}
        values["player_2_controls_only_player_2"]=False
        self.assertEqual(make_report(values)["result"],"failed")
    def test_full_success(self):
        self.assertEqual(make_report({k:True for k in CHECKS})["result"],"passed")
    def test_invalid_results_rejected(self):
        for values in ({}, {k:"passed" for k in CHECKS}, {k:1 for k in CHECKS}):
            with self.assertRaises(ValueError):
                make_report(values)
    def test_no_personal_data_required(self):
        result=make_report({k:None for k in CHECKS})
        self.assertNotIn("email",result)
        self.assertNotIn("ip_address",result)

if __name__=="__main__":
    unittest.main()
