#!/usr/bin/env python3
"""Read-only DTB structure parser for board identity clues; never authorizes boot."""
import argparse
import json
import struct
from pathlib import Path

MAGIC = 0xd00dfeed
BEGIN, END_NODE, PROP, NOP, END = 1, 2, 3, 4, 9
MAX_SIZE = 16 * 1024 * 1024
TARGET_PROPERTIES = {"model", "compatible", "status", "device_type"}

def parse(data):
    if not isinstance(data, bytes) or not 56 <= len(data) <= MAX_SIZE:
        raise ValueError("Invalid DTB data length")
    magic, total, structure, strings, reserve, version, last, cpu, strings_size, structure_size = struct.unpack_from(">10I", data)
    if magic != MAGIC or total != len(data) or version < 17 or last > version:
        raise ValueError("Invalid DTB header")
    if any(a < 40 or a > total or n > total - a for a, n in (
            (structure, structure_size), (strings, strings_size), (reserve, 16))):
        raise ValueError("DTB section outside file")
    s_end, n_end = structure + structure_size, strings + strings_size
    if structure < n_end and strings < s_end:
        raise ValueError("DTB sections overlap")
    if reserve < s_end and structure < reserve + 16:\n        raise ValueError("Reserve map overlaps structure")\n    if reserve < n_end and strings < reserve + 16:\n        raise ValueError("Reserve map overlaps strings")\n    position, stack, nodes, finished = structure, [], [], False
    while position + 4 <= s_end:
        token = struct.unpack_from(">I", data, position)[0]
        position += 4
        if token == BEGIN:
            terminator = data.find(b"\0", position, s_end)
            if terminator < 0:
                raise ValueError("Unterminated DTB node")
            name = data[position:terminator].decode("utf-8", errors="replace")
            position = (terminator + 4) & ~3
            if (terminator + 4) & ~3 > s_end:\n                raise ValueError("Node padding out of bounds")\n            stack.append(name)
            if len(stack) > 64:
                raise ValueError("Too many nested nodes")
            nodes.append({"path": "/" + "/".join(p for p in stack if p), "properties": {}})
            if len(nodes) > 4096:
                raise ValueError("Too many DTB nodes")
        elif token == END_NODE:
            if not stack:
                raise ValueError("Unmatched end-node")
            stack.pop()
        elif token == PROP:
            if not stack or position + 8 > s_end:
                raise ValueError("Malformed DTB property")
            length, offset = struct.unpack_from(">II", data, position)
            position += 8
            if length > s_end - position or offset >= strings_size:
                raise ValueError("Invalid DTB property bounds")
            key_start = strings + offset
            key_end = data.find(b"\0", key_start, n_end)
            if key_end < 0:
                raise ValueError("Unterminated property name")
            key = data[key_start:key_end].decode("ascii", errors="replace")
            raw = data[position:position + length]
            position += (length + 3) & ~3
            if position > s_end:
                raise ValueError("Property padding out of bounds")
            if key in TARGET_PROPERTIES:
                nodes[-1]["properties"][key] = [
                    x.decode("utf-8", errors="replace") for x in raw.split(b"\0") if x
                ][:16]
        elif token == NOP:
            continue
        elif token == END:
            if stack:
                raise ValueError("Unclosed DTB nodes")
            finished = True
            break
        else:
            raise ValueError("Unknown DTB structure token")
    if not finished:
        raise ValueError("No DTB end marker")
    relevant = [node for node in nodes if node["path"] == "/" or
                any(tag in node["path"].lower() for tag in ("mmc@", "sd@", "usb@", "memory@"))]
    return {"format": "nexus-relay-dtb-node-evidence-v2",
            "observed_nodes": relevant, "total_nodes": len(nodes),
            "board_match_verified": False, "usb_boot_verified": False,
            "boot_authorized": False, "write_authorized": False,
            "warning": "Parsed labels are clues only. No GPIO, regulator, DDR or U-Boot compatibility is established."}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dtb-copy", required=True, type=Path)
    args = parser.parse_args()
    try:
        p = args.dtb_copy
        if p.is_symlink() or not p.is_file() or not 56 <= p.stat().st_size <= MAX_SIZE:
            raise ValueError("Use a normal copied DTB file, not a device")
        result = parse(p.read_bytes())
    except (OSError, ValueError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
