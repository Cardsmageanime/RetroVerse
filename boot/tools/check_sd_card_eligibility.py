#!/usr/bin/env python3
"""Offline read-only eligibility check; JSON observations only, never accesses disks."""
import argparse
import json
from pathlib import Path

MAX_BYTES = 1_000_000_000_000


def evaluate(observation):
    if not isinstance(observation, dict):
        raise ValueError("Input must be a JSON object")
    issues = []
    size = observation.get("capacity_bytes")
    if type(size) is not int or size <= 0:
        issues.append("unknown-or-invalid-capacity")
    elif size > MAX_BYTES:
        issues.append("capacity-exceeds-1TB")
    gates = {
        "removable_verified": (True, "removable-media-not-verified"),
        "internal_system_storage": (False, "internal-storage-exclusion-not-verified"),
        "target_unambiguous": (True, "target-not-unambiguous"),
        "write_protected": (False, "write-protection-not-cleared"),
        "io_errors_observed": (False, "io-reliability-not-verified"),
        "full_capacity_verified": (True, "actual-capacity-not-verified"),
    }
    for key, (expected, issue) in gates.items():
        if observation.get(key) is not expected:
            issues.append(issue)
    return {
        "format": "retroverse-sd-eligibility-v1",
        "eligibility": "passes-observation-preflight" if not issues else "blocked",
        "capacity_bytes": size if type(size) is int and size > 0 else None,
        "capacity_max_bytes": MAX_BYTES,
        "brand_restriction": False,
        "issues": issues,
        "can_write": False,
        "boot_verified": False,
        "notes": "Offline observations only. No live-device identity, physical integrity, boot compatibility or consent is established.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observation", type=Path, required=True, help="JSON report, NOT a block-device path")
    args = parser.parse_args()
    try:
        result = evaluate(json.loads(args.observation.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
