#!/usr/bin/env python3
"""Prevent provisional hardware observations being misrepresented as flash-ready."""
import json,sys
from pathlib import Path
p=Path(__file__).resolve().parents[2]/"hardware/profiles/vayava-franklin-2gb.json"
data=json.loads(p.read_text())
assert data["android_board"]=="franklin"
assert data["cpu"]["arm64_capable"] is True
assert data["cpu"]["android_userspace_bits"]==32
assert data["status"]=="hardware-observed-boot-unverified"
assert all(data[k] is False for k in ("boot_chain_verified","external_sd_boot_verified","dtb_kernel_match_verified"))
assert data["permissions"]["flash_internal_storage"] is False
print("Franklin reference profile validated: boot remains UNVERIFIED")
