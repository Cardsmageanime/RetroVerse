# Nexus Relay Learning Lesson 005 — ARM64 USB kernel handoff checks

**Phase 1 milestone.** The Linux kernel, device tree (DTB) and compressed initramfs must not be assigned overlapping memory regions for a proposed bootloader handoff.

## How the new code works
- `images.kernel`, `images.dtb`, and `images.initramfs` contain **integer byte addresses and lengths** in a JSON manifest. They are hypothetical planning data, not Vayava-confirmed addresses.
- The checker rejects missing or malformed regions, zero-length buffers, booleans masquerading as integer addresses, and 64-bit address overflow.
- Regions use half-open ranges `[address, address + size)`. The overlap test is `a_start < b_end and b_start < a_end`. Adjacent regions are allowed.
- Independent board identity, verified RAM map and safe nonpersistent USB loader confirmation must be explicitly recorded. Unknown persistent bootloader or eMMC write behavior blocks the report.
- The tool **always** sets `boot_authorized`, `image_bootable`, and `storage_writes_authorized` to `false`. Passing these structural checks cannot prove that RAM regions are truly available: bootloader relocation, reserved memory, secure firmware and U-Boot versions remain unknown.

## Run a harmless simulation
```bash
printf '{}' > sample-handoff.json
python3 boot/tools/check_boot_handoff.py --manifest sample-handoff.json
python3 -m unittest discover -s boot/tests -p 'test_check_boot_handoff.py' -v
```

A report with no valid evidence will be **blocked**. Never substitute example addresses for verified GameBox RAM allocation or execute legacy `aml_autoscript`.

## Status
**10 new tests passed in the local test run**, along with 20 earlier Phase 1 unit tests (30 total). No real USB boot or media write was attempted. A board-specific DTB, RAM map, nonpersistent external loader, and on-device validation remain required. Phases 1–5 only.
