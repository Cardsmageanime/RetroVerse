import importlib.util
import unittest
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'tools' / 'check_controlled_usb_trial.py'
spec = importlib.util.spec_from_file_location('trial', p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
COMPLETE = {**{k: True for k in m.REQUIRED}, **{k: False for k in m.FORBIDDEN}}

class TrialTests(unittest.TestCase):
    def test_empty_is_blocked(self):
        self.assertEqual(m.evaluate({})['status'], 'blocked')
    def test_never_grants_boot_even_if_complete(self):
        r = m.evaluate(COMPLETE)
        self.assertFalse(r['boot_authorized'])
        self.assertFalse(r['physical_boot_verified'])
    def test_never_grants_writes(self):
        r = m.evaluate(COMPLETE)
        self.assertFalse(r['flash_authorized'])
        self.assertFalse(r['storage_write_authorized'])
    def test_unknown_forbidden_condition_fails_closed(self):
        d = COMPLETE.copy(); d.pop('emmc_write_required')
        self.assertEqual(m.evaluate(d)['status'], 'blocked')
    def test_legacy_script_blocks(self):
        self.assertEqual(m.evaluate({**COMPLETE, 'legacy_aml_autoscript_executed': True})['status'], 'blocked')
    def test_missing_operator_blocks(self):
        self.assertEqual(m.evaluate({**COMPLETE, 'user_physically_present': False})['status'], 'blocked')
    def test_wrong_boolean_blocks(self):
        self.assertEqual(m.evaluate({**COMPLETE, 'board_matched_dtb_reviewed': 'true'})['status'], 'blocked')
    def test_usb_error_blocks(self):
        self.assertEqual(m.evaluate({**COMPLETE, 'unresolved_usb_errors': True})['status'], 'blocked')
    def test_ref_sd_protection_blocks(self):
        self.assertEqual(m.evaluate({**COMPLETE, 'reference_sd_removed_and_protected': False})['status'], 'blocked')
    def test_bad_type(self):
        with self.assertRaises(ValueError): m.evaluate([])

if __name__ == '__main__': unittest.main()
