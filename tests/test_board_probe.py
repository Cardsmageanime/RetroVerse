import importlib.util, pathlib, unittest
from unittest.mock import patch
PATH=pathlib.Path(__file__).resolve().parents[1]/"boot/tools/probe_android_board.py"
spec=importlib.util.spec_from_file_location("probe_android_board",PATH)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
class ProbeTests(unittest.TestCase):
 def test_commands_are_read_only(self):
  expected={"soc_platform","hardware","product_board","bootloader_version","device_tree_model","device_tree_compatible","kernel_release","mmc_hosts"}
  self.assertEqual(set(module.FIELDS),expected)
  forbidden=(" flash ","reboot","setprop"," dd ","su ","rm ","mkfs","fastboot","serialno","mac_address")
  for cmd in module.FIELDS.values():
   self.assertFalse(any(token in cmd.lower() for token in forbidden),cmd)
 def test_collects_fields_without_adb_device(self):
  class Result:
   returncode=0
   stdout="s905x2\n"
  with patch.object(module.subprocess,"run",return_value=Result()) as runner:
   result=module.survey()
  self.assertEqual(result["soc_platform"]["value"],"s905x2")
  self.assertEqual(runner.call_count,len(module.FIELDS))
