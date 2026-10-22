#!/usr/bin/env python3
"""Validate a staged external diagnostic boot package, without writing to devices."""
import argparse, gzip, hashlib, json, struct
from pathlib import Path

def validate(directory):
    root=Path(directory)
    problems=[]
    for rel in ("Image","board.dtb","initramfs.cpio.gz","extlinux/extlinux.conf","SHA256SUMS.json"):
        if not (root/rel).is_file(): problems.append(f"Missing {rel}")
    if problems:return problems
    with (root/"Image").open("rb") as f: header=f.read(64)
    if len(header)<64 or header[56:60]!=struct.pack("<I",0x644d5241):
        problems.append("Invalid AArch64 Image signature")
    with (root/"board.dtb").open("rb") as f:dtb=f.read()
    if len(dtb)<40 or dtb[:4]!=bytes.fromhex("d00dfeed"):
        problems.append("Invalid device-tree header")
    elif struct.unpack(">I",dtb[4:8])[0]>len(dtb):
        problems.append("Device-tree total size exceeds file length")
    try:
        with gzip.open(root/"initramfs.cpio.gz","rb") as f:
            magic=f.read(6)
        if magic not in (b"070701",b"070702"):
            problems.append("Initramfs is not a newc CPIO archive")
    except (OSError, EOFError) as exc:
        problems.append(f"Invalid compressed initramfs: {exc}")
    config=(root/"extlinux/extlinux.conf").read_text()
    for directive in ("LINUX /Image","FDT /board.dtb","INITRD /initramfs.cpio.gz","rdinit=/init"):
        if directive not in config:problems.append(f"Missing extlinux directive: {directive}")
    try:
        sums=json.loads((root/"SHA256SUMS.json").read_text())["files"]
        for path,expected in sums.items():
            if path not in ("Image","board.dtb","initramfs.cpio.gz","extlinux/extlinux.conf"):
                problems.append("Unexpected checksum path: "+path);continue
            digest=hashlib.sha256((root/path).read_bytes()).hexdigest()
            if digest!=expected:problems.append("Checksum mismatch: "+path)
    except (ValueError,KeyError,TypeError) as exc:
        problems.append("Invalid checksum manifest: "+str(exc))
    return problems

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("directory",type=Path)
    args=parser.parse_args()
    errors=validate(args.directory)
    print(json.dumps({"status":"STRUCTURAL_CHECK_PASSED" if not errors else "INVALID","boot_verified":False,"flashable":False,"errors":errors},indent=2))
    raise SystemExit(bool(errors))
