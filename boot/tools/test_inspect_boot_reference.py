import tempfile
import unittest
from pathlib import Path
from inspect_boot_reference import inspect,NAMES

class BootReferenceTests(unittest.TestCase):
 def test_missing_files_do_not_imply_bootable(self):
  with tempfile.TemporaryDirectory() as d:
   result=inspect(d)
   self.assertFalse(result["bootable"])
   self.assertFalse(result["device_verified"])
   for name in NAMES:self.assertEqual(result["files"][name]["state"],"missing")
 def test_dtb_signature_and_hash(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/"dtb.img"
   path.write_bytes(bytes.fromhex("d00dfeed")+b"test")
   result=inspect(d)
   self.assertTrue(result["files"]["dtb.img"]["fdt_magic"])
   self.assertEqual(result["files"]["dtb.img"]["bytes"],8)
   self.assertEqual(len(result["files"]["dtb.img"]["sha256"]),64)
 def test_reject_symlink_reference(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/"actual").write_bytes(b"abc")
   (root/"dtb.img").symlink_to(root/"actual")
   self.assertEqual(inspect(root)["files"]["dtb.img"]["state"],"symlink-rejected")
 def test_no_modification(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/"config.ini";path.write_bytes(b"original")
   inspect(d)
   self.assertEqual(path.read_bytes(),b"original")
if __name__=="__main__":unittest.main()
