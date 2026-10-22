#!/usr/bin/env python3
"""Conservative, offline lint of *text* U-Boot scripts. Never executes scripts.

A clean lint report is not approval to run a script on hardware: U-Boot
commands, variable expansion, boot-source numbering and platform hooks vary.
"""
import argparse
import json
import re
from pathlib import Path

# This is a tripwire, not a full U-Boot command interpreter.
DANGEROUS = re.compile(
    r"\b(?:mmc\s+(?:write|erase|partconf|bootpart-resize)|"
    r"sf\s+(?:write|erase|update)|"
    r"nand\s+(?:write|erase|scrub)|"
    r"store\s+|defenv\b|saveenv\b|"
    r"setenv\b|env\s+(?:set|delete|erase|save|default)|"
    r"run\b|autoscr\b|source\b|"
    r"fatwrite\b|ext4write\b|mw\b|cp\b|"
    r"update\b|upgrade\b|recovery\b|"
    r"reset\b|reboot\b|bootm\b|booti\b|bootz\b|go\b)\b",
    re.IGNORECASE,
)
# Intentionally tiny: commands in this list are inspect-only under normal
# U-Boot behavior; even passing them does not prove that execution is safe.
READ_ONLY_LINES = (
    re.compile(r"^echo(?:\s+[A-Za-z0-9 ._:/=-]+)?$", re.IGNORECASE),
    re.compile(r"^version$", re.IGNORECASE),
    re.compile(r"^mmc\s+list$", re.IGNORECASE),
)

def lint_script(content):
    issues = []
    lines = content.splitlines()
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # Fail closed on control flow, shell chaining, expansion or binary text.
        if any(x in stripped for x in (";", "&&", "||", "`", "$", "\\", "{", "}", "\x00")):
            issues.append({"line": number, "category": "unreviewed-syntax"})
        elif DANGEROUS.search(stripped):
            issues.append({"line": number, "category": "possible-state-change-or-control-transfer"})
        elif not any(rule.fullmatch(stripped) for rule in READ_ONLY_LINES):
            issues.append({"line": number, "category": "not-on-tiny-observation-allowlist"})
    if len(content.encode("utf-8")) > 65536:
        issues.append({"line": 0, "category": "script-too-large"})
    return {
        "line_count": len(lines),
        "needs_manual_review": bool(issues),
        "issues": issues,
        "hardware_execution_approved": False,
        "firmware_or_emmc_write_approved": False,
        "warning": "Text-only heuristic. Never run an unaudited U-Boot script or treat an empty issue list as hardware authorization.",
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path, help="Local UTF-8 U-Boot script text, not a compiled script image")
    args = parser.parse_args()
    try:
        text = args.script.read_text(encoding="utf-8")
    except (UnicodeError, OSError) as exc:
        parser.error(f"Unable to read text script: {exc}")
    result = lint_script(text)
    print(json.dumps(result, indent=2))
    return 1 if result["needs_manual_review"] else 0

if __name__ == "__main__":
    raise SystemExit(main())
