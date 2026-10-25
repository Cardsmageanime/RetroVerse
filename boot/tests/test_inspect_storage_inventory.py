"""Tests for read-only storage inventory parser."""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "tools" / "inspect_storage_inventory.py"
spec = importlib.util.spec_from_file_location("inventory", path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def disk(name, size, rm, tran, children=None, **kw):
    return {"name": name, "type": "disk", "size": size, "rm": rm, "tran": tran, "ro": 0,
            "children": children or [], **kw}

class InventoryTests(unittest.TestCase):
    def test_internal_ssd_rejected(self):
        result = m.analyze({"blockdevices": [disk("sda", 1_000_000_000_000, False, "sata")]})
        self.assertFalse(result["devices"][0]["inventory_candidate"])
        self.assertFalse(result["can_write"])

    def test_reference_sd_card_with_partitions_rejected(self):
        partition = {"name": "sdb1", "type": "part", "mountpoints": ["/media/EMUELEC"]}
        result = m.analyze({"blockdevices": [disk("sdb", 115_000_000_000, True, "usb", [partition])]})
        self.assertIn("existing-partitions-present", result["devices"][0]["issues"])
        self.assertIn("mounted-partitions-present", result["devices"][0]["issues"])
        self.assertFalse(result["devices"][0]["install_authorized"])

    def test_unpartitioned_candidate_still_not_authorized(self):
        result = m.analyze({"blockdevices": [disk("sdc", 64_000_000_000, True, "usb")]})
        self.assertTrue(result["devices"][0]["inventory_candidate"])
        self.assertFalse(result["devices"][0]["install_authorized"])

    def test_over_one_tb_rejected(self):
        result = m.analyze({"blockdevices": [disk("sdc", 1_000_000_000_001, True, "usb")]})
        self.assertFalse(result["devices"][0]["inventory_candidate"])

    def test_unknown_capacity_rejected(self):
        result = m.analyze({"blockdevices": [disk("sdc", "64G", True, "usb")]})
        self.assertFalse(result["devices"][0]["inventory_candidate"])

    def test_nested_mount_is_detected(self):
        root = {"name": "sdc1", "type": "part", "children": [
            {"name": "cryptdata", "type": "crypt", "mountpoints": ["/home"]}]}
        report = m.analyze({"blockdevices": [disk("sdc", 64_000_000_000, True, "usb", [root])]})
        dev = report["devices"][0]
        self.assertIn("/home", dev["existing_mounts"])
        self.assertIn("mounted-partitions-present", dev["issues"])
        self.assertFalse(dev["install_authorized"])

    def test_intact_system_disk_with_nested_root_is_blocked(self):
        dev = disk("sda", 500_000_000_000, False, "sata", [
            {"name": "sda3", "type": "part", "children": [
                {"name": "root", "type": "lvm", "mountpoint": "/"}]}])
        report = m.analyze({"blockdevices": [dev]})
        self.assertIn("/", report["devices"][0]["existing_mounts"])
        self.assertFalse(report["devices"][0]["inventory_candidate"])

    def test_invalid_input_rejected(self):
        with self.assertRaises(ValueError):
            m.analyze({"foo": []})

if __name__ == "__main__":
    unittest.main()
