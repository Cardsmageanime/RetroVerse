"""Offline unit tests: no ADB executable or physical device required."""
import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest.mock import Mock

path = Path(__file__).resolve().parents[1] / "tools" / "probe_android_board.py"
spec = importlib.util.spec_from_file_location("probe", path)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

class BoardProbeTests(unittest.TestCase):
    def test_one_authorized(self):
        self.assertEqual(probe.authorized_device_count("List of devices attached\nABC123\tdevice\n"), 1)
    def test_unauthorized_not_counted(self):
        self.assertEqual(probe.authorized_device_count("ABC\tunauthorized\nXYZ\toffline\n"), 0)
    def test_multiple_authorized_counted(self):
        self.assertEqual(probe.authorized_device_count("AAA\tdevice\nBBB\tdevice\n"), 2)
    def test_noise_not_counted(self):
        self.assertEqual(probe.authorized_device_count("List of devices attached\n* daemon started\n"), 0)
    def test_bad_devices_output_rejected(self):
        with self.assertRaises(ValueError): probe.authorized_device_count(None)
    def test_all_commands_are_fixed(self):
        calls = []
        def fake(cmd, **kwargs):
            calls.append((cmd, kwargs))
            return Mock(returncode=0, stdout="g12a\n")
        rows = probe.survey(run=fake)
        self.assertEqual(len(calls), len(probe.FIELDS))
        self.assertEqual(set(rows), set(probe.FIELDS))
        self.assertTrue(all(c[:4] == ["adb", "shell", "sh", "-c"] for c, _ in calls))
    def test_failed_command_has_no_output(self):
        rows = probe.survey(run=lambda *a, **kw: Mock(returncode=1, stdout="secret"))
        self.assertTrue(all(not x["ok"] and not x["value"] for x in rows.values()))
    def test_timeout_recovery(self):
        def timeout(*a, **kw): raise subprocess.TimeoutExpired("adb", 15)
        self.assertTrue(all(not x["ok"] for x in probe.survey(run=timeout).values()))
    def test_truncates_large_output(self):
        rows = probe.survey(run=lambda *a, **kw: Mock(returncode=0, stdout="x" * 5000))
        self.assertTrue(all(len(x["value"]) == 1024 for x in rows.values()))
    def test_report_does_not_claim_boot(self):
        report = probe.make_report({})
        self.assertFalse(report["board_boot_verified"])
        self.assertFalse(report["boot_authorized"])
        self.assertEqual(report["project"], "Nexus Relay")

if __name__ == "__main__":
    unittest.main()
