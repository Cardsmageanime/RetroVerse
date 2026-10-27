# Nexus Relay Learning Lesson 002 — Read-only USB boot evidence gate

## Why this exists
The USB boot project is preserved, but real hardware startup has not been demonstrated. The legacy EmuELEC `aml_autoscript` changes U-Boot environment and **must not be used** as a test shortcut. This utility checks an *existing JSON file only*: it cannot discover, write, format or boot USB devices.

## Reading the source
- `REQUIRED` lists six facts that need direct board-specific confirmation: exact model, DTB, nonpersistent USB boot command, media integrity, kernel compatibility, and Android protection.
- `HAZARDS` lists known failure conditions; even a positive checklist cannot override a hazard.
- `evaluate()` fails closed if any required field is absent or not a real JSON boolean `true`.
- `boot_authorized`, `can_write` and `hardware_boot_verified` are **always false**, even with all reported checks passed.
- `main()` reads JSON using Python's standard library and produces a JSON report.

## Safe simulated example
Save `{"exact_board_identity_verified": false}` as `usb-evidence.json` (ordinary text file) then:
```bash
python3 boot/tools/check_usb_boot_readiness.py --evidence usb-evidence.json
python3 -m unittest discover -s boot/tests -p 'test_check_usb_boot_readiness.py' -v
```
The result is blocked. Never point this program at a disk device. The true state of the Vayava board cannot be established from an invented evidence file. It is not a physical test.

## Hardware gates
Before a controlled boot trial, verify the exact Vayava board identity, its correctly sourced DTB, a **nonpersistent external USB** boot route, medium health, kernel compatibility and no Android/eMMC writes. Keep the EmuELEC SD reference untouched. Stop if a command includes `defenv`, `saveenv`, `mmc write` or flashes internal partitions.

**Verified locally during milestone implementation:** 8 standalone Python unit tests passed. Live GameBox USB boot remains **not tested**. Only Phases 1–5 are authorized.
