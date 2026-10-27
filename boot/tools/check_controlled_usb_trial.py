#!/usr/bin/env python3
"""Offline checklist review only. Cannot approve or initiate a USB boot."""
import argparse
import json
from pathlib import Path

REQUIRED = {
    'exact_board_revision_evidenced': 'Board revision not independently established',
    'board_matched_dtb_reviewed': 'Board-specific DTB not independently reviewed',
    'ram_and_reserved_ranges_reviewed': 'RAM and firmware reservations unverified',
    'nonpersistent_usb_handoff_reviewed': 'Nonpersistent USB boot route unverified',
    'usb_image_checksums_reviewed': 'USB image integrity unverified',
    'recovery_to_android_reviewed': 'Android recovery path unverified',
    'reference_sd_removed_and_protected': 'Reference EmuELEC SD protection unverified',
    'user_physically_present': 'No physical operator confirmed',
}
FORBIDDEN = {
    'legacy_aml_autoscript_executed': 'Legacy boot script must not be executed',
    'environment_save_required': 'Persistent boot environment changes are forbidden',
    'emmc_write_required': 'Internal Android/eMMC writes are forbidden',
    'unverified_dtb_selected': 'Unverified DTB cannot be used',
    'unresolved_usb_errors': 'USB I/O errors must be resolved',
}

def evaluate(data):
    if not isinstance(data, dict):
        raise ValueError('Expected JSON object')
    findings = [msg for key, msg in REQUIRED.items() if data.get(key) is not True]
    findings += [msg for key, msg in FORBIDDEN.items() if data.get(key) is not False]
    return {
        'format': 'nexus-relay-controlled-usb-trial-preflight-v1',
        'status': 'blocked' if findings else 'paper-checklist-complete-independent-approval-required',
        'findings': findings,
        'boot_authorized': False,
        'flash_authorized': False,
        'storage_write_authorized': False,
        'physical_boot_verified': False,
        'warning': 'Self-reported paper checklist is not hardware proof. Do not execute U-Boot commands or boot from this result.',
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checklist', required=True, type=Path, help='Saved JSON checklist file only')
    args = p.parse_args()
    try:
        result = evaluate(json.loads(args.checklist.read_text(encoding='utf-8')))
    except (OSError, UnicodeError, ValueError) as exc:
        p.exit(2, f'ERROR: {exc}\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
