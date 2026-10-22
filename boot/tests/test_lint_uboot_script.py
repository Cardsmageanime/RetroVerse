"""Offline tests for conservative U-Boot text linting."""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "tools" / "lint_uboot_script.py"
spec = importlib.util.spec_from_file_location("lint_uboot_script", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class LintUBootTests(unittest.TestCase):
    def test_observational_text_does_not_authorize_execution(self):
        report = module.lint_script("# inspect only\nversion\nmmc list\necho test\n")
        self.assertEqual(report["issues"], [])
        self.assertFalse(report["hardware_execution_approved"])

    def test_flash_and_environment_changes_flagged(self):
        for command in ("mmc erase 0 1", "saveenv", "setenv bootcmd something", "fatwrite mmc 0:1 x 0 4096", "store erase boot", "booti 0x1000", "run bootcmd"):
            with self.subTest(command=command):
                self.assertTrue(module.lint_script(command)["needs_manual_review"])

    def test_variable_expansion_and_command_chaining_flagged(self):
        for command in ("echo hi; saveenv", "echo $bootcmd", "echo hi && reset"):
            with self.subTest(command=command):
                self.assertTrue(module.lint_script(command)["needs_manual_review"])

    def test_unknown_command_flagged(self):
        report = module.lint_script("fatload mmc 0:1 0x01000000 Image")
        self.assertTrue(report["needs_manual_review"])

if __name__ == "__main__":
    unittest.main()
