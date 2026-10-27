"""U-Boot static audit tests: no hardware interaction."""
import importlib.util
from pathlib import Path
import unittest

p = Path(__file__).resolve().parents[1] / "tools" / "inspect_uboot_script.py"
spec = importlib.util.spec_from_file_location("uboot", p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class UBootAuditTests(unittest.TestCase):
    def kinds(self, text):
        return {x["kind"] for x in mod.inspect(text)["findings"]}
    def test_known_reference_hazards(self):
        self.assertIn("persistent-environment", self.kinds("defenv\nsaveenv\nsetenv bootcmd run distro_bootcmd"))
    def test_storage_write(self):
        self.assertIn("storage-write-or-erase", self.kinds("mmc write 0x10000 0 10"))
    def test_spi_erase(self):
        self.assertIn("storage-write-or-erase", self.kinds("sf erase 0 100"))
    def test_env_save(self):
        self.assertIn("persistent-environment", self.kinds("env save"))
    def test_case_insensitive(self):
        self.assertIn("persistent-environment", self.kinds("SAVEENV"))
    def test_control_flow_requires_review(self):
        self.assertIn("manual-control-flow-review", self.kinds("run boot_sequence"))
    def test_no_matches_still_unsafe_to_execute(self):
        r = mod.inspect("echo Hello")
        self.assertEqual(r["status"], "manual-review-required")
        self.assertFalse(r["safe_to_execute"])
    def test_multiline(self):
        self.assertIn("persistent-environment", self.kinds("setenv \\\nbootcmd echo hello"))
    def test_bad_type(self):
        with self.assertRaises(ValueError): mod.inspect(None)
    def test_upgrade_step(self):
        self.assertIn("persistent-boot-control", self.kinds("setenv upgrade_step 2"))

if __name__ == "__main__":
    unittest.main()
