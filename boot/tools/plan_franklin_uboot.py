#!/usr/bin/env python3
"""Generate a NON-DEPLOYABLE U-Boot boot plan for Franklin G12A.

Only emits a JSON/text review proposal; never emits aml_autoscript,
boot.scr, an executable image, disk writes, or a command to install.
The boot index and memory addresses must be verified on physical firmware.
"""
import argparse
import json
import re
from pathlib import Path

SAFE_FILE = re.compile(r"^[A-Za-z0-9._/-]{1,128}$")
HEX_ADDR = re.compile(r"^0x[0-9a-fA-F]{6,16}$")

def generate_plan(device="UNVERIFIED", partition="1",
                  kernel="/Image", dtb="/dtb/meson-g12a-u212.dtb",
                  initramfs="/initramfs.cpio.gz",
                  kernel_addr="0x01080000", dtb_addr="0x08000000",
                  initramfs_addr="0x09000000"):
    if device != "UNVERIFIED":
        raise ValueError("Physical U-Boot mmc index is unverified; no device selection allowed")
    if partition != "1":
        raise ValueError("Partition is a placeholder pending confirmation")
    for label, name in (("kernel", kernel), ("dtb", dtb), ("initramfs", initramfs)):
        if not SAFE_FILE.fullmatch(name) or ".." in name.split("/"):
            raise ValueError(f"Invalid {label} pathname")
    addrs = [kernel_addr, dtb_addr, initramfs_addr]
    if not all(HEX_ADDR.fullmatch(x) for x in addrs) or len(set(addrs)) != 3:
        raise ValueError("Addresses must be distinct hexadecimal placeholders")
    return {
      "target": "g12a_u212_2g / franklin candidate",
      "status": "NON-DEPLOYABLE-REVIEW-ONLY",
      "uboot_device_index": "UNKNOWN; Android mmcblk numbers cannot be substituted",
      "memory_addresses": "EXAMPLES ONLY; placement/overlap/DRAM must be verified",
      "script_image_generated": False,
      "would_modify_internal_emmc": False,
      "proposed_sequence_for_manual_review": [
        "Discover bootloader MMC numbering from passive vendor boot logs",
        f"Identify external partition (provisional partition {partition})",
        f"Check kernel file exists: {kernel}",
        f"Check board-matched DTB exists: {dtb}",
        f"Check initramfs exists: {initramfs}",
        f"Review candidate load buffers {kernel_addr}, {dtb_addr}, {initramfs_addr} against memory map and file sizes",
        "Verify required U-Boot booti command and FDT/initramfs support",
        "Only after independent boot-path validation, design a recoverable boot test",
      ],
      "approved_for_execution": False,
      "approved_for_flashing": False,
      "physical_boot_verified": False,
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, help="Write a new JSON report file; existing files never overwritten")
    args = p.parse_args()
    report = json.dumps(generate_plan(), indent=2) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as f:
            f.write(report)
        print("Wrote review-only plan:", args.output)
    else:
        print(report)

if __name__ == "__main__":
    main()
