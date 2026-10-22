#!/usr/bin/env python3
"""Reject archive entries that escape the destination. Preserve safe Debian symlinks."""
import posixpath
import sys
import tarfile
from pathlib import PurePosixPath

def safe_relative(path):
    if not path or path.startswith("/"):
        return False
    return posixpath.normpath(path) != ".." and not posixpath.normpath(path).startswith("../")

for filename in sys.argv[1:]:
    with tarfile.open(filename, "r:gz") as tf:
        members = tf.getmembers()
        for m in members:
            name = m.name.removeprefix("./")
            if not safe_relative(name):
                raise SystemExit(f"Unsafe archive path {m.name}")
            if m.isdev() or m.isfifo():
                raise SystemExit(f"Unsupported special file {m.name}")
            if m.issym():
                # Debian systemd unit enablement legitimately uses absolute in-image
                # /lib/systemd/system targets. Admit only this explicit class;
                # all other absolute symlink targets remain rejected.
                if m.linkname.startswith("/"):
                    if not (name.startswith("etc/systemd/system/") and
                            m.linkname.startswith("/lib/systemd/system/") and
                            ".." not in PurePosixPath(m.linkname).parts):
                        raise SystemExit(f"Unsafe absolute symlink {m.name}: {m.linkname}")
                else:
                    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), m.linkname))
                    if not safe_relative(resolved):
                        raise SystemExit(f"Unsafe symlink {m.name}: {m.linkname}")
            elif m.islnk():
                # Tar hardlink targets resolve relative to archive root.
                if not safe_relative(m.linkname.removeprefix("./")):
                    raise SystemExit(f"Unsafe hardlink {m.name}: {m.linkname}")
print("Tar archive path and link boundary checks passed")
