#!/usr/bin/env python3
"""Validate tar member paths and symlinks before a trusted CI build extraction.

Absolute Linux symlink targets are legitimate *inside* a target rootfs:
e.g. /etc/alternatives/which -> /usr/bin/which. These are not extraction
destinations. Reject archive member path escapes, devices, and unsafe links.
"""
import posixpath
import sys
import tarfile
from pathlib import PurePosixPath

def inside_root(path):
    normalized = posixpath.normpath(path)
    return normalized not in (".", "..") and not normalized.startswith("../")

def validate(archive):
    with tarfile.open(archive, "r:gz") as tf:
        members = tf.getmembers()
        member_names = set()
        symlinks = {}
        for m in members:
            raw = m.name.removeprefix("./")
            if raw in ("", ".") and m.isdir():
                continue  # Standard root directory entry emitted by tar -C rootfs .
            if not raw or raw.startswith("/") or ".." in PurePosixPath(raw).parts or not inside_root(raw):
                raise ValueError(f"Unsafe archive member path: {m.name}")
            name = posixpath.normpath(raw)
            if m.isdev() or m.isfifo():
                raise ValueError(f"Unsupported device/FIFO: {m.name}")
            if m.issym():
                link = m.linkname
                # Absolute symlinks are normal in a Linux rootfs; interpret
                # their targets *relative to the intended rootfs*, not host /.
                if link.startswith("/"):
                    target = link.lstrip("/")
                    if ".." in PurePosixPath(target).parts or not inside_root(target):
                        raise ValueError(f"Unsafe absolute symlink: {m.name} -> {link}")
                else:
                    target = posixpath.join(posixpath.dirname(name), link)
                    if not inside_root(target):
                        raise ValueError(f"Unsafe relative symlink: {m.name} -> {link}")
                symlinks[name] = link
            elif m.islnk():
                link = m.linkname.removeprefix("./")
                if m.linkname.startswith("/") or ".." in PurePosixPath(link).parts or not inside_root(link):
                    raise ValueError(f"Unsafe hardlink: {m.name} -> {m.linkname}")
            member_names.add(name)
        # Do not allow extraction of regular content into a member's
        # symlink subtree. GNU tar could follow that link outside staging.
        for name in member_names:
            parts = name.split("/")
            for i in range(1, len(parts)):
                ancestor = "/".join(parts[:i])
                if ancestor in symlinks:
                    raise ValueError(f"Unsafe archive content below symlink: {name} (via {ancestor})")
    return len(members)

if __name__ == "__main__":
    for filename in sys.argv[1:]:
        try:
            count = validate(filename)
            print(f"Checked {count} members: {filename}")
        except (OSError, tarfile.TarError, ValueError) as e:
            raise SystemExit(str(e))
    print("Archive member and symlink checks passed")
