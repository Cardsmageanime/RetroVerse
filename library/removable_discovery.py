#!/usr/bin/env python3
"""Discover mounted removable ROM folders on Linux; never mount or scan them automatically.

User must explicitly choose an offered path before library scanning. Uses lsblk
JSON in read-only mode; restricts mounts to /media, /run/media, /mnt.
"""
import json
from pathlib import Path
import subprocess

ALLOWED_PREFIXES=(Path("/media"),Path("/run/media"),Path("/mnt"))
def allowed_mount(path):
    candidate=Path(path)
    if not candidate.is_absolute() or ".." in candidate.parts:return False
    resolved=candidate.resolve()
    return any(resolved!=p and p in resolved.parents for p in ALLOWED_PREFIXES)

def candidates(tree):
    found=[]
    def visit(node, parent_removable=False):
        removable=parent_removable or str(node.get("rm",0)).lower() in ("1","true")
        mounted=node.get("mountpoint")
        if removable and isinstance(mounted,str) and allowed_mount(mounted):
            root=Path(mounted).resolve()
            for roms in (root/"roms",root/"ROMS",root/"games",root/"GAMES"):
                if roms.is_dir() and not roms.is_symlink():
                    found.append(str(roms))
        for child in node.get("children") or []:visit(child,removable)
    for device in tree.get("blockdevices",[]):visit(device)
    return sorted(set(found))

def discover_mounts():
    result=subprocess.run(["lsblk","--json","--output","NAME,RM,MOUNTPOINT","--list"],
                          capture_output=True,text=True,check=True,timeout=5)
    return candidates(json.loads(result.stdout))

if __name__=="__main__":
    for folder in discover_mounts():print(folder)
