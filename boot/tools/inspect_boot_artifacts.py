#!/usr/bin/env python3
"""Read-only structural inspection of RetroVerse ARM64 boot artifacts.

Only checks binary signatures and FDT header ranges. Does not establish
board compatibility, bootloader support, physical boot, or flashing safety.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

def inspect_file(path, kind):
    p = Path(path)
    if not p.is_file():
        return {"kind": kind, "ok": False, "reason": "missing-regular-file"}
    size = p.stat().st_size
    with p.open("rb") as f:
        header = f.read(64)
        f.seek(0)
        digest = hashlib.sha256()
        while True:
            block = f.read(1048576)
            if not block:
                break
            digest.update(block)
    result = {"kind": kind, "size_bytes": size, "sha256": digest.hexdigest(), "ok": False}
    if kind == "kernel":
        result["ok"] = len(header) >= 64 and header[56:60] == b"ARM\x64"
    elif kind == "dtb":
        if len(header) >= 40:
            magic, total, off_struct, off_strings, off_reserve, version, last_comp, _, strings_size, struct_size = struct.unpack(">10I", header[:40])
            result["ok"] = (
                magic == 0xd00dfeed and 40 <= total <= size
                and 0 < off_reserve < total and off_struct < total and off_strings < total
                and off_struct + struct_size <= total
                and off_strings + strings_size <= total
                and version >= 16 and last_comp <= version
            )
            result["dtb_total_size"] = total
    elif kind == "initramfs":
        result["ok"] = header.startswith(b"\x1f\x8b\x08") or header.startswith(b"070701") or header.startswith(b"070702")
    else:
        raise ValueError("Unsupported kind")
    result["reason"] = "signature-and-header-accepted" if result["ok"] else "signature-or-header-rejected"
    return result

def inspect(kernel, dtb, initramfs):
    items = [inspect_file(kernel, "kernel"), inspect_file(dtb, "dtb"), inspect_file(initramfs, "initramfs")]
    return {
        "structural_checks_passed": all(item["ok"] for item in items),
        "boot_compatibility_verified": False,
        "physical_boot_verified": False,
        "safe_to_flash": False,
        "artifacts": items,
        "warning": "Structural checks alone never authorize flashing or prove external U-Boot boot."
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kernel", required=True)
    p.add_argument("--dtb", required=True)
    p.add_argument("--initramfs", required=True)
    a = p.parse_args()
    result = inspect(a.kernel, a.dtb, a.initramfs)
    print(json.dumps(result, indent=2))
    return 0 if result["structural_checks_passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
