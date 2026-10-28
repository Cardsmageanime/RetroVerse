"""Tests of offline-only reference-copy inventory."""
import importlib.util
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "tools" / "reference_inventory.py"
spec = importlib.util.spec_from_file_location("inventory", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def image(payload=b"hello"):
    h = bytearray(64)
    struct.pack_into(">I", h, 0, m.MAGIC)
    struct.pack_into(">I", h, 12, len(payload))
    struct.pack_into(">I", h, 24, zlib.crc32(payload))
    struct.pack_into(">I", h, 4, zlib.crc32(h))
    return bytes(h) + payload

class InventoryTests(unittest.TestCase):
    def test_absent_files_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            r = m.analyze(Path(td))
            self.assertEqual(len(r["missing_or_unreadable"]), 4)
            self.assertFalse(r["boot_authorized"])
    def test_valid_uimage(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/"aml_autoscript").write_bytes(image())
            r = m.analyze(Path(td))
            self.assertTrue(r["files"]["aml_autoscript"]["legacy_uimage"]["header_crc_valid"])
            self.assertTrue(r["files"]["aml_autoscript"]["legacy_uimage"]["payload_crc_valid"])
    def test_broken_payload(self):
        with tempfile.TemporaryDirectory() as td:
            data = bytearray(image()); data[-1] ^= 1
            (Path(td)/"aml_autoscript").write_bytes(data)
            r = m.analyze(Path(td))
            self.assertFalse(r["files"]["aml_autoscript"]["legacy_uimage"]["payload_crc_valid"])
    def test_unknown_magic(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/"aml_autoscript").write_bytes(b"not uimage")
            self.assertFalse(m.analyze(Path(td))["files"]["aml_autoscript"]["legacy_uimage"]["recognized"])
    def test_sha(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/"dtb.img").write_bytes(b"abc")
            self.assertEqual(len(m.analyze(Path(td))["files"]["dtb.img"]["sha256"]), 64)
    def test_reject_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/"real").write_bytes(b"123")
            (Path(td)/"dtb.img").symlink_to(Path(td)/"real")
            self.assertIsNone(m.analyze(Path(td))["files"]["dtb.img"])
    def test_reject_empty(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/"dtb.img").write_bytes(b"")
            self.assertIsNone(m.analyze(Path(td))["files"]["dtb.img"])
    def test_reject_directory(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/"dtb.img").mkdir()
            self.assertIsNone(m.analyze(Path(td))["files"]["dtb.img"])
    def test_never_approve(self):
        with tempfile.TemporaryDirectory() as td:
            r = m.analyze(Path(td))
            self.assertFalse(r["safe_to_execute"])
            self.assertFalse(r["write_authorized"])
            self.assertFalse(r["device_tree_approved"])
    def test_bad_reference_directory(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError): m.analyze(Path(td)/"missing")
    def test_ignore_extra_files(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/"unrecognized").write_bytes(b"abc")
            self.assertEqual(set(m.analyze(Path(td))["files"]), set(m.NAMES))

if __name__ == "__main__":
    unittest.main()
