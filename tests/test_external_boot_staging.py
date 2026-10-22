import pathlib, subprocess, tempfile, unittest, struct, gzip
SCRIPT=pathlib.Path(__file__).resolve().parents[1]/"boot/tools/stage_external_boot.py"
class ExternalBootStageTest(unittest.TestCase):
 def test_fake_kernel_rejected_and_no_output(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d)
   (root/"Image").write_bytes(b"invalid"*20)
   (root/"board.dtb").write_bytes(bytes.fromhex("d00dfeed")+b"x"*40)
   (root/"initramfs.gz").write_bytes(gzip.compress(b"cpio"))
   out=root/"out"
   cmd=["python3",str(SCRIPT),"--kernel",str(root/"Image"),"--dtb",str(root/"board.dtb"),"--initramfs",str(root/"initramfs.gz"),"--output",str(out)]
   result=subprocess.run(cmd,capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0)
   self.assertFalse(out.exists())
 def test_stage_inputs_and_explicit_warning(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d)
   head=bytearray(64);head[56:60]=struct.pack("<I",0x644d5241)
   (root/"Image").write_bytes(head)
   (root/"board.dtb").write_bytes(bytes.fromhex("d00dfeed")+b"x"*40)
   (root/"initramfs.gz").write_bytes(gzip.compress(b"cpio"))
   out=root/"out"
   cmd=["python3",str(SCRIPT),"--kernel",str(root/"Image"),"--dtb",str(root/"board.dtb"),"--initramfs",str(root/"initramfs.gz"),"--output",str(out)]
   result=subprocess.run(cmd,capture_output=True,text=True)
   self.assertEqual(result.returncode,0,result.stderr)
   self.assertIn("rdinit=/init",(out/"extlinux/extlinux.conf").read_text())
   self.assertIn("NOT FLASHABLE",(out/"SHA256SUMS.json").read_text())
