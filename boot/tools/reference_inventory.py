#!/usr/bin/env python3
"""Inventory offline copies of GameBox boot references, never block devices."""
import argparse
import hashlib
import json
import stat
import struct
import zlib
from pathlib import Path

NAMES = ("aml_autoscript", "dtb.img", "kernel.img", "config.ini")
MAX = 128 * 1024 * 1024
MAGIC = 0x27051956

def inspect_copy(path):
    if path.is_symlink():
        raise ValueError("symlink disallowed")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= MAX:
        raise ValueError("not a nonempty regular file within size limit")
    data = path.read_bytes()
    result = {"size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    if path.name == "aml_autoscript":
        result["legacy_uimage"] = {"recognized": False, "header_crc_valid": False,
                                   "payload_crc_valid": False}
        if len(data) >= 64 and struct.unpack_from(">I", data)[0] == MAGIC:
            size = struct.unpack_from(">I", data, 12)[0]
            h = bytearray(data[:64]); h[4:8] = b"\0" * 4
            hcrc = struct.unpack_from(">I", data, 4)[0]
            dcrc = struct.unpack_from(">I", data, 24)[0]
            result["legacy_uimage"] = {
                "recognized": True,
                "header_crc_valid": zlib.crc32(h) == hcrc,
                "payload_crc_valid": size <= len(data) - 64 and zlib.crc32(data[64:64+size]) == dcrc,
            }
    return result

def analyze(directory):
    if not directory.is_dir() or directory.is_symlink():
        raise ValueError("expected a real directory containing COPIES of reference files")
    records, gaps = {}, []
    for name in NAMES:
        path = directory / name
        try:
            records[name] = inspect_copy(path)
        except (OSError, ValueError) as exc:
            records[name] = None
            gaps.append(f"{name}: {exc.__class__.__name__}")
    return {
        "format": "nexus-relay-reference-inventory-v1", "files": records,
        "missing_or_unreadable": gaps,
        "boot_authorized": False, "safe_to_execute": False,
        "write_authorized": False, "device_tree_approved": False,
        "warning": "Hashes and CRCs establish neither authenticity nor hardware compatibility. Never execute aml_autoscript.",
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--reference-dir", type=Path, required=True,
                   help="Directory containing ordinary OFFLINE COPIES, not a mounted SD device")
    args = p.parse_args()
    try:
        result = analyze(args.reference_dir)
    except (OSError, ValueError) as exc:
        p.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
