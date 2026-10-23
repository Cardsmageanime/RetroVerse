#!/usr/bin/env python3
"""Read-only, opt-in removable-media library indexer for RetroVerse.

Only scans an explicitly provided ROM directory; never mounts, modifies,
copies, hashes, or launches games. No internal Android filesystem discovery.
"""
import argparse
import json
from pathlib import Path

EXTENSIONS={".nes":"NES",".sfc":"SNES",".smc":"SNES",".gb":"Game Boy",
".gbc":"Game Boy Color",".gba":"Game Boy Advance",".n64":"Nintendo 64",
".z64":"Nintendo 64",".v64":"Nintendo 64",".iso":"Disc image",
".chd":"Disc image",".cue":"Disc image",".gen":"Sega Genesis",
".md":"Sega Genesis",".sms":"Sega Master System",".gg":"Game Gear",
".pce":"PC Engine",".cdi":"Dreamcast"}
MAX_FILES=5000

def discover(root, limit=MAX_FILES):
    root=Path(root).resolve(strict=True)
    if not root.is_dir():raise ValueError("ROM root must be a directory")
    if not 1<=limit<=MAX_FILES:raise ValueError("Invalid scan limit")
    entries=[]
    # Symlinks are never followed; exclude hidden directories.
    for directory, dirs, files in __import__("os").walk(root, followlinks=False):
        dirs[:]=sorted(d for d in dirs if not d.startswith(".") and not (Path(directory)/d).is_symlink())
        for name in sorted(files):
            if name.startswith("."):continue
            file=Path(directory)/name
            if file.is_symlink() or file.suffix.lower() not in EXTENSIONS:continue
            if len(entries)>=limit:return entries,True
            entries.append({"title":file.stem[:180],"system":EXTENSIONS[file.suffix.lower()],
                "relative_path":str(file.relative_to(root))})
    return entries,False

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom-root",type=Path,required=True,help="Explicit removable-media ROM folder; read-only")
    p.add_argument("--output",type=Path,required=True,help="New JSON index path (must not exist)")
    p.add_argument("--limit",type=int,default=MAX_FILES)
    a=p.parse_args()
    try:
        if a.output.resolve()==a.rom_root.resolve():raise ValueError("Index output must differ from ROM root")
        entries,truncated=discover(a.rom_root,a.limit)
        payload={"format":"retroverse-library-v1","root":str(a.rom_root.resolve()),
            "count":len(entries),"truncated":truncated,"games":entries}
        with a.output.open("x",encoding="utf-8") as f:json.dump(payload,f,indent=2)
    except (ValueError,OSError) as e:p.error(str(e))
    print(f"Indexed {len(entries)} games (read-only, truncated={truncated})")

if __name__=="__main__":main()
