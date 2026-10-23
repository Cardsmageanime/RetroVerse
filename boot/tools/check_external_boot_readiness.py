#!/usr/bin/env python3
"""Evaluate RetroVerse external boot readiness without accessing disks or ADB.

This is a conservative evidence check, NOT proof of successful boot. It never
writes to a storage device, changes firmware, or authorizes flashing.
"""
import argparse
import json
from pathlib import Path

REQUIRED_GATES = (
    "soc_identity_confirmed",
    "board_dtb_matches_compiled_kernel",
    "external_uboot_boot_path_verified",
)
STORAGE_GATES = (
    "windows_hash_readback_passed",
    "gamebox_sd_link_reliability_verified",
)

def evaluate(profile, evidence):
    findings = []
    if profile.get("android_amlogic_dt_id_observed") != "g12a_u212_2g":
        findings.append("Board-specific G12A u212 2GB identification missing or changed.")
    if profile.get("android_sd_bus_width_bits_observed") != 4:
        findings.append("4-bit SD bus width evidence missing or changed.")
    if profile.get("android_sd_max_frequency_hz_observed") != 100000000:
        findings.append("100 MHz Android SD maximum-frequency evidence missing or changed.")
    for gate in REQUIRED_GATES:
        if evidence.get(gate) is not True:
            findings.append("Required boot evidence not verified: " + gate)
    if evidence.get("android_internal_storage_untouched") is not True:
        findings.append("Internal storage preservation not verified: android_internal_storage_untouched")
    for gate in STORAGE_GATES:
        if evidence.get(gate) is not True:
            findings.append("Storage evidence not verified: " + gate)
    # A passed Windows hash test is not the same as card integrity or device-side stability.
    return {
        "profile": profile.get("profile_id", "unknown"),
        "readiness": "research-only" if findings else "candidate-for-controlled-boot-planning",
        "can_flash": False,
        "can_claim_successful_boot": False,
        "findings": findings,
        "warning": "No disk writes or reboots are performed; this tool never authorizes flashing."
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", default="hardware/profiles/vayava-franklin-2gb.json")
    parser.add_argument("--evidence", default="hardware/evidence/vayava-franklin-external-boot.json")
    args = parser.parse_args()
    with Path(args.profile).open(encoding="utf-8") as f:
        profile = json.load(f)
    with Path(args.evidence).open(encoding="utf-8") as f:
        evidence = json.load(f)
    print(json.dumps(evaluate(profile, evidence), indent=2))

if __name__ == "__main__":
    main()
