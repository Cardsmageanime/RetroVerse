#!/usr/bin/env python3
"""Extract privacy-conscious text observations from a saved U-Boot log.

This tool does not connect to hardware, execute boot commands, or verify a
boot path. All readiness fields are intentionally hard-coded false.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

MAX_LOG_BYTES = 4 * 1024 * 1024
VERSION_RE = re.compile(r"^U-Boot\s+([^\s]+)", re.IGNORECASE)
MODEL_RE = re.compile(r"^Model:\s*(.{1,120})\s*$", re.IGNORECASE)
MMC_RE = re.compile(r"\bmmc\s*([0-9]+)(?=[:\s])", re.IGNORECASE)


def analyze_text(text: str) -> dict:
    """Return normalized marker observations without retaining raw log text."""
    lines = text.splitlines()
    version = None
    model = None
    mmc_indexes = set()
    sd_load = False
    autoscript = False
    boot_handoff = False
    linux_start = False
    env_write = False
    flash_erase = False

    for line in lines:
        stripped = line.strip()
        if version is None:
            match = VERSION_RE.search(stripped)
            if match:
                version = match.group(1)[:100]
        if model is None:
            match = MODEL_RE.search(stripped)
            if match:
                # Keep only a short, printable label; never emit arbitrary log lines.
                candidate = re.sub(r"[^A-Za-z0-9 ._+()/-]", "", match.group(1)).strip()
                model = candidate[:80] or None
        mmc_indexes.update(MMC_RE.findall(stripped))
        lower = stripped.lower()
        sd_load |= bool(re.search(r"\b(?:fatload|load)\s+mmc\s+\d+:", lower))
        autoscript |= "autoscr" in lower or "executing script at" in lower
        boot_handoff |= bool(re.search(r"\bbootm(?:\s|$)", lower) or re.search(r"\bbooti(?:\s|$)", lower))
        linux_start |= "starting kernel" in lower or "booting linux" in lower
        env_write |= bool(re.search(r"\b(?:saveenv|env\s+save)\b", lower))
        flash_erase |= bool(re.search(r"\b(?:erase|flash|write|update)\b", lower) and
                            re.search(r"\b(?:nand|mmc|emmc|spi|flash|partition|device)\b", lower))

    return {
        "format": "retroverse-uboot-log-observations-v1",
        "input": {"line_count": len(lines), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()},
        "observations": {
            "uboot_version": version,
            "board_model": model,
            "mmc_index_tokens_seen": sorted(mmc_indexes, key=int),
            "sd_load_text_marker_seen": sd_load,
            "autoscript_text_marker_seen": autoscript,
            "boot_handoff_text_marker_seen": boot_handoff,
            "linux_start_text_marker_seen": linux_start,
            "persistent_environment_write_text_marker_seen": env_write,
            "flash_or_erase_text_marker_seen": flash_erase,
        },
        "manual_review_required": env_write or flash_erase,
        "raw_log_lines_included": False,
        "readiness": {
            "external_uboot_boot_path_verified": False,
            "external_sd_boot_verified": False,
            "can_flash": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, type=Path, help="saved text log from passive observation")
    parser.add_argument("--output", type=Path, help="new JSON report path (must not already exist)")
    args = parser.parse_args(argv)
    try:
        size = args.log.stat().st_size
        if size > MAX_LOG_BYTES:
            parser.error(f"log exceeds the {MAX_LOG_BYTES}-byte limit")
        raw = args.log.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        report = analyze_text(text)
        # Hash original bytes too, so decoding replacement does not obscure identity.
        report["input"]["sha256"] = hashlib.sha256(raw).hexdigest()
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(rendered)
        else:
            sys.stdout.write(rendered)
    except FileExistsError:
        parser.error("output already exists; choose a new report path")
    except OSError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
