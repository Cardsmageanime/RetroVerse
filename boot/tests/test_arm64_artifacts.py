import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "tools" / "inspect_arm64_artifacts.py"
spec = importlib.util.spec_from_file_location("artifact_inspector", TOOL)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class ArtifactInspectionTests(unittest.TestCase):
    def test_structural_success_is_never_hardware_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            image, dtb = Path(directory) / "Image", Path(directory) / "board.dtb"
            header = bytearray(64)
            struct.pack_into("<I", header, 56, mod.ARM64_MAGIC)
            image.write_bytes(header)
            tree = bytearray(40)
            struct.pack_into(">II", tree, 0, mod.FDT_MAGIC, 40)
            dtb.write_bytes(tree)
            result = mod.inspect(image, dtb)
            self.assertTrue(result["structural_checks_passed"])
            self.assertFalse(result["boot_verified"])
            self.assertFalse(result["flash_ready"])

    def test_invalid_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            image, dtb = Path(directory) / "Image", Path(directory) / "board.dtb"
            image.write_bytes(b"not a kernel")
            dtb.write_bytes(b"not a tree")
            result = mod.inspect(image, dtb)
            self.assertFalse(result["structural_checks_passed"])
            self.assertFalse(result["boot_verified"])

    def test_truncated_fdt_size_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            image, dtb = Path(directory) / "Image", Path(directory) / "board.dtb"
            image.write_bytes(bytes(64))
            header = bytearray(40)
            struct.pack_into(">II", header, 0, mod.FDT_MAGIC, 1000)
            dtb.write_bytes(header)
            self.assertFalse(mod.inspect(image, dtb)["checks"]["dtb_header_and_size"])

if __name__ == "__main__":
    unittest.main()
