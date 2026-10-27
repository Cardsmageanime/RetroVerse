import importlib.util
import unittest
from pathlib import Path
from copy import deepcopy
p = Path(__file__).resolve().parents[1] / 'tools' / 'check_usb_boot_evidence_bundle.py'
spec = importlib.util.spec_from_file_location('bundle', p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
GOOD = {'reports': {
    'usb': {'format': 'nexus-relay-usb-boot-readiness-v1', 'status': 'reported-checks-complete-review-required', 'blockers': [], 'boot_authorized': False, 'can_write': False, 'hardware_boot_verified': False},
    'board': {'format': 'nexus-relay-board-evidence-v1', 'status': 'reported-evidence-requires-independent-review', 'blockers': [], 'boot_authorized': False, 'flash_authorized': False, 'device_tree_approved': False},
    'handoff': {'format': 'nexus-relay-arm64-handoff-check-v1', 'status': 'structural-checks-only-external-review-required', 'problems': [], 'boot_authorized': False, 'image_bootable': False, 'storage_writes_authorized': False},
}}
class BundleTests(unittest.TestCase):
    def test_empty_blocks(self):
        self.assertEqual(m.evaluate({})['status'], 'review-blocked')
    def test_complete_never_authorizes(self):
        r = m.evaluate(GOOD)
        self.assertFalse(r['boot_authorized'])
        self.assertFalse(r['physical_boot_verified'])
        self.assertFalse(r['write_authorized'])
    def test_each_missing_report(self):
        for name in m.EXPECTED:
            b = deepcopy(GOOD)
            del b['reports'][name]
            self.assertEqual(m.evaluate(b)['status'], 'review-blocked')
    def test_forward_blockers(self):
        b = deepcopy(GOOD)
        b['reports']['board']['blockers'] = ['SD power rails unverified']
        self.assertIn('board: SD power rails unverified', m.evaluate(b)['outstanding'])
    def test_wrong_format(self):
        b = deepcopy(GOOD)
        b['reports']['usb']['format'] = 'unknown'
        self.assertEqual(m.evaluate(b)['status'], 'review-blocked')
    def test_reject_true_safety_flag(self):
        b = deepcopy(GOOD)
        b['reports']['usb']['boot_authorized'] = True
        self.assertEqual(m.evaluate(b)['status'], 'review-blocked')
    def test_reject_missing_safety_flag(self):
        b = deepcopy(GOOD)
        del b['reports']['handoff']['storage_writes_authorized']
        self.assertEqual(m.evaluate(b)['status'], 'review-blocked')
    def test_reject_unexpected_status(self):
        b = deepcopy(GOOD)
        b['reports']['board']['status'] = 'approved'
        self.assertEqual(m.evaluate(b)['status'], 'review-blocked')
    def test_reject_non_string_findings(self):
        b = deepcopy(GOOD)
        b['reports']['handoff']['problems'] = [123]
        self.assertEqual(m.evaluate(b)['status'], 'review-blocked')
    def test_reject_non_object(self):
        for b in (None, [], 'x'):
            with self.assertRaises(ValueError): m.evaluate(b)
    def test_partial_reports_can_never_be_ready(self):
        b = deepcopy(GOOD)
        b['reports']['usb']['blockers'].append('USB route unverified')
        self.assertEqual(m.evaluate(b)['status'], 'review-blocked')
if __name__ == '__main__': unittest.main()
