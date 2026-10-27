#!/usr/bin/env python3
"""Review saved board/DTB evidence without reading device nodes or modifying hardware."""
import argparse
import json
from pathlib import Path

REQUIRED = {
    "board_revision_confirmed": "Exact board revision has not been confirmed",
    "soc_identity_confirmed": "SoC identity has not been independently confirmed",
    "dtb_matches_board": "A board-matched DTB has not been validated",
    "memory_map_verified": "Bootloader/kernel memory map has not been verified",
    "sd_gpio_mapping_verified": "SD card-detect and GPIO mapping have not been verified",
    "sd_power_rails_verified": "SD power rails have not been verified",
    "usb_bootloader_path_verified": "Nonpersistent USB bootloader path has not been verified",
}
HAZARDS = {
    "uses_example_board_dtb": "An example-board DTB is proposed for unverified Vayava hardware",
    "vendor_gpio_assumed_upstream": "Vendor GPIO numbering is assumed identical to upstream",
    "boot_script_changes_environment": "Boot script changes persistent environment",
    "internal_emmc_write_required": "Boot procedure requires internal eMMC writes",
    "unresolved_sd_crc_errors": "Observed SD CRC errors have not been resolved",
}


def evaluate(evidence):
    """Use strict booleans; unknown and missing information fail closed."""
    if not isinstance(evidence, dict):
        raise ValueError("Expected a JSON object")
    blockers = [message for key, message in REQUIRED.items() if evidence.get(key) is not True]
    blockers += [message for key, message in HAZARDS.items() if evidence.get(key) is not False]
    return {
        "format": "nexus-relay-board-evidence-v1",
        "status": "verification-blocked" if blockers else "reported-evidence-requires-independent-review",
        "blockers": blockers,
        "boot_authorized": False,
        "flash_authorized": False,
        "device_tree_approved": False,
        "warning": "Self-reported offline evidence only; not board verification, boot authorization or proof of hardware compatibility.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True, help="Saved JSON file, not a hardware device")
    args = parser.parse_args()
    try:
        result = evaluate(json.loads(args.evidence.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
