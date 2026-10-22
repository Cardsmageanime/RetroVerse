import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "tools" / "plan_franklin_uboot.py"
spec = importlib.util.spec_from_file_location("plan_franklin_uboot", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class PlanTests(unittest.TestCase):
    def test_review_plan_not_executable(self):
        plan = module.generate_plan()
        self.assertEqual(plan["status"], "NON-DEPLOYABLE-REVIEW-ONLY")
        self.assertFalse(plan["approved_for_execution"])
        self.assertFalse(plan["approved_for_flashing"])
        self.assertFalse(plan["script_image_generated"])
        self.assertIn("UNKNOWN", plan["uboot_device_index"])
    def test_device_index_cannot_be_guessed(self):
        with self.assertRaises(ValueError):
            module.generate_plan(device="0")
    def test_reject_traversal(self):
        with self.assertRaises(ValueError):
            module.generate_plan(kernel="../../bootloader")
    def test_reject_address_reuse(self):
        with self.assertRaises(ValueError):
            module.generate_plan(dtb_addr="0x01080000")

if __name__ == "__main__":
    unittest.main()
