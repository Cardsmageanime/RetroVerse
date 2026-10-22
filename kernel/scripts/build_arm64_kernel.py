#!/usr/bin/env python3
"""Build actual ARM64 Image, modules and kernel-matched DTBs from Linux source."""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--linux-source",type=Path,required=True)
p.add_argument("--output",type=Path,required=True)
p.add_argument("--jobs",type=int,default=2)
p.add_argument("--execute",action="store_true")
a=p.parse_args()
source=a.linux_source.resolve(); out=a.output.resolve()
fragment=Path(__file__).resolve().parents[1]/"config/retroverse-g12a.fragment"
if not (source/"Makefile").is_file() or not (source/"scripts/kconfig/merge_config.sh").is_file():p.error("full Linux kernel sources required")
if source==out or source in out.parents or out in source.parents:p.error("output must be separate from kernel source")
if out.exists() and any(out.iterdir()):p.error("output must be empty")
if not 1<=a.jobs<=64:p.error("jobs must be 1..64")
if not fragment.is_file():p.error("missing kernel config fragment")
flags=["ARCH=arm64","CROSS_COMPILE=aarch64-linux-gnu-"]
cmds=[
["make","-C",str(source),"O="+str(out),*flags,"defconfig"],
["bash",str(source/"scripts/kconfig/merge_config.sh"),"-m","-O",str(out),str(out/".config"),str(fragment)],
["make","-C",str(source),"O="+str(out),*flags,"olddefconfig"],
["make","-C",str(source),"O="+str(out),*flags,"-j"+str(a.jobs),"Image","dtbs","modules"]]
for cmd in cmds:print(" ".join(cmd),flush=True)
if not a.execute:sys.exit("DRY RUN only; pass --execute to compile")
for tool in ["make","bash","aarch64-linux-gnu-gcc"]:
 if shutil.which(tool) is None:p.error("missing build tool: "+tool)
out.mkdir(parents=True,exist_ok=True)
for cmd in cmds:subprocess.run(cmd,check=True)
image=out/"arch/arm64/boot/Image"
with image.open("rb") as f:header=f.read(64)
if len(header)<64 or int.from_bytes(header[56:60],"little")!=0x644d5241:sys.exit("invalid ARM64 Image header")
g12a=sorted(x for x in (out/"arch/arm64/boot/dts").rglob("*.dtb") if x.name.startswith("meson-g12a"))
if not g12a:sys.exit("No compiled G12A DTBs; build rejected")
for dtb in g12a:
 with dtb.open("rb") as f: magic=f.read(4)
 if magic!=bytes.fromhex("d00dfeed"):sys.exit("Invalid DTB: "+str(dtb))
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
 return h.hexdigest()
manifest={"status":"compiled-not-boot-verified","kernel_image":str(image),"kernel_image_sha256":sha(image),"dtbs":[{"path":str(x),"sha256":sha(x)} for x in g12a]}
(out/"retroverse-arm64-build-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print("Compiled Image and",len(g12a),"G12A DTBs; hardware not verified.")
