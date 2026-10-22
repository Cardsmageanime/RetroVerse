import unittest, tempfile, pathlib, gzip, json, hashlib, struct, sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"boot/tools"))
from validate_external_boot import validate
class BootValidation(unittest.TestCase):
 def test_invalid_empty_package(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertIn("Missing Image",validate(d))
 def test_synthetic_valid_package_and_checksum_detection(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d)
   (root/"extlinux").mkdir()
   image=bytearray(64);image[56:60]=struct.pack("<I",0x644d5241)
   (root/"Image").write_bytes(image)
   dtb=bytearray(40);dtb[:4]=bytes.fromhex("d00dfeed");dtb[4:8]=struct.pack(">I",40)
   (root/"board.dtb").write_bytes(dtb)
   (root/"initramfs.cpio.gz").write_bytes(gzip.compress(b"070701"))
   (root/"extlinux/extlinux.conf").write_text("LINUX /Image\nFDT /board.dtb\nINITRD /initramfs.cpio.gz\nAPPEND rdinit=/init")
   checks={}
   for f in ["Image","board.dtb","initramfs.cpio.gz","extlinux/extlinux.conf"]:
    checks[f]=hashlib.sha256((root/f).read_bytes()).hexdigest()
   (root/"SHA256SUMS.json").write_text(json.dumps({"files":checks}))
   self.assertEqual([],validate(root))
   (root/"Image").write_bytes(b"wrong")
   self.assertTrue(any("checksum" in s.lower() for s in validate(root)))
