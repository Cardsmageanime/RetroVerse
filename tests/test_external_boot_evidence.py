import importlib.util
import json
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("gate",ROOT/"hardware/tests/check_external_boot_evidence.py")
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class GateTests(unittest.TestCase):
    def setUp(self):
        self.profile=json.loads((ROOT/"hardware/profiles/vayava-franklin-2gb.json").read_text())
        self.evidence=json.loads((ROOT/"hardware/evidence/vayava-franklin-external-boot.json").read_text())
    def test_unverified_stays_blocked(self):
        report=gate.evaluate(self.profile,self.evidence)
        self.assertFalse(report["ready_for_controlled_external_boot_test"])
        self.assertFalse(report["automated_tests_prove_bootability"])
    def test_partial_evidence_stays_blocked(self):
        evidence=self.evidence.copy()
        evidence["soc_identity_confirmed"]=True
        self.assertFalse(gate.evaluate(self.profile,evidence)["ready_for_controlled_external_boot_test"])
    def test_internal_storage_protection_required(self):
        p=self.profile.copy()
        p["permissions"]={"flash_internal_storage":True}
        self.assertFalse(gate.evaluate(p,self.evidence)["ready_for_controlled_external_boot_test"])
