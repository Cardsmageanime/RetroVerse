#!/usr/bin/env python3
"""Conservative, read-only assessment of a candidate RetroVerse board profile."""
import argparse
import json
from pathlib import Path

REQUIRED_EVIDENCE = (
    "soc_identity_confirmed",
    "board_dtb_matches_compiled_kernel",
    "external_uboot_boot_path_verified",
    "android_internal_storage_untouched",
)

def evaluate(profile, evidence):
    problems = []
    if profile.get("android_board") != "franklin":
        problems.append("Unexpected board profile")
    if profile.get("status") != "hardware-observed-boot-unverified":
        problems.append("Hardware profile status must remain explicit")
    if evidence.get("board_id") != profile.get("android_board"):
        problems.append("Evidence must reference the expected board")
    for key in REQUIRED_EVIDENCE:
        if evidence.get(key) is not True:
            problems.append("Missing physical verification: " + key)
    if profile.get("permissions", {}).get("flash_internal_storage") is not False:
        problems.append("Internal storage protection required")
    return {"ready_for_controlled_external_boot_test": not problems,
            "automated_tests_prove_bootability": False,
            "missing_evidence": problems,
            "warning": "Even a positive evidence report requires supervised testing; it is not a flash authorization."}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--profile",type=Path,required=True)
    p.add_argument("--evidence",type=Path,required=True)
    a=p.parse_args()
    result=evaluate(json.loads(a.profile.read_text()),json.loads(a.evidence.read_text()))
    print(json.dumps(result,indent=2))
    return 0 if result["ready_for_controlled_external_boot_test"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
