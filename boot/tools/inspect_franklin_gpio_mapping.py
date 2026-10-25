#!/usr/bin/env python3
"""Read-only inspection of decompiled G12A vendor SD card-detect evidence."""
import argparse
import json
import re
from pathlib import Path


def enclosing_block(text, position):
    """Return smallest balanced DTS block enclosing a source offset."""
    stack = []
    for i, char in enumerate(text[:position + 1]):
        if char == "{":
            stack.append(i)
        elif char == "}" and stack:
            stack.pop()
    if not stack:
        return None
    start = stack[-1]
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:i]
    return None


def inspect(text):
    start = re.search(r"(?m)^\s*sd2@ffe05000\s*\{", text)
    if not start:
        raise ValueError("Missing vendor sd2@ffe05000 node")
    # Find the matching node brace rather than searching the entire DTS.
    brace = text.index("{", start.start())
    depth = 0
    end = None
    for i in range(brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end is None:
        raise ValueError("Unclosed SD controller node")
    sd_node = text[brace + 1:end]
    sd_child = re.search(r"(?ms)^\s*sd\s*\{(.*?)^\s*\};", sd_node)
    if sd_child is None:
        raise ValueError("Missing vendor SD child node")
    cd = re.search(r"\bgpio_cd\s*=\s*<\s*(0x[0-9a-f]+|\d+)\s+(0x[0-9a-f]+|\d+)\s+(0x[0-9a-f]+|\d+)\s*>\s*;", sd_child.group(1), re.I)
    if not cd:
        raise ValueError("Missing or unsupported vendor gpio_cd property")
    phandle, raw_index, raw_flags = (int(x, 0) for x in cd.groups())
    controller_candidates = []
    for match in re.finditer(r"\bphandle\s*=\s*<\s*(0x[0-9a-f]+|\d+)\s*>\s*;", text, re.I):
        if int(match.group(1), 0) == phandle:
            controller_candidates.append(enclosing_block(text, match.start()))
    controller_found = any(
        s is not None
        and re.search(r"\bgpio-controller\s*;", s)
        and re.search(r"#gpio-cells\s*=\s*<\s*(?:0x0*2|2)\s*>\s*;", s, re.I)
        for s in controller_candidates
    )
    return {
        "status": "research-only",
        "vendor_sd_node": "sd2@ffe05000",
        "vendor_gpio_cd": {"phandle": hex(phandle), "raw_index": raw_index, "raw_flags": raw_flags},
        "vendor_gpio_controller_candidate_found": controller_found,
        "mainline_gpio_guess": None,
        "mainline_gpio_polarity_verified": False,
        "sd_power_rails_verified": False,
        "approved_for_boot": False,
        "approved_for_flash": False,
        "warnings": [
            "Vendor GPIO indices and flags cannot be assumed equivalent to mainline numbering.",
            "DTS inspection cannot establish electrical wiring, supply rails or SD-link reliability."
        ]
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vendor-dts", type=Path, required=True, help="Copied vendor DTS (read-only)")
    args = p.parse_args()
    try:
        report = inspect(args.vendor_dts.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        p.exit(1, f"ERROR: {exc}\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
