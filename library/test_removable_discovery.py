import unittest
from unittest.mock import patch
from pathlib import Path
from removable_discovery import allowed_mount,candidates

class DiscoveryTests(unittest.TestCase):
 def test_refuses_internal_mounts(self):
  for path in ("/", "/home/user", "/storage/emulated/0", "/media/../etc", "relative"):
   self.assertFalse(allowed_mount(path))
 def test_mount_requires_removable_device(self):
  data={"blockdevices":[{"rm":0,"mountpoint":"/media/USB"}]}
  with patch.object(Path,"is_dir",return_value=True):
   self.assertEqual(candidates(data),[])
 def test_lists_removable_partition_candidates(self):
  data={"blockdevices":[{"rm":1,"children":[{"rm":0,"mountpoint":"/media/TESTUSB"}]}]}
  with patch.object(Path,"is_dir",return_value=True):
   found=candidates(data)
  self.assertIn("/media/TESTUSB/roms",found)
 def test_nonremovable_never_listed(self):
  data={"blockdevices":[{"rm":0,"mountpoint":"/mnt/internal"}]}
  with patch.object(Path,"is_dir",return_value=True):
   self.assertEqual(candidates(data),[])
if __name__=="__main__":unittest.main()
