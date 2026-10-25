"""Tests for offline SD reliability evidence checks."""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "tools" / "check_sd_reliability.py"
spec = importlib.util.spec_from_file_location("sd_reliability", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

CLEAN = {key: True for key in module.CHECKS}

class ReliabilityTests(unittest.TestCase):
    def test_empty_evidence_fails_closed(self):
        result = module.evaluate({})
        self.assertEqual(result["status"], "verification-blocked")
        self.assertEqual(len(result["blockers"]), 4)
        self.assertFalse(result["can_write"])

    def test_crc_error_overrides_positive_fields(self):
        result = module.evaluate({**CLEAN, "gamebox_sd_crc_errors_observed": True})
        self.assertEqual(result["status"], "verification-blocked")
        self.assertIn("GameBox reported SD CRC errors", result["blockers"])

    def test_partial_windows_readback_does_not_clear_card(self):
        result = module.evaluate({"windows_hash_readback_passed": True, "windows_hash_readback_test_bytes": 268435456})
        self.assertEqual(result["status"], "verification-blocked")

    def test_clean_supplied_evidence_never_authorizes_writes(self):
        result = module.evaluate(CLEAN)
        self.assertEqual(result["status"], "no-current-blockers-in-reported-evidence")
        self.assertFalse(result["can_write"])
        self.assertFalse(result["boot_verified"])

    def test_invalid_input_rejected(self):
        with self.assertRaises(ValueError):
            module.evaluate([])

    def test_other_explicit_errors_block(self):
        result = module.evaluate({**CLEAN, "io_errors_observed": True, "capacity_mismatch_observed": True})
        self.assertIn("I/O errors observed", result["blockers"])
        self.assertIn("Capacity mismatch observed", result["blockers"])

if __name__ == "__main__":
    unittest.main()
