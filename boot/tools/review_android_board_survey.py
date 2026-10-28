#!/usr/bin/env python3
"""Read a saved ADB board survey and extract non-authorizing hardware clues."""
import argparse
import json
from pathlib import Path

EXPECTED = ("soc_platform", "hardware", "product_board", "bootloader_version",
            "device_tree_model", "device_tree_compatible", "kernel_release", "mmc_hosts")
MAX_LEN = 1024

def analyze(survey):
    if not isinstance(survey, dict) or survey.get("survey_type") != "read-only-android-board-probe":
        raise ValueError("Expected a read-only-android-board-probe JSON report")
    fields = survey.get("results")
    if not isinstance(fields, dict):
        raise ValueError("Missing results object")
    results = {}
    gaps = []
    for key in EXPECTED:
        record = fields.get(key)
        if not isinstance(record, dict) or type(record.get("ok")) is not bool:
            results[key] = None
            gaps.append(f"{key}: missing or malformed")
            continue
        value = record.get("value")
        if record["ok"] is not True or not isinstance(value, str) or not value.strip() or len(value) > MAX_LEN:
            results[key] = None
            gaps.append(f"{key}: not available")
            continue
        results[key] = value.strip()
    # No detected SoC/board string alone proves that a matching DTB or USB boot path exists.
    clues = []
    joined = " ".join(str(results.get(k) or "") for k in ("soc_platform", "hardware", "device_tree_compatible")).lower()
    if "g12a" in joined or "s905x2" in joined:
        clues.append("G12A/S905X2-family text appears in reported Android fields; verify physical board revision.")
    if results.get("mmc_hosts"):
        clues.append("MMC hosts were listed, but this does not prove USB boot or SD link reliability.")
    return {
        "format": "nexus-relay-android-board-survey-review-v1",
        "survey_fields": results,
        "missing_fields": gaps,
        "clues_not_confirmations": clues,
        "board_revision_confirmed": False,
        "dtb_matches_board": False,
        "nonpersistent_usb_boot_path_verified": False,
        "boot_authorized": False,
        "storage_write_authorized": False,
        "next_evidence": [
            "Corroborate GameBox board revision and exact SoC against trustworthy hardware evidence.",
            "Verify board-specific DTB, RAM/DDR layout and regulators separately.",
            "Verify external USB loading is possible without persistent bootloader or internal storage changes.",
        ],
        "warning": "Read-only Android observations cannot prove safe bootloader behavior. Do not flash, run aml_autoscript, or boot on this basis.",
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--survey", required=True, type=Path, help="Existing JSON report file only")
    args = parser.parse_args()
    try:
        result = analyze(json.loads(args.survey.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
