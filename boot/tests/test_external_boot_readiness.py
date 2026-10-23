"""Unit tests for the external boot readiness evaluation."""
import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "check_external_boot_readiness.py"
spec = importlib.util.spec_from_file_location("external_readiness", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

PROFILE = {
    "profile_id": "vayava-franklin-2gb-candidate",
    "android_amlogic_dt_id_observed": "g12a_u212_2g",
    "android_sd_bus_width_bits_observed": 4,
    "android_sd_max_frequency_hz_observed": 100000000,
}
EVIDENCE = {
    "soc_identity_confirmed": True,
    "board_dtb_matches_compiled_kernel": False,
    "external_uboot_boot_path_verified": False,
    "windows_hash_readback_passed": True,
    "gamebox_sd_link_reliability_verified": False,
}

class ReadinessTests(unittest.TestCase):
    def test_real_current_gates_block_boot(self):
        result = module.evaluate(PROFILE, EVIDENCE)
        self.assertEqual(result["readiness"], "research-only")
        self.assertFalse(result["can_flash"])
        self.assertTrue(any("external_uboot_boot_path_verified" in x for x in result["findings"]))

    def test_windows_hash_alone_does_not_clear_android_crc(self):
        result = module.evaluate(PROFILE, EVIDENCE)
        self.assertTrue(any("gamebox_sd_link_reliability_verified" in x for x in result["findings"]))

    def test_even_full_evidence_never_authorizes_flashing(self):
        all_evidence = {key: True for key in (*module.REQUIRED_GATES, *module.STORAGE_GATES, "android_internal_storage_untouched")}
        result = module.evaluate(PROFILE, all_evidence)
        self.assertEqual(result["readiness"], "candidate-for-controlled-boot-planning")
        self.assertFalse(result["can_flash"])
        self.assertFalse(result["can_claim_successful_boot"])

    def test_unverified_internal_storage_blocks_planning(self):
        evidence = {key: True for key in (*module.REQUIRED_GATES, *module.STORAGE_GATES)}
        evidence["android_internal_storage_untouched"] = False
        result = module.evaluate(PROFILE, evidence)
        self.assertEqual(result["readiness"], "research-only")
        self.assertTrue(any("android_internal_storage_untouched" in x for x in result["findings"]))

    def test_missing_internal_storage_evidence_blocks_planning(self):
        evidence = {key: True for key in (*module.REQUIRED_GATES, *module.STORAGE_GATES)}
        result = module.evaluate(PROFILE, evidence)
        self.assertEqual(result["readiness"], "research-only")
        self.assertTrue(any("android_internal_storage_untouched" in x for x in result["findings"]))

    def test_string_truthy_internal_storage_evidence_is_rejected(self):
        evidence = {key: True for key in (*module.REQUIRED_GATES, *module.STORAGE_GATES)}
        evidence["android_internal_storage_untouched"] = "true"
        result = module.evaluate(PROFILE, evidence)
        self.assertEqual(result["readiness"], "research-only")
        self.assertFalse(result["can_flash"])

    def test_wrong_board_profile_blocks_planning(self):
        result = module.evaluate({**PROFILE, "android_amlogic_dt_id_observed": "different"}, EVIDENCE)
        self.assertEqual(result["readiness"], "research-only")
        self.assertTrue(any("identification" in x for x in result["findings"]))

if __name__ == "__main__":
    unittest.main()
