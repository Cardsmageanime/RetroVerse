"""Pure local tests for legacy U-Boot integrity checks."""
import importlib.util
import struct
import unittest
import zlib
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'tools' / 'verify_uboot_legacy_crc.py'
spec = importlib.util.spec_from_file_location('verify_uboot_legacy_crc', p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def make_image(payload=b'hello'):
    h = bytearray(64)
    struct.pack_into('>I', h, 0, m.MAGIC)
    struct.pack_into('>I', h, 12, len(payload))
    struct.pack_into('>I', h, 24, zlib.crc32(payload))
    struct.pack_into('>I', h, 4, zlib.crc32(h))
    return bytes(h) + payload

class Tests(unittest.TestCase):
    def test_valid_checksums_not_authorization(self):
        r = m.verify(make_image()); self.assertTrue(r['header_crc_valid']); self.assertTrue(r['payload_crc_valid']); self.assertFalse(r['boot_authorized'])
    def test_corrupt_header(self):
        data = bytearray(make_image()); data[32] ^= 1
        self.assertFalse(m.verify(bytes(data))['header_crc_valid'])
    def test_corrupt_payload(self):
        data = bytearray(make_image()); data[-1] ^= 1
        self.assertFalse(m.verify(bytes(data))['payload_crc_valid'])
    def test_short_header(self):
        self.assertIn('Truncated', m.verify(b'abcd')['issues'][0])
    def test_unknown_magic(self):
        self.assertFalse(m.verify(b'x'*64)['legacy_header_present'])
    def test_invalid_type(self):
        with self.assertRaises(ValueError): m.verify('text')
    def test_empty(self):
        with self.assertRaises(ValueError): m.verify(b'')
    def test_too_large(self):
        with self.assertRaises(ValueError): m.verify(b'0' * (m.MAX_BYTES + 1))
    def test_declared_exceeds_length(self):
        data=bytearray(make_image()); struct.pack_into('>I',data,12,100)
        self.assertFalse(m.verify(bytes(data))['payload_length_valid'])
    def test_trailing_data(self):
        self.assertIn('Trailing bytes after declared payload',m.verify(make_image()+b'!')['issues'])
    def test_empty_payload_valid(self):
        self.assertTrue(m.verify(make_image(b''))['payload_crc_valid'])

if __name__ == '__main__': unittest.main()
