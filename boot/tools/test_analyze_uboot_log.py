import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "boot" / "tools" / "analyze_uboot_log.py"
spec = importlib.util.spec_from_file_location("analyze_uboot_log", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class UBootLogAnalysisTests(unittest.TestCase):
    def test_reports_text_markers_without_claiming_boot_readiness(self):
        report = module.analyze_text(
            "U-Boot 2015.01-g51e6fd64e9-dirty\n"
            "Model: Amlogic G12A candidate\n"
            "mmc0 is current device\n"
            "fatload mmc 0:1 0x01000000 aml_autoscript\n"
            "## Executing script at 01000000\n"
            "bootm 0x01000000\n"
            "Starting kernel ...\n"
        )
        self.assertEqual(report["observations"]["uboot_version"], "2015.01-g51e6fd64e9-dirty")
        self.assertEqual(report["observations"]["board_model"], "Amlogic G12A candidate")
        self.assertEqual(report["observations"]["mmc_index_tokens_seen"], ["0"])
        self.assertTrue(report["observations"]["sd_load_text_marker_seen"])
        self.assertTrue(report["observations"]["autoscript_text_marker_seen"])
        self.assertTrue(report["observations"]["boot_handoff_text_marker_seen"])
        self.assertTrue(report["observations"]["linux_start_text_marker_seen"])
        self.assertFalse(report["readiness"]["external_uboot_boot_path_verified"])
        self.assertFalse(report["readiness"]["external_sd_boot_verified"])
        self.assertFalse(report["readiness"]["can_flash"])

    def test_reports_write_risk_tokens_as_review_flags_only(self):
        report = module.analyze_text("saveenv\nnand erase 0x0 0x1000\n")
        self.assertTrue(report["observations"]["persistent_environment_write_text_marker_seen"])
        self.assertTrue(report["observations"]["flash_or_erase_text_marker_seen"])
        self.assertTrue(report["manual_review_required"])
        self.assertFalse(report["readiness"]["can_flash"])

    def test_does_not_copy_raw_log_lines_into_report(self):
        secret = "MAC=aa:bb:cc:dd:ee:ff SERIAL=private-unit-123"
        report = module.analyze_text(f"Model: TVBOX-GAME\n{secret}\n")
        rendered = str(report)
        self.assertNotIn("aa:bb:cc:dd:ee:ff", rendered)
        self.assertNotIn("private-unit-123", rendered)
        self.assertFalse(report["raw_log_lines_included"])

    def test_empty_log_stays_unverified(self):
        report = module.analyze_text("")
        self.assertEqual(report["input"]["line_count"], 0)
        self.assertEqual(report["observations"]["mmc_index_tokens_seen"], [])
        self.assertFalse(report["readiness"]["external_uboot_boot_path_verified"])


if __name__ == "__main__":
    unittest.main()
