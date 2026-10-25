#!/usr/bin/env python3
"""Read-only lsblk JSON inventory for RetroVerse. Does not open block devices."""
import argparse
import json
from pathlib import Path

MAX_BYTES = 1_000_000_000_000

def analyze(data):
    if not isinstance(data, dict) or not isinstance(data.get("blockdevices"), list):
        raise ValueError("Expected lsblk JSON object with blockdevices list")
    devices = []
    for dev in data["blockdevices"]:
        if not isinstance(dev, dict) or dev.get("type") != "disk":
            continue
        # Walk descendant partitions, crypt, LVM and mapped filesystems.
        children = dev.get("children") or []
        mounts = []
        def visit(node):
            if not isinstance(node, dict):
                return
            points = node.get("mountpoints")
            if isinstance(points, list):
                mounts.extend(m for m in points if isinstance(m, str) and m)
            point = node.get("mountpoint")
            if isinstance(point, str) and point:
                mounts.append(point)
            for child in node.get("children") or []:
                visit(child)
        visit(dev)
        mounts = list(dict.fromkeys(mounts))
        name = dev.get("name")
        size = dev.get("size")
        # Only unrounded integer bytes are accepted.
        valid_size = type(size) is int and 0 < size <= MAX_BYTES
        removable = dev.get("rm") in (1, True, "1")
        transport = dev.get("tran")
        optical = dev.get("type") == "rom"
        issues = []
        if not isinstance(name, str) or not name:
            issues.append("missing-device-name")
        if not valid_size:
            issues.append("unknown-or-unsupported-size")
        if not removable or transport not in ("usb", "mmc"):
            issues.append("removable-transport-not-verified")
        if dev.get("ro") not in (0, False, "0"):
            issues.append("write-protection-unverified")
        if mounts:
            issues.append("mounted-partitions-present")
        if children:
            issues.append("existing-partitions-present")
        if optical:
            issues.append("optical-device")
        devices.append({
            "name": name, "reported_capacity_bytes": size if type(size) is int else None,
            "model": dev.get("model"), "transport": transport, "removable": removable,
            "existing_mounts": mounts, "issues": issues,
            "inventory_candidate": not issues,
            "install_authorized": False,
            "physical_boot_verified": False,
        })
    return {"format": "retroverse-readonly-storage-inventory-v1", "max_bytes": MAX_BYTES,
            "devices": devices, "can_write": False,
            "warning": "Inventory is not proof of trust, capacity integrity, health, or board boot compatibility. Never install based on this report alone."}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lsblk-json", type=Path, required=True, help="Saved output of lsblk -J -b ...")
    args = p.parse_args()
    try:
        result = analyze(json.loads(args.lsblk_json.read_text()))
    except (OSError, ValueError) as e:
        p.exit(2, f"ERROR: {e}\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
