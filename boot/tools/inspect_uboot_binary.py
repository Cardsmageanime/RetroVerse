#!/usr/bin/env python3
"""Read-only legacy U-Boot header and printable-string inspection; never execute input."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

UIMAGE_MAGIC = 0x27051956
MAX_FILE = 16 * 1024 * 1024
HAZARDS = {
    "persistent-environment": re.compile(rb"\b(?:saveenv|defenv|env\s+save|env\s+default|setenv\s+bootcmd)\b", re.I),
    "storage-modification": re.compile(rb"\b(?:mmc\s+(?:write|erase|hwpartition)|sf\s+(?:write|erase|update)|nand\s+(?:write|erase)|fastboot\s+flash)\b", re.I),
    "indirect-execution": re.compile(rb"\b(?:run|source|autoscr|bootm|booti|bootz)\b", re.I),
}

def inspect(data):
    if not isinstance(data, bytes):
        raise ValueError("Expected file bytes")
    if not data or len(data) > MAX_FILE:
        raise ValueError("File is empty or exceeds 16 MiB")
    header = {"legacy_uimage_magic": False, "header_complete": False,
              "image_size_bytes": None, "payload_within_file": False,
              "image_type": None, "compression": None}
    if len(data) >= 4 and struct.unpack_from(">I", data)[0] == UIMAGE_MAGIC:
        header["legacy_uimage_magic"] = True
        if len(data) >= 64:
            size = struct.unpack_from(">I", data, 12)[0]
            header.update(header_complete=True, image_size_bytes=size,
                          payload_within_file=size <= len(data) - 64,
                          image_type=data[30], compression=data[31])
    strings = re.findall(rb"[\x20-\x7e]{4,}", data)
    findings = [name for name, pattern in HAZARDS.items()
                if any(pattern.search(s) for s in strings)]
    return {
        "format": "nexus-relay-legacy-uboot-binary-triage-v1",
        "bytes_examined": len(data), "sha256": hashlib.sha256(data).hexdigest(),
        "header": header, "hazards": findings,
        "status": "hazards-visible" if findings else "unknown-manual-review-required",
        "safe_to_execute": False, "boot_authorized": False,
        "write_authorized": False,
        "warning": "Strings may miss compressed, encoded, split, or indirect commands. A recognizable header is not proof of validity or compatibility. Never execute legacy aml_autoscript.",
    }

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--reference-file", type=Path, required=True,
                   help="Existing regular file only; never a block device")
    args = p.parse_args(argv)
    try:
        if not args.reference_file.is_file() or args.reference_file.is_symlink():
            raise ValueError("Input must be a nonsymlink regular file")
        size = args.reference_file.stat().st_size
        if not 0 < size <= MAX_FILE:
            raise ValueError("Invalid file size")
        report = inspect(args.reference_file.read_bytes())
    except (OSError, ValueError) as exc:
        p.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
