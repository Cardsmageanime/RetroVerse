"""Offline tests; no USB access, flashing or booting."""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "tools" / "check_usb_boot_readiness.py"
spec = importlib.util.spec_from_file_location("usb_readiness", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
CLEAN = {key: True for key in module.REQUIRED}

class UsbReadinessTests(unittest.TestCase):
    def test_missing_evidence_blocks_all_gates(self):
        r = module.evaluate({})
        self.assertEqual(len(r["blockers"]), 6)
        self.assertEqual(r["status"], "verification-blocked")

    def test_reported_positive_checks_never_authorize_boot(self):
        r = module.evaluate(CLEAN)
        self.assertEqual(r["status"], "reported-checks-complete-review-required")
        self.assertFalse(r["boot_authorized"])
        self.assertFalse(r["hardware_boot_verified"])
        self.assertFalse(r["can_write"])

    def test_persistent_bootloader_script_blocks(self):
        r = module.evaluate({**CLEAN, "boot_script_writes_environment": True})
        self.assertEqual(r["status"], "verification-blocked")

    def test_internal_storage_write_blocks(self):
        r = module.evaluate({**CLEAN, "internal_storage_write_required": True})
        self.assertTrue(any("internal storage" in b for b in r["blockers"]))

    def test_usb_errors_block(self):
        r = module.evaluate({**CLEAN, "usb_io_errors_observed": True})
        self.assertEqual(r["status"], "verification-blocked")

    def test_borrowed_dtb_blocks(self):
        r = module.evaluate({**CLEAN, "device_tree_from_other_board": True})
        self.assertEqual(r["status"], "verification-blocked")

    def test_non_boolean_confirmation_is_rejected(self):
        r = module.evaluate({**CLEAN, "board_dtb_verified": "true"})
        self.assertEqual(r["status"], "verification-blocked")

    def test_invalid_evidence_rejected(self):
        for bad in ([], None, "ok"):
            with self.assertRaises(ValueError):
                module.evaluate(bad)

if __name__ == "__main__":
    unittest.main()
