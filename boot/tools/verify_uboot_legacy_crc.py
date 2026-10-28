#!/usr/bin/env python3
"""Offline legacy U-Boot uImage header/payload CRC verification; no execution."""
import argparse
import json
import struct
import zlib
from pathlib import Path

MAGIC = 0x27051956
MAX_BYTES = 16 * 1024 * 1024
HEADER_BYTES = 64

def verify(data):
    if not isinstance(data, bytes) or not 0 < len(data) <= MAX_BYTES:
        raise ValueError('Expected nonempty bytes no larger than 16 MiB')
    errors = []
    result = {'format': 'nexus-relay-uboot-crc-v1',
              'legacy_header_present': False, 'header_crc_valid': False,
              'payload_crc_valid': False, 'payload_length_valid': False,
              'declared_payload_bytes': None, 'issues': errors,
              'boot_authorized': False, 'safe_to_execute': False,
              'write_authorized': False}
    if len(data) < HEADER_BYTES:
        errors.append('Truncated legacy uImage header')
        return result
    magic, expected_hcrc, _, size, _, _, expected_dcrc = struct.unpack_from('>7I', data)
    if magic != MAGIC:
        errors.append('Not a legacy U-Boot uImage header')
        return result
    result['legacy_header_present'] = True
    result['declared_payload_bytes'] = size
    header_copy = bytearray(data[:HEADER_BYTES])
    header_copy[4:8] = bytes(4)
    result['header_crc_valid'] = zlib.crc32(header_copy) == expected_hcrc
    if not result['header_crc_valid']:
        errors.append('Header CRC32 mismatch')
    if size > len(data) - HEADER_BYTES:
        errors.append('Declared payload exceeds available bytes')
        return result
    result['payload_length_valid'] = True
    result['payload_crc_valid'] = zlib.crc32(data[HEADER_BYTES:HEADER_BYTES + size]) == expected_dcrc
    if not result['payload_crc_valid']:
        errors.append('Payload CRC32 mismatch')
    if len(data) != HEADER_BYTES + size:
        errors.append('Trailing bytes after declared payload')
    return result

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-file', type=Path, required=True, help='Existing regular file only')
    args = parser.parse_args(argv)
    try:
        path = args.reference_file
        if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= MAX_BYTES:
            raise ValueError('Input must be a non-symlink, nonempty regular file <=16 MiB')
        result = verify(path.read_bytes())
    except (OSError, ValueError) as exc:
        parser.exit(2, f'ERROR: {exc}\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
