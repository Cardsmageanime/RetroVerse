#!/usr/bin/env python3
"""Read-only offline merger of three independently authored boot-evidence reports."""
import argparse
import json
from pathlib import Path

EXPECTED = {
    'usb': ('nexus-relay-usb-boot-readiness-v1', 'blockers'),
    'board': ('nexus-relay-board-evidence-v1', 'blockers'),
    'handoff': ('nexus-relay-arm64-handoff-check-v1', 'problems'),
}

def evaluate(bundle):
    if not isinstance(bundle, dict):
        raise ValueError('Bundle must be a JSON object')
    reports = bundle.get('reports')
    if not isinstance(reports, dict):
        reports = {}
    sections = {}
    outstanding = []
    for name, (expected_format, problem_key) in EXPECTED.items():
        report = reports.get(name)
        problems = []
        if not isinstance(report, dict):
            problems.append('Missing or malformed report')
        else:
            if report.get('format') != expected_format:
                problems.append('Unexpected report format')
            items = report.get(problem_key)
            if not isinstance(items, list) or any(not isinstance(x, str) or not x.strip() for x in items):
                problems.append('Missing or malformed findings array')
            else:
                problems.extend(items)
            required_flags = ('boot_authorized',) + (('can_write', 'hardware_boot_verified') if name == 'usb' else ('flash_authorized', 'device_tree_approved') if name == 'board' else ('image_bootable', 'storage_writes_authorized'))
            for flag in required_flags:
                if report.get(flag) is not False:
                    problems.append(f'Safety flag {flag} is not explicitly false')
            if report.get('status') not in {
                'usb': {'verification-blocked', 'reported-checks-complete-review-required'},
                'board': {'verification-blocked', 'reported-evidence-requires-independent-review'},
                'handoff': {'blocked', 'structural-checks-only-external-review-required'},
            }[name]:
                problems.append('Unexpected report status')
        sections[name] = {'valid_structure': not any(p.startswith(('Missing or malformed', 'Unexpected', 'Safety flag')) for p in problems), 'findings': problems}
        outstanding.extend(f'{name}: {p}' for p in problems)
    return {
        'format': 'nexus-relay-usb-boot-evidence-bundle-v1',
        'status': 'review-blocked' if outstanding else 'reports-structurally-complete-hardware-unverified',
        'sections': sections,
        'outstanding': outstanding,
        'physical_boot_verified': False,
        'boot_authorized': False,
        'write_authorized': False,
        'warning': 'Static third-party/self-reported JSON only. Never interpret this as permission to execute boot scripts, write storage, or start hardware testing.',
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle', type=Path, required=True, help='Saved ordinary JSON file, not a device')
    args = p.parse_args()
    try:
        report = evaluate(json.loads(args.bundle.read_text(encoding='utf-8')))
    except (OSError, UnicodeError, ValueError) as exc:
        p.exit(2, f'ERROR: {exc}\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
