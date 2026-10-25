"""Regression tests for read-only Franklin vendor GPIO inspection."""
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "tools" / "inspect_franklin_gpio_mapping.py"
spec = importlib.util.spec_from_file_location("franklin_gpio", MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

VENDOR = """
pinctrl@ff634480 {
  banks@ff6346c0 {
    gpio-controller;
    #gpio-cells = <0x02>;
    phandle = <0x27>;
  };
};
sd2@ffe05000 {
  status = "okay";
  sd {
    gpio_cd = <0x27 0x30 0x00>;
  };
};
"""


class TestFranklinGPIO(unittest.TestCase):
    def test_report_does_not_claim_compatibility(self):
        report = module.inspect(VENDOR)
        self.assertEqual(report["vendor_gpio_cd"]["raw_index"], 48)
        self.assertTrue(report["vendor_gpio_controller_candidate_found"])
        self.assertIsNone(report["mainline_gpio_guess"])
        self.assertFalse(report["approved_for_boot"])
        self.assertFalse(report["approved_for_flash"])

    def test_distant_gpio_controller_is_resolved_by_node(self):
        separated = VENDOR.replace(
            "    phandle = <0x27>;",
            "    /* " + ("padding " * 200) + " */\n    phandle = <0x27>;"
        )
        report = module.inspect(separated)
        self.assertTrue(report["vendor_gpio_controller_candidate_found"])

    def test_unrelated_gpio_controller_does_not_match(self):
        fake = VENDOR.replace("    gpio-controller;\n", "")
        fake = "other { gpio-controller; #gpio-cells = <0x02>; };\n" + fake
        report = module.inspect(fake)
        self.assertFalse(report["vendor_gpio_controller_candidate_found"])
        self.assertFalse(report["approved_for_boot"])

    def test_decimal_gpio_cells(self):
        decimal = VENDOR.replace("#gpio-cells = <0x02>", "#gpio-cells = <2>")
        self.assertTrue(module.inspect(decimal)["vendor_gpio_controller_candidate_found"])

    def test_missing_sd_node_fails_closed(self):
        with self.assertRaises(ValueError):
            module.inspect("not a DTS")

    def test_missing_gpio_cd_fails_closed(self):
        with self.assertRaises(ValueError):
            module.inspect(VENDOR.replace("gpio_cd", "other_field"))


if __name__ == "__main__":
    unittest.main()
