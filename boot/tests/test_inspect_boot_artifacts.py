"""Synthetic tests; do not access any devices or firmware."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

target = Path(__file__).resolve().parents[1] / "tools" / "inspect_boot_artifacts.py"
spec = importlib.util.spec_from_file_location("inspect_boot_artifacts", target)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

class InspectorTests(unittest.TestCase):
    def test_valid_headers_do_not_prove_boot(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            kernel = root / "Image"
            kernel.write_bytes(bytes(56) + b"ARM\x64" + bytes(100))
            dtb = root / "board.dtb"
            dtb.write_bytes(struct.pack(">10I", 0xd00dfeed, 96, 56, 80, 40, 17, 16, 0, 8, 16) + bytes(56))
            initrd = root / "initramfs.gz"
            initrd.write_bytes(b"\x1f\x8b\x08" + bytes(20))
            result = tool.inspect(kernel, dtb, initrd)
            self.assertTrue(result["structural_checks_passed"])
            self.assertFalse(result["boot_compatibility_verified"])
            self.assertFalse(result["safe_to_flash"])

    def test_missing_and_invalid_artifacts_fail(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            kernel = root / "Image"; kernel.write_bytes(b"bad")
            dtb = root / "board.dtb"; dtb.write_bytes(b"bad")
            result = tool.inspect(kernel, dtb, root / "missing")
            self.assertFalse(result["structural_checks_passed"])
            self.assertTrue(all(not item["ok"] for item in result["artifacts"]))

    def test_malformed_fdt_offsets_fail(self):
        with tempfile.TemporaryDirectory() as d:
            dtb = Path(d) / "bad.dtb"
            dtb.write_bytes(struct.pack(">10I", 0xd00dfeed, 96, 88, 80, 40, 17, 16, 0, 32, 32) + bytes(56))
            self.assertFalse(tool.inspect_file(dtb, "dtb")["ok"])

if __name__ == "__main__":
    unittest.main()
