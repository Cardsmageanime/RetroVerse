"""Tests for fail-closed, brand-neutral offline SD card preflight."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("sd_preflight", Path(__file__).resolve().parents[1] / "tools" / "check_sd_card_eligibility.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

GOOD = dict(removable_verified=True, internal_system_storage=False, target_unambiguous=True, write_protected=False, io_errors_observed=False, full_capacity_verified=True)


class EligibilityTests(unittest.TestCase):
    def test_supported_sizes(self):
        for size in (8_000_000_000, 32_000_000_000, 64_000_000_000, 128_000_000_000, 256_000_000_000, 512_000_000_000, 1_000_000_000_000):
            with self.subTest(size=size):
                result = m.evaluate({**GOOD, "capacity_bytes": size})
                self.assertEqual(result["eligibility"], "passes-observation-preflight")
                self.assertFalse(result["can_write"])

    def test_over_limit_and_one_tib(self):
        for size in (1_000_000_000_001, 1_099_511_627_776):
            self.assertIn("capacity-exceeds-1TB", m.evaluate({**GOOD, "capacity_bytes": size})["issues"])

    def test_brand_neutral(self):
        for brand in ("Popular Brand", "unknown off-brand", None):
            self.assertEqual(m.evaluate({**GOOD, "capacity_bytes": 64_000_000_000, "brand": brand})["issues"], [])

    def test_unknown_capacity_and_bad_types(self):
        for size in (None, True, "64000000000", -5, 0):
            self.assertIn("unknown-or-invalid-capacity", m.evaluate({**GOOD, "capacity_bytes": size})["issues"])

    def test_all_safety_gates_fail_closed(self):
        for key in GOOD:
            candidate = {**GOOD, "capacity_bytes": 32_000_000_000, key: None}
            with self.subTest(key=key):
                self.assertEqual(m.evaluate(candidate)["eligibility"], "blocked")
                self.assertFalse(m.evaluate(candidate)["can_write"])

    def test_internal_disk_rejected(self):
        result = m.evaluate({**GOOD, "capacity_bytes": 128_000_000_000, "internal_system_storage": True})
        self.assertIn("internal-storage-exclusion-not-verified", result["issues"])


if __name__ == "__main__":
    unittest.main()
