#!/usr/bin/env python3
"""Manifest compiled ARM64 artifacts. No claims of bootability."""
import argparse
import hashlib
import json
from pathlib import Path

def manifest(output, source_label):
    out=Path(output).resolve(strict=True)
    image=out/"arch/arm64/boot/Image"
    if not image.is_file() or image.stat().st_size==0:
        raise ValueError("ARM64 Image missing or empty")
    dtbs=sorted((out/"arch/arm64/boot/dts").rglob("*.dtb"))
    if not dtbs:
        raise ValueError("No device tree blobs compiled")
    def describe(file):
        digest=hashlib.sha256()
        with file.open("rb") as stream:
            for block in iter(lambda:stream.read(1024*1024),b""):
                digest.update(block)
        return {"path":str(file.relative_to(out)),"bytes":file.stat().st_size,"sha256":digest.hexdigest()}
    return {"format":"retroverse-arm64-build-v1","source":source_label,
            "architecture":"arm64","build_verified":True,
            "gamebox_compatible":False,"boot_tested":False,
            "kernel_image":describe(image),"device_trees":[describe(d) for d in dtbs]}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",required=True,type=Path)
    parser.add_argument("--source",required=True)
    parser.add_argument("--manifest",required=True,type=Path)
    args=parser.parse_args()
    data=manifest(args.output,args.source)
    with args.manifest.open("x",encoding="utf-8") as file:
        json.dump(data,file,indent=2)
    print("Build manifest created; GameBox compatibility NOT established.")
if __name__=="__main__":main()
