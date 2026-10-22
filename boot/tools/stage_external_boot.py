#!/usr/bin/env python3
"""Stage external-boot diagnostic files. Does not install a bootloader or write block devices."""
import argparse, hashlib, json, shutil
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--kernel",type=Path,required=True)
p.add_argument("--dtb",type=Path,required=True)
p.add_argument("--initramfs",type=Path,required=True)
p.add_argument("--output",type=Path,required=True)
p.add_argument("--label",default="RetroVerse ARM64 diagnostic")
a=p.parse_args()
files=[a.kernel,a.dtb,a.initramfs]
for f in files:
 if not f.is_file() or not f.stat().st_size:p.error("missing/empty input: "+str(f))
with a.kernel.open("rb") as f:k=f.read(64)
if len(k)<64 or int.from_bytes(k[56:60],"little")!=0x644d5241:p.error("ARM64 Image header invalid")
with a.dtb.open("rb") as f:d=f.read(8)
if len(d)<8 or d[:4]!=bytes.fromhex("d00dfeed"):p.error("FDT header invalid")
with a.initramfs.open("rb") as f:i=f.read(2)
if i!=bytes.fromhex("1f8b"):p.error("initramfs must be gzip")
dest=a.output
if dest.exists():p.error("output already exists; refusing overwrite")
dest.mkdir(parents=True)
(dest/"extlinux").mkdir()
shutil.copy2(a.kernel,dest/"Image")
shutil.copy2(a.dtb,dest/"board.dtb")
shutil.copy2(a.initramfs,dest/"initramfs.cpio.gz")
conf=f"""# Diagnostic only; requires verified external U-Boot extlinux support on exact board.
DEFAULT retroverse-diagnostic
TIMEOUT 50
MENU TITLE RetroVerse ARM64 diagnostic (NOT a flashable OS)
LABEL retroverse-diagnostic
  MENU LABEL {a.label}
  LINUX /Image
  FDT /board.dtb
  INITRD /initramfs.cpio.gz
  APPEND console=ttyAML0,115200 earlycon rdinit=/init
"""
(dest/"extlinux"/"extlinux.conf").write_text(conf)
manifest={"warning":"NOT FLASHABLE, NO BOOTLOADER; only works if existing U-Boot reads extlinux; DTB must match board/kernel","files":{}}
for x in [dest/"Image",dest/"board.dtb",dest/"initramfs.cpio.gz",dest/"extlinux/extlinux.conf"]:
 manifest["files"][str(x.relative_to(dest))]=hashlib.sha256(x.read_bytes()).hexdigest()
(dest/"SHA256SUMS.json").write_text(json.dumps(manifest,indent=2)+"\n")
print("Staged external boot files only; NO FLASHABLE IMAGE:",dest)
