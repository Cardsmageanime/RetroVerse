#!/usr/bin/env python3
"""Read-only ARM64 kernel artifact inspection; never claims hardware bootability."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

ARM64_MAGIC = 0x644D5241
FDT_MAGIC = 0xD00DFEED

def inspect(image: Path, dtb: Path) -> dict:
    report = {"schema": "retroverse-arm64-artifacts-v1",
              "kernel_image": str(image), "dtb": str(dtb),
              "checks": {}, "boot_verified": False, "flash_ready": False}
    with image.open("rb") as handle:
        header = handle.read(64)
    valid_arm64 = len(header) >= 64 and struct.unpack_from("<I", header, 56)[0] == ARM64_MAGIC
    with dtb.open("rb") as handle:
        dtb_header = handle.read(40)
    valid_fdt = len(dtb_header) >= 40 and struct.unpack_from(">I", dtb_header)[0] == FDT_MAGIC
    declared_size = struct.unpack_from(">I", dtb_header, 4)[0] if valid_fdt else 0
    dtb_size = dtb.stat().st_size
    valid_fdt = valid_fdt and 40 <= declared_size <= dtb_size
    report["checks"] = {"arm64_image_magic": valid_arm64,
                          "dtb_header_and_size": valid_fdt}
    for label, path in (("kernel", image), ("dtb", dtb)):
        sha = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                sha.update(chunk)
        report[label + "_sha256"] = sha.hexdigest()
        report[label + "_bytes"] = path.stat().st_size
    report["structural_checks_passed"] = all(report["checks"].values())
    report["notes"] = ("Passing checks proves only recognizable file structure, "
                       "not DTB/kernel compatibility, bootloader support, or hardware boot.")
    return report

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--dtb", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = inspect(args.image, args.dtb)
    except (OSError, ValueError, struct.error) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["structural_checks_passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
