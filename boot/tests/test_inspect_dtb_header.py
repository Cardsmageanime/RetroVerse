"""Synthetic DTB envelope tests; no hardware interaction."""
import importlib.util
import struct
import unittest
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'tools' / 'inspect_dtb_header.py'
spec = importlib.util.spec_from_file_location('dtb', p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def fixture():
    data = bytearray(128)
    struct.pack_into('>10I', data, 0, m.MAGIC, 128, 56, 96, 40, 17, 16, 0, 32, 40)
    return bytes(data)

class DtbTests(unittest.TestCase):
    def test_valid_structure_not_board_approval(self):
        result = m.inspect(fixture())
        self.assertTrue(result['structurally_consistent'])
        self.assertFalse(result['board_matched'])
        self.assertFalse(result['boot_authorized'])
    def test_bad_magic(self):
        d = bytearray(fixture()); d[0] = 0
        self.assertIn('Invalid FDT magic', m.inspect(bytes(d))['problems'])
    def test_truncated_header(self):
        self.assertFalse(m.inspect(b'abc')['structurally_consistent'])
    def test_declared_size_exceeds_input(self):
        d = bytearray(fixture()); struct.pack_into('>I', d, 4, 256)
        self.assertFalse(m.inspect(bytes(d))['structurally_consistent'])
    def test_trailing_bytes(self):
        self.assertFalse(m.inspect(fixture()+b'extra')['structurally_consistent'])
    def test_structure_overflow(self):
        d=bytearray(fixture()); struct.pack_into('>I',d,36,100)
        self.assertFalse(m.inspect(bytes(d))['structurally_consistent'])
    def test_strings_overflow(self):
        d=bytearray(fixture()); struct.pack_into('>I',d,32,100)
        self.assertFalse(m.inspect(bytes(d))['structurally_consistent'])
    def test_overlapping_sections(self):
        d=bytearray(fixture()); struct.pack_into('>I',d,12,72)
        self.assertFalse(m.inspect(bytes(d))['structurally_consistent'])
    def test_invalid_version(self):
        d=bytearray(fixture()); struct.pack_into('>I',d,20,0)
        self.assertFalse(m.inspect(bytes(d))['structurally_consistent'])
    def test_invalid_type(self):
        with self.assertRaises(ValueError): m.inspect('text')
    def test_oversized(self):
        self.assertFalse(m.inspect(b'0'*(m.MAX_BYTES+1))['structurally_consistent'])

if __name__ == '__main__': unittest.main()
