"""Pure offline tests for Android board survey review."""
import importlib.util
from pathlib import Path
import unittest

p = Path(__file__).resolve().parents[1] / "tools" / "review_android_board_survey.py"
spec = importlib.util.spec_from_file_location("board_survey_review", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def sample():
    return {"survey_type": "read-only-android-board-probe", "results": {
        name: {"ok": True, "value": "g12a" if name == "soc_platform" else "example"}
        for name in m.EXPECTED
    }}

class ReviewTests(unittest.TestCase):
    def test_typical_report_is_clue_only(self):
        r = m.analyze(sample())
        self.assertTrue(r["clues_not_confirmations"])
        self.assertFalse(r["boot_authorized"])
        self.assertFalse(r["dtb_matches_board"])
    def test_absent_fields_recorded(self):
        d = sample(); d["results"].pop("mmc_hosts")
        self.assertIn("mmc_hosts: missing or malformed", m.analyze(d)["missing_fields"])
    def test_failed_probe_recorded(self):
        d = sample(); d["results"]["soc_platform"] = {"ok": False, "value": "g12a"}
        self.assertIsNone(m.analyze(d)["survey_fields"]["soc_platform"])
    def test_boolean_ok_must_be_boolean(self):
        d = sample(); d["results"]["hardware"]["ok"] = "true"
        self.assertIsNone(m.analyze(d)["survey_fields"]["hardware"])
    def test_overlong_field_rejected(self):
        d = sample(); d["results"]["product_board"]["value"] = "x" * 1025
        self.assertIsNone(m.analyze(d)["survey_fields"]["product_board"])
    def test_empty_field_rejected(self):
        d = sample(); d["results"]["device_tree_model"]["value"] = ""
        self.assertIsNone(m.analyze(d)["survey_fields"]["device_tree_model"])
    def test_no_g12a_not_invented(self):
        d = sample(); d["results"]["soc_platform"]["value"] = "unknown"
        self.assertFalse(any("G12A" in x for x in m.analyze(d)["clues_not_confirmations"]))
    def test_invalid_payload_rejected(self):
        for d in ([], None, {}, {"survey_type": "other", "results": {}}):
            with self.subTest(d=d), self.assertRaises(ValueError): m.analyze(d)
    def test_missing_results_rejected(self):
        with self.assertRaises(ValueError):
            m.analyze({"survey_type": "read-only-android-board-probe"})
    def test_never_authorizes_writes(self):
        self.assertFalse(m.analyze(sample())["storage_write_authorized"])

if __name__ == "__main__":
    unittest.main()
