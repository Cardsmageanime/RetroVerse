#!/usr/bin/env python3
"""Offline ARM64 memory handoff structural checks; never touches hardware."""
import argparse
import json
from pathlib import Path

NAMES = ("kernel", "dtb", "initramfs")
MAX64 = (1 << 64) - 1

def evaluate(manifest):
    if not isinstance(manifest, dict):
        raise ValueError("Expected a JSON object")
    problems = []
    images = manifest.get("images")
    if not isinstance(images, dict):
        images = {}
        problems.append("images must be an object")
    regions = []
    for name in NAMES:
        entry = images.get(name)
        if not isinstance(entry, dict):
            problems.append(f"{name}: missing image entry")
            continue
        address, size = entry.get("address"), entry.get("size_bytes")
        if (type(address) is not int or type(size) is not int or address < 0
                or size <= 0 or address > MAX64 or size > MAX64
                or size > MAX64 - address):
            problems.append(f"{name}: invalid address/size or 64-bit overflow")
            continue
        regions.append((name, address, address + size))
    for i, (a, alo, ahi) in enumerate(regions):
        for b, blo, bhi in regions[i + 1:]:
            if alo < bhi and blo < ahi:
                problems.append(f"{a} and {b}: memory regions overlap")
    for key in ("board_identity_independently_verified", "bootloader_ram_map_verified",
                "nonpersistent_usb_loader_verified", "board_dtb_independently_verified",
                "android_emmc_unchanged_verified"):
        if manifest.get(key) is not True:
            problems.append(f"{key}: no independent verification")
    for key in ("persistent_environment_changes", "internal_storage_writes"):
        if manifest.get(key) is not False:
            problems.append(f"{key}: not explicitly ruled out")
    return {
        "format": "nexus-relay-arm64-handoff-check-v1",
        "status": "blocked" if problems else "structural-checks-only-external-review-required",
        "problems": problems,
        "boot_authorized": False,
        "image_bootable": False,
        "storage_writes_authorized": False,
        "warning": "Untrusted manifest is not hardware evidence. RAM reservations, relocation, firmware ownership and bootloader behavior cannot be validated by this check.",
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", required=True, type=Path, help="Existing JSON file (never device path)")
    args = p.parse_args()
    try:
        result = evaluate(json.loads(args.manifest.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, ValueError) as exc:
        p.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
