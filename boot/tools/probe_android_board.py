#!/usr/bin/env python3
"""Read-only Android board properties over authorized ADB; no device modifications."""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

FIELDS = {
    "soc_platform": "getprop ro.board.platform",
    "hardware": "getprop ro.hardware",
    "product_board": "getprop ro.product.board",
    "bootloader_version": "getprop ro.bootloader",
    "device_tree_model": "if [ -r /proc/device-tree/model ]; then tr '\\000' ' ' </proc/device-tree/model; fi",
    "device_tree_compatible": "if [ -r /proc/device-tree/compatible ]; then tr '\\000' ' ' </proc/device-tree/compatible; fi",
    "kernel_release": "uname -r",
    "mmc_hosts": "ls /sys/class/mmc_host 2>/dev/null",
}

def authorized_device_count(output):
    """Count only authorized device rows; never return/display serials."""
    if not isinstance(output, str):
        raise ValueError("ADB device listing must be text")
    return sum(1 for line in output.splitlines()
               if len(line.split()) == 2 and line.split()[1] == "device")

def survey(adb="adb", run=subprocess.run):
    """Issue only the fixed, read-only ADB shell commands in FIELDS."""
    rows = {}
    for key, command in FIELDS.items():
        try:
            result = run([adb, "shell", "sh", "-c", command], capture_output=True,
                         text=True, timeout=15, check=False)
            ok = result.returncode == 0
            value = result.stdout.strip()[:1024] if ok else ""
        except (OSError, subprocess.TimeoutExpired, UnicodeError):
            ok, value = False, ""
        rows[key] = {"ok": ok, "value": value}
    return rows

def make_report(rows):
    return {
        "project": "Nexus Relay",
        "survey_type": "read-only-android-board-probe",
        "survey_utc": datetime.now(timezone.utc).isoformat(),
        "results": rows,
        "board_boot_verified": False,
        "boot_authorized": False,
        "caution": "Hardware clues only; does not prove nonpersistent USB boot, board DTB match or recovery. Review content for device-specific data before sharing.",
    }

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Create a NEW local JSON file; never overwrite")
    args = parser.parse_args(argv)
    if shutil.which("adb") is None:
        parser.error("Android platform-tools (adb) not found")
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True,
                                text=True, timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired, UnicodeError):
        parser.error("Cannot query ADB device status (no serials collected)")
    if result.returncode != 0 or authorized_device_count(result.stdout) != 1:
        parser.error("Exactly one authorized ADB device required; no device IDs are reported")
    report = make_report(survey())
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        try:
            with args.output.open("x", encoding="utf-8") as dest:
                dest.write(rendered)
        except OSError as exc:
            parser.error(f"Unable to create output file: {exc.__class__.__name__}")
        print("Survey saved in new file; review its contents before sharing")
    else:
        print(rendered, end="")
    return 0

if __name__ == "__main__":
    sys.exit(main())
