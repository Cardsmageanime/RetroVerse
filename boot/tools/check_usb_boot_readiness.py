#!/usr/bin/env python3
"""Assess a saved USB boot evidence JSON; never access or change hardware."""
import argparse
import json
from pathlib import Path

REQUIRED = {
    "exact_board_identity_verified": "Exact GameBox board identity unverified",
    "board_dtb_verified": "Board-specific device tree unverified",
    "nonpersistent_usb_boot_path_verified": "Safe nonpersistent USB boot path unverified",
    "usb_media_integrity_verified": "USB test media integrity unverified",
    "kernel_initramfs_compatible_verified": "Kernel/initramfs board compatibility unverified",
    "android_storage_protection_verified": "Android/eMMC protection unverified",
}
HAZARDS = {
    "boot_script_writes_environment": "Boot script may persistently change bootloader environment",
    "internal_storage_write_required": "Proposed boot path requires internal storage writes",
    "device_tree_from_other_board": "Device tree is from an unverified board",
    "usb_io_errors_observed": "USB media I/O errors observed",
}

def evaluate(evidence):
    """Fail closed on absent evidence; true assertions are still not physical proof."""
    if not isinstance(evidence, dict):
        raise ValueError("Evidence must be a JSON object")
    blockers = [message for key, message in REQUIRED.items()
                if evidence.get(key) is not True]
    blockers += [message for key, message in HAZARDS.items()
                 if evidence.get(key) is True]
    return {
        "format": "nexus-relay-usb-boot-readiness-v1",
        "status": "verification-blocked" if blockers else "reported-checks-complete-review-required",
        "blockers": blockers,
        "hardware_boot_verified": False,
        "boot_authorized": False,
        "can_write": False,
        "warning": "Offline self-reported evidence only. Never run legacy aml_autoscript, flash Android/eMMC, or attempt boot based on this output.",
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", required=True, type=Path,
                        help="Path to a saved JSON report, not a block device")
    args = parser.parse_args()
    try:
        report = evaluate(json.loads(args.evidence.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
