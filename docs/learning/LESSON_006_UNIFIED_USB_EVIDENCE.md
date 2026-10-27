# Nexus Relay — Learning Lesson 006: Unified USB boot evidence report

**Scope:** Phase 1, safe research only. No removable-media writes, no internal Android/eMMC changes, no physical boot.

## What this milestone adds

The new `boot/tools/check_usb_boot_evidence_bundle.py` reads one *saved JSON file* containing three reports created by earlier Nexus Relay tools:

- `usb` — output of `check_usb_boot_readiness.py`
- `board` — output of `check_board_dtb_evidence.py`
- `handoff` — output of `check_boot_handoff.py`

Each report goes in a `reports` object. A useful learning exercise is to save `{"reports":{}}` to `sample-evidence-bundle.json`, then run:

```bash
python3 boot/tools/check_usb_boot_evidence_bundle.py --bundle sample-evidence-bundle.json
python3 -m unittest discover -s boot/tests -p 'test_check_usb_boot_evidence_bundle.py' -v
```

The example must return `review-blocked`.

## Code concepts

1. A Python dictionary, `EXPECTED`, lists each report's expected schema marker and finding-array key.
2. `evaluate()` walks through every report instead of stopping at the first error. The `outstanding` list gathers specific findings for each subsystem.
3. Missing reports, incorrect formats, malformed findings and invalid safety flags all block review. Every supplied safety flag must explicitly be the JSON boolean `false`.
4. Even when all three source reports *claim* no outstanding findings, the unified report still says `physical_boot_verified: false`, `boot_authorized: false`, and `write_authorized: false`. This prevents self-reported or fabricated JSON from being mistaken for hardware approval.
5. Standard-library-only code means the check is usable offline and never invokes a shell, reads a hardware block device, or executes a bootloader script.

## Limitations

This is a report collector and structural gate, **not** a cryptographic authenticity check or real hardware proof. It cannot independently verify that earlier source reports are truthful, come from the GameBox, or reference the same board revision. The tool does not certify RAM addresses, DTB electrical wiring, USB bootloader support, or USB media health.

**Next hardware blockers:** establish genuine model/revision evidence, approved board DTB and RAM map, a demonstrably nonpersistent U-Boot USB load path, and a safe controlled test plan. Never run legacy EmuELEC `aml_autoscript` or write internal eMMC.

## Tests

11 new unit-test methods passed in local development, including an additional missing-report test that checks all three report types. With earlier locally available bootloader and board/handoff test modules, the local Python discovery run reported **41 tests passed**. These are software-only tests, not USB boots.

Phases 1–5 remain the active development scope. Phase 6 is reserved for joint planning.
