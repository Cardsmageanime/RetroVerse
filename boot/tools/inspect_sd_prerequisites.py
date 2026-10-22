#!/usr/bin/env python3
"""Read-only inventory of RetroVerse external boot artifacts and unresolved gates."""
import argparse, hashlib, json, struct
from pathlib import Path

def inspect(path):
    p=Path(path)
    out={"path":str(p),"exists":p.is_file()}
    if not p.is_file():return out
    out["size_bytes"]=p.stat().st_size
    h=hashlib.sha256()
    with p.open("rb") as f:
        header=f.read(4096)
        h.update(header)
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    out["sha256"]=h.hexdigest()
    out["arm64_image"]=len(header)>=60 and header[56:60]==struct.pack("<I",0x644d5241)
    out["dtb"]=len(header)>=8 and header[:4]==bytes.fromhex("d00dfeed") and 40<=struct.unpack(">I",header[4:8])[0]<=p.stat().st_size
    out["ext4_superblock"]=len(header)>=1082 and header[1080:1082]==bytes.fromhex("53ef")
    return out

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--kernel",required=True)
    a.add_argument("--dtb",required=True)
    a.add_argument("--rootfs",required=True)
    a.add_argument("--out",required=True)
    args=a.parse_args()
    dest=Path(args.out)
    if dest.exists():a.error("Refusing to overwrite existing manifest")
    data={k:inspect(getattr(args,k)) for k in ("kernel","dtb","rootfs")}
    status=all(x.get("exists") for x in data.values()) and data["kernel"].get("arm64_image") and data["dtb"].get("dtb") and data["rootfs"].get("ext4_superblock")
    report={"artifact_format_checks_pass":bool(status),"hardware_boot_verified":False,"flashable":False,"missing_hardware_requirements":["Vayava boot ROM and U-Boot path","board-specific DTB compatibility","external SD boot capability"],"artifacts":data}
    dest.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    return 0 if status else 2

if __name__=="__main__":
    raise SystemExit(main())
