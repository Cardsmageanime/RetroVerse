#!/usr/bin/env python3
"""Offline assessment of supplied SD reliability evidence; never touches disks."""
import argparse
import json
from pathlib import Path

CHECKS = {
    "full_capacity_verified": "Full-card capacity/integrity remains unverified",
    "gamebox_sd_link_reliability_verified": "GameBox SD interface reliability remains unverified",
    "reader_readback_verified": "Reader readback validation remains unverified",
    "bootloader_card_detection_verified": "Bootloader SD detection remains unverified",
}
PROBLEMS = {
    "gamebox_sd_crc_errors_observed": "GameBox reported SD CRC errors",
    "io_errors_observed": "I/O errors observed",
    "capacity_mismatch_observed": "Capacity mismatch observed",
}

def evaluate(evidence):
    if not isinstance(evidence, dict):
        raise ValueError("Expected a JSON object")
    blockers = [message for key, message in CHECKS.items() if evidence.get(key) is not True]
    blockers.extend(message for key, message in PROBLEMS.items() if evidence.get(key) is True)
    return {
        "format": "retroverse-sd-reliability-v1",
        "status": "verification-blocked" if blockers else "no-current-blockers-in-reported-evidence",
        "blockers": blockers,
        "can_write": False,
        "boot_verified": False,
        "warning": "Supplied evidence is not a live hardware test or authorization to flash, format or boot.",
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", required=True, type=Path, help="Existing JSON file, not a block-device path")
    args = parser.parse_args()
    try:
        report = evaluate(json.loads(args.evidence.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
