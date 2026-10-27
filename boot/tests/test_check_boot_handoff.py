"""Standalone non-writing ARM64 handoff unit tests."""
import importlib.util
from pathlib import Path
import unittest
from copy import deepcopy

p = Path(__file__).resolve().parents[1] / "tools" / "check_boot_handoff.py"
spec = importlib.util.spec_from_file_location("handoff", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
GOOD = {
    "images": {"kernel": {"address": 0x200000, "size_bytes": 0x100000},
               "dtb": {"address": 0x500000, "size_bytes": 0x10000},
               "initramfs": {"address": 0x600000, "size_bytes": 0x100000}},
    "board_identity_independently_verified": True, "bootloader_ram_map_verified": True,
    "nonpersistent_usb_loader_verified": True, "board_dtb_independently_verified": True,
    "android_emmc_unchanged_verified": True,
    "persistent_environment_changes": False, "internal_storage_writes": False,
}

class HandoffTests(unittest.TestCase):
    def test_empty_blocks(self):
        self.assertEqual(m.evaluate({})["status"], "blocked")
    def test_clean_still_not_boot_authorized(self):
        r = m.evaluate(GOOD)
        self.assertFalse(r["boot_authorized"])
        self.assertFalse(r["image_bootable"])
        self.assertFalse(r["storage_writes_authorized"])
    def test_overlap(self):
        d = deepcopy(GOOD)
        d["images"]["dtb"]["address"] = 0x200100
        self.assertTrue(any("overlap" in s for s in m.evaluate(d)["problems"]))
    def test_adjacent_ok(self):
        d = deepcopy(GOOD)
        d["images"]["dtb"]["address"] = 0x300000
        self.assertFalse(any("overlap" in s for s in m.evaluate(d)["problems"]))
    def test_overflow(self):
        d = deepcopy(GOOD)
        d["images"]["kernel"]["address"] = (1 << 64) - 1
        self.assertEqual(m.evaluate(d)["status"], "blocked")
    def test_bool_address_rejected(self):
        d = deepcopy(GOOD)
        d["images"]["kernel"]["address"] = True
        self.assertEqual(m.evaluate(d)["status"], "blocked")
    def test_zero_size(self):
        d = deepcopy(GOOD)
        d["images"]["dtb"]["size_bytes"] = 0
        self.assertEqual(m.evaluate(d)["status"], "blocked")
    def test_missing_verification(self):
        self.assertEqual(m.evaluate({**GOOD, "board_dtb_independently_verified": "true"})["status"], "blocked")
    def test_unruled_out_writes(self):
        self.assertEqual(m.evaluate({**GOOD, "internal_storage_writes": None})["status"], "blocked")
    def test_not_dict(self):
        with self.assertRaises(ValueError):
            m.evaluate([])

if __name__ == "__main__":
    unittest.main()
