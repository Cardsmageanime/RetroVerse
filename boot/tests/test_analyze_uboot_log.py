#!/usr/bin/env python3
"""Offline safety and parser regression tests for the U-Boot log observer."""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "analyze_uboot_log.py"
spec = importlib.util.spec_from_file_location("analyze_uboot_log", SCRIPT)
analyzer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyzer)


class LogAnalyzerTests(unittest.TestCase):
    def test_empty_log_never_verifies_boot_or_flash(self):
        report = analyzer.analyze_text("")
        self.assertEqual(report["readiness"], {
            "external_uboot_boot_path_verified": False,
            "external_sd_boot_verified": False,
            "can_flash": False,
        })
        self.assertFalse(report["manual_review_required"])

    def test_marker_observations_are_not_boot_proof(self):
        log = "\n".join((
            "U-Boot 2024.01",
            "Model: Test Board",
            "fatload mmc 1:1 0x01000000 Image",
            "autoscr 0x01000000",
            "booti 0x01000000 - 0x02000000",
            "Starting kernel ...",
        ))
        report = analyzer.analyze_text(log)
        obs = report["observations"]
        self.assertEqual(obs["uboot_version"], "2024.01")
        self.assertEqual(obs["board_model"], "Test Board")
        self.assertEqual(obs["mmc_index_tokens_seen"], ["1"])
        self.assertTrue(obs["sd_load_text_marker_seen"])
        self.assertTrue(obs["autoscript_text_marker_seen"])
        self.assertTrue(obs["boot_handoff_text_marker_seen"])
        self.assertTrue(obs["linux_start_text_marker_seen"])
        self.assertFalse(any(report["readiness"].values()))

    def test_dangerous_write_markers_require_review(self):
        for command in ("saveenv", "env save", "mmc write 0 100 1", "nand erase"):
            with self.subTest(command=command):
                self.assertTrue(analyzer.analyze_text(command)["manual_review_required"])

    def test_raw_log_is_not_included(self):
        secret = "PRIVATE_SERIAL_TOKEN_123456"
        report = analyzer.analyze_text("Model: Test Board\n" + secret)
        self.assertNotIn(secret, json.dumps(report))
        self.assertFalse(report["raw_log_lines_included"])

    def test_cli_refuses_to_overwrite_output(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source = folder / "boot.log"
            destination = folder / "report.json"
            source.write_text("U-Boot 2024.01\n")
            destination.write_text("unchanged")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--log", str(source), "--output", str(destination)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(destination.read_text(), "unchanged")

    def test_cli_parses_valid_saved_log(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "boot.log"
            source.write_text("U-Boot 2024.01\n")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--log", str(source)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["observations"]["uboot_version"], "2024.01")


if __name__ == "__main__":
    unittest.main()
