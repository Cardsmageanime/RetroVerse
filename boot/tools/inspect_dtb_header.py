#!/usr/bin/env python3
"""Read-only Flattened Device Tree (DTB) envelope inspection of saved copies."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

MAGIC = 0xD00DFEED
HEADER_LEN = 40
MAX_BYTES = 16 * 1024 * 1024
FIELDS = ('magic', 'totalsize', 'off_dt_struct', 'off_dt_strings', 'off_mem_rsvmap',
          'version', 'last_comp_version', 'boot_cpuid_phys', 'size_dt_strings', 'size_dt_struct')

def inspect(data):
    """Validate DTB header and section boundaries; never assert board compatibility."""
    if not isinstance(data, bytes):
        raise ValueError('Expected bytes')
    problems = []
    if not HEADER_LEN <= len(data) <= MAX_BYTES:
        problems.append('DTB size outside supported bounds')
    header = None
    if len(data) >= HEADER_LEN:
        header = dict(zip(FIELDS, struct.unpack_from('>10I', data)))
        if header['magic'] != MAGIC:
            problems.append('Invalid FDT magic')
        total = header['totalsize']
        if total < HEADER_LEN or total > len(data):
            problems.append('Declared total size outside input')
        if total != len(data):
            problems.append('Declared total size differs from file length')
        if header['version'] < 16 or header['last_comp_version'] > header['version']:
            problems.append('Unsupported or inconsistent FDT version')
        for region, start, size in (
            ('structure', header['off_dt_struct'], header['size_dt_struct']),
            ('strings', header['off_dt_strings'], header['size_dt_strings']),
            ('reserve-map', header['off_mem_rsvmap'], 16),
        ):
            if start < HEADER_LEN or start > total or size > total - start:
                problems.append(f'{region} region outside declared DTB size')
        st = (header['off_dt_struct'], header['off_dt_struct'] + header['size_dt_struct'])
        ss = (header['off_dt_strings'], header['off_dt_strings'] + header['size_dt_strings'])
        if st[0] < ss[1] and ss[0] < st[1]:
            problems.append('Structure and strings regions overlap')
    return {
        'format': 'nexus-relay-dtb-envelope-review-v1',
        'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
        'header': header, 'structurally_consistent': not problems,
        'problems': problems, 'board_matched': False,
        'boot_authorized': False, 'write_authorized': False,
        'warning': 'Envelope checks do not parse FDT nodes, identify wiring, confirm board compatibility or authorize boot.',
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dtb-copy', type=Path, required=True, help='Saved ordinary DTB copy only')
    args = p.parse_args()
    path = args.dtb_copy
    try:
        if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= MAX_BYTES:
            raise ValueError('Input must be a nonsymlink regular file <= 16 MiB')
        report = inspect(path.read_bytes())
    except (OSError, ValueError) as exc:
        p.exit(2, f'ERROR: {exc}\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
