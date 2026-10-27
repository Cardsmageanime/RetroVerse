#!/usr/bin/env python3
"""Conservative text-only U-Boot command audit. Never executes commands."""
import argparse
import json
import re
from pathlib import Path

# A heuristic guardrail, not a shell parser or proof that any script is safe.
DANGEROUS = {
    "persistent-environment": r"\b(?:saveenv|env\s+save|defenv|setenv\s+bootcmd|env\s+default)\b",
    "storage-write-or-erase": r"\b(?:mmc\s+(?:write|erase|hwpartition)|sf\s+(?:write|erase|update)|nand\s+(?:write|erase)|fastboot\s+flash|flash_erase|dd\s+)\b",
    "persistent-boot-control": r"\b(?:bcb\s+set|reboot\s+bootloader|upgrade_step)\b",
}
UNKNOWN_EXECUTION = r"\b(?:run|source|autoscr|bootm|booti|bootz|bootelf|go|usb\s+start|fatload|ext4load)\b"

def inspect(text):
    if not isinstance(text, str):
        raise ValueError("Script must be text")
    # Ignore nothing: even comments can contain example commands and require review.
    normalized = re.sub(r"\\\s*\n", " ", text)
    findings = []
    for line_number, line in enumerate(normalized.splitlines(), 1):
        for name, pattern in DANGEROUS.items():
            if re.search(pattern, line, re.IGNORECASE):
                findings.append({"line": line_number, "kind": name})
        if re.search(UNKNOWN_EXECUTION, line, re.IGNORECASE):
            findings.append({"line": line_number, "kind": "manual-control-flow-review"})
    return {
        "format": "nexus-relay-uboot-text-audit-v1",
        "status": "hazard-detected" if any(x["kind"] != "manual-control-flow-review" for x in findings) else "manual-review-required",
        "findings": findings,
        "boot_authorized": False,
        "safe_to_execute": False,
        "warning": "Static keyword scan only: variables, aliases, scripts and binaries can conceal behavior. Never execute based on this report.",
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--script-text", required=True, type=Path, help="Saved plain-text commands, NOT a binary U-Boot script or device")
    args = p.parse_args()
    try:
        content = args.script_text.read_text(encoding="utf-8")
        result = inspect(content)
    except (OSError, UnicodeError, ValueError) as exc:
        p.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
