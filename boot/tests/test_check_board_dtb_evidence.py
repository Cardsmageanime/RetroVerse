"""Unit tests for read-only board evidence gating."""
import importlib.util
from pathlib import Path
import unittest

p = Path(__file__).resolve().parents[1] / "tools" / "check_board_dtb_evidence.py"
spec = importlib.util.spec_from_file_location("board_evidence", p)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
CLEAN = {**{k: True for k in module.REQUIRED}, **{k: False for k in module.HAZARDS}}


class BoardEvidenceTests(unittest.TestCase):
    def test_missing_fields_block(self):
        r = module.evaluate({})
        self.assertEqual(len(r["blockers"]), len(module.REQUIRED) + len(module.HAZARDS))
        self.assertEqual(r["status"], "verification-blocked")

    def test_clean_report_does_not_authorize_boot(self):
        r = module.evaluate(CLEAN)
        self.assertEqual(r["status"], "reported-evidence-requires-independent-review")
        self.assertFalse(r["boot_authorized"])
        self.assertFalse(r["flash_authorized"])
        self.assertFalse(r["device_tree_approved"])

    def test_unverified_dtb_blocks(self):
        self.assertIn("A board-matched DTB has not been validated", module.evaluate({**CLEAN, "dtb_matches_board": False})["blockers"])

    def test_example_board_dtb_blocks(self):
        self.assertEqual(module.evaluate({**CLEAN, "uses_example_board_dtb": True})["status"], "verification-blocked")

    def test_unknown_hazard_blocks(self):
        self.assertEqual(module.evaluate({k: v for k, v in CLEAN.items() if k != "internal_emmc_write_required"})["status"], "verification-blocked")

    def test_gpio_guess_blocks(self):
        self.assertEqual(module.evaluate({**CLEAN, "vendor_gpio_assumed_upstream": True})["status"], "verification-blocked")

    def test_crc_errors_block(self):
        self.assertEqual(module.evaluate({**CLEAN, "unresolved_sd_crc_errors": True})["status"], "verification-blocked")

    def test_string_true_is_not_boolean(self):
        self.assertEqual(module.evaluate({**CLEAN, "board_revision_confirmed": "true"})["status"], "verification-blocked")

    def test_string_false_is_not_boolean(self):
        self.assertEqual(module.evaluate({**CLEAN, "internal_emmc_write_required": "false"})["status"], "verification-blocked")

    def test_reject_non_dict(self):
        for bad in ([], None, "text"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                module.evaluate(bad)


if __name__ == "__main__":
    unittest.main()
