import tempfile
import unittest
from pathlib import Path
from scan_library import discover
class LibraryTests(unittest.TestCase):
 def test_discovery_without_writes(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/"SNES").mkdir();(root/"SNES"/"Game.sfc").write_bytes(b"test")
   (root/"hidden").mkdir();(root/"hidden"/".hidden.nes").write_bytes(b"x")
   games,cut=discover(root)
   self.assertEqual(len(games),1)
   self.assertEqual(games[0]["system"],"SNES")
   self.assertEqual(games[0]["relative_path"],str(Path("SNES")/"Game.sfc"))
   self.assertFalse(cut)
 def test_symlinks_not_followed(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/"safe.nes").write_bytes(b"x")
   (root/"link.nes").symlink_to(root/"safe.nes")
   self.assertEqual(len(discover(root)[0]),1)
 def test_limit(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   for i in range(3):(root/(str(i)+".gba")).write_bytes(b"x")
   games,truncated=discover(root,1)
   self.assertEqual(len(games),1);self.assertTrue(truncated)
if __name__=="__main__":unittest.main()
