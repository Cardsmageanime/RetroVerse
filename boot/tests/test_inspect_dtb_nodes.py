"""Offline parser tests with a fabricated minimal flattened device tree."""
import importlib.util
import struct
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "tools" / "inspect_dtb_nodes.py"
spec = importlib.util.spec_from_file_location("dtb_nodes", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def fixture():
    strings = b"model\0compatible\0"
    def word(x): return struct.pack(">I", x)
    def node(name):
        value = name.encode() + b"\0"
        return word(1) + value + bytes((-len(value)) % 4)
    def prop(nameoff, value):
        return word(3) + word(len(value)) + word(nameoff) + value + bytes((-len(value)) % 4)
    structure = (node("") + prop(0, b"Test Board\0") + prop(6, b"example,board\0") +
                 node("mmc@ffe05000") + word(2) + word(2) + word(9))
    reserved = bytes(16)
    off_res, off_struct, off_strings = 40, 56, 56 + len(structure)
    total = off_strings + len(strings)
    header = struct.pack(">10I", mod.MAGIC, total, off_struct, off_strings, off_res,
                         17, 16, 0, len(strings), len(structure))
    return header + reserved + structure + strings

class Tests(unittest.TestCase):
    def test_parses_identity_and_node(self):
        result = mod.parse(fixture())
        self.assertIn("Test Board", result["observed_nodes"][0]["properties"]["model"])
        self.assertTrue(any("mmc@" in x["path"] for x in result["observed_nodes"]))
    def test_not_authorized(self):
        result = mod.parse(fixture())
        self.assertFalse(result["boot_authorized"])
        self.assertFalse(result["board_match_verified"])
    def test_bad_magic(self):
        d = bytearray(fixture()); d[0] = 0
        with self.assertRaises(ValueError): mod.parse(bytes(d))
    def test_truncated(self):
        with self.assertRaises(ValueError): mod.parse(fixture()[:30])
    def test_length_mismatch(self):
        with self.assertRaises(ValueError): mod.parse(fixture() + b"x")
    def test_wrong_input_type(self):
        with self.assertRaises(ValueError): mod.parse("not bytes")
    def test_missing_end_marker(self):
        d = bytearray(fixture()); end = 56 + struct.unpack_from(">I", d, 36)[0] - 4; struct.pack_into(">I", d, end, 0)
        with self.assertRaises(ValueError): mod.parse(bytes(d))

    def test_section_overlap_rejected(self):
        d = bytearray(fixture()); struct.pack_into(">I", d, 12, 60)
        with self.assertRaises(ValueError): mod.parse(bytes(d))
    def test_old_version_rejected(self):
        d = bytearray(fixture()); struct.pack_into(">I", d, 20, 16)
        with self.assertRaises(ValueError): mod.parse(bytes(d))
    def test_empty_property_strings_rejected(self):
        d = bytearray(fixture()); struct.pack_into(">I", d, 32, 0)
        with self.assertRaises(ValueError): mod.parse(bytes(d))

if __name__ == "__main__":
    unittest.main()
