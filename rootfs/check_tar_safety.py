#!/usr/bin/env python3
"""Reject risky tar archive entries before extracting build artifacts."""
import sys,tarfile
from pathlib import PurePosixPath
for filename in sys.argv[1:]:
 with tarfile.open(filename,"r:gz") as tf:
  for m in tf:
   name=m.name.removeprefix("./")
   parts=PurePosixPath(name).parts
   if m.name.startswith("/") or ".." in parts:
    raise SystemExit(f"Unsafe archive path {m.name}")
   if m.isdev() or m.isfifo():
    raise SystemExit(f"Unsupported special file {m.name}")
   if m.issym() or m.islnk():
    target=PurePosixPath(m.linkname)
    if m.linkname.startswith("/") or ".." in target.parts:
     raise SystemExit(f"Unsafe archive link {m.name}: {m.linkname}")
print("Tar path and link checks passed")
