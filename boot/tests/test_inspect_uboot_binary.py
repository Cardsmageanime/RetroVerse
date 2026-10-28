"""Standalone offline tests; no bootloader, removable storage or ADB calls."""
import importlib.util
import struct
import unittest
from pathlib import Path
p = Path(__file__).resolve().parents[1] / "tools" / "inspect_uboot_binary.py"
spec = importlib.util.spec_from_file_location("inspect_binary", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LegacyBinaryTests(unittest.TestCase):
    def test_known_persistent_commands(self):
        self.assertIn("persistent-environment", m.inspect(b"saveenv\x00defenv\x00" + b"X"*8)["hazards"])
    def test_storage_modification(self):
        self.assertIn("storage-modification", m.inspect(b"mmc write 1000 0 1")["hazards"])
    def test_indirect_execution(self):
        self.assertIn("indirect-execution", m.inspect(b"run bootcmd")["hazards"])
    def test_empty_rejected(self):
        with self.assertRaises(ValueError): m.inspect(b"")
    def test_wrong_type_rejected(self):
        with self.assertRaises(ValueError): m.inspect("saveenv")
    def test_oversize_rejected(self):
        with self.assertRaises(ValueError): m.inspect(b"x" * (m.MAX_FILE + 1))
    def test_truncated_legacy_header(self):
        r = m.inspect(struct.pack(">I", m.UIMAGE_MAGIC) + b"abc")
        self.assertTrue(r["header"]["legacy_uimage_magic"])
        self.assertFalse(r["header"]["header_complete"])
    def test_legacy_header_payload_bounds(self):
        h = bytearray(64)
        struct.pack_into(">I", h, 0, m.UIMAGE_MAGIC)
        struct.pack_into(">I", h, 12, 16)
        self.assertFalse(m.inspect(bytes(h) + b"abcd")["header"]["payload_within_file"])
    def test_header_with_full_payload(self):
        h = bytearray(64)
        struct.pack_into(">I", h, 0, m.UIMAGE_MAGIC)
        struct.pack_into(">I", h, 12, 4)
        self.assertTrue(m.inspect(bytes(h) + b"abcd")["header"]["payload_within_file"])
    def test_clean_is_not_safe(self):
        r = m.inspect(b"harmless example text")
        self.assertFalse(r["safe_to_execute"])
        self.assertFalse(r["boot_authorized"])
    def test_deterministic_hash(self):
        self.assertEqual(m.inspect(b"example")["sha256"], m.inspect(b"example")["sha256"])

if __name__ == "__main__":
    unittest.main()
