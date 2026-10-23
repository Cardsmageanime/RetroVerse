#!/usr/bin/env python3
"""Read-only boot-reference inventory for RetroVerse ARM Systems Edition.

Inspect copied EmuELEC boot files, not original disks. Never writes, flashes,
mounts, edits bootloader settings, or asserts board compatibility.
"""
import argparse
import hashlib
import json
from pathlib import Path

NAMES=("aml_autoscript","cfgload","config.ini","dtb.img")
MAX_BYTES=32*1024*1024

def inspect(directory):
    base=Path(directory).resolve(strict=True)
    if not base.is_dir():
        raise ValueError("Reference location must be a directory")
    files={}
    for name in NAMES:
        candidate=base/name
        if candidate.is_symlink():
            files[name]={"state":"symlink-rejected"}
            continue
        if not candidate.is_file():
            files[name]={"state":"missing"}
            continue
        size=candidate.stat().st_size
        if size<1 or size>MAX_BYTES:
            files[name]={"state":"invalid-size","bytes":size}
            continue
        hash_value=hashlib.sha256()
        with candidate.open("rb") as inp:
            for chunk in iter(lambda:inp.read(65536),b""):
                hash_value.update(chunk)
        files[name]={"state":"present","bytes":size,"sha256":hash_value.hexdigest()}
        if name=="dtb.img":
            with candidate.open("rb") as inp:
                magic=inp.read(4)
            files[name]["fdt_magic"]=magic==bytes.fromhex("d00dfeed")
            files[name]["note"]="Magic only; no compatibility check"
    return {"format":"retroverse-arm-boot-reference-v1",
            "read_only":True,"bootable":False,"device_verified":False,"files":files,
            "next_step":"Review actual EmuELEC reference files and board-specific boot chain before building an image."}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--reference-dir",required=True,type=Path,
                   help="Folder containing COPIES of four known working EmuELEC boot references")
    a=p.parse_args()
    try:
        print(json.dumps(inspect(a.reference_dir),indent=2))
    except (OSError,ValueError) as exc:
        p.error(str(exc))

if __name__=="__main__":main()
